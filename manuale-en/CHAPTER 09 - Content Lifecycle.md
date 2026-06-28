# CHAPTER 9: Content Lifecycle

This chapter turns a database into an editorial system: how a piece of content is born as a draft, gets scheduled, goes public, and how the API that serves it decides shape, count, and visibility. It’s also the chapter that closes a thread opened in Chapter 6: the payload contract the client reads defensively is born here, on the server side.

## 1. Dynamic States vs. Persistent States

The database stores a fixed state (`status`), but the application computes a dynamic one that depends on time. The clean matrix is this:

| `status` (DB) | `published_at` | Real state (UI) | Description |
| :--- | :--- | :--- | :--- |
| `draft` | any | **draft** | never visible to the public |
| `published` | in the future | **scheduled** | visible to admins only, waiting |
| `published` | in the past | **published** | visible to everyone |

This is the matrix of **SimonePizziWebSite**, and it’s the tidiest one. The other two sites carry the scars of their migrations: **SitoRuntime** filters the public list with `status = 'published' OR status IS NULL`, where the `IS NULL` is the residue of the `status` column having been added outside the base schema; **DISINTELLIGENZA** still queries `status = 'scheduled'`, a state a migration declared obsolete but that the code keeps looking for. The tidy matrix is a destination, not the natural state of things (Chapter 15).

## 2. Scheduling without Cron: the Three Strategies of the Present

The idea is elegant and shared: no scheduled job. An article with `published_at` in the future is “published but not yet visible,” and it shows up on its own when the visibility query finds `published_at <= now`. On the React side, the dashboard computes the same state on the fly to give the admin immediate feedback:

```typescript
const isDraft     = item.status === 'draft';
const isScheduled = item.status === 'published' && new Date(item.published_at) > new Date();
const isPublished = item.status === 'published' && new Date(item.published_at) <= new Date();
```

The delicate part is what “now” means. There’s no single right answer: the three sites compute it in three ways, and each has its own way of getting it wrong.

- **SimonePizziWebSite** forces `date_default_timezone_set('Europe/Rome')` and compares in PHP. Correct, but only as long as the timezone is forced in *every* endpoint (Chapter 5).
- **SitoRuntime** compares `date('Y-m-d H:i:s')` strings with a space separator. The query is right, but if the client sends a date in ISO format with the `T`, the string comparison breaks: it’s the incident documented in `debug_time.php`.
- **DISINTELLIGENZA** delegates to SQLite’s `CURRENT_TIMESTAMP`, which is in **UTC**, while `published_at` is stored in the server’s timezone. An article appears or disappears off by an hour or two.

> [!WARNING]
> **Who computes the present: PHP or the database?**
> Converting `datetime-local` (the browser’s `T`) to the DB format (the space) isn’t “the standard”: it’s the sore point for anyone who compares dates as strings, namely SitoRuntime. The other two strategies avoid that problem but introduce others (the timezone to force everywhere in SPW, the UTC offset in DIS). The practical rule: pick a single source of the present and use it consistently. If you compare in PHP, force the timezone in the shared prelude; if you compare in the database, make sure `published_at` and `NOW`/`CURRENT_TIMESTAMP` live in the same timezone. Mixing them is the recipe for a post that shows up an hour ahead of schedule.

```typescript
// the T <-> space conversion is SitoRuntime's, not a universal rule
value={published_at.replace(' ', 'T').slice(0, 16)}              // DB -> UI
onChange={e => setPublishedAt(e.target.value.replace('T', ' ') + ':00')}   // UI -> DB
```

## 3. The Response Contract: Where the Double Read Closes

In Chapter 6 the client read the payload defensively, because the shape of the responses isn’t uniform. The why is here, on the server side: the contract was never versioned, it was **extended whenever needed** (adding pagination, a `success` wrapper), and so the envelope differs by endpoint and by site.

- **SimonePizziWebSite**: *only* the article list returns `{ data, total, page, limit }`; everything else (projects, categories, tags) is a bare array. The client does the “Double Read” not because an endpoint changes shape, but because it mixes the two families in its loaders.
- **SitoRuntime**: three different envelopes, `{ success, data, meta }` for news, `{ success, articles, total }` for the admin, a bare array for speakers and podcasts. A per-endpoint mosaic.
- **DISINTELLIGENZA**: always a bare array or object, the “zero envelope.”

The pagination count lives in different places too. SPW returns the raw `total` and leaves the `hasMore` calculation to the client (with a separate `COUNT(*)` over the same conditions and, a mandatory MySQL detail, the `LIMIT/OFFSET` bound with `PARAM_INT`, otherwise PDO treats them as strings and the query fails). SitoRuntime pre-computes `total_pages` on the server and puts it in `meta`, so the client’s load-more is trivial. DISINTELLIGENZA gives no metadata at all: the client asks for the next page blind, until it comes back empty.

> [!NOTE]
> **Extending a contract instead of versioning it: what it costs**
> Adding `{ data, total }` to an endpoint that used to return a bare array is the quickest thing in the world, and it doesn’t break anything right away. The cost comes later, and the client pays it: it has to guess which shape it will receive, and when it guesses wrong (a bare array read as if it carried the count) you get the broken `hasMore` from Chapter 6. Versioning an API costs discipline; extending it in place costs widespread fragility. For a small CMS the second is a legitimate choice, but it should be made knowing that the price moves to the frontend.

## 4. The Content Cache without Redis

SitoRuntime is the only one of the three to add a read cache, and it does it in the most thin-stack way possible: a JSON file on disk, no Redis, no Memcached. The news list is served from a file in `.cache/`, regenerated only when it’s older than the TTL.

```php
// SR news.php — file cache with a TTL and a diagnostic header
$cacheFile = __DIR__ . "/.cache/news_p{$page}_l{$limit}.json";
if (file_exists($cacheFile) && (time() - filemtime($cacheFile) < 300)) {  // TTL 300s
    header('X-Cache: HIT');
    echo file_get_contents($cacheFile);
    exit;
}
// ...otherwise query the DB, save the JSON, and:
header('X-Cache: MISS');
```

Two details keep it sound. Invalidation is explicit: on every `save` or `delete` the `.cache/` folder is wiped, so the public never sees stale data after a change. And the `X-Cache: HIT/MISS` header makes it possible to check from the outside whether the cache is doing its job. It’s the same mechanism that, applied to SEO, becomes the anti-bot shield of Chapter 11; here it just keeps the database from being queried on every visit to the same list page.

## 5. Taxonomies: Categories and Tags (and When You Don’t Need Them)

Here the Model shows its scale again, and a common assumption needs correcting: relational multi-tagging isn’t everyone’s standard, it’s the choice of **one** site when it’s genuinely needed.

**SimonePizziWebSite** is the full taxonomic blog: hierarchical categories with `parent_id` (a container category filters its subcategories too, via `IN`), and tags in a many-to-many relation on `article_tags`. But this isn’t an “exclusive switch” to the relational model: the function that saves the tags also writes, **in parallel**, the old CSV field `articles.tags`, kept as a backward-compatibility cache. It’s the coexistence of the old model and the new one during a migration that was never closed, not a clean cut.

```php
// SPW — double write: new M:N relation + legacy CSV field in parallel
syncArticleTags($pdo, $articleId, $tagIds);                 // article_tags table (new)
$pdo->prepare("UPDATE articles SET tags = ? WHERE id = ?")  // CSV field (legacy, backward-compat cache)
    ->execute([implode(',', $tagNames), $articleId]);
```

**SitoRuntime** and **DISINTELLIGENZA** have no relational tags at all: the `category` is a free string (in DIS with a default of `'generale'`), and the “tags,” where they exist, are a `TEXT` or `JSON` field. For a site that isn’t a taxonomic archive, a categories table is weight you don’t need: a string is enough.

> [!TIP]
> **When You Don’t Need a Categories Table**
> The `parent_id` hierarchy with M:N tags is right for a blog with hundreds of articles to filter by topic. For a radio with a few fixed categories, or a festival, a free string does the same job without joins, without a relation table, without a taxonomy editor. Adding relational taxonomy “because it’s more correct” is the kind of complexity the Model invites you to defer until the content asks for it.

## 6. Public vs. Admin: the Bypass and the Deliberate 404

The same resource serves two audiences, and the difference is a visibility condition added only for whoever isn’t logged in. SimonePizziWebSite does it with a conditional `AND` in the same endpoint; SitoRuntime with two queries in two different files (reading in `news.php`, management in `admin.php`); DISINTELLIGENZA with an `if (!$isAdmin)` that adds the `WHERE`. Same idea, three structures.

On a single unpublished article, though, there’s a security detail worth a rule of its own: you respond **404, not 403**.

```php
// SPW articles.php?slug=... — the deliberate 404: don't confirm a draft exists
$article = $stmt->fetch();
if ($article) {
    $is_admin     = isset($_SESSION['user_id']);
    $is_published = $article['status'] === 'published' &&
                    (empty($article['published_at']) || strtotime($article['published_at']) <= $ita_now_time);
    if (!$is_admin && !$is_published) {
        http_response_code(404);                       // not 403: a 403 would confirm the draft exists
        echo json_encode(['error' => 'Articolo non trovato']);
        exit;
    }
    echo json_encode($article);                        // the admin sees everything
}
```

For the dashboard list, which has to show drafts too, you need a double check: the session **and** an explicit parameter.

```php
// the ?admin=true parameter alone would be bypassable: always tie it to the session
$is_admin_dashboard = isset($_SESSION['user_id']) && ($_GET['admin'] ?? '') === 'true';
if (!$is_admin_dashboard) {
    $conditions[] = "status = 'published'";
    $conditions[] = "(published_at IS NULL OR published_at = '' OR published_at <= ?)";
    $params[]     = $ita_now_str;
}
```

The fetch by `id` (not by slug) serves only the dashboard editor, and requires a mandatory `Auth::check()`, because it has to load even never-published drafts into the form. It’s the third way to reach the same content, each with its own level of gate.

## 7. Editorial Workflow and Integrity

Three precautions hold the editorial experience together:
- **Auto-slug only on creation**: the slug is generated when the article is born, not on every title change, so as not to break links that are already published and indexed.
- **An editor that cleans itself between one piece of content and the next**: moving from editing one article to another, the editor component has to be unmounted and remounted (`key={item.id}`), so its internal buffers don’t drag text from one piece of content into the next.
- **Cover preview**: the form shows a thumbnail of the selected image, with immediate removal before saving.

On the dashboard side, the management table minds its proportions (the title no wider than 45% of the grid, a category column with colored badges for quick scanning, dates and dynamic state clearly visible, the actions condensed into icons at the end of the row): SimonePizziWebSite details, useful as a UX reference more than as a prescription.

> [!IMPORTANT]
> **The Canon**
> - Draft/scheduled/published states; the `published_at <= NOW` comparison must be done in the same format and timezone (or delegated to `NOW()`).
> - For non-public content, respond 404, not 403: don’t confirm that a draft exists.
> - Extend a contract (e.g., `{data, total}`) instead of versioning it, but keep it consistent across endpoints.
> - JSON cache with a TTL for heavy listings, invalidated on `save`/`delete`.

---
*Next Chapter: Security & Auth. Session management, CSRF, roles, and anti-abuse protection.*
