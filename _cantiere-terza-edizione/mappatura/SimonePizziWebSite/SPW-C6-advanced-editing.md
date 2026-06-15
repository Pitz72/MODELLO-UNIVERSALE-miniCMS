# Mappatura — SimonePizziWebSite — C6: Advanced Editing / Editor & Sanitizzazione

> **Stato:** COMPLETATO
> **Sessione:** 6 · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `SimonePizziWebSite/`)
> - `src/components/admin/RichTextEditor.tsx` (editor Tiptap v3: estensioni, toolbar, guardie di inserimento link/YouTube, conteggio parole, sync esterno)
> - `src/components/admin/MediaSelectorModal.tsx` (modale galleria/upload riusata dall'editor per inserire immagini nel testo)
> - `src/components/admin/InternalLinkSelector.tsx` (modale link interni/esterni: articoli per `/categoria/slug` + URL libero)
> - `src/pages/admin/ArticleEditor.tsx` (form articolo: monta `RichTextEditor` per `content`, bozza localStorage, CTA, pubblicazione/programmazione)
> - `src/pages/admin/ProjectEditor.tsx` (form progetto: `description` è una `<textarea>` semplice — **NON** usa l'editor ricco)
> - `src/components/SingleArticle.tsx:24-45,156` (render pubblico: `sanitizeArticleHtml` con DOMPurify + hook iframe; unico `dangerouslySetInnerHTML`)
> - `src/utils/mappers.ts:20,44` (mapping `article.content`→`description`, `project.description`→`description` per `PortfolioItem`)
> - `public/api/articles.php:17-23,252,269,314` (lato server: `content` salvato **grezzo**; solo i CTA passano da `sanitizeUrl`) — letto come consumatore, dominio C4
> - `package.json:13-28` (versioni `@tiptap/* ^3.22.x`, `dompurify ^3.3.3`)

## 1. Cosa fa (sintesi narrativa)

C6 è **l'editing dei contenuti ricchi e la difesa XSS-stored end-to-end**. Il cuore è
`RichTextEditor.tsx`: un wrapper attorno a **Tiptap v3** (ProseMirror) che produce **HTML** salvato
nel campo `articles.content` (C4). Non è Quill, non è un `contenteditable` artigianale: è Tiptap
con `StarterKit` + un set mirato di estensioni (immagini, colore testo, allineamento, tabelle,
embed YouTube nocookie). L'editor è montato **solo** in `ArticleEditor.tsx`. `ProjectEditor.tsx`
usa una `<textarea>` semplice per la `description`: i progetti **non hanno editing ricco**.

Il flusso del contenuto ricco è:

1. **Composizione** — l'autore scrive in `RichTextEditor`. Ogni transazione Tiptap chiama
   `onUpdate` → `editor.getHTML()` → `onChange(html)` → `formData.content` in `ArticleEditor`
   (`RichTextEditor.tsx:145-148`, `ArticleEditor.tsx:346-350`).
2. **Inserimenti speciali** — immagini via `MediaSelectorModal` (riusa `api.getMedia` /
   `api.uploadMediaWithProgress` di C3/C5), link via `InternalLinkSelector`, video via input
   YouTube. Ognuno ha una **guardia di validazione al punto di inserimento** (vedi §2).
3. **Bozza locale** — `formData` (incluso l'HTML) viene autosalvato in `localStorage` ogni 2s
   (`ArticleEditor.tsx:127-137`); un banner offre il **ripristino sessione** alla riapertura.
   Lo stato `isDirty` alimenta `NavigationBlocker` + `beforeunload` (ponte C3).
4. **Salvataggio** — `api.createArticle/updateArticle` invia `content` al server. **`articles.php`
   lo memorizza grezzo** (`:252,269,314`): nessun `strip_tags`/`htmlspecialchars`. La sola
   sanitizzazione lato server riguarda i **link dei CTA** (`sanitizeUrl`, C4), non il corpo HTML.
5. **Render pubblico** — `SingleArticle.tsx:156` inietta l'HTML con `dangerouslySetInnerHTML`,
   ma **solo dopo** `sanitizeArticleHtml()` (DOMPurify, `:28-45`). **Questo è l'unico punto in cui
   l'HTML di contenuto viene effettivamente ripulito**: la difesa XSS-stored è interamente
   **client-side, a render-time**, non in fase di scrittura né lato server.

La catena XSS-stored è quindi: **editor (guardie all'inserimento, ma nessun sanitize forzato del
markup) → DB (HTML grezzo) → render (DOMPurify = vero choke point difensivo)**.

## 2. Pattern miniCMS rilevanti

- **Editor = Tiptap v3, output HTML "source of truth" nel DB.** `RichTextEditor.tsx:95-154`:
  l'editor non tiene uno stato JSON proprietario, ma serializza ad **HTML** (`getHTML()`) ad ogni
  update. Il DB conserva HTML renderizzabile direttamente (coerente col render
  `dangerouslySetInnerHTML`), non un AST da ri-serializzare. Scelta "thin": il contenuto è già
  nella forma in cui verrà mostrato.
- **Estensioni mirate, non "tutto Tiptap".** `:100-138`: `StarterKit` (con `heading` limitato a
  `[1,2,3,4]`) + `Image`, `TextStyle`+`Color`, `TextAlign`, famiglia `Table` (resizable),
  `Youtube` (**`nocookie: true`**). Ogni estensione porta classi Tailwind di default
  (`HTMLAttributes.class`) così l'HTML salvato è **già stilizzato** per il render pubblico
  (es. immagini `rounded-xl my-4 shadow-lg`).
- **Guardie di validazione al PUNTO DI INSERIMENTO (difesa #1, lato client).**
  - **Link**: `isSafeLinkUrl` (`:36-42`) ammette solo `http(s)://`, percorsi relativi (`/`, `#`),
    `mailto:`; **blocca esplicitamente `javascript:` e `data:`**. Applicata in
    `handleInternalLinkSelect` (`:171-182`) — quindi anche l'URL "libero" della
    `InternalLinkSelector` passa di qui prima di diventare un `<a>`.
  - **YouTube**: `normalizeYoutubeUrl` (`:48-65`) accetta un ID di 11 char o un URL il cui host è
    in whitelist (`youtube.com`/`m.youtube.com`/`youtube-nocookie.com`/`youtu.be`); altrimenti
    `null` → errore in UI. Niente embed arbitrari.
  - **Immagini**: `handleMediaSelect` (`:184-187`) inserisce `setImage({ src: url })` **senza**
    validare l'URL — ma la fonte è fidata (galleria/upload di C5), non input libero.
- **Sanitizzazione a render-time con DOMPurify + hook iframe selettivo (difesa #2, il vero choke
  point).** `SingleArticle.tsx:28-45`: `DOMPurify.sanitize(html, { ADD_TAGS:['iframe'],
  ADD_ATTR:['style','allowfullscreen','frameborder','allow','src'] })`. Un hook
  `uponSanitizeElement` rimuove **ogni `<iframe>` il cui `src` non inizi** per
  `https://www.youtube.com/embed/` o `.../youtube-nocookie.com/embed/`. L'hook è registrato e
  **sempre rimosso in `finally`** (niente leak di hook globali tra render). È qui — non
  nell'editor — che si neutralizza l'HTML malevolo eventualmente finito nel DB.
- **Modali di inserimento che riusano il bridge di C3/C5.** `MediaSelectorModal` chiama
  `api.getMedia()` (galleria, filtrata `onlyImages` su `mime_type`) e
  `api.uploadMediaWithProgress()` (tab "Carica Nuovo", barra di progresso XHR di C3). Selezionando
  un media, ritorna `item.file_path` (galleria, `:179`) o `result.url` (upload, `:71`) → l'editor
  fa `setImage`. **Conferma diretta della domanda di C5**: sì, l'embed nel testo riusa
  `uploadMedia/uploadMediaWithProgress`.
- **Bozza locale anti-perdita-lavoro (no autosave server).** `ArticleEditor.tsx:127-151` +
  `ProjectEditor.tsx:122-146`: `localStorage` per-chiave (`article_draft_<id>` / `_new`), banner di
  ripristino se la bozza diverge dai dati DB, pulizia post-salvataggio. È il "draft system" del
  thin stack: **niente endpoint di autosave**, tutto nel browser. Ponte a `NavigationBlocker` (C3).
- **Sync esterno→editor senza "bozze fantasma" (gotcha Tiptap v3).** `:157-165`: quando `value`
  cambia da fuori (apertura articolo esistente), `setContent(value, { emitUpdate: false })`. Il
  commento `:159-161` spiega: in v3 `setContent` emette `onUpdate` di default, che marcherebbe il
  form `dirty` e creerebbe bozze fantasma in `localStorage`. Dettaglio di migrazione molto citabile.

## 3. Codice chiave (stralci con origine)

**Configurazione editor Tiptap v3 + estensioni con classi di default** — `RichTextEditor.tsx:95-138`:

```tsx
const editor = useEditor({
    shouldRerenderOnTransaction: true,   // v3: necessario per gli stati attivi della toolbar
    extensions: [
        StarterKit.configure({ heading: { levels: [1, 2, 3, 4] } }),
        Image.configure({ HTMLAttributes: { class: 'max-w-full h-auto rounded-xl my-4 ...' } }),
        TextStyle, Color,
        TextAlign.configure({ types: ['heading', 'paragraph'] }),
        Table.configure({ resizable: true, /* ... */ }), TableRow, TableHeader, TableCell,
        Youtube.configure({ nocookie: true, /* ... */ }),
    ],
    content: value,
    onUpdate: ({ editor }) => { onChange(editor.getHTML()); updateCounts(editor.getText()); },
});
```

**Guardia link al punto di inserimento (blocca `javascript:`/`data:`)** — `RichTextEditor.tsx:36-42,171-182`:

```tsx
const isSafeLinkUrl = (url: string): boolean => {
    const trimmed = url.trim();
    return /^https?:\/\//i.test(trimmed) || trimmed.startsWith('/')
        || trimmed.startsWith('#') || /^mailto:/i.test(trimmed);
};
// ...
const handleInternalLinkSelect = (url: string) => {
    if (/^www\./i.test(url.trim())) url = 'https://' + url.trim();
    if (!isSafeLinkUrl(url)) { window.alert('URL non valido: ...'); return; }
    editor.chain().focus().extendMarkRange('link').setLink({ href: url.trim() }).run();
};
```

**Sanitizzazione a render-time: DOMPurify + hook iframe YouTube-only** — `SingleArticle.tsx:28-45`:

```tsx
const sanitizeArticleHtml = (html: string): string => {
    DOMPurify.addHook('uponSanitizeElement', (node, data) => {
        if (data.tagName === 'iframe') {
            const src = (node as HTMLElement).getAttribute('src') || '';
            if (!src.startsWith('https://www.youtube.com/embed/') &&
                !src.startsWith('https://www.youtube-nocookie.com/embed/')) {
                node.parentNode?.removeChild(node);     // iframe non-YouTube → via
            }
        }
    });
    try {
        return DOMPurify.sanitize(html, {
            ADD_TAGS: ['iframe'],
            ADD_ATTR: ['style', 'allowfullscreen', 'frameborder', 'allow', 'src'],
        });
    } finally {
        DOMPurify.removeHooks('uponSanitizeElement');    // niente hook globali residui
    }
};
// uso unico:
<div ... dangerouslySetInnerHTML={{ __html: sanitizeArticleHtml(article.description) }} />
```

**Il server salva `content` GREZZO (nessun sanitize del corpo HTML)** — `articles.php:252,269` (gemello `:297,314`):

```php
$content = $data['content'] ?? '';                     // nessun strip_tags / htmlspecialchars
// ...
$stmt = $pdo->prepare("INSERT INTO articles (title, slug, content, ...) VALUES (?, ?, ?, ...)");
$stmt->execute([$title, $slug, $content, ...]);        // HTML così com'è
// (solo i CTA passano da sanitizeUrl: $button_a_link = sanitizeUrl($data['button_a_link'] ?? ''))
```

**Embed media nel testo: la modale riusa il bridge upload di C3/C5** — `MediaSelectorModal.tsx:65-71,179`:

```tsx
const result = await api.uploadMediaWithProgress(file, (p) => setUploadProgress(p));
if (result.url) onSelect(result.url);                  // tab "Carica Nuovo" → URL → setImage
// galleria: onClick={() => onSelect(item.file_path)}  // tab "Scegli dai Media"
```

## 4. Problemi riscontrati & soluzioni

- **La difesa XSS-stored è interamente a render-time, in UN solo file (GOLD).** Il server salva
  HTML grezzo; le guardie dell'editor (`isSafeLinkUrl`, `normalizeYoutubeUrl`) coprono **solo gli
  inserimenti via toolbar**, non l'HTML incollato o costruito altrimenti (Tiptap limita comunque
  nodi/marks allo schema, ma non è una sanitizzazione di sicurezza). L'unica barriera reale è
  `DOMPurify` in `SingleArticle.tsx:156`. **Conseguenza:** qualunque *altro* consumatore che
  renderizzi `articles.content` senza DOMPurify riaprirebbe il buco — in particolare il
  **prerender (C7)**, l'**RSS (C8)** e la **newsletter (C9)** che potrebbero emettere lo stesso HTML
  altrove. → Box "la sanitizzazione che vive solo nel componente di render" + verifica trasversale
  C7/C8/C9 (annotata in §8).
- **`ADD_ATTR: ['style', ...]` allarga la superficie.** Consentire l'attributo `style` arbitrario
  (`SingleArticle.tsx:40`) è gestito da DOMPurify (che ripulisce il CSS pericoloso), ma è una scelta
  da documentare: serve per gli stili inline dell'editor (colore testo via `TextStyle`/`Color`).
  Trade-off "fedeltà visiva vs superficie" — box.
- **Doppio campo `description` sovraccarico nel mapper.** `mappers.ts:20` mappa
  `article.content` → `PortfolioItem.description`, mentre `:44` mappa `project.description` →
  stessa chiave. `SingleArticle` rende `article.description` (= HTML articolo) con DOMPurify; i
  **progetti** (`description` da `<textarea>` semplice, plain text) **non** hanno un render
  `dangerouslySetInnerHTML` (verificato: nessun match nei componenti progetto). Stesso nome di campo,
  due nature (HTML ricco vs testo) → ambiguità da conoscere; se un domani un progetto venisse reso
  come HTML, il plain-text non sarebbe sanitizzato perché non passa da DOMPurify.
- **`InternalLinkSelector` carica solo articoli, non progetti.** `InternalLinkSelector.tsx:33-46`:
  il tipo `LinkableItem` prevede `'article' | 'project'`, ma vengono mappati solo gli articoli (`api.getArticles({admin:true})`); i progetti non sono mai aggiunti. Funzionalità incompleta vs intento.
  Inoltre `:36` ripete il **Double Read** di C3/C4 (`Array.isArray(...) ? ... : (data.data || data.items || [])`), col commento "Fix: `.data` invece di `.items`": traccia archeologica del contratto non uniforme.
- **Bozza locale = solo `localStorage`, niente autosave server.** Se l'utente cambia browser/dispositivo o pulisce la cache, la bozza non salvata è persa. Scelta "thin" coerente (nessun endpoint dedicato), ma è un limite noto → box "draft system senza backend".
- **Dipendenze Tiptap potenzialmente inutilizzate.** `package.json:15,22` elenca
  `@tiptap/extension-link` e `@tiptap/extension-underline`, ma `RichTextEditor.tsx` importa solo
  `StarterKit` + le estensioni esplicite e usa `toggleUnderline`/`setLink` (in v3 inclusi in
  `StarterKit`). Da verificare se i due pacchetti standalone siano dead-deps (vedi §8).

## 5. Estetica / UX (moderna ma funzionale)

- **Toolbar "premium" sticky** (`RichTextEditor.tsx:210`): `role="toolbar"`, raggruppata con
  separatori, stati attivi evidenziati (`bg-dis-green text-black`), `aria-pressed`/`aria-label` sui
  pulsanti, `onMouseDown preventDefault` per non perdere la selezione (`:510`). Accessibilità curata.
- **Color picker a griglia** (30 colori tematici, `:67-78,296-326`) con "Rimuovi Colore" e
  overlay-to-close. **Selettore heading** che si auto-resetta a `p` dopo la scelta (`:239`).
- **Footer statistiche live**: parole, caratteri, **tempo di lettura stimato** (`~min`, 200 wpm)
  (`:455-476`) — micro-dato editoriale aggiornato a ogni transazione.
- **Modali di inserimento ricche**: `MediaSelectorModal` con tab Galleria/Upload, ricerca per nome,
  barra di progresso circolare animata, blocco scroll del body + chiusura su `Escape`
  (`MediaSelectorModal.tsx:23-38`). `InternalLinkSelector` con tab Articoli/URL libero e
  suggerimento "Usa come URL diretto" quando il testo sembra un URL (`:160-176`).
- **Recupero sessione**: banner "Recupero Sessione Interrotta" arancione con Ripristina/Ignora
  (`ArticleEditor.tsx:297-323`) — UX che trasforma il crash recovery in una scelta esplicita.
- **Overlay di salvataggio** con spinner + barra indeterminata e stato "Completato!" prima del
  redirect (`ArticleEditor.tsx:225-264`).

## 6. Differenze rispetto agli altri siti

(Da consolidare in FASE 2. Ipotesi/puntatori:)
- **SitoRuntime (SR-C6 se esiste)**: verificare se usa lo **stesso** `RichTextEditor` Tiptap v3 o
  una variante (es. editor per i podcast/speaker), e soprattutto **se la sanitizzazione di render è
  ugualmente client-only con DOMPurify** o se SR sanitizza anche lato server. Confronto chiave sulla
  difesa XSS-stored.
- **DISINTELLIGENZA/FDCA (festival, SQLite)**: probabilmente **niente editor ricco** (contenuti
  brevi/voto), forse solo `<textarea>` come i progetti qui. Termine di paragone "minimo": quando il
  thin stack **non** ha bisogno di Tiptap.
- Verificare se altrove l'embed media nel testo riusa lo stesso `MediaSelectorModal`/`uploadMedia`
  o se l'inserimento immagini è gestito diversamente.
- Verificare se il pattern **bozza in `localStorage`** (no autosave server) è comune a tutti i siti.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **Tiptap v3 come editor HTML "source of truth"** (output `getHTML()` salvato nel DB) | Cap. "Un editor di contenuti ricchi nel thin stack" (centrale) |
| **Estensioni mirate con classi di default** (HTML già stilizzato per il render) | Box "configurare Tiptap: solo ciò che serve" |
| **Difesa XSS-stored end-to-end: editor → DB grezzo → DOMPurify a render** | Cap. "Dove sanitizzare l'HTML di contenuto" (alto valore, ponte C4 `sanitizeUrl`) |
| **DOMPurify + hook iframe YouTube-only** (`uponSanitizeElement`, `finally removeHooks`) | Box "permettere SOLO gli embed che vuoi" |
| **Guardie al punto d'inserimento** (`isSafeLinkUrl`, `normalizeYoutubeUrl`) vs sanitize a render | Box "due livelli, un solo choke point reale" |
| **Sanitizzazione client-only: il rischio degli altri consumatori** (prerender/RSS/newsletter) | Box problemi/soluzioni "quando la difesa vive in un solo componente" (ponte C7/C8/C9) |
| **Gotcha Tiptap v3**: `shouldRerenderOnTransaction` + `setContent({emitUpdate:false})` | Box "migrare a Tiptap v3: le bozze fantasma" |
| **Embed media nel testo riusa il bridge upload** (`uploadMediaWithProgress`) | Cap. "Inserire immagini nel contenuto" (ponte C3/C5) |
| **Draft system in `localStorage`** (no autosave server) + `NavigationBlocker` | Box "non perdere il lavoro dell'editor senza un backend" (ponte C3) |
| **Toolbar accessibile** (`role/aria-pressed`, `onMouseDown preventDefault`) | Box "una toolbar che non perde la selezione" |

## 8. Note / domande aperte

- **Puntatori ad altri cluster** (annotati qui, NON mappati in questa card):
  - Il **prerender (C7)**, l'**RSS (C8)** e la **newsletter (C9)** consumano `articles.content`:
    **da verificare in quei cluster se emettono l'HTML senza DOMPurify** (la sanitizzazione qui è
    solo nel render React di `SingleArticle`). È il follow-up di sicurezza più importante aperto da C6.
  - `sanitizeUrl` dei CTA (`articles.php:17-23`) → già mappato in **C4**; qui ricontestualizzato come
    *l'altra metà* della difesa XSS-stored (i link dei bottoni sono sanitizzati lato server, il corpo no).
  - `SeoScorePanel` (`ArticleEditor.tsx:554-560`) e l'analisi SEO live → **C7** (SEO): non ispezionato qui.
  - `MediaSelectorModal`/`api.uploadMediaWithProgress` lato server (validazione, WebP) → **C5** (già fatto).
  - Grafico visualizzazioni articolo (`ArticleEditor.tsx:566-604`, `articleAnalytics`) → **C11** (Engagement).
- **Da verificare (dead-deps):** `@tiptap/extension-link` e `@tiptap/extension-underline`
  (`package.json:15,22`) non sono importati in `RichTextEditor.tsx` — confermare se ridondanti
  rispetto a `StarterKit` v3 o usati altrove.
- **Confermato (domanda di C5):** l'editor riusa `api.uploadMedia`/`uploadMediaWithProgress` per
  l'embed media nel testo (via `MediaSelectorModal`); l'URL ritornato (`result.url` / `file_path`)
  diventa un `<img src>` Tiptap, non validato all'inserimento ma di fonte fidata.
- **Confermato:** `ProjectEditor` **non** usa l'editor ricco (`<textarea>` per `description`); i
  progetti non passano da `dangerouslySetInnerHTML` nel render pubblico (plain text, auto-escape React).
- Nessuna credenziale/segreto presente nei file di C6.
- Versione di riferimento allineata a SPW-C1..C5 (sito **1.21.0**); editor marcato "Tiptap Editor v3"
  in UI (`RichTextEditor.tsx:474`), pacchetti `@tiptap/* ^3.22.x`, `dompurify ^3.3.3`.
