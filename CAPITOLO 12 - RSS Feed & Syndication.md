# CAPITOLO 12: RSS Feed & Syndication (Terza Edizione)

Il feed RSS è il canale con cui un sito consegna i propri contenuti a chi non viene a leggerli sul sito: aggregatori, lettori di notizie, app podcast, bot di Telegram. Nel Modello è sempre lo stesso gesto thin-stack: un endpoint PHP che, a ogni richiesta, interroga il database e stampa l'XML al volo. Niente cron, niente file `.xml` materializzato su disco, niente libreria di serializzazione. Un articolo pubblicato compare nel feed al primo refresh.

Ma questo capitolo ha una lente precisa, ed è la chiusura di un filo. Al CAP 8 abbiamo aperto il quadro dei quattro emettitori del `content`: lo stesso HTML salvato grezzo nel database esce verso il mondo da quattro punti, ognuno con la propria difesa. Al CAP 11 abbiamo visto il prerender lasciare il buco aperto. Il feed è l'emettitore che lo **chiude**: in tutti e tre i siti, o non emette affatto il `content`, o lo escapa per intero. È il punto più sicuro della catena.

E proprio perché sulla sicurezza i tre siti convergono, è interessante quanto divergano su tutto il resto. La geografia va da un file unico a un trittico di file con ruoli opposti, fino a un feed che non è nemmeno di notizie ma di podcast. E sulla disciplina del GUID si vede una piccola storia di regressione: una buona idea risolta da un sito e dimenticata dagli altri due.

> [!NOTE]
> **Correzioni rispetto alla Seconda Edizione.** Tre punti del capitolo precedente erano sbagliati o fuorvianti. Il **feed podcast non è di SitoRuntime ma di DISINTELLIGENZA**: SR non genera un feed podcast, *consuma* quelli esterni con un proxy (§4). Il **catch vuoto** era insegnato come «fallback silenzioso» virtuoso: è invece un anti-pattern, perché serve un feed troncato con HTTP 200 (§7). E **`feed.php` non è un «alias»** di `rss.php`: è il feed podcast di DIS, un endpoint con tutt'altro scopo (§3).

---

## 1. L'anatomia comune di un feed

Sotto le differenze, i feed dei tre siti condividono la stessa ossatura. Un solo file, una `GET`, l'XML stampato in diretta dal database. L'esempio è il `rss.php` di SimonePizziWebSite, il più lineare dei tre:

```php
// public/api/rss.php (SPW) — il feed news, real-time dal DB
header('Content-Type: application/rss+xml; charset=utf-8');
$pdo = Database::connect();
date_default_timezone_set('Europe/Rome');                 // fuso forzato nel singolo file
$ita_now_str = date('Y-m-d H:i:s');
define('RSS_FEED_LIMIT', 50);

echo '<?xml version="1.0" encoding="UTF-8" ?>' . "\n<rss version=\"2.0\">\n<channel>\n";
echo '  <title>' . htmlspecialchars($site_title) . "</title>\n";
echo '  <link>'  . htmlspecialchars($base_url)   . "</link>\n";
echo '  <language>it-IT</language>' . "\n";
```

Tre attenzioni ricorrono in tutti e tre. Ogni campo dinamico che entra nell'XML passa per `htmlspecialchars`: titolo, link, URL dell'immagine, nessuno finisce crudo nel feed. Il fuso `Europe/Rome` viene riforzato dentro il file stesso, senza fidarsi del timezone impostato altrove, perché ogni file che confronta date col database deve difendersi da solo da un server in un fuso sbagliato (la lezione del CAP 9). E la data di pubblicazione esce sempre in formato RFC-822, quello che RSS 2.0 pretende, tramite la costante `DATE_RSS`: mai ISO 8601, che molti lettori rifiutano.

C'è anche una piccola asimmetria condivisa. Mentre `sitemap.xml` e `robots.txt` sono serviti da URL puliti tramite una rewrite (lo abbiamo visto al CAP 11), il feed si raggiunge sempre all'URL grezzo del file PHP: `/api/rss.php`, `/api/feed_news_rss.php`, `/api/feed.php`. Nessuno dei tre siti gli dà un `/feed.xml` pulito. Cura SEO sugli altri asset, nessuna cura qui.

---

## 2. Il feed chiude il filo dei quattro emettitori

Riprendiamo la tabella aperta al CAP 8. Lo stesso `content`, salvato grezzo, esce da quattro emettitori, e l'unica difesa che vale davvero è quella che ognuno mette per conto suo. Il render usa DOMPurify (tranne DIS). Il prerender usa `strip_tags` con allowlist, che lascia passare gli attributi: è la falla viva del CAP 11. Il feed, terzo emettitore, la chiude.

| # | Emettitore | Cosa emette del `content` | Difesa | Esito |
|---|---|---|---|---|
| 1 | **Render React** (CAP 8) | `content` pieno | DOMPurify (SPW, SR) / niente (DIS) | choke-point reale; DIS scoperto |
| 2 | **Prerender SEO** (CAP 11) | `content` pieno | `strip_tags` allowlist (solo tag) | **buco sugli attributi** (SPW, SR) |
| 3 | **Feed RSS** (questo capitolo) | niente (SPW, DIS) / preview escapata (SR) | `htmlspecialchars` / `strip_tags`+`htmlspecialchars` | **sicuro** |
| 4 | **Newsletter** (CAP 13) | (la chiude il prossimo capitolo) | — | — |

Il feed è sicuro, ma per due strade diverse. SPW lo è **per sottrazione**: il suo `rss.php` carica la colonna `content` nella query ma non la stampa mai; la `<description>` dell'item usa solo l'`excerpt`, escapato.

```php
// public/api/rss.php (SPW) — content SELECTato ma MAI emesso; description = solo excerpt escapato
echo '    <description>' . htmlspecialchars($article['excerpt']) . "</description>\n";  // ← excerpt, non content
// (la colonna content è nella SELECT ma non c'è un solo echo di $article['content'])
```

SR invece **rompe la sottrazione**: quando il riassunto manca, ripiega sui primi 500 caratteri del `content`. Ma lo neutralizza con uno `strip_tags` senza allowlist, che toglie *tutti* i tag, seguito da `htmlspecialchars`:

```php
// public/api/feed_news_rss.php (SR) — emette una preview del content, ma escapata per intero
$descriptionText = $article['summary'] ?: $article['content_preview'] . '...';   // usa il content se manca summary
$description = htmlspecialchars(strip_tags($descriptionText));                    // strip_tags SENZA allowlist + escape
```

La differenza con il prerender del CAP 11 è tutta qui: là `strip_tags` aveva una allowlist e lasciava i tag (e i loro attributi pericolosi); qui non ha allowlist, quindi non resta nessun tag, e quel poco testo viene anche trasformato in entità. DIS, dal canto suo, non emette un feed di notizie: il suo è un feed podcast, e il `content` delle news non lo tocca nessuno.

> [!IMPORTANT]
> **Due modi di rendere sicuro un feed: non emettere, o escapare**
> Il feed dimostra in positivo la tesi che attraversa CAP 8, 11 e 13: quando la difesa XSS vive in un solo render, ogni altro emettitore deve cavarsela da sé, e il feed ci riesce. SPW non emette il campo pericoloso (sicuro per sottrazione: robusto, ma perde informazione, niente articolo completo nel feed). SR lo emette ma lo escapa per intero (sicuro per escape: più informativo, ma più fragile, perché basterebbe rimettere un'allowlist a `strip_tags` per riaprire il buco, com'è successo nel prerender). Esiti uguali, filosofie opposte. La conclusione resta quella del filo: la sanitizzazione dovrebbe vivere una volta sola, lato server, non essere reinventata da ogni emettitore. Il quadro si chiude del tutto al CAP 13, dove nessuno emette il `content`.

---

## 3. La geografia: un file, un trittico, un feed podcast

Sulla forma, i tre siti non potrebbero essere più diversi.

SPW è un file solo, `rss.php`: feed di notizie, minimale e rigoroso. SR è un trittico, e qui sta la sua complessità: `feed_news_rss.php` genera il feed news del sito, `rss.php` (stesso nome di SPW, ruolo opposto) è un proxy che *consuma* feed esterni, e `feed_config.php` è un dispenser che serve all'admin l'indirizzo del feed. DIS è un caso a parte: niente feed di notizie, solo `feed.php`, un feed **podcast** in RSS 2.0 con il namespace iTunes, sottoscrivibile da un'app come Apple Podcasts.

> [!NOTE]
> **Produrre un feed podcast, o consumarne uno: non è la stessa cosa**
> Qui la Seconda Edizione si confondeva. Il sito che *genera* un feed podcast è DIS, con `feed.php`: legge la tabella `podcasts` ed emette gli episodi con `<enclosure>` audio e i tag `<itunes:*>`. SR fa l'opposto: non genera nessun feed podcast, ma con `rss.php` *scarica* i feed podcast altrui (Spreaker, il suo AzuraCast) per mostrarli sul sito. Produrre e consumare un feed sono due operazioni speculari, ed è proprio il contrasto tra questi due siti a renderlo evidente. Lo vediamo al paragrafo seguente.

---

## 4. Il proxy CORS inbound: consumare feed altrui

Un browser non può leggere un feed ospitato su un altro dominio se quel dominio non manda gli header CORS, e i feed podcast esterni di solito non li mandano. SR risolve con un proxy server-side: `rss.php` scarica il feed altrui e lo restituisce same-origin. La parte interessante è la difesa, perché un proxy che scarica qualunque URL gli passi è un *open proxy*, una porta spalancata verso attacchi SSRF.

```php
// public/api/rss.php (SR) — proxy inbound: allowlist + https-only + stale fallback
$allowedHosts = ['www.spreaker.com', 'spreaker.com', 'player.runtimeradio.com'];
if ($scheme !== 'https' || !in_array($host, $allowedHosts, true)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Feed URL not allowed']); exit;   // niente open proxy
}
// ... cache su disco rss_<md5>.xml, TTL 30' ...
if ($xml === false || $httpCode !== 200) {
    if (file_exists($cacheFile)) { header('X-Cache: STALE'); readfile($cacheFile); exit; }  // una cache scaduta è meglio di niente
}
```

Due scelte sane: una allowlist di host (il proxy scarica solo da quei domini) e l'obbligo di HTTPS chiudono la porta SSRF; una cache su disco con fallback «stale» fa sì che, se l'upstream è giù, si serva l'ultima copia buona invece di fallire. C'è però un dettaglio meno sano sul lato client: se il proxy del sito non risponde, il codice frontend ripiega su proxy pubblici di terzi (CodeTabs, AllOrigins), che l'allowlist non la conoscono. La resilienza si compra con una dipendenza da terzi non dichiarata.

> [!WARNING]
> **Un proxy che scarica URL è un bersaglio SSRF**
> Qualunque endpoint che, su richiesta, scarica un URL fornito dall'esterno va trattato come una potenziale leva per raggiungere risorse interne (metadati cloud, servizi su `localhost`, IP privati). Le due difese di `rss.php` sono il minimo corretto: una allowlist esplicita di host fidati e il rifiuto di tutto ciò che non è HTTPS. La regola è la stessa del CAP 10 sull'IP: non fidarti di un valore che arriva dal client, in questo caso l'URL da scaricare. E attenzione ai fallback: il ripiego del client su proxy pubblici aggira l'allowlist e va saputo.

---

## 5. `feed_config.php`: il lucchetto sulla porta accanto

Nel trittico di SR c'è un terzo file che vale un box a sé, perché è un caso da manuale di sicurezza apparente. `feed_config.php` è protetto da `isAdmin()` e il suo commento promette molto: «Restituisce l'URL del feed RSS privato solo ad admin autenticati. Il token non viene mai esposto nel bundle JavaScript pubblico».

```php
// public/api/feed_config.php (SR) — gata l'URL, ma l'endpoint è pubblico
require_once 'auth_utils.php';
if (!isAdmin()) { http_response_code(403); echo json_encode(['success'=>false,'error'=>'Forbidden']); exit; }
$origin = (/* https */ . '://' . $_SERVER['HTTP_HOST']);
echo json_encode(['success' => true, 'feed_url' => $origin . '/api/feed_news_rss.php']);
```

Due cose non tornano. Non esiste alcun token: l'URL restituito è nudo. E soprattutto il feed che quell'URL raggiunge, `feed_news_rss.php`, è **completamente pubblico**: non include `auth_utils.php`, non chiama `isAdmin()`, chiunque può leggerlo senza login. Il gate `isAdmin()` protegge l'atto di *scoprire* un indirizzo che è comunque pubblico e indovinabile.

> [!WARNING]
> **Il lucchetto sulla porta accanto**
> Mettere un gate sul dispenser di un URL non rende privato l'endpoint che quell'URL raggiunge. È sicurezza per oscurità, e l'oscurità qui non c'è nemmeno, perché il nome del file è prevedibile. Quasi certamente è il fossile di un'intenzione mai realizzata: un feed news autenticato con token per il bot Telegram (coerente con il `TELEGRAM_BOT_TOKEN` che vive nei segreti, CAP 10), progettato e mai costruito. La lezione: se un endpoint deve essere privato, l'autenticazione va su *quell'endpoint*, non sul foglietto che ne riporta l'indirizzo.

---

## 6. Il GUID che ripubblica

Ogni `<item>` di un feed ha un `<guid>`, l'identificatore con cui i consumatori riconoscono se un contenuto è nuovo o già visto. Sbagliarlo ha una conseguenza concreta e fastidiosa: se il GUID di un articolo cambia, gli aggregatori e i bot lo trattano come un articolo nuovo e lo ripubblicano. Su un'integrazione Telegram, significa spammare di nuovo tutti gli iscritti.

SPW ha risolto il problema in modo netto: il GUID è un URN costruito sull'ID di database, disaccoppiato dall'URL.

```php
// public/api/rss.php (SPW) — GUID stabile, indipendente dall'URL
$stable_guid = 'urn:simonepizzi:article:' . (int)$article['id'];
echo '    <guid isPermaLink="false">' . $stable_guid . "</guid>\n";
```

Così un cambio di slug o di categoria non tocca l'identità dell'articolo: per i consumatori resta lo stesso contenuto. È la stessa preoccupazione che, lato URL, giustifica i redirect 301: tenere stabile l'identità di una pagina anche quando il suo indirizzo cambia.

Gli altri due siti questa idea l'hanno persa. SR usa il permalink come GUID, con `isPermaLink="true"`: al primo cambio di slug, l'articolo si ripubblica (e SR non ha nemmeno i 301 a fare da rete). DIS scende ancora più giù e usa l'URL del file audio: basta che `migrate_media` sposti l'audio e ogni episodio torna «nuovo» nelle app podcast.

> [!TIP]
> **L'identità stabile di un articolo: un URN, non il permalink**
> Il vecchio capitolo raccomandava già il GUID a URN, ed è corretto. Quello che andava aggiunto è che è una best practice che due siti su tre **non** seguono: SPW la applica, SR è regredito al permalink, DIS all'URL audio (il meno stabile di tutti). La regola, in una riga: l'identità di un item nel feed deve dipendere da qualcosa che non cambia mai (l'ID di database), mai dall'indirizzo, che cambia eccome.

---

## 7. Il catch vuoto che nasconde un database giù

Resta da correggere un punto che la Seconda Edizione insegnava come virtù. Sia SPW sia DIS avvolgono la query in un `try/catch` con il `catch` **vuoto**:

```php
// public/api/rss.php (SPW) — il catch vuoto: l'header e <channel> sono già usciti con HTTP 200
} catch (Exception $e) {
    // fallback silenzioso: nessun log, nessun 5xx
}
echo "</channel></rss>";
```

Il problema è la sequenza. Quando l'eccezione scatta, l'header `Content-Type` e l'apertura del `<channel>` sono già stati stampati, con codice di risposta 200. Il `catch` vuoto inghiotte l'errore, e la chiusura `</channel></rss>` esce comunque: il client riceve un feed perfettamente ben formato e **vuoto**, indistinguibile da «non ci sono novità». Nessun log, nessun 500, nessun segnale. Un database giù diventa invisibile.

SR fa meglio, anche se non perfettamente: intercetta l'eccezione e risponde con un vero errore HTTP.

```php
// public/api/feed_news_rss.php (SR) — almeno segnala il guasto
} catch (PDOException $e) {
    http_response_code(500);
    echo "<error>Database Error</error>";   // (copre solo PDOException: un errore non-PDO sfuggirebbe)
}
```

> [!WARNING]
> **Il fallback silenzioso che nasconde un guasto**
> Un errore mascherato da risposta valida è peggio di un errore visibile: nessuno lo nota finché un utente non si lamenta che il feed «non aggiorna da una settimana». La regola è di non aprire la risposta (header e primo output) prima di aver eseguito la parte che può fallire, oppure di gestire il fallimento con un codice HTTP onesto, come prova a fare SR. Il `catch` vuoto non è un fallback: è un guasto silenziato.

---

## 8. Cicatrici minori

Alcuni dettagli più piccoli, ma reali. Il filtro di visibilità del CAP 9 (`status = 'published'`) viene dimenticato anche qui: il feed news di SR filtra solo sulla data, quindi una bozza con data passata trapela nel feed, terzo file dopo l'`index.php` e la sitemap a dimenticare la stessa regola. L'`<enclosure>` dell'immagine dichiara `type="image/jpeg"` cablato nel codice, ma l'upload converte le cover in WebP (CAP 7): i lettori più pignoli scartano una miniatura il cui MIME non corrisponde. E in entrambi i flagship la configurazione del canale (titolo, descrizione) è hardcoded, con un commento che promette di leggerla «dai settings»: una configurabilità annunciata e mai cablata, di cui DIS è la versione estrema (legge chiavi `podcast_*` che nessuno popola, quindi gira sempre sui default).

Su DIS c'è anche un dettaglio che è quasi un reperto. Il `feed.php` contiene commenti in cui il codice ragiona ad alta voce con sé stesso:

```php
// public/api/feed.php (DIS) — il codice che discute i propri dubbi, in produzione
// During init_db.php step I created a 'podcasts' table? Let's check init_db.php if I can.
// Fallback: ... create it via SQL here? No, bad practice on GET.
// I'll assume it exists or use NEWS with a category.
```

> [!NOTE]
> **Quando il codice racconta i suoi dubbi**
> Non è un bug, ma è una cicatrice di processo: il ritratto di un codebase generato in conversazione con un assistente, e mai riletto prima del deploy. Lo stesso tono si ritrova in altri file di DIS (l'`init_db.php`, l'`api.ts`). In produzione il codice dovrebbe affermare, non interrogarsi: questi monologhi vanno tolti nella rilettura, perché rivelano, a chiunque apra il sorgente, esattamente cosa l'autore non aveva verificato.

---

## 9. Annunciare e consegnare il feed

Un feed serve a poco se nessuno lo trova. Va annunciato nell'`<head>` dell'HTML, così browser e lettori RSS lo scoprono da soli:

```html
<link rel="alternate" type="application/rss+xml" title="Feed Notizie" href="/api/rss.php" />
```

E va consegnato ai distributori. SPW ha un bottone «Copia RSS» nell'area admin, che mette l'indirizzo negli appunti con un click; SR mostra l'URL in dashboard (è ciò a cui serve davvero `feed_config.php`, una volta tolta la pretesa di privatezza). Piccola UX redazionale: dare a chi pubblica un modo per passare il feed a un aggregatore o a un bot senza trascriverlo a mano.

---

## In sintesi

Il feed è la parte più tranquilla del giro del contenuto: l'emettitore che chiude il buco XSS, per sottrazione o per escape. Ma intorno a questa quiete i tre siti raccontano tre storie diverse: SPW è minimale e disciplinato (GUID stabile, regola di visibilità rispettata, errori a parte); SR è più ricco e più frammentato, con un proxy inbound ben difeso, un dispenser che finge una privatezza che non c'è, e qualche regressione (le bozze nel feed, il GUID che ripubblica); DIS fa solo podcast, sui default, con i dubbi dell'autore ancora scritti nel codice. Il filo dei quattro emettitori, intanto, ha un'ultima casella da riempire: la newsletter.

> [!IMPORTANT]
> **Il Canone**
> - Feed RSS 2.0 valido: header corretto, date RFC-822, URL assoluti, `content` escapato (o non emesso affatto).
> - Il feed è un emettitore del `content`: o lo escapi del tutto o non lo metti dentro.
> - GUID stabile con `isPermaLink="false"` (un URN), non il permalink mutevole.
> - Niente `catch` vuoto che maschera un guasto: meglio un 5xx esplicito. Un proxy inbound va protetto con allowlist host + https-only (anti-SSRF).

---
*Prossimo Capitolo: Newsletter & Email System. L'ultimo emettitore del contenuto, che chiude del tutto il filo, e una scala di quanto si può semplificare un sistema di posta prima che diventi pericoloso.*
