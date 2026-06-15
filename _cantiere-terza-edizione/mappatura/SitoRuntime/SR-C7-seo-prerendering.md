# Mappatura — SitoRuntime — C7: SEO & Prerendering (+ seo-cache)

> **Stato:** COMPLETATO
> **Sessione:** 16 (coppia SR-C7 + SR-C8) · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `SitoRuntime/`)
> - `public/index.php` (**SEO Engine v3.0** — Dynamic Rendering ibrido crawler/umano: routing, query DB, JSON-LD, iniezione meta, HTML server-side per i bot) — **cuore di C7**
> - `public/sitemap.php` (sitemap XML dinamica: home + statiche + news + speakers + podcast; `baseUrl` da `HTTP_HOST`)
> - `public/robots.php` (robots.txt dinamica: Allow/Disallow + blocco Ahrefs/Semrush/DotBot + `Crawl-delay` + puntatore sitemap)
> - `public/.htaccess:32-35,57-85` (deny by-prefix dei file di manutenzione; rewrite `sitemap.xml`→`sitemap.php`, `robots.txt`→`robots.php`; blocco `^api/\.cache`; fallback SPA su `index.php`)
> - `public/api/rebuild_seo_cache.php` (**one-shot v2.6.2** — rigenera `seo_news_*.json`/`seo_speaker_*.json` per le entità pre-esistenti; "da cancellare dopo l'uso")
> - `public/api/debug_seo.php` (diagnostica: dump testuale di `news.id/slug/title/cover_image`)
> - `public/api/admin.php:292-297,305-310,340-342` (scrittura/invalidazione della **seo-cache** `seo_news_*.json` su save/delete news — la *strategia*, già intravista in SR-C4)
> - `public/api/speakers.php:156-160,170-174,193-195` (scrittura/invalidazione `seo_speaker_*.json` su save/delete speaker)
> - `src/components/SEO.tsx` (componente client: aggiorna `document.title`/meta/OG/Twitter via `useEffect`; montato in tutte le pagine pubbliche)
> - **Controprova grep** (`seo_news_|seo_speaker_|\.cache|seoData` su `*.php` e su `src/`): **nessun lettore** dei file `seo_*.json` in tutto il codebase — vedi §4 (GOLD seo-cache morta).

## 1. Cosa fa (sintesi narrativa)

C7 in SitoRuntime risponde allo **stesso problema** di SPW-C7 — *come una SPA React diventa
indicizzabile su hosting PHP/MySQL senza un framework SSR* — e lo risolve con **lo stesso pattern-firma**:
un unico `public/index.php` che `.htaccess` mette davanti a `index.html` (`DirectoryIndex index.php
index.html`, `.htaccess:59`) e a cui dirotta ogni URL virtuale di React Router (`.htaccess:84`). Il
file si auto-marca **"SEO Engine v3.0 (Dynamic Rendering)"** (`index.php:3`) e, per ogni richiesta, in
tempo reale:

1. **deriva `baseUrl` da `$_SERVER['HTTP_HOST']`** (`index.php:26-28`) — conferma di SR-C1: **non esiste
   `SITE_URL` canonico**, l'URL si calcola dall'host della richiesta (funziona su qualunque dominio/staging);
2. **fa il parsing dell'URL** per dedurre il `pageType` (`homepage`/`article`/`speaker`/`podcast`/
   `news_list`/`speakers_list`/`podcasts_list`/`static`/`admin`) — `index.php:83-112`, routing PHP
   speculare a React Router;
3. **interroga il DB** (singleton `Database::connect()` di C1) per i dati reali della pagina
   (articolo, speaker, podcast, oppure le 8 notizie recenti in homepage) — `index.php:124-275`;
4. **decide tra due percorsi** via `isCrawler()` (sniff UA, `index.php:41-56,285`):
   - **UMANO** → serve `index.html` di Vite con title + meta OG/Twitter + JSON-LD **iniettati
     nell'`<head>`** e `Cache-Control: no-store`, lasciando il `<body>` a React (`index.php:398-440`);
   - **CRAWLER** → genera un **HTML completo server-side** con `<title>`, meta, JSON-LD **e il
     contenuto reale nel `<body>`** (breadcrumb, `<h1>`, testo articolo) — `index.php:292-396`.

Come in SPW, il file rivendica che **non è cloaking** perché il contenuto servito ai bot è lo stesso
che l'utente vede dopo l'idratazione (`index.php:12-13`).

Accanto al motore PHP c'è il satellite client **`SEO.tsx`** (no `react-helmet`: aggiorna il DOM
"a mano" via `useEffect`, `SEO.tsx:21-67`), montato in ogni pagina pubblica.

**La grande differenza con SPW sta nella `seo-cache`.** La ROADMAP segnava per SR una "seo-cache"
(che SPW non ha): esiste davvero — i file `.cache/seo_news_*.json` e `.cache/seo_speaker_*.json`
scritti su ogni save da `admin.php`/`speakers.php` e rigenerabili in blocco da `rebuild_seo_cache.php`.
Ma — scoperta centrale della card — **quella cache è MORTA: la scrive chiunque, non la legge nessuno**
(§4). Il banner stesso di `index.php` lo dichiara: *"[v3.0] Riscrittura completa. Sostituisce il proxy
cache-file della v2 (solo meta statici)"* (`index.php:15`). La v2 era un proxy che **leggeva** i file
`seo_*.json`; la v3.0 li ha sostituiti con la query diretta al DB, **rimuovendo il lettore ma non gli
scrittori**. La seo-cache di SR è il relitto di un'architettura precedente.

## 2. Pattern miniCMS rilevanti

- **Dynamic Rendering in un solo `index.php` come "SSR dei poveri"** — pattern identico a SPW-C7:
  un file PHP dietro `.htaccess` fa da front controller, sniffa il bot e ramifica HTML-per-crawler vs
  SPA-per-umani in ~440 righe, zero infrastruttura. È il **pattern-firma del thin stack per la SEO**,
  ora confermato copiato tra due siti diversi (forte candidato cross-sito per la FASE 2).
- **Routing server-side speculare a React Router** (`index.php:83-112`): conteggio dei segmenti URL
  (`news`+1 = lista, `news`+2 = articolo, ecc.). **Doppia verità delle rotte** (una in React, una qui):
  aggiungere una rotta significa toccarla in due posti, esattamente come in SPW.
- **`baseUrl` da `HTTP_HOST`, mai hardcoded** (`index.php:26-28`, `sitemap.php:13-14`, `robots.php:10-11`):
  l'assenza di `SITE_URL` (SR-C1) qui è una **virtù** — stesso file su prod/staging. Ma è **incoerente**
  col lato client (`SEO.tsx:18` e i feed di C8 **hardcodano** `runtimeradio.com`): server host-derived,
  client/feed hardcoded → vedi §4.
- **JSON-LD per tipo di pagina** (`index.php:145-159,176-184,201-209,223-240`): `NewsArticle`
  (con `publisher` Organization + `mainEntityOfPage`), `Person` (speaker, con `worksFor`),
  `PodcastSeries` (podcast), e in homepage un `@graph` con `WebSite` + **`RadioStation`** (tipo
  specifico del dominio radio, assente in SPW). Array PHP serializzati con
  `JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE`.
- **SEO files dinamici, mai fisici** (`.htaccess:77-78`): `sitemap.xml`→`sitemap.php`,
  `robots.txt`→`robots.php`. Identico a SPW. La sitemap include news + speakers + podcast con
  `changefreq`/`priority` per tipo; `robots.php` aggiunge il blocco esplicito dei crawler SEO
  commerciali (`AhrefsBot`/`SemrushBot`/`DotBot` → `Disallow: /`) e `Crawl-delay: 10` — micro-policy
  anti-consumo-banda che SPW non ha.
- **Escaping disciplinato server-side**: `esc()` = `htmlspecialchars(ENT_QUOTES)` (`index.php:69-71`),
  `truncateText()` con `strip_tags`+`html_entity_decode`+collapse+taglio a parola (`:58-67`),
  `absImageUrl()` per assolutizzare le immagini (`:73-77`). Helper **identici nei nomi e nella logica**
  a SPW-C7 (ulteriore prova del codice-firma copiato). **Eccezione critica: il corpo articolo** (§4).
- **`/admin` escluso dagli indici** (`index.php:288-290`): `X-Robots-Tag: noindex, nofollow` +
  nessun rendering crawler per `pageType === 'admin'`. `robots.php:15` ribadisce `Disallow: /admin`.
- **seo-cache su file con scrittura+invalidazione esplicita** (`admin.php:296,309,342`;
  `speakers.php:159,173,195`): ogni save scrive `seo_<entità>_<md5(slug|id)>.json`, ogni delete lo
  `unlink`. È un layer di cache applicativo "alla SR" (gemello della cache di **contenuto**
  `news_*.json` di C4) — solo che, a differenza di quella, **non ha più consumatori** (§4).

## 3. Codice chiave (stralci con origine)

**Lo snodo crawler vs umano + `baseUrl` da host** — `index.php:26-28,41-56,285,292`:

```php
$protocol = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off' || $_SERVER['SERVER_PORT'] == 443) ? 'https://' : 'http://';
$baseUrl  = $protocol . $_SERVER['HTTP_HOST'];     // ← niente SITE_URL canonico (SR-C1)
// …
function isCrawler(): bool {
    $ua = $_SERVER['HTTP_USER_AGENT'] ?? '';
    $crawlers = ['Googlebot', /* … */ 'TelegramBot', 'WhatsApp', 'Discordbot', 'Lighthouse', /* … */];
    foreach ($crawlers as $bot) { if (stripos($ua, $bot) !== false) return true; }
    return false;
}
$isCrawler = isCrawler();
if ($isCrawler && $pageType !== 'admin') { /* HTML completo server-side */ }
else { /* index.html di Vite + meta iniettati, body lo fa React */ }
```

**Il corpo articolo per il crawler: `strip_tags` allowlist, NON DOMPurify (ponte C6) + manca il filtro `status` (ponte C4)** — `index.php:130-135,318`:

```php
// NB: filtra SOLO published_at <= now — MANCA "AND (status='published' OR status IS NULL)" di C4!
$stmt = $pdo->prepare(
    "SELECT id, title, slug, summary, content, cover_image, published_at
     FROM news WHERE slug = ? AND published_at <= ? LIMIT 1");
$stmt->execute([strip_tags(trim($slug)), $now]);
// …(ramo crawler)…
<div>' . strip_tags($article['content'] ?? '',
        '<p><br><h2><h3><h4><ul><ol><li><strong><em><a><blockquote><pre><code>') . '</div>
```

**Iniezione meta nell'`<head>` per gli umani + rimozione del title di Vite** — `index.php:403,416-437`:

```php
header('Cache-Control: no-store, no-cache, must-revalidate');
$htmlContent = file_get_contents(__DIR__ . '/index.html');
$seoInjection = '
    <title>' . $metaTitle . '</title>
    <meta name="description" content="' . esc($metaDesc) . '" />
    <link rel="canonical" href="' . esc($canonicalUrl) . '" />
    <!-- OG/Twitter + JSON-LD inline … --></head>';
$htmlContent = preg_replace('/<title>.*?<\/title>/s', '', $htmlContent, 1);   // niente title doppio
$htmlContent = str_replace('</head>', $seoInjection, $htmlContent);
echo $htmlContent;
```

**La seo-cache: la scrive `admin.php` su ogni save…** — `admin.php:292-297` (gemello in `speakers.php:156-159`):

```php
// Generate SEO Cache
$seoData = ['title' => $title, 'description' => $summary, 'image' => $cover_image];
$cacheDir = __DIR__ . '/.cache';
if (!is_dir($cacheDir)) mkdir($cacheDir, 0755, true);
file_put_contents($cacheDir . '/seo_news_' . md5($slug) . '.json', json_encode($seoData));
array_map('unlink', glob($cacheDir . '/news_*.json'));   // invalida la cache di CONTENUTO (C4)
```

**…e `rebuild_seo_cache.php` la rigenera in blocco — col commento che tradisce il lettore scomparso** — `rebuild_seo_cache.php:67-79`:

```php
$seoData = [
    'title' => $speaker['name'],
    'description' => $speaker['role'] . ' - ' . substr($speaker['bio'] ?? '', 0, 150) . '...',
    'image' => $speaker['image'],
    'name' => $speaker['name'], // Injected for consistency with index.php reader  ← il reader NON esiste più (v3.0)
    'role' => $speaker['role'],
    'bio'  => $speaker['bio']
];
file_put_contents($cacheDir . '/seo_speaker_' . md5($speaker['id']) . '.json', json_encode($seoData));
```

**Il client `SEO.tsx`: aggiorna il DOM a mano, ma NON emette `<link rel="canonical">` + image cross-domain hardcoded** — `SEO.tsx:11-19,51-58`:

```tsx
const SEO = ({ title, description, image = "https://runtimeradio.com/og-image.jpg", type = "website" }) => {
    const location = useLocation();
    const currentUrl = `https://runtimeradio.com${location.pathname}`;   // host HARDCODED (≠ index.php host-derived)
    useEffect(() => {
        document.title = title ? `${title} | Runtime Radio` : defaultTitle;
        updateMeta('description', finalDescription);
        updateMeta('og:url', currentUrl, true);      // og:url SÌ parametrizzato (≠ canonical fisso di SPW)…
        updateMeta('og:image', image, true);
        // …ma NESSUN aggiornamento di <link rel="canonical"> lato client: lo mette solo index.php server-side
    }, [title, description, image, type, currentUrl]);
    return null;
};
```

**`.htaccess`: front controller + SEO files dinamici + blocco cache interna** — `.htaccess:71,77-78,84`:

```apache
RewriteRule ^api/\.cache(/.*)?$ - [F,L]        # la .cache delle API non è web-accessibile
RewriteRule ^sitemap\.xml$ sitemap.php [L,NC]
RewriteRule ^robots\.txt$  robots.php  [L,NC]
RewriteRule ^ /index.php [L]                   # ogni URL virtuale React → SEO Engine
```

## 4. Problemi riscontrati & soluzioni

- **GOLD — La seo-cache è MORTA: la scrivono in tre, non la legge nessuno.** I file
  `.cache/seo_news_*.json` e `.cache/seo_speaker_*.json` sono **scritti** da `admin.php:296,309`,
  `speakers.php:159,173` (su ogni save), **rigenerati** in blocco da `rebuild_seo_cache.php`, e
  **invalidati** su delete (`admin.php:342`, `speakers.php:195`). Ma **nessun file li legge** —
  verificato con grep `seo_news_|seo_speaker_` su tutto `*.php` e su `src/`: zero `file_get_contents`/
  `readfile`/`fetch` su quei nomi. `index.php` v3.0 **interroga il DB direttamente** (`:130-275`) e non
  tocca `.cache`. La prova del delitto è nel codice stesso: il banner di `index.php:15` dichiara *"[v3.0]
  Sostituisce il proxy cache-file della v2 (solo meta statici)"*, e `rebuild_seo_cache.php:71` annota
  `// Injected for consistency with index.php reader` — **un lettore che la v3.0 ha rimosso**. La
  seo-cache è il **relitto della v2**: ogni save paga ancora il costo di scrivere un JSON che nessuno
  aprirà mai. → Box problemi/soluzioni di altissimo valore: **"la cache che sopravvive al suo lettore"**
  — quando riscrivi il motore (v2→v3) e dimentichi di spegnere gli *scrittori*. È l'esatto **opposto**
  di SPW (che la seo-cache non l'ha *per scelta*): qui c'era, è stata orfanata, ma continua a girare.
  Chiude (con sorpresa) il ponte aperto da SR-C4 §8: la *strategia* della seo-cache è… che non c'è più
  strategia.

- **GOLD — Il prerender RIAPRE il buco XSS-stored a livello attributi (ponte C6), identico a SPW.**
  In SitoRuntime la difesa XSS di `news.content` vive **solo a render-time client** (DOMPurify in
  `Article.tsx`, SR-C3/C6). Ma `index.php:318` ri-emette quello stesso `content` sul ramo crawler con
  `strip_tags($content, '<p>…<a>…')`, **non** DOMPurify:
  - `strip_tags` con allowlist **rimuove i tag pericolosi** (`<script>`/`<iframe>`/`<svg>` non in lista
    → eliminati), ma **non tocca gli attributi** dei tag permessi: un `<a href="javascript:…">` o un
    `<p onmouseover=…>` **sopravvive**. DOMPurify invece rimuove `href="javascript:"` e gli handler `on*`.
  - **Raggiungibilità:** l'HTML "crawler" è servito a chiunque presenti uno `User-Agent` in lista
    (`isCrawler()` è solo sniff UA): basta `User-Agent: Googlebot` per ricevere il `content` passato solo
    da `strip_tags`. Superficie **stretta ma reale** (un secondo render-path non sanitizzato come C6).
  - È **lo stesso identico buco** documentato in SPW-C7 §4 (stesso codice, stessa allowlist): la conferma
    che il pattern-firma è stato copiato **insieme alla sua falla**. → rafforza la tesi cross-sito:
    serve una **sanitizzazione server-side condivisa** da tutti gli emettitori PHP del `content`.

- **GOLD — La regola di visibilità di C4 NON è riusata: la SEO mostra le bozze.** La SELECT articolo
  (`index.php:132`), la homepage recenti (`:218`) e la **sitemap** (`sitemap.php:42`) filtrano **solo**
  `published_at <= ?`, **senza** `AND (status='published' OR status IS NULL)` — la clausola che C4 usa
  in `news.php`. Conseguenza: un articolo in **bozza** (`status='draft'`) con `published_at` nel passato
  è **invisibile** nella lista pubblica (C4) ma **trapela** in: meta/OG dell'articolo, HTML crawler,
  blocco "Ultime Notizie" della homepage, **e nella sitemap** (che lo dà in pasto a Google). Il prompt
  chiedeva esplicitamente se C7 *riusa* la regola di C4: **no, la dimentica.** Disallineamento
  pericoloso tra "cosa è pubblico per gli umani" e "cosa è pubblico per i bot". → Box "quando la SEO
  conosce regole di visibilità diverse dall'API" (alto valore, ponte C4).

- **`SEO.tsx` non emette affatto `<link rel="canonical">` lato client.** A differenza di SPW (dove il
  canonical *c'è* ma è bloccato sull'homepage), qui `SEO.tsx` aggiorna `document.title`, `description`,
  OG e Twitter (`:51-65`) ma **non crea/aggiorna** alcun `<link rel="canonical">`. Il canonical esiste
  **solo** server-side (`index.php:419/377`). Per i bot JS-capable che ri-renderizzano la pagina, il
  canonical resta quello iniettato da `index.php` (corretto), ma il client non lo gestisce → i due
  sistemi SEO **divergono** (come in SPW, ma per omissione invece che per default sbagliato).

- **Incoerenza host-derived (server) vs hardcoded (client/feed).** `index.php`/`sitemap.php`/`robots.php`
  derivano `baseUrl` da `HTTP_HOST`; `SEO.tsx:14,18` hardcoda `https://runtimeradio.com` per `image`
  e `currentUrl`, e i feed di C8 (`feed_news_rss.php:9`) hardcodano `https://www.runtimeradio.com`.
  Su **staging** o su `runtimeradio.**it**`, il server produce URL corretti ma il client/feed puntano
  a `.com`. → Box "metà del sito sa su che dominio gira, l'altra metà no".

- **`og:image:width/height` dichiarati solo per l'immagine di default.** `index.php:34,385-386,427-428`:
  le dimensioni `1200×630` sono emesse **solo** quando si usa `og-image.jpg` di default
  (`$ogImgKnownSize`), e omesse per le cover reali (dimensioni ignote). Scelta corretta (meglio nessuna
  dimensione che una sbagliata) — micro-attenzione citabile.

- **`rebuild_seo_cache.php` e `debug_seo.php`: gated solo da `.htaccess`, non nel file.** Nessuno dei
  due controlla l'autenticazione **nel codice PHP**: `debug_seo.php` fa un dump in chiaro di
  `news.id/slug/title/cover_image`, `rebuild_seo_cache.php` scrive su disco. La protezione è
  **esclusivamente** il `FilesMatch "^(debug_|…|rebuild_|setup_|…)"` di `.htaccess:32-35` (deny all).
  Pattern "sicurezza delegata al web server" già visto in SR-C2/C5: se il `.htaccess` non venisse
  applicato (misconfig server), entrambi diventerebbero pubblici. `rebuild_seo_cache.php:91` lo sa e
  avvisa "elimina questo file dopo l'uso". Per di più, oggi rigenera una **cache morta** (vedi GOLD).

- **`isCrawler()` è UA-sniffing puro (spoofabile).** Oltre al vettore XSS sopra, chiunque può vedere la
  versione "crawler" cambiando UA. Innocuo per il ranking (dynamic rendering coerente), ma è il limite
  noto del metodo; la lista bot è statica/hardcoded (`:44-51`) e va mantenuta a mano.

- **`catch (Exception)` con `error_log` ma nessun fallback di contenuto** (`index.php:277-279`): se il
  DB va giù durante la query, l'eccezione è loggata e il flusso **prosegue** con i meta di default;
  l'utente riceve comunque la SPA (o un HTML crawler generico). Degradazione graziosa, ma per un crawler
  significa indicizzare una pagina "vuota" senza segnale d'errore. Minore.

## 5. Estetica / UX (moderna ma funzionale)

- **Per gli umani il body NON è duplicato**: `index.php` inietta solo i meta nell'`<head>` e lascia il
  `<body>` a React (`:436-439`), evitando il flash "contenuto server poi sostituito". `Cache-Control:
  no-store` (`:403`) evita versioni vecchie dopo un deploy. UX pulita, identica alla scelta di SPW.
- **Breadcrumb semantici nell'HTML crawler** (`index.php:306-310,324-328,339-343`): `<nav
  aria-label="Breadcrumb"><ol>…` per articolo/speaker/podcast — accessibilità + rich result per i bot.
- **JSON-LD `RadioStation` in homepage** (`index.php:233-238`): tipo schema.org specifico del dominio,
  un tocco di cura SEO "verticale" che SPW (portfolio) non ha motivo di avere.
- **`robots.php` con policy anti-scraper SEO** (`:19-22`): bloccare Ahrefs/Semrush/DotBot è una scelta
  "editoriale" (non sprecare banda per tool che non portano traffico) — piccola personalità del sito.

## 6. Differenze rispetto agli altri siti

Il confronto con **SPW-C7** è il cuore della card.

| Aspetto | SimonePizziWebSite (SPW-C7) | SitoRuntime (questa card) |
|---|---|---|
| **Motore SEO** | `index.php` "SEO Engine v2.0" Dynamic Rendering UA-sniff | `index.php` "SEO Engine **v3.0**" Dynamic Rendering UA-sniff (**stesso pattern-firma**) |
| **`baseUrl`** | da `HTTP_HOST` | da `HTTP_HOST` (identico; `SITE_URL` assente, SR-C1) |
| **Tipi JSON-LD** | `Article`/`CollectionPage`/`ContactPage`/`@graph` WebSite+Person | `NewsArticle`/`Person`/`PodcastSeries`/`@graph` WebSite+**RadioStation** |
| **Corpo articolo crawler** | `strip_tags` allowlist ≠ DOMPurify (buco attributi) | `strip_tags` allowlist ≠ DOMPurify — **identico buco**, stesso codice |
| **Regola visibilità in SEO** | **riusa** `status='published' AND published_at<=now` (C4) in prerender+sitemap | **NON riusa**: solo `published_at<=now`, **niente `status`** → le bozze trapelano |
| **seo-cache** | **assente per scelta** (real-time + `no-store`) | **presente ma MORTA**: scritta da admin/speakers/rebuild, **letta da nessuno** (relitto v2) |
| **`rebuild_seo_cache`/`debug_seo`** | **non esistono** | esistono (one-shot), gated solo da `.htaccess` by-prefix |
| **SEO client** | `react-helmet-async`, canonical **fisso homepage** (default mai sovrascritto) | `SEO.tsx` DOM-a-mano (no helmet), **nessun `<link canonical>` client**, `og:url` parametrizzato |
| **Host client/feed** | (coerente col server) | **hardcoded `runtimeradio.com`** (≠ server host-derived) → divergenza staging/`.it` |
| **sitemap/robots dinamici** | `.htaccess` rewrite, no file fisici | identico; `robots.php` in più blocca Ahrefs/Semrush/DotBot + `Crawl-delay` |
| **Pannello SEO redazionale** | **`SeoScorePanel`** (7 euristiche nell'editor) | **N/A** — nessun pannello SEO redazionale lato admin |

Sintesi: SR-C7 **eredita il motore di SPW-C7 quasi alla lettera** (stesso `isCrawler`, stessi helper
`esc/truncateText/absImageUrl`, stessa iniezione meta, **stesso buco XSS**), ma diverge in tre punti
sostanziali: (1) la **seo-cache morta**, relitto della v2, che SPW non ha mai avuto; (2) la **regola di
visibilità dimenticata** (le bozze trapelano nella SEO/sitemap); (3) **niente pannello SEO redazionale**.
Dove SPW è "real-time per scelta architetturale", SR è "real-time perché la cache che doveva accelerarlo
è stata orfanata".

Per **DISINTELLIGENZA/FDCA** (festival, SQLite) la SEO sarà verosimilmente minimale (poche pagine,
forse solo meta statici, niente Dynamic Rendering): termine di paragone "minimo" alle rispettive card.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **Dynamic Rendering in un solo `index.php`** confermato copiato tra due siti | Cap. "Rendere indicizzabile una SPA senza framework SSR" (il pattern-firma, ora cross-sito) |
| **La seo-cache morta** (scritta da tutti, letta da nessuno; relitto v2→v3) | Box problemi/soluzioni "la cache che sopravvive al suo lettore" (**altissimo valore**, ponte C4) |
| **Lo stesso buco XSS `strip_tags` ≠ DOMPurify copiato tra i siti** | Box "quando copi un pattern, copi anche la sua falla" (ponte C6, parallelo SPW-C7) |
| **La SEO che ignora il filtro `status` e indicizza le bozze** | Box "due idee diverse di 'pubblico' nello stesso sito" (ponte C4) |
| **`baseUrl` host-derived (server) vs host hardcoded (client/feed)** | Box "metà del sito sa su che dominio gira" |
| **sitemap/robots dinamici via `.htaccess`** + blocco scraper SEO | Cap. "sitemap e robots senza file fisici" (variante con policy anti-Ahrefs) |
| **JSON-LD `RadioStation`/`PodcastSeries`** (dati strutturati verticali) | Box "dati strutturati per un dominio specifico" |
| **Sicurezza delegata al `.htaccess`** (`rebuild_/debug_` non gated nel codice) | Box "l'auth che vive nel web server, non nel PHP" (ponte SR-C2/C5) |

## 8. Note / domande aperte

- **Ponti di sicurezza:**
  - **C7 ↔ C6 — RIAPERTO (come SPW):** `index.php:318` emette `news.content` con `strip_tags`
    allowlist, **non** DOMPurify → buco XSS-stored a livello *attributi* via UA spoofing. Da chiudere
    con sanitizzazione server-side condivisa. Verificato in **C8** (feed): vedi card SR-C8 — il feed
    emette `content` **escapato** (`strip_tags`+`htmlspecialchars`), quindi lì il buco **non** si apre.
  - **C7 ↔ C4 — disallineamento di visibilità:** la SEO non filtra `status` → bozze indicizzabili.
    È un bug di dominio, non solo di sicurezza. Da segnalare in fase di sintesi.
- **Puntatori ad altri cluster** (annotati, NON mappati qui):
  - `Database::connect()` / singleton PDO / timezone `Europe/Rome` (`index.php:18,20`) → **C1**.
  - Schema `news`/`speakers`/`podcasts` e regola `status`/`published_at` → **C4** (qui solo consumati).
  - `cover_image`/`image` come stringa URL (OG image, dangling media) → **C5**.
  - La **cache di contenuto** `news_*.json` (≠ seo-cache) e la sua invalidazione → **C4** (mappata lì);
    qui distinta dalla seo-cache `seo_*.json` (i due livelli sono separati, §1).
  - `TELEGRAM_BOT_TOKEN` (UA `TelegramBot` in `isCrawler`) e l'invio Telegram/newsletter → **C9**.
  - Editor e sanitizzazione client (DOMPurify in `Article.tsx`) → **C6**.
  - L'admin UI che mostra il feed URL (`Admin.tsx`) → **C8/C12**.
- **Assenze confermate:** nessun pannello SEO redazionale (no `SeoScorePanel`); nessun lettore della
  seo-cache; nessun `prerender.php`/`prerender.js` (a differenza dei fossili SSG di SPW — SR è andato
  diretto a Dynamic Rendering); nessun `SITE_URL` canonico (SR-C1).
- **Nessuna credenziale/segreto** nei file di C7 (connessione via `db.php`/`db_credentials.php` di SR-C1).
- Versione di riferimento: sito **2.9.13** (coerente con SR-C1..C5); SEO Engine marcato **v3.0**
  (`index.php:3,15`); `rebuild_seo_cache.php` marcato **v2.6.2** (ulteriore traccia che la cache è di
  un'epoca precedente).
