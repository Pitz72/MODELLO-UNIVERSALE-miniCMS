# CAPITOLO 4: Frontend Dependencies (v1.0)

Le dipendenze frontend sono scelte architetturali, non solo dichiarazioni in `package.json`. Ogni libreria aggiunta ha un costo — dimensione del bundle, superficie di aggiornamento, complessità di integrazione — e deve guadagnarsi il suo posto. Questo capitolo documenta le scelte fatte nei 4 siti di riferimento, con le motivazioni che le guidano.

## 1. Il Core Stack (Ogni Progetto)

Queste dipendenze sono presenti in tutti e 4 i siti senza eccezioni:

| Libreria | Versione | Ruolo |
| :--- | :--- | :--- |
| `react` + `react-dom` | ^19.2.x | Framework UI — componenti, stato, rendering |
| `react-router-dom` | ^7.x | Client-side routing, React Router v7 (API stabile) |
| `typescript` | ~5.x | Type safety a compile time |
| `vite` | ^7.x | Build tool — dev server HMR, bundle ottimizzato |
| `@vitejs/plugin-react` | ^5.x | Plugin Vite per JSX/TSX transform |
| `lucide-react` | ^0.5xx | Libreria icone SVG — tree-shakeable, React-native |

React 19 introduce significativi miglioramenti al rendering concorrente e alle Server Components. Per il Modello Universale (solo SPA client-side), la differenza pratica con v18 è minima, ma mantenere l'ultima versione stabile è la scelta corretta per nuovi progetti.

## 2. Tailwind CSS: v3 vs v4

I 4 siti usano versioni diverse di Tailwind, con configurazione significativamente diversa.

### SitoRuntime — Tailwind v3 (Setup Classico)

```json
// devDependencies
"tailwindcss": "^3.4.17",
"autoprefixer": "^10.4.22",
"postcss": "^8.5.6"
```

Richiede `tailwind.config.js` e `postcss.config.js` espliciti. Il file CSS di ingresso:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### SimonePizziWebSite, DISINTELLIGENZA, FDCA — Tailwind v4

```json
// devDependencies
"tailwindcss": "^4.x",
"@tailwindcss/vite": "^4.x"  // o "@tailwindcss/postcss"
```

Tailwind v4 usa il plugin Vite nativo — nessun `postcss.config.js` separato, nessun `tailwind.config.js` obbligatorio. Il file CSS:
```css
@import "tailwindcss";
```

**Quando usare v4**: Per tutti i nuovi progetti. La migrazione da v3 a v4 richiede attenzione alle classi rinominate (es. `shadow-sm` → `shadow-xs`).

### @tailwindcss/typography

Presente in tutti i siti come devDependency. Aggiunge la classe `prose` che applica stili tipografici curati a blocchi di HTML generato dinamicamente (come output Markdown o contenuto da rich text editor).

```html
<div class="prose prose-invert max-w-none">
  {/* HTML generato da showdown o Quill */}
</div>
```

## 3. Rendering del Contenuto

### showdown — Markdown → HTML

**Usato in:** SimonePizziWebSite, SitoRuntime, DISINTELLIGENZA (3/4 siti)

```json
"showdown": "^2.1.0",
"@types/showdown": "^2.0.6"
```

Converte Markdown in HTML. Pattern di utilizzo:
```typescript
import showdown from 'showdown';
const converter = new showdown.Converter({ tables: true, strikethrough: true });
const html = converter.makeHtml(markdownContent);
```

**Non usare mai showdown senza dompurify** — l'HTML generato da contenuto non trusted deve essere sanificato.

### dompurify — Sanitizzazione XSS

**Usato in:** SimonePizziWebSite, SitoRuntime (2/4 siti, sempre accoppiato con showdown o Quill)

```json
"dompurify": "^3.3.x",
"@types/dompurify": "^3.0.5"
```

DOMPurify rimuove script iniettati e attributi pericolosi dall'HTML:

```typescript
import DOMPurify from 'dompurify';
import showdown from 'showdown';

const converter = new showdown.Converter();
const rawHtml = converter.makeHtml(markdownContent);
const safeHtml = DOMPurify.sanitize(rawHtml);

// Solo ora è sicuro usare dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{ __html: safeHtml }} />
```

**Regola assoluta**: `showdown` + `dangerouslySetInnerHTML` senza `DOMPurify` in mezzo è una vulnerabilità XSS. I due vanno sempre in coppia.

### react-quill-new — Rich Text Editor WYSIWYG

**Usato in:** SitoRuntime (1/4 siti — solo dove serve editing visivo avanzato)

```json
"react-quill-new": "^3.7.0",
"quill-image-drop-module": "^1.0.3",
"quill-magic-url": "^4.2.0"
```

`react-quill-new` è il fork mantenuto di `react-quill`, necessario perché la versione originale non supporta React 19. Output in HTML (non Markdown), quindi richiede comunque `DOMPurify` lato rendering.

Il modulo `quill-image-drop-module` aggiunge drag & drop di immagini nell'editor. `quill-magic-url` converte automaticamente URL incollati in link cliccabili.

**Quando usarlo**: Solo quando il progetto richiede un editor visivo tipo Word per i redattori — es. radio web, sito editoriale. Per un portfolio o blog tecnico, un'area textarea con Markdown è più semplice e altrettanto efficace.

## 4. Animazioni & Effetti Visivi

### framer-motion

**Usato in:** tutti e 4 i siti

```json
"framer-motion": "^12.x"
```

La libreria di animazioni declarative per React. Pattern fondamentali nel Modello Universale:

```typescript
import { motion } from 'framer-motion';

// Fade-in all'ingresso del componente
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.4 }}
>
  {/* contenuto */}
</motion.div>

// Animazioni su lista di elementi (staggered)
<motion.ul variants={containerVariants} initial="hidden" animate="show">
  {items.map(item => (
    <motion.li key={item.id} variants={itemVariants}>...</motion.li>
  ))}
</motion.ul>
```

framer-motion è pesante (~100KB gzip). Giustificato quando le animazioni sono parte integrante dell'identità visiva del sito. Per siti dove le animazioni sono marginali, CSS transitions native sono la scelta corretta.

### typewriter-effect

**Usato in:** SimonePizziWebSite (1/4 siti)

```json
"typewriter-effect": "^2.22.0"
```

Effetto macchina da scrivere per headline animati — specifico per portfolio/presentazioni personali.

### tailwindcss-animate

**Usato in:** DISINTELLIGENZA (1/4 siti)

```json
"tailwindcss-animate": "^1.0.7"
```

Plugin Tailwind che aggiunge classi di animazione come `animate-in`, `fade-in`, `slide-in-from-bottom`. Alternativa leggera a framer-motion per animazioni semplici basate su CSS.

## 5. SEO & Meta Tag

### react-helmet-async

**Usato in:** SimonePizziWebSite, DISINTELLIGENZA (2/4 siti)

```json
"react-helmet-async": "^2.0.5"
```

Gestisce dinamicamente `<title>`, `<meta>`, `<link>` nel `<head>` del documento da qualsiasi componente React:

```typescript
import { Helmet } from 'react-helmet-async';

<Helmet>
  <title>{article.title} — Runtime Radio</title>
  <meta name="description" content={article.excerpt} />
  <meta property="og:image" content={article.cover_image} />
</Helmet>
```

**Perché `react-helmet-async` e non `react-helmet`**: La versione originale (`react-helmet`) non è più mantenuta e ha problemi di memory leak con React 18+. `react-helmet-async` è il fork attivo e compatibile con React 19.

**Limitazione importante**: `react-helmet-async` gestisce i meta tag per gli utenti con JavaScript attivo (browser reali). I crawler dei social media e dei motori di ricerca richiedono il **PHP SEO Engine** (Capitolo 11) per ricevere meta tag corretti, perché non eseguono JavaScript.

SitoRuntime non usa `react-helmet-async` perché delega tutto il SEO all'engine PHP lato server.

## 6. Utilities

### clsx + tailwind-merge

**Usati in:** SimonePizziWebSite, DISINTELLIGENZA

```json
"clsx": "^2.1.1",
"tailwind-merge": "^3.x"
```

`clsx` permette la composizione condizionale di className:
```typescript
import { clsx } from 'clsx';
const classes = clsx('base-class', isActive && 'active', error && 'text-red-500');
```

`tailwind-merge` risolve i conflitti tra classi Tailwind (es. `text-sm text-lg` → `text-lg`):
```typescript
import { twMerge } from 'tailwind-merge';
const cn = (...inputs) => twMerge(clsx(inputs)); // Pattern helper classico
```

### date-fns

**Usato in:** DISINTELLIGENZA (1/4 siti)

```json
"date-fns": "^4.1.0"
```

Utilità per la formattazione e manipolazione delle date. Alternativa a `dayjs` e `moment.js` (quest'ultimo deprecato). Usato in DISINTELLIGENZA per formattare le date del festival e delle iscrizioni nel frontend.

Gli altri siti gestiscono la formattazione date lato PHP (con `date()` e `strtotime()`), riducendo la complessità frontend.

## 7. Build-Time Optimization

### sharp

**Usato in:** SimonePizziWebSite (come dependency, usato solo in script post-build)

```json
"sharp": "^0.34.5"
```

`sharp` è una libreria Node.js per la manipolazione di immagini ad alte prestazioni. Nel contesto del Modello Universale, viene usato nel `clean-dist.js` post-build per ottimizzare automaticamente le immagini nella cartella `dist/` prima del deploy.

```javascript
// Esempio di utilizzo in clean-dist.js
import sharp from 'sharp';
await sharp('input.jpg')
  .resize(1200)
  .webp({ quality: 80 })
  .toFile('output.webp');
```

È tecnicamente una `dependency` invece che `devDependency` perché il build script (`postbuild`) la richiede al momento della build — ma non viene mai inclusa nel bundle React (non è importata da nessun file `.tsx`).

## 8. Matrice delle Dipendenze per Sito

| Libreria | SitoRuntime | DISINTELLIGENZA | FDCA | SimonePizziWebSite |
| :--- | :---: | :---: | :---: | :---: |
| React 19 | ✓ | ✓ | ✓ | ✓ |
| react-router-dom v7 | ✓ | ✓ | ✓ | ✓ |
| framer-motion | ✓ | ✓ | ✓ | ✓ |
| showdown | ✓ | ✓ | — | ✓ |
| dompurify | ✓ | — | — | ✓ |
| lucide-react | ✓ | ✓ | ✓ | ✓ |
| Tailwind v3 | ✓ | — | — | — |
| Tailwind v4 | — | ✓ | ✓ | ✓ |
| @tailwindcss/typography | ✓ | ✓ | ✓ | ✓ |
| react-helmet-async | — | ✓ | ✓ | ✓ |
| react-quill-new | ✓ | — | — | — |
| clsx + tailwind-merge | — | ✓ | ✓ | ✓ |
| sharp | — | — | — | ✓ |
| date-fns | — | ✓ | ✓ | — |
| typewriter-effect | — | — | — | ✓ |
| tailwindcss-animate | — | ✓ | ✓ | — |

## 9. Regole per i Nuovi Progetti

1. **Parti dal minimo**: Core stack + framer-motion + lucide-react. Aggiungi solo quando la funzionalità è richiesta concretamente.

2. **showdown richiede sempre dompurify**: Mai usare l'uno senza l'altro quando il contenuto è user-generated o proviene dal DB.

3. **react-quill-new solo per editor WYSIWYG**: Per semplici aree di testo Markdown, un `<textarea>` è sufficiente e mantiene il bundle piccolo.

4. **react-helmet-async per SEO client-side, PHP engine per SEO crawler**: I due si complementano — non sono alternativi.

5. **Tailwind v4 per nuovi progetti**: La configurazione è più semplice. Verificare la compatibilità delle classi se si migra da v3.

---
*Capitoli correlati: Cap 2 (Struttura Progetto) per la configurazione Vite, Cap 7 (Media & Optimization) per sharp nel dettaglio, Cap 11 (SEO Pre-rendering) per il rapporto tra react-helmet-async e PHP engine.*

---
*Prossimo Capitolo: Backend Logic (PHP) - CRUD unificato, gestione dei buffer e sanitizzazione degli input.*
