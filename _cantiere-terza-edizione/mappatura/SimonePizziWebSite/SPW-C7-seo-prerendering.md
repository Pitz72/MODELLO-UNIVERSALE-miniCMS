# Mappatura — SimonePizziWebSite — C7: SEO & Prerendering

> **Stato:** COMPLETATO
> **Sessione:** 7 · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `SimonePizziWebSite/`)
> - `public/index.php` (**SEO Engine v2.0** — Dynamic Rendering ibrido crawler/umano: routing URL, query DB, JSON-LD, iniezione meta, HTML server-side per i bot) — **cuore di C7**
> - `public/sitemap.php` (sitemap XML dinamica real-time: home + statiche + categorie + sottocategorie + articoli pubblicati)
> - `public/robots.php` (robots.txt dinamica: Allow/Disallow + puntatore sitemap)
> - `public/.htaccess:10-35` (DirectoryIndex `index.php` prima di `index.html`; rewrite `sitemap.xml`→`sitemap.php`, `robots.txt`→`robots.php`; fallback SPA su `index.php`)
> - `src/components/SEO.tsx` (componente client `react-helmet-async`: title/description/canonical/OG/Twitter)
> - `src/App.tsx:5,11,164,282-286` (`HelmetProvider`, `<SEO />` di default nel layout pubblico)
> - `src/components/admin/SeoScorePanel.tsx` (analisi SEO live nell'editor: 7 euristiche, punteggio 0-100, tutto client, nessuna API)
> - `src/pages/admin/ArticleEditor.tsx:553-560` (montaggio del `SeoScorePanel` nel form articolo)
> - `public/api/prerender.php` (**DEPRECATO** dalla v2.0 — ritorna solo un avviso JSON)
> - `prerender.js` + `prerender-routes.js` (**dead code**: vecchia SSG postbuild, non più wirata — `postbuild` esegue `clean-dist.js`)
> - `docs/archive/analisi-seo-prerendering.md` (post-mortem dell'esperimento SSG Puppeteer scartato → scelta del Dynamic Rendering PHP)

## 1. Cosa fa (sintesi narrativa)

C7 è **come una SPA React diventa indicizzabile senza un framework SSR**. Il problema di partenza
(documentato in `docs/archive/analisi-seo-prerendering.md`) è il classico della SPA su hosting
tradizionale PHP/MySQL: Google Search Console vede una "pagina bianca" perché il contenuto arriva
solo dopo l'esecuzione di JavaScript. La storia di questo cluster è un **percorso evolutivo a tre tappe**:

1. **v1.7.3 — "solo meta tag"**: `index.php` iniettava solo titolo/descrizione/OG nell'`<head>`.
2. **SSG con Puppeteer (scartata)**: uno script Node che prerenderizzava ogni rotta in HTML statico
   su disco. Tecnicamente funzionante, ma **concettualmente sbagliata per un CMS**: rompeva il flusso
   "modifica online → pubblica" (richiedeva build locale + upload FTP), congelava i dati alla build,
   e introduceva complessità (bridge API anti-CORS, buffer `dist-static`, render-event). Abbandonata.
3. **v2.0 — Dynamic Rendering ibrido (attuale)**: tutto si concentra in **`public/index.php`**, che
   `.htaccess` mette davanti a `index.html` (`DirectoryIndex index.php index.html`) e a cui dirotta
   ogni URL virtuale di React Router. Per ogni richiesta, in tempo reale, `index.php`:
   - **fa il parsing dell'URL** per dedurre il tipo di pagina (homepage, categoria, articolo,
     progetti, contatti, pagine legali) — `index.php:119-154`;
   - **interroga il DB** (MySQL via il singleton `Database::connect()` di C1) per recuperare i dati
     reali della pagina (articolo, articoli di categoria, progetti) — `:156-358`;
   - **decide tra due percorsi** via `isCrawler()` (sniff dello `User-Agent`) — `:46-86,364`:
     - **UMANO** → serve `index.html` di Vite con i meta SEO + JSON-LD **iniettati nell'`<head>`**,
       e lascia che React renderizzi il `<body>` client-side (`:560-617`);
     - **CRAWLER** → genera un **HTML completo server-side** con `<title>`, meta OG/Twitter, JSON-LD
       **e il contenuto reale nel `<body>`** (breadcrumb, `<h1>`, testo articolo), così il bot indicizza
       senza eseguire JS (`:376-558`).

Questo è esplicitamente il pattern **"Dynamic Rendering"** raccomandato da Google per le SPA
(`index.php:11-13`), e il file rivendica che **non è cloaking** perché il contenuto servito ai bot è
lo stesso che l'utente vede dopo l'idratazione React.

Accanto al motore PHP server-side esistono **due sistemi SEO "satellite" lato client**:
- **`SEO.tsx`** (`react-helmet-async`): aggiorna `<title>`/`<meta>`/`canonical`/OG/Twitter **nel DOM
  runtime**, montato per ogni pagina pubblica (Home, categoria, articolo, contatti, progetti). Serve
  per la title del tab del browser e per i crawler che *eseguono* JS; **non** emette JSON-LD.
- **`SeoScorePanel.tsx`**: il lato **redazionale** della SEO — un pannello live nell'editor che dà
  all'autore un punteggio 0-100 su 7 euristiche (lunghezza titolo/excerpt, copertura, tag, lunghezza
  contenuto, heading, presenza keyword). Puramente didattico/client, **nessuna chiamata API**.

**Non esiste alcuna cache SEO** in questo sito: niente `seo-cache`, `rebuild_seo_cache` o `debug_seo`
(cercati: assenti). La scelta v2.0 è **real-time per ogni richiesta** — anzi, per gli umani
`index.php:567` invia `Cache-Control: no-store` per impedire a proxy/CDN di conservare l'HTML.

## 2. Pattern miniCMS rilevanti

- **Dynamic Rendering in un singolo `index.php` come "SSR dei poveri".** Nessun Next.js, nessun
  Node SSR: un file PHP che, dietro `.htaccess`, fa da front controller, sniffa il bot, e ramifica
  HTML-per-crawler vs SPA-per-umani. È **l'incarnazione massima della filosofia thin stack** applicata
  alla SEO: il problema "SPA non indicizzabile" risolto con ~600 righe di PHP e zero infrastruttura.
- **Routing duplicato lato server (`index.php:119-154`) speculare a React Router.** Il PHP deve
  re-implementare la stessa mappa di rotte del client (homepage / `tutti-i-progetti` / `contatti` /
  `<categoria>` / `<categoria>/<slug>` / legali). Conteggio dei segmenti URL: 2 parti = articolo,
  1 parte = categoria. **Doppia verità delle rotte** (una in `App.tsx`, una in `index.php`): pattern
  da raccontare come costo del Dynamic Rendering manuale.
- **Stesso contratto di visibilità di C4, ribadito nelle query SEO.** Le SELECT di `index.php`
  (`:175,231,262`) e di `sitemap.php` (`:99`) ripetono la stessa clausola di C4:
  `status = 'published' AND (published_at IS NULL OR published_at <= :now)`. **Bozze e post programmati
  restano fuori da meta, body-crawler e sitemap**: la stessa regola di pubblicazione governa API,
  prerender e sitemap. Coerenza di dominio attraverso tre file diversi.
- **Escaping disciplinato a render-time server-side.** Helper `esc()` = `htmlspecialchars(ENT_QUOTES)`
  (`:105-107`), `truncateText()` che fa `strip_tags`+`html_entity_decode`+collapse spazi e taglia a
  parola intera (`:91-100`), `absImageUrl()` che assolutizza gli URL immagine (`:112-117`). Ogni dato
  dal DB passa da `esc()` prima di finire in un attributo/title. **Eccezione critica: il corpo
  dell'articolo** (vedi §4).
- **Due livelli di SEO, due platee.** Server-side (`index.php`) per il *primo byte* e per i bot
  no-JS; client-side (`SEO.tsx`/Helmet) per il tab e i bot JS-capable. Si sovrappongono di proposito
  ("Google esegue JS ma apprezza JSON-LD server-side", `:602`). Pattern "belt and suspenders".
- **JSON-LD per tipo di pagina** (`index.php:189-340`): `Article` (con `author`/`publisher` Person,
  `mainEntityOfPage`), `CollectionPage` (categoria/progetti), `ContactPage`, e in homepage un
  `@graph` con `WebSite` + `Person`. Dati strutturati costruiti come array PHP e serializzati con
  `JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE`.
- **SEO files dinamici, mai fisici** (`.htaccess:21-25`): `sitemap.xml` e `robots.txt` sono **rewrite**
  verso `sitemap.php`/`robots.php`. Il commento spiega che questo elimina il "bug v1.9.6 del 404
  sporadico su robots.txt" e tiene la sitemap sempre fresca senza prerendering. `baseUrl` calcolato
  da `$_SERVER['HTTP_HOST']` (non hardcoded) → stesso file funziona su qualunque dominio/staging.
- **Pannello SEO redazionale 100% client, euristiche trasparenti** (`SeoScorePanel.tsx:34-135`): 7
  check con soglie esplicite (titolo 30-65, excerpt 80-165, ≥300 parole, presenza H2/H3, keyword =
  primo tag nel titolo/excerpt), punteggio normalizzato su `maxScore = 7`. Nessun segreto lato server:
  l'autore capisce *perché* il punteggio è quello. Coerente col thin stack (logica leggibile, niente
  servizio SEO esterno).

## 3. Codice chiave (stralci con origine)

**Lo snodo crawler vs umano** — `index.php:46-86,364,376`:

```php
function isCrawler(): bool {
    $ua = $_SERVER['HTTP_USER_AGENT'] ?? '';
    if (empty($ua)) return false;
    $crawlers = ['Googlebot', 'Bingbot', 'Slurp', /* … */ 'facebookexternalhit',
                 'Twitterbot', 'TelegramBot', 'WhatsApp', 'Discordbot', 'Lighthouse', /* … */];
    foreach ($crawlers as $bot) { if (stripos($ua, $bot) !== false) return true; }
    return false;
}
// …
$isCrawler = isCrawler();
if ($isCrawler && $pageType !== 'admin') { /* HTML completo server-side */ }
else { /* index.html di Vite + meta iniettati nell'head, body lo fa React */ }
```

**Routing server-side speculare a React Router** — `index.php:133-154`:

```php
if (count($uri_parts) === 0)            $pageType = 'homepage';
elseif ($uri_parts[0] === 'admin')      $pageType = 'admin';      // niente SEO per l'admin
elseif ($uri_parts[0] === 'tutti-i-progetti') $pageType = 'projects';
elseif ($uri_parts[0] === 'contatti')   $pageType = 'contact';
elseif (count($uri_parts) === 2) { $pageType = 'article';  $catSlug = $uri_parts[0]; $slug = $uri_parts[1]; }
elseif (count($uri_parts) === 1) { $pageType = 'category'; $catSlug = $uri_parts[0]; }
```

**Stessa regola di pubblicazione di C4 nelle query SEO** — `index.php:172-179`:

```php
$stmt = $pdo->prepare(
    "SELECT id, title, slug, content, excerpt, cover_image, category, published_at, created_at
     FROM articles
     WHERE slug = :slug AND status = 'published' AND (published_at IS NULL OR published_at <= :now)
     LIMIT 1");
$stmt->execute([':slug' => strip_tags(trim($slug)), ':now' => $now]);
```

**Il corpo articolo per il crawler: `strip_tags` con allowlist, NON DOMPurify (ponte C6)** —
`index.php:403-405`:

```php
<section>' . ($article['excerpt'] ? '<p><strong>' . esc(strip_tags($article['excerpt'])) . '</strong></p>' : '') . '</section>
<div>' . strip_tags($article['content'],
        '<p><br><h2><h3><h4><ul><ol><li><strong><em><a><blockquote><pre><code>') . '</div>
```

**Iniezione meta nell'`<head>` per gli umani + rimozione del title di Vite** — `index.php:576-614`:

```php
$seoInjection = '
    <title>' . $metaTitle . '</title>
    <meta name="description" content="' . esc($metaDesc) . '" />
    <link rel="canonical" href="' . esc($canonicalUrl) . '" />
    <!-- OG/Twitter… --> ';
if ($jsonLd) { $seoInjection .= '<script type="application/ld+json">' . json_encode($jsonLd, …) . '</script>'; }
$seoInjection .= "\n    <script src=\"/js/cookie-banner.js\" defer></script>\n</head>";
$htmlContent = str_replace('</head>', $seoInjection, $htmlContent);
$htmlContent = preg_replace('/<title>.*?<\/title>/s', '', $htmlContent, 1); // evita title duplicato
```

**Il componente client Helmet (NB: `url` non parametrizzato → canonical sempre homepage)** —
`SEO.tsx:12-27`:

```tsx
const SEO: React.FC<SEOProps> = ({
    title, description = "Portfolio creativo di Simone Pizzi…",
    image = "/images/og-image.jpg",
    url = "https://simonepizzi.runtimeradio.it",   // ← default fisso, mai sovrascritto dai chiamanti
    type = "website" }) => {
    const fullTitle = title ? `${title} | Simone Pizzi` : "Simone Pizzi | Portfolio Creativo";
    return (<Helmet>
        <title>{fullTitle}</title>
        <link rel="canonical" href={url} />  {/* sempre l'homepage, vedi §4 */}
        {/* … OG/Twitter … */}
    </Helmet>);
};
```

**SeoScorePanel: euristiche e punteggio (estratto)** — `SeoScorePanel.tsx:45-58,134`:

```tsx
const titleLen = title.trim().length;
if (titleLen === 0)        checks.push({ status:'error', message:'Il titolo è vuoto.' });
else if (titleLen < 30)    { checks.push({ status:'warn',  message:`Troppo corto (${titleLen}/30 min)…` }); score += 0.5; }
else if (titleLen > 65)    { checks.push({ status:'warn',  message:`…Google tronca oltre 65.` });          score += 0.5; }
else                       { checks.push({ status:'ok',    message:`Lunghezza ottimale (${titleLen})…` }); score += 1; }
// … 7 check totali …
return { checks, score: Math.round((score / maxScore) * 100) };  // maxScore = 7
```

**Sitemap dinamica con `lastmod` per categoria (subquery sull'articolo più recente)** —
`sitemap.php:51-70`:

```php
$stmtCat = $pdo->query(
    "SELECT c.slug,
            (SELECT MAX(COALESCE(a.published_at, a.created_at))
             FROM articles a WHERE a.category = c.slug AND a.status = 'published') as latest_article
     FROM categories c WHERE c.parent_id IS NULL ORDER BY c.sort_order ASC");
// → <loc>, <lastmod> (se c'è), <changefreq>weekly</changefreq>, <priority>0.8</priority>
```

**`.htaccess`: front controller + SEO files dinamici** — `.htaccess:10-34`:

```apache
DirectoryIndex index.php index.html                 # index.php (SEO Engine) prima di index.html
RewriteRule ^sitemap\.xml$ sitemap.php [L,NC]
RewriteRule ^robots\.txt$  robots.php  [L,NC]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_URI} !^/api/ [NC]
RewriteRule ^(.*)$ /index.php [L,QSA]               # ogni URL virtuale React → SEO Engine
```

## 4. Problemi riscontrati & soluzioni

- **GOLD — Il prerender RIAPRE parzialmente il buco XSS-stored che C6 chiudeva solo a render-time.**
  C6 aveva stabilito che `articles.content` è salvato **grezzo** nel DB e che l'**unico** choke point
  difensivo è `DOMPurify` in `SingleArticle.tsx` (render React). **`index.php:404` emette quello stesso
  `content` sul ramo crawler usando `strip_tags($content, '<p>…<a>…')`, NON DOMPurify.** Differenze
  sostanziali e rischio:
  - `strip_tags` con allowlist **rimuove i tag pericolosi a livello di elemento** (`<script>`,
    `<iframe>`, `<svg>`, `<object>` non sono nell'allowlist → eliminati). Questo neutralizza i vettori
    XSS più ovvi.
  - **MA `strip_tags` NON tocca gli attributi dei tag permessi.** Un `<a href="javascript:…">` o un
    event handler su un tag consentito (`<p onmouseover=…>`, `<a onclick=…>`) **sopravvive** alla
    pulizia. DOMPurify invece rimuove `href="javascript:"` e gli handler `on*`.
  - **Raggiungibilità:** l'HTML "crawler" è servito a chiunque presenti uno `User-Agent` in lista
    (`isCrawler()` fa solo sniff UA, `:46-86`). Un attaccante può impostare `User-Agent: Googlebot` e
    ricevere il `content` passato solo da `strip_tags`. L'exploit reale richiede però che la *vittima*
    abbia un UA-crawler (i bot di norma non eseguono JS), quindi la superficie è **stretta ma reale**:
    è un secondo render-path del contenuto utente che **non condivide la sanitizzazione di C6**.
  - **Mitigazione presente vs mancante:** l'allowlist limita molto il danno (niente `<script>`/`<iframe>`),
    ma manca la sanitizzazione **attributo-level**. Il ramo **umano** invece **non emette affatto**
    `content` (lo fa React+DOMPurify), quindi lì il buco resta chiuso.
  - → **Box problemi/soluzioni di altissimo valore per il libro**: "quando la difesa XSS vive in un
    solo componente di render, ogni *altro* emettitore del contenuto deve ri-sanitizzare". Conferma e
    chiude il follow-up aperto in SPW-C6 §8 per il prerender. (Resta aperto lo stesso controllo per
    RSS=C8 e newsletter=C9.) Soluzione suggerita nel manuale: una funzione di sanitizzazione **lato
    server** condivisa (HTMLPurifier o equivalente) usata da *tutti* gli emettitori PHP del `content`.

- **`SEO.tsx` ha `canonical`/`url` non parametrizzabile → canonical client sempre = homepage.**
  `SEO.tsx:16` fissa `url = "https://simonepizzi.runtimeradio.it"` come default e **nessun chiamante
  passa `url`** (`SingleArticle.tsx:65`, `ArticleArchive.tsx:36,52`, `ContactPage`, `AllProjects`
  passano solo `title`/`description`/`image`). Quindi il `<link rel="canonical">` iniettato da Helmet
  punta **sempre all'homepage**, su ogni pagina. **Non è un disastro** perché il canonical *autorevole*
  è quello server-side di `index.php` (per articolo `:187` = `baseUrl/categoria/slug`, corretto), che
  arriva nel primo byte; ma i due sistemi SEO **divergono** e un crawler JS-capable potrebbe vedere il
  canonical sbagliato sovrascritto da Helmet. → Box "due sistemi SEO che non concordano" (incoerenza
  client/server da unificare).

- **Incoerenza dei default tra i due sistemi SEO.** `SEO.tsx` usa `image="/images/og-image.jpg"` e
  titolo di default "Simone Pizzi | Portfolio Creativo"; `index.php` usa `image=/Simone-Pizzi.webp`
  (`:34`) e titolo "Simone Pizzi - Videogiochi, Software e Narrativa" (`:32`). Stesso sito, due verità
  di branding SEO. Da consolidare.

- **Doppia verità del routing (server PHP ↔ client React).** Aggiungere una rotta pubblica significa
  toccarla **in due posti**: `App.tsx` e `index.php:133-154`. Una rotta nuova non mappata in
  `index.php` ricade nel default `homepage`/`category` con meta sbagliati per i bot. Costo strutturale
  del Dynamic Rendering manuale → box "il prezzo di non avere un framework SSR".

- **`prerender.php` deprecato ma ancora presente.** `public/api/prerender.php` non fa più nulla:
  ritorna un JSON `status: deprecated` (`:18-23`). È tenuto **solo** per non generare 404 su vecchi
  bookmark admin. Da rimuovere a una pulizia futura → traccia archeologica citabile ("come muore un
  endpoint quando la strategia cambia").

- **`prerender.js` / `prerender-routes.js` = dead code (SSG fossile).** Verificato: il `postbuild` di
  `package.json:9` esegue `clean-dist.js`, **non** `prerender.js`; `dist/` contiene solo `index.html`
  alla root (nessuna cartella per-rotta). Quindi i due script (più la devDep `vite-plugin-prerender`)
  sono **resti dell'esperimento SSG abbandonato** descritto nel post-mortem. Inoltre `prerender.js`,
  anche se girasse, **copierebbe solo `index.html` senza iniettare contenuto** (`:51`), quindi sarebbe
  comunque inutile dopo il passaggio a Dynamic Rendering. → Candidato a cleanup; ottimo esempio di
  "codice che resta dopo che la strategia è cambiata".

- **`IS_PRERENDERING` mai definito.** `sitemap.php:16` e `robots.php:12` proteggono l'invio degli
  header con `if (!defined('IS_PRERENDERING'))`, ma **nessun file definisce mai questa costante**
  (verificato con grep). È una guardia **vestigiale** dell'epoca SSG (quando il prerender includeva
  quei file per catturarne l'output). Oggi la condizione è sempre vera: rumore morto da ripulire.

- **`isCrawler()` è UA-sniffing puro (spoofabile).** Oltre al vettore XSS sopra, lo sniff dell'UA è
  per definizione falsificabile: chiunque può vedere la versione "crawler" cambiando UA. Per la SEO è
  innocuo (Google non penalizza il dynamic rendering coerente), ma è bene saperlo come limite del
  metodo. La lista bot è statica e hardcoded (`:50-78`) → va mantenuta a mano.

## 5. Estetica / UX (moderna ma funzionale)

- **`SeoScorePanel` = "premium UX" per l'autore** (`SeoScorePanel.tsx:163-209`): anello di punteggio
  SVG (`strokeDasharray = `${score} ${100-score}``) con colore semaforico (emerald/amber/red),
  etichetta "Ottimizzato / Da Migliorare / Critico", conteggio parole + tempo di lettura, e lista di
  check con icone `lucide` (`CheckCircle`/`AlertCircle`/`XCircle`). Trasforma la SEO in un **gioco a
  punti** dentro l'editor, senza chiamate API: feedback istantaneo via `useMemo` sui campi del form.
- **Per gli umani il body NON è duplicato**: `index.php` inietta solo i meta nell'`<head>` e lascia a
  React il `<body>`, evitando flash di contenuto server poi sostituito (a differenza dell'idea
  "iniezione nel `<div id=root>`" del piano archiviato, **non** adottata). UX pulita.
- **`Cache-Control: no-store` per gli umani** (`index.php:567`): niente versioni vecchie su hard
  refresh dopo un deploy — micro-attenzione di QoL.
- **Breadcrumb semantici nell'HTML crawler** (`index.php:390-396,411-416,478-483`): `<nav
  aria-label="Breadcrumb"><ol>…` — buona accessibilità *e* rich result per i bot.

## 6. Differenze rispetto agli altri siti

(Da consolidare in FASE 2. Ipotesi/puntatori:)
- **SitoRuntime (SR-C7 "SEO + seo-cache")**: la ROADMAP segna per SR una **cache SEO** (`seo-cache`),
  qui **assente per scelta** (real-time + `no-store`). Confronto chiave: SPW sceglie freschezza
  assoluta, SR probabilmente introduce una cache per scalare (coerente col ruolo "scalabilità" di SR).
  Verificare anche se SR usa lo stesso `isCrawler()` UA-sniff o una libreria, e se ha `rebuild_seo_cache`/
  `debug_seo` (endpoint che in SPW **non esistono**).
- **DISINTELLIGENZA/FDCA (festival, SQLite)**: probabilmente SEO minimale (poche pagine statiche,
  niente articoli) → forse nessun Dynamic Rendering, solo meta statici. Termine di paragone "minimo".
- Verificare se il **Dynamic Rendering in `index.php`** è un pattern copiato tra i siti React+PHP di
  Simone o specifico di SPW: è probabilmente **il** pattern-firma del thin stack per la SEO.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **Dynamic Rendering in un solo `index.php`** (SSR-dei-poveri: sniff UA, HTML-per-bot vs SPA-per-umano) | Cap. "Rendere indicizzabile una SPA senza framework SSR" (**centrale, alto valore**) |
| **Il percorso evolutivo SEO** (meta-only → SSG Puppeteer scartata → Dynamic Rendering) | Box/Intro "tre tentativi per indicizzare una SPA" (post-mortem `analisi-seo-prerendering.md`) |
| **Il prerender ri-emette `content` con `strip_tags` ≠ DOMPurify** | Box problemi/soluzioni "la difesa XSS che vive in un solo render" (**ponte C6**, altissimo valore) |
| **Stessa regola `published_at <= now` in API, prerender e sitemap** | Box "una sola regola di pubblicazione, tre file" (ponte C4) |
| **SEO files dinamici via `.htaccess`** (`sitemap.xml`→`.php`, `robots.txt`→`.php`, `baseUrl` da host) | Cap. "sitemap e robots senza file fisici" |
| **JSON-LD per tipo di pagina** (Article/CollectionPage/ContactPage/`@graph` WebSite+Person) | Box "dati strutturati costruiti in PHP" |
| **Due sistemi SEO (server PHP + Helmet client) che divergono** | Box "quando il canonical client e quello server non concordano" |
| **`SeoScorePanel`: SEO redazionale come gioco a punti, 100% client** | Cap. "guidare l'autore: un SEO score nell'editor" (ponte C6/C12) |
| **Doppia verità del routing (React Router ↔ `index.php`)** | Box "il prezzo di non avere un framework SSR" |
| **Archeologia: `prerender.php` deprecato, `prerender.js` dead code, `IS_PRERENDERING` vestigiale** | Box "come muore il codice quando la strategia cambia" |

## 8. Note / domande aperte

- **Ponti di sicurezza aperti (follow-up trasversale dei contenuti, da chiudere nei rispettivi cluster):**
  - **C7 ↔ C6 — CHIUSO QUI (in parte):** il prerender crawler (`index.php:404`) emette `content` con
    `strip_tags` allowlist, **non** DOMPurify → riapre parzialmente il buco XSS-stored a livello di
    *attributi* (event handler / `javascript:` su tag permessi), raggiungibile via UA spoofing. Vedi §4.
  - **Ancora da verificare in C8 (RSS) e C9 (Newsletter):** emettono anch'essi `articles.content`?
    Con quale sanitizzazione? È l'estensione naturale del controllo iniziato in C6/chiuso qui per C7.
- **Puntatori ad altri cluster** (annotati, NON mappati qui):
  - `Database::connect()` / singleton PDO / timezone `Europe/Rome` (`index.php:19,25,167`) → **C1**.
  - Schema `articles`/`categories`/`projects` e la regola `status`/`published_at` → **C4** (qui solo
    *consumati* per la SEO).
  - `sanitizeUrl` dei CTA, `cover_image` solo-URL (dangling media) → **C4/C5**.
  - `cookie-banner.js`, `privacy.php`/`cookie-policy.php` serviti da `index.php:367-374` → cluster
    legale/privacy (non in roadmap esplicita; eventualmente C12/Admin o nota a sé).
  - `react-helmet-async` come dipendenza del bridge front-end → già citato in **C3** §8 come rinvio a C7.
- **Confermato (chiude domande aperte di C3/C6):** sì, `SEO.tsx`+`react-helmet-async` e i `prerender*.js`
  erano i rinvii a C7 segnati in C3 §8; mappati qui. I `prerender*.js` risultano **dead code** (postbuild
  = `clean-dist.js`), non parte del flusso vivo.
- **Assenze confermate (non N/A per dimenticanza, ma per scelta architetturale):** **nessuna** cache
  SEO (`seo-cache`), **nessun** `rebuild_seo_cache`, **nessun** `debug_seo` in SPW (cercati: assenti).
  La v2.0 è real-time per richiesta. Questi endpoint vanno cercati semmai in **SR-C7**.
- **Nessuna credenziale/segreto** presente nei file di C7.
- Versione di riferimento allineata a SPW-C1..C6: sito **1.21.0**; SEO Engine marcato **v2.0** nel
  banner di `index.php:1-17`.
