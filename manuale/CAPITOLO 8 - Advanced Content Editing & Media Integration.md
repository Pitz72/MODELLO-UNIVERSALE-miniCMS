# CAPITOLO 8: Advanced Content Editing

L'editor di contenuti è il punto in cui un CMS si fa toccare con mano: è lì che l'autore scrive, formatta, incolla, inserisce un'immagine o un video. Sembra un dettaglio di interfaccia, ma porta con sé due domande di fondo che questo capitolo tiene insieme. La prima è quanto editor ti serve davvero, perché si va da una libreria di una decina di pacchetti fino a zero dipendenze. La seconda, più seria, è dove vive la difesa contro l'XSS: il contenuto che l'autore compone è HTML, quell'HTML finisce nel database, e prima o poi qualcuno lo stampa in pagina. Se nessuno lo ripulisce, un `<script>` scritto da chi ha accesso all'editor diventa codice eseguito nel browser di ogni lettore.

I tre siti rispondono su tre gradini. SimonePizziWebSite (SPW) ha un editor Tiptap blindato, con guardie all'inserimento e sanitizzazione al render. SitoRuntime (SR) usa lo stesso motore Tiptap, con la stessa difesa al render, ma con guardie più deboli e una storia in più alle spalle: una migrazione da Quill che ha lasciato cicatrici nel codice. DISINTELLIGENZA (DIS) scende al gradino artigianale, un `contentEditable` pilotato a mano, e qui la difesa XSS sparisce del tutto. La scala dell'editor e la scala della sicurezza, vedremo, non coincidono: il discrimine vero non è quale motore usi, ma se ripulisci l'HTML al momento di stamparlo.

> [!NOTE]
> **Due malintesi da sciogliere subito.** È facile pensare a questo editor come «una soluzione native-React che rinuncia alle pesanti dipendenze esterne». È vero solo per DIS. I due flagship (SPW e SR) usano **Tiptap v3** (ProseMirror), cioè una decina di pacchetti `@tiptap/*`: una dipendenza esterna tutt'altro che leggera. E la «Paste Protection», che a prima vista sembra una difesa capace di rimuovere «script e attributi pericolosi», è in realtà solo una pulizia cosmetica dell'incolla. La difesa XSS reale è altrove, al momento del render, come vedremo in questo capitolo.

---

## 1. L'editor: una scala a tre gradini

Lo stesso bisogno, comporre HTML ricco, è risolto a tre livelli di dipendenza.

### 1.1 SPW: Tiptap v3 «blindato»

SPW fattorizza un componente `RichTextEditor` riusabile attorno a Tiptap v3, con un set mirato di estensioni: testo formattato, immagini, colore, allineamento, tabelle, embed YouTube in modalità `nocookie`. Ogni estensione porta le sue classi Tailwind di default, così l'HTML salvato è già stilizzato per il render pubblico.

```tsx
// src/components/admin/RichTextEditor.tsx:95-138 (estratto)
const editor = useEditor({
    shouldRerenderOnTransaction: true,   // v3: serve per gli stati attivi della toolbar
    extensions: [
        StarterKit.configure({ heading: { levels: [1, 2, 3, 4] } }),
        Image.configure({ HTMLAttributes: { class: 'max-w-full h-auto rounded-xl my-4 ...' } }),
        TextStyle, Color,
        TextAlign.configure({ types: ['heading', 'paragraph'] }),
        Table.configure({ resizable: true }), TableRow, TableHeader, TableCell,
        Youtube.configure({ nocookie: true }),
    ],
    content: value,
    onUpdate: ({ editor }) => { onChange(editor.getHTML()); updateCounts(editor.getText()); },
});
```

### 1.2 SR: lo stesso Tiptap, ma con una migrazione alle spalle

SR usa lo stesso motore, però incorporato direttamente dentro `ArticleEditor.tsx` (toolbar e `useEditor` nello stesso file), e ne tiene una seconda copia in `SpeakerEditor.tsx` per la biografia degli speaker. L'editing ricco non è centralizzato in un componente unico come in SPW: è duplicato per dominio, e una modifica alla configurazione va replicata in due posti.

La sua identità, però, sta altrove: SR è migrato da Quill a Tiptap, e la migrazione è scritta nel codice. Gli articoli vecchi contengono `<iframe>` YouTube «nudi» lasciati da Quill, che Tiptap non sa più editare. Una funzione li riavvolge nel formato che Tiptap riconosce, prima di passarli all'editor:

```tsx
// src/components/admin/ArticleEditor.tsx:29-36
// Converte i bare iframe di Quill in div[data-youtube-video] che Tiptap sa editare.
const QUILL_YT_RE = /<iframe\b[^>]*?\bsrc=["'](https?:\/\/(?:www\.)?youtube(?:-nocookie)?\.com\/embed\/[^"'<>]+)["'][^>]*(?:><\/iframe>|\/>)/gi;
function prepareForEditor(html: string): string {
    return html.replace(QUILL_YT_RE, (_m, src) =>
        `<div data-youtube-video=""><iframe src="${src}" allowfullscreen="true" frameborder="0"></iframe></div>`);
}
// uso: setLoadedContent(prepareForEditor(res.article.content || ''));
```

Restano altre due tracce della vecchia libreria: la classe CSS `ql-video` di Quill, tenuta dentro la configurazione di Tiptap, e il file `react-quill.d.ts` ancora nel repo. Tre indizi convergenti di un cambio di editor mai del tutto ripulito.

> [!TIP]
> **Cambiare editor a contenuti già scritti: il compatibility shim**
> Quando si cambia il motore dell'editor, i contenuti vecchi restano nel formato di prima. Hai due strade: una migrazione una-tantum che riscrive tutti i record nel DB, oppure uno shim che converte il vecchio formato «al volo», ogni volta che apri un contenuto per modificarlo. SR ha scelto la seconda, con `prepareForEditor()`. Il vantaggio è che non tocchi il database e non rischi una migrazione di massa andata storta; il prezzo è che lo shim resta nel codice per sempre, o almeno finché esiste un solo articolo vecchio non riaperto. È un debito che si paga a rate piccole invece che in un colpo solo.

### 1.3 DIS: l'editor artigianale

DIS rinuncia del tutto alla libreria. L'editor è un `<div contentEditable>` pilotato da `document.execCommand`, l'API del DOM ormai deprecata. L'unica dipendenza esterna è `showdown`, e serve solo a convertire il markdown incollato.

```tsx
// src/components/RichTextEditor.tsx:94-102 (estratto)
const exec = (command: string, value?: string) => {
    document.execCommand(command, false, value);        // API deprecata
    if (editorRef.current) onChange(editorRef.current.innerHTML);
};
// <div ref={editorRef} contentEditable onInput={handleInput} className="prose prose-invert ..." />
```

Funziona, e nei browser di oggi gira ancora. Ma è l'opzione più fragile: il `contentEditable` produce HTML diverso da un browser all'altro, `execCommand` è deprecato e il suo comportamento futuro non è garantito.

> [!NOTE]
> **Quanto editor ti serve davvero**
> DIS dimostra il minimo assoluto, zero pacchetti per l'editing, e insieme ne mostra il prezzo: HTML inconsistente, API deprecata, e come «source of truth» l'`innerHTML` grezzo del DOM invece dell'output controllato di un serializzatore come `getHTML()`. La scala non è «più pacchetti uguale meglio». È una scelta di compromesso: SPW e SR pagano una decina di dipendenze per avere uno schema controllato e una UX ricca; DIS non paga nulla e accetta la fragilità. Quello che DIS non può permettersi di togliere, lo vedremo al §3, non è l'editor: è la difesa al render.

---

## 2. L'HTML è la source of truth, e il server lo salva grezzo

Sotto le tre implementazioni c'è una scelta architetturale comune. Nessuno dei tre tiene uno stato JSON o un AST proprietario da ri-serializzare: l'editor emette HTML (il `getHTML()` di Tiptap, o l'`innerHTML` del `contentEditable`) e quell'HTML è esattamente ciò che finisce in `articles.content` o `news.content`. Il contenuto è già nella forma in cui sarà mostrato.

E il server non lo tocca. Coerentemente con quanto visto al CAP 9 sul ciclo di vita dei contenuti, il backend salva il corpo HTML così com'è, senza `strip_tags` né `htmlspecialchars`:

```php
// SPW articles.php:252 — il content entra grezzo nel DB
$content = $data['content'] ?? '';                     // nessun strip_tags / htmlspecialchars
$stmt = $pdo->prepare("INSERT INTO articles (title, slug, content, ...) VALUES (?, ?, ?, ...)");
$stmt->execute([$title, $slug, $content, ...]);        // HTML così com'è
```

Questa non è una svista, è il modello: il contenuto ricco viene conservato fedele e la difesa si sposta al momento in cui lo si stampa. Tutto il peso della sicurezza, quindi, grava su un solo gesto. Vediamo dove.

---

## 3. Sicurezza dei contenuti ricchi: dove vive la difesa XSS

Il `content` è salvato grezzo e scrivere è riservato agli autenticati (login admin o editor, come al CAP 10). Si tratta quindi di uno stored-XSS da autore autenticato: non è il visitatore anonimo a iniettare lo script, ma chi ha accesso all'editor. Il rischio resta reale, perché un account editor compromesso, o un copia-incolla distratto da una fonte ostile, basta a piazzare HTML pericoloso nel database. La domanda è: c'è un punto in cui quell'HTML viene ripulito prima di arrivare al browser del lettore?

### 3.1 Il choke-point: DOMPurify a render-time

In SPW la risposta è una sola funzione, chiamata appena prima dell'unico `dangerouslySetInnerHTML` del componente pubblico. Passa l'HTML per DOMPurify, e con un hook ammette solo gli `<iframe>` di YouTube, rimuovendo qualunque altro:

```tsx
// src/components/SingleArticle.tsx:28-45
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
```

Due dettagli meritano attenzione. L'hook viene sempre rimosso nel `finally`, così non resta registrato a livello globale tra un render e l'altro. E l'aver concesso l'attributo `style` allarga la superficie: serve per i colori inline dell'editor, ed è DOMPurify a ripulire il CSS pericoloso, ma è un compromesso tra fedeltà visiva e sicurezza da tenere presente.

SR fa la stessa cosa, con DOMPurify, su tutte le pagine di dettaglio (articolo, speaker, podcast). Stessa filosofia, stesso choke-point a render-time.

DIS non lo fa. `NewsDetail.tsx` inietta l'HTML grezzo, e `dompurify` non è nemmeno tra le dipendenze del progetto:

```tsx
// src/pages/NewsDetail.tsx — nessuna sanitizzazione
<div dangerouslySetInnerHTML={{ __html: news.content }} />   // HTML del DB iniettato così com'è
```

> [!WARNING]
> **Dove sanitizzare l'HTML di contenuto: il choke-point a render-time**
> Salvare grezzo e ripulire al render è una scelta legittima, a una condizione: che il render ripulisca davvero, e che sia l'unico modo in cui quel contenuto raggiunge un browser. SPW e SR rispettano la condizione con DOMPurify. DIS no, ed è l'unico dei tre dove lo stored-XSS non incontra alcun choke-point: grezzo in scrittura, grezzo al render. La sua unica difesa è il confine admin/editor sull'accesso all'editor. Zero difesa in profondità. Il discrimine tra i due siti sicuri e quello scoperto non è l'editor (Tiptap contro `contentEditable`): è la presenza o l'assenza di questa funzione.

### 3.2 Le guardie all'inserimento: un secondo livello, non il primo

C'è una seconda difesa, più visibile all'autore ma meno decisiva. Quando si inserisce un link dalla toolbar, SPW ne valida l'URL sul posto, bloccando gli schemi pericolosi:

```tsx
// src/components/admin/RichTextEditor.tsx:36-42
const isSafeLinkUrl = (url: string): boolean => {
    const trimmed = url.trim();
    return /^https?:\/\//i.test(trimmed) || trimmed.startsWith('/')
        || trimmed.startsWith('#') || /^mailto:/i.test(trimmed);   // blocca javascript: e data:
};
```

SR e DIS non hanno questo filtro. SR fa `setLink({ href: url })` nudo; DIS prende l'URL da un `prompt()` e lo passa a `createLink` senza guardarlo, così un `javascript:alert(1)` digitato finisce tale e quale nell'HTML:

```tsx
// DIS RichTextEditor.tsx:104-107
const promptLink = () => {
    const url = prompt('Inserisci URL:');
    if (url) exec('createLink', url);     // nessun filtro: 'javascript:...' verrebbe inserito così com'è
};
```

> [!TIP]
> **Due livelli, un solo choke-point reale**
> La guardia all'inserimento (`isSafeLinkUrl`) e la sanitizzazione al render (DOMPurify) non sono intercambiabili. La prima copre solo ciò che passa dalla toolbar, e non tocca l'HTML incollato o costruito in altro modo: è difesa in profondità e buona UX, perché avvisa subito l'autore invece di lasciar passare l'URL fino alla pagina pubblica. Ma la barriera vera, quella che intercetta qualunque HTML comunque sia entrato nel DB, è il render. Se devi sceglierne una sola, scegli il choke-point al render. Averle entrambe è meglio; avere solo la prima è un'illusione di sicurezza.

### 3.3 Ripulire l'incolla non è difendersi dall'XSS

Resta da sciogliere il malinteso della vecchia «Paste Protection». DIS, quando intercetta un incolla, fa due cose: se riconosce del markdown lo converte con `showdown`, altrimenti ripulisce l'HTML dagli stili inline e dalle `class` di Word o Wikipedia. Utile per non importare font e sfondi indesiderati. Ma non è sicurezza:

```tsx
// DIS RichTextEditor.tsx:63-85 (estratto) — pulizia COSMETICA
const doc = new DOMParser().parseFromString(htmlText, 'text/html');
doc.querySelectorAll('[style]').forEach(el => { el.style.backgroundColor=''; el.style.color=''; });
doc.querySelectorAll('*').forEach(el => el.removeAttribute('class'));   // toglie stili/classi, NON script/handler
document.execCommand('insertHTML', false, doc.body.innerHTML);
```

Toglie `style` e `class`, ma lascia passare `<script>`, gli attributi `on*` e gli URL `javascript:`. Il commento nel codice parla di «classi nemiche», non di XSS, ed è onesto: è cosmesi. Va distinta nettamente da una sanitizzazione vera. Rimuovere la formattazione di Word migliora l'aspetto del testo; non protegge nessuno.

---

## 4. Box-ancora: i quattro emettitori del `content`

Qui si apre un filo che attraversa quattro capitoli, e che conviene fissare una volta sola. Il punto di partenza è ciò che abbiamo appena visto: il `content` è salvato grezzo nel database, e la sanitizzazione vive solo nel render React. Ma il render React non è l'unico posto da cui quel contenuto esce verso il mondo. Lo stesso `articles.content` viene riletto e riemesso da almeno quattro «emettitori» diversi, e ognuno deve difendersi per conto suo. La difesa che vive in un solo componente non copre gli altri tre.

| Emettitore | Dove | Cosa fa col `content` | Difesa anti-XSS | Esito |
|---|---|---|---|---|
| **Render React** | pagina pubblica (questo capitolo) | lo inietta via `dangerouslySetInnerHTML` | DOMPurify (SPW, SR) / **niente** (DIS) | choke-point reale; **DIS scoperto** |
| **Prerender SEO** | `index.php` per i bot (CAP 11) | ne riemette il corpo HTML | `strip_tags` con allowlist (SPW, SR) / non emette il corpo (DIS) | **buco attributi** vivo in SPW e SR; DIS immune per sottrazione |
| **Feed RSS** | `rss.php`/`feed_*` (CAP 12) | emette l'articolo | non emette il `content` (SPW usa l'excerpt; DIS fa solo podcast) / lo escapa (SR: `strip_tags` + `htmlspecialchars`) | chiuso |
| **Newsletter** | invio email (CAP 13) | manda l'articolo | nessuno emette il `content` | chiuso |

La lettura è questa. Il feed e la newsletter chiudono il problema, perché o non emettono il corpo o lo escapano del tutto. Il render lo chiude dove c'è DOMPurify e lo lascia aperto in DIS. L'unica falla che resta viva nei flagship è il prerender SEO: per servire ai bot un corpo indicizzabile, SPW e SR riemettono il `content` passandolo per `strip_tags` con una allowlist di tag, che non è DOMPurify. `strip_tags` rimuove i tag non ammessi ma non tocca gli attributi: un `onerror` o un `javascript:` dentro un tag permesso sopravvive. E poiché SR ha copiato il motore SEO di SPW alla lettera, ne ha copiato anche la falla.

> [!IMPORTANT]
> **La lezione del quadro: una sanitizzazione server-side condivisa**
> Quando salvi il contenuto grezzo e affidi la pulizia a chi lo stampa, stai scommettendo che *ogni* punto di stampa si ricordi di ripulire. Bastano quattro emettitori e basta che uno solo dimentichi: in DIS dimentica il render, nei flagship dimentica il prerender. La conclusione che attraversa i prossimi tre capitoli è che la sanitizzazione dovrebbe vivere una volta sola, lato server, là dove il contenuto è prodotto o riletto, invece di essere reinventata da ogni consumatore. Il filo si riapre al CAP 11 (dove il buco del prerender è vivo), si richiude al CAP 12 (il feed che escapa) e si chiude del tutto al CAP 13 (la newsletter che non emette).

---

## 5. Inserire media nel contenuto

Una cosa è gestire la libreria dei media (upload, ottimizzazione, formati: è il CAP 7); un'altra è incorporare un'immagine *dentro* il testo dell'articolo. Qui interessa la seconda, ed è un altro punto in cui i tre siti divergono.

SPW apre una galleria modale, `MediaSelectorModal`, che riusa lo stesso bridge di upload del CAP 7: l'autore sceglie un'immagine già caricata oppure ne carica una nuova con barra di progresso, e l'URL torna all'editor.

```tsx
// src/components/admin/MediaSelectorModal.tsx:65-71 (estratto)
const result = await api.uploadMediaWithProgress(file, (p) => setUploadProgress(p));
if (result.url) onSelect(result.url);     // l'URL diventa un <img src> nell'editor
// galleria: onClick={() => onSelect(item.file_path)}
```

SR salta la galleria: un `<input type="file">` creato al volo, upload diretto, e via. Più semplice, ma niente riuso di immagini già presenti. DIS non permette affatto immagini nel corpo dell'articolo: l'editor copre solo testo formattato e link, e la cover si gestisce altrove.

Sul versante della portabilità, tutti e tre salvano nel database **solo percorsi relativi** (per esempio `/api/uploads/file.jpg`), così il contenuto non si lega a un dominio. Quando serve un URL assoluto, al momento di copiare o condividere un link, è il client a ricostruirlo da `window.location.origin`. La cosa salvata resta portabile; la cosa mostrata si adatta al contesto.

---

## 6. Le micro-cure editoriali

Sotto le differenze, l'esperienza di scrittura condivide alcune attenzioni che vale la pena raccogliere, perché sono il genere di dettaglio che distingue un editor usabile da uno che frustra.

Tutti e tre mostrano in tempo reale il conteggio delle parole e una stima del tempo di lettura. Tutti hanno una toolbar che resta visibile mentre si scorre un articolo lungo (`sticky`), con i pulsanti che non perdono la selezione del testo (`onMouseDown` con `preventDefault`). E tutti devono risolvere lo stesso problema sottile: quando il contenuto cambia «da fuori» (perché si apre un articolo esistente), aggiornare l'editor senza far saltare il cursore né marcare il form come modificato. Tiptap lo fa con `setContent(value, { emitUpdate: false })`, e il commento nel codice di SPW spiega perché:

```tsx
// SPW RichTextEditor.tsx:157-165 — la gotcha di Tiptap v3
// In v3 setContent emette onUpdate di default, marcando il form "dirty"
// e creando bozze fantasma in localStorage. emitUpdate:false lo evita.
editor.commands.setContent(value, { emitUpdate: false });
```

DIS ottiene lo stesso risultato a mano, aggiornando l'`innerHTML` solo quando l'editor non è in focus.

Dove i siti divergono davvero è nella rete di sicurezza contro la perdita del lavoro. SPW salva una bozza in `localStorage` ogni paio di secondi e, alla riapertura, offre un banner per ripristinare la sessione interrotta; lo stato «modificato» alimenta anche un blocco alla navigazione. SR si ferma al `beforeunload`, l'avviso del browser quando chiudi la scheda con modifiche non salvate. DIS non ha né l'uno né l'altro.

> [!TIP]
> **Non perdere il lavoro dell'editor senza un backend**
> Nel thin stack non c'è un endpoint di autosave: la bozza vive nel browser. La soluzione di SPW (`localStorage` più banner di ripristino) è la più robusta a costo zero di backend, e trasforma un crash del browser in una scelta esplicita («ripristina» o «ignora») invece che in lavoro perso. Il limite resta: se cambi dispositivo o pulisci la cache, la bozza non salvata sparisce comunque. Ma tra il niente di DIS e il solo avviso di SR, una bozza locale è la differenza tra perdere mezz'ora di scrittura e ritrovarla.

---

> [!IMPORTANT]
> **Il Canone**
> - Editor Tiptap, HTML come fonte di verità salvato grezzo.
> - La difesa contro l'XSS è la sanitizzazione **al render** (DOMPurify), choke-point unico; la pulizia all'incolla è cosmetica, non sicurezza.
> - Guardie all'inserimento dei link (`isSafeLinkUrl`): niente `javascript:` né URL non validati.
> - I quattro emettitori del `content` (render, prerender SEO, feed, newsletter) condividono la stessa sanitizzazione server-side: se uno la dimentica, il buco XSS si riapre.

*Prossimo Capitolo: Content Lifecycle. Il ciclo di vita dei contenuti, dalla bozza alla pubblicazione programmata, e le tre regole di visibilità che decidono cosa il pubblico vede davvero.*
