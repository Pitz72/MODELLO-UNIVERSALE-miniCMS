# CHAPTER 3: Database Strategy

The database is the heart of the miniCMS. This chapter defines the strategies for connection, integrity, and migration, drawing a careful line between two things that are easy to confuse: what the Model **recommends** and what the real sites **actually do**. The two don’t always line up, and saying so out loud is more useful than passing off a prescription as a snapshot.

## 1. Connection Architecture (PDO, One Engine at a Time)

The system uses PDO with a memoized singleton (the connection opens only once per request, Chapter 5). The engine underneath, though, isn’t abstracted away: SQLite and MySQL open the connection with different options, and the three sites pick those options at three different levels.

### 1.1 The Connection Options: The Snapshot

Before the prescription, here’s what happens in the real code. The three sites set PDO option sets of escalating paranoia, and it’s a good example of the three-rung scale from Chapter 1.

| Site | Engine | Real PDO options |
|---|---|---|
| **DISINTELLIGENZA** | SQLite (live) | **only** `ERRMODE=EXCEPTION` + `DEFAULT_FETCH_MODE=ASSOC`, via `setAttribute()`. No `PRAGMA` in `connect()`. |
| **SimonePizziWebSite** | MySQL | `ERRMODE` + `FETCH` + `EMULATE_PREPARES=false` (real prepared statements) |
| **SitoRuntime** | MySQL | `ERRMODE` + `FETCH` + `ATTR_TIMEOUT=5` + `MYSQL_ATTR_INIT_COMMAND` (`SET NAMES`) |

The surprising figure is the first row: the only site that today **actually** runs on SQLite (DISINTELLIGENZA) sets none of the “optimal” `PRAGMA` directives that most manuals take for granted. It opens the file and that’s it, with two options. It’s a minimal choice that works for its load, but it isn’t the most robust setup possible, and that’s why the prescription below should be taken for what it is: a piece of advice, not a description of the existing code.

### 1.2 The Connection Options: The Prescription

For an SQLite deployment on shared hosting, the Model recommends three `PRAGMA` directives on top of the base options:

```php
// RECOMMENDED for SQLite on shared hosting (not what DIS sets today)
self::$pdo = new PDO("sqlite:" . $dbPath);
self::$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
self::$pdo->exec("PRAGMA journal_mode = DELETE;");   // more stable than WAL on shared hosting
self::$pdo->exec("PRAGMA busy_timeout = 5000;");     // waits instead of failing under concurrent writes
self::$pdo->exec("PRAGMA foreign_keys = ON;");       // referential integrity (off by default in SQLite)
```

The 5000ms `busy_timeout` makes a concurrent write wait instead of failing right away (handy when the newsletter and the admin panel write at the same time). The `foreign_keys = ON` is needed because SQLite, unlike MySQL, leaves foreign keys disabled by default. But the line that carries a scar is the first one.

> [!WARNING]
> **Why `DELETE` and not `WAL`: the lesson comes from an incident**
> SitoRuntime, back when it still ran on SQLite, tried `journal_mode = WAL` in production to improve performance under load. On shared Apache hosting, WAL did damage: the `.sqlite-wal` lock file would hang around and corrupt reads. It took an emergency script (`emergency_revert_wal.php`) to get back to `DELETE`, and not long after, that disaster pushed the migration to MySQL (the full story is in Chapter 15). The lesson, for anyone staying on SQLite: on shared hosting, choose `DELETE`, not `WAL`. It’s a recommendation born from a real failure, not a matter of taste.

### 1.3 Hiding the File-Based Database (SQLite Only)

Anyone using SQLite has a problem that MySQL users don’t: the database is a file inside the site’s folders, and a file reachable over the web is the entire database, downloadable by anyone. In **DISINTELLIGENZA**, the defense is generated at runtime by the connection code: on the first `connect()`, if the `.data/` folder doesn’t exist, it gets created, and a `Deny from all` `.htaccess` is written inside it.

```php
// DISINTELLIGENZA db.php — the file-based DB's protection is created by the app, not pre-deployed
$dir = dirname($dbPath);                                  // .../.data
if (!is_dir($dir)) mkdir($dir, 0755, true);
$htaccessPath = $dir . '/.htaccess';
if (!file_exists($htaccessPath)) {
    file_put_contents($htaccessPath, "Require all denied\n");   // second net: <Files> in the global .htaccess
}
```

This pattern belongs to the SQLite sites, not the MySQL ones. SimonePizziWebSite and SitoRuntime have migrated to MySQL: they have no `.data/` folder with the database inside, because their data lives on the MySQL server, outside the docroot by nature. Generating the protection at runtime, rather than trusting it to a committed file, has a concrete reason that comes back in Chapter 14: the build script can strip the `.data/` folder out of the distribution, and with it the deny `.htaccess`, which would otherwise never reach the server.

---

## 2. Strategic Indexing

Read queries have to be instant. The Model calls for these indexes:

| Table | Column | Type | Purpose |
| :--- | :--- | :--- | :--- |
| `news` / `articles` | `slug` | UNIQUE | Article lookup by URL (SEO) |
| `news` / `articles` | `published_at` | DESC | Fast chronological ordering |
| `news` / `articles` | `status` | INDEX | Draft/published filtering |
| `speakers` | `sort_order` | ASC | Manual drag-and-drop ordering |
| `podcasts` | `slug` | UNIQUE | Quick access to series |
| `projects` | `category` | INDEX | Portfolio category filtering |
| `projects` | `sort_order` | ASC | Manual portfolio ordering |

After bulk loads, it helps to run `ANALYZE;` to recompute the access statistics and optimize the query plan.

---

## 3. The Migration Lifecycle

Schema changes have to be atomic, idempotent, and protected. Those are the requirements; the real sites meet them unevenly, and the difference matters.

- **Atomicity**: every migration uses a transaction (`beginTransaction`).
- **Idempotency**: the script checks whether a column or table exists before creating it (`IF NOT EXISTS`, `PRAGMA table_info`), so rerunning it breaks nothing.
- **Protection**: migration scripts **should** be unreachable by unauthenticated web requests. Here reality diverges: SitoRuntime denies them by prefix in the `.htaccess` or keeps them inside `admin.php` (gated), while DISINTELLIGENZA leaves its `update_db_*.php` and `migrate_media.php` reachable over HTTP without a gate. That’s a real security debt (Chapter 15), not a detail.
- **Naming**: no site has a `schema_version` table. The version lives in the **file names** (`update_db_v0.4.2.php`, `update_db_v0.5.4.php`), aligned with the version in `package.json`. The migration history is read from the folder, not from a record in the database.

---

## 4. Data Normalization

To avoid inconsistencies between PHP, JS, and the database, the Model normalizes before saving:
- **Dates**: `Y-m-d H:i:s` format, for SQL and JS compatibility. Mind the time zone: the `published_at <= NOW` visibility check is done on strings, and a date written with the wrong separator shifts the threshold (Chapter 5 and Chapter 9).
- **Numbers**: integers, or rounded to zero decimals, to avoid floating-point bugs.
- **Booleans**: `INTEGER` (0 or 1) in SQLite, `TINYINT(1)` in MySQL.

---

## 5. Maintenance and Integrity

- **VACUUM**: run it after bulk deletions to recompact the file and shrink it (relevant on SQLite).
- **Backups**: every migration **should** be preceded by a copy of the database in a protected folder. Here too, reality isn’t uniform: SimonePizziWebSite has an automatic backup outside the docroot, DISINTELLIGENZA makes a `.bak` copy before destructive actions, and SitoRuntime (the site that suffered the crash) has no automatic backup at all. The “treatment without prevention” paradox is in Chapter 14.
- **`optimize_db.php`**: SitoRuntime includes a maintenance script (`VACUUM`, `ANALYZE`, integrity check); despite its “throwaway” header, it’s actually non-destructive (it only adds idempotent indexes).

---

## 6. When to Move to MySQL

The full story, with the real scripts, is in Chapter 15. One point needs clearing up right away, because it’s a widespread half-truth: SitoRuntime’s migration was **not** decided by a traffic threshold reached at a calm pace. It was the reaction to an incident (the WAL crash that night) that made SQLite suddenly unreliable on that hosting. The threshold wasn’t a number on a chart, it was a corrupted database at 3 a.m.

The counterpoint is just as instructive: DISINTELLIGENZA, a festival with public voting, **still runs on SQLite** in production today, no trouble. SQLite isn’t a rung to abandon the moment you can: it’s the right choice as long as it holds, and “as long as it holds” depends on the load and the hosting, not on a universal rule. You move to MySQL when a concrete constraint forces it, not out of superstition.

### 6.1 The Numbers, Honestly

“As long as it holds” isn’t an answer you can leave to gut feeling. You need orders of magnitude, with the caveat that they stay that: they depend on the hardware, on the shared host’s disk, and on the shape of the queries, and they have to be measured against your own case, not taken as guarantees.

The key point is that in SQLite, **reads and writes don’t scale the same way**. Reads are concurrent and very fast: a read-heavy site (a blog, a portfolio, a radio station with news and podcasts) handles thousands of reads per second from the page cache and hundreds of read queries per second straight to the file without breaking a sweat, because multiple requests can read the same database at once. Writes, though, are **serialized**: SQLite allows one writer at a time and locks the whole file during a write. That’s where the ceiling is.

In practice, on typical shared hosting:

| Signal | SQLite is comfortable | Worth weighing MySQL |
| :--- | :--- | :--- |
| **Concurrent writes** | up to a few dozen per minute, sporadic | sustained dozens per second, or regular concurrent spikes |
| **Load profile** | read-dominant (90%+), isolated writes | frequent, simultaneous writes (forms, votes, queues) |
| **Write concurrency** | one process at a time is enough | multiple processes writing together (newsletter + admin + public) |
| **Topology** | a single application server | you need to scale across multiple nodes sharing the data |
| **Symptom in the logs** | no `database is locked` | recurring `busy timeout` or `database is locked` |

The real threshold isn’t a number but a **symptom**: when the logs start showing lock errors or `busy timeout` despite the configured `busy_timeout`, the database is telling you that write contention has outgrown what a file-based database can handle on that hosting. That’s the moment for MySQL, and not an instant sooner. Runtime Radio got there through an incident (Chapter 15); most sites never get there, and that’s exactly right.

> [!IMPORTANT]
> **The Canon**
> - SQLite with `journal_mode=DELETE` (never WAL on shared hosting), `busy_timeout`, and `foreign_keys=ON`; PDO in `ERRMODE_EXCEPTION`.
> - Index `slug` (UNIQUE), `published_at` (DESC), and `status`; run `ANALYZE` after bulk loads.
> - Migrations atomic, idempotent, and unreachable by unauthenticated web requests; keep a `schema_version` table (the real sites don’t have one: it’s a debt not to inherit).
> - Back up before every migration, in a protected folder outside the docroot.
> - Move to MySQL when the logs show recurring `database is locked`/`busy timeout`, not out of superstition.

---
*Next Chapter: Frontend Dependencies. The dependency matrix, the rules for choosing, and the cost of every library.*
