# Analisi — omologazione dell'editor articoli su Festival, SimonePizzi e Runtime Radio

> **Data:** 07/09/2026 · **Tipo:** sola lettura e mappatura, nessun file dei tre siti è stato modificato.
> **Repo letti:** `FDCA-PHP` (v1.13.0), `SimonePizziWebSite` (v1.27.0), `SitoRuntime` (v2.34.3),
> più `MODELLO-UNIVERSALE-miniCMS`, `rruntime-magazine` e `KEYLADAMAER.COM` per la parte sul libro.
> **Verifica fatta sul codice**, non sui changelog: `RichTextEditor.tsx`, `ArticleEditor.tsx`,
> `markdown.ts`, `SeoScorePanel.tsx`, `admin/news.php`, `admin.js`, `safe_html()`, `sanitize_html.php`,
> gli endpoint di salvataggio e i tre `index.php`.

> **Stato al 07/09/2026, sera.** Decisione di Simone: si parificano **Festival e Runtime** prendendo da
> SimonePizzi quello che serve; **SimonePizzi non si tocca** fino alla sua migrazione a PHP puro
> (Parte 3), e la Fase B è rimandata a dopo. Fatto nella stessa giornata:
> - **Fase A — Festival v1.14.0** (`FDCA-PHP`, commit `93b6b04`): editor visuale di casa
>   (`assets/js/editor.js`), markdown all'incolla, pulizia dell'HTML incollato con l'allowlist di
>   `safe_html()`, video YouTube, bozza locale, verificatore (`seo-check.js`), colonna
>   `focus_keyword`, scheda riordinata. Prove: 60 asserzioni JS (jsdom + Chrome), 32 PHP.
> - **Fase C — Runtime Radio v2.35.0** (`SitoRuntime`): riquadro «Come esce su Google»
>   (`seo_title`, `seo_description`, `focus_keyword`, migrazione lazy), verificatore `SeoCheck.tsx`
>   con le soglie della tabella 2.1. 87 test frontend verdi, +10 asserzioni PHP.
> - Perimetro confermato per Festival: niente colori, allineamenti e tabelle; sì YouTube.
> - Restano aperte le decisioni **1c** (migrazione di SPW) e **1d** (libro nuovo), e da Runtime il
>   redirect sullo slug cambiato e l'H1 nella tendina.

Quattro parti, nell'ordine chiesto da Simone:

1. Fotografia dei tre editor com'erano stamattina.
2. Matrice dei divari e piano per portare i tre siti allo stesso livello.
3. Fattibilità della trasformazione di SimonePizzi in HTML + JS + PHP.
4. Che cosa i siti hanno appuntato per il manuale, e se il libro va mandato in pensione.

---

## PARTE 1 — Fotografia

### 1.1 In una tabella

| | **Festival (FDCA-PHP)** | **SimonePizzi (SPW)** | **Runtime Radio (SR)** |
|---|---|---|---|
| Stack | PHP puro server-rendered, SQLite, zero build | React 19 + Vite + Tailwind 4, PHP/MySQL | React 19 + Vite + Tailwind 4, PHP/MySQL |
| Editor | `<textarea>` + 10 pulsanti che **incollano tag HTML** attorno alla selezione (`admin.js`) | Tiptap 3 (`RichTextEditor.tsx`, 521 righe) | Tiptap 3 (`RichTextEditor.tsx`, 469 righe) |
| Visuale (WYSIWYG) | **no** | sì | sì |
| Markdown → visuale all'incolla | **no** | **no** | **sì** (`utils/markdown.ts` + `looksLikeMarkdown`, v2.28.0, 18 test) |
| Pulizia dell'HTML incollato | **no** (va nel textarea così com'è) | implicita: lo schema Tiptap scarta ciò che non conosce | implicita (schema Tiptap) + `prepareForEditor` per gli iframe ereditati da Quill |
| Comandi | H2 H3 P, grassetto, corsivo, elenco, citazione, link (via `prompt`), immagine (media picker → `<figure>`), anteprima | undo/redo, blocco (P H2 H3 H4 citazione), B I U S, **colore**, allineamento, elenchi, immagine (modale media), **tabella**, YouTube, link (selettore link interni), cancella formattazione | blocco (P **H1** H2 H3 H4 citazione), B I U S, colore, allineamento, elenchi, immagine (upload con percentuale), YouTube, link (con guardia `isSafeLinkUrl`), cancella formattazione |
| Conteggio parole / lettura | no | sì (piè dell'editor) | sì (sotto l'editor) |
| Layout della scheda | **una colonna** (dati → editor → dati) | **due colonne** (editor 2/3 a sinistra, dati 1/3 a destra, verificatore in fondo alla colonna destra) | **una colonna** (dati → editor → azioni) |
| Verificatore SEO | **no** | **sì** (`SeoScorePanel.tsx`: 9 controlli, punteggio 0-100) | **no** |
| Bozza locale (localStorage) | no (un refresh perde tutto) | sì (ogni 2 s, banner di ripristino) | no (solo `beforeunload`) |
| Anteprima | interruttore sotto il textarea (solo il corpo) | apre `/cat/slug?preview=1` (ultima versione **salvata**) | modale a schermo intero con titolo, sommario e corpo **non salvato** |
| Sanitizzatore server | **`safe_html()`** con DOMDocument e allowlist di tag+attributi (`helpers.php:803`) | **`strip_tags` con allowlist** in `index.php:553` → gli attributi passano (è il buco del CAP 11 §4 del manuale) | `sanitize_html.php` (DOMDocument) sul ramo crawler + DOMPurify nel client |
| CSP | `script-src 'self' 'nonce-…'`, niente `frame-src` | no | no |

### 1.2 I campi della scheda articolo

| Campo | Festival | SPW | SR |
|---|---|---|---|
| Titolo | sì (200) | sì | sì |
| Slug modificabile | sì, **con redirect 301 automatico** in tabella `redirects` | sì, con la riga `.htaccess` da copiare a mano | sì, **senza redirect** |
| Sommario / excerpt | sì (300, `<input>` a una riga) | sì (textarea) | sì (textarea) |
| **Titolo per Google** (`seo_title`) | **sì** (v1.9.0, tetto 60) | no | no |
| **Descrizione per Google** (`seo_description`) | **sì** (v1.9.0, 120-158) | no (usa l'excerpt) | no (usa il sommario) |
| Parola chiave principale | no | **sì** (`focus_keyword`, v1.27.0) | no |
| Copertina | testo + «Scegli dai media» + «Rimuovi» + anteprima | solo URL a mano (il modale media esiste ma serve solo alle immagini nel corpo) | URL + upload con barra |
| Categoria | testo libero | select gerarchico da DB | select fisso a 6 voci |
| Tag | colonna `tags` **esiste ma non è nel form** | sì (`TagPicker`) | no |
| Stato | bozza / pubblicato | bozza / pubblicato | bozza / pubblicato (due pulsanti) |
| Data di pubblicazione | sì (futura = programmata) | sì | sì |
| In vetrina | no | sì (`is_featured`, `is_category_pinned`) | no |
| Call to action | no | due bottoni (URL o email) | no |
| Grafico visualizzazioni | no | sì (30 giorni, Chart.js) | no |

### 1.3 Tre cose viste sul codice che vale la pena dire subito

1. **Il «blocco dati» di Festival è il più completo sul fronte SEO** (i due campi per Google con i testi
   di aiuto giusti), ma **è l'unico senza editor visuale e senza verificatore**. È esattamente lo scambio
   che Simone chiede: Festival dà i campi, riceve l'editor e il controllo.
2. **`safe_html()` di Festival decide che cosa può entrare nell'editor visuale.** Ammette
   `p br b strong i em u ul ol li h2 h3 h4 blockquote pre code figure figcaption a img`, e **nessun
   `span`, `style`, `class`, `iframe`, `hr`**. Quindi colori e allineamenti (che Tiptap salva come
   `style="color:…"` e `style="text-align:…"`) e i video YouTube (`<iframe>`) verrebbero **cancellati al
   render** anche se l'editor li scrivesse. Il perimetro dei comandi di Festival va deciso insieme a
   `safe_html()`, non prima.
3. **SPW ha nel suo `index.php` il buco che il manuale racconta** (`strip_tags` con allowlist: toglie i
   tag, non gli attributi). Runtime lo ha chiuso con `sanitize_html.php`, Festival è nato con
   `safe_html()`. «Stesso livello» vuol dire anche questo.

---

## PARTE 2 — Divari e piano

### 2.1 La regola d'oro dell'omologazione

I tre siti condivideranno **una specifica sola** anche se il codice resta in tre repo:

- **la stessa lista di comandi** nell'editor;
- **lo stesso convertitore markdown** (l'erede di `markdown.ts` di Runtime: titoli, grassetto/corsivo/
  barrato, code span e blocchi, elenchi, citazioni, `hr`, link e immagini con la guardia sugli URL,
  niente `_corsivo_` per via degli snake_case);
- **la stessa pulizia dell'incolla** (DOMParser sull'HTML degli appunti → si ricostruisce solo con
  l'allowlist del sanitizzatore server: via `span`, `style`, `class`, `font`, `div`→`p`, `b`→`strong`,
  `i`→`em`, `&nbsp;` e paragrafi vuoti, la sporcizia di Word e Google Docs);
- **lo stesso blocco dati**, nello stesso ordine, con le stesse etichette e gli stessi testi di aiuto
  (quelli di Festival, che sono già scritti bene);
- **lo stesso verificatore**, con le stesse soglie;
- **la stessa disposizione**: dati sopra, editor sotto, verificatore in fondo.

Le soglie del verificatore vanno unificate adesso, perché oggi SPW e Festival non concordano:

| Controllo | Oggi in SPW (`SeoScorePanel`) | Oggi in Festival (testi di aiuto) | **Proposta unica** |
|---|---|---|---|
| Titolo articolo | 30-65 caratteri | — | 30-65 |
| Titolo per Google | — | ≤ 60 | ≤ 60 (se vuoto si valuta il titolo) |
| Descrizione per Google | excerpt 80-165 | 120-158 | **120-158** ok, avviso sotto 80 o sopra 165 (se vuota si valuta il sommario) |
| Copertina | presente | — | presente |
| Lunghezza corpo | ≥ 300 parole (errore < 100) | — | uguale |
| Struttura | almeno un H2/H3 | — | uguale |
| Parola chiave | nel titolo, nel riassunto, nel corpo (dosata: 1 ogni 100 parole, min 4) | — | uguale, 3 punti su 9 |
| Tag | 2-8 | — | solo dove i tag esistono (SPW); altrove il punteggio si fa su 8 |

### 2.2 Matrice dei divari (chi ha cosa, chi deve riceverla)

| Funzione | Festival | SPW | SR | Da fare |
|---|---|---|---|---|
| Editor visuale | ✘ | ✔ | ✔ | **Festival**: editor vanilla (vedi 2.3) |
| Markdown → visuale all'incolla | ✘ | ✘ | ✔ | **Festival**: porting di `markdown.ts` in JS senza moduli · **SPW**: copia di `markdown.ts` + `links.ts` e lo stesso `handlePaste` (Tiptap 3 identico: mezz'ora) |
| Pulizia dell'incolla | ✘ | implicita | implicita | **Festival**: esplicita (l'editor vanilla non ha uno schema che scarti da solo) |
| Comandi completi | 10 pulsanti su testo grezzo | ✔ (+ tabelle, undo/redo) | ✔ | **Festival**: blocco P/H2/H3/H4/citazione, B I U S, elenchi, link con guardia, immagine da media, YouTube, `hr`, cancella formattazione, undo/redo nativi. **Colori, allineamento e tabelle: no** (vedi 2.3) |
| Conteggio parole | ✘ | ✔ | ✔ | **Festival** |
| Verificatore | ✘ | ✔ | ✘ | **Festival**: porting in JS puro (la funzione `computeChecks` non dipende da React) · **SR**: copia del componente adattata ai token `--c-*` |
| `seo_title` / `seo_description` | ✔ | ✘ | ✘ | **SPW**: migrazione MySQL + `articles.php` + `index.php` + `SEO.tsx` · **SR**: migrazione via `?action=apply_v235_seo` + `admin.php` + `index.php` + form |
| `focus_keyword` | ✘ | ✔ | ✘ | **Festival** e **SR**: colonna nuova (serve ai 3 controlli della parola chiave). Festival la aggiunge col pattern `news_ha_seo()` già in uso |
| Una colonna sola | ✔ | ✘ | ✔ | **SPW**: riscrivere la disposizione di `ArticleEditor.tsx` |
| Ordine dati → editor → verificatore | dati, editor, **poi ancora dati** (categoria, stato, data stanno sotto il corpo) | — | dati, editor, azioni | **Festival**: spostare categoria/stato/data sopra l'editor · **SR**: verificatore fra l'editor e le azioni |
| Copertina dai media | ✔ | ✘ | upload | **SPW**: pulsante «Scegli dai media» che riusa `MediaSelectorModal` |
| Slug cambiato → redirect | automatico | riga da copiare | ✘ | **SR**: almeno l'avviso; meglio la tabella `redirects` di Festival |
| Bozza locale | ✘ | ✔ | ✘ | **Festival** (JS vanilla, 30 righe) · **SR** (facoltativo) |
| Sanitizzatore server con DOMDocument | ✔ | ✘ | ✔ | **SPW**: sostituire lo `strip_tags` di `index.php:553` con una `safe_html()` (la funzione di Festival si copia tale e quale) |

### 2.3 Fase A — Festival riceve l'editor (la fase grossa)

**Vincoli che il codice impone**, verificati:
- niente npm, niente build, niente CDN: l'editor è **un file** `assets/js/editor.js` caricato con il nonce
  della CSP (nessun gestore inline, come già fa `admin.js`);
- gli articoli in archivio sono **già HTML** (`<h2>`, `<figure>`, `<p>`): l'editor deve caricarli
  dentro un `contenteditable` senza perdere niente, e il `<textarea name="content">` resta come
  campo nascosto che si riempie al submit (il salvataggio PHP non cambia di una riga);
- **Tiptap non è un'opzione** qui: è un pacchetto ESM da bundlare, contro la filosofia del repo e
  contro la CSP. L'editor si scrive in casa, e questa è la notizia buona: **diventa l'editor canonico
  dello stack senza React**, riusabile da SPW se migra (Parte 3) e da Runtime Magazine.

**Che cosa contiene `editor.js`** (stima 600-900 righe, ben commentate):
1. `contenteditable` con la classe `article-body` (così l'anteprima è il render stesso);
2. barra comandi: blocco (P, H2, H3, H4, citazione), grassetto, corsivo, sottolineato, barrato,
   elenco puntato e numerato, link (finestrina come in SR, con la guardia degli schemi: http(s),
   mailto, percorsi interni), immagine dal media picker (→ `<figure><img><figcaption>` come oggi),
   YouTube (→ `<figure class="video"><iframe src="https://www.youtube-nocookie.com/embed/ID">`),
   riga orizzontale, cancella formattazione, undo/redo nativi del browser;
3. `markdownToHtml` + `looksLikeMarkdown`: **traduzione riga per riga** di `markdown.ts` (163 righe
   TypeScript → JS ES5-compatibile come il resto di `admin.js`), stesse regole, stessa guardia URL;
4. `cleanPastedHtml`: DOMParser sull'HTML degli appunti → ricostruzione con la **stessa allowlist di
   `safe_html()`**; il testo semplice passa dal convertitore markdown se somiglia a markdown, altrimenti
   diventa paragrafi;
5. conteggio parole e minuti di lettura; bozza locale in `localStorage` con banner di ripristino;
6. sincronizzazione col textarea nascosto e serializzazione **pulita** (niente `<div>`, niente
   `<br>` orfani, niente `&nbsp;`: il browser ne produce, e vanno normalizzati prima del submit).

**Decisioni sul perimetro** (da confermare con Simone):
- **Colori e allineamenti: fuori.** Richiedono `style=` e `safe_html()` lo vieta a ragione; sul sito del
  Festival i colori del testo non hanno mai avuto un uso. Se un giorno serviranno, la via è
  `class="ta-center"` ammessa in allowlist, non `style`.
- **Tabelle: fuori** (le ha solo SPW, e non risultano usate negli articoli).
- **YouTube: dentro**, perché è il sito di un festival musicale. Richiede tre ritocchi: `iframe` in
  `safe_html()` con `src` ammesso **solo** su `youtube-nocookie.com/embed/`, `frame-src
  https://www.youtube-nocookie.com` nella CSP di `helpers.php:103`, e due righe di CSS per il rapporto
  16:9 in `.article-body figure.video`.
- **H1: fuori** (lo è già in `safe_html()`: il titolo è l'H1 della pagina). Runtime lo consente
  nell'editor: andrebbe tolto anche lì per coerenza.
- **`hr` e `s`/`del`: dentro** in `safe_html()` (mancano).

**Verificatore**: `assets/js/seo-check.js`, porting puro di `computeChecks`, legge i campi del form a
ogni `input` e disegna la lista sotto l'editor. Servono `focus_keyword` (migrazione additiva, come le
colonne SEO della v1.9.0) e la lettura dei due campi Google con ripiego su titolo e sommario.

**Disposizione**: la scheda è già a una colonna; si sposta il gruppo categoria / stato / data sopra il
corpo, così l'ordine diventa dati → editor → verificatore → «Salva».

**Collaudo**: il repo non ha test JS; si aggiunge `docs/collaudo/prova-editor.html` (pagina statica
che carica `editor.js` e stampa PASS/FAIL sulle 16 asserzioni del convertitore già scritte in
`markdown.test.ts` di Runtime, tradotte) e si estende `prova-seo.php` ai nuovi controlli di
`safe_html()`.

### 2.4 Fase B — SimonePizzi riceve il blocco dati e cambia disposizione

1. **Disposizione**: `ArticleEditor.tsx` passa da `grid lg:grid-cols-3` a una colonna: in alto il
   blocco dati (titolo, slug, sommario, i due campi Google, copertina, categoria, tag, parola chiave,
   stato, data, vetrina, i due CTA in un riquadro compatto), poi l'editor a tutta larghezza (via
   `h-[calc(100vh-300px)]`, che aveva senso solo nella colonna), poi `SeoScorePanel`, in fondo il
   grafico. La bozza locale, il blocco di navigazione e l'avviso di redirect non cambiano.
2. **Campi**: `seo_title` e `seo_description` su `articles` (MySQL: migrazione additiva nel registro
   `schema_version` già presente in `db_maintenance.php`), lettura/scrittura in `articles.php`,
   uso in `index.php` (meta e JSON-LD: valgono se pieni, altrimenti titolo ed excerpt come oggi) e in
   `SEO.tsx` per il lato React; etichette e testi di aiuto **copiati da Festival**.
3. **Verificatore**: aggiunge i due controlli sui campi Google e allinea le soglie alla tabella 2.1.
4. **Markdown all'incolla**: copia di `utils/markdown.ts` e `utils/links.ts` da Runtime con i loro
   test, e lo stesso `handlePaste` in `editorProps`. Nel passaggio conviene anche sostituire
   `shouldRerenderOnTransaction: true` con `useEditorState` come fa Runtime (nota H.5 delle note per
   il manuale: ridisegna solo la barra, non l'editor a ogni battuta).
5. **Copertina dai media** e **`safe_html()` al posto di `strip_tags`** in `index.php:553`.

> ⚠️ **Avvertenza legata alla Parte 3.** I punti 1 e 4 sono lavoro **sul React** di SPW: se la
> migrazione a PHP puro viene decisa a breve, quel lavoro si butta. I punti 2, 3 (la logica) e 5
> vivono nel PHP e nel DB e **sopravvivono** alla migrazione. Ordine consigliato: decidere prima la
> Parte 3; se la risposta è «sì, entro l'anno», in SPW si fanno solo 2 e 5 e si aspetta l'editor
> canonico di Festival.

### 2.5 Fase C — Runtime Radio riceve il blocco dati e il verificatore

1. Migrazione `?action=apply_v235_seo` (pattern di casa): `seo_title`, `seo_description`,
   `focus_keyword` su `news`; `admin.php` (`save_article`) e `news.php` li leggono e scrivono;
   `index.php` li usa nei meta con ripiego.
2. Il fieldset «Come esce su Google» in `ArticleEditor.tsx`, con i testi di Festival; sotto il
   sommario, prima del corpo.
3. `SeoScorePanel` copiato da SPW (senza il controllo tag, punteggio su 8), reso con i token `--c-*`,
   posizionato fra le statistiche parole e la riga delle azioni.
4. Slug cambiato su articolo pubblicato: avviso + riga `RewriteRule`, oppure la tabella `redirects`
   di Festival letta da `index.php` (mezza giornata, chiude un buco vero).
5. Facoltativo: bozza locale come SPW; togliere H1 dalla tendina.

### 2.6 Ordine e stime

| Fase | Sito | Stima | Perché in quest'ordine |
|---|---|---|---|
| A | Festival | 1 sessione lunga (editor + sanitizzatore + verificatore + collaudo) | È il pezzo grosso e il pezzo **riusabile**: l'editor vanilla serve anche alla Parte 3 |
| C | Runtime | mezza sessione | Solo campi e un componente copiato: nessun rischio |
| B | SimonePizzi | mezza sessione (solo DB/PHP) oppure 1 sessione (anche React) | Dipende dalla decisione della Parte 3 |

---

## PARTE 3 — Fattibilità: SimonePizzi in HTML + JS + PHP

### 3.1 Che cosa c'è oggi (misurato)

| Strato | Dimensione | Nota |
|---|---|---|
| React (`src/`) | **12.296 righe** TS/TSX in 45 file | di cui 537 sono dati statici (`portfolioData.ts`) e ~5.500 il pannello admin (15 pagine) |
| PHP (`public/api/` + `index.php`) | **4.467 righe** in 27 file | `index.php` da solo 814: è già un renderer che scrive nel `<body>` articoli, categorie, tag, progetti e contatti **per i crawler** |
| Database | MySQL | `articles`, `projects`, `categories` gerarchiche, `tags`, `subscribers`, `messages`, `reactions`, `analytics`, `app_settings`, `schema_version` |
| URL pubblici | `/{categoria}/{slug}`, `/tag/{slug}`, `/{categoria}`, progetti, contatti, newsletter | tutto passa da `index.php` via `.htaccess`; robots e sitemap già in PHP |
| Dipendenze da sostituire | react, react-router 7 (loaders), framer-motion, react-helmet-async, dompurify, tiptap (12 pacchetti), chart.js/react-chartjs-2, tailwind 4 | |

### 3.2 Che cosa si tiene, che cosa cade, che cosa si riscrive

**Si tiene tale e quale (≈ tutto il PHP):** `auth.php`, `articles.php`, `projects.php`, `tags.php`,
`categories.php`, `media.php`, `upload.php`, `newsletter_send.php`, `subscribers.php`, `messages.php`,
`reactions.php`, `analytics.php`, `search.php`, `rss.php`, `backup.php`, `db_maintenance.php`,
`robots.php`, `sitemap.php`. Il database **non si tocca**: zero migrazione dati. Gli endpoint JSON
restano utili alle poche parti che hanno bisogno di JavaScript (reazioni, ricerca, iscrizione
newsletter, azioni in blocco nel pannello).

**Cade per costruzione** (è la tabella del CAP 11 nella ricognizione del 14/08, verificata qui):
il ramo `isCrawler()` e la doppia mappa delle rotte (`App.tsx` + `index.php`), DOMPurify, i fossili
del prerender (`prerender.js`, `prerender-routes.js`, `api/prerender.php`, `clean-dist.js`,
`fix-slug.js`, la costante `IS_PRERENDERING`), `react-helmet`, i loader, la build, e **il buco dello
`strip_tags`** in `index.php:553`, perché resta un solo percorso di render con una `safe_html()`.

**Si riscrive:**

| Che cosa | Da | A | Peso |
|---|---|---|---|
| Pagine pubbliche | Hero, Header/Footer, ArticleArchive (paginazione + filtri), FeaturedCard, PortfolioGrid/AllProjects, SingleArticle (+ TOC, Share, Letter, ReactionBar), SearchModal, NewsletterSignup, ContactPage, Confirm/Unsubscribe | `pages/*.php` + `partials/*` sul modello di Festival; il corpo lo scrive già `index.php` per i crawler, quindi **si parte da HTML esistente** | medio |
| JavaScript pubblico | componenti React | 5-6 moduli vanilla piccoli: particelle (è già canvas), ricerca Ctrl+K, reazioni, form newsletter, modali share/lettera, scrollspy del sommario | piccolo |
| Transizioni | framer-motion | View Transitions native + `animation-timeline: view()` come in Festival | piccolo |
| Pannello admin | 15 pagine React (~5.500 righe) | pagine PHP server-rendered: **Festival ha già** login, news, media, newsletter, messaggi, utenti, impostazioni, sistema, profilo. Specifici di SPW: progetti, categorie gerarchiche, tag (rinomina/unisci), elenco articoli con azioni in blocco e duplica, cruscotto analytics | **il pezzo più grosso** |
| Editor | Tiptap | **l'editor vanilla della Fase A** | già fatto, se la Fase A viene prima |
| Grafici | react-chartjs-2 | Chart.js self-hosted (un file, niente React) o SVG scritto da PHP | piccolo |
| CSS | Tailwind 4 nei `.tsx` | **da decidere**: Tailwind come compilatore sui `.php` (scelta di Runtime Magazine) o token CSS senza framework (scelta di Festival). Consiglio: token, perché SPW ha una palette sua e Tailwind è l'ultimo `npm` rimasto | medio |

### 3.3 Rischi e condizioni

- **Gli URL devono restare identici** (la lezione di Keyla, `DECISIONE-01-stack.md`): il piano è a
  rischio zero perché la mappa è già in `index.php` e `.htaccess`; si aggiunge la tabella
  `redirects` di Festival per i due `RedirectMatch` esistenti.
- **La parità del pannello** è dove si perde tempo: bozza locale, azioni in blocco, duplica, tag
  picker, selettore link interni. Tutto fattibile in vanilla, ma va rifatto a mano.
- **Il pannello analytics** (Chart.js) è l'unica dipendenza JS che vale la pena tenere, self-hosted.
- **Il gradino successivo del libro** (Parte 4) ha bisogno di questa migrazione come caso reale
  «da SPA a pagine»: la migrazione produce l'appendice che oggi manca.

### 3.4 Verdetto

**Fattibile, e conveniente**, a patto di farla **dopo** la Fase A: l'editor vanilla e la
`safe_html()` sono il 30% del lavoro e vengono gratis da Festival. Stima complessiva **6-10 sessioni**
(2 per il pubblico, 3-5 per il pannello, 1 per CSS e transizioni, 1 di collaudo e deploy), senza
migrazione dati e senza cambio di hosting. Il momento giusto è dopo la chiusura della Fase A e
prima di qualunque lavoro React su SPW che non sia strettamente necessario.

---

## PARTE 4 — Gli appunti per il manuale, e il libro

### 4.1 Che cosa è stato appuntato, e dove

| Fonte | Che cosa contiene | Stato |
|---|---|---|
| **`SitoRuntime/docs/NOTE_PER_IL_MANUALE.md`** (813 righe) | Il canale ufficiale. Parti I-V (sezioni A-P, fino a P.7 del 03/09/2026): **oltre 15 reference implementation** (sanitizzatore condiviso, `function_exists` come cucitura, sonda a tre stati, doppia cache dell'aggregatore, upload a pezzi su hosting condiviso…), **~30 gotcha** (Tiptap 3, didascalie che restano indietro, `itunes:duration`, header HTTP dell'hosting, prosa come specifica, feed come contratto), e la proposta di **un capitolo che manca**: hosting condiviso e privacy a costo zero | Scritto, **mai portato nel manuale** |
| **`MODELLO/_ricognizioni/2026-08-12-SitoRuntime.md`** | Canone intatto, ma **11 affermazioni «dal vivo» del libro sono false** dal 18/07 | Fatta; decisione (a)/(b)/(c)/(d) **aperta dal 14/08** |
| **`MODELLO/_ricognizioni/2026-08-14-RuntimeMagazine-senza-React.md`** | I quattro rilievi sul libro: il CAP 11 è una protesi; il filo dei quattro emettitori si chiude da solo senza React; le cicatrici hanno una radice sola («ogni regola di dominio vive in una funzione»); Tailwind non è React | Fatta |
| **`rruntime-magazine/concept/RECUPERO_02_REALTA_TECNICA.md`** + `ROADMAP.md` | **Il manuale rimappato capitolo per capitolo senza React**, con i marcatori CANONE / MUTA / CADE / NUOVO / CICATRICE; la roadmap è «l'Appendice A riscritta senza React» | Fatti; il sito è ancora a livello di roadmap, senza cicatrici proprie |
| **`KEYLADAMAER.COM/DECISIONE-01-stack.md`** | Seconda decisione indipendente per il PHP puro (09/08/2026), col SEO e la conservazione degli URL come causa: «sulla carta funziona tutto, in realtà no» | Decisa |
| **`FDCA-PHP`** (nessun file NOTE) | Le lezioni stanno nel README («lezioni incorporate»), in **23 changelog**, in `AUDIT-2026-09-05.md` (37 rilievi chiusi), nei registri GDPR e in `ROADMAP-REVISIONE-2026-09-02.md`. È **il primo sito in produzione dello stack senza React**, con cicatrici vere: l'hosting che rifiuta il cron e il sito che «si sveglia da solo» (v1.13.0), il voto aggirabile via User-Agent, `safe_html()` con DOMDocument, la CSP col nonce, il cookie `__Host-`, la tabella dei redirect, il registro delle azioni | **Mai raccolte in un canale**: è il vuoto più grande |
| **`SimonePizziWebSite`** (nessun file NOTE) | Lezioni sparse nei changelog: v1.27.0 (il verificatore SEO che **premiava gli hashtag** e ha generato 208 tag usati una volta: gli incentivi di un pannello sono una specifica), v1.26.0 (slug + redirect), v1.25.0 (`no-store`), `Nota_Miglioramento_SEO.md` | Non raccolte |
| **`DISINTELLIGENZA`** | Niente di nuovo dopo la terza edizione | — |

Il canale «lì si scrive, qui si decide» funziona solo per Runtime Radio. Festival e SimonePizzi
non hanno un `NOTE_PER_IL_MANUALE.md`, e Festival è proprio il sito che avrebbe più da dire.

### 4.2 Il libro: pensionare la terza edizione, scriverne uno nuovo

**Verdetto: sì, un libro nuovo, non una quarta edizione.** Tre ragioni, tutte verificate su repo:

1. **Tre decisioni consecutive hanno tolto React** dai siti nuovi: Keyla (09/08), Runtime Magazine
   (14/08), Festival (rifondazione, v1.0.0 → oggi v1.13.0 in produzione). L'unico sito che resta
   React è Runtime Radio, e ci resta per il player sempre acceso e la Live Room, non per convinzione.
2. **La ricognizione del 14/08 ha già misurato che cosa cade**: il CAP 11 per intero, il CAP 6 per
   intero, buona parte del CAP 4, il CAP 8 (l'editor: da Tiptap a un editor di casa, che con la
   Fase A esiste davvero), il CAP 14 (pannello server-rendered, che Festival ha già). Una quarta
   edizione di «React + PHP» sarebbe un libro che smentisce il proprio titolo per metà delle pagine.
3. **Il materiale c'è già, ed è distribuito in tre posti**: `RECUPERO_02` è la mappa dei capitoli;
   Festival è la reference implementation con 23 changelog e un audit; le Parti III-V delle note di
   Runtime (hosting condiviso, feed come contratto, migrazioni a fette, prosa come specifica) sono
   indipendenti dallo stack e passano nel libro nuovo senza modifiche.

**Che cosa fare della terza edizione**: **non toccarla**. Applicare la sola opzione **(b)** della
decisione aperta (datare esplicitamente il «dal vivo» a giugno 2026, in una nota nella pagina del
listing o in un'errata scaricabile) e chiudere il canale delle ricognizioni **verso il libro nuovo**.
L'opzione (c), la quarta edizione, si scarta; l'opzione (d), il capitolo su hosting condiviso e
privacy, **diventa un capitolo del nuovo libro**.

**Titolo di lavoro**: «PHP puro: The Thin Stack senza il thin client» (è la frase del README di
Festival). **Scala dei gradini**, finalmente vera anche sulla presentazione: pagine PHP (Festival,
Keyla, Runtime Magazine, SPW migrato) come gradino base, la SPA React (Runtime Radio) come gradino
alto **con il conto dei costi** che il CAP 11 oggi presenta come inevitabili.

**Ossatura proposta** (per confronto con l'indice attuale):

| Parte | Capitoli | Da dove viene |
|---|---|---|
| I · Visione | Manifesto della scala; **il principio nominato**: «ogni regola di dominio vive in una funzione, mai in una stringa copiata» (con la tabella delle sei cicatrici) | CAP 1 + ricognizione 14/08 §5 |
| II · Architettura | Front controller e rotte come dati; il prelude unico; SQLite → MySQL; CSS senza framework (token, `view()`, View Transitions) o Tailwind come compilatore | Festival `index.php`/`rotte.php`, CAP 2-3, RECUPERO_02 Parte III |
| III · Componenti | Helper ed escaping; **`safe_html()`** come sanitizzatore unico; media center e picker; **l'editor di casa** (contenteditable, markdown, pulizia dell'incolla, verificatore); newsletter a lotti | Festival, Fase A di questo documento, CAP 7-8-13 |
| IV · Flusso | Ciclo di vita e slug con redirect; sicurezza (sessioni `__Host-`, CSP col nonce, CSRF, rate-limit su file); **SEO senza protesi** (una pagina per tutti, sitemap/robots dinamici, JSON-LD, i due campi Google, il verificatore); RSS come contratto; pannello server-rendered | CAP 9-10-11§8-12-14 riscritti, note SR parti I-II |
| V · Casi reali | Il motore del festival (iscrizioni, votazioni, giuria, GDPR: Festival v1.8-v1.13); **Runtime Radio come gradino React** e che cosa costa; **da SPA a pagine**: la migrazione di SPW | CAP 17-19 aggiornati, note SR, Parte 3 di questo documento |
| Appendici | A · Boilerplate senza React (la roadmap di Runtime Magazine) · B · Ciclo di vita di un fork · C · Collaudo senza Node (`docs/collaudo/*.php`) · D · **Hosting condiviso e privacy a costo zero** | rruntime-magazine, App. B, Festival, note SR proposta (d) |

**Condizione**: prima di scrivere una riga del libro, servono i due `NOTE_PER_IL_MANUALE.md` che
mancano (Festival e SPW), compilati a ritroso dai changelog, altrimenti si scrive di nuovo un libro
che fotografa un solo sito.

---

## Prossime azioni, in ordine

1. **Decisioni di Simone** (bastano quattro sì/no):
   a. perimetro dell'editor di Festival: niente colori/allineamenti/tabelle, sì YouTube (2.3);
   b. soglie uniche del verificatore (2.1);
   c. migrazione di SPW a PHP puro: sì/no e quando (3.4), perché cambia la Fase B;
   d. libro nuovo al posto della quarta edizione (4.2).
2. **Fase A** su `FDCA-PHP`: `editor.js`, `seo-check.js`, `safe_html()` esteso, CSP `frame-src`,
   migrazione `focus_keyword`, riordino della scheda, `prova-editor.html`.
3. **Fase C** su `SitoRuntime`: migrazione SEO, fieldset «Come esce su Google», verificatore.
4. **Fase B** su `SimonePizziWebSite`: nella forma decisa al punto 1c.
5. **Canale del manuale**: aprire `docs/NOTE_PER_IL_MANUALE.md` in Festival e in SPW; aggiornare
   `_ricognizioni/PROSSIMA-SESSIONE.md` con la decisione sul libro.
