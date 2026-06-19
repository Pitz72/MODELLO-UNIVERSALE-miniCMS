# Scheda di Sintesi — S1-C6 — Advanced Editing / Editor

> **Stato:** COMPLETATO
> **Cluster FASE 2:** S1-C6 · **Data:** 2026-06-19 · **Commit:** _(in corso)_
> **Fonti (card di mappatura, in particolare i §6):** SPW-C6, SR-C6, DIS-C6 (+ FDCA-DIFF: frontend riscritto → editor assente, fuori scala)
> **Capitoli del libro toccati:** CAP 8 (Advanced Content Editing & Media Integration) — principale · ponti a CAP 10 (Security, XSS-stored), CAP 11 (SEO, il `content` grezzo nel prerender → S1-C7), CAP 7 (Media, embed nel testo) → vedi §4

---

## 0. In una frase
L'editor di contenuti è una **scala a tre gradini** — Tiptap v3 *blindato* (SPW) / Tiptap v3 con uno
*shim di migrazione da Quill* e guardie più deboli (SR) / editor *artigianale* `contentEditable` +
`execCommand` senza alcuna difesa (DIS) — ma tutti e tre condividono la stessa architettura di
sicurezza: il server salva `content` **grezzo** (S1-C4) e l'unico vero choke-point anti-XSS è
**DOMPurify a render-time**. La lezione del capitolo è quindi doppia: *quanto editor ti serve davvero*
(da ~10 pacchetti a zero dipendenze) e *dove vive la difesa XSS-stored* — con DIS che, non avendo
DOMPurify, è l'unico sito dove lo stored-XSS non incontra **nessun** choke-point.

## 1. Il pattern comune — la filosofia "thin stack" su questa lente

Sotto le tre implementazioni, l'editing ricco dei tre siti condivide quattro tratti.

**1) L'editor produce HTML, e l'HTML è la "source of truth" nel DB.** Nessuno tiene uno stato JSON/AST
proprietario da ri-serializzare: l'editor emette HTML (`getHTML()` di Tiptap, o l'`innerHTML` grezzo
del `contentEditable`) e quell'HTML è ciò che finisce in `articles.content`/`news.content` ed è ciò
che verrà renderizzato. Il contenuto è già nella forma in cui sarà mostrato.

**2) Il server NON sanitizza: la difesa XSS-stored è a render-time.** Coerente con S1-C4, il backend
salva il corpo HTML **così com'è** (nessun `strip_tags`/`htmlspecialchars` sul `content`). La barriera
reale è lato client, **al momento del render** (`dangerouslySetInnerHTML` preceduto — dove c'è — da
DOMPurify). Scrivere è gated dietro login admin/editor (S1-C2): è uno stored-XSS *da autore
autenticato*, ma il modello di difesa è lo stesso ovunque.

**3) Le guardie "all'inserimento" sono un secondo livello, non la difesa primaria.** Dove esistono
(SPW), filtrano l'URL di un link o di un embed *al momento in cui l'autore lo inserisce dalla
toolbar* — ma non toccano l'HTML incollato o costruito altrimenti. Sono difesa in profondità e UX, non
il choke-point: quello resta il render.

**4) Micro-cure editoriali condivise.** Tutti mostrano un conteggio parole + tempo di lettura, tutti
gestiscono il sync esterno→editor senza disturbare il cursore/creare "bozze fantasma" (con tecniche
diverse: `setContent({emitUpdate:false})` in Tiptap, aggiornamento dell'`innerHTML` solo-se-non-in-focus
nel contentEditable), tutti hanno una toolbar sticky con color picker.

A questi si aggiunge un filo che esce dal cluster: poiché il `content` è salvato grezzo e sanitizzato
solo nel render React, **ogni altro emettitore** che stampi lo stesso `content` (il prerender SEO, il
feed RSS, la newsletter) deve ri-sanitizzare per conto proprio — il "quadro dei 4 emettitori del
content" che S1-C7 svilupperà.

## 2. Le varianti per sito (tabella unica, deduplicata)

| Asse | SimonePizziWebSite | SitoRuntime | DISINTELLIGENZA | *(FDCA)* |
|---|---|---|---|---|
| **Motore editor** | **Tiptap v3** (componente `RichTextEditor` riusabile) | **Tiptap v3** (incorporato in `ArticleEditor` + `SpeakerEditor`) | **`contentEditable` + `execCommand`** (artigianale, no libreria) | — |
| **Dipendenze editor** | ~10 `@tiptap/*` | ~10 `@tiptap/*` (+ relic Quill) | **0** (solo `showdown` per il paste) | — |
| **Eredità / migrazione** | nativo Tiptap | **shim Quill→Tiptap** (`prepareForEditor`, `ql-video`, `react-quill.d.ts`) | nessuna (artigianale) | — |
| **Source of truth** | `getHTML()` (schema controllato) | `getHTML()` | **`innerHTML` grezzo** dal DOM | — |
| **Guardia link inserimento** | **`isSafeLinkUrl`** (blocca `javascript:`/`data:`) | **assente** (`setLink` nudo) | **assente** (`prompt`→`createLink` nudo) | — |
| **Embed YouTube** | `normalizeYoutubeUrl` (host-whitelist) | estensione `Youtube` (nocookie) | **assente** | — |
| **Insert immagine nel testo** | `MediaSelectorModal` (galleria + upload, riusa C5) | `<input file>` diretto → upload | **assente** (no immagini inline) | — |
| **Tabelle** | sì (`Table`) | no | no | — |
| **Sanitizzazione render (choke-point XSS)** | **DOMPurify** + hook iframe YouTube-only | **DOMPurify** (Article/SpeakerDetail/PodcastDetail) | **NESSUNA** (`NewsDetail` HTML grezzo) | — |
| **Bozza locale** | `localStorage` + banner recovery + `NavigationBlocker` | solo `beforeunload` | nessuna | — |
| **Preview admin** | overlay salvataggio | **`dangerouslySetInnerHTML` NON sanitizzato** (self, basso rischio) | render grezzo | — |
| **Feature / tocco unico** | gotcha v3 `setContent({emitUpdate:false})`, `SeoScorePanel` | shim migrazione + `published_at` spazio↔`T` | **paste markdown** (`showdown`) + pulizia incolla cosmetica | — |
| **Dove vive l'editor** | solo `ArticleEditor` (`ProjectEditor` = `<textarea>`) | `ArticleEditor` + `SpeakerEditor` (**duplicato**) | `NewsManager` (custom) | — |

**Lettura della tabella.** La scala è netta: **SPW** è il Tiptap "blindato" (guardie all'inserimento +
DOMPurify con hook iframe selettivo + media picker + draft recovery); **SR** è il **gemello sul
motore** (stesso Tiptap, stessa DOMPurify al render, quindi difesa XSS robusta come SPW) ma con **meno
guardie** (niente `isSafeLinkUrl`, niente whitelist YouTube custom, niente galleria) e **una storia in
più** — la migrazione da Quill scritta nel codice; **DIS** è il gradino artigianale, e l'unico con un
**costo di sicurezza reale**: senza DOMPurify (non è nemmeno installato) lo stored-XSS è esposto
end-to-end. Il discrimine non è il motore (Tiptap vs contentEditable) ma la **difesa di render**: SPW
e SR ce l'hanno, DIS no — ed è questo, non l'editor, a separare due siti sicuri da uno scoperto.

**FDCA è fuori scala (come S1-C3):** il frontend riscritto via AI Studio è una vetrina senza area
admin → **nessun editor**. Niente da confrontare; caso fork.

## 3. GOLD & box problemi-soluzioni

- **La scala a tre gradini dell'editor** — *(SPW vs SR vs DIS)* — il GOLD portante. Lo stesso bisogno
  (comporre HTML ricco) risolto a tre livelli di dipendenza: **Tiptap v3 riusabile** (SPW), **Tiptap v3
  incorporato + shim di migrazione** (SR), **`contentEditable` + `execCommand`** senza libreria (DIS).
  È il caso perfetto per "quanto editor ti serve davvero": DIS dimostra il minimo assoluto (zero
  pacchetti) e insieme il prezzo (HTML inconsistente tra browser, API deprecata, `innerHTML` grezzo
  come source of truth). → Box "Quanto editor ti serve: da Tiptap al contentEditable".

- **La difesa XSS-stored vive in un solo punto: il render** — *(tutti, con DIS che lo prova in
  negativo)* — il server salva `content` grezzo; le guardie dell'editor coprono solo gli inserimenti da
  toolbar; l'**unica** barriera reale è DOMPurify a render-time. SPW lo fa con un hook che ammette
  **solo** gli iframe YouTube (`uponSanitizeElement`, rimosso in `finally`); SR con DOMPurify su tutte
  le pagine di dettaglio; **DIS non lo fa affatto** — `NewsDetail` inietta l'HTML grezzo e l'editor
  aggiunge link via `prompt`→`createLink` senza filtro (un `javascript:` finisce nel DB). → Box "Dove
  sanitizzare l'HTML di contenuto: il choke-point a render-time" (alto valore; corregge CAP 8, §4).

- **Il sito senza DOMPurify** — *(DIS, completa il quadro)* — DIS è l'**unico** dei tre senza
  sanitizzazione: grezzo in scrittura (S1-C4) **e** in render. Mitigazione unica: il confine
  admin/editor sulla scrittura (S1-C2). Zero difesa in profondità. La sua trovata simpatica — il
  **paste markdown** via `showdown` — non compensa l'assenza del choke-point. → Box "Quando manca la
  difesa di render" + il ponte: questo `content` grezzo viene riemesso anche dal prerender (S1-C7) e
  dal feed (S1-C8), dove però DIS *non* emette il body — quindi lì il buco non si propaga.

- **Migrare l'editor senza rompere i contenuti vecchi: il compatibility shim** — *(SR, unico)* — SR
  porta tre tracce convergenti di una migrazione **Quill→Tiptap**: `prepareForEditor()` che riavvolge i
  bare `<iframe>` YouTube lasciati da Quill in nodi `<div data-youtube-video>` che Tiptap sa editare;
  la classe CSS `ql-video` *di Quill* tenuta dentro la config Tiptap; il file `react-quill.d.ts`
  ancora nel repo. **Correzione di memoria:** la nota "SitoRuntime usa Quill" è **stale** — oggi è
  Tiptap v3, Quill è solo un fossile. → Box "Cambiare editor a contenuti esistenti" (alto valore).

- **Le guardie all'inserimento: cosa succede se le togli** — *(SPW le ha, SR/DIS no)* — `isSafeLinkUrl`
  (SPW) blocca `javascript:`/`data:` *al punto in cui l'autore inserisce il link*; SR fa `setLink`
  nudo, DIS `createLink` nudo. Non è la difesa primaria (quella è DOMPurify al render), ma è difesa in
  profondità e UX: avvisa subito l'autore invece di lasciare passare l'URL fino al render. → Box "Due
  livelli, un solo choke-point reale".

- **"Sembra sanitize ma non lo è"** — *(DIS)* — la "pulizia dell'incolla" di DIS rimuove stili inline e
  `class` (per non importare la formattazione di Word/Wikipedia) ma **non** tocca `<script>`,
  attributi `on*`, `javascript:`. È cosmesi, non sicurezza — e il commento nel codice parla di "classi
  nemiche", non di XSS. Va distinta nettamente da una sanitizzazione vera. → Box "Ripulire l'incolla ≠
  difendersi dall'XSS".

- **Dove vive l'editor + come si embedda un'immagine** — *(SPW vs SR vs DIS)* — SPW fattorizza un
  `RichTextEditor` riusabile e inserisce immagini via `MediaSelectorModal` (che riusa il bridge upload
  di S1-C5); SR **duplica** l'editor (ArticleEditor + SpeakerEditor) e inserisce via `<input file>`
  diretto; DIS non permette immagini inline. → Box "Un componente o N copie" + "Inserire immagini:
  quanto serve un media picker".

## 4. Mappa → capitolo/i del libro

| Materiale della scheda | Capitolo esistente | Azione |
|---|---|---|
| **La scala a 3 gradini dell'editor** (Tiptap blindato / Tiptap+shim / contentEditable) | **CAP 8 §3** | **riscrivi**: oggi §3 descrive un editor "native-React senza dipendenze" che è solo DIS (vedi correzioni) |
| **Tiptap v3 come editor HTML source-of-truth** (estensioni mirate, classi default) | **CAP 8 §3** | **aggiungi**: CAP 8 non nomina mai Tiptap, il motore reale dei flagship |
| **Difesa XSS-stored a render-time** (DOMPurify + hook iframe) | **CAP 8** (nuova sezione) + **CAP 10** | **nuova sezione**: oggi CAP 8 non parla di DOMPurify né di dove si sanitizza (lacuna) |
| **Il sito senza DOMPurify** (DIS) + link `prompt` nudo | **CAP 10** (ponte) | **nuovo box** sicurezza |
| **Compatibility shim Quill→Tiptap** (SR) | **CAP 8** (nuovo box) | **nuovo box**: caso reale di migrazione editor (manca oggi) |
| **Guardie all'inserimento** (`isSafeLinkUrl`, whitelist YouTube) | **CAP 8 §3** + **CAP 10** | **aggiungi**: oggi assenti dal capitolo |
| **"Sembra sanitize ma non lo è"** (pulizia incolla cosmetica) | **CAP 8 §3** | **correggi §3 "Paste Protection"** (vedi correzioni) |
| **Embed media: media picker vs upload diretto** | **CAP 8 §2** + **CAP 7** | **aggiorna**: §2 descrive un solo modello (il MediaPicker) |
| **Draft system in `localStorage`** (SPW) vs `beforeunload` (SR) vs niente (DIS) | **CAP 8** + **CAP 6** (ponte) | **nuovo box**: non perdere il lavoro dell'editor |
| **Il `content` grezzo riemesso dagli altri consumatori** | **CAP 11** (→ S1-C7) | **ponte**: qui si apre il filo dei "4 emettitori", chiuso in S1-C7 |

**Correzioni al testo attuale (la mappatura smentisce / disallinea il libro):**
- **CAP 8 §3 — l'editor NON è "native-React senza pesanti dipendenze".** Il capitolo dice che l'editor
  "rinuncia a pesanti dipendenze esterne in favore di soluzioni native-React". È vero **solo per DIS**
  (il `contentEditable` grado-zero). I due flagship (**SPW e SR**) usano **Tiptap v3 / ProseMirror**,
  cioè ~10 pacchetti `@tiptap/*` — una dipendenza esterna tutt'altro che leggera. CAP 8 **non nomina
  mai Tiptap**. Da riscrivere come scala a tre gradini (Tiptap riusabile / Tiptap+shim / contentEditable).
- **CAP 8 §3 "Paste Protection" è sovradichiarata, e manca la vera difesa.** Il capitolo dice che il
  paste rimuove "stili inline, **script e attributi pericolosi**". Nella realtà la pulizia dell'incolla
  (DIS) rimuove **solo** stili e classi (cosmesi), **non** script/handler. La difesa XSS reale è
  **DOMPurify a render-time**, che CAP 8 **non menziona affatto**. Da separare i due concetti e
  aggiungere il choke-point di render.
- **CAP 8 ignora del tutto la dimensione di sicurezza dell'editing.** Mancano: dove si sanitizza
  (render-time DOMPurify), le guardie all'inserimento (`isSafeLinkUrl`), e il fatto che **un sito (DIS)
  non ha alcuna sanitizzazione**. Va aggiunta una sezione "Sicurezza dei contenuti ricchi".
- **CAP 8 §1–2 mescolano due modelli di media come se fossero uno.** Le tab "Audio Partecipanti /
  Audio Podcast" (§1.1) sono il modello **festival/DIS** (sottocartelle `participants/`/`podcasts/`,
  S1-C5), mentre il `MediaPicker` (§2) è il `MediaSelectorModal` di **SPW**. Da chiarire che sono di
  siti diversi (il media picker con galleria è di SPW; SR usa upload diretto; DIS ha le tab festival).

## 5. Cosa si scarta / dedup

- **Ripetizioni fuse:** la tabella a TRE viveva già in SR-C6 §6 e DIS-C6 §6 (ridondante). Qui è scritta
  **una volta sola**, dal punto di vista della scala Tiptap-blindato → Tiptap+shim → contentEditable.
- **Dettaglio per-sito che NON entra nel libro:** numeri di riga, le dead-deps `@tiptap/extension-link`/
  `-underline` (dubbio aperto in SPW/SR), il numero esatto di colori del picker (30/21/12), il doppio
  campo `description` sovraccarico nel mapper di SPW, l'`InternalLinkSelector` che carica solo articoli.
  Restano nelle card come fonte.
- **Materiale che appartiene ad altre schede:**
  - **`content` salvato grezzo** lato server, regola di visibilità → **S1-C4**; qui solo l'origine del
    "grezzo nel DB".
  - **gli altri emettitori del content** (prerender, RSS, newsletter) e il buco XSS-attributi del
    prerender → **S1-C7 / S1-C8 / S1-C9**; qui solo il *filo aperto* (la difesa vive in un render).
  - **upload immagine** (validazione, WebP, catena RCE) → **S1-C5**; qui solo l'embed nel testo.
  - **`published_at` spazio↔`T`** e il fuso → **S1-C1/C4** (già consolidato in S1-C4 come "tre modi di
    sbagliare il fuso").
  - **orchestrazione admin** (NewsManager, ArticleEditor come pannello) → **S1-C12**.
