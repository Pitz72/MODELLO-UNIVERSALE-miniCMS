# CAPITOLO 9: Content Lifecycle

Questo capitolo trasforma un database in un sistema editoriale: come un contenuto nasce bozza, viene programmato, diventa pubblico, e come l'API che lo serve decide forma, conteggio e visibilità. È anche il capitolo in cui si chiude un filo aperto al Capitolo 6: il contratto di payload che il client legge in modo difensivo nasce qui, lato server.

## 1. Stati Dinamici contro Stati Persistenti

Il database salva uno stato fisso (`status`), ma l'applicazione ne calcola uno dinamico, che dipende dal tempo. La matrice pulita è questa:

| `status` (DB) | `published_at` | Stato reale (UI) | Descrizione |
| :--- | :--- | :--- | :--- |
| `draft` | qualsiasi | **bozza** | mai visibile al pubblico |
| `published` | nel futuro | **programmato** | visibile solo agli admin, in attesa |
| `published` | nel passato | **pubblicato** | visibile a tutti |

Questa è la matrice di **SimonePizziWebSite**, ed è la più ordinata. Gli altri due siti portano le cicatrici delle loro migrazioni: **SitoRuntime** filtra la lista pubblica con `status = 'published' OR status IS NULL`, dove l'`IS NULL` è il residuo del fatto che la colonna `status` è stata aggiunta fuori dallo schema base; **DISINTELLIGENZA** interroga ancora `status = 'scheduled'`, uno stato che una migrazione ha dichiarato superato ma che il codice continua a cercare. La matrice ordinata è un punto d'arrivo, non lo stato naturale delle cose (Capitolo 15).

## 2. Programmazione senza Cron: le Tre Strategie del Presente

L'idea è elegante e condivisa: nessun job schedulato: un articolo con `published_at` nel futuro è «pubblicato ma non ancora visibile», e compare da solo quando la query di visibilità trova `published_at <= adesso`. Lato React, la dashboard calcola lo stesso stato al volo per dare un feedback immediato all'admin:

```typescript
const isDraft     = item.status === 'draft';
const isScheduled = item.status === 'published' && new Date(item.published_at) > new Date();
const isPublished = item.status === 'published' && new Date(item.published_at) <= new Date();
```

Il punto delicato è cosa significhi «adesso». Non c'è un'unica risposta giusta: i tre siti lo calcolano in tre modi, e ognuno ha il suo modo di sbagliare.

- **SimonePizziWebSite** forza `date_default_timezone_set('Europe/Rome')` e confronta in PHP. Corretto, ma solo finché il fuso è forzato in *ogni* endpoint (Capitolo 5).
- **SitoRuntime** confronta stringhe `date('Y-m-d H:i:s')` con separatore spazio. La query è giusta, ma se il client invia una data in formato ISO con la `T`, il confronto fra stringhe salta: è l'incidente documentato in `debug_time.php`.
- **DISINTELLIGENZA** delega a `CURRENT_TIMESTAMP` di SQLite, che è in **UTC**, mentre `published_at` è salvato nel fuso del server. Un articolo compare o sparisce con uno scarto di una o due ore.

> [!WARNING]
> **Chi calcola il presente: PHP o il database?**
> La conversione `datetime-local` (la `T` del browser) verso il formato del DB (lo spazio) non è «lo standard»: è il punto dolente di chi confronta date come stringhe, cioè SitoRuntime. Le altre due strategie evitano quel problema ma ne introducono altri (il fuso da forzare ovunque in SPW, lo scarto UTC in DIS). La regola pratica: scegli una sola fonte del presente e usala sempre. Se confronti in PHP, forza il fuso nel prelude condiviso; se confronti nel database, assicurati che `published_at` e `NOW`/`CURRENT_TIMESTAMP` vivano nello stesso fuso. Mescolarle è la ricetta del post che appare un'ora prima del previsto.

```typescript
// la conversione T <-> spazio è di SitoRuntime, non una regola universale
value={published_at.replace(' ', 'T').slice(0, 16)}              // DB -> UI
onChange={e => setPublishedAt(e.target.value.replace('T', ' ') + ':00')}   // UI -> DB
```

## 3. Il Contratto di Risposta: dove si chiude il Double Read

Al Capitolo 6 il client leggeva il payload in modo difensivo, perché la forma delle risposte non è uniforme. Il perché è qui, lato server: il contratto non è mai stato versionato, è stato **esteso quando serviva** (aggiungendo la paginazione, un wrapper `success`), e così la busta è diversa per endpoint e per sito.

- **SimonePizziWebSite**: *solo* la lista articoli ritorna `{ data, total, page, limit }`; tutto il resto (progetti, categorie, tag) è array nudo. Il client fa il «Double Read» non perché un endpoint cambi forma, ma perché mescola le due famiglie nei loader.
- **SitoRuntime**: tre buste diverse, `{ success, data, meta }` per le news, `{ success, articles, total }` per l'admin, array nudo per speaker e podcast. Un mosaico per-endpoint.
- **DISINTELLIGENZA**: sempre array o oggetto nudo, la «busta zero».

Anche il conteggio per la paginazione vive in posti diversi. SPW ritorna il `total` grezzo e lascia il calcolo di `hasMore` al client (con un `COUNT(*)` separato sulle stesse condizioni e, dettaglio MySQL obbligatorio, i `LIMIT/OFFSET` bindati con `PARAM_INT`, altrimenti PDO li tratta come stringhe e la query fallisce). SitoRuntime pre-calcola `total_pages` lato server e lo mette in `meta`, così il load-more del client è banale. DISINTELLIGENZA non dà nessun metadato: il client chiede la pagina successiva alla cieca, finché torna vuota.

> [!NOTE]
> **Estendere un contratto invece di versionarlo: cosa costa**
> Aggiungere `{ data, total }` a un endpoint che prima tornava un array nudo è la cosa più rapida del mondo, e non rompe subito niente. Il costo arriva dopo, e lo paga il client: deve indovinare quale forma riceverà, e quando sbaglia (un array senza `total` letto come se avesse il conteggio) nasce il `hasMore` errato del Capitolo 6. Versionare un'API costa disciplina; estenderla in-place costa fragilità diffusa. Per un CMS piccolo la seconda è una scelta legittima, ma va fatta sapendo che il prezzo si sposta sul frontend.

## 4. La Cache dei Contenuti senza Redis

SitoRuntime è l'unico dei tre ad aggiungere una cache di lettura, e lo fa nel modo più thin-stack possibile: file JSON su disco, senza Redis, senza Memcached. La lista delle news viene servita da un file in `.cache/`, rigenerato solo quando è più vecchio del TTL.

```php
// SR news.php — cache su file con TTL e header diagnostico
$cacheFile = __DIR__ . "/.cache/news_p{$page}_l{$limit}.json";
if (file_exists($cacheFile) && (time() - filemtime($cacheFile) < 300)) {  // TTL 300s
    header('X-Cache: HIT');
    echo file_get_contents($cacheFile);
    exit;
}
// ...altrimenti interroga il DB, salva il JSON, e:
header('X-Cache: MISS');
```

Due dettagli la rendono sana. L'invalidazione è esplicita: a ogni `save` o `delete` la cartella `.cache/` viene ripulita, così il pubblico non vede mai dati vecchi dopo una modifica. E l'header `X-Cache: HIT/MISS` permette di verificare dall'esterno se la cache sta lavorando. È lo stesso meccanismo che, applicato al SEO, diventa lo scudo anti-bot del Capitolo 11; qui serve solo a non interrogare il database per ogni visita alla stessa pagina di lista.

## 5. Tassonomie: Categorie e Tag (e quando non servono)

Qui il Modello mostra di nuovo la sua scala, e va corretta un'idea diffusa: il multi-tagging relazionale non è lo standard di tutti, è la scelta di **un** sito quando serve davvero.

**SimonePizziWebSite** è il blog tassonomico completo: categorie gerarchiche con `parent_id` (una categoria-contenitore filtra anche le sottocategorie, via `IN`), e tag in relazione molti-a-molti su `article_tags`. Ma non è un «passaggio esclusivo» al modello relazionale: la funzione che salva i tag scrive **in parallelo** anche il vecchio campo CSV `articles.tags`, tenuto come cache di retrocompatibilità. È la convivenza del modello vecchio e nuovo durante una migrazione mai chiusa, non un taglio netto.

```php
// SPW — doppia scrittura: relazione M:N nuova + campo CSV legacy in parallelo
syncArticleTags($pdo, $articleId, $tagIds);                 // tabella article_tags (nuovo)
$pdo->prepare("UPDATE articles SET tags = ? WHERE id = ?")  // campo CSV (legacy, cache retro-compat)
    ->execute([implode(',', $tagNames), $articleId]);
```

**SitoRuntime** e **DISINTELLIGENZA** non hanno affatto tag relazionali: la `category` è una stringa libera (in DIS con default `'generale'`), e i «tag», dove esistono, sono un campo `TEXT` o `JSON`. Per un sito che non è un archivio tassonomico, una tabella categorie è peso che non serve: una stringa basta.

> [!TIP]
> **Quando NON ti serve una tabella categorie**
> La gerarchia `parent_id` con tag M:N è giusta per un blog con centinaia di articoli da filtrare per argomento. Per una radio con poche categorie fisse, o un festival, una stringa libera fa lo stesso lavoro senza join, senza tabella di relazione, senza editor di tassonomia. Aggiungere la tassonomia relazionale «perché è più corretto» è il genere di complessità che il Modello invita a rimandare finché il contenuto non la chiede.

## 6. Pubblico contro Admin: il Bypass e il 404 Deliberato

La stessa risorsa serve due pubblici, e la differenza è una condizione di visibilità aggiunta solo a chi non è loggato. SimonePizziWebSite lo realizza con un `AND` condizionale nello stesso endpoint; SitoRuntime con due query in due file diversi (lettura in `news.php`, gestione in `admin.php`); DISINTELLIGENZA con un `if (!$isAdmin)` che aggiunge il `WHERE`. Stessa idea, tre strutture.

Sul singolo articolo non pubblicato, però, c'è un dettaglio di sicurezza che vale la regola: si risponde **404, non 403**.

```php
// SPW articles.php?slug=... — il 404 deliberato: non confermare l'esistenza di una bozza
$article = $stmt->fetch();
if ($article) {
    $is_admin     = isset($_SESSION['user_id']);
    $is_published = $article['status'] === 'published' &&
                    (empty($article['published_at']) || strtotime($article['published_at']) <= $ita_now_time);
    if (!$is_admin && !$is_published) {
        http_response_code(404);                       // non 403: un 403 confermerebbe che la bozza esiste
        echo json_encode(['error' => 'Articolo non trovato']);
        exit;
    }
    echo json_encode($article);                        // l'admin vede tutto
}
```

Per la lista della dashboard, che deve mostrare anche le bozze, serve un controllo doppio: la sessione **e** un parametro esplicito.

```php
// il parametro ?admin=true da solo sarebbe bypassabile: va sempre legato alla sessione
$is_admin_dashboard = isset($_SESSION['user_id']) && ($_GET['admin'] ?? '') === 'true';
if (!$is_admin_dashboard) {
    $conditions[] = "status = 'published'";
    $conditions[] = "(published_at IS NULL OR published_at = '' OR published_at <= ?)";
    $params[]     = $ita_now_str;
}
```

Il fetch per `id` (non per slug) serve solo all'editor in dashboard, e richiede `Auth::check()` obbligatorio, perché deve caricare nel form anche le bozze mai pubblicate. È il terzo modo di accedere allo stesso contenuto, ciascuno con il suo livello di gate.

## 7. Workflow Editoriale e Integrità

Tre accortezze tengono insieme l'esperienza di redazione:
- **Auto-slug solo alla creazione**: lo slug si genera quando l'articolo nasce, non a ogni modifica del titolo, per non rompere i link già pubblicati e indicizzati.
- **Editor che si ripulisce tra un contenuto e l'altro**: passando dalla modifica di un articolo a un altro, il componente editor va smontato e rimontato (`key={item.id}`), così i buffer interni non trascinano testo da un contenuto al successivo.
- **Anteprima della copertina**: il form mostra la miniatura dell'immagine selezionata, con rimozione immediata prima del salvataggio.

Sul lato dashboard, la tabella di gestione cura le proporzioni (il titolo non oltre il 45% della griglia, una colonna categoria con badge colorati per la scansione rapida, date e stato dinamico ben visibili, le azioni condensate in icone a fine riga): dettagli di SimonePizziWebSite, utili come riferimento di UX più che come prescrizione.

> [!IMPORTANT]
> **Il Canone**
> - Stati bozza/programmato/pubblicato; il confronto `published_at <= NOW` va fatto nello stesso formato e fuso (o delegato a `NOW()`).
> - Per i contenuti non pubblici rispondi 404, non 403: non confermare l'esistenza di una bozza.
> - Estendi un contratto (es. `{data, total}`) invece di versionarlo, ma mantienilo coerente tra gli endpoint.
> - Cache JSON con TTL per i listing pesanti, invalidata su `save`/`delete`.

---
*Prossimo Capitolo: Security & Auth. Gestione delle sessioni, CSRF, ruoli e protezione anti-abuso.*
