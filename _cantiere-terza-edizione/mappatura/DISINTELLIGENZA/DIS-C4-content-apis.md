# Mappatura — DISINTELLIGENZA — C4: Content APIs (news + podcasts)

> **Stato:** COMPLETATO
> **Sessione:** 23 · **Data:** 2026-06-18 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `DISINTELLIGENZA/`)
> - `public/api/news.php` (endpoint-router su `REQUEST_METHOD`: GET pubblico lista/slug + POST admin `?action=create/update/delete`)
> - `public/api/podcasts.php` (GET lista array-nudo + POST admin create/delete; `CREATE TABLE` inline divergente)
> - `public/api/init_db.php:33-44,72-83` (schema fossile `news`/`podcasts` — letto per la forma, dettaglio in DIS-C1)
> - `public/api/feed.php` (RSS — solo puntatore a C8)
> - confronto: `SR-C4-content-apis.md`, `SPW-C4-content-apis.md`

## 1. Cosa fa (sintesi narrativa)

C4 è il **lato server dei contenuti editoriali** di DISINTELLIGENZA: le **news** (gli articoli del
sito-festival) e i **podcast** (episodi audio). È il dominio "contenuto" minore rispetto al cuore del
sito, che è il festival (participants/votes → C10); qui si gestisce solo il blog/news e la lista
episodi.

La struttura è quella "thin stack" di DIS-C1: ogni file `.php` è una risorsa autonoma, bootstrap
inline (`require_once 'db.php'; session_start(); header('Content-Type: application/json');
$pdo = Database::connect();`, `news.php:1-7`), nessun framework. Ma rispetto agli altri due siti la
**forma strutturale è la più semplice in assoluto**:

1. **`news.php` — endpoint-router CRUD su `REQUEST_METHOD` in UN solo file.** Qui DIS assomiglia a
   **SPW** (un endpoint-router per dominio), **non** a SR (che spezza lettura news e scrittura news in
   due file). `news.php` fa GET pubblico (lista paginata + dettaglio per slug, `:15-49`) e POST admin
   con sub-dispatch `?action=create|update|delete` (`:51-105`). Un file, una risorsa, dispatch sul
   verbo + sull'azione.

2. **`podcasts.php` — endpoint-router minimale.** GET lista (array nudo, `:20-22`) + POST admin
   create/delete (`:23-54`), gate `role==admin` (più stretto di news, che accetta anche `editor`).
   In testa fa un `CREATE TABLE IF NOT EXISTS podcasts` **inline** (`:8-16`) "Quick Migration for this
   step" — auto-scaffolding difensivo, ma con uno schema **divergente** da `init_db.php` (vedi §4).

La cosa centrale di questa card è quanto DIS **toglie**: nessuna busta `{success}` né `{data,total}`
(risposte sempre **nude**), nessun `meta` di paginazione, nessuna tabella categorie/tag, nessuna
ricerca, nessun campo `author`. È la versione "grado zero" del CMS, ancora più scarna di SR-C4 (che
pure era più piatto di SPW).

## 2. Pattern miniCMS rilevanti

- **Endpoint-router su `REQUEST_METHOD` + sub-action** (`news.php:6,51,59`): GET pubblico, POST gated
  con `$_GET['action']` per scegliere create/update/delete. È il pattern SPW (un file = una risorsa
  con dispatch sul verbo), in contrasto con la frammentazione di SR (news lettura/scrittura in file
  diversi). DIS è **strutturalmente più vicino a SPW** che a SR, qui.
- **Risposte SEMPRE nude — "busta zero"** (`news.php:34,48`; `podcasts.php:22`): la GET lista fa
  `echo json_encode($stmt->fetchAll())` (array nudo), la GET dettaglio `echo json_encode($news)`
  (oggetto nudo), il 404 è `{status:'error',message}`. Niente wrapper `{success,data,meta}` di SR,
  niente Double Read `{data,total}` di SPW: il client riceve sempre l'oggetto/array diretto. È il
  contratto di payload **più semplice dei tre siti**.
- **Visibilità calcolata IN-QUERY con `CURRENT_TIMESTAMP` SQLite** (`news.php:28,42`): la regola
  pubblica è `(status = 'published' OR status = 'scheduled') AND published_at <= CURRENT_TIMESTAMP`.
  La differenza forte: DIS **non** costruisce "adesso" in PHP con `date('Y-m-d H:i:s')` (SR) o
  `date()`+timezone (SPW) — lascia che **sia SQLite a calcolare il presente** dentro la query. Questo
  **aggira del tutto** l'incidente del separatore `T` e del confronto-stringa che tormentava SR
  (`debug_time.php`, SR-C1) — ma introduce un rischio diverso: `CURRENT_TIMESTAMP` in SQLite è in
  **UTC**, mentre i `published_at` vengono salvati con `date('Y-m-d H:i:s')` nel fuso del server
  (timezone forzato solo in `index.php`, DIS-C1) → possibile sfasamento orario sui post programmati
  (vedi §4).
- **Slug senza gestione accenti** (`news.php:10-13`, `createSlug`): `preg_replace('/[^A-Za-z0-9-]+/',
  '-', $string)` + lowercase + trim. "Caffè letterario" → `caff-letterario` (la `è` cade nel set
  negato). È la **stessa filosofia di SR news** (`admin.php` senza accenti), diversa da SPW (tabella
  accenti) e dal `iconv` dei podcast SR.
- **Unicità slug preventiva (pre-check + suffisso `time()`)** (`news.php:71-75`): `SELECT count(*)`,
  se >0 appende `'-'.time()`. È l'approccio **preventivo** (come i podcast di SR), non quello reattivo
  catch-UNIQUE delle news di SR. NB: c'è una piccola race (check-then-insert non atomico), mitigata
  solo dal basso traffico.
- **Auto-scaffolding difensivo inline** (`podcasts.php:7-16`): l'endpoint crea la sua tabella se
  manca, "Quick Migration for this step". Pattern self-healing simile alle micro-migrazioni di SR
  dentro `admin.php`, ma qui dentro l'endpoint di contenuto e con schema divergente (§4).
- **`category` stringa libera, `tags` campo TEXT** (`news.php:77,40`): nessuna tabella categorie/tag,
  nessuna gerarchia, nessuna relazione M:N. Identico a SR (e ancora più spoglio: SR aveva almeno i
  `tags` JSON sugli speaker). Default `category='generale'` (`news.php:77`).
- **`content` salvato grezzo** (`news.php:81`): nessuna sanitizzazione server. La difesa XSS-stored,
  se esiste, è a render-time lato client → puntatore C6/frontend.

## 3. Codice chiave (stralci con origine)

**Endpoint-router GET pubblico + visibilità in-query con `CURRENT_TIMESTAMP`** — `news.php:15-48`:

```php
if ($method === 'GET') {
    $isAdmin = isset($_SESSION['user_id']) && ($_SESSION['role'] === 'admin' || $_SESSION['role'] === 'editor');
    $slug = $_GET['slug'] ?? null;
    $limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 10;
    $page  = isset($_GET['page'])  ? (int)$_GET['page']  : 1;
    $offset = ($page - 1) * $limit;

    if ($slug) {
        $sql = "SELECT * FROM news WHERE slug = ?";
        if (!$isAdmin) {
            $sql .= " AND (status = 'published' OR status = 'scheduled') AND published_at <= CURRENT_TIMESTAMP";
        }
        // ... fetch + echo json_encode($news)  (oggetto NUDO) / 404
    } else {
        $sql = "SELECT id, title, slug, excerpt, cover_image, published_at, category, tags, status FROM news";
        if (!$isAdmin) {
            $sql .= " WHERE (status = 'published' OR status = 'scheduled') AND published_at <= CURRENT_TIMESTAMP";
        }
        $sql .= " ORDER BY published_at DESC LIMIT ? OFFSET ?";
        $stmt = $pdo->prepare($sql);
        $stmt->execute([$limit, $offset]);
        echo json_encode($stmt->fetchAll());   // <-- ARRAY NUDO, nessun meta/total
    }
}
```

**Slug senza accenti + unicità preventiva + create gated** — `news.php:51-84`:

```php
if (!isset($_SESSION['user_id']) || ($_SESSION['role'] !== 'admin' && $_SESSION['role'] !== 'editor')) {
    http_response_code(401);
    die(json_encode(['status' => 'error', 'message' => 'Unauthorized']));
}
// ...
$slug = createSlug($title);                       // "caffè" -> "caff-"
$stmt = $pdo->prepare("SELECT count(*) FROM news WHERE slug = ?");
$stmt->execute([$slug]);
if ($stmt->fetchColumn() > 0) { $slug .= '-' . time(); }   // unicità PREVENTIVA
$category = $data['category'] ?? 'generale';
$status   = $data['status']   ?? 'published';
// INSERT INTO news (..., category, tags, status) VALUES (...);
echo json_encode(['status' => 'success', 'slug' => $slug]);
```

**Podcast: auto-scaffolding inline con schema DIVERGENTE da init_db** — `podcasts.php:8-16,40`:

```php
$pdo->exec("CREATE TABLE IF NOT EXISTS podcasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    audio_url TEXT NOT NULL,
    cover_image TEXT,
    duration TEXT DEFAULT '00:00',
    published_at DATETIME DEFAULT CURRENT_TIMESTAMP
)");                                  // <-- NIENTE colonna `slug` qui...
// ma poi:
$stmt = $pdo->prepare("INSERT INTO podcasts (title, slug, description, audio_url, cover_image, duration) VALUES (?, ?, ?, ?, ?, ?)");  // <-- ...INSERT con `slug`!
```

## 4. Problemi riscontrati & soluzioni

- **GOLD — schema vivo divergente da TUTTI gli scaffolding (rafforza "init mente" di DIS-C1).** La
  lista news SELECTa `category, tags, status` (`news.php:40`) e l'INSERT scrive `category, status`
  (`news.php:81`), ma la tabella `news` di `init_db.php:34-44` **non** ha né `category` né `status`
  (solo id/title/slug/content/excerpt/cover_image/published_at/created_at/tags). E **nessuno** degli
  `update_db_*` (DIS-C1) aggiunge `category`/`status` a `news` (v0.5.4 le *usa* ma non le crea). Quindi
  le colonne esistono solo nel file `.sqlite` vivo, aggiunte a mano o da codice eliso: lo schema reale
  **non è ricostruibile** da nessun file del repo. È la prova pratica del tema DIS-C1 "l'init mente" e
  "la verità è nel `.sqlite`". → Box "lo schema che non vive in nessun file".
- **GOLD — incoerenza `scheduled` vs `published` tra migrazione e query.** `update_db_v0.5.4.php:19`
  (DIS-C1) ha **normalizzato** tutti gli `status='scheduled'` in `'published'` dichiarando "la
  visibilità è ora gestita dalla data". Ma `news.php:28,42` **continua** a includere
  `status = 'scheduled'` nel filtro pubblico. Intento della migrazione (eliminare 'scheduled') e
  codice vivo (che ancora lo accetta) si contraddicono: un residuo non ripulito. Innocuo finché
  nessuno crea più 'scheduled', ma è codice morto che mente sulla logica. → Box "la migrazione che il
  codice ha dimenticato".
- **GOLD — timezone in-query (UTC) vs `published_at` salvato nel fuso server.** Usare
  `CURRENT_TIMESTAMP` di SQLite (`news.php:28,42`) **evita** l'incidente del separatore `T`/confronto-
  stringa di SR (perché il confronto è fatto dal motore, non in PHP). Ma `CURRENT_TIMESTAMP` SQLite
  ritorna **UTC**, mentre `published_at` di default è `date('Y-m-d H:i:s')` (`news.php:66,95`) nel fuso
  del server PHP — e il timezone `Europe/Rome` è forzato **solo in `index.php`**, NON in `news.php`
  (DIS-C1). Risultato: un post programmato può comparire/sparire con uno scarto pari al delta
  server-tz↔UTC (1–2 ore). È lo **stesso bug di fondo** di SR (fuso/confronto data) ma in salsa
  diversa: lì era il formato della stringa, qui è UTC-vs-locale. → Box "tre siti, tre modi di
  sbagliare il fuso sui post programmati".
- **Schema podcast divergente tra inline e init_db.** `podcasts.php:8-16` crea `podcasts` **senza**
  colonna `slug`, ma l'INSERT (`:40`) scrive `slug`. Se la tabella venisse creata da questo statement
  inline (DB fresco), l'INSERT **fallirebbe** (no such column: slug). Funziona solo perché la tabella
  reale esiste già da `init_db.php:73-83` (che lo `slug` ce l'ha). Ennesima "tabella che nessuno crea
  due volte uguale" (gemello del doppio schema `settings` di DIS-C1 e dei 3 schemi `subscribers` di
  SR). → consolidare nel box cross-sito sugli schemi divergenti.
- **Nessun metadato di paginazione.** `news.php` fa `LIMIT ? OFFSET ?` (cast `(int)`, niente
  `PARAM_INT` come SR) ma ritorna un **array nudo**: niente `total`, niente `total_pages`. Il client
  non può sapere quante pagine esistono — può solo chiedere la pagina successiva "alla cieca" finché
  torna vuota. Più minimale di SR (`meta.total_pages`) e di SPW (`{data,total}`). Limite onesto.
- **`UPDATE` news senza controllo di esistenza/owner.** Il ramo `action=update` (`news.php:89-99`)
  fa l'UPDATE diretto per `id` senza verificare che la riga esista né chi sia l'autore (del resto non
  c'è colonna `author`). Un editor può modificare/cancellare qualunque news. Coerente col modello a
  ruoli grezzo (→C2), ma da annotare.
- **Nessun `author`.** A differenza di SR (`author` sempre 'Admin', filo sessione) e SPW, le news di
  DIS **non hanno proprio il concetto di autore**: nessuna colonna, nessun campo nell'INSERT. La firma
  dell'articolo non esiste. Divergenza netta (semplificazione).

## 5. Estetica / UX (moderna ma funzionale)

C4 è back-end, ma alcune scelte servono la UX:

- **Distinzione pubblico/admin nello stesso GET** (`news.php:17,27,41`): l'admin/editor loggato vede
  anche bozze e programmati (salta il filtro `status`/`published_at`), il pubblico no — un endpoint,
  due audience, realizzato con un `if (!$isAdmin)` che **aggiunge** il `WHERE` (più semplice delle due
  query in due file di SR, più simile all'`AND` condizionale di SPW).
- **Post programmati "gratis"** (`news.php:66`): `published_at` futuro = post che appare da solo
  quando la data arriva, senza cron (la query con `CURRENT_TIMESTAMP` lo nasconde finché è futuro).
  Stessa UX redazionale di SPW/SR, ma con il caveat timezone (§4).
- **Contratto di errore JSON uniforme** (`{status:'error',message}`) con 401/404/405 corretti
  (`news.php:36,54,108`): coerenza delle risposte come base dell'estetica "pulita".

## 6. Differenze rispetto agli altri siti

Confronto a **TRE**: DIS-C4 (SQLite vivo) vs SPW-C4 e SR-C4 (MySQL migrati).

| Aspetto | SimonePizziWebSite (SPW-C4) | SitoRuntime (SR-C4) | **DISINTELLIGENZA (questa card)** |
|---|---|---|---|
| **Struttura endpoint** | endpoint-router CRUD per dominio | **frammentato** (news lettura/scrittura in file diversi) | **endpoint-router in un file** (GET+POST `?action`) — come SPW |
| **Busta lista** | Double Read (`{data,total}` solo articoli) | tre buste (`{success,data,meta}` / `{success,articles,total}` / nudo) | **sempre NUDA** (array/oggetto diretto) — "busta zero" |
| **Wrapper `success`** | assente | presente su news/admin | **assente ovunque** |
| **Paginazione** | `total` grezzo + `PARAM_INT` | `total_pages` pre-calcolato server | **nessun metadato** (solo LIMIT/OFFSET, array nudo) |
| **"Adesso" per la visibilità** | PHP `date()` + `Europe/Rome` forzato | PHP `date('Y-m-d H:i:s')` (separatore spazio) | **`CURRENT_TIMESTAMP` SQLite (UTC)** — calcolato dal motore |
| **Incidente data** | — | separatore 'T' (debug_time, SR-C1) | **UTC vs fuso server** (timezone solo in index.php) |
| **Categorie** | gerarchia `parent_id` + navigation | N/A (stringa libera) | **N/A** (stringa libera, default 'generale') |
| **Tag** | M:N `article_tags` | speaker `tags` JSON | **campo TEXT** semplice |
| **Ricerca** | `search.php` unificata | N/A | **N/A** |
| **Slug** | tabella accenti | tre filosofie (no-acc / iconv / id) | **senza accenti** (come SR news) |
| **Unicità slug** | pre-check + suffisso | news reattiva / podcast preventiva | **preventiva** (count + `-time()`) |
| **`author`** | salvato reale | sempre 'Admin' (sessione) | **inesistente** (nessuna colonna) |
| **Cache di contenuto** | nessuna | `.cache/news_*.json` TTL 300s | **nessuna** |
| **Schema fonte di verità** | `migrate_to_mysql.php` | `init_mysql.php` + migrazioni | **solo il `.sqlite` vivo** (init/update non bastano, §4) |

**Sintesi.** DIS-C4 è il CMS **grado-zero**: struttura a endpoint-router come SPW (non frammentato
come SR), ma contratto di payload ridotto all'osso ("busta zero", niente meta), zero tassonomie, zero
autore, zero cache. La sua specificità rispetto agli altri due è il modo di gestire il tempo: delega
"adesso" a `CURRENT_TIMESTAMP` SQLite, evitando l'incidente-stringa di SR ma esponendosi a un
disallineamento UTC↔fuso. E soprattutto rende **tangibile** il tema DIS-C1: lo schema reale
(`category`/`status`) non vive in nessun file del repo, solo nel `.sqlite` — la "verità nel file" del
DB-a-file vivo.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **"Busta zero"**: risposte sempre nude vs Double Read (SPW) vs mosaico (SR) | Cap. "Contratti di payload elastici": il terzo punto della scala (alto valore) |
| **Visibilità in-query con `CURRENT_TIMESTAMP`** vs "adesso" in PHP | Box "chi calcola il presente: PHP o il database?" (ponte SR debug_time) |
| **Timezone UTC vs fuso server sui post programmati** | confluisce nel box "tre siti, tre modi di sbagliare il fuso" |
| **Schema che non vive in nessun file** (`category`/`status` solo nel `.sqlite`) | Box "quando lo scaffolding mente: la verità è nel file DB" (ponte DIS-C1) |
| **La migrazione che il codice ha dimenticato** (`scheduled` normalizzato ma ancora interrogato) | Box "residui di migrazione nel codice vivo" |
| **Schema podcast divergente inline vs init** | consolidare nel box cross-sito "la tabella che nessuno crea due volte uguale" |
| **Slug senza accenti** (terzo caso) | confluisce nel box "lo slug accentato nei tre siti" |
| **CMS senza autore/tassonomie/cache** | Box "quanto puoi togliere a un CMS" (gemello del framing upload di SR-C5) |

## 8. Note / domande aperte

- **Puntatori ad altri cluster** (annotati qui, NON mappati in questa card):
  - `cover_image` come stringa URL in news/podcasts → **C5** (Media/Upload, mappato in coppia in
    questa stessa sessione): C4 salva solo il percorso, il file è gestito da `upload.php`.
  - `content` salvato grezzo (`news.php:81`) → difesa XSS a render-time lato client → **C6/frontend**.
  - `feed.php` (RSS dei contenuti) → **C8** (RSS & Feed): non ispezionato qui se non come puntatore.
  - Gate `$_SESSION['role']` admin/editor (news) vs solo admin (podcasts), `session_start()` per
    endpoint → **C2** (Security & Auth). Asimmetria: editor può scrivere news ma non podcast.
  - `participants` come "contenuto" del festival (iscrizioni, audio) → **C10** (Festival Logic), NON
    C4: i partecipanti non sono contenuto editoriale ma entità di concorso.
  - L'audio dei podcast (`audio_url`) e l'upload relativo → **C5** (`upload.php` type=`audio_podcast`).
- **Da verificare in C2:** il ramo `update`/`delete` di news non controlla esistenza/owner; valutare
  in chiave sicurezza/ruoli.
- **Da verificare in C10:** la `category` libera delle news ha valori speciali legati al festival?
  (qui solo default 'generale').
- Versione del sito al momento della mappatura: **0.5.x** (`package.json`); ultimo `update_db` =
  `v0.5.4` (che ha toccato `news.status`).
