# Scheda di Sintesi — S1-C7 — SEO & Prerendering

> **Stato:** COMPLETATO
> **Cluster FASE 2:** S1-C7 · **Data:** 2026-06-19 · **Commit:** _(in corso)_
> **Fonti (card di mappatura, in particolare i §6):** SPW-C7, SR-C7, DIS-C7 (+ FDCA-DIFF: vetrina statica, SEO minima → fuori scala)
> **Capitoli del libro toccati:** CAP 11 (SEO Pre-rendering con PHP Entry-Point) — principale · ponti a CAP 8 (il `content` grezzo riemesso → da S1-C6), CAP 10 (XSS-attributi, UA non è gatekeeper), CAP 9 (regola di visibilità) → vedi §4

---

## 0. In una frase
Rendere indicizzabile una SPA senza framework SSR è risolto con **un solo `index.php`** dietro
`.htaccess` che inietta i meta nel build di Vite — ma su due assi i siti divergono in una **scala a
tre gradini**: il *Dynamic Rendering completo* (SPW≡SR, UA-sniff + HTML del corpo per i bot) contro
l'*OG-proxy leggero* (DIS, solo meta escaped). E proprio il gradino "più capace" è quello che **riapre
il buco XSS-stored** che S1-C6 chiudeva solo a render-time: il prerender ri-emette il `content` con
`strip_tags`-allowlist (≠ DOMPurify), e — siccome SR ha **copiato il motore di SPW alla lettera** — ha
copiato anche la falla. DIS, non stampando il corpo, è l'unico immune: *sicuro per sottrazione*.

## 1. Il pattern comune — la filosofia "thin stack" su questa lente

Sotto le differenze, l'approccio SEO dei tre siti condivide quattro tratti.

**1) Un entry-point PHP che avvolge la SPA — "SSR dei poveri".** Nessun Next.js, nessun Node SSR: un
`public/index.php` che `.htaccess` mette davanti a `index.html` (o serve il build rinominato
`index_react.html`), legge l'HTML compilato da Vite, vi **inietta i meta** e lo serve. Il problema
"SPA non indicizzabile" risolto con qualche centinaio di righe di PHP e zero infrastruttura.

**2) Iniezione meta chirurgica + escaping disciplinato.** Tutti rimuovono il `<title>` di Vite con una
`preg_replace` e iniettano un blocco SEO prima di `</head>` con `str_replace`. I valori dal DB passano
sempre da `htmlspecialchars`/`esc()` prima di finire in un attributo. L'immagine OG è resa **assoluta**
(i bot la pretendono). Il `content`, dove serve, è letto dal DB ma trattato con cura — *tranne* sul
ramo che riemette il corpo (§3).

**3) `baseUrl` dall'host della richiesta.** Gli URL OG/canonical si derivano da `$_SERVER['HTTP_HOST']`
(in SR e DIS; SPW ha invece il `SITE_URL` canonico, S1-C1) → lo stesso file funziona su prod e
staging. Rovescio: dipendenza dall'host (poisoning teorico) e — in SR — divergenza col client/feed che
**hardcodano** il dominio.

**4) Degradazione graziosa.** Se il DB cade durante la query SEO, l'eccezione è loggata e il flusso
**prosegue** coi meta di default: un errore del motore SEO non rompe la pagina. Coerente con la
filosofia "il sito non deve mai mostrare uno stack-trace".

A questi si aggiunge il filo che entra da S1-C6: il `content` salvato grezzo e sanitizzato solo nel
render React **viene riletto qui** per la SEO. *Come* viene riemesso (corpo prerenderizzato vs solo
meta) decide se il buco XSS si riapre — ed è il cuore della scheda.

## 2. Le varianti per sito (tabella unica, deduplicata)

| Asse | SimonePizziWebSite | SitoRuntime | DISINTELLIGENZA | *(FDCA)* |
|---|---|---|---|---|
| **Strategia** | **Dynamic Rendering** ("SEO Engine v2.0") | **Dynamic Rendering** ("v3.0", stesso pattern-firma) | **OG-proxy leggero** (solo anteprime social) | — |
| **UA-sniffing (`isCrawler`)** | **sì** (HTML diverso ai bot) | **sì** | **no** (stesso HTML a tutti, niente cloaking) | — |
| **Pre-render del corpo per i bot** | **sì** (HTML completo nel `<body>`) | **sì** | **no** (solo meta; React rende il body) | — |
| **Buco XSS attributi** (`strip_tags` ≠ DOMPurify) | **sì** | **sì** (identico, stesso codice) | **no** (meta `htmlspecialchars`, body non emesso) | — |
| **JSON-LD** | `Article`/`CollectionPage`/`ContactPage`/`@graph` WebSite+Person | `NewsArticle`/`Person`/`PodcastSeries`/`@graph` WebSite+**RadioStation** | **nessuno** | — |
| **`baseUrl`** | **`SITE_URL`** canonico | `HTTP_HOST` | `HTTP_HOST` | — |
| **Regola visibilità (`status`) nella SEO** | **riusa** `status='published' AND published_at<=now` (prerender + sitemap) | **NON riusa**: solo `published_at<=now` → **le bozze trapelano** | **dimenticata** (meta per bozze via slug) | — |
| **sitemap / robots dinamici** | sì (rewrite `.htaccess`) | sì (+ blocco Ahrefs/Semrush/DotBot, `Crawl-delay`) | **no** | — |
| **seo-cache** | **assente per scelta** (real-time + `no-store`) | **presente ma MORTA** (scritta da tutti, letta da nessuno) | **assente** | — |
| **SEO client** | `react-helmet-async`, canonical **fisso homepage** (default mai sovrascritto) | `SEO.tsx` DOM-a-mano, **nessun canonical client**, host **hardcoded** | React idrata sopra i meta | — |
| **Pannello SEO redazionale** | **`SeoScorePanel`** (7 euristiche nell'editor) | N/A | N/A | — |
| **Archeologia SSG** | `prerender.php` deprecato + `prerender.js` dead code + `IS_PRERENDERING` vestigiale | nessun fossile (diretto a Dynamic Rendering) | nessuno | — |

**Lettura della tabella.** Sull'asse *capacità SEO* la scala è chiara: **SPW e SR** fanno il
**Dynamic Rendering completo** (sniffano il bot e gli servono un HTML con il corpo dell'articolo),
**DIS** si ferma all'**OG-proxy** (solo meta per le anteprime social, il body lo fa React). Ma il
gradino "più capace" porta tre debiti: (1) il **buco XSS-attributi** del corpo riemesso; (2) in SR la
**regola di visibilità dimenticata** (bozze indicizzate, persino in sitemap); (3) in SR la
**seo-cache morta**. DIS, facendo meno, evita tutti e tre — *non* per difesa migliore ma per
sottrazione. La chiave cross-sito è che **SR ha ereditato il motore di SPW quasi alla lettera** (stesso
`isCrawler`, stessi helper `esc/truncateText/absImageUrl`, stessa iniezione) — e con esso ne ha
ereditato la falla XSS, mentre *ha perso* la regola di visibilità: copiare un pattern significa
copiarne i bug e poterne introdurre di nuovi.

**FDCA è fuori scala:** la vetrina statica generata via AI Studio ha SEO minimale (pagine fisse,
niente articoli dinamici) → niente Dynamic Rendering. Caso fork.

## 3. GOLD & box problemi-soluzioni

- **I tre gradini del prerender** — *(SPW≡SR vs DIS)* — il GOLD portante. Stesso problema (SPA non
  indicizzabile), tre risposte: **Dynamic Rendering completo** che sniffa l'UA e serve ai bot un HTML
  con `<title>`, meta, JSON-LD **e il corpo** dell'articolo (SPW, SR); **OG-proxy leggero** che inietta
  *solo* i meta escaped e lascia il corpo a React, senza UA-sniff (DIS). Il primo indicizza meglio sui
  crawler no-JS ma è più complesso e rischioso; il secondo è semplice e non fa cloaking ma ha SEO
  testuale debole per i bot che non eseguono JS. → Box "SEO senza framework SSR: Dynamic Rendering vs
  OG-proxy" (alto valore; corregge CAP 11, §4).

- **Il prerender riapre il buco XSS-stored che l'editor chiudeva solo a render-time** — *(SPW + SR;
  salda S1-C6→C7)* — S1-C6 aveva stabilito che `content` è salvato grezzo e l'unico choke-point è
  DOMPurify nel render React. Ma `index.php` (ramo crawler) ri-emette lo stesso `content` con
  `strip_tags($content, '<p>…<a>…')`, **non** DOMPurify: l'allowlist rimuove i tag pericolosi
  (`<script>`/`<iframe>` → via) **ma non tocca gli attributi** dei tag permessi — un
  `<a href="javascript:…">` o un `<p onmouseover=…>` **sopravvive**. Raggiungibile via **UA-spoof**
  (basta `User-Agent: Googlebot` per ricevere il ramo crawler). Superficie stretta ma reale: è un
  secondo render-path del contenuto utente **che non condivide la sanitizzazione di S1-C6**. Lezione:
  *quando la difesa XSS vive in un solo render, ogni altro emettitore deve ri-sanitizzare* — la
  soluzione è una sanitizzazione **server-side condivisa** da tutti gli emettitori PHP del `content`.
  → Box "La difesa XSS che vive in un solo render" (altissimo valore, ponte S1-C6).

- **Quando copi un pattern, copi anche la sua falla** — *(SR eredita SPW)* — SR-C7 è SPW-C7 quasi
  verbatim: stesso `isCrawler`, stessi helper, stessa iniezione meta, **stesso identico** buco
  `strip_tags`. È la prova che il "pattern-firma" del thin stack per la SEO è stato copiato tra i siti
  *insieme al suo difetto*. E nel copiarlo SR ha **perso** un pezzo (la clausola `status`), introducendo
  un bug nuovo. → Box "Riusare un pattern: eredità e deriva".

- **Il prerender che non stampa il corpo: sicuro per sottrazione** — *(DIS)* — DIS evita il buco XSS
  non con una difesa migliore ma perché **emette di meno**: inietta solo i meta (tutti
  `htmlspecialchars`) e non pre-renderizza il body. È il contraltare *positivo* dell'assenza di
  DOMPurify in S1-C6: lì il "non difendere" faceva male, qui il "non emettere" salva. Prezzo: SEO
  testuale debole per i crawler no-JS. → Box "Emettere meno per esporre meno".

- **La seo-cache morta: la cache che sopravvive al suo lettore** — *(SR)* — i file
  `.cache/seo_*.json` sono **scritti** da `admin.php`/`speakers.php` su ogni save, **rigenerati** da
  `rebuild_seo_cache.php`, **invalidati** su delete — ma **letti da nessuno** (grep negativo). Sono il
  relitto della v2 (un proxy che li leggeva): la v3.0 ha riscritto il motore con query diretta al DB e
  ha **rimosso il lettore senza spegnere gli scrittori**. Il commento `// Injected for consistency with
  index.php reader` tradisce il lettore scomparso. Ogni save paga ancora il costo di un JSON che
  nessuno aprirà. È l'opposto di SPW (che la seo-cache non l'ha *per scelta*). → Box "La cache che
  sopravvive al suo lettore" (alto valore, ponte S1-C4/C13).

- **La SEO che indicizza le bozze** — *(SR + DIS)* — la regola di pubblicazione di S1-C4
  (`status='published' AND published_at<=now`) **non** è riusata nella SEO: SR e DIS filtrano *solo*
  `published_at<=now`. Conseguenza: una bozza con data passata è invisibile nell'API ma **trapela** in
  meta/OG, HTML crawler, blocco "ultime notizie" della homepage e — in SR — nella **sitemap**, che la
  dà in pasto a Google. Due idee diverse di "pubblico" nello stesso sito. SPW invece riusa la regola
  correttamente in prerender *e* sitemap. → Box "Due idee di 'pubblico': quando la SEO non conosce le
  regole dell'API" (ponte S1-C4/C9-Lifecycle).

- **Due sistemi SEO che divergono: server vs client** — *(SPW e SR)* — accanto al motore PHP c'è un
  satellite client (`SEO.tsx`). In SPW il canonical client è **fisso sull'homepage** (default mai
  sovrascritto dai chiamanti); in SR il client **non emette affatto** un `<link canonical>` e
  **hardcoda** `runtimeradio.com` (≠ host-derived del server) → su staging/`.it` il server è corretto e
  il client sbaglia. Il canonical *autorevole* resta quello server-side, ma i due sistemi non
  concordano. → Box "Quando il canonical client e quello server non concordano".

- **Archeologia: come muore il codice quando la strategia cambia** — *(SPW)* — SPW conserva i fossili
  del percorso evolutivo: `prerender.php` deprecato (ritorna solo un avviso), `prerender.js`/
  `prerender-routes.js` dead code (il `postbuild` esegue `clean-dist.js`), `IS_PRERENDERING` mai
  definito (guardia vestigiale). Sono i resti dell'esperimento **SSG con Puppeteer abbandonato**, di cui
  resta pure il post-mortem. SR invece è andato **diretto** al Dynamic Rendering, senza fossili. → Box
  "Il codice che resta dopo che la strategia è cambiata" (corregge CAP 11, §4).

## 4. Mappa → capitolo/i del libro

| Materiale della scheda | Capitolo esistente | Azione |
|---|---|---|
| **Dynamic Rendering completo** (UA-sniff + body server-side per i bot) | **CAP 11** (riscrittura §1-3) | **riscrivi**: oggi CAP 11 descrive solo l'iniezione meta e raccomanda l'SSG abbandonato (vedi correzioni) |
| **I tre gradini del prerender** (Dynamic Rendering vs OG-proxy) | **CAP 11** | **nuova sezione**: la scala SPW≡SR / DIS |
| **Il buco XSS-attributi del corpo crawler** (`strip_tags` ≠ DOMPurify) | **CAP 11** (box) + **CAP 10** | **nuovo box** ad alto valore (ponte S1-C6, assente oggi) |
| **La regola di visibilità nella SEO** (riusata SPW / dimenticata SR+DIS) | **CAP 11** + **CAP 9** | **nuovo box**: oggi CAP 11 §3 mostra `status='published'` ma non discute chi la dimentica |
| **La seo-cache morta** (relitto v2→v3) | **CAP 11** + **CAP 7 §2.2** | **nuovo box** + **correzione** (CAP 7 cita `rebuild_seo_cache` come utile; è morta) |
| **sitemap/robots dinamici via `.htaccess`** + blocco scraper SEO | **CAP 11 §6** | **aggiungi**: oggi §6 liquida il `.htaccess` come "già gestito" |
| **JSON-LD per tipo di pagina** (Article/RadioStation/PodcastSeries) | **CAP 11** | **nuovo box**: dati strutturati in PHP (assenti oggi) |
| **Due sistemi SEO (server + client) che divergono** | **CAP 11** | **nuovo box**: canonical client vs server |
| **`SeoScorePanel`: SEO redazionale 100% client** (SPW) | **CAP 11** + **CAP 8** (ponte) | **nuovo box**: il SEO score nell'editor |
| **Archeologia SSG** (prerender.php/.js fossili) | **CAP 11 §1 WARNING** | **correggi**: il WARNING raccomanda proprio l'SSG che SPW ha abbandonato |

**Correzioni al testo attuale (la mappatura smentisce / disallinea il libro):**
- **CAP 11 raccomanda la soluzione che SPW ha PROVATO e SCARTATO.** Il capitolo descrive l'iniezione
  *meta-only* (il livello DIS) e nel WARNING di §1 ammette che non basta per Google, consigliando di
  aggiungere lo **Static Prerendering** (`vite-plugin-prerender`). Ma quella è **esattamente la SSG con
  Puppeteer che SimonePizziWebSite ha implementato e poi abbandonato** (oggi `prerender.js` è dead code,
  con tanto di post-mortem). La soluzione realmente adottata dai flagship è il **Dynamic Rendering**
  (UA-sniff + HTML del corpo per i bot), che CAP 11 **non descrive**. Da riscrivere documentando le tre
  tappe (meta-only → SSG Puppeteer scartata → Dynamic Rendering) e il pattern vincente.
- **CAP 11 §3 — l'esempio di codice è SQLite ma è attribuito a SimonePizziWebSite (MySQL).** Lo snippet
  "implementato in SimonePizziWebSite (v1.4.0)" connette con `new PDO('sqlite:'.$dbPath)` a
  `api/.data/database.sqlite`. Ma SPW gira su **MySQL** (via `Database::connect()`, S1-C1). La forma
  con SQLite e connessione diretta è quella di **DIS** (l'OG-proxy). Da correggere l'attribuzione o
  marcare lo snippet come "forma minima generica".
- **CAP 11 omette interamente** il buco XSS-attributi del corpo crawler, la regola di visibilità
  dimenticata (bozze indicizzate), la seo-cache (e la sua morte in SR), i `sitemap.php`/`robots.php`
  dinamici e il JSON-LD. Sono dimensioni reali del cluster assenti dal capitolo.
- **CAP 7 §2.2 (ponte) dà `rebuild_seo_cache.php` come "utile per migrazioni".** In realtà oggi
  rigenera una **cache morta** (nessun lettore): da segnalare insieme a S1-C5 (che già correggeva CAP 7).

## 5. Cosa si scarta / dedup

- **Ripetizioni fuse:** i §6 di SPW-C7 e SR-C7 erano lo stesso confronto da due lati; DIS-C7 aggiungeva
  la riga "OG-proxy". Qui la comparazione è scritta **una volta sola**, sulla scala Dynamic Rendering ≡
  (SPW/SR) vs OG-proxy (DIS).
- **Dettaglio per-sito che NON entra nel libro:** numeri di riga, la lista esatta degli UA in
  `isCrawler`, le 7 euristiche del `SeoScorePanel`, l'`og:image:width/height` solo-per-default di SR, il
  blocco `RadioStation` vs `Person` dei JSON-LD (basta il *pattern* "JSON-LD per tipo"). Restano nelle
  card come fonte.
- **Materiale che appartiene ad altre schede:**
  - **`content` salvato grezzo + DOMPurify a render-time** → **S1-C6** (qui solo il *riuso* SEO del
    content e il buco che ne deriva).
  - **gli altri emettitori del content** — feed RSS, newsletter — e il completamento del "quadro dei 4
    emettitori" → **S1-C8 / S1-C9** (in SR il feed escapa, quindi lì il buco non si apre).
  - **la regola `status`/`published_at`, gli slug, il contratto di lista** → **S1-C4**.
  - **`cover_image` come OG image / dangling media** → **S1-C5**.
  - **la seo-cache come *strategia di cache* e la sua storia (v2→v3)** → **S1-C13 (DB/architettura
    evolution)**; qui solo il *sintomo* (scritta-ma-non-letta).
  - **`SITE_URL` vs `HTTP_HOST`, timezone, singleton PDO** → **S1-C1/C2** (già consolidati).
