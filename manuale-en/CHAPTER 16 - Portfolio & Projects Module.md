# CHAPTER 16: Portfolio & Projects Module

The Portfolio module is an entity distinct from News/Article, meant for a personal site, an agency, a showcase. Mapped onto **SimonePizziWebSite**, it brings patterns of its own: granular visibility, manual ordering, multiple action buttons, category-based management. It’s the reference for any site that has to display a catalog of works, products, or projects.

## 1. The Difference from the News/Articles Module

| Feature | News/Articles | Projects/Portfolio |
| :--- | :--- | :--- |
| URL identifier | `slug` (human-readable text) | `id` (numeric) |
| Visibility | `status` (draft/published) | `is_visible` (boolean) |
| Time scheduling | `published_at` | not provided |
| Rich-text body | yes (HTML) | optional (short description) |
| Ordering | by date (automatic) | `sort_order` (manual) |
| CTA | none | `button_a` + `button_b` (external URLs) |
| Categorization | category + tag | category only |

The row on the identifier matters more than it seems: articles live on human-readable URLs (`slug`), projects on a numeric `id`. Projects, then, generate no slug, and the advanced slug logic (with its map of Italian accents) lives only once, in Chapter 5, where the articles need it.

## 2. Database Schema

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
    is_visible   INTEGER NOT NULL DEFAULT 1,    -- 1=visible to the public, 0=hidden
    sort_order   INTEGER NOT NULL DEFAULT 0,    -- manual ordering within a category
    created_at   DATETIME DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_projects_category   ON projects(category);
CREATE INDEX IF NOT EXISTS idx_projects_sort_order ON projects(sort_order ASC);
```

> [!NOTE]
> **A note on dialect.** The schema above is in the SQLite dialect, the book’s base language (Chapter 3). SimonePizziWebSite today runs on MySQL (Chapter 15), and there the same constructs change shape: `INTEGER PRIMARY KEY AUTOINCREMENT` becomes `INT AUTO_INCREMENT PRIMARY KEY`, `DEFAULT (datetime('now'))` becomes `DEFAULT CURRENT_TIMESTAMP`, and the `INTEGER` boolean becomes `TINYINT(1)`, exactly as in the reactions schema in Chapter 20. Translated badly, `datetime('now')` doesn’t run at all on MySQL: it’s one of the fossils Chapter 15 collects.

## 3. The `projects.php` API: All Five Verbs

The module uses the full range of HTTP methods, and `PATCH` is what sets it apart: it’s the right verb for the visibility and reordering operations, which change a single field.

**GET: list with admin bypass.** The public sees only the visible ones; the admin sees everything. Same pattern as Chapter 9, here on `is_visible` instead of `status`.

```php
$is_admin = isset($_SESSION['user_id']);
if (!$is_admin) $conditions[] = "is_visible = 1";          // the public sees only the visible ones
if ($category)  { $conditions[] = "category = ?"; $params[] = $category; }
$query .= " ORDER BY category ASC, sort_order ASC, created_at ASC";
```

**POST: creation with auto-sort.** On creation, `sort_order` becomes `MAX(sort_order) + 1` within the same category, so the new project shows up at the bottom of its list.

```php
$stmtMax = $pdo->prepare("SELECT COALESCE(MAX(sort_order), 0) FROM projects WHERE category = ?");
$stmtMax->execute([$category]);
$sort_order = (int)$stmtMax->fetchColumn() + 1;
```

**PATCH: partial updates.** It doesn’t send the whole object, only the field that changes: the visibility toggle, or the new `sort_order` arriving from the frontend’s drag-to-sort.

```php
if (isset($data['is_visible'])) {
    $pdo->prepare("UPDATE projects SET is_visible=? WHERE id=?")->execute([(int)$data['is_visible'], $id]);
}
if (isset($data['sort_order'])) {
    $pdo->prepare("UPDATE projects SET sort_order=? WHERE id=?")->execute([(int)$data['sort_order'], $id]);
}
```

The HTTP semantics are clear: `POST` creates, `PUT` replaces the whole object, `PATCH` modifies a piece. Using `PATCH` for the toggle and the reordering communicates intent better than a generic `POST` would.

## 4. The CTA Buttons (`button_a` / `button_b`)

Each project can have up to two buttons pointing to external resources: one primary, whose default label is “Scopri” (Discover) but which an author can rename to “Visit the Site” or “Play Now,” and one optional secondary (“GitHub,” “Case Study,” “App Store”).

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

The `rel="noopener noreferrer"` on `target="_blank"` links is mandatory: it stops the destination page from reaching the `window.opener` of the originating one (tabnapping).

### 4.1 The Web / Email Switch

A refinement introduced in the CTA handling (SimonePizziWebSite v1.7.x) is a “link type” toggle in the editor: a button often doesn’t point to a website but has to open the mail client. If the author picks “Email,” the editor prepends `mailto:` to the saved string on its own, ignoring the `https://`. It’s a small, distraction-proof piece of UX: the content editor doesn’t have to remember the right protocol.

## 5. Unified Search: One Endpoint for Articles and Projects

Articles and projects are different entities, but to someone searching the site they’re the same thing: content. SimonePizziWebSite recognizes this with a single search endpoint, `search.php`, which queries both tables with a `LIKE` and tags every result with a `type` field so the frontend knows how to render it.

```php
// SPW search.php — one query per family, results merged and tagged with `type`
$like = '%' . $q . '%';
$articles = $pdo->prepare("SELECT id, title AS name, slug, 'article' AS type FROM articles
                           WHERE status='published' AND (title LIKE ? OR content LIKE ?)");
$projects = $pdo->prepare("SELECT id, name, NULL AS slug, 'project' AS type FROM projects
                           WHERE is_visible=1 AND (name LIKE ? OR description LIKE ?)");
// ...both run, the results are concatenated, and the client sorts by `type`
```

It’s a search that’s honest about its limits: `LIKE '%q%'`, not a full-text engine. For a portfolio or a personal blog it’s more than enough, and the `type` field saves you from building two separate searches in the frontend. This endpoint lives halfway between the content lifecycle (Chapter 9) and this module: it’s the point where the two entities go back to speaking the same language.

## 6. React Frontend: The Key Components

- **`PortfolioGrid.tsx`**: the public grid, which filters by category on the client, shows the cover images with lazy loading, renders the two CTAs conditionally, and the category badges.
- **`ProjectEditor.tsx`** (admin): image upload via `MediaPicker` (Chapter 8), the two label+URL button pairs, the `is_visible` toggle, the category from a dropdown.
- **`ProjectsList.tsx`** (admin): drag-to-sort that sends a `PATCH` on every repositioning, a visibility toggle with an instant `PATCH` (the open/closed eye icon), a category filter.

## 7. Category Strategies: From Static to DB-Driven

Up to v1.6, the categories were fixed strings in the React code (`PROJECT_CATEGORIES`). A growing portfolio needs more freedom, and from v1.7.10 the categories become DB-driven: a `categories` table the frontend queries on startup (`GET /api/categories.php`), so the admin can rename them or add new ones from the panel without a fresh Vite build.

Many-to-many multi-tagging, on the other hand, stays a feature of the **articles**, not the projects (which have a single `category`): its treatment, with the dual track toward the legacy CSV field, is in Chapter 9. Here the lesson on availability is enough: moving the categories out of the code and into the database makes them editable on the fly, and for an editorial catalog that’s what counts.

> [!NOTE]
> **The `auth_helper.php` pattern**
> Like every protected endpoint, `projects.php` too leans on the `auth_helper.php` that wraps `session_start()`, the JSON headers, and the `Auth` class (the detail is in Chapter 5). Concentrating those calls in a single include, instead of repeating them in every file, cuts down on “headers already sent” errors.

> [!IMPORTANT]
> **The Canon**
> - A `projects` table with `sort_order`, `is_visible`, and the CTA fields; an endpoint with `PATCH` for the visibility toggle and reordering.
> - Project URLs on a numeric id, not a slug; a single category (M:N multi-tagging belongs to the articles, Chapter 9).
> - Unified search with a `type` field that sorts the results on the client.

---
*Next Chapter: Festival Logic — Submissions and the Approval Workflow. The competitor-management cycle for DISINTELLIGENZA and FDCA.*
