# Mappatura — SitoRuntime — C4: Content APIs (news + speakers + podcasts)

> **Stato:** COMPLETATO
> **Sessione:** 15 · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `SitoRuntime/`)
> - `public/api/news.php` (lettura pubblica: lista paginata `{success,data,meta}` + lookup per slug; visibilità `published_at<=now`; cache su file `.cache/news_*.json`)
> - `public/api/admin.php:236-345` (rami contenuto gated: `action=list`/`get`/`save`/`delete`; slug, author, draft/published, programmati, invalidazione cache)
> - `public/api/speakers.php` (CRUD speaker: GET lista array-nudo + GET singolo normalizzato; colonne JSON `tags`/`programs`/`social_urls`; `is_founder`; gate `isAdmin`+CSRF)
> - `public/api/podcasts.php` (CRUD podcast: lista array-nudo; slug con `iconv` translit; record link esterni `name/url/description/image`)
> - `public/api/init_mysql.php:16-91` (schema `news`/`speakers`/`podcasts`, letto per la forma dei record — dettaglio DB già in SR-C1)
> - Letti come consumatori (contratti già mappati in SR-C3): `src/utils/news.ts`, `src/pages/Admin.tsx`, `src/pages/Podcasts.tsx`, `src/pages/About.tsx`

## 1. Cosa fa (sintesi narrativa)

C4 è il **lato server dei contenuti** di SitoRuntime: gli endpoint PHP che la SPA (SR-C3) interroga
per leggere e scrivere i tre domini editoriali del sito — **news** (articoli), **speakers** (gli
host della radio) e **podcasts** (i programmi/feed). Come in SimonePizziWebSite non c'è router
framework: ogni file `.php` è una risorsa, con la struttura "thin stack" di SR-C1 (prologo `cors.php`
+ `getDB()` lazy con `static` copia-incollata in ogni file). Ma rispetto a SPW-C4 la geografia è
**più piatta e più frammentata**, ed è l'osservazione centrale della card:

1. **`news.php` — sola LETTURA pubblica.** A differenza di `articles.php` di SPW (che è un
   endpoint-router CRUD completo su `REQUEST_METHOD`), in SitoRuntime la lettura pubblica e la
   scrittura admin **vivono in file diversi**: `news.php` fa **solo GET** (lista paginata + singolo
   per slug), mentre il CRUD passa da `admin.php?action=…`. `news.php` è quindi un endpoint
   "vetrina": filtra solo i `published`, pagina con `{success,data,meta}`, e ha una **cache su file
   JSON** (`.cache/news_p{page}_l{limit}.json`, TTL 300s) con header `X-Cache: HIT|MISS`.

2. **`admin.php` — il CRUD dei contenuti (gated).** I rami `action=list/get/save/delete`
   (`admin.php:236-345`) sono la dashboard-side delle news: lista paginata admin (vede anche bozze e
   programmati), get singolo, save (create/update con slug+author+status), delete. Tutto dietro il
   gate `isLoggedIn()` di SR-C2 (`admin.php:231`) + `validateCsrf()` sui rami mutativi. **Non esiste
   un `articles.php` mutativo separato**: il CRUD news è una *sezione* del file admin tuttofare.

3. **`speakers.php` e `podcasts.php` — endpoint-router classici su `REQUEST_METHOD`.** Questi due,
   invece, seguono il pattern SPW: un file = una risorsa, `if ($method === 'GET'|'POST'|'DELETE')`
   nello stesso file, gate `isAdmin()`+CSRF sui rami mutativi, lettura pubblica. Sono i due domini
   "anagrafici" del sito radio: gli speaker (con bio, foto, programmi, social) e i podcast (link
   esterni ai programmi).

La frammentazione (lettura news in un file, scrittura news in un altro, speakers/podcasts in file a
sé con CRUD completo) è la prima differenza forte da SPW, dove ogni dominio è UN endpoint-router
omogeneo.

## 2. Pattern miniCMS rilevanti

- **Separazione lettura-pubblica / scrittura-admin in file diversi** (`news.php` GET-only vs
  `admin.php?action=save/delete`): in SitoRuntime il dominio "news" è spezzato in due file con due
  responsabilità (vetrina cacheabile vs CRUD gated), invece dell'endpoint-router unico di SPW. È una
  scelta che semplifica la cache pubblica (un file fa solo letture cacheabili) ma sparpaglia la
  logica di un dominio su due punti.
- **Tre buste di lista DIVERSE per tre domini** (la radice del "non-Double-Read" visto da SR-C3):
  | Endpoint | GET lista | GET singolo |
  |---|---|---|
  | `news.php` (pubblico) | **`{success, data, meta:{current_page,total_pages,total_items,limit}}`** (`news.php:67-76`) | **`{success, data}`** (`news.php:31`) / 404 `{success:false,error}` |
  | `admin.php?action=list` | **`{success, articles, total, page, limit}`** (`admin.php:245`) | **`{success, article}`** (`admin.php:258`) |
  | `speakers.php` | **array NUDO** (`speakers.php:113-116`) | oggetto normalizzato NUDO (`speakers.php:68`) / `{error}` |
  | `podcasts.php` | **array NUDO** (`podcasts.php:35`) | — (no GET singolo) |
  Tre forme di lista: `{success,data,meta}`, `{success,articles,total}`, array nudo. Il client (SR-C3)
  conosce ognuna "per forma nota" e usa la guardia `Array.isArray` su speakers/podcasts. Qui la mappa
  server è **completa**: è un mosaico, non un contratto unico esteso in-place come in SPW.
- **Paginazione backend-driven con `meta` pre-calcolato** (`news.php:55-76`): `COUNT(*)` con le
  **stesse** condizioni di visibilità, poi `LIMIT ? OFFSET ?`. A differenza di SPW (che ritorna il
  `total` grezzo e lascia il client calcolare `hasMore`), SitoRuntime **calcola `total_pages` lato
  server** (`ceil($totalItems/$limit)`, `news.php:59`) e lo mette in `meta` — il client legge
  `current_page < total_pages` (vedi `News.tsx` load-more, SR-C3). I parametri `LIMIT/OFFSET` qui
  **NON** sono bindati con `PDO::PARAM_INT` esplicito (`news.php:63` passa l'array `[$now,$limit,$offset]`
  a `execute()`): regge perché `$limit`/`$offset` sono castati `(int)` a monte (`news.php:41-42`) e
  ATTR_EMULATE_PREPARES è attivo di default → vedi §4.
- **Visibilità pubblico/admin come due query in due file** (`news.php:56,62` vs `admin.php:242-243`):
  la regola pubblica `published_at <= now AND (status='published' OR status IS NULL)` vive in
  `news.php`; la dashboard (`admin.php?action=list`) fa una `SELECT` **senza** quel filtro → l'admin
  vede tutto (bozze, programmati). Stessa logica di SPW ("un endpoint, due audience") ma realizzata
  con **due query in due file** invece che con un `AND` condizionale nello stesso endpoint.
- **Compatibilità schema con `OR status IS NULL`** (`news.php:25,56,62`): la colonna `status` **non è
  nello schema base** (`init_mysql.php` non la prevede) — è aggiunta dalla migrazione idempotente
  `apply_v291_status` (`admin.php:459-470`, → C13). Le righe create *prima* della migrazione hanno
  `status NULL`; il `OR status IS NULL` le tratta come pubblicate. È una difesa di retrocompatibilità
  "schema che evolve sotto i piedi" — gold per il box migrazioni.
- **Cache di contenuto su file con invalidazione esplicita** (`news.php:44-50,78` + `admin.php:297,310,341`):
  la lista pubblica è materializzata in `.cache/news_*.json` (TTL 300s, `X-Cache` header); ogni
  `save`/`delete` fa `array_map('unlink', glob($cacheDir.'/news_*.json'))` per invalidare. È un
  **layer di cache applicativo** che SPW non ha in C4. (La *strategia* di cache/SEO è dominio C7: qui
  annotata perché è scritta dentro gli endpoint di contenuto — vedi §8.)
- **Colonne JSON native MySQL con fallback legacy-string** (`speakers.php:50-53,95-97`): `tags`,
  `programs`, `social_urls` sono colonne `JSON` (`init_mysql.php:67-69`). In lettura il codice
  gestisce **entrambi** i formati: `if (is_string($x)) $x = json_decode($x, true)` — perché a seconda
  del driver/versione MySQL la colonna JSON può tornare come stringa o già decodificata. Pattern
  "non fidarti del tipo che ti torna dal driver". È il motivo per cui il client (SR-C3) riceve array
  veri e usa `Array.isArray`.
- **Speaker normalizzato camelCase lato server** (`speakers.php:55-67,99-110`): l'endpoint **rimappa**
  i nomi colonna snake_case (`long_bio`, `is_founder`, `sort_order`) in camelCase (`longBio`,
  `isFounder`, `sortOrder`) e castinga i tipi (`(bool)`, `(int)`) **prima** di serializzare. È un
  mini-mapper *lato server* (in SPW il mapping snake→camel è tutto client in `mappers.ts`). Lista e
  singolo differiscono: il singolo include `longBio`, la lista lo esclude "for performance"
  (`speakers.php:73`).
- **Tre filosofie di slug nello STESSO sito** (gold per §4): `admin.php` news →
  `preg_replace('/[^A-Za-z0-9-]+/','-', $title)` **senza** gestione accenti (`admin.php:274-276`);
  `podcasts.php` → `iconv('UTF-8','ASCII//TRANSLIT')` per traslitterare gli accenti (`podcasts.php:55-60`);
  speakers → **nessuno slug** (l'`id` è la PK `VARCHAR` fornita dal client). Tre approcci divergenti,
  contro la singola tabella-accenti coerente di SPW.

## 3. Codice chiave (stralci con origine)

**Lista pubblica: COUNT + LIMIT/OFFSET, busta `{success,data,meta}` con `total_pages` server-side** — `news.php:55-76`:

```php
// Get total count (Published only)
$stmtCount = getDB()->prepare("SELECT COUNT(*) FROM news WHERE published_at <= ? AND (status = 'published' OR status IS NULL)");
$stmtCount->execute([$now]);
$totalItems = $stmtCount->fetchColumn();
$totalPages = ceil($totalItems / $limit);

$stmt = getDB()->prepare("SELECT id, slug, title, summary, cover_image, author, category, created_at, published_at FROM news WHERE published_at <= ? AND (status = 'published' OR status IS NULL) ORDER BY published_at DESC LIMIT ? OFFSET ?");
$stmt->execute([$now, $limit, $offset]);
$articles = $stmt->fetchAll();

$response = json_encode([
    'success' => true,
    'data' => $articles,
    'meta' => ['current_page'=>$page, 'total_pages'=>$totalPages, 'total_items'=>$totalItems, 'limit'=>$limit]
]);
```

**Visibilità con separatore SPAZIO (NON 'T') + cache su file** — `news.php:44-63`:

```php
$cacheFile = "{$cacheDir}/news_p{$page}_l{$limit}.json";
if (file_exists($cacheFile) && (time() - filemtime($cacheFile)) < 300) {
    header('X-Cache: HIT'); readfile($cacheFile); exit;          // HIT: salta del tutto il DB
}
$now = date('Y-m-d H:i:s');   // <-- separatore SPAZIO, formato MySQL DATETIME canonico
```

> **Nota incidente 'T' (SR-C1 / `debug_time.php`):** la query di produzione di `news.php` usa
> `date('Y-m-d H:i:s')` (separatore spazio), che combacia col formato `DATETIME` MySQL. L'incidente
> del separatore **'T'** documentato in `debug_time.php` riguardava un confronto-stringa con formato
> ISO (`...T...`) che NON ordina come un `DATETIME`; **qui la query è nella forma corretta**. Il
> rischio resta latente solo se un `published_at` venisse salvato in formato ISO con la 'T' (vedi §8).

**Slug news SENZA normalizzazione accenti + author che è sempre 'Admin' + programmati** — `admin.php:272-285`:

```php
$rawSlug = $input['slug'] ?? '';
if (empty($rawSlug)) {
    $slug = strtolower(trim(preg_replace('/[^A-Za-z0-9-]+/', '-', $title)));  // "caffè" -> "caff-"
} else {
    $slug = strtolower(trim(preg_replace('/[^A-Za-z0-9-]+/', '-', $rawSlug)));
}
$published_at = $input['published_at'] ?? date('Y-m-d H:i:s');   // futuro = post programmato
$author = $_SESSION['username'] ?? 'Admin';                       // username NON in sessione (SR-C2) -> SEMPRE 'Admin'
$status = in_array($input['status'] ?? '', ['draft','published']) ? $input['status'] : 'published';
```

**Unicità slug REATTIVA: niente pre-check, si affida al vincolo UNIQUE + catch 23000** — `admin.php:314-320`:

```php
} catch (PDOException $e) {
    if ($e->getCode() == 23000) {                 // violazione UNIQUE su news.slug
        sendError('Slug already exists. Please choose a specific slug.');
    } else {
        error_log('Runtime DB Error [save_article]: ' . $e->getMessage());
        sendError('Errore del server. Riprova più tardi.', 500);
    }
}
```

**Speaker: colonna JSON con fallback legacy-string + normalizzazione camelCase/tipi** — `speakers.php:91-110`:

```php
$tags = $s['tags']; $programs = $s['programs']; $socialUrls = $s['social_urls'];
if (is_string($tags))      $tags = json_decode($tags, true);        // JSON nativo O stringa legacy
if (is_string($programs))  $programs = json_decode($programs, true);
if (is_string($socialUrls))$socialUrls = json_decode($socialUrls, true);
$speakers[] = [
    'id'=>$s['id'], 'name'=>$s['name'], 'role'=>$s['role'], 'image'=>$s['image'], 'bio'=>$s['bio'],
    'tags'=>$tags ?: [], 'programs'=>$programs ?: [], 'socialUrls'=>$socialUrls ?: (object)[],
    'isFounder'=>(bool)$s['is_founder'], 'sortOrder'=>(int)$s['sort_order']
];
echo json_encode($speakers);   // ARRAY NUDO
```

**Slug podcast CON traslitterazione accenti (iconv) — terza filosofia di slug** — `podcasts.php:53-65`:

```php
if (empty($slug)) {
    $cleanName = iconv('UTF-8', 'ASCII//TRANSLIT', $input['name']);   // "Caffè" -> "Caffe"
    $slug = preg_replace('/[^a-zA-Z0-9\s-]/', '', $cleanName);
    $slug = preg_replace('/[\s-]+/', '-', $slug);
    $slug = strtolower(trim($slug, '-'));
    if (empty($slug)) $slug = 'podcast-' . time();
}
```

## 4. Problemi riscontrati & soluzioni

- **GOLD — Tre filosofie di slug nello stesso codebase.** `admin.php` (news) **non gestisce gli
  accenti** (`admin.php:274`): un titolo "Caffè letterario" diventa slug `caff-letterario` (la `è`
  cade nel `[^A-Za-z0-9-]+` → trattino). `podcasts.php` invece **traslittera** con `iconv ASCII//TRANSLIT`
  (`podcasts.php:55`) → `caffe`. SPW ha una **terza** soluzione ancora (tabella accenti→sostituti).
  Stesso problema (slug ASCII da testo italiano), tre risposte incoerenti nello stesso ecosistema:
  box "lo slug accentato: tre modi di sbagliarlo/risolverlo".
- **GOLD — `author` è SEMPRE 'Admin' (filo che si chiude da SR-C2/C3).** `admin.php:284`
  `$author = $_SESSION['username'] ?? 'Admin'`. SR-C2 ha mostrato che il login salva **solo**
  `user_id` e `role` in sessione, **non** `username` (`admin.php:123-124`). Quindi `$_SESSION['username']`
  è sempre `null` → ogni articolo salvato ha `author = 'Admin'`, anche se a video (SR-C3) il nome del
  login appare correttamente (rispedito nel body, non in sessione). La firma dell'articolo è una
  finzione: box "l'autore che non c'è — quando la sessione non porta ciò che credi".
- **Unicità slug reattiva invece che preventiva.** `admin.php` non fa il pre-check + suffisso di SPW:
  prova l'INSERT/UPDATE e **cattura** la violazione `UNIQUE` (errno 23000) restituendo "Slug already
  exists" (`admin.php:315`). `podcasts.php` invece **pre-controlla** e appende `-time()` in caso di
  collisione (`podcasts.php:76-91`). Due strategie opposte (reattiva vs preventiva) di nuovo nello
  stesso sito. La reattiva è più semplice ma scarica sull'utente la risoluzione del conflitto.
- **`LIMIT ?/OFFSET ?` senza `PARAM_INT` esplicito.** `news.php:63` e `admin.php:244` passano gli
  interi via array a `execute()`, non con `bindValue(..., PDO::PARAM_INT)` come fa SPW. Regge perché
  (a) i valori sono castati `(int)` a monte e (b) il driver MySQL di SR-C1 ha `ATTR_EMULATE_PREPARES`
  di default ON, che interpola lato PHP senza quoting fatale. Funziona, ma è il tipo di dipendenza
  implicita ("regge per via di un'impostazione del driver") da segnalare → ponte SR-C1.
- **Nessun filtro/ricerca/categoria reale.** La lista pubblica `news.php` **non** accetta filtri:
  niente `?category=`, niente `?q=`, niente `?tag=`. `category` è una **stringa libera**
  (`VARCHAR(100) DEFAULT 'News'`, `init_mysql.php:29`) senza tabella categorie, gerarchia o
  navigazione; **non esistono** `categories.php`/`tags.php`/`navigation.php`/`search.php`. SitoRuntime
  è **molto più piatto** di SPW su questo asse (vedi §6, voci N/A). Limite onesto: la ricerca/filtro è
  delegata interamente al client sui dati già scaricati.
- **`status IS NULL` come debito di migrazione.** Il `OR status IS NULL` (`news.php:56`) è necessario
  solo perché la colonna `status` è stata aggiunta dopo (migrazione `apply_v291_status`). È una
  pezza corretta ma permanente: ogni query di visibilità porta con sé la cicatrice della migrazione.
  → C13.
- **La cache pubblica può servire un articolo "spubblicato" fino a 5 minuti.** `news.php` invalida
  `news_*.json` su save/delete da `admin.php`, ma se un `published_at` programmato scatta (passa da
  futuro a passato) **senza** un save, la lista cacheata non si rigenera fino allo scadere del TTL
  (300s). Finestra di incoerenza accettabile, da conoscere. → ponte C7 (strategia cache).

## 5. Estetica / UX (moderna ma funzionale)

C4 è back-end, ma alcune scelte server servono la UX:

- **`total_pages` pre-calcolato lato server** (`news.php:59`): il client non deve sapere come si
  pagina, riceve già "sei a pagina X di Y" → il load-more di `News.tsx` (SR-C3) è banale
  (`current_page < total_pages`). Decisione server al servizio di un client minimale.
- **Lista speaker "alleggerita"** (`speakers.php:73,84`): la lista esclude `long_bio` (LONGTEXT)
  "for performance", servendo solo il necessario per le card; il `long_bio` arriva solo nel GET
  singolo. Ottimizzazione payload invisibile all'utente.
- **`X-Cache: HIT|MISS`** (`news.php:47,80`): header diagnostico che rende visibile (a chi ispeziona)
  se la pagina arriva da cache o dal DB — micro-trasparenza operativa.
- **Ordinamento speaker manuale + alfabetico** (`speakers.php:84` `ORDER BY sort_order ASC, name ASC`):
  l'admin decide l'ordine in vetrina (`sort_order`), a parità vince l'alfabetico. Controllo
  redazionale leggero, gemello del pin di categoria di SPW ma senza la logica "un solo pin".

## 6. Differenze rispetto agli altri siti

Il confronto con **SPW-C4** è il cuore della card.

| Aspetto | SimonePizziWebSite (SPW-C4) | SitoRuntime (questa card) |
|---|---|---|
| **Struttura endpoint** | un endpoint-router CRUD per dominio (`articles.php` GET+POST+PUT+DELETE+PATCH) | **frammentato**: news lettura in `news.php`, news scrittura in `admin.php?action=…`; speakers/podcasts router classici |
| **Busta lista** | **Double Read**: solo `articles` lista = `{data,total}`, resto array nudo | **tre buste diverse**: `{success,data,meta}` (news), `{success,articles,total}` (admin), array nudo (speakers/podcasts) |
| **Wrapper `success`** | assente (oggetto o array diretti) | **presente** su news/admin (`{success:true,…}`), assente su speakers/podcasts (array nudo) |
| **Paginazione** | `total` grezzo, client calcola `hasMore`; `PARAM_INT` esplicito | `total_pages` **pre-calcolato** server in `meta`; **niente `PARAM_INT`** (regge su cast+emulate) |
| **Categorie** | gerarchia `parent_id` + filtro "contenitore" via `IN` sottocategorie + `navigation.php` ad albero | **N/A**: `category` stringa libera, nessuna tabella/gerarchia/navigazione |
| **Tag** | M:N `article_tags` + cache CSV legacy (doppia scrittura) | **N/A** per gli articoli; gli speaker hanno un campo `tags` **JSON denormalizzato** (cosa diversa) |
| **Ricerca** | `search.php` `LIKE` unificata articoli+progetti, campo `type` | **N/A**: nessun endpoint di ricerca; filtro delegato al client |
| **Slug** | una tabella accenti→sostituti coerente | **tre filosofie**: news senza accenti, podcast con `iconv`, speaker senza slug (id client) |
| **Unicità slug** | pre-check + suffisso `-timestamp` | news **reattiva** (catch UNIQUE 23000); podcast **preventiva** (`-time()`) |
| **Visibilità** | `AND status='published' AND published_at<=now` condizionale nello **stesso** endpoint | **due query in due file** (news.php pubblica vs admin.php list); `OR status IS NULL` retro-compat |
| **Confronto data** | `published_at <= ?` con ora forzata `Europe/Rome` | `published_at <= date('Y-m-d H:i:s')` (separatore spazio, NON 'T'); incidente 'T' = `debug_time.php` (SR-C1), non qui |
| **`author`** | salvato reale (presumibilmente) | **sempre 'Admin'** (username non in sessione, SR-C2) |
| **Cache di contenuto** | nessuna in C4 | **cache su file** `.cache/news_*.json` TTL 300s + invalidazione su save/delete |
| **Colonne JSON** | tag in tabella relazionale | `tags`/`programs`/`social_urls` colonne `JSON` native con fallback legacy-string |
| **Post programmati** | sì (`published_at` futuro, no cron) | sì (identico), ma la cache può ritardare la comparsa fino a 5′ |

Sintesi: **SPW-C4** è un CMS editoriale "ricco" (categorie gerarchiche, tag M:N, ricerca, un endpoint
per dominio); **SitoRuntime-C4** è **più piatto e più sparpagliato** — niente tassonomie, `category`
stringa libera, lettura/scrittura news in file separati, ma in più una **cache di contenuto su file**
e le **colonne JSON** sugli speaker che SPW non ha. La novità di SR è la combinazione cache-su-file +
JSON nativo; il "debito" è la frammentazione e le tre filosofie di slug.

Per DISINTELLIGENZA/FDCA (SQLite, festival) il dominio contenuti sarà verosimilmente ancora più
minimale (news/feed per il festival): termine di paragone alle rispettive card C4.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **Lettura e scrittura di un dominio in file separati** (news.php vs admin.php) | Cap. "L'anatomia di un endpoint": variante "vetrina cacheabile + CRUD altrove" |
| **Tre buste di lista diverse** (`{success,data,meta}` / `{success,articles,total}` / array nudo) | Cap. "Contratti di payload elastici": il mosaico di SR vs il Double Read di SPW |
| **`total_pages` pre-calcolato server** vs `total` grezzo client | Box "chi calcola la paginazione: server o client?" |
| **Tre filosofie di slug nello stesso sito** (no-accenti / iconv / id-client) | Box "lo slug accentato: tre modi nello stesso codebase" (alto valore) |
| **L'autore che è sempre 'Admin'** (sessione che non porta lo username) | Box problemi/soluzioni "quando la sessione non contiene ciò che credi" (ponte SR-C2/C3) |
| **Unicità slug: reattiva (catch UNIQUE) vs preventiva (pre-check)** | Box "due modi di garantire l'unicità di uno slug" |
| **Cache di contenuto su file + invalidazione `glob+unlink`** | Cap. "Cache senza Redis: file JSON nel thin stack" (ponte C7) |
| **Colonne JSON native con fallback legacy-string** | Box "il campo JSON che a volte torna stringa" |
| **`OR status IS NULL` come cicatrice di migrazione** | Box "la query che porta i segni di una migrazione" (ponte C13) |
| **`category` stringa libera vs tassonomia** | Box "quando NON ti serve una tabella categorie" |

## 8. Note / domande aperte

- **Puntatori ad altri cluster** (annotati qui, NON mappati in questa card):
  - **Cache su file `.cache/news_*.json` + `seo_news_*.json`** (`news.php:44`, `admin.php:292-297`):
    la *strategia* di cache e SEO-cache è dominio **C7** (SEO & Prerendering + seo-cache). Qui
    interessa solo che la scrittura/invalidazione della cache di **contenuto** vive dentro gli
    endpoint C4. La generazione di `seo_news_*.json`/`seo_speaker_*.json` su save → C7.
  - **`cover_image`/`image` come stringa URL** in news/speakers/podcasts → **C5** (Media/Upload): C4
    memorizza solo il percorso; la gestione del file (upload, WebP, flat `/uploads/`) è di C5. Gli
    one-shot `optimize_webp`/`fix_image_paths` (`admin.php:347-371,472-523`) toccano `news.content`,
    `news.cover_image`, `speakers.image` → logica **media** = C5, **storia migratoria** = C13.
  - **`content` salvato grezzo** (`admin.php:280,289,302`): `news.content` è salvato senza
    sanitizzazione server (come SPW). La difesa XSS-stored è a **render-time** lato client (DOMPurify
    in `Article.tsx`, vedi SR-C3) → **C6** (Editor/sanitizzazione). Qui solo annotato.
  - **`podcasts.url`**: è il link esterno al programma/feed; la *syndication* RSS (feed news) è
    **C8** (`feed_news_rss.php`, già intravisto in SR-C3/glob). I podcast qui sono semplici record
    link, non episodi. → C8.
  - **Migrazioni dentro `admin.php`** (`apply_v291_status`, `apply_v293_newsletter`,
    `optimize_webp`, `fix_image_paths`) e `test_smtp`: sono **azioni one-shot/diagnostiche** ospitate
    nell'endpoint admin → DB evolution **C13**, SMTP/newsletter **C9**. Fuori ambito C4 (annotate).
  - **Gate `isLoggedIn`/`isAdmin`/`validateCsrf`**: meccanica già mappata in **SR-C2**. Qui solo
    osservato *dove* è applicata (news save/delete = `isLoggedIn`+CSRF; speakers/podcasts = `isAdmin`+CSRF).
- **Asimmetria di gate tra domini:** news CRUD richiede solo `isLoggedIn()` (admin **o** editor),
  mentre speakers/podcasts richiedono `isAdmin()` (`speakers.php:124`, `podcasts.php:42`). Quindi un
  *editor* può scrivere articoli ma non toccare speaker/podcast. Coerente coi ruoli di SR-C2, ma è una
  regola implicita sparsa, non documentata in un punto unico.
- **Rischio 'T' latente:** la query è corretta (`date('Y-m-d H:i:s')`), ma `published_at` arriva da
  `$input['published_at']` (`admin.php:283`) senza normalizzazione di formato: se il client inviasse
  un ISO `2026-06-15T10:00:00`, verrebbe salvato così e il confronto `<=` (string-compare in
  emulate-prepares) potrebbe sfasare. Da verificare lato client che `published_at` sia inviato in
  formato MySQL. → ponte SR-C1 (`debug_time.php`) / C13.
- **Nessuna credenziale/segreto** negli endpoint di contenuto (connessione via `db.php`/`db_credentials.php`
  di SR-C1).
- Versione del sito al momento della mappatura: **2.9.13** (coerente con SR-C1/C2/C3); le migrazioni
  citate sono marcate `v2.9.1` (status), `v2.9.2` (optimize_webp), `v2.9.3` (newsletter double opt-in).
