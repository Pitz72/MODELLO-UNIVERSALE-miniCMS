# CAPITOLO 4: Frontend Dependencies (Terza Edizione)

Le dipendenze frontend sono scelte architetturali, non solo righe in `package.json`. Ogni libreria aggiunta ha un costo (dimensione del bundle, superficie di aggiornamento, complessità di integrazione) e deve guadagnarsi il posto. Questo capitolo documenta le scelte fatte nei quattro siti di riferimento, con le motivazioni che le guidano, e dedica spazio anche a un'assenza: le librerie che il Modello sceglie di **non** usare.

## 1. Il Core Stack (Ogni Progetto)

Queste dipendenze sono presenti in tutti e quattro i siti senza eccezioni:

| Libreria | Versione | Ruolo |
| :--- | :--- | :--- |
| `react` + `react-dom` | ^19.2.x | Framework UI: componenti, stato, rendering |
| `react-router-dom` | ^7.x | Routing client-side, React Router v7 (API stabile) |
| `typescript` | ~5.x | Type safety a compile time |
| `vite` | ^7.x | Build tool: dev server HMR, bundle ottimizzato |
| `@vitejs/plugin-react` | ^5.x | Plugin Vite per la trasformazione JSX/TSX |
| `lucide-react` | ^0.5xx | Icone SVG tree-shakeable, native in React |

React 19 introduce miglioramenti al rendering concorrente e alle Server Components. Per il Modello Universale (sola SPA client-side) la differenza pratica con la v18 è minima, ma tenere l'ultima versione stabile è la scelta corretta per i nuovi progetti.

### 1.1 L'Assenza che Conta: Niente Librerie di Data-Fetching

Prima di elencare cosa c'è, vale un elenco di cosa manca, perché è una scelta tanto quanto le altre. Nessuno dei quattro siti usa una libreria di data-fetching o di gestione dello stato: niente Axios, niente React Query, niente SWR, niente Redux, niente Zustand. Il ponte verso il backend PHP è l'oggetto `api`, un wrapper sottile su `fetch` nativo (Capitolo 6); lo stato condiviso vive nel router (SimonePizziWebSite, con i loader di React Router) oppure è `useState` locale ai componenti (SitoRuntime e DISINTELLIGENZA).

Non è pigrizia, è coerenza con la filosofia del Capitolo 1: ogni dipendenza che non aggiungi è una superficie di aggiornamento che non devi mantenere, un bundle che non cresce, un comportamento che non devi imparare. `fetch` fa quasi tutto ciò che serve a un CMS; il poco che manca (un punto unico per gli errori, un interceptor per la sessione scaduta) si scrive in poche righe, e il Capitolo 6 racconta dove i siti hanno scelto di non scriverle.

## 2. Tailwind CSS: v3 contro v4

I quattro siti usano versioni diverse di Tailwind, con configurazione sensibilmente diversa.

### SitoRuntime: Tailwind v3 (setup classico)

```json
// devDependencies
"tailwindcss": "^3.4.17",
"autoprefixer": "^10.4.22",
"postcss": "^8.5.6"
```

Richiede `tailwind.config.js` e `postcss.config.js` espliciti. Il CSS di ingresso:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### SimonePizziWebSite, DISINTELLIGENZA, FDCA: Tailwind v4

```json
// devDependencies
"tailwindcss": "^4.x",
"@tailwindcss/vite": "^4.x"  // oppure "@tailwindcss/postcss"
```

Tailwind v4 usa il plugin Vite nativo: nessun `postcss.config.js` separato, nessun `tailwind.config.js` obbligatorio. Il CSS:
```css
@import "tailwindcss";
```

Per i nuovi progetti la scelta è la v4. La migrazione da v3 richiede attenzione alle classi rinominate (per esempio `shadow-sm` è diventato `shadow-xs`).

### @tailwindcss/typography

Presente in tutti i siti come devDependency. Aggiunge la classe `prose`, che applica stili tipografici curati a blocchi di HTML generato dinamicamente (l'output di un editor di testo ricco, o di un convertitore Markdown).

```html
<div class="prose prose-invert max-w-none">
  <!-- HTML generato da Tiptap o da showdown -->
</div>
```

## 3. Editing e Rendering del Contenuto

### Tiptap v3: il Rich Text Editor dei flagship

**Usato in:** SimonePizziWebSite e SitoRuntime (i due siti con redazione editoriale).

L'editor di testo ricco dei due flagship è **Tiptap v3**, non un editor monolitico ma un insieme di pacchetti `@tiptap/*` che si compongono come mattoncini: una decina di moduli per il nucleo e le estensioni effettivamente usate.

```json
"@tiptap/react": "^3.x",
"@tiptap/pm": "^3.x",
"@tiptap/starter-kit": "^3.x",
"@tiptap/extension-image": "^3.x",
"@tiptap/extension-text-style": "^3.x",
"@tiptap/extension-color": "^3.x",
"@tiptap/extension-text-align": "^3.x",
"@tiptap/extension-table": "^3.x",
"@tiptap/extension-youtube": "^3.x"
```

Tiptap produce **HTML** (non Markdown), che viene salvato grezzo nel database e sanificato al momento del rendering con DOMPurify (la trattazione completa, comprese le guardie all'inserimento dei link e il choke-point di sanitizzazione, è al Capitolo 8). SitoRuntime ci è arrivato con una migrazione: prima usava Quill, e nel codice restano i segni di quel passaggio (uno shim di conversione, qualche type-def `react-quill` residua). Quei residui non sono l'editor attivo, sono cicatrici della migrazione a Tiptap.

DISINTELLIGENZA non usa nessuna libreria di editing: il suo editor è costruito a mano con `contentEditable` ed `execCommand`. È il gradino grado-zero della scala, con la conseguenza di sicurezza che il Capitolo 8 mette in chiaro (è l'unico sito senza DOMPurify).

### showdown: Markdown → HTML

**Usato in:** SimonePizziWebSite, SitoRuntime, DISINTELLIGENZA, per i contenuti scritti in Markdown.

```json
"showdown": "^2.1.0",
"@types/showdown": "^2.0.6"
```

```typescript
import showdown from 'showdown';
const converter = new showdown.Converter({ tables: true, strikethrough: true });
const html = converter.makeHtml(markdownContent);
```

L'HTML generato da contenuto non fidato va sempre sanificato (vedi sotto): showdown e DOMPurify vanno in coppia.

### dompurify: sanitizzazione XSS

**Usato in:** SimonePizziWebSite, SitoRuntime (sempre accoppiato all'editor o al convertitore Markdown). **Assente in DISINTELLIGENZA**, ed è il buco di sicurezza che il Capitolo 8 documenta.

```json
"dompurify": "^3.3.x",
"@types/dompurify": "^3.0.5"
```

```typescript
import DOMPurify from 'dompurify';
const safeHtml = DOMPurify.sanitize(rawHtml);
// Solo ora è sicuro usare dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{ __html: safeHtml }} />
```

> [!WARNING]
> **HTML grezzo più `dangerouslySetInnerHTML` senza DOMPurify è una vulnerabilità XSS**
> Vale per l'output di showdown, di Tiptap, di qualunque sorgente. Salvare HTML grezzo è una scelta legittima (preserva la formattazione), ma il momento del rendering è dove la sanitizzazione diventa obbligatoria. DISINTELLIGENZA salta questo passaggio, e il Capitolo 8 mostra cosa significa.

## 4. Animazioni ed Effetti Visivi

### framer-motion

**Usato in:** tutti e quattro i siti.

```json
"framer-motion": "^12.x"
```

```typescript
import { motion } from 'framer-motion';
<motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
  {/* contenuto */}
</motion.div>
```

framer-motion è pesante (circa 100KB gzip). Si giustifica quando le animazioni sono parte dell'identità visiva del sito; dove sono marginali, le transizioni CSS native sono la scelta giusta.

### typewriter-effect

**Usato in:** SimonePizziWebSite. Effetto macchina da scrivere per le headline animate, specifico per un portfolio personale.

### tailwindcss-animate

**Usato in:** DISINTELLIGENZA. Plugin Tailwind con classi come `animate-in`, `fade-in`, `slide-in-from-bottom`: alternativa leggera a framer-motion per animazioni semplici basate su CSS.

## 5. SEO e Meta Tag

### react-helmet-async

**Usato in:** SimonePizziWebSite, DISINTELLIGENZA. Gestisce `<title>`, `<meta>`, `<link>` dal lato React, per gli utenti con JavaScript attivo.

```json
"react-helmet-async": "^2.0.5"
```

La versione originale (`react-helmet`) non è più mantenuta e ha problemi di memory leak con React 18+; `react-helmet-async` è il fork attivo, compatibile con React 19.

I crawler dei social e dei motori di ricerca non eseguono JavaScript, quindi i meta tag che contano per loro li produce il **SEO Engine PHP** (Capitolo 11). I due si completano, non sono alternativi: SitoRuntime, infatti, rinuncia del tutto a `react-helmet-async` e delega l'intero SEO all'engine lato server.

## 6. Utilities

### clsx + tailwind-merge

**Usati in:** SimonePizziWebSite, DISINTELLIGENZA.

```json
"clsx": "^2.1.1",
"tailwind-merge": "^3.x"
```

`clsx` compone className in modo condizionale; `tailwind-merge` risolve i conflitti tra classi Tailwind (`text-sm text-lg` diventa `text-lg`). Insieme danno il classico helper `cn()`.

### date-fns

**Usato in:** DISINTELLIGENZA, per formattare le date del festival nel frontend. Gli altri siti gestiscono le date lato PHP (`date()`, `strtotime()`), riducendo la complessità nel client.

## 7. Ottimizzazione in Build

### sharp

**Usato in:** SimonePizziWebSite, come `dependency` ma solo negli script post-build.

```json
"sharp": "^0.34.5"
```

`sharp` è una libreria Node.js per la manipolazione di immagini ad alte prestazioni; viene usata negli script di build per ottimizzare gli asset statici. È una `dependency` (non `devDependency`) perché il `postbuild` la richiede al momento della build, ma non entra mai nel bundle React: nessun file `.tsx` la importa. La conversione WebP degli upload a runtime, invece, è tutta lato PHP con GD (Capitolo 7): `sharp` e GD coprono due momenti diversi.

## 8. Matrice delle Dipendenze per Sito

| Libreria | SitoRuntime | DISINTELLIGENZA | FDCA | SimonePizziWebSite |
| :--- | :---: | :---: | :---: | :---: |
| React 19 | sì | sì | sì | sì |
| react-router-dom v7 | sì | sì | sì | sì |
| framer-motion | sì | sì | sì | sì |
| showdown | sì | sì | no | sì |
| dompurify | sì | no | no | sì |
| lucide-react | sì | sì | sì | sì |
| Tailwind v3 | sì | no | no | no |
| Tailwind v4 | no | sì | sì | sì |
| @tailwindcss/typography | sì | sì | sì | sì |
| react-helmet-async | no | sì | sì | sì |
| `@tiptap/*` (editor) | sì | no | no | sì |
| clsx + tailwind-merge | no | sì | sì | sì |
| sharp | no | no | no | sì |
| date-fns | no | sì | sì | no |
| typewriter-effect | no | no | no | sì |
| tailwindcss-animate | no | sì | sì | no |
| *librerie di data-fetching* | no | no | no | no |

L'ultima riga è la più importante del Modello: nessun sito ne ha.

## 9. Regole per i Nuovi Progetti

1. **Parti dal minimo**: core stack, framer-motion, lucide-react. Aggiungi solo quando la funzionalità serve davvero.
2. **Niente data-fetching library**: `fetch` e un oggetto `api` bastano (Capitolo 6). Aggiungere React Query o Axios è quasi sempre peso che non ripaga in un CMS thin-stack.
3. **showdown richiede sempre dompurify** quando il contenuto è user-generated o viene dal database.
4. **Tiptap per l'editing ricco, `<textarea>` per il resto**: monta i pacchetti `@tiptap/*` solo dove serve un editor visivo per i redattori; per un input semplice, una textarea mantiene il bundle piccolo.
5. **react-helmet-async per il SEO client, PHP engine per i crawler**: si completano, non sono alternativi.
6. **Tailwind v4 per i nuovi progetti**: configurazione più semplice; se migri da v3, verifica le classi rinominate.

---
*Capitoli correlati: Capitolo 2 (struttura del progetto) per la configurazione Vite; Capitolo 6 (Frontend Bridge) per l'oggetto `api` su `fetch`; Capitolo 8 (Advanced Content Editing) per Tiptap e la sanitizzazione; Capitolo 11 (SEO) per il rapporto tra react-helmet-async e l'engine PHP.*

---
*Prossimo Capitolo: Backend Logic (PHP). CRUD unificato, gestione dei buffer e sanitizzazione degli input.*
