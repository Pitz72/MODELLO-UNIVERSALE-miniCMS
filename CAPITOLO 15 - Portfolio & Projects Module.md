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

---
*Conclusione: Con i capitoli 14-15 il Modello Universale copre i pattern di migrazione e showcase reali emersi dai progetti di produzione.*

---
*Prossimo Capitolo: Festival Logic - Iscrizioni e Workflow Approvazione - Il ciclo completo di gestione concorrenti per DISINTELLIGENZA e FDCA.*
