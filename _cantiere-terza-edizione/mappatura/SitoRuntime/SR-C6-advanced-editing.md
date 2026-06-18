# Mappatura — SitoRuntime — C6: Advanced Editing / Editor & Sanitizzazione

> **Stato:** COMPLETATO · **(card aggiunta in FASE 1-bis: colmatura gap di copertura, 2026-06-18)**
> **Sessione:** 29 · **Data:** 2026-06-18 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `SitoRuntime/`)
> - `src/components/admin/ArticleEditor.tsx` (editor Tiptap v3 dell'articolo: estensioni, toolbar, upload immagine, preview)
> - `src/components/admin/SpeakerEditor.tsx:3-5,43` (un **secondo** editor Tiptap per la bio speaker)
> - `src/types/react-quill.d.ts` (dichiarazione di tipo **residuo di Quill** — fossile di migrazione)
> - `src/pages/Article.tsx` · `SpeakerDetail.tsx` · `PodcastDetail.tsx` · `ShowExtraDetail.tsx` (render pubblico: **DOMPurify**)
> - `package.json` (`@tiptap/* ^3.23.1`, `dompurify ^3.3.0`)
> - confronto: `SPW-C6-advanced-editing.md`

## 1. Cosa fa (sintesi narrativa)

C6 è **l'editing dei contenuti ricchi e la difesa XSS-stored** di SitoRuntime. Come
SimonePizziWebSite (SPW-C6), il motore è **Tiptap v3** (ProseMirror) che produce **HTML** salvato in
`news.content` (C4). Ma rispetto a SPW ci sono due differenze che danno l'identità alla card: (1) SR
porta i **segni di una migrazione da Quill a Tiptap** — un compatibility shim per i vecchi contenuti e
relitti (`react-quill.d.ts`, classe `ql-video`); (2) le **guardie di inserimento sono più deboli**
(nessun `isSafeLinkUrl`), mentre la **difesa di render è ugualmente solida** (DOMPurify nelle pagine
pubbliche).

L'editor non è un componente riusabile come `RichTextEditor` di SPW: è **incorporato dentro
`ArticleEditor.tsx`** (toolbar + `useEditor` nello stesso file), e ne esiste una **seconda istanza**
in `SpeakerEditor.tsx` per la bio dello speaker. Il flusso del contenuto:

1. **Composizione** — Tiptap; ogni `onUpdate` fa `editor.getHTML()` → `formData.content`
   (`ArticleEditor.tsx:102-108`).
2. **Apertura di un articolo esistente** — `setContent(loadedContent, { emitUpdate:false })`
   (`:117`, stesso gotcha v3 di SPW), ma **prima** il contenuto passa per `prepareForEditor()`
   (`:32-36`) che **converte i vecchi `<iframe>` Quill** in nodi `<div data-youtube-video>` Tiptap.
3. **Inserimenti** — immagine via `<input type=file>` diretto → `api.uploadImage` → `setImage(url)`
   (`:162-183`, **nessuna galleria/MediaSelectorModal** come SPW); YouTube via la stessa estensione
   `Youtube`; link via `setLink({href})` **senza guardia di sicurezza** (vedi §4).
4. **Salvataggio** — `api.saveArticle` invia `content`; il server (`admin.php`, C4) lo salva **grezzo**.
5. **Render pubblico** — `Article.tsx` (e `SpeakerDetail`/`PodcastDetail`/`ShowExtraDetail`) usa
   **DOMPurify** prima di `dangerouslySetInnerHTML`: come SPW, il choke point difensivo è a
   **render-time** lato client.

## 2. Pattern miniCMS rilevanti

- **Tiptap v3, HTML come "source of truth"** (`ArticleEditor.tsx:90-112`): identico spirito a SPW —
  l'editor serializza ad HTML salvato direttamente, niente AST proprietario.
- **Estensioni mirate (con UNA in meno di SPW: niente Table).** `:91-100`: `StarterKit` (heading
  1-4), `Image`, `TextStyle`+`Color`, `TextAlign`, `Underline`, `Link` (`openOnClick:false`,
  `rel:noopener noreferrer`), `Youtube` (`nocookie:true`). Set quasi sovrapponibile a SPW ma **senza
  la famiglia Table**. Le immagini portano classi Tailwind di default (`:93`).
- **Shim di migrazione Quill→Tiptap (GOLD, identità della card).** `prepareForEditor()` (`:29-36`)
  riconosce con una regex i **bare `<iframe>` YouTube** lasciati da Quill negli articoli vecchi e li
  riavvolge nel formato `<div data-youtube-video>` che Tiptap sa renderizzare/editare. Inoltre la
  config `Youtube` mantiene `HTMLAttributes: { class: 'ql-video' }` (`:99`) — la **classe CSS di
  Quill** sopravvive dentro la config Tiptap. Più il file `react-quill.d.ts` ancora nel repo. Tre
  tracce convergenti: **SR è migrato da Quill a Tiptap e ne porta le cicatrici**.
- **Due editor Tiptap nello stesso admin** (`ArticleEditor` per `news.content`, `SpeakerEditor` per
  la bio): l'editing ricco non è centralizzato in un componente unico (come `RichTextEditor` di SPW)
  ma **duplicato** per dominio.
- **Inserimento immagine senza galleria** (`:162-183`): un `<input type=file>` creato al volo →
  `api.uploadImage` (C5) → `editor.setImage({src:res.url})`. Più semplice del `MediaSelectorModal`
  di SPW (niente tab galleria/ricerca): si carica e basta.
- **Difesa di render con DOMPurify** (pagine pubbliche): `dompurify` è in `package.json` e usato nei
  componenti di dettaglio (`Article.tsx`, `SpeakerDetail.tsx`, `PodcastDetail.tsx`,
  `ShowExtraDetail.tsx`). Come SPW, l'HTML grezzo del DB viene ripulito **al momento del render**,
  non in scrittura.
- **Gestione `published_at` con conversione spazio↔`T`** (`:74,131`): il default del
  `datetime-local` neutralizza il fuso (`getTimezoneOffset`), e in apertura `published_at.replace(' ',
  'T').slice(0,16)` adatta il `DATETIME` MySQL all'input HTML. Tocca esattamente l'incidente
  separatore-`T` di SR-C1 (qui sul versante client).
- **Anti-perdita-lavoro via `beforeunload`** (`:141-147`): se ci sono modifiche non salvate, il
  browser avverte. **Niente bozza in `localStorage`** (a differenza di SPW): la protezione è solo il
  prompt di uscita, nessun recovery.
- **Word count + tempo di lettura** (`:106-107`, 200 wpm): micro-dato editoriale come SPW.

## 3. Codice chiave (stralci con origine)

**Configurazione Tiptap v3 + classe Quill residua** — `ArticleEditor.tsx:90-100`:

```tsx
const editor = useEditor({
    extensions: [
        StarterKit.configure({ heading: { levels: [1, 2, 3, 4] } }),
        TiptapImage.configure({ HTMLAttributes: { class: 'max-w-full h-auto rounded-lg my-4' } }),
        TextStyle, Color,
        TextAlign.configure({ types: ['heading', 'paragraph'] }),
        Underline,
        TiptapLink.configure({ openOnClick: false, HTMLAttributes: { rel: 'noopener noreferrer' } }),
        Youtube.configure({ nocookie: true, HTMLAttributes: { class: 'ql-video' } }),  // ← classe di QUILL
    ],
    // ...
});
```

**Shim di migrazione Quill→Tiptap (GOLD)** — `ArticleEditor.tsx:29-36`:

```tsx
// Convert Quill bare iframes → Tiptap div[data-youtube-video] so the editor
// can recognize and display them correctly when editing old articles.
const QUILL_YT_RE = /<iframe\b[^>]*?\bsrc=["'](https?:\/\/(?:www\.)?youtube(?:-nocookie)?\.com\/embed\/[^"'<>]+)["'][^>]*(?:><\/iframe>|\/>)/gi;
function prepareForEditor(html: string): string {
    return html.replace(QUILL_YT_RE, (_m, src) =>
        `<div data-youtube-video=""><iframe src="${src}" allowfullscreen="true" frameborder="0"></iframe></div>`);
}
// uso: setLoadedContent(prepareForEditor(res.article.content || ''));   (:134)
```

**Inserimento link SENZA guardia di sicurezza (divergenza da SPW)** — `ArticleEditor.tsx:193-199`:

```tsx
const handleLinkInsert = () => {
    const url = linkUrl.trim();
    if (!url) return;
    editor?.chain().focus().extendMarkRange('link').setLink({ href: url }).run();  // nessun isSafeLinkUrl: javascript:/data: non bloccati all'inserimento
    setLinkUrl(''); setShowLinkInput(false);
};
```

**Inserimento immagine via upload diretto (niente galleria)** — `ArticleEditor.tsx:162-183`:

```tsx
const handleImageInsert = () => {
    const input = document.createElement('input'); input.type = 'file'; input.accept = 'image/*'; input.click();
    input.onchange = async () => {
        const res = await api.uploadImage(input.files![0]);                 // C5
        if (res.success) editor?.chain().focus().setImage({ src: res.url }).run();
    };
};
```

**Preview admin con `dangerouslySetInnerHTML` NON sanitizzato** — `ArticleEditor.tsx:299-307`:

```tsx
<article className="prose prose-invert ..."
    dangerouslySetInnerHTML={{ __html: formData.content }} />   // preview = contenuto proprio dell'admin, NON ripulito
```

## 4. Problemi riscontrati & soluzioni

- **GOLD — la migrazione Quill→Tiptap è scritta nel codice.** Tre tracce: `prepareForEditor()` che
  converte i vecchi embed Quill (`:29-36`), la classe `ql-video` tenuta nella config Tiptap (`:99`),
  e il `react-quill.d.ts` residuo. È la **storia di un cambio di editor** lasciata nel repo per
  retro-compatibilità con i contenuti vecchi. Per il manuale è un caso reale di "migrare l'editor
  senza rompere gli articoli già scritti". (Nota: la memoria di progetto diceva "SitoRuntime usa
  Quill" — **stale**: oggi è Tiptap, Quill è solo un fossile.) → Box "cambiare editor a contenuti
  esistenti: il compatibility shim".
- **GOLD sicurezza — guardia di inserimento link più debole di SPW.** `handleLinkInsert` (`:193-199`)
  fa `setLink({href:url})` **senza** un `isSafeLinkUrl` che blocchi `javascript:`/`data:` (SPW-C6 ce
  l'ha). Tiptap `Link` con `openOnClick:false` riduce il rischio di click accidentale e l'estensione
  applica una sua validazione di base, ma SR **non** aggiunge il filtro esplicito. La rete reale resta
  DOMPurify al render. → Box "le guardie all'inserimento: cosa succede se le togli" (contrappunto SPW).
- **Difesa XSS-stored solo a render-time (come SPW), ma su PIÙ pagine.** Il server salva `content`
  grezzo (C4); la sanitizzazione vive in DOMPurify dentro `Article.tsx` e gli altri dettagli. Stessa
  filosofia di SPW (choke point a render), con la stessa conseguenza: ogni **altro** emettitore che
  stampi `news.content` senza DOMPurify riaprirebbe il buco. In SR la verifica è **già chiusa** dai
  cluster emettitori: il **prerender** `index.php` usa `strip_tags` allowlist (SR-C7, buco attributi
  via UA-spoof), l'**RSS** non emette `content` o lo escapa (SR-C8), la **newsletter** lo escapa
  (SR-C9). → ricuce il quadro "4 emettitori" di SR.
- **Preview admin non sanitizzata** (`:306`): `dangerouslySetInnerHTML={{__html: formData.content}}`
  senza DOMPurify. È l'anteprima dell'autore sul **proprio** contenuto (rischio basso, self-XSS), ma
  è un `dangerouslySetInnerHTML` "nudo" da segnalare. → nota.
- **Editor duplicato (Article + Speaker), niente componente unico.** Due `useEditor` in due file
  (`ArticleEditor`, `SpeakerEditor`): modifiche alla config vanno replicate. Contrasto col
  `RichTextEditor` riusabile di SPW. → nota di fattorizzazione.
- **Niente bozza locale.** Solo `beforeunload` (`:141-147`), nessun autosave `localStorage`: un crash
  del browser perde il lavoro non salvato (SPW recupera da `localStorage`). → box "draft system: SR
  ha meno rete di SPW".
- **`document.execCommand` assente qui (a differenza di DIS).** SR usa l'API Tiptap moderna, non il
  `contentEditable`+`execCommand` deprecato: utile come contrasto con DIS-C6 (vedi §6).

## 5. Estetica / UX (moderna ma funzionale)

- **Toolbar sticky completa** (`:426-608`): heading select, bold/italic/underline/strike, **color
  picker a 21 colori** tematici, allineamenti, liste, immagine, **popup YouTube** e **popup Link**
  con `Enter`/`Escape`, pulsante "cancella formattazione". `onMouseDown preventDefault` per non
  perdere la selezione. UX di pari livello con SPW.
- **Anteprima a tutto schermo** (`:260-310`) con cover, titolo serif, sommario e contenuto renderizzato
  — l'autore vede l'articolo "come sul sito" prima di pubblicare (badge "non salvato").
- **Footer live**: parole + tempo di lettura stimato (`:620-623`).
- **Salva Bozza / Pubblica / Aggiorna** distinti, con stato `draft/published` mostrato come pill
  colorata (`:628-651`).
- **Conferma uscita** su modifiche non salvate (`:154-160`).

## 6. Differenze rispetto agli altri siti

Confronto a **TRE** sull'editor e la difesa XSS-stored.

| Aspetto | SimonePizziWebSite (SPW-C6) | SitoRuntime (questa card) | DISINTELLIGENZA (DIS-C6) |
|---|---|---|---|
| **Motore editor** | Tiptap v3 (componente `RichTextEditor` riusabile) | **Tiptap v3** (incorporato in ArticleEditor + SpeakerEditor) | **custom `contentEditable` + `execCommand`** (no Tiptap) |
| **Eredità/migrazione** | nativo Tiptap | **shim Quill→Tiptap** (prepareForEditor, ql-video, react-quill.d.ts) | nessuna (editor artigianale) |
| **Guardia link** | `isSafeLinkUrl` (blocca `javascript:`/`data:`) | **assente** (setLink nudo) | **assente** (`prompt`→`createLink` nudo) |
| **Embed YouTube** | `normalizeYoutubeUrl` whitelist | estensione Youtube (nocookie) | **assente** |
| **Insert immagine** | `MediaSelectorModal` (galleria+upload) | `<input file>` diretto → upload | **assente** (no immagini nel testo) |
| **Bozza locale** | `localStorage` + recovery | solo `beforeunload` | solo sync esterno |
| **Sanitizzazione render** | DOMPurify + hook iframe YouTube-only | **DOMPurify** (Article.tsx, ecc.) | **NESSUNA** (NewsDetail HTML grezzo) |
| **Tabelle** | sì (Table) | no | no |

**Sintesi.** SR-C6 è il **gemello di SPW sul motore** (Tiptap v3, HTML source-of-truth, DOMPurify al
render) ma con **meno guardie all'inserimento** (niente `isSafeLinkUrl`/whitelist YouTube custom,
niente galleria) e **una storia in più**: la migrazione da Quill, visibile nel compatibility shim. È
il punto intermedio della scala editor: tra il Tiptap "blindato" di SPW e l'editor **artigianale senza
difese** di DIS-C6. La difesa XSS-stored è robusta come SPW (DOMPurify), il che lo distingue nettamente
da DIS (che non ne ha).

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **Migrare l'editor (Quill→Tiptap) senza rompere i contenuti vecchi** (compatibility shim) | Box problemi/soluzioni "cambiare editor a contenuti esistenti" (alto valore, unico di SR) |
| **Tiptap v3 incorporato vs componente riusabile** (SR duplica, SPW fattorizza) | Box "dove vive l'editor: un componente o N copie" |
| **Guardie all'inserimento: SPW le ha, SR no** | confluisce nel box "due livelli, un solo choke point" |
| **Insert immagine: upload diretto vs galleria** | Box "inserire immagini: quanto serve un media picker" |
| **DOMPurify al render su più pagine** | confluisce nel cap. "Dove sanitizzare l'HTML di contenuto" |
| **`published_at` spazio↔T lato client** | confluisce nel box fuso orario (ponte SR-C1) |

## 8. Note / domande aperte

- **Puntatori ad altri cluster:**
  - `news.content` salvato grezzo → **C4** (già mappato); render DOMPurify → choke point qui.
  - Emettitori del content (`index.php` prerender, `feed_news_rss.php`, `newsletter.php`) → **C7/C8/C9**
    (già mappati): SR chiude il quadro "4 emettitori" (a differenza di DIS, vedi §6).
  - `api.uploadImage` (insert immagine) → **C5** (già mappato).
  - `SpeakerEditor` bio → secondo editor; la gestione speaker è **C4**.
- **Correzione memoria:** la nota "SitoRuntime usa Quill" è **superata** — il sito usa **Tiptap v3**;
  Quill è solo un residuo (`react-quill.d.ts`, `ql-video`, shim). Da aggiornare in FASE 2.
- **Da verificare (dead-deps):** se i pacchetti `@tiptap/extension-link`/`-underline` standalone sono
  ridondanti rispetto a quanto già in `StarterKit` v3 (come il dubbio analogo di SPW-C6).
- Versione del sito: **2.9.13** (allineata alle altre card SR); `@tiptap/* ^3.23.1`, `dompurify ^3.3.0`.
