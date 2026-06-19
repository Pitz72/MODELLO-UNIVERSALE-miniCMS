# CAPITOLO 16: Portfolio & Projects Module

Il modulo Portfolio è un'entità distinta da News/Article, pensata per un sito personale, un'agenzia, uno showcase. Mappato su **SimonePizziWebSite**, porta pattern propri: visibilità granulare, ordinamento manuale, pulsanti d'azione multipli, gestione per categorie. È il riferimento per qualunque sito che debba esporre un catalogo di lavori, prodotti o progetti.

## 1. La Differenza con il Modulo News/Articles

| Caratteristica | News/Articles | Projects/Portfolio |
| :--- | :--- | :--- |
| Identificatore URL | `slug` (testo parlante) | `id` (numerico) |
| Visibilità | `status` (draft/published) | `is_visible` (boolean) |
| Programmazione temporale | `published_at` | non prevista |
| Rich text body | sì (HTML) | opzionale (description breve) |
| Ordinamento | per data (automatico) | `sort_order` (manuale) |
| CTA | nessuna | `button_a` + `button_b` (URL esterni) |
| Categorizzazione | category + tag | solo category |

La riga sull'identificatore conta più di quanto sembri: gli articoli vivono su URL parlanti (`slug`), i progetti su un `id` numerico. I progetti, quindi, non generano slug, e la logica di slug avanzata (con la mappa degli accenti italiani) vive una volta sola al Capitolo 5, dove serve agli articoli.

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
    sort_order   INTEGER NOT NULL DEFAULT 0,    -- ordinamento manuale per categoria
    created_at   DATETIME DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_projects_category   ON projects(category);
CREATE INDEX IF NOT EXISTS idx_projects_sort_order ON projects(sort_order ASC);
```

## 3. L'API `projects.php`: tutti e cinque i verbi

Il modulo usa l'intera gamma dei metodi HTTP, e `PATCH` è quello che lo distingue: è il verbo giusto per le operazioni di visibilità e riordino, che cambiano un solo campo.

**GET: lista con bypass admin.** Il pubblico vede solo i visibili; l'admin vede tutto. Stesso pattern del Capitolo 9, qui su `is_visible` invece che su `status`.

```php
$is_admin = isset($_SESSION['user_id']);
if (!$is_admin) $conditions[] = "is_visible = 1";          // il pubblico vede solo i visibili
if ($category)  { $conditions[] = "category = ?"; $params[] = $category; }
$query .= " ORDER BY category ASC, sort_order ASC, created_at ASC";
```

**POST: creazione con auto-sort.** Alla creazione, `sort_order` diventa `MAX(sort_order) + 1` nella stessa categoria, così il nuovo progetto compare in fondo alla sua lista.

```php
$stmtMax = $pdo->prepare("SELECT COALESCE(MAX(sort_order), 0) FROM projects WHERE category = ?");
$stmtMax->execute([$category]);
$sort_order = (int)$stmtMax->fetchColumn() + 1;
```

**PATCH: aggiornamenti parziali.** Non invia l'intero oggetto, solo il campo che cambia: il toggle di visibilità, o il nuovo `sort_order` arrivato dal drag-to-sort del frontend.

```php
if (isset($data['is_visible'])) {
    $pdo->prepare("UPDATE projects SET is_visible=? WHERE id=?")->execute([(int)$data['is_visible'], $id]);
}
if (isset($data['sort_order'])) {
    $pdo->prepare("UPDATE projects SET sort_order=? WHERE id=?")->execute([(int)$data['sort_order'], $id]);
}
```

La semantica HTTP è chiara: `POST` crea, `PUT` sostituisce l'intero oggetto, `PATCH` modifica un pezzo. Usare `PATCH` per il toggle e il riordino comunica l'intento meglio di un `POST` generico.

## 4. I Pulsanti CTA (`button_a` / `button_b`)

Ogni progetto può avere fino a due pulsanti verso risorse esterne: uno principale («Scopri», «Visita il sito», «Gioca ora») e uno secondario opzionale («GitHub», «Case Study», «App Store»).

```typescript
{project.button_a_url && (
  <a href={project.button_a_url} target="_blank" rel="noopener noreferrer" className="btn-primary">
    {project.button_a_label || 'Scopri'}
  </a>
)}
{project.button_b_url && (
  <a href={project.button_b_url} target="_blank" rel="noopener noreferrer" className="btn-secondary">
    {project.button_b_label}
  </a>
)}
```

Il `rel="noopener noreferrer"` sui link `target="_blank"` è obbligatorio: impedisce alla pagina di destinazione di accedere alla `window.opener` di quella di partenza (il tabnapping).

### 4.1 Lo switch Web / Email

Una rifinitura introdotta nella gestione dei CTA (SimonePizziWebSite v1.7.x) è un toggle «tipo di link» nell'editor: spesso un pulsante non punta a un sito ma deve aprire il client di posta. Se l'autore sceglie «Email», l'editor antepone da solo `mailto:` alla stringa salvata, ignorando l'`https://`. È una piccola UX a prova di distrazione: il redattore non deve ricordarsi il protocollo giusto.

## 5. Ricerca Unificata: un Solo Endpoint per Articoli e Progetti

Articoli e progetti sono entità diverse, ma per chi cerca sul sito sono la stessa cosa: contenuti. SimonePizziWebSite lo riconosce con un endpoint di ricerca unico, `search.php`, che interroga entrambe le tabelle con un `LIKE` e marca ogni risultato con un campo `type` perché il frontend sappia come renderlo.

```php
// SPW search.php — una query per famiglia, risultati uniti e marcati con `type`
$like = '%' . $q . '%';
$articles = $pdo->prepare("SELECT id, title AS name, slug, 'article' AS type FROM articles
                           WHERE status='published' AND (title LIKE ? OR content LIKE ?)");
$projects = $pdo->prepare("SELECT id, name, NULL AS slug, 'project' AS type FROM projects
                           WHERE is_visible=1 AND (name LIKE ? OR description LIKE ?)");
// ...si eseguono entrambe, si concatenano i risultati, il client smista per `type`
```

È una ricerca onesta nei suoi limiti: `LIKE '%q%'`, non un motore full-text. Per un portfolio o un blog personale è più che sufficiente, e il campo `type` evita di costruire due ricerche separate nel frontend. Questo endpoint vive a metà strada tra il ciclo di vita dei contenuti (Capitolo 9) e questo modulo: è il punto in cui le due entità tornano a parlare la stessa lingua.

## 6. Frontend React: i Componenti Chiave

- **`PortfolioGrid.tsx`**: la griglia pubblica, che filtra per categoria lato client, mostra le copertine con lazy loading, rende i due CTA in modo condizionale e i badge di categoria.
- **`ProjectEditor.tsx`** (admin): upload immagine via `MediaPicker` (Capitolo 8), le due coppie label+URL dei pulsanti, il toggle `is_visible`, la categoria da dropdown.
- **`ProjectsList.tsx`** (admin): drag-to-sort che invia un `PATCH` a ogni riposizionamento, toggle di visibilità con `PATCH` istantaneo (l'icona occhio aperto/chiuso), filtro per categoria.

## 7. Strategie di Categoria: da Statiche a DB-driven

Fino alla v1.6, le categorie erano stringhe fisse nel codice React (`PROJECT_CATEGORIES`). Un portfolio che cresce ha bisogno di più libertà, e dalla v1.7.10 le categorie diventano DB-driven: una tabella `categories` interrogata dal frontend all'avvio (`GET /api/categories.php`), così l'admin può rinominarle o aggiungerne dal pannello senza una nuova build di Vite.

Il multi-tagging molti-a-molti, invece, resta una feature degli **articoli**, non dei progetti (che hanno una sola `category`): la sua trattazione, con il doppio binario verso il campo CSV legacy, è al Capitolo 9. Qui basta la lezione di disponibilità: spostare le categorie dal codice al database le rende modificabili a caldo, e questo per un catalogo editoriale è ciò che conta.

> [!NOTE]
> **Il pattern `auth_helper.php`**
> Anche `projects.php`, come ogni endpoint protetto, si appoggia all'`auth_helper.php` che incapsula `session_start()`, gli header JSON e la classe `Auth` (il dettaglio è al Capitolo 5). Concentrare quelle chiamate in un solo include, invece di ripeterle in ogni file, riduce gli errori da «headers already sent».

> [!IMPORTANT]
> **Il Canone**
> - Tabella `projects` con `sort_order`, `is_visible` e i campi CTA; endpoint con `PATCH` per toggle di visibilità e riordino.
> - URL dei progetti su id numerico, non slug; categoria singola (il multi-tag M:N è degli articoli, Capitolo 9).
> - Ricerca unificata con un campo `type` che smista i risultati lato client.

---
*Prossimo Capitolo: Festival Logic, Iscrizioni e Workflow di Approvazione. Il ciclo di gestione dei concorrenti per DISINTELLIGENZA e FDCA.*
