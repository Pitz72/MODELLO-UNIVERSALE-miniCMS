# Mappatura — DISINTELLIGENZA — C6: Advanced Editing / Editor & Sanitizzazione

> **Stato:** COMPLETATO · **(card aggiunta in FASE 1-bis: colmatura gap di copertura, 2026-06-18)**
> **Sessione:** 29 · **Data:** 2026-06-18 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `DISINTELLIGENZA/`)
> - `src/components/RichTextEditor.tsx` (editor **custom `contentEditable` + `document.execCommand`**; paste markdown via `showdown`)
> - `src/pages/NewsDetail.tsx` (render pubblico: `dangerouslySetInnerHTML` **senza sanitizzazione**)
> - `package.json` (**nessuna** dipendenza editor Tiptap/Quill; presente `showdown`; **nessun** `dompurify`)
> - richiami: `news.php:81` (content salvato grezzo, DIS-C4), `NewsManager.tsx` (consumer dell'editor, DIS-C12)
> - confronto: `SPW-C6-advanced-editing.md`, `SR-C6-advanced-editing.md`

## 1. Cosa fa (sintesi narrativa)

C6 è l'editing dei contenuti ricchi di DISINTELLIGENZA — e, coerentemente con tutto il sito, è la
versione **grado zero**: **non usa Tiptap né Quill né alcuna libreria editor**. È un editor
**artigianale** costruito su un `<div contentEditable>` pilotato da `document.execCommand` (l'API DOM
deprecata), con un solo aiuto esterno — `showdown` — per convertire il **markdown incollato** in HTML.

L'osservazione centrale, che chiude il quadro XSS dei tre siti: **DIS non sanitizza NULLA.** Il
contenuto è salvato grezzo (DIS-C4) e renderizzato grezzo: `NewsDetail.tsx` usa
`dangerouslySetInnerHTML` **senza `DOMPurify`** (che non è nemmeno una dipendenza del progetto). E
l'editor stesso inserisce link via `prompt()`→`createLink` **senza alcuna validazione** — quindi un
`javascript:` digitato finisce nell'HTML. Dove SPW e SR hanno una difesa di render (DOMPurify), DIS
**non ha alcun choke point**: lo stored-XSS è esposto end-to-end (mitigato solo dal fatto che scrivere
news richiede login admin/editor — DIS-C2).

Il flusso del contenuto:
1. **Composizione** — l'autore scrive nel `contentEditable`; `onInput` fa
   `onChange(editorRef.current.innerHTML)` (`RichTextEditor.tsx:100-102`). L'HTML è la source of truth
   (come gli altri, ma estratto dal DOM grezzo).
2. **Formattazione** — i pulsanti chiamano `document.execCommand('bold'|'italic'|'foreColor'|
   'justifyLeft'|'insertUnorderedList'|'createLink'|'formatBlock'…)` (`:94-98`). API deprecata, ma
   funzionante nei browser attuali.
3. **Paste intelligente** — un handler `paste` (`:40-86`) riconosce il **markdown** (regex per
   heading/bold/link/list) e lo converte con `showdown`; oppure ripulisce l'**HTML incollato** da
   stili inline di sfondo/colore e da tutte le `class` ("classi CSS nemiche esportate da word o
   wikipedia"). È pulizia *cosmetica* dell'incolla, **non** sicurezza.
4. **Salvataggio** — l'HTML va a `news.php` (DIS-C4), salvato grezzo.
5. **Render pubblico** — `NewsDetail.tsx` inietta l'HTML con `dangerouslySetInnerHTML` **grezzo**.

## 2. Pattern miniCMS rilevanti

- **Editor `contentEditable` + `execCommand` (il pattern "artigianale").** `RichTextEditor.tsx:94-98,
  189-196`: nessuna libreria, un `<div contentEditable>` e l'API `document.execCommand`. È la scelta
  "thin" estrema: zero dipendenze editor (≠ i ~10 pacchetti `@tiptap/*` di SPW/SR), ma su un'API
  **deprecata** e con tutti i limiti del contentEditable nativo (HTML inconsistente tra browser).
- **HTML come source of truth, ma letto dal DOM** (`:100-102`): `onChange(editorRef.current.innerHTML)`.
  Come gli altri il DB conserva HTML, ma qui è l'`innerHTML` grezzo del contentEditable, non l'output
  controllato di un serializzatore (Tiptap `getHTML()`).
- **Sync esterno→editor anti-cursor-jump** (`:22-26`): aggiorna `innerHTML` da `value` **solo se non
  in focus** (per non spostare il cursore). È l'equivalente artigianale del `setContent({emitUpdate:
  false})` di Tiptap — stesso problema (sync senza disturbare l'editing), soluzione manuale.
- **Paste markdown via `showdown`** (`:28-34,48-61`): rileva pattern markdown nel testo incollato e li
  converte in HTML (`makeHtml`). Tocco "developer-friendly" raro: incollare markdown da un altro tool
  e vederlo formattato. Unica dipendenza esterna dell'editor.
- **Pulizia cosmetica dell'incolla HTML** (`:63-85`): su paste di HTML, un `DOMParser` rimuove
  `background`/`color` inline e **tutte** le `class` prima di `insertHTML`. Serve a non importare gli
  stili di Word/Wikipedia, **non** a bloccare script/handler: `<script>`, `onerror`, `javascript:`
  passerebbero (execCommand `insertHTML` + nessun sanitize). → §4.
- **Color picker + heading select + liste + align** (`:124-187`): toolbar essenziale (bold, italic,
  strike, colore, allineamenti, liste, link/unlink, clear). **Niente immagini, niente YouTube,
  niente tabelle** (≠ SPW/SR).
- **Render pubblico grezzo** (`NewsDetail.tsx`, `dangerouslySetInnerHTML` senza DOMPurify): il DB e il
  render sono entrambi "grezzi" → l'unica barriera è il confine admin/editor sulla scrittura (DIS-C2).

## 3. Codice chiave (stralci con origine)

**Editor contentEditable + onChange dall'innerHTML** — `RichTextEditor.tsx:94-102,189-196`:

```tsx
const exec = (command: string, value?: string) => {
    document.execCommand(command, false, value);        // API DEPRECATA
    if (editorRef.current) onChange(editorRef.current.innerHTML);
};
const handleInput = () => { if (editorRef.current) onChange(editorRef.current.innerHTML); };
// ...
<div ref={editorRef} contentEditable onInput={handleInput}
     onFocus={() => setIsFocused(true)} onBlur={() => setIsFocused(false)}
     className="prose prose-invert ..." />
```

**Link via `prompt()` senza alcuna validazione (GOLD sicurezza)** — `RichTextEditor.tsx:104-107`:

```tsx
const promptLink = () => {
    const url = prompt('Inserisci URL:');
    if (url) exec('createLink', url);     // 'javascript:alert(1)' verrebbe inserito tale e quale
};
```

**Paste: markdown→HTML (showdown) + pulizia cosmetica (NON sicurezza)** — `RichTextEditor.tsx:48-85`:

```tsx
const isExplicitMarkdown = hasMarkdownHeaders || hasMarkdownBold || hasMarkdownLinks;
if (isExplicitMarkdown || (!htmlText && hasMarkdownLists)) {
    const mdHtml = mdConverter.makeHtml(plainText);
    document.execCommand('insertHTML', false, mdHtml); return;       // markdown → HTML
}
if (htmlText) {
    const doc = new DOMParser().parseFromString(htmlText, 'text/html');
    doc.querySelectorAll('[style]').forEach(el => { el.style.backgroundColor=''; el.style.color=''; });
    doc.querySelectorAll('*').forEach(el => el.removeAttribute('class'));   // toglie stili/classi, NON script/handler
    document.execCommand('insertHTML', false, doc.body.innerHTML);
}
```

**Render pubblico GREZZO, senza DOMPurify** — `src/pages/NewsDetail.tsx` (DIS non ha `dompurify` in `package.json`):

```tsx
<div dangerouslySetInnerHTML={{ __html: news.content }} />   // nessuna sanitizzazione: HTML del DB iniettato così com'è
```

## 4. Problemi riscontrati & soluzioni

- **GOLD sicurezza — nessuna difesa XSS-stored, da capo a fondo (chiude il quadro a tre).** DIS è
  l'**unico** dei tre siti **senza** sanitizzazione: `content` salvato grezzo (DIS-C4) **e**
  renderizzato grezzo (`NewsDetail.tsx`, `dangerouslySetInnerHTML` senza DOMPurify — che non è
  nemmeno installato). SPW e SR mettono `DOMPurify` come choke point a render-time; DIS no. In più,
  l'editor inserisce link via `prompt`→`createLink` **senza** filtro: un `javascript:` finisce
  letteralmente nell'HTML. Mitigazione **unica**: scrivere news richiede login admin/editor (DIS-C2)
  → è uno stored-XSS da autore autenticato, ma **zero difese in profondità**. → Box "il sito senza
  DOMPurify: quando la difesa XSS-stored manca del tutto" (alto valore, completa il quadro emettitori
  SPW/SR).
- **GOLD — l'editor "thin" all'estremo: `contentEditable` + `execCommand`.** Niente libreria editor
  (≠ ~10 pacchetti `@tiptap/*`): un `<div contentEditable>` e l'API DOM **deprecata** `execCommand`
  (`:94-98`). Funziona, ma è l'opzione più fragile (HTML inconsistente tra browser, comportamenti non
  garantiti in futuro). È il caso-limite "quando il thin stack rinuncia anche all'editor". → Box
  "l'editor senza dipendenze: pro e contro del contentEditable".
- **La pulizia dell'incolla NON è sicurezza** (`:63-85`): rimuove stili inline e `class` per non
  importare la formattazione di Word/Wikipedia, ma **non** tocca `<script>`, attributi `on*`,
  `javascript:`. Il commento parla di "classi nemiche", non di XSS — è cosmesi, e va distinta da una
  sanitizzazione vera (DOMPurify). → nota didattica "sembra sanitize ma non lo è".
- **`showdown` per il markdown incollato** (`:28-34`): comodità reale (incolli markdown e si formatta),
  ma `makeHtml` produce HTML che poi viene iniettato via `insertHTML` **senza** sanitize → un markdown
  con HTML inline malevolo passerebbe. Stessa lacuna del resto.
- **Niente immagini/YouTube/tabelle nel testo** (`:124-187`): l'editor copre solo testo formattato +
  link. Le immagini (cover) sono gestite altrove (NewsManager/upload, DIS-C5), ma **non** si possono
  incorporare nel corpo dell'articolo. Limite funzionale vs SPW/SR. → nota.
- **`innerHTML` grezzo come source of truth.** A differenza di `getHTML()` di Tiptap (che serializza
  uno schema controllato), qui si salva l'`innerHTML` del contentEditable: qualunque markup il browser
  abbia prodotto/accettato finisce nel DB. Meno controllo sulla forma del contenuto. → nota.

## 5. Estetica / UX (moderna ma funzionale)

- **Toolbar essenziale ma curata** (`:122-188`): heading select (P/H2/H3/H4/citazione/codice), bold/
  italic/strike, **color picker a 12 colori**, allineamenti, liste, link/unlink, clear. Coerente con
  l'estetica "terminale" dell'admin DIS (DIS-C12).
- **Paste markdown** (`:48-61`): UX da power-user — si incolla markdown da Notion/ChatGPT e diventa
  HTML formattato. Tocco moderno che riscatta l'editor artigianale.
- **Pulizia incolla da Word/Wikipedia** (`:63-85`): chi incolla da fonti esterne non si porta dietro
  font/sfondi indesiderati — micro-cortesia editoriale (anche se non è sicurezza).
- **Sync anti-cursor-jump** (`:22-26`): aggiorna il contenuto da fuori senza far "saltare" il cursore
  durante la digitazione — dettaglio di qualità del contentEditable fatto a mano.

## 6. Differenze rispetto agli altri siti

Confronto a **TRE** (la tabella completa è in SR-C6 §6). Sintesi per DIS:

| Aspetto | SPW-C6 | SR-C6 | **DIS-C6 (questa card)** |
|---|---|---|---|
| **Motore** | Tiptap v3 (riusabile) | Tiptap v3 (incorporato) + shim Quill | **`contentEditable` + `execCommand`** (artigianale, no libreria) |
| **Dipendenze editor** | ~10 `@tiptap/*` | ~10 `@tiptap/*` (+ Quill relic) | **0** (solo `showdown` per paste) |
| **Guardia link** | `isSafeLinkUrl` | assente | **assente** (`prompt`→`createLink` nudo) |
| **Immagini/YouTube nel testo** | sì (gallery + whitelist) | sì (upload + estensione) | **no** |
| **Sanitizzazione render** | DOMPurify + hook iframe | DOMPurify | **NESSUNA** (HTML grezzo) |
| **Feature unica** | media picker, draft localStorage | shim migrazione Quill→Tiptap | **paste markdown (showdown)** |

**Sintesi.** DIS-C6 è il **terzo gradino della scala editor**: SPW (Tiptap blindato con DOMPurify) →
SR (Tiptap con difesa di render ma guardie più deboli, + migrazione Quill) → **DIS (editor artigianale
`contentEditable` senza alcuna sanitizzazione)**. È il caso perfetto per il capitolo "quanto editor ti
serve davvero": DIS dimostra il minimo assoluto (zero dipendenze) e, insieme, il **costo di sicurezza**
di rinunciare alla difesa di render (è l'unico sito dove lo stored-XSS non incontra alcun choke point).
La sua trovata simpatica — il paste markdown — non compensa l'assenza di DOMPurify.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **L'editor senza dipendenze** (`contentEditable`+`execCommand`) vs Tiptap | Cap. "Quanto editor ti serve": il gradino minimo (alto valore) |
| **Il sito senza DOMPurify**: stored-XSS senza choke point | Box sicurezza "quando manca la difesa di render" (completa il quadro SPW/SR) |
| **"Sembra sanitize ma non lo è"**: pulizia incolla vs sanitizzazione | Box "ripulire l'incolla ≠ difendersi dall'XSS" |
| **Paste markdown con showdown** | Box "un tocco moderno nell'editor artigianale" |
| **`innerHTML` grezzo vs `getHTML()` serializzato** | Box "chi controlla la forma dell'HTML salvato" |
| **La scala editor a tre** (Tiptap blindato / Tiptap+migrazione / contentEditable) | tabella di sintesi cross-sito (FASE 2) |

## 8. Note / domande aperte

- **Puntatori ad altri cluster:**
  - `news.content` grezzo in scrittura → **C4** (già mappato); render grezzo qui = **nessun** choke
    point (a differenza di SPW/SR).
  - **Emettitori del content in DIS:** la newsletter (DIS-C9) **escapa** title/excerpt e **non** emette
    `content`; il SEO proxy `index.php` (DIS-C7, gap in chiusura) e il feed `feed.php` (DIS-C8) vanno
    verificati per capire se emettono `content` grezzo — il rischio XSS-stored si propaga lì.
  - `RichTextEditor` è montato in `NewsManager` (DIS-C12, admin): l'editor è gated dietro login.
  - Upload immagine cover (non inline) → **C5** (già mappato).
- **Sicurezza (rilievo documentale, sola lettura):** l'assenza totale di sanitizzazione + il link via
  `prompt` senza filtro rendono DIS il sito più esposto allo stored-XSS da autore autenticato. Si
  somma agli altri rilievi DIS (RCE upload DIS-C5, no CSRF DIS-C2): è lo stesso quadro "apertura senza
  hardening". Non si modifica il sito sorgente.
- **Conferma:** DIS **non** ha `dompurify` in `package.json`; l'unico `dangerouslySetInnerHTML` del
  frontend è in `NewsDetail.tsx` (grep), senza sanitizzazione.
- Versione del sito: **0.5.x** (`package.json`); editor custom, dipendenza `showdown`.
