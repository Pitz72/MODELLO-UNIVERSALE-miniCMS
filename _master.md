---
title: "React + PHP: The Thin Stack"
subtitle: "Il protocollo miniCMS per Web App moderne"
author: "Simone Pizzi"
date: "Maggio 2026 — Seconda Edizione"
lang: it
book: true
classoption: [oneside]
toc: true
toc-own-page: true
toc-depth: 2
colorlinks: true
linkcolor: teal
titlepage: true
titlepage-color: "1E293B"
titlepage-text-color: "FFFFFF"
titlepage-rule-color: "2DD4BF"
titlepage-rule-height: 4
footnotes-pretty: true
code-block-font-size: \footnotesize
...

\part{La Visione}

# CAPITOLO 1: Manifesto

## Perché Esiste Questo Protocollo

Esiste una tensione irrisolta al centro dello sviluppo web moderno.

Da un lato, il frontend ha raggiunto una maturità estetica e funzionale straordinaria: React, TypeScript, Tailwind. Animazioni fluide, componenti riutilizzabili, type safety, hot reload. L'esperienza di sviluppo è diventata un piacere, e il prodotto finale — quando fatto bene — è visivamente e funzionalmente superiore a qualsiasi soluzione del passato.

Dall'altro lato, questa rivoluzione ha portato con sé una complessità infrastrutturale sproporzionata rispetto ai bisogni reali della maggioranza dei siti. Node.js, database cloud, container, pipeline CI/CD, micro-servizi, CMS headless con piani in abbonamento. L'overhead tecnico e il costo operativo sono diventati la norma anche per siti che potrebbero girare perfettamente su un hosting da 5 euro al mese.

Questo protocollo nasce da una domanda precisa: **è possibile avere la potenza estetica e tecnica di React senza abbandonare la semplicità, il controllo e l'economicità di un backend PHP con SQLite?**

La risposta, costruita su anni di lavoro reale su progetti reali, è sì.

\newpage

## Il Principio Fondativo: La Separazione dei Piani

Il Modello Universale non è una tecnologia. È un'architettura mentale.

Separa con nettezza due piani che spesso vengono confusi:

**Il Piano della Presentazione** appartiene a React. È il luogo della forma, dell'interazione, dell'animazione, della tipografia, della palette colori. È dove vive il talento estetico, dove Tailwind traduce l'intenzione visiva in CSS preciso, dove framer-motion aggiunge peso e respiro ai movimenti. Questo piano è compilato, ottimizzato, servito come asset statico.

**Il Piano dei Dati** appartiene a PHP e SQLite (o MySQL quando necessario). È il luogo della persistenza, della logica di business, della sicurezza, del ciclo di vita dei contenuti. Non è "il backend" nel senso pesante del termine — nessun framework, nessun ORM, nessuna dipendenza esterna. Solo PHP nativo, PDO, e un database file-based che non richiede configurazione server.

Questi due piani comunicano attraverso un contratto preciso: le API REST. Il frontend non sa niente del database. Il backend non sa niente di React. La loro separazione è la fonte di tutta la scalabilità e la manutenibilità del sistema.

\newpage

## Cosa Non È Questo Protocollo

Non è un framework. Non impone strutture di codice rigide, non richiede dipendenze specifiche, non vincola le scelte stilistiche.

Non è un CMS tradizionale. Non c'è un'interfaccia visual builder, non ci sono temi preconfezionati, non c'è un marketplace di plugin. Ogni sito costruito con questo protocollo è unico, fatto a mano, tailor-made per il suo scopo.

Non è una soluzione enterprise. Non è progettato per gestire milioni di utenti simultanei, flussi di dati complessi o architetture distribuite. È progettato per siti che devono essere eccellenti, veloci, sicuri e mantenibili da un team piccolo — o anche da una persona sola.

Non è per chi vuole un sito in 10 minuti. È per chi vuole capire cosa sta costruendo.

\newpage

## I Valori che Guidano Ogni Decisione

**Controllo totale.** Chi costruisce un sito con questo protocollo possiede ogni riga del suo stack. Nessun vendor lock-in, nessun aggiornamento forzato che rompe la produzione, nessuna dipendenza da un servizio esterno per la sopravvivenza del sito.

**Leggerezza come principio, non come compromesso.** SQLite non è la scelta "economica" rispetto a MySQL — è la scelta giusta per il 90% dei casi d'uso. La semplicità non è una limitazione da superare: è un obiettivo da raggiungere e difendere.

**La sicurezza come architettura, non come patch.** Le decisioni di sicurezza sono integrate nel design del sistema: database fuori dalla root pubblica, clean-dist.js che non lascia mai il database nel deploy, sessioni PHP con cookie httponly, password mai in chiaro. Non sono misure aggiunte dopo — sono la struttura stessa.

**La documentazione come parte del codice.** Un sistema che non si capisce è un sistema che non si può mantenere. Questo protocollo è documentato con la stessa cura con cui è costruito, perché la conoscenza deve rimanere accessibile anche quando il contesto cambia.

**L'esperienza reale come unico validatore.** Ogni pattern documentato in questo manuale è stato estratto da codice che gira in produzione. Le lezioni più importanti — il crash del WAL in produzione, l'attacco DDoS che ha messo in ginocchio Runtime Radio, la migrazione SQLite/MySQL forzata dal traffico crescente — sono incidenti reali, non scenari ipotetici. La teoria senza la cicatrice non insegna abbastanza.

\newpage

## A Chi È Rivolto

A chiunque voglia costruire un sito web che sia una cosa viva — non un template, non un WordPress personalizzato, non un sito generato da un builder.

Al developer che conosce React e vuole un backend senza dover imparare un framework intero.

Al freelance che deve consegnare un sito veloce, mantenibile e sicuro a un cliente che non ha budget per infrastrutture cloud.

All'autore, al musicista, al festival, alla radio che vuole una presenza digitale propria, controllata, indipendente dai capricci delle piattaforme.

A chiunque creda che il web possa essere ancora un posto fatto da persone, per persone — senza intermediari.

\newpage

## Come Usare Questo Manuale

Il manuale è organizzato in capitoli tematici indipendenti. Non è necessario leggerlo dall'inizio alla fine — ogni capitolo è una reference autonoma.

Per iniziare un nuovo progetto da zero, la **BOILERPLATE-CHECKLIST** è il punto di partenza pratico.

Per migliorare un progetto esistente, i capitoli specifici (Database Strategy, Security & Auth, SEO Pre-rendering) offrono pattern applicabili chirurgicamente.

Per imparare dalla storia, i capitoli con la voce esperienziale (WAL disaster, DDoS su Runtime Radio, migrazione MySQL) sono la lettura più onesta che questo manuale può offrire.

Il codice non mente. Le cicatrici nemmeno.

\newpage

*"La perfezione si raggiunge non quando non c'è più niente da aggiungere, ma quando non c'è più niente da togliere."*
*— Antoine de Saint-Exupéry*

\newpage
*Prossimo Capitolo: Architettura e Struttura Progetto — dove le idee diventano cartelle.*

\part{L'Architettura}

# CAPITOLO 2: Architettura e Struttura Progetto (v1.2 - ADVANCED)

Questa sezione definisce l'architettura fisica e logica del sistema, garantendo sicurezza dei dati, portabilità e scalabilità.

## 1. Topologia delle Cartelle e Asset Separation
Il Modello Universale impone una separazione netta tra i file sorgente (Build-time) e i file di runtime (Persistent-data).

### 1.1 Struttura Fisica (Root)
```text
/
├── public/                 # Contenuto pubblico e Entry Point API
│   ├── .htaccess           # Routing SPA (Cruciale per React Router)
│   ├── index.php           # SEO Engine (Capitolo 11) — entry-point PHP
│   └── api/                # Core Backend PHP (Vedi 1.2)
├── src/                    # Frontend React 19 / TS
├── scripts/                # Utility Tools (Build, Clean, Migration)
├── .env.local              # Configurazione locale (VITE_API_URL)
├── package.json            # Gestione dipendenze e Script di automazione
└── clean-dist.js           # Script di sanitizzazione post-build (SECURITY)
```

### 1.2 Anatomia dell'Area API (public/api/)
La cartella `api/` deve essere configurata per gestire la persistenza senza dipendenze esterne:
- **.data/**: Contiene il database SQLite. Deve contenere un file `.htaccess` con `Deny from all`.
- **.cache/**: File JSON generati dinamicamente per le performance. Puliti automaticamente ad ogni scrittura.
- **uploads/**: Asset caricati dall'utente (immagini, audio). Deve essere esclusa dai backup del codice sorgente.

## 2. Meccanismi di Sicurezza in Build (The Clean-Dist Logic)
Uno dei rischi maggiori è il "Database Overwrite" durante il deploy. Il sistema implementa uno script `clean-dist.js` eseguito post-build che:
1. Analizza la cartella `dist/api/`.
2. Rimuove ricorsivamente ogni file con estensione `.sqlite`, `.sqlite3`, `.db` o `.bak`.
3. Notifica l'operatore con log di sicurezza (`🚨 SECURITY: Removed...`).
4. **Regola Progettuale**: La cartella `dist/` generata deve essere "database-free". Il DB deve essere inizializzato sul server o migrato manualmente, mai sovrascritto dalla build automatica.

Il pattern esatto del build script varia per sito:
- **SimonePizziWebSite**: `"postbuild": "node clean-dist.js"` (hook automatico npm)
- **DISINTELLIGENZA**: `"build": "tsc -b && vite build && node clean-dist.js && move dist\\index.html dist\\index_react.html"` (rinomina index.html per abilitare il SEO Engine PHP, vedi Capitolo 11)
- **SitoRuntime**: `"build": "tsc -b && vite build && node scripts/remove-db-from-dist.js"` (script dedicato in cartella scripts/)

## 3. Gestione del Routing e degli URL (SPA vs API)
Per permettere a React Router di funzionare in armonia con le API PHP su server Apache, lo standard prevede un `.htaccess` nella root pubblica:

```apacheconf
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  # Se la richiesta punta a un file o cartella reale, servilo direttamente (permette alle API di funzionare)
  RewriteCond %{REQUEST_FILENAME} -f [OR]
  RewriteCond %{REQUEST_FILENAME} -d
  RewriteRule ^ - [L]
  # Altrimenti, reindirizza tutto a index.html (o index.php se presente)
  RewriteRule ^ index.html [L]
</IfModule>
```

**Nota**: Apache serve `index.php` prima di `index.html` per priorità predefinita. Questo è il meccanismo che permette al SEO Engine (Capitolo 11) di intercettare le richieste senza modificare le regole di rewrite.

## 4. Inizializzazione Dinamica del File System
Il backend PHP non deve dare per scontato l'esistenza delle cartelle di runtime. Ogni script di inizializzazione (`init_db.php`) o la classe `Database` devono implementare la logica di **Auto-Scaffolding**:

```php
// Logica di creazione cartelle con permessi corretti (0755)
$paths = [__DIR__ . '/.data', __DIR__ . '/.cache', __DIR__ . '/uploads'];
foreach ($paths as $path) {
    if (!is_dir($path)) {
        mkdir($path, 0755, true);
        // Protezione immediata se è la cartella .data
        if (basename($path) === '.data') {
            file_put_contents($path . '/.htaccess', "Order allow,deny\nDeny from all");
        }
    }
}
```

In **SimonePizziWebSite** questo auto-scaffolding è integrato direttamente in `db.php` (connessione lazy), mentre in altri siti è in `init_db.php`. Entrambi i pattern sono validi; il primo è più robusto perché si attiva ad ogni connessione.

## 5. Gestione degli Ambienti (Env Strategy)
- **Local Dev**: React punta a `http://localhost/tuo-progetto/public/api`.
- **Production**: React punta a `/api` (percorso relativo, garantendo la compatibilità con SSL e domini diversi).
- **Vite Config**: Utilizzo del proxy in fase di sviluppo per evitare errori CORS continui.

## 6. Il Pattern Fork (FDCA / DISINTELLIGENZA)
FDCA e DISINTELLIGENZA condividono **identica struttura PHP** (stessi file, stessa logica). Questo è un pattern deliberato: quando due progetti condividono la stessa base funzionale (es. festival con votazioni), si parte da un fork del progetto più maturo.

**Vantaggi**: Nessuna dipendenza condivisa — ogni progetto evolve indipendentemente.
**Rischio**: Bugfix e miglioramenti vanno applicati manualmente a entrambi i fork. Per questo è fondamentale mantenere una documentazione (questo manuale) come fonte di verità comune.

\newpage
*Prossimo Capitolo: Database Strategy - Dettagli avanzati su lock, indici, migrazioni e la vera storia del WAL.*


# CAPITOLO 3: Database Strategy (v1.2 - ADVANCED)

Il database è il cuore pulsante del miniCMS. Questa sezione definisce le strategie di ottimizzazione, integrità e migrazione per garantire performance "zero-latency" anche su hosting condivisi.

## 1. Architettura di Connessione (Agnostic PDO)
Il sistema utilizza un wrapper PDO che astrae il motore sottostante.

### 1.1 Configurazione Ottimale SQLite
Per evitare il problema dei "file lock" comuni su Apache/PHP, il Modello Universale impone:
- **Journal Mode: DELETE**: Più lento di WAL ma infinitamente più stabile su hosting condivisi dove il locking del file system è imprevedibile.
- **Busy Timeout**: Impostato a 5000ms per gestire tentativi di scrittura simultanei (es. Newsletter + Admin).

```php
// In db.php
self::$pdo = new PDO("sqlite:" . $dbPath);
self::$pdo->exec("PRAGMA journal_mode=DELETE;");
self::$pdo->exec("PRAGMA busy_timeout=5000;");
self::$pdo->exec("PRAGMA foreign_keys = ON;");
```

**⚠️ Perché DELETE e non WAL**: SitoRuntime ha tentato di usare `journal_mode=WAL` in produzione per migliorare le performance sotto carico. Il WAL ha causato problemi gravi su hosting condiviso Apache: il file di lock `.sqlite-wal` rimaneva "appeso" corrompendo le letture. È stato necessario uno script di emergenza (`emergency_revert_wal.php`) per tornare a DELETE. **Questa è la lezione: usare sempre DELETE mode su hosting condiviso.**

### 1.2 Auto-Scaffolding della Cartella .data
La classe `Database` in **SimonePizziWebSite** integra la creazione automatica della cartella `.data/` e del relativo `.htaccess` di protezione direttamente nella connessione lazy:

```php
public static function connect() {
    if (self::$pdo === null) {
        $dbPath = __DIR__ . '/.data/database.sqlite';
        $dir    = dirname($dbPath);

        // Crea la cartella se non esiste
        if (!is_dir($dir)) {
            mkdir($dir, 0777, true);
        }

        // Protezione immediata con .htaccess
        $htaccessPath = $dir . '/.htaccess';
        if (!file_exists($htaccessPath)) {
            file_put_contents($htaccessPath, "Require all denied\n");
        }

        try {
            self::$pdo = new PDO('sqlite:' . $dbPath);
            self::$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            self::$pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
            self::$pdo->exec('PRAGMA journal_mode = DELETE;');
            self::$pdo->exec('PRAGMA foreign_keys = ON;');
        } catch (PDOException $e) {
            http_response_code(500);
            echo json_encode(['status' => 'error', 'message' => 'Database connection failed']);
            exit;
        }
    }
    return self::$pdo;
}
```

## 2. Indicizzazione Strategica (Performance Engineering)
Le query di lettura devono essere istantanee. Il Modello Universale impone la creazione dei seguenti indici:

| Tabella | Colonna | Tipo | Scopo |
| :--- | :--- | :--- | :--- |
| `news` / `articles` | `slug` | UNIQUE | Ricerca articolo via URL (SEO) |
| `news` / `articles` | `published_at` | DESC | Ordinamento cronologico veloce |
| `news` / `articles` | `status` | INDEX | Filtraggio Bozza/Pubblicato |
| `speakers` | `sort_order` | ASC | Ordinamento manuale trascinabile |
| `podcasts` | `slug` | UNIQUE | Accesso rapido alle serie |
| `projects` | `category` | INDEX | Filtraggio per categoria portfolio |
| `projects` | `sort_order` | ASC | Ordinamento manuale portfolio |

**Comando di Manutenzione**: Periodicamente (o dopo caricamenti massivi) deve essere eseguito `ANALYZE;` per ricalcolare le statistiche di accesso e ottimizzare il piano di esecuzione delle query.

## 3. Ciclo di Vita delle Migrazioni (Safe-Schema Update)
Le modifiche allo schema devono essere atomiche e reversibili.
- **Atomicità**: Ogni script di migrazione deve utilizzare le transazioni (`beginTransaction`).
- **Idempotenza**: Lo script deve verificare l'esistenza di colonne o tabelle prima di tentare la creazione (`IF NOT EXISTS`, `PRAGMA table_info`).
- **Protezione**: Gli script di migrazione (`update_db_vX.X.X.php`) devono essere protetti da controllo sessione admin per evitare esecuzioni non autorizzate.
- **Nomenclatura**: Il pattern di naming dei siti reali: `update_db_v0.4.2.php`, `update_db_v0.5.4.php`. Numerazione semantica (Major.Minor.Patch) allineata alla versione del progetto in `package.json`.

## 4. Normalizzazione Dati (The "Round" Rule)
Per evitare errori di precisione nei calcoli (es. durata podcast o bitrate), il sistema impone la normalizzazione lato backend prima del salvataggio:
- **Date**: Formato ISO 8601 (`Y-m-d H:i:s`) per compatibilità SQL e JS.
- **Numerici**: Interi puri o arrotondati a zero decimali per evitare bug di virgola mobile tra PHP e SQLite.
- **Booleani**: Sempre `INTEGER` in SQLite (`0` o `1`). In MySQL `TINYINT(1)`.

## 5. Manutenzione e Integrità
- **VACUUM**: Da eseguire mensilmente o post-cancellazione massiva per ricostruire il file database e ridurne il peso fisico.
- **Backup**: Ogni operazione di migrazione deve essere preceduta da una copia fisica del file `.sqlite` in una cartella di backup protetta.
- **optimize_db.php**: SitoRuntime include uno script dedicato alla manutenzione (`VACUUM`, `ANALYZE`, verifica integrità) eseguibile manualmente dall'admin.

## 6. Quando Passare a MySQL
Vedi Capitolo 14 per la storia completa e il processo di migrazione. In sintesi: rimani su SQLite finché il traffico è gestibile (< 50 scritture/ora) e non ci sono vincoli di hosting. La migrazione è documentata con script reali, testati in produzione.

\newpage
*Prossimo Capitolo: Frontend Dependencies - La matrice delle dipendenze, le regole di scelta e il costo di ogni libreria.*


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

\newpage
*Capitoli correlati: Cap 2 (Struttura Progetto) per la configurazione Vite, Cap 7 (Media & Optimization) per sharp nel dettaglio, Cap 11 (SEO Pre-rendering) per il rapporto tra react-helmet-async e PHP engine.*

\newpage
*Prossimo Capitolo: Backend Logic (PHP) - CRUD unificato, gestione dei buffer e sanitizzazione degli input.*

\part{I Componenti}

﻿# CAPITOLO 5: Backend Logic (PHP) (v2.0 - ADVANCED)

Il backend del miniCMS funge da motore di elaborazione dati e guardiano della sicurezza. Questa sezione definisce gli standard per la manipolazione delle stringhe, l'elaborazione dei file e la gestione delle risposte.

## 1. Gestione degli Identificatori (Slug Logic)
Gli URL devono essere parlanti (SEO-friendly) e univoci. Il Modello Universale impone una strategia di generazione e collisione lato server.

### 1.1 Algoritmo Base
```php
function createSlug($string) {
    // Minuscolo, trim e rimozione caratteri non alfanumerici (eccetto trattino)
    $slug = strtolower(trim(preg_replace('/[^A-Za-z0-9-]+/', '-', $string)));
    return $slug;
}
```

### 1.2 Algoritmo Avanzato (con Normalizzazione Accenti Italiani)
Il pattern base produce slug malformati con parole italiane che contengono accenti (es. `"caffÃ¨"` â†’ `"caff-"`). Il pattern avanzato, implementato in **SimonePizziWebSite**, risolve il problema con una mappa esplicita:

```php
function generateSlug($title, $pdo) {
    // Mappa esplicita accenti italiani e francesi comuni
    $accents      = ['Ã ','Ã¨','Ã©','Ã¬','Ã²','Ã¹','Ã€','Ãˆ','Ã‰','ÃŒ','Ã’','Ã™',
                     'Ã¢','Ãª','Ã®','Ã´','Ã»','Ã¤','Ã«','Ã¯','Ã¶','Ã¼'];
    $replacements = ['a','e','e','i','o','u','a','e','e','i','o','u',
                     'a','e','i','o','u','a','e','i','o','u'];

    $title = str_replace($accents, $replacements, $title);
    $slug  = strtolower(trim(preg_replace('/[^A-Za-z0-9-]+/', '-', $title)));

    // Anti-collisione
    $stmt = $pdo->prepare("SELECT COUNT(*) FROM articles WHERE slug = ?");
    $stmt->execute([$slug]);
    if ($stmt->fetchColumn() > 0) {
        $slug .= '-' . time();
    }
    return $slug;
}
```
Usare sempre il pattern avanzato per siti con contenuto italiano.

### 1.3 Strategia Anti-Collisione
In fase di creazione, il backend deve verificare l'esistenza dello slug. Se presente, viene aggiunto un suffisso temporale per garantire l'unicitÃ  senza errori di database.
```php
$stmt = $pdo->prepare("SELECT count(*) FROM news WHERE slug = ?");
$stmt->execute([$slug]);
if ($stmt->fetchColumn() > 0) {
    $slug .= '-' . time(); // Aggiunge timestamp per unicitÃ  assoluta
}
```

## 2. Gestione del Fuso Orario (Timezone Forcing)
Su hosting internazionali (es. server a Los Angeles), `date()` e `time()` usano il timezone del server. Questo causa problemi nella logica `published_at <= NOW()` per siti italiani.

**Soluzione standard** (implementata in SimonePizziWebSite e SitoRuntime):
```php
// All'inizio di ogni endpoint con logica temporale
date_default_timezone_set('Europe/Rome');
$ita_now_str  = date('Y-m-d H:i:s'); // Ora italiana per confronti SQL
$ita_now_time = time();               // Timestamp Unix italiano
```
Questa istruzione va inserita in ogni endpoint che filtra per `published_at` o che genera timestamp di creazione.

## 3. Gestione dei Metodi HTTP (RESTful Completo)
Il Modello Universale supporta tutti i metodi HTTP standard per API RESTful:

- **GET**: Lettura. Supporta `page`, `limit`, `slug`, `id`, `category`, `admin=true`.
- **POST**: Creazione di nuove risorse.
- **PUT**: Sostituzione completa di una risorsa esistente (tutti i campi).
- **PATCH**: Aggiornamento parziale (singolo campo: es. toggle `is_visible`, aggiornamento `sort_order`).
- **DELETE**: Eliminazione di una risorsa.

```php
$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') { /* ... */ }
elseif ($method === 'POST') { Auth::check(); /* ... */ }
elseif ($method === 'PUT') { Auth::check(); /* ... */ }
elseif ($method === 'PATCH') { Auth::check(); /* ... */ }
elseif ($method === 'DELETE') { Auth::check(); /* ... */ }
```

**Nota**: In progetti piÃ¹ vecchi (DISINTELLIGENZA, SitoRuntime prima del refactor), tutte le operazioni di modifica usavano POST con un campo `action` nel body. Il pattern RESTful con metodi separati Ã¨ piÃ¹ leggibile e permette al frontend TypeScript di essere piÃ¹ espressivo.

## 4. Il Pattern auth_helper.php (v2.0) (Autenticazione Inline)
SimonePizziWebSite introduce un pattern piÃ¹ snello per la gestione dell'autenticazione: un file `auth_helper.php` che incapsula `session_start()`, l'header `Content-Type` e la classe `Auth` in un unico include:

```php
<?php
// auth_helper.php
require_once 'db.php';
session_start();
header('Content-Type: application/json');

class Auth {
    public static function check() {
        if (!isset($_SESSION['user_id'])) {
            http_response_code(401);
            echo json_encode(['status' => 'error', 'message' => 'Non autorizzato']);
            exit;
        }
    }
}
```

**Utilizzo in ogni endpoint**:
```php
require_once 'auth_helper.php'; // Gestisce session_start() e Content-Type per tutti

// Nelle route protette:
Auth::check();
```

**Vantaggio**: `session_start()` e `header()` vengono chiamati una volta sola nel file helper â€” meno rischi di "headers already sent" dovuti a spazi o BOM nel file PHP.

## 5. Elaborazione Media e Ottimizzazione Immagini
Il caricamento di un file non Ã¨ un semplice spostamento (`move_uploaded_file`), ma un processo di trasformazione.

### 5.1 Polimorfismo dei Percorsi
Il sistema deve mappare il `type` di upload a percorsi fisici e pubblici differenti, applicando logiche di sicurezza specifiche per ogni categoria:
- **images/**: Accessibili pubblicamente, ridimensionamento automatico.
- **audio/podcasts/**: Solo caricamento via Admin.
- **audio/participants/**: Caricamento aperto (se abilitato), cartella isolata.

### 5.2 Auto-Resize & Trasparenza
Ogni immagine caricata dall'admin deve essere normalizzata (es. max 1920px) per preservare lo spazio su disco e la velocitÃ  di caricamento del frontend.
- **PNG/WebP**: Il backend deve preservare il canale Alpha (`imagealphablending`, `imagesavealpha`).
- **QualitÃ **: Standard fissato a 85% per JPEG/WebP per un bilanciamento ottimale peso/qualitÃ .

## 6. Sicurezza dell'Input e Output
- **Sanitizzazione Nomi**: Ogni file caricato deve essere rinominato usando `uniqid()` e pulito da caratteri speciali per evitare vulnerabilitÃ  di esecuzione script.
- **JSON Integrity**: Ogni risposta deve essere preceduta da `header('Content-Type: application/json')`. In caso di errore, deve essere inviato il codice HTTP corretto (`400`, `401`, `403`, `500`) unito a un messaggio JSON descrittivo.
- **FILTER_SANITIZE_STRING deprecato** (PHP 8.1+): Usare `strip_tags(trim($var))` in alternativa.

## 7. CORS Management
SitoRuntime include un file dedicato `cors.php` per la gestione degli header CORS, utile quando il frontend Ã¨ servito da un dominio diverso dall'API (es. sviluppo locale con Vite proxy):

```php
<?php
// cors.php â€” da includere prima di qualsiasi output nelle API pubbliche
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With");
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit(0); // Risponde al preflight e termina
}
```

**Nota**: In produzione con frontend e API sullo stesso dominio, questo file non Ã¨ necessario. Limitare `Access-Control-Allow-Origin: *` all'ambiente di sviluppo; in produzione specificare il dominio esatto.

## 8. Buffer Management
Per evitare che errori PHP (Notice/Warning) sporchino l'output JSON rendendolo invalido per il frontend, il Modello Universale suggerisce l'uso di `ob_start()` o la disattivazione dei log a schermo in produzione (`display_errors = 0`).

\newpage
*Prossimo Capitolo: Frontend Bridge (API.ts) - La connessione tipizzata tra React e PHP, il pattern Double Read.*



# CAPITOLO 6: Frontend Bridge (API.ts) (v1.1 - ADVANCED)

Il "Bridge" tra React e PHP è il punto di snodo critico per la stabilità dell'applicazione. Questa sezione definisce gli standard per la gestione delle chiamate asincrone, la cattura degli errori parlanti e la sincronizzazione dello stato.

## 1. Architettura del Wrapper Universale
Invece di chiamate `fetch` isolate, il sistema utilizza un oggetto `api` centralizzato che incapsula la logica di base degli URL e degli header.

### 1.1 Il Pattern "Double Read" (Response Cloning)
Per estrarre messaggi di errore dal server senza perdere la possibilità di gestire lo stato HTTP, il Modello Universale impone il clonaggio della risposta:

```typescript
async function handleResponse(res: Response) {
    if (!res.ok) {
        let errorMessage = 'Errore imprevisto dal server';
        try {
            const json = await res.clone().json(); // Clona lo stream
            errorMessage = json.message || errorMessage;
        } catch (e) { /* Ignora errori di parsing */ }
        throw new Error(errorMessage);
    }
    return await res.json();
}
```

## 2. Polimorfismo delle Chiamate
Il Bridge deve adattarsi al tipo di dato inviato, distinguendo tra payload JSON e flussi binari (multipart).

- **JSON Standard**: Utilizzato per configurazioni, news e login. Richiede `JSON.stringify(body)`.
- **FormData**: Obbligatorio per upload di file o form complessi (es. iscrizioni con allegati). Non deve essere stringhizzato; va passato direttamente alla fetch.

## 3. Sincronizzazione dello Stato Globale
### 3.1 Silent Auth Check
L'operazione di `checkAuth` deve essere "silenziosa": non deve lanciare eccezioni in caso di fallimento, ma restituire `null`. Questo permette all'applicazione di decidere se reindirizzare l'utente o permettere la navigazione pubblica senza interrompere il flusso di rendering.

### 3.2 Hard Logout
Per garantire che nessun dato sensibile rimanga negli stati di React (Context, Redux, etc.), l'azione di logout deve concludersi con un `window.location.reload()`, resettando l'intero ambiente di esecuzione del browser.

## 4. Validazione Incrociata (HTTP vs Logic)
Alcune risposte del backend potrebbero essere tecnicamente corrette (HTTP 200) ma contenere fallimenti logici. Il Bridge deve validare entrambi i livelli:

```typescript
const data = await res.json();
if (data.status === 'error') throw new Error(data.message);
return data;
```

## 5. TypeScript Integration (Type Safety)
Ogni metodo dell'oggetto API deve (dove possibile) essere tipizzato. Questo garantisce che il frontend conosca esattamente la struttura dei dati (es. `NewsArticle[]`, `UserRole`, `StatsResponse`) riducendo errori di runtime dovuti a proprietà mancanti o rinominate.

## 6. Scalabilità e Paginazione Backend-driven
Nei primi stadi di vita di un portfolio o blog, fetching globali (es. estrattore massivo di tutti gli articoli array-based) sono tollerabili. Tuttavia, l'esperienza operativa di SimonePizziWebSite (giunto alla v1.7.12) manifesta come tale ingenuità causi degradazione prestazionale e memory issues (rallentamento del Time to Interactive React).

Lo standard del Modello Universale eleva l'approccio alla **paginazione nativa server-side**:
- **Parametrizzazione Query**: Le API GET di liste (articoli, log, item) devono accettare query params tipizzati `?page=N&limit=10`. Le query backend devono forzare stringhe di `LIMIT :limit OFFSET :offs`.
- **Custom React Hooks**: Il bridge usa hook specializzati (come `useFetchArticles`) che conservano lo step matematico e lo stato `hasMore`. La logica "Carica altro" non sostituisce lo scope del JS, ma *appensa* linearmente i nuovi frame JSON ricevuti.
- **Strategie Pre-Fetch Limitizzate**: Sezioni UI ad alta densità (come vetrine e griglie Home Page) limitizzano *at runtime* la chiamata (es. `slice(0, 7)`) garantendo un mounting fulmineo.

\newpage
*Prossimo Capitolo: Media & Optimization - Caching, ridimensionamento e SEO.*


# CAPITOLO 7: Media & Optimization (v1.3 - ADVANCED)

Per garantire un'esperienza utente istantanea e un'indicizzazione SEO perfetta, il Modello Universale adotta strategie di caching aggressivo e pre-rendering dei metadati.

## 1. Architettura di Caching (The TTL Strategy)
Il database non deve essere interrogato per query di sola lettura ripetitive. Il sistema implementa un caching basato su file JSON.

### 1.1 Cache Paginata (Listings)
Ogni richiesta di lista (es. `news.php?page=1`) genera un file univoco in `.cache/` (es. `news_p1_l10.json`).
- **Validità**: Il file viene servito direttamente se creato meno di 300 secondi fa.
- **Header di Tracciamento**: Il sistema deve inviare `X-Cache: HIT` o `X-Cache: MISS` per monitorare l'efficienza del sistema.

### 1.2 Invalidazione Intelligente
Ad ogni operazione di scrittura (`POST`), il backend deve pulire la cartella `.cache/` per garantire che il pubblico veda immediatamente le nuove modifiche, evitando il "vizio" dei dati obsoleti.

## 2. SEO & Social Pre-rendering
Le Single Page Application (SPA) hanno problemi di SEO. Il Modello Universale risolve questo problema con un **PHP Entry-Point** (non una cache file JSON separata come in approcci precedenti).

### 2.1 Il Meccanismo (Riferimento Completo: Capitolo 11)
L'`index.php` nella root pubblica intercetta tutte le richieste, estrae lo slug dall'URL, interroga direttamente il database SQLite, e inietta i meta tag `og:title`, `og:description` e `og:image` nell'HTML generato da Vite prima di servirlo. I bot di social e i motori di ricerca ricevono HTML completo con meta tag corretti.

**Flusso**:
1. Apache riceve richiesta `/categoria/mio-slug`
2. `.htaccess` -> nessun file fisico trovato -> passa a `index.php`
3. `index.php` interroga SQLite per `slug = 'mio-slug'`
4. Inietta meta tag nell'HTML di Vite via `str_replace('</head>', $seoBlock, $html)`
5. Serve HTML completo al browser/bot

## 3. Ottimizzazione Media & Smart Upload
Il miniCMS evolve verso una gestione professionale degli asset per massimizzare il punteggio PageSpeed e la sicurezza del server.

### 3.1 Smart Upload & Anti-Spoofing
Non è sufficiente controllare l'estensione del file. Il sistema implementa una **validazione MIME rigorosa**:
- **Anti-Spoofing**: Utilizzo di `finfo_file()` per verificare il magic byte reale del file, impedendo il caricamento di script malevoli mascherati da immagini (es. `shell.php.jpg`).
- **Sottocartelle Dinamiche**: Per evitare il rallentamento del file system (limitazione degli inode per cartella), gli upload vengono smistati automaticamente in cartelle basate sulla data: `uploads/YYYY/MM/`. Il database memorizza il path relativo completo.

### 3.2 Normalizzazione Immagini e Auto-WebP (PHP GD)
Non è permesso servire immagini "grezze" caricate dall'utente. Il backend PHP (script di upload) implementa due passi inderogabili:
- **Ridimensionamento geometrico**: Scale-down proporzionale automatico a **max 1920px** (larghezza) o 1080px (altezza). Questo abbatte il peso dei file caricati da smartphone o fotocamere professionali (spesso >10MB) a pochi KB.
- **Transcodifica obbligatoria WebP**: Conversione on-the-fly via PHP GD (`imagewebp()`). Il formato WebP garantisce una riduzione del peso del 30-50% rispetto a JPG/PNG mantenendo una qualità visiva eccellente.

### 3.3 Sharp (Node.js) per Image Processing Build-Time
**SimonePizziWebSite** introduce `sharp` come dipendenza Node.js per il processing di immagini in fase di build o come utility script. Sharp è più performante di PHP GD per batch processing e supporta formati moderni (AVIF, WebP) con qualità superiore. Non è un'alternativa al backend PHP per upload live — è complementare per pre-processing di asset statici.

### 3.4 Cache Control sui File Statici
Tramite `.htaccess`, i file nella cartella `uploads/` devono essere serviti con header di cache a lungo termine:
```apacheconf
<IfModule mod_expires.c>
    ExpiresActive On
    <FilesMatch "\.(jpg|jpeg|png|gif|webp|svg|ico)$">
        ExpiresDefault "access plus 1 year"
        Header set Cache-Control "max-age=31536000, public"
    </FilesMatch>
</IfModule>
```

## 4. Manutenzione e Rebuilding
Il sistema include script protetti per operazioni straordinarie:
- **rebuild_seo_cache.php**: Rigenera i file JSON SEO.
- **optimize_db.php**: Esegue `VACUUM` e `ANALYZE` (SQLite) o `OPTIMIZE TABLE` (MySQL).

## 5. Portabilità Dati: Full Content Exporter
Per prevenire il vendor lock-in e facilitare i backup migratori, il miniCMS include un **Full Content Exporter** nell'area admin:
- **Meccanismo**: Genera dinamicamente un file **ZIP** contenente l'intero database (dump SQL o file .sqlite) e la cartella `uploads/` completa.
- **Sicurezza**: Lo script di export deve verificare i permessi admin e cancellare lo ZIP temporaneo dopo il download per non occupare spazio inutile e non esporre dati sensibili.

## 6. Benefici Tecnici
- **PageSpeed**: L'uso combinato di WebP, Resize e Caching JSON porta il punteggio LCP (Largest Contentful Paint) sotto i 1.2s.
- **Sicurezza**: La validazione MIME frena l'80% degli attacchi di tipo RCE (Remote Code Execution) legati agli upload.

\newpage
*Prossimo Capitolo: Advanced Content Editing & Media Integration - L'editor definitivo.*


# CAPITOLO 8: Advanced Content Editing & Media Integration (v1.1 - ADVANCED)

Il Modello Universale (miniCMS) eleva l'esperienza di editing trasformandola in un centro di controllo multimediale integrato. Questa sezione definisce gli standard per la gestione degli asset, l'editing del testo e l'integrazione fluida tra i due mondi.

## 1. Il Media Center Centralizzato
L'architettura dei media non Ã¨ un semplice file browser, ma un gestore di stato con logiche di anteprima e azioni di massa.

### 1.1 Filtraggio Contestuale (Tab Strategy)
I media vengono organizzati in base alla loro natura e destinazione, filtrati dinamicamente tramite i percorsi del file system:
- **Immagini**: Filtrate per mime-type `image/*`.
- **Audio Partecipanti**: Isolati nella sottocartella `/participants/`.
- **Audio Podcast**: Riservati alla cartella `/podcasts/` con permessi di scrittura limitati agli Admin.

### 1.2 Gestione Asset Avanzata
Il sistema deve implementare funzioni di manutenzione proattiva:
- **Bulk Delete**: Selezione multipla e cancellazione atomica per la pulizia del server.
- **Audio Engine**: Player integrato (`Audio API`) per il pre-ascolto istantaneo direttamente dalla griglia media.
- **Visual Feedback**: Visualizzazione del peso dei file (`formatBytes`) per sensibilizzare l'editor sull'occupazione del disco.

## 2. Il Componente MediaPicker (Integration Layer)
Il `MediaPicker` Ã¨ il ponte tra l'editor di news e la libreria media.
- **Modal Logic**: Deve aprirsi in sovrapposizione (Overlay) senza perdere lo stato del form sottostante.
- **Search & Filter**: Ricerca testuale in tempo reale sulla lista dei file e filtraggio automatico per il tipo di dato richiesto dal form (es. solo immagini per la cover, solo audio per il podcast).
- **Selection Callback**: Restituzione dell'URL relativo al componente genitore, con chiusura automatica del modale.

## 3. Rich Text Editor & Formattazione (UX Avanzata)
L'editor di testo Ã¨ il cuore dell'interfaccia. Pur rinunciando a pesanti dipendenze esterne in favore di soluzioni native-React, le evoluzioni architetturali (v1.7.9) prevedono l'implementazione obbligatoria dei seguenti pattern UX:
- **Sticky Actions**: La toolbar di formattazione deve utilizzare `sticky top-0 z-30` (o simili) affinchÃ© non scompaia mai dallo schermo durante la scrittura di articoli molto lunghi.
- **Keyboard Shortcuts**: L'intercettazione nativa degli eventi tastiera (es. `Ctrl+K`) per innescare modali specifici (es. inserimento link) senza costringere l'uso del mouse.
- **Metriche in Real-Time**: Il rendering di una status bar a piÃ¨ di pagina con contatori istantanei di parole e caratteri, fornendo metriche vitali per il targeting SEO.
- **InteroperabilitÃ  Tabelle**: Funzioni native per l'inserimento di griglie di dati compatibili con i plugin di Typography del frontend pubblico.
- **State Reset (Key Strategy)**: L'uso rigido di `key={id}` nel componente genitore React per garantire la pulizia istantanea dei buffer interni al caricamento di un nuovo articolo.
- **Paste Protection**: Intercettazione pro-attiva dell'evento `paste` con rimozione di stili inline, script e attributi pericolosi (generati tipicamente incollando da Word o Wikipedia).
- **Markdown Paster**: Conversione silenziosa "in volo" se il testo intercettato segue notazioni Markdown verso l'HTML semantico compatibile.

## 4. Gestione degli URL e PortabilitÃ 
- **Relative Path Strategy**: Nel database vengono salvati solo percorsi relativi (es. `/api/uploads/file.jpg`).
- **Absolute Resolver**: In fase di condivisione o copia (pulsante "Copia URL"), il sistema trasforma il percorso in URL assoluto (`window.location.origin + path`) per garantire che i link funzionino anche al di fuori dell'applicazione.

## 5. UX e Feedback Visivo
- **Miniature (Lazy Loading)**: Caricamento differito delle miniature nella griglia media per non appesantire il browser in librerie con centinaia di file.
- **Transizioni**: Uso di animazioni CSS (`animate-in`, `fade-in`) per rendere fluida l'apertura dei modali e il caricamento delle liste.

\newpage
*Conclusione: Il Modello Universale miniCMS Ã¨ ora un sistema completo, sicuro e scalabile, pronto per essere impiegato come standard universale.*

\newpage
*Prossimo Capitolo: Content Lifecycle - Il ciclo di vita dei contenuti, dalla bozza alla pubblicazione programmata, con il pattern di bypass admin.*



\part{Il Flusso Operativo}


\part{Il Flusso Operativo}

# CAPITOLO 9: Content Lifecycle (v1.2 - ADVANCED)

Il Modello Universale trasforma un semplice database in un sistema editoriale dinamico. Questa sezione definisce la logica degli stati, la programmazione temporale e il feedback visivo necessario per una gestione professionale del palinsesto.

## 1. Stati Dinamici vs Stati Persistenti
Mentre il database salva uno stato "statico" (`status`), l'applicazione deve calcolare uno stato "dinamico" basato sul tempo.

### 1.1 Matrice degli Stati
| DB Status | Data di Pubblicazione | Stato Reale (UI) | Descrizione |
| :--- | :--- | :--- | :--- |
| `draft` | *Qualsiasi* | **BOZZA** | Mai visibile al pubblico. |
| `published` | `> NOW()` | **PROGRAMMATO** | Visibile solo agli Admin, in attesa del momento giusto. |
| `published` | `<= NOW()` | **PUBBLICATO** | Visibile a tutti. |

## 2. Implementazione della "Programmazione Reale"
La programmazione non richiede cron job. La visibilità è controllata dalla query SQL e riflessa nella logica React.

### 2.1 Logica Frontend (React)
Per fornire feedback immediato all'amministratore, la tabella di gestione deve calcolare lo stato al volo:

```typescript
const isDraft = item.status === 'draft';
const isScheduled = item.status === 'published' && new Date(item.published_at) > new Date();
const isPublished = item.status === 'published' && new Date(item.published_at) <= new Date();
```

### 2.2 Normalizzazione Data/Ora (Input Strategy)
Il formato `datetime-local` del browser utilizza il separatore `T`, mentre il DB richiede uno spazio. Lo standard impone la conversione bidirezionale nel componente di editing:

```typescript
// Da DB a UI
value={published_at.replace(' ', 'T').slice(0, 16)}

// Da UI a DB
onChange={e => setPublishedAt(e.target.value.replace('T', ' ') + ':00')}
```

### 2.3 UX della Tabella di Gestione (Admin)
Mentre le API formiscono i dati bruti, la dashboard amministrativa (rivisitata architetturalmente in SimonePizziWebSite v1.7.x) impone standard visivi di proporzione per la tabella articoli (`ArticlesList.tsx`), vitali per non asfissiare l'editing:
- **Contenimento Titolo**: La main column (Titolo) non deve eccedere il 45% della table-grid.
- **Badge Cromatico Categoria**: Rendere esplicita una colonna per la "Categoria" (15% di footprint) decorata con badge a colori sfalsati per la selezione rapida con lo sguardo.
- **Metadati Fissi**: Riservare il 20% alle Date di pubblicazione ed un 20% allo Stato dinamicamente calcolato (Bozza/Programmato).
- **Icon Actions**: Condensare l'edit/delete in action-button con icona standardizzata a fine riga (senza label text) per salvare la responsività da tablet.

## 3. Workflow Editoriale e Integrità
- **Auto-Slug**: Lo slug deve essere rigenerato solo alla creazione o se esplicitamente richiesto, per evitare di rompere i link esistenti (SEO integrity) in caso di modifica del titolo.
- **Rich Text Reset**: Durante il passaggio tra la modifica di due contenuti diversi, il componente editor deve essere forzatamente rimosso e reinserito (`key={item.id}`) per pulire i buffer interni e prevenire perdite di dati cross-articolo.
- **Anteprima Immediata**: Il form deve mostrare una miniatura (preview) dell'immagine di copertina selezionata, con possibilità di rimozione istantanea prima del salvataggio.

## 4. Gestione Categorie Sincrone e Tagging Relazionale
Storicamente (fino alle versioni 1.6), il tagging veniva gestito come campo testuale e organizzato visivamente dividendo con la virgola. Questa pratica (flat-string) rende i filtri globali fragili e non scalabili.

Dalla versione 1.7.12 (SimonePizziWebSite), lo standard miniCMS decreta il passaggio esclusivo all'architettura **RDBMS Multi-Tagging Relazionale**:
1. Abbandono stringhe statiche per la generazione delle tabelle relazionali: `tags` e `article_tags` (per le relazioni Many-to-Many).
2. L'editor React per la generazione/scrittura degli articoli fa il preload dei `tags` censiti sul database popolando un sistema **Select Multiplo API-driven**, annullando il tasso d'errore (typo) dell'editor.
3. Questo permette al filesystem SQL di creare rotte parametriche iper-semantiche e query combinate (es: `articoli categoria X e tag Y`) a costo misero.

## 5. Security & Visibility (Bypass Logic)

Gli endpoint API devono implementare una logica di "Bypass" per gli utenti autenticati:
- **Pubblico**: `WHERE status = 'published' AND published_at <= NOW()`
- **Admin**: nessun filtro — lista completa con bozze e articoli programmati nel futuro

Questo permette all'amministratore di testare la visualizzazione di un articolo programmato semplicemente navigando sul sito dopo aver effettuato il login, senza alcun meccanismo di preview separato.

### 5.1 Bypass per Singolo Articolo (via Slug)

L'endpoint recupera sempre l'articolo dal DB indipendentemente dallo stato. La decisione di mostrarlo o meno avviene *dopo* il fetch, in base alla sessione:

```php
// GET /api/articles.php?slug=titolo-articolo
$stmt = $pdo->prepare("SELECT * FROM articles WHERE slug = ?");
$stmt->execute([$_GET['slug']]);
$article = $stmt->fetch();

if ($article) {
    $is_admin = isset($_SESSION['user_id']); // Sessione attiva = admin

    // Articolo pubblico: status=published E data nel passato/presente
    $is_published = $article['status'] === 'published' &&
                    (empty($article['published_at']) || strtotime($article['published_at']) <= $ita_now_time);

    // Fingere il 404 — non 403 — per non rivelare l'esistenza di bozze a utenti non autenticati
    if (!$is_admin && !$is_published) {
        http_response_code(404);
        echo json_encode(['error' => 'Articolo non trovato']);
        exit;
    }

    echo json_encode($article); // Admin vede tutto: bozze, programmati, pubblicati
}
```

**Principio chiave**: il 404 simulato (anziché il 403) è una misura di sicurezza deliberata. Un 403 confermerebbe l'esistenza del contenuto; un 404 lo nega.

### 5.2 Bypass per Lista (via Parametro Admin)

Per la dashboard amministrativa, che deve mostrare *tutti* gli articoli incluse le bozze, si usa un parametro esplicito combinato con il controllo sessione:

```php
// GET /api/articles.php?admin=true (solo da dashboard autenticata)
$is_admin_dashboard = isset($_SESSION['user_id']) &&
                      isset($_GET['admin']) &&
                      $_GET['admin'] === 'true';

if (!$is_admin_dashboard) {
    // Filtri pubblici: solo pubblicati e già usciti
    $conditions[] = "status = 'published'";
    $conditions[] = "(published_at IS NULL OR published_at = '' OR published_at <= ?)";
    $params[] = $ita_now_str; // Stringa datetime calcolata all'inizio dello script
}
// Se $is_admin_dashboard === true: nessun filtro, lista completa
```

Il doppio controllo (`session + parametro`) è fondamentale: il parametro `?admin=true` da solo sarebbe bypassabile da chiunque.

### 5.3 Accesso per ID (Editor Admin)

Un terzo pattern — fetch per ID anziché slug — serve esclusivamente al form di editing in dashboard. Richiede autenticazione obbligatoria:

```php
// GET /api/articles.php?id=42 (solo admin editor)
if (isset($_GET['id'])) {
    Auth::check(); // Termina con 401 se non autenticato
    $stmt = $pdo->prepare("SELECT * FROM articles WHERE id = ?");
    $stmt->execute([$_GET['id']]);
    // ...
}
```

Questo endpoint bypassa il filtro sullo stato perché è progettato per caricare nel form anche le bozze mai pubblicate.

\newpage
*Prossimo Capitolo: Security & Auth - Gestione sessioni, ruoli e protezione avanzata.*


# CAPITOLO 10: Security & Auth (v1.2 - ADVANCED)

La sicurezza nel Modello Universale non Ã¨ un'opzione, ma un'architettura stratificata che protegge l'integritÃ  dei dati e la privacy degli utenti attraverso controlli sia lato client che lato server.

## 1. Gestione della Sessione (Stateful-Sec)
Il sistema utilizza sessioni PHP native, ma con parametri di sicurezza moderni per prevenire il dirottamento (Session Hijacking).

### 1.1 Configurazione Server-Side
Prima di ogni `session_start()`, il sistema deve configurare i cookie per essere inaccessibili agli script JavaScript (prevenzione XSS):
```php
ini_set('session.cookie_httponly', 1);
ini_set('session.cookie_secure', 1); // Solo se HTTPS
ini_set('session.cookie_samesite', 'Lax');
session_start();
```

### 1.2 Endpoint check_auth
Il frontend non deve mai memorizzare la password o lo stato di login in `localStorage`. Deve invece interrogare periodicamente il server per confermare che la sessione sia ancora valida:
```php
if (isset($_SESSION['user_id'])) {
    echo json_encode([
        'status' => 'success',
        'user' => [
            'username' => $_SESSION['username'],
            'role' => $_SESSION['role']
        ]
    ]);
}
```

## 2. Architettura Protected Routes (React)
L'accesso all'area Admin Ã¨ protetto da un **Higher-Order Component** o un **Layout Wrapper** (`AdminLayout.tsx`).

### 2.1 Bootstrapping della Sicurezza
All'interno del `useEffect` principale, l'app verifica l'identitÃ . Se il server risponde con `401 Unauthorized`, il frontend distrugge lo stato locale e reindirizza istantaneamente alla pagina di login, impedendo flash di contenuti sensibili.

### 2.2 Role-Based UI (RBAC)
La sidebar e le rotte admin vengono generate dinamicamente in base al ruolo ricevuto dal server:
- **Admin**: Accesso a Gestione Utenti, Impostazioni di Sistema, Reset Database.
- **Editor**: Accesso limitato a News, Media e Podcast.

## 3. Sicurezza Crittografica
- **Hashing**: Le password vengono salvate esclusivamente tramite `password_hash($pass, PASSWORD_DEFAULT)`.
- **Verifica**: In fase di login, si utilizza `password_verify($pass, $hash)`. Il sistema non conosce mai la password in chiaro dell'utente.
- **Brute Force Mitigation**: Gli endpoint di login devono implementare un ritardo artificiale (`sleep(1)`) in caso di errore per rallentare i tentativi di attacco automatizzato.

## 4. Protezione del Database SQLite
Il database fisico (`.sqlite`) deve essere protetto da accesso diretto tramite URL.
- **Strategia 1**: Posizionamento del file in una cartella esterna alla root pubblica (es. `../data/`).
- **Strategia 2**: Se all'interno della root, protezione tramite `.htaccess` (`Deny from all`) e scelta di nomi file non prevedibili.

## 5. Sanitizzazione dei Buffer di Output
Per evitare che errori PHP involontari (Notice/Warning) rompano l'output JSON e forniscano indizi ad un attaccante (Path Disclosure), lo standard impone:
- `error_reporting(0);` in produzione.
- Cattura delle eccezioni via `try-catch` e restituzione di messaggi di errore "parlanti" ma generici.

\newpage

## 6. Caso Reale: L'Attacco DDoS a Runtime Radio (Febbraio 2026)

> *"I grafici del traffico hanno iniziato a disegnare picchi anomali, simili a pareti verticali."*

Questa sezione documenta un incidente reale accaduto a **Runtime Radio (runtimeradio.com)** tra il 23 e il 27 febbraio 2026. Non Ã¨ un caso di studio teorico: Ã¨ una cicatrice viva nel codice e nell'architettura del progetto.

### 6.1 Il Contesto: Due Crisi Sovrapposte

La settimana del 23 febbraio 2026 ha visto due eventi distinti che si sono sovrapposti in modo devastante:

**Crisi 1 â€” Collasso del Database (23 febbraio)**
Il traffico crescente sulla piattaforma aveva messo sotto stress il database SQLite per mesi. Il 23 febbraio il sistema ha ceduto: l'infrastruttura database, sottodimensionata rispetto al carico reale, ha smesso di rispondere. *"Il sistema aveva tenuto per mesi, poi Ã¨ ceduto tutto insieme, e rapidamente."* In meno di 24 ore il team ha completato la migrazione completa dei dati a MySQL â€” senza perdita di dati (vedi Capitolo 14 per il processo di migrazione).

**Crisi 2 â€” L'Attacco DDoS (24-27 febbraio)**
Mentre l'infrastruttura era giÃ  in fase di stabilizzazione post-migrazione, Ã¨ arrivato l'attacco. I server hanno iniziato a restituire errori 503 e 500. Il traffico mostrava picchi anomali, verticali, impossibili da spiegare con la crescita organica degli utenti.

### 6.2 Il Vettore di Attacco: I Bot dei Social Media

La vulnerabilitÃ  sfruttata era elegante e insidiosa. Runtime Radio, come tutti i siti costruiti con il Modello Universale, implementava il **SEO pre-rendering via PHP entry-point** (Capitolo 11): ogni richiesta in arrivo veniva processata da `index.php`, che interrogava il database per estrarre i meta tag OG corretti da servire ai crawler di Telegram, Facebook e X/Twitter.

Questa funzionalitÃ  â€” progettata per migliorare l'esperienza di condivisione dei link sui social â€” si Ã¨ trasformata in un'arma. Migliaia di bot ostili, **simulando i crawler dei social media**, hanno bombardato il server con richieste continue. Ogni richiesta forzava una query al database. Il database â€” appena migrato, ancora in fase di stabilizzazione â€” ha ceduto sotto il peso.

```
Bot ostile â†’ simula Telegram/Facebook crawler
â†’ richiesta a / o /news/slug
â†’ index.php â†’ query MySQL â†’ meta tag
â†’ risposta â†’ bot scarta â†’ ripete 1000 volte/secondo
â†’ MySQL sopraffatto â†’ 503/500
```

**La lezione**: qualsiasi endpoint che interroga il database per rispondere a richieste non autenticate Ã¨ un potenziale bersaglio. I bot dei social media sono riconoscibili dallo user-agent â€” e possono essere falsificati.

### 6.3 La Risposta: Tre Livelli di Difesa

La risoluzione Ã¨ avvenuta in fasi, documentata nell'articolo *"Sopravvivere alla Tempesta"* (27 febbraio 2026):

**Fase 1 â€” Spegnimento d'Emergenza con Degradazione Controllata**
Il sito principale Ã¨ stato messo offline, ma lo **streaming audio Ã¨ rimasto attivo** tramite una pagina statica di manutenzione. Principio fondamentale: il servizio core (la radio) non si interrompe mai, anche durante un attacco. La pagina di manutenzione non interrogava nessun database.

**Fase 2 â€” Cache Precompilata per i Bot**
La soluzione definitiva ha separato il percorso delle richieste dei bot da quello degli utenti reali:
- Le risposte per i crawler social (i tag OG, i meta SEO) vengono ora servite da **file JSON statici precompilati**, scritti nel momento in cui un articolo viene pubblicato o aggiornato.
- Il bot riceve la risposta in millisecondi, **senza che il database venga mai interrogato**.
- Solo le richieste di utenti reali (browser con JavaScript) ricevono la pagina React completa.

**Fase 3 â€” Sistema Ibrido Leggero e Corazzato**
L'architettura risultante distingue esplicitamente tra:
- **Richieste bot** (identificate dallo user-agent): servite da cache statica, zero DB access.
- **Richieste umane**: percorso normale, React SPA + API.

```php
// Pattern anti-DDoS: identificazione bot e servizio da cache statica
$userAgent = $_SERVER['HTTP_USER_AGENT'] ?? '';
$isSocialBot = preg_match('/facebookexternalhit|Twitterbot|TelegramBot|LinkedInBot|WhatsApp/i', $userAgent);

if ($isSocialBot && $slug) {
    $cacheFile = __DIR__ . '/api/.cache/seo_' . md5($slug) . '.json';
    if (file_exists($cacheFile)) {
        $seoData = json_decode(file_get_contents($cacheFile), true);
        // Serve meta tag da cache statica â€” nessuna query DB
        // ... iniezione nell'HTML ...
        exit;
    }
}
// Percorso normale per utenti reali
```

### 6.4 Le Persone

L'incidente non Ã¨ stato risolto in solitudine. Carlo Santagostino, Walter Sbano, Peppe Pugliese e Valerio Galano (del podcast *Pensieri in Codice*) hanno contribuito alla ricostruzione dell'infrastruttura. La comunitÃ  tecnica intorno al progetto si Ã¨ dimostrata parte dell'architettura di resilienza â€” non solo il codice.

### 6.5 Le Lezioni da Portare in Ogni Progetto

1. **Ogni endpoint pubblico che interroga il DB Ã¨ un bersaglio potenziale.** Valutare sempre se la risposta puÃ² essere servita da cache statica per le richieste non autenticate.

2. **I bot dei social media possono essere falsificati.** Non fare mai affidamento solo sullo user-agent per decisioni di sicurezza critiche â€” usarlo solo per ottimizzare le performance (cache bot), mai come gatekeeper di accesso.

3. **Il servizio core deve sopravvivere a qualsiasi crisi.** Progettare sempre una "modalitÃ  degradata" che mantenga attiva la funzione principale del sito (streaming, in questo caso) anche quando tutto il resto Ã¨ offline.

4. **La migrazione del database non Ã¨ mai un momento sicuro.** Un sistema appena migrato Ã¨ fragile. Pianificare la migrazione in periodi di basso traffico e avere un piano di emergenza pronto prima di iniziare.

5. **La cache non Ã¨ solo una ottimizzazione di performance â€” Ã¨ un layer di sicurezza.** Un sistema che risponde alle richieste ripetitive senza interrogare il database Ã¨ intrinsecamente piÃ¹ resiliente agli attacchi volumetrici.

\newpage
*Prossimo Capitolo: SEO Pre-rendering con PHP Entry-Point - Il motore SEO invisibile che trasforma una SPA in un sito indicizzabile.*




# CAPITOLO 11: SEO Pre-rendering con PHP Entry-Point (v1.0)

Il problema fondamentale delle Single Page Application (SPA) React è che i bot di Google, Facebook, Twitter e LinkedIn vedono solo un `<div id="root"></div>` vuoto: JavaScript non viene eseguito al momento della scansione. Il Modello Universale risolve questo problema con un **PHP Entry-Point** che inietta i meta tag corretti nell'HTML prima che arrivi al bot, senza rinunciare alla potenza di React.

Questo capitolo documenta il pattern reale implementato in **SimonePizziWebSite (v1.4.0)** e menzionato in forma più semplice in SitoRuntime.

## 1. Il Problema e la Soluzione

### Il Problema
```
Bot Google → richiede /videogiochi/mio-articolo
Server → serve index.html (solo <div id="root">)
Bot → "non c'è contenuto, ignoro"
```

### La Soluzione: The Swap Trick
```
Bot Google → richiede /videogiochi/mio-articolo
Server → Apache → index.php (invece di index.html!)
index.php → query SQLite → estrae title, description, image dell'articolo
index.php → legge index.html compilato da Vite → inietta meta tag → serve HTML completo
Bot → "ho trovato contenuto, indexo"
```

> [!WARNING]
> **I Limiti della Soluzione (Incidente "Sito Invisibile")**
> L'esperienza sul campo (SimonePizziWebSite v1.7.x) ha dimostrato che il trick dello Swap PHP è una soluzione eccellente per **Social Bot** (Telegram, Facebook, Twitter, iMessage) che si accontentano dei meta-tag nell'<head>.
> Tuttavia, **NON è sufficiente per l'indicizzazione organica su Google (SEO puro)**. I moderni crawler come Googlebot cercano l'HTML renderizzato semantico nel `<body>`. Trovando solo un `<div id="root">`, Google indicizzerà pochissime pagine (es. 1 su 30).
> Per risolvere l'indicizzazione SEO profonda di una SPA, l'architettura miniCMS consiglia l'integrazione di plugin per **Static Prerendering** in fase di build (come `vite-plugin-prerender`), pur mantenendo l'infrastruttura di deploy immutata.

## 2. Il Meccanismo: Build Rename Strategy

Il trick sta nel **rinominare** l'`index.html` generato da Vite in modo che `index.php` possa occupare quella posizione come entry-point principale.

### In DISINTELLIGENZA (build script in package.json):
```json
"build": "tsc -b && vite build && node clean-dist.js && move dist\\index.html dist\\index_react.html"
```
Vite genera `dist/index.html`, lo script di build lo rinomina in `dist/index_react.html`. L'`index.php` nella cartella sorgente viene poi copiato nella `dist/` durante il deploy. In questo modo Apache serve `index.php` come file predefinito.

### In SimonePizziWebSite (build script standard):
```json
"build": "tsc && vite build",
"postbuild": "node clean-dist.js"
```
Qui `index.php` è già nella cartella `public/` e Vite compila tutti gli asset statici nella stessa cartella (o la struttura è organizzata diversamente). Il risultato è identico: `index.php` è il file servito da Apache.

## 3. Il Codice di index.php (Analisi Completa)

```php
<?php
/**
 * SEO ENGINE SERVER-SIDE (v1.4.0)
 * Intercetta le richieste di React Router, interroga il database,
 * popola i meta tag HTML (OpenGraph/Twitter) e passa il controllo a React.
 */

// 1. META DI DEFAULT (Fallback per homepage e rotte sconosciute)
$protocol = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off' || $_SERVER['SERVER_PORT'] == 443)
    ? "https://" : "http://";
$metaTitle       = "Nome Sito - Tagline principale";
$metaDescription = "Descrizione generale del sito per SEO";
$metaImage       = $protocol . $_SERVER['HTTP_HOST'] . "/og-default.png";
$currentUrl      = $protocol . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI'];

// 2. ESTRAZIONE SLUG DALL'URL
$request_uri = trim($_SERVER['REQUEST_URI'], '/');
$uri_parts   = explode('/', $request_uri);
$slug = null;

// Escludere l'area admin dal match SEO (la SPA gestisce il suo routing)
if (isset($uri_parts[0]) && $uri_parts[0] === 'admin') {
    $slug = null;
} elseif (count($uri_parts) == 2) {
    // URL tipo /categoria/mio-slug → prende l'ultimo segmento
    $slug = end($uri_parts);
} elseif (count($uri_parts) == 1 && $uri_parts[0] !== '') {
    // URL corto tipo /mio-slug
    $slug = $uri_parts[0];
}

// 3. QUERY DATABASE (Connessione diretta, senza includere api/db.php)
$dbPath = __DIR__ . '/api/.data/database.sqlite';

if ($slug && file_exists($dbPath)) {
    try {
        $pdo = new PDO('sqlite:' . $dbPath);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        // Sanitizzazione: PHP 8.1+ ha deprecato FILTER_SANITIZE_STRING
        $cleanSlug = strip_tags(trim($slug));

        $stmt = $pdo->prepare(
            "SELECT title, excerpt, cover_image
             FROM articles
             WHERE slug = :slug AND status = 'published'
             LIMIT 1"
        );
        $stmt->execute([':slug' => $cleanSlug]);
        $article = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($article) {
            $metaTitle = htmlspecialchars($article['title'], ENT_QUOTES, 'UTF-8') . " | Nome Sito";
            $rawDesc   = $article['excerpt'] ?: "Leggi l'articolo completo.";
            $metaDescription = htmlspecialchars(strip_tags($rawDesc), ENT_QUOTES, 'UTF-8');

            if (!empty($article['cover_image'])) {
                $img = filter_var($article['cover_image'], FILTER_SANITIZE_URL);
                // Rendere il path assoluto se relativo (i bot richiedono URL assoluti)
                if (strpos($img, 'http') !== 0) {
                    $prefix    = (substr($img, 0, 1) !== '/') ? '/' : '';
                    $metaImage = $protocol . $_SERVER['HTTP_HOST'] . $prefix . $img;
                } else {
                    $metaImage = $img;
                }
            }
        }
    } catch (PDOException $e) {
        // Fallback silenzioso: proseguiamo con i meta default
        error_log("SEO Engine DB Error: " . $e->getMessage());
    }
}

// 4. LETTURA E INIEZIONE NELL'HTML DI VITE
$htmlFile = __DIR__ . '/index_react.html'; // o index.html se non rinominato

if (!file_exists($htmlFile)) {
    die("Error: Production HTML not found. Eseguire 'npm run build'.");
}

$htmlContent = file_get_contents($htmlFile);

// Costruzione del blocco SEO da iniettare
$seoInjection = "
    <title>{$metaTitle}</title>
    <meta name=\"title\" content=\"{$metaTitle}\" />
    <meta name=\"description\" content=\"{$metaDescription}\" />
    <meta property=\"og:type\" content=\"website\" />
    <meta property=\"og:url\" content=\"{$currentUrl}\" />
    <meta property=\"og:title\" content=\"{$metaTitle}\" />
    <meta property=\"og:description\" content=\"{$metaDescription}\" />
    <meta property=\"og:image\" content=\"{$metaImage}\" />
    <meta property=\"twitter:card\" content=\"summary_large_image\" />
    <meta property=\"twitter:url\" content=\"{$currentUrl}\" />
    <meta property=\"twitter:title\" content=\"{$metaTitle}\" />
    <meta property=\"twitter:description\" content=\"{$metaDescription}\" />
    <meta property=\"twitter:image\" content=\"{$metaImage}\" />
</head>";

// Operazione chirurgica: rimuove il <title> di Vite e inietta il pacchetto SEO
$htmlContent = preg_replace('/<title>.*?<\/title>/s', '', $htmlContent, 1);
$htmlContent = str_replace('</head>', $seoInjection, $htmlContent);

echo $htmlContent;
?>
```

## 4. Punti Critici del Pattern

### 4.1 Connessione Diretta al DB (No Include Esterno)
`index.php` non deve fare `require_once 'api/db.php'`. Connette direttamente tramite PDO per due motivi:
- Semplicità: evita dipendenze da path relativi che cambiano in base alla posizione del file.
- Performance: connessione read-only, niente sessioni, niente CORS headers.

### 4.2 Sanitizzazione dello Slug
L'uso di `strip_tags(trim($slug))` al posto del deprecato `FILTER_SANITIZE_STRING` garantisce:
- Compatibilità PHP 8.1+.
- Rimozione di eventuali tag HTML iniettati via URL.

### 4.3 Fallback Silenzioso
Il blocco `try-catch` intorno alla query NON mostra errori all'utente. Se il DB non è raggiungibile, serve i meta default. Questo è fondamentale: un errore del SEO Engine non deve rompere l'intera applicazione.

### 4.4 Bypass Admin
Le rotte `/admin/*` non vengono processate dal motore SEO. L'area admin non ha bisogno di Open Graph e include già il proprio ciclo di autenticazione React.

### 4.5 Immagine Assoluta
I bot di social richiedono URL assoluti per `og:image`. La logica trasforma i path relativi (come `/api/uploads/copertina.jpg`) in `https://dominio.com/api/uploads/copertina.jpg`.

## 5. Estensione a Più Entità

Il pattern si estende facilmente a più tipi di contenuto. Basta aggiungere query successive:

```php
// Prima: cercare tra gli articoli
$stmt = $pdo->prepare("SELECT title, excerpt, cover_image FROM articles WHERE slug=? AND status='published' LIMIT 1");

// Poi: se non trovato, cercare tra i progetti
if (!$article) {
    $stmt = $pdo->prepare("SELECT name as title, description as excerpt, cover_image FROM projects WHERE slug=? AND is_visible=1 LIMIT 1");
}
```

## 6. Configurazione Apache (.htaccess)

Il `.htaccess` del Modello Universale (Capitolo 2) gestisce già il routing. Apache serve `index.php` come documento predefinito se presente, prima di `index.html`. Non è necessario alcun aggiornamento delle regole RewriteRule.


## 7. Dynamic Sitemap & Robots.txt (v2.0)

L'evoluzione naturale dal prerendering statico è la generazione dinamica dei file di servizio SEO. Questo elimina la necessità di rigenerare file fisici ogni volta che un articolo viene pubblicato o modificato.

### 7.1 Mappatura via .htaccess
Invece di avere file sitemap.xml e obots.txt reali, usiamo Apache per dirottare le richieste verso script PHP:

`pache
# SEO Files — SEMPRE serviti da PHP (contenuto dinamico real-time)
RewriteRule ^sitemap\.xml$ sitemap.php [L,NC]
RewriteRule ^robots\.txt$ robots.php [L,NC]
`

### 7.2 Robots.php Dinamico
Garantisce che il link alla Sitemap punti sempre al dominio corretto, calcolato dinamicamente:

`php
header("Content-Type: text/plain; charset=utf-8");
 = (!empty(['HTTPS']) && ['HTTPS'] !== 'off') ? "https://" : "http://";
  =  . ['HTTP_HOST'];

echo "User-agent: *" . PHP_EOL;
echo "Allow: /" . PHP_EOL;
echo "Disallow: /admin/" . PHP_EOL;
echo PHP_EOL;
echo "Sitemap: /sitemap.xml" . PHP_EOL;
`

### 7.3 Sitemap.php Dinamica
Recupera categorie, sottocategorie e articoli direttamente dal database.

**Vantaggi Chiave:**
1.  **Real-time:** Un nuovo articolo appare nella sitemap istantaneamente.
2.  **Lastmod Preciso:** Il campo <lastmod> delle categorie viene calcolato in base alla data dell'ultimo articolo pubblicato in quella categoria.
3.  **Zero Manutenzione:** Non serve più uno script di prerendering o una build manuale per aggiornare la SEO.
4.  **BaseUrl Dinamico:** Lo stesso script funziona su localhost, staging e produzione senza modifiche.

\newpage

*Prossimo Capitolo: RSS Feed & Syndication - Come generare feed XML per aggregatori e podcast app.*


# CAPITOLO 12: RSS Feed & Syndication (v1.0)

Il feed RSS è il canale di distribuzione automatica dei contenuti verso aggregatori, lettori di notizie, podcast app e motori di ricerca. Tutti i siti del Modello Universale implementano almeno un feed: **SimonePizziWebSite** (`rss.php`), **SitoRuntime** (`feed_news_rss.php`), **DISINTELLIGENZA** e **FDCA** (`feed.php`). Questo capitolo consolida il pattern standard.

## 1. Struttura del Feed RSS Standard

Un feed RSS valido richiede un header HTTP preciso e una struttura XML rigorosa:

```php
<?php
require_once 'db.php';

// Header fondamentale: senza questo, i lettori RSS rifiutano il feed
header('Content-Type: application/rss+xml; charset=utf-8');

$pdo = Database::connect();

// Recupero dinamico del protocollo e del dominio
$protocol = (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on') ? 'https' : 'http';
$host     = $_SERVER['HTTP_HOST'];
$base_url = $protocol . '://' . $host;

// Forzatura del fuso orario per siti su hosting internazionali (es. Los Angeles)
date_default_timezone_set('Europe/Rome');
$now_str = date('Y-m-d H:i:s');

define('RSS_FEED_LIMIT', 50); // Numero massimo di articoli nel feed

$site_title       = "Nome del Sito";
$site_description = "Descrizione del sito per il feed RSS";

echo '<?xml version="1.0" encoding="UTF-8" ?>' . "\n";
echo '<rss version="2.0">' . "\n";
echo '<channel>' . "\n";
echo '  <title>' . htmlspecialchars($site_title) . '</title>' . "\n";
echo '  <link>' . htmlspecialchars($base_url) . '</link>' . "\n";
echo '  <description>' . htmlspecialchars($site_description) . '</description>' . "\n";
echo '  <language>it-IT</language>' . "\n";

try {
    $stmt = $pdo->prepare(
        "SELECT id, title, slug, excerpt, content, cover_image, category, published_at
         FROM articles
         WHERE status = 'published'
           AND (published_at IS NULL OR published_at = '' OR published_at <= :now)
         ORDER BY published_at DESC
         LIMIT " . RSS_FEED_LIMIT
    );
    $stmt->execute([':now' => $now_str]);
    $articles = $stmt->fetchAll();

    foreach ($articles as $article) {
        // Formato data secondo RFC 822 (obbligatorio per RSS 2.0)
        $pubDate  = date(DATE_RSS, strtotime($article['published_at'] ?? 'now'));
        $item_url = $base_url . '/' . rawurlencode($article['category']) . '/' . rawurlencode($article['slug']);
        $guid     = 'urn:tuosito:article:' . $article['id'];

        echo '  <item>' . "\n";
        echo '    <title>' . htmlspecialchars($article['title']) . '</title>' . "\n";
        echo '    <link>' . htmlspecialchars($item_url) . '</link>' . "\n";
        echo '    <description>' . htmlspecialchars($article['excerpt']) . '</description>' . "\n";
        echo '    <pubDate>' . $pubDate . '</pubDate>' . "\n";
        echo '    <guid isPermaLink="false">' . htmlspecialchars($guid) . '</guid>' . "\n";

        // Enclosure per immagine (utile per aggregatori che mostrano preview)
        if (!empty($article['cover_image'])) {
            $img_url = str_starts_with($article['cover_image'], 'http')
                ? $article['cover_image']
                : $base_url . '/' . ltrim($article['cover_image'], '/');
            echo '    <enclosure url="' . htmlspecialchars($img_url) . '" type="image/jpeg" />' . "\n";
        }

        echo '  </item>' . "\n";
    }
} catch (Exception $e) {
    // Fallback silenzioso: il feed rimane valido anche senza articoli
}

echo '</channel>' . "\n";
echo '</rss>';
```

## 2. Dettagli Tecnici Critici

### 2.1 Il Problema del Fuso Orario
Su hosting internazionali (es. server fisicamente a Los Angeles), `date()` e `strtotime()` usano il timezone del server. Un articolo programmato alle **10:00 ora italiana** risulterebbe pubblicato alle **01:00 Pacific Time**, rompendo la logica di filtro `published_at <= NOW()`.

**Soluzione**: `date_default_timezone_set('Europe/Rome')` all'inizio del file. Questa istruzione deve precedere qualsiasi uso di `date()` o `time()`. Pattern valido anche in `articles.php`, `news.php` e qualsiasi endpoint con logica temporale.

```php
// All'inizio del file, prima di qualsiasi uso di date()
date_default_timezone_set('Europe/Rome');
$ita_now_str  = date('Y-m-d H:i:s'); // Ora italiana corretta
$ita_now_time = time();               // Timestamp Unix corretto
```

### 2.2 Formato Data RFC 822
RSS 2.0 richiede date nel formato RFC 822. PHP fornisce la costante `DATE_RSS` che genera il formato corretto:
```
Mon, 24 Mar 2026 10:00:00 +0100
```
Non usare mai ISO 8601 (`Y-m-d\TH:i:s`) in un feed RSS: molti lettori lo rifiutano.

### 2.3 URL degli Articoli nel Feed
L'URL deve essere **assoluto e correttamente encodato**:
```php
$item_url = $base_url . '/' . rawurlencode($article['category']) . '/' . rawurlencode($article['slug']);
```
`rawurlencode()` gestisce spazi, accenti e caratteri speciali nei category slug. Non usare `urlencode()` (sostituisce gli spazi con `+` invece che `%20`).

### 2.4 Enclosure per Immagini
Il tag `<enclosure>` permette agli aggregatori di mostrare l'immagine di anteprima dell'articolo nel feed. Richiede URL assoluto — i path relativi (`/api/uploads/...`) non funzionano:
```php
$img_url = str_starts_with($article['cover_image'], 'http')
    ? $article['cover_image']                                   // Già assoluto
    : $base_url . '/' . ltrim($article['cover_image'], '/');    // Rendi assoluto
```

### 2.5 GUID Univoco
Il tag `<guid>` identifica univocamente ogni articolo nel feed. **Mai usare l'URL dell'articolo come GUID**. 
L'esperienza reale (Incidente Titan Desktop v1.7.3) ha dimostrato che qualora vi sia in futuro un refactoring delle URL (es. cambio struttura categorie nel CMS), i bot degli aggregatori e i bot di Telegram considereranno tutti gli articoli con nuova URL come contenuti "nuovi", ri-pubblicandoli e generando spam gravissimo.

**Soluzione Definitiva**: Usare uno standard URN crittografico, totalmente svincolato dal nome dominio o dal percorso cartelle, basato sull'ID nativo di database: 
`<guid isPermaLink="false">urn:tuosito:article:{id}</guid>`.
In questo modo anche se l'URL e le tassonomie cambiano 100 volte, il bot tratterà il contenuto come "entità già vista".

## 3. Feed RSS per Podcast (Podcast App)

SitoRuntime implementa anche un feed per podcast nel formato Apple Podcasts / Spotify. Il feed podcast ha requisiti aggiuntivi rispetto al feed news:

```php
// Namespace iTunes obbligatorio per podcast app
echo '<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">' . "\n";
echo '<channel>' . "\n";
echo '  <itunes:author>Nome Autore</itunes:author>' . "\n";
echo '  <itunes:category text="Technology" />' . "\n";

// Per ogni episodio:
echo '  <item>' . "\n";
echo '    <title>' . htmlspecialchars($ep['title']) . '</title>' . "\n";
echo '    <enclosure url="' . $audio_url . '" type="audio/mpeg" length="' . $ep['file_size'] . '" />' . "\n";
echo '    <itunes:duration>' . $ep['duration'] . '</itunes:duration>' . "\n";
echo '  </item>' . "\n";
```

## 4. Registrazione del Feed nel Routing

Il feed deve essere accessibile tramite URL dedicato. Con il `.htaccess` del Modello Universale (che reindirizza tutto a `index.php`), i file PHP fisici sono già serviti direttamente — non servono configurazioni aggiuntive per `rss.php` o `feed.php`.

**URL consigliati**:
- `/api/rss.php` — feed notizie standard
- `/api/feed.php` — alias alternativo
- `/api/feed_news_rss.php` — naming esplicito SitoRuntime

## 5. Integrazione nel Frontend (Discovery)

Il feed RSS deve essere **annunciato** nell'`<head>` HTML per permettere ai browser e ai lettori RSS di scoprirlo automaticamente. Il blocco va aggiunto all'`index.php` (SEO engine) o all'`index.html` base:

```html
<link rel="alternate" type="application/rss+xml"
      title="Nome Sito - Feed Notizie"
      href="/api/rss.php" />
```

\newpage
*Prossimo Capitolo: Newsletter & Email System - La lista email come asset posseduto, indipendente dalle piattaforme.*


# CAPITOLO 13: Newsletter & Email System (v2.0)

La newsletter è uno degli strumenti di fidelizzazione più diretti e indipendenti dalle piattaforme. Il Modello Universale implementa un sistema professionale completo basato su **SimonePizziWebSite (v1.7.4)**, con supporto a Double Opt-in, gestione template dark-mode e tracking degli invii.

## 1. Schema del Database (Evoluto)

Rispetto alla v1.0, lo schema include token di sicurezza univoci per ogni utente, necessari per la conformità GDPR e la protezione contro le iscrizioni bot.

`sql
CREATE TABLE IF NOT EXISTS subscribers (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    email             VARCHAR(255) UNIQUE NOT NULL,
    name              VARCHAR(100) NULL,
    status            ENUM('pending', 'confirmed', 'unsubscribed') DEFAULT 'pending',
    confirm_token     VARCHAR(64) NULL,
    unsubscribe_token VARCHAR(64) NOT NULL,
    confirmed_at      DATETIME NULL,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabella Storico Invii
CREATE TABLE IF NOT EXISTS newsletter_sends (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    subject         VARCHAR(255) NOT NULL,
    body            TEXT NOT NULL,
    sent_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
    recipient_count INT DEFAULT 0
);
`

## 2. Architettura Double Opt-in

Per garantire la qualità della lista e la conformità normativa, il sistema segue il flusso Double Opt-in:

1.  **Iscrizione:** L'utente inserisce l'email. Lo stato è pending. Viene generato un confirm_token.
2.  **Verifica:** Viene inviata un'email transazionale con un link di conferma unico.
3.  **Conferma:** Solo al click sul link, lo stato passa a confirmed e viene registrata la data confirmed_at.

### Generazione Token Sicuri
`php
     = bin2hex(random_bytes(32));
 = bin2hex(random_bytes(32));
`

## 3. Invio Newsletter e Composizione (v2.0)

### 3.1 Template HTML Professionale (Dark Theme)
Le newsletter moderne devono essere leggibili su client che supportano la dark mode. Il template di riferimento usa un design "Cyber-Dark" coerente con l'estetica del Modello Universale:

- **Sfondo:** #0a0a0a con container #111.
- **Tipografia:** Font di sistema puliti (Segoe UI, Arial).
- **Accent Color:** #22c55e (Verde Cyber).
- **Responsive:** Layout table-based a 600px per massima compatibilità (Outlook/Gmail).

### 3.2 Gestione Unsubscribe (GDPR)
Ogni email include un link di disiscrizione univoco in fondo. La disiscrizione è immediata (one-click) tramite l'unsubscribe_token, senza richiedere login all'utente.

`php
 = "https://tuosito.it/newsletter/disiscritto?token=" . urlencode();
`

## 4. Tracking e Storico (Admin)

L'interfaccia admin permette di:
- Visualizzare le statistiche (Totali, Confermati, In attesa, Disiscritti).
- Consultare lo storico degli invii effettuati (
ewsletter_sends).
- Approvare manualmente un iscritto se necessario (es. assistenza clienti).

## 5. Protezione Anti-Spam e Rate Limiting

- **Mailing Limit:** L'invio cicla sugli iscritti con un piccolo delay (es. usleep(100000)) per evitare di essere contrassegnati come spam dai provider.
- **Header SMTP:** Utilizzo di Reply-To reale per permettere all'utente di rispondere alla newsletter, mantenendo il From tecnico per i server di posta.

\newpage
*Prossimo Capitolo: Social Interactions & Reactions - Come gestire l'engagement anonimo e sicuro.*
\part{I Casi Reali}

# CAPITOLO 14: Database Evolution - Da SQLite a MySQL (v1.1)

Questo capitolo documenta il percorso reale di migrazione da SQLite a MySQL, focalizzandosi sulle best practice di connessione e sulla sicurezza dei dati sensibili.

## 1. Quando e Perchè Migrare

SQLite è perfetto per progetti leggeri. MySQL diventa essenziale quando:
- **Traffico crescente**: Più utenti simultanei richiedono la gestione nativa dei lock a livello di riga.
- **Accesso Remoto**: Necessità di gestire il DB tramite tool esterni (phpMyAdmin, TablePlus).
- **Scalabilità**: Necessità di separare il server web dal server database.

## 2. La Lezione del WAL Mode
In produzione (hosting Apache), il WAL mode di SQLite può causare corruzione dei dati se il file di lock non viene rilasciato correttamente. Il Modello Universale impone il `journal_mode=DELETE` come standard di massima affidabilità su hosting condiviso.

## 3. Best Practice di Connessione MySQL
La transizione a MySQL richiede una configurazione PDO rigorosa per garantire sicurezza e performance.

### 3.1 Il File dei Segreti (`db_credentials.php`)
Le credenziali **non devono mai essere committate**. Il file `db_credentials.php` deve essere escluso dal controllo di versione.
```php
<?php
// public/api/db_credentials.php
return [
    'DB_HOST'  => 'localhost',
    'DB_NAME'  => 'miocms_db',
    'DB_USER'  => 'admin',
    'DB_PASS'  => 'password_molto_sicura',
    'DB_PORT'  => 3306,
];
```

### 3.2 Configurazione PDO Avanzata
Nel file `db.php`, la connessione deve includere parametri specifici:
- **Charset `utf8mb4`**: Essenziale per il supporto completo a emoji e caratteri speciali (unicode).
- **`EMULATE_PREPARES => false`**: Forza l'uso dei prepared statements nativi di MySQL. Questo è il pilastro della **sicurezza contro le SQL Injection**, poiché la query e i dati vengono inviati separatamente al server.
- **Error Mode Exception**: Per intercettare e loggare correttamente i problemi di rete o autenticazione.

```php
self::$pdo = new PDO($dsn, $config['DB_USER'], $config['DB_PASS'], [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE  => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES    => false, // Sicurezza: Prepared statements nativi
    PDO::MYSQL_ATTR_INIT_COMMAND  => "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"
]);
```

## 4. Checklist di Migrazione

- [ ] **Backup**: Export completo del file `.sqlite`.
- [ ] **Schema**: Esecuzione di `init_mysql.php` per creare le tabelle.
- [ ] **Migrazione Dati**: Uso di `migrate_to_mysql.php` con logica `ON DUPLICATE KEY UPDATE` per l'idempotenza.
- [ ] **Sicurezza**: Verificare che `db_credentials.php` sia nel `.gitignore`.
- [ ] **Bonifica**: Eliminazione degli script di migrazione e del file `.sqlite` dal server dopo il completamento.

## 5. Evoluzione MySQL e Sicurezza
L'adozione di MySQL permette di implementare policy di backup automatici (es. cronjob con `mysqldump`) e di limitare l'accesso al database solo a specifici indirizzi IP (Whitelist), aumentando drasticamente il livello di sicurezza rispetto a un file `.sqlite` potenzialmente scaricabile se non protetto correttamente via `.htaccess`.

\newpage
*Prossimo Capitolo: Portfolio & Projects Module - Il modulo universale per portfolio e showcase.*


# CAPITOLO 15: Portfolio & Projects Module (v1.0)

Il modulo Portfolio è un'entità distinta dalla News/Article, progettata per siti di tipo personale, agenzia o showcase. Documentato da **SimonePizziWebSite**, introduce pattern specifici: visibilità granulare, ordinamento manuale, pulsanti azione multipli e gestione per categorie. È il modello di riferimento per qualsiasi sito che debba esporre un catalogo di lavori, prodotti o progetti.

## 1. La Differenza con il Modulo News/Articles

| Caratteristica | News/Articles | Projects/Portfolio |
| :--- | :--- | :--- |
| Identificatore URL | `slug` (testo parlante) | `id` (numerico) |
| Visibilità | `status` (draft/published) | `is_visible` (boolean) |
| Programmazione temporale | `published_at` | Non prevista |
| Rich Text body | Sì (HTML) | Opzionale (description breve) |
| Ordinamento | Per data (automatico) | `sort_order` (manuale) |
| CTA | — | `button_a` + `button_b` (URL esterni) |
| Categorizzazione | category + tags | Solo category |

## 2. Schema Database

```sql
CREATE TABLE IF NOT EXISTS projects (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL DEFAULT 'Nuovo Progetto',
    description  TEXT DEFAULT '',
    category     TEXT NOT NULL DEFAULT 'progetti-software',
    cover_image  TEXT DEFAULT '',
    button_a_label TEXT DEFAULT 'Scopri',
    button_a_url   TEXT DEFAULT '',
    button_b_label TEXT DEFAULT '',
    button_b_url   TEXT DEFAULT '',
    is_visible   INTEGER NOT NULL DEFAULT 1,    -- 1=visibile al pubblico, 0=nascosto
    sort_order   INTEGER NOT NULL DEFAULT 0,    -- Ordinamento manuale per categoria
    created_at   DATETIME DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_projects_category   ON projects(category);
CREATE INDEX IF NOT EXISTS idx_projects_sort_order ON projects(sort_order ASC);
```

## 3. L'API projects.php (5 Metodi HTTP)

Il modulo Projects usa **tutti e 5 i metodi HTTP**, incluso `PATCH` per aggiornamenti parziali — il pattern più pulito per operazioni di visibilità e riordinamento:

### GET — Lista con Bypass Admin
```php
$is_admin = isset($_SESSION['user_id']);
$conditions = [];
$params = [];

if (!$is_admin) {
    $conditions[] = "is_visible = 1"; // Il pubblico vede solo i visibili
}

if ($category) {
    $conditions[] = "category = ?";
    $params[] = $category;
}

// Ordinamento: per categoria poi per sort_order manuale
$query .= " ORDER BY category ASC, sort_order ASC, created_at ASC";
```

### POST — Creazione con Auto-Sort
Alla creazione, `sort_order` viene calcolato automaticamente come `MAX(sort_order) + 1` all'interno della stessa categoria. Questo garantisce che i nuovi progetti appaiano in fondo alla lista della loro categoria:
```php
$stmtMax = $pdo->prepare("SELECT COALESCE(MAX(sort_order), 0) FROM projects WHERE category = ?");
$stmtMax->execute([$category]);
$sort_order = (int)$stmtMax->fetchColumn() + 1;
```

### PATCH — Aggiornamenti Parziali
`PATCH` è il metodo corretto per aggiornamenti atomici di un singolo campo. Non invia l'intero oggetto: solo il campo che cambia.

```php
// Toggle visibilità singolo progetto
if (isset($data['is_visible'])) {
    $stmt = $pdo->prepare("UPDATE projects SET is_visible=? WHERE id=?");
    $stmt->execute([(int)$data['is_visible'], $id]);
}

// Aggiornamento ordinamento (da drag-to-sort frontend)
if (isset($data['sort_order'])) {
    $stmt = $pdo->prepare("UPDATE projects SET sort_order=? WHERE id=?");
    $stmt->execute([(int)$data['sort_order'], $id]);
}
```

**Perché PATCH e non POST?** Semantica HTTP: `POST` crea, `PUT` sostituisce l'intero oggetto, `PATCH` modifica parzialmente. Usare PATCH per toggle di visibilità e riordinamento è la scelta corretta e comunica chiaramente l'intento dell'operazione.

## 4. Il Pattern dei Pulsanti CTA (button_a / button_b)

Ogni progetto può avere fino a due pulsanti di azione che puntano a risorse esterne:
- `button_a`: Pulsante principale (es. "Scopri", "Visita il sito", "Gioca ora")
- `button_b`: Pulsante secondario opzionale (es. "GitHub", "Case Study", "App Store")

```typescript
// Frontend TypeScript: rendering condizionale dei bottoni
{project.button_a_url && (
  <a href={project.button_a_url} target="_blank" rel="noopener noreferrer"
     className="btn-primary">
    {project.button_a_label || 'Scopri'}
  </a>
)}
{project.button_b_url && (
  <a href={project.button_b_url} target="_blank" rel="noopener noreferrer"
     className="btn-secondary">
    {project.button_b_label}
  </a>
)}
```

Il `rel="noopener noreferrer"` è obbligatorio per i link `target="_blank"`: previene l'accesso alla `window.opener` della pagina madre da parte della pagina di destinazione (vulnerabilità tabnapping).

### 4.1 Switch Dinamico Web / Email
Una feature avanzata introdotta nella gestione dei CTA (SimonePizziWebSite v1.7.x) è il toggle "Tipo di Link" lato Editor. Spesso un CTA in un progetto personale non punta a un sito web, ma deve aprire il client email.
L'editor include uno switch (Web URL / Email) che, se impostato su Email, aggiunge automaticamente il prefisso protocollare `mailto:` alla stringa salvata nel DB ignorando l'`https://`, garantendo che l'autore non compia errori di distrazione fornendo una UX sicura.

## 5. Il Pattern di Slug Avanzato (Normalizzazione Accenti Italiani)

Scoperto in `articles.php` di SimonePizziWebSite, questo pattern risolve un problema reale: le parole italiane con accenti generano slug malformati.

**Problema**:
```php
// Input: "Il caffè di Genova è buono"
// Risultato naive: "il-caff-di-genova--buono"  ← accenti rimossi male
```

**Soluzione con mappa esplicita**:
```php
function generateSlug($title, $pdo) {
    // Mappa esplicita accenti italiani e francesi comuni
    $accents      = ['à','è','é','ì','ò','ù','À','È','É','Ì','Ò','Ù',
                     'â','ê','î','ô','û','ä','ë','ï','ö','ü'];
    $replacements = ['a','e','e','i','o','u','a','e','e','i','o','u',
                     'a','e','i','o','u','a','e','i','o','u'];

    $title = str_replace($accents, $replacements, $title);
    $slug  = strtolower(trim(preg_replace('/[^A-Za-z0-9-]+/', '-', $title)));

    // Anti-collisione: verifica unicità prima del salvataggio
    $stmt = $pdo->prepare("SELECT COUNT(*) FROM projects WHERE slug = ?");
    $stmt->execute([$slug]);
    if ($stmt->fetchColumn() > 0) {
        $slug .= '-' . time();
    }

    return $slug;
}
```

**Risultato**:
```
"Il caffè di Genova è buono" → "il-caffe-di-genova-e-buono"  ✓
```

Questo pattern va applicato a **tutti i moduli che generano slug** in siti con contenuto italiano.

## 6. React Frontend — Componenti Chiave

### PortfolioGrid.tsx
La griglia del portfolio filtra i progetti per categoria e li mostra in cards. Con dati provenienti dall'API, supporta:
- Filtraggio lato client per `category`
- Visualizzazione dell'immagine di copertina con lazy loading
- Rendering condizionale dei due pulsanti CTA
- Badge di categoria

### ProjectEditor.tsx (Admin)
Il form di editing del progetto nell'area admin include:
- Upload immagine via `MediaPicker` (vedi Capitolo 8)
- Due coppie `label + URL` per i pulsanti
- Toggle `is_visible` con switch UI
- Selezione categoria da dropdown

### ProjectsList.tsx (Admin)
La lista admin dei progetti espone:
- **Drag-to-sort**: invio di PATCH request ad ogni riposizionamento
- **Toggle visibilità**: PATCH istantaneo con cambio di icona (occhio aperto/chiuso)
- **Filtro per categoria**: segmentazione visiva della lista

## 7. Strategie di Categoria
Inizialmente (sino alla v1.6.0), le categorie erano progettate in modo statico: stringhe fisse definite all'interno del codice React (`PROJECT_CATEGORIES`).

Tuttavia, l'esperienza in produzione su SimonePizziWebSite ha dimostrato che un portfolio in crescita richiede flessibilità editoriale totale. Con la **v1.7.10**, l'architettura è stata migrata verso un modello nativamente **DB-driven e Dinamico**.

### Sistema Relazionale Categorie e Tag
Il database si è arricchito delle tabelle `categories` e `tags`, assieme a tabelle pivot per relazioni molti-a-molti (`article_tags`).
Il frontend non possiede più array hardcoded, ma effettua il fetching all'avvio chiamando endpoints specifici (es. `GET /api/categories.php`).

**Perché questa migrazione è stata vitale:**
1. L'amministratore può modificare, rinominare o depotenziare categorie dal volo tramite pannello admin senza richiedere una nuova "build" di Vite.
2. Introduce il supporto al **Multi-Tagging** per l'incrocio dimensionale dei contenuti.
3. Il frontend mappa in UI istantaneamente questi nuovi filtri, rendendo la navigazione della libreria estremamente flessibile.

## 8. `auth_helper.php` — Il Pattern Minimale

SimonePizziWebSite ha introdotto un pattern di autenticazione più snello rispetto agli altri siti: `auth_helper.php` è una classe `Auth` con un unico metodo statico `check()`.

```php
<?php
// auth_helper.php
require_once 'db.php';

session_start();
header('Content-Type: application/json');

class Auth {
    public static function check() {
        if (!isset($_SESSION['user_id'])) {
            http_response_code(401);
            echo json_encode(['status' => 'error', 'message' => 'Non autorizzato']);
            exit;
        }
    }
}
```

**Utilizzo in ogni endpoint protetto**:
```php
// In projects.php, articles.php, ecc.
require_once 'auth_helper.php'; // Include anche session_start() e gli header

// Nelle route protette:
Auth::check();
```

Il vantaggio rispetto al pattern `auth.php` standard: `session_start()` e gli header JSON vengono gestiti **una volta sola** nel file helper, non ripetuti in ogni endpoint. Riduce errori di "headers already sent".

\newpage
*Conclusione: Con i capitoli 14-15 il Modello Universale copre i pattern di migrazione e showcase reali emersi dai progetti di produzione.*

\newpage
*Prossimo Capitolo: Festival Logic - Iscrizioni e Workflow Approvazione - Il ciclo completo di gestione concorrenti per DISINTELLIGENZA e FDCA.*


# CAPITOLO 16: Festival Logic - Iscrizioni e Workflow Approvazione (v1.0)

Il Modello Universale include un sistema gestionale per concorsi e festival, focalizzato sull'acquisizione di talenti e la gestione del loro ciclo di vita.

## 1. Il Workflow del Partecipante
Ogni iscrizione passa attraverso una pipeline di validazione obbligatoria gestita dal backend.

### 1.1 Stati di Iscrizione
- **pending**: Stato iniziale. Il partecipante ha caricato i dati ma non è visibile sul sito.
- **approved**: Il partecipante è validato, riceve l'email di conferma e viene inserito automaticamente nella newsletter.
- **rejected**: Il partecipante viene scartato e riceve una notifica di cortesia.

## 2. Automazione Email (Transaction Emails)
Il backend deve gestire l'invio di email transazionali in tempo reale per ogni cambio di stato, utilizzando template HTML coerenti con il branding del festival.
- **Email di Ricezione**: Conferma tecnica del caricamento file.
- **Email di Esito**: Comunicazione formale (positiva o negativa).

## 3. Gestione Asset Partecipanti
I file audio o video caricati dagli utenti devono essere isolati (`api/uploads/audio/participants/`) e rinominati in modo univoco. L'admin deve poterli pre-ascoltare nel Media Center prima di procedere all'approvazione.

## 4. Newsletter Sync Strategy
Il sistema garantisce la crescita del database marketing inserendo l'indirizzo email dell'utente nella tabella `newsletter_subscribers` **solo nel momento dell'approvazione**. Questo assicura che il database contenga solo utenti reali e validati.

\newpage
*Prossimo Capitolo: Festival Logic - Votazioni e Protezione Anti-Frode.*


# CAPITOLO 17: Festival Logic - Votazioni e Protezione Anti-Frode (v1.0)

Il Modello Universale implementa un sistema di votazione pubblica robusto, progettato per prevenire manipolazioni e garantire l'equità del concorso.

## 1. La Sessione di Voto
L'utente può esprimere una o più preferenze (es. da 1 a 3) in una singola chiamata API.
- **Validazione Server-Side**: Il backend verifica che i partecipanti votati siano effettivamente approvati e nel round attivo (`in_current_round = 1`).
- **Transazione Atomica**: L'inserimento del voto e l'aggiornamento del contatore (`vote_count`) nel partecipante devono avvenire all'interno di una transazione SQL (`beginTransaction`).

## 2. Meccanismi di Protezione (Anti-Abuso)
Per impedire voti multipli dallo stesso utente o da bot:
- **Client-Side Protection**: Impostazione di un cookie (`dis_voted`) con scadenza a 30 giorni dopo il voto.
- **Server-Side Protection (IP Tracking)**: Il backend registra l'indirizzo IP del votante e impedisce nuovi voti dallo stesso IP per le successive 24 ore.
- **User Agent Check**: Ogni voto memorizza lo `User Agent` per permettere l'analisi post-voto in caso di comportamenti sospetti.

## 3. Gestione dei Round (Il "Palcoscenico" del Voto)
I partecipanti sono visibili nella pagina pubblica di voto solo se soddisfano due condizioni:
1. `status = 'approved'`
2. `in_current_round = 1`

Questo permette all'admin di attivare/disattivare interi gruppi di partecipanti (eliminatorie, semifinali, finale) semplicemente cambiando un interruttore booleano nella dashboard.

## 4. Master Switch di Votazione
La possibilità di votare è regolata da un interruttore globale (`voting_active`) nella tabella `settings`. Se disattivato, il backend deve restituire un errore `403 Forbidden` a chiunque tenti di inviare un voto.

\newpage
*Prossimo Capitolo: Festival Logic - Dashboard Admin, Settings e Reporting.*


# CAPITOLO 18: Festival Logic - Dashboard Admin, Settings e Reporting (v1.0)

Il controllo del Festival avviene tramite una dashboard centralizzata che permette all'admin di attivare/disattivare intere fasi dell'evento e monitorare i risultati.

## 1. Master Switches (Global Settings)
La tabella `settings` agisce come il "quadro elettrico" del festival:
- **`registration_active`**: Abilita/Disabilita il form di iscrizione pubblico.
- **`voting_active`**: Apre/Chiude la sessione di voto pubblico.
- **`current_round`**: Identifica la fase attuale del concorso.

## 2. Dashboard Gestionale (KPIs)
L'area admin deve mostrare indicatori chiave di prestazione (KPI) in tempo reale:
- **Totale Partecipanti**: Suddivisi per stato (Pending, Approved).
- **Voti Totali**: Volume di voti ricevuti.
- **Votanti Unici**: Stima degli utenti unici basata sull'IP e sul Cookie.

## 3. Workflow di Approvazione e Ranking
- **Approvazione**: L'admin visualizza i partecipanti in una tabella dedicata, ascolta l'audio e decide l'esito. L'approvazione è l'unica azione che scatena l'invio dell'email di conferma ufficiale.
- **Classifica (Ranking)**: Il sistema deve fornire una classifica ordinata per `vote_count`, permettendo all'admin di selezionare i finalisti da spostare nel round successivo.

## 4. Reporting Automatico
Alla chiusura della sessione di voto (quando `voting_active` viene portato a `0`), il backend può innescare l'invio di un'email di report finale allo staff:
- Riepilogo voti totali.
- Top 20 dei partecipanti più votati.
- Statistiche di partecipazione geografica (facoltativo, basato sugli IP).

\newpage
*Fine della Documentazione Avanzata del Modello Universale Festival miniCMS.*

\part{Allegati}

# BOILERPLATE CHECKLIST: Avvio Nuovo Progetto miniCMS (v2.0)

Questa checklist riassume i passi pratici per inizializzare un nuovo progetto Web (Sito o Web App) basato sugli standard definiti nel "Modello Universale miniCMS". Per i dettagli implementativi, fare riferimento ai capitoli indicati.

\newpage

## Fase 1: Setup Ambiente e Sicurezza Iniziale
- [ ] Creare la struttura base delle cartelle (`public/api/`, `src/`, `scripts/`).
- [ ] Creare il file `public/.htaccess` per il routing della SPA (React Router). *(Cap. 2)*
- [ ] Eseguire lo scaffolding del database: cartella `public/api/.data/` con `.htaccess` → `Deny from all`. *(Cap. 2)*
- [ ] Creare la cartella media (`public/api/uploads/`) e la cache (`public/api/.cache/`).
- [ ] Configurare `vite.config.ts` con il proxy corretto per evitare CORS in locale.
- [ ] Creare `.env.local` con le variabili di sviluppo (`VITE_API_URL=http://localhost/...`).
- [ ] Aggiungere `db_credentials.php` e `.env.local` al `.gitignore` (mai committare credenziali). *(Cap. 14)*

## Fase 2: Configurazione Backend Core (PHP)
- [ ] Implementare `db.php` con connessione Lazy a SQLite (`PRAGMA journal_mode=DELETE`, `busy_timeout=5000`, `PRAGMA foreign_keys=ON`). *(Cap. 3)*
- [ ] Includere Auto-Scaffolding in `db.php`: creazione cartella `.data/` e `.htaccess` se non esistono. *(Cap. 3)*
- [ ] Creare `init_db.php` per generare le tabelle e l'utente admin di default con `password_hash()`.
- [ ] Creare `auth_helper.php` o `auth.php` con classe `Auth::check()` che gestisce `session_start()` e header JSON. *(Cap. 5)*
- [ ] Configurare i cookie di sessione sicuri (`httponly`, `samesite=Lax`, `secure` se HTTPS). *(Cap. 10)*
- [ ] Applicare `date_default_timezone_set('Europe/Rome')` in tutti gli endpoint con logica temporale. *(Cap. 5, 12)*
- [ ] Nascondere gli errori in produzione (`display_errors = 0` o `try-catch` globale). *(Cap. 10)*

## Fase 3: Configurazione Frontend Core (React)
- [ ] Implementare `src/api.ts` con il pattern "Double Read" per intercettare gli errori del server. *(Cap. 6)*
- [ ] Configurare `AdminLayout.tsx` con logica di auth check e "Hard Logout" (`window.location.reload()`). *(Cap. 10)*
- [ ] Abilitare il "Role-Based UI" per mostrare solo le voci consentite al ruolo connesso (Admin vs Editor). *(Cap. 10)*
- [ ] Usare `key={item.id}` nel componente editor per forzare il reset del rich text editor al cambio articolo. *(Cap. 9)*

## Fase 4: Integrazione Media e Contenuti
- [ ] Implementare `upload.php` con ridimensionamento automatico GD e sanitizzazione nomi (`uniqid()`). *(Cap. 5)*
- [ ] Inserire il componente `MediaPicker` per il caricamento diretto di audio e immagini. *(Cap. 8)*
- [ ] Usare l'editor "Clean-HTML" con gestione sicura dell'evento "Paste". *(Cap. 8)*
- [ ] Implementare la logica slug con normalizzazione accenti italiani se il contenuto è in italiano. *(Cap. 5)*

## Fase 5: SEO e Syndication
- [ ] Creare `public/index.php` come SEO Engine: query DB → iniezione meta tag nell'HTML di Vite. *(Cap. 11)*
- [ ] Aggiungere il rinomina di `index.html` → `index_react.html` nel build script se index.php è in public/. *(Cap. 2, 11)*
- [ ] Creare `api/rss.php` con feed RSS 2.0 valido (header corretto, date RFC 822, URL assoluti). *(Cap. 12)*
- [ ] Aggiungere tag `<link rel="alternate" type="application/rss+xml">` nell'`<head>` HTML. *(Cap. 12)*

## Fase 6: Ottimizzazione e Deploy
- [ ] Configurare la "Programmazione Reale" tramite query SQL su `published_at`. *(Cap. 9)*
- [ ] Configurare la Cache JSON con TTL 300s per query di listing pesanti. *(Cap. 7)*
- [ ] Impostare `clean-dist.js` nel processo di build per rimuovere i file `.sqlite` dalla cartella `dist/`. *(Cap. 2)*
- [ ] Configurare header `Cache-Control: max-age=31536000` per i file in `uploads/` via `.htaccess`. *(Cap. 7)*

## Fase 7: Specifico per Tipologia di Sito

### Per Siti con Newsletter (SitoRuntime pattern)
- [ ] Creare tabella `subscribers` con `email UNIQUE`, `is_active`, `created_at`. *(Cap. 13)*
- [ ] Implementare `newsletter.php` con gate admin + azioni pubbliche (subscribe, unsubscribe). *(Cap. 13)*
- [ ] Usare il pattern `{EMAIL_PLACEHOLDER}` per il link di disiscrizione personalizzato. *(Cap. 13)*
- [ ] Abilitare rate limiting con `usleep(500000)` ogni 10 email nel ciclo di invio. *(Cap. 13)*

### Per Portfolio/Sito Personale (SimonePizziWebSite pattern)
- [ ] Aggiungere tabella `projects` con `sort_order`, `is_visible`, `button_a`, `button_b`. *(Cap. 15)*
- [ ] Implementare `projects.php` con i 5 metodi HTTP incluso PATCH per toggle visibilità e riordinamento. *(Cap. 15)*
- [ ] Creare componenti `PortfolioGrid.tsx`, `ProjectEditor.tsx`, `ProjectsList.tsx`. *(Cap. 15)*

### Per Festival/Concorso (FDCA / DISINTELLIGENZA pattern)
- [ ] Aggiungere tabelle `participants`, `votes`, `settings` con master switch `registration_active` e `voting_active`. *(Cap. 16, 17)*
- [ ] Implementare `participants.php` con workflow pending → approved/rejected. *(Cap. 16)*
- [ ] Implementare `votes.php` con protezione IP + cookie anti-frode. *(Cap. 17)*

### Per Migrazione SQLite → MySQL (SitoRuntime pattern)
- [ ] Creare `db_credentials.php` separato (aggiungere al `.gitignore`). *(Cap. 14)*
- [ ] Aggiornare `db.php` con connessione PDO MySQL (`utf8mb4`, `EMULATE_PREPARES=false`). *(Cap. 14)*
- [ ] Eseguire `init_mysql.php` per creare lo schema MySQL sul server. *(Cap. 14)*
- [ ] Eseguire `migrate_to_mysql.php` per trasloco dati (ONE-SHOT, eliminare dopo). *(Cap. 14)*

\newpage
*Questa checklist è generata basandosi sui capitoli del Modello Universale miniCMS v2.0. Per i dettagli implementativi fare riferimento ai file `.md` corrispondenti.*


# CAPITOLO 19: Social Interactions & Reactions (v1.0)

L'engagement degli utenti è fondamentale per un blog moderno. Il Modello Universale integra un sistema di **Reazioni Social** anonime, sicure e totalmente GDPR-compliant, ispirato alla logica di **SimonePizziWebSite (v2.0)**.

## 1. Filosofia del Modulo
A differenza dei commenti, che richiedono moderazione e gestione di dati personali (email, nomi), le reazioni permettono un'interazione istantanea senza frizioni.

- **Anonimato:** L'utente non deve registrarsi.
- **Sicurezza:** Protezione contro il voto multiplo (Spam) tramite hashing dell'identità.
- **Leggerezza:** Icone SVG native cross-platform (Emoji style).

## 2. Il Sistema delle 5 Reazioni
Il set standard include 5 tipi di feedback emotivo:
1.  **Thumb** (Apprezzamento standard)
2.  **Heart** (Amore/Passione)
3.  **Fire** (Contenuto "caldo" o di tendenza)
4.  **Think** (Contenuto riflessivo o complesso)
5.  **Game** (Contenuto ludico o interattivo)

## 3. Sicurezza e GDPR: Il Voter Hash
Per impedire a un utente di cliccare 100 volte la stessa reazione senza memorizzare il suo indirizzo IP (dato personale sensibile), usiamo un **Hash SHA256** salato e anonimo.

`php
// Hash anonimo del visitatore
 = hash('sha256',
    (['REMOTE_ADDR'] ?? 'unknown') .
    (['HTTP_USER_AGENT'] ?? 'unknown')
);
`
Questo hash identifica univocamente la "sessione/dispositivo" ma non permette di risalire all'IP originale, garantendo la conformità GDPR.

## 4. Rate Limiting (Protezione Anti-Frode)
Oltre alla chiave univoca sul database, il sistema implementa un limite temporale per IP: **max 20 azioni al minuto**. Questo blocca script automatizzati che tenterebbero di falsare le statistiche di engagement.

## 5. Schema Database (MySQL)

`sql
CREATE TABLE IF NOT EXISTS article_reactions (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    article_id  INT NOT NULL,
    reaction    VARCHAR(20) NOT NULL,
    voter_hash  VARCHAR(64) NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY (article_id, voter_hash, reaction) -- Impedisce voti doppi
);
`

## 6. Logica API (Toggle Pattern)
L'endpoint eactions.php non si limita ad aggiungere voti, ma implementa la logica **Toggle**:
- Se l'utente clicca su una reazione che ha già dato, questa viene **rimossa**.
- Se clicca su una nuova, viene **aggiunta**.

Questo permette un'esperienza fluida simile ai "Like" dei social media moderni (Instagram/Facebook).

\newpage
*Prossimo Capitolo: [Capitolo successivo previsto in roadmap]*
