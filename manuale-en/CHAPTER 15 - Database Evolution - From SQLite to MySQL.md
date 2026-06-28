# CHAPTER 15: Database Evolution — From SQLite to MySQL

On February 23, 2026, at 2:25 a.m., a SitoRuntime commit carries a terse message: “Risolto crash server e ottimizzate performance con switch SQLite WAL->DELETE” (Fixed server crash and optimized performance by switching SQLite WAL→DELETE). The next day, the 24th, the site abandons SQLite and moves to MySQL. The two dates, one day apart, tell the story of this chapter on their own: the migration wasn’t a planned upgrade, it was an escape.

It’s the difference that changes everything. You could describe the move from SQLite to MySQL as a growth threshold: more traffic, more writes, more contention on the file, and at some point you change engines. It’s a reasonable guideline, and further on we give it too. But it isn’t SitoRuntime’s real story, and telling it that way would lose the most valuable lesson. SitoRuntime migrated because it had hurt itself, and this chapter isn’t about “how you migrate” but about **what a migration leaves behind** and who’s equipped to survive the next bad night.

The three sites in the Model have three different relationships with the same technique. DISINTELLIGENZA runs **on SQLite to this day, in production, without ever having gone down**: it’s living proof that the problem wasn’t the engine. SimonePizziWebSite migrated to MySQL quietly, with no incident in git, and with a safety net underneath. SitoRuntime migrated on the run, at night, and left six fossils and no backup behind it. It’s the same reversal that runs through the whole book: the site that suffered the most is the one least prepared to suffer again.

---

## 1. The WAL Night: When the Optimization Is the Disaster

Before the migration, SitoRuntime was on SQLite and wanted to go faster. SQLite, on its own, can use a journaling mode called **WAL** (Write-Ahead Logging): faster on writes, because it queues the changes in a side file instead of rewriting the database right away. On paper it’s an optimization. In practice, on shared Apache/PHP hosting, WAL creates two service files (`.sqlite-wal` and `.sqlite-shm`) and needs a kind of locking that many shared hosts don’t handle well. The locks don’t release, the requests time out, the site goes down.

The treatment lives inside the code that explains it, and it’s twofold. One script forces the return to classic journaling:

```php
// SitoRuntime optimize_db.php:17-22 — the "optimization" that triggered the crash, this is SQLite code
// WAL is performant but often causes locks on shared hosting.
// We set DELETE for maximum stability.
$pdo->exec("PRAGMA journal_mode=DELETE;");   // ← PRAGMA: a SQLite-only directive
```

And a second script is the red button, to be pressed from the browser if the site is already timing out:

```php
// SitoRuntime emergency_revert_wal.php:19-43 — the first-aid kit
$result = $pdo->query("PRAGMA journal_mode=DELETE");   // removes the .wal/.shm files
$mode = $result->fetchColumn();
if (strtoupper($mode) === 'DELETE') echo "SUCCESSO: …ripristinato…";
$pdo->exec("VACUUM;");                                  // rebuild of the DB file
// in the catch: "potresti dover eliminare manualmente i file .wal e .shm via FTP"
```

> [!WARNING]
> **When the optimization is the cause of the disaster**
> WAL isn’t a mistake: in many contexts it’s the right choice. But on shared hosting, where the filesystem and the locking are outside your control, touching a file-based database’s `journal_mode` is a high-risk change disguised as an improvement. It’s the reason Chapter 3 prescribes `journal_mode=DELETE` and not WAL: it isn’t an aesthetic preference, it’s a lesson paid for in production, at night. The general rule: an optimization that changes how the engine writes to disk has to be treated as a risky change, with a backup first and a rollback plan ready, not as a switch to flip and forget.

The correct diagnosis isn’t “SQLite can’t take it.” It’s “touching WAL on shared hosting can’t take it.” The proof comes from the site next door.

---

## 2. DISINTELLIGENZA: SQLite Alive, in Production, Without Scars

While SitoRuntime fled, DISINTELLIGENZA stayed. It runs today on SQLite, with the database in a file inside `.data/`, on the same kind of shared hosting, and it has never gone down. Everything that in SitoRuntime is an inert fossil (`PRAGMA`, `sqlite_master`, `AUTOINCREMENT`, the file-based database) is here the real, current engine. The difference isn’t the engine: it’s that DISINTELLIGENZA never touched the journal mode to squeeze out performance it didn’t need, and it makes a `.bak` backup before every destructive operation (Chapter 10).

This qualifies the practical rule rather than refuting it. SQLite stays perfect for lightweight or in-development projects: zero configuration, a single file, a deploy in seconds. The threshold beyond which it’s worth considering MySQL does exist, and it’s recognized by concrete signals more than by a number:

- **frequent concurrent writes**: more users writing at the same instant means more contention on the file lock;
- **hosting that limits or blocks SQLite** for internal policy reasons;
- **a need for external access to the database**, for example from phpMyAdmin or visual management tools, which talk to a server, not to a file;
- **complex queries on large tables**, where MySQL handles joins and aggregations better.

As a rough line, as long as a site stays under a few dozen writes an hour and shows no recurring locks, SQLite is enough for it. DISINTELLIGENZA is in that band and sits there comfortably. SitoRuntime left it not because it had crossed the traffic threshold, but because a botched optimization had made it want to no longer have a file-based database. They’re two different roads to MySQL, and only one of them is the textbook one.

---

## 3. Evolving a Schema Without Migration Tools

There’s a trait the three sites share, and it’s the real context of the whole chapter: **none of them has a migration tool**. No `migrations/` folder, no `schema_version` table, no runner that keeps track of what’s already been applied. The schema evolves with a single tool, the same everywhere.

The tool is `ALTER TABLE … ADD COLUMN` inside a `try/catch`, made idempotent. You add the column, and if the error says it already exists you treat it as a success. On MySQL the signal is the `Duplicate column` code:

```php
// SitoRuntime migrate_status.php:6-16 — the micro-migration that heals itself
$pdo->exec("ALTER TABLE news ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'published'");
// …
} catch (PDOException $e) {
    if ($e->getCode() == '42S21' || strpos($e->getMessage(), 'Duplicate column') !== false) {
        echo "OK: colonna 'status' già presente.\n";   // re-running = no harm
    } else { echo "ERRORE: " . $e->getMessage() . "\n"; }
}
```

On SQLite the same philosophy changes dialect: you query `PRAGMA table_info` and add the column only if it’s missing.

```php
// DISINTELLIGENZA update_db_v0.4.2.php:10-17 — same pattern, SQLite dialect
$columns = $pdo->query("PRAGMA table_info(users)")->fetchAll(PDO::FETCH_COLUMN, 1);
if (!in_array('role', $columns)) {
    $pdo->exec("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'editor'");
    $logs[] = "Added 'role' column to users table.";
} else {
    $logs[] = "'role' column already exists in users table.";
}
```

The price of this simplicity is that **no file represents the current schema**. The version is implicit, written in the file names: DISINTELLIGENZA has a chain `update_db_0_1_3` → `0_1_4` → `v0.4.2` → `v0.5.4`, SitoRuntime has `apply_v291` and `apply_v293`. To know what a table really looks like today, reading a file isn’t enough: you have to query the database, or reconstruct the history from the names and the order in which they were run.

> [!WARNING]
> **Without a registry, the schema’s truth lives only in the database**
> Versioning the schema with file names works as long as there’s a single person who remembers the order. But there’s no clean path to recreate the database from scratch: in SitoRuntime it would take `init_mysql.php` plus the `apply_v29x` chain applied in the right order, and the starting `init_db.php` is a fossil stuck at an old version. It’s the thin stack’s “schema-as-code” debt: the price to pay for not having adopted a migration system. If the project grows, a `schema_version` table with a list of applied migrations costs little and pays off at the first disaster recovery.

To this is added a delivery duality. The same migration often exists in two forms: as a throwaway file to upload and delete, and as a persistent action inside the admin console. SitoRuntime’s `status` column, for example, lives both in `migrate_status.php` and as an `?action=apply_v291_status` action inside `admin.php`:

```php
// SitoRuntime admin.php:459-469 — the same migration, but self-healing behind the login
if ($action === 'apply_v291_status' && $_SERVER['REQUEST_METHOD'] === 'GET') {
    try {
        getDB()->exec("ALTER TABLE news ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'published'");
        sendSuccess(['message' => "OK: colonna 'status' aggiunta…"]);
    } catch (PDOException $e) {
        if (strpos($e->getMessage(), 'Duplicate column') !== false) sendSuccess([/* … */]);
        else sendError('Errore DB: ' . $e->getMessage(), 500);
    }
}
```

Two philosophies coexist: the script to FTP and then remove, and the maintenance console behind a login. They’re both legitimate, but without a registry neither one tells you, just by looking at it, whether that migration has already run on a given database. They’re GETs protected by `isLoggedIn` alone, not by role or a CSRF token: their harmlessness depends on being idempotent, not on a real barrier (it’s the same gate hole seen in Chapter 14).

---

## 4. Switching Engines: the Three-Script Pattern

When the engine migration was decided, SitoRuntime carried it out with three dedicated scripts, each with a precise role. It’s a hand-rolled ETL, with no tools, and it’s a positive, citable pattern.

The first is the secrets file, kept out of version control:

```php
// db_credentials.php — to be added to .gitignore RIGHT AWAY, never commit real credentials
<?php
return [
    'DB_HOST' => 'mysql.tuohoster.com',
    'DB_NAME' => 'nome_database',
    'DB_USER' => 'utente_mysql',
    'DB_PASS' => 'password_sicura',
    'DB_PORT' => 3306,
];
```

The second is the MySQL connector, which replaces the SQLite version of `db.php`:

```php
// db.php (MySQL version) — the connection singleton
$config = require __DIR__ . '/db_credentials.php';
$dsn = sprintf("mysql:host=%s;dbname=%s;port=%d;charset=utf8mb4",
               $config['DB_HOST'], $config['DB_NAME'], $config['DB_PORT']);
self::$pdo = new PDO($dsn, $config['DB_USER'], $config['DB_PASS'], [
    PDO::ATTR_ERRMODE           => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES   => false,   // native prepared statements: on SQLite this was the default, here it must be forced
    PDO::ATTR_TIMEOUT            => 5,        // SQLite read a local file; MySQL is over the network, the timeout matters
    PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"
]);
```

Three details of the move deserve attention. `EMULATE_PREPARES => false` enables native prepared statements, which on SQLite were implicit. The `charset=utf8mb4` in the DSN plus the `SET NAMES` ensure that emoji and accents survive. And `PDO::ATTR_TIMEOUT` appears for the first time: with a local file it wasn’t needed, with a server over the network it’s essential. What disappears, instead, are all the `PRAGMA` directives: `journal_mode`, `busy_timeout`, `foreign_keys` were SQLite language and on MySQL they make no sense.

The third script, `init_mysql.php`, recreates the schema from scratch in MySQL dialect; it’s run once, protected by authentication and then removed. And the fourth, the real move, is the ETL: it opens two connections, copies table by table idempotently, and closes with an explicit check.

```php
// SitoRuntime migrate_to_mysql.php:37-72,199-209 — two PDOs, idempotent copy, count verification
$sqlite = new PDO("sqlite:" . $sqlitePath);   // source: the file
$mysql  = Database::connect();                 // destination: MySQL
$rows = $sqlite->query("SELECT * FROM news ORDER BY id ASC")->fetchAll();
$stmt = $mysql->prepare("INSERT INTO news (id, slug, title, summary, content, …)
                         VALUES (?, ?, ?, ?, ?, …)
                         ON DUPLICATE KEY UPDATE title=VALUES(title), …");   // re-runnable
foreach ($rows as $r) { $stmt->execute([$r['id'], $r['slug'], …]); $count++; }
// at the end, the cross-check table by table:
foreach (['news','users','subscribers','speakers','podcasts'] as $t) {
    $c = $mysql->query("SELECT COUNT(*) FROM $t")->fetchColumn();
    echo "  $t: $c record in MySQL\n";
}
```

> [!TIP]
> **The thin stack’s ETL: two PDOs and a COUNT**
> To move data between two engines you don’t need a dedicated tool: two PDO connections, a loop that copies with `ON DUPLICATE KEY UPDATE` (so the copy can be repeated without creating duplicates), and a final `COUNT(*)` that confirms how many records reached the destination are enough. It’s the minimal, readable, verifiable version of a data migration. The script should then be uploaded to the server only for as long as needed and deleted together with the `.sqlite` file: leaving it lying around is a risk, not a convenience.

---

## 5. What Changes, Line by Line, Between the Two Engines

The move touches dozens of micro-decisions. The table sums them up.

| Aspect | SQLite | MySQL |
| :--- | :--- | :--- |
| Connection | local file | network (host:port) |
| Engine directives | `PRAGMA journal_mode`, `busy_timeout`, `foreign_keys` | not applicable |
| Charset | configurable per file | `utf8mb4` for emoji and accents |
| Auto-increment | `INTEGER PRIMARY KEY AUTOINCREMENT` | `INT AUTO_INCREMENT PRIMARY KEY` |
| Boolean | `INTEGER` (0/1) | `TINYINT(1)` |
| JSON | stored as `TEXT` | native `JSON` type |
| Prepared statements | native by default | native with `EMULATE_PREPARES=false` |
| Concurrent writes | file lock (problematic) | row-level locking, handled by the daemon |
| Backup | copy of the `.sqlite` file | `mysqldump` or dedicated tools |

The last row is the one that hurts SitoRuntime the most, and we’ll get to it shortly.

---

## 6. The Six Fossils: Repo Hygiene After a Migration

After the switch, the SQLite layer wasn’t removed. In a MySQL repository there remain **six files written for an engine that no longer exists**: inert at best, broken at worst.

| Fossil | SQLite mechanism | State on MySQL |
| :--- | :--- | :--- |
| `init_db.php` | `AUTOINCREMENT`, seed of the 24 speakers | creates the wrong types, partly broken |
| `fix_users_table.php` | `sqlite_master`, `PRAGMA`, `datetime('now')` | **broken** (PRAGMA gives a syntax error) |
| `fix_newsletter_table.php` | `sqlite_master`, `PRAGMA`, 4-column schema | **broken** and obsolete |
| `setup_podcasts.php` | `AUTOINCREMENT` | partly harmless |
| `optimize_db.php` | `PRAGMA journal_mode`, `CREATE INDEX IF NOT EXISTS` | **broken** |
| `emergency_revert_wal.php` | `PRAGMA`, `VACUUM` | **inert** (WAL doesn’t exist on MySQL) |

The most toxic fossil is the first. `fix_users_table.php` queries the schema with SQLite dialect, on a database that is now MySQL:

```php
// SitoRuntime fix_users_table.php:12,20 — code that speaks the wrong engine's language
$stmt = $pdo->query("SELECT name FROM sqlite_master WHERE type='table' AND name='users'");  // SQLite!
$stmt = $pdo->query("PRAGMA table_info(users)");        // on MySQL → syntax error
$pdo->exec("UPDATE users SET created_at = datetime('now') WHERE created_at IS NULL");        // datetime() = SQLite
```

The only safety net keeping them in check is the by-prefix `.htaccess` deny, which blocks HTTP execution of every script with a maintenance name:

```apache
# SitoRuntime public/.htaccess:32-35 — the only barrier against the fossils
RewriteRule ^(debug_|test_|emergency_|migrate_|fix_|init_|rebuild_|setup_|optimize_) - [F,L]
```

> [!WARNING]
> **An engine migration has to be finished by deleting, too**
> Those scripts are still on the server and still in the repo. They produce three harms: noise (whoever opens the project doesn’t know which files count), confusion about the schema’s truth, and a latent attack surface, because if one day the `.htaccess` deny dropped, they’d be powerful, reachable endpoints. Migrating engines isn’t done when the data has moved: it’s done when the old engine’s code has been removed. Keeping the fossils “to be safe” is the opposite of safe.

---

## 7. One Table, Three Different `CREATE`s

The “no file represents the schema” debt has a concrete face in SitoRuntime’s `subscribers` table, which in the code exists in **three divergent definitions**:

1. `init_mysql.php` creates it with four columns, the base schema, predating double opt-in.
2. `fix_newsletter_table.php`, the SQLite fossil, recreates the same four columns, and it’s broken on MySQL and insufficient anyway.
3. `apply_v293_newsletter`, inside `admin.php`, is the **real** migration: it adds the double opt-in columns (`confirmation_token`, `confirmed_at`, `subscribed_at`, `subscribed_ip`) and retroactively confirms the historical subscribers.

Only the third is aligned with the runtime. The newsletter code (Chapter 13) **assumes** the extended schema, so on a database that has only the base schema every query fails until `apply_v293` runs. It’s an undeclared ordering dependency: the right schema exists, but only if you’ve run the right migration, which no file tells you to run.

> [!WARNING]
> **Where a table’s truth lives**
> When the same table has three `CREATE`s scattered across three files, and only one is the good one, the source of truth isn’t the code but the running database. It’s a symptom of a schema versioned by file names: the correct definition exists, but it’s hidden in the chain of migrations instead of in a single place. You pay for it the day someone recreates the database from the wrong file and everything looks fine until the runtime starts failing.

---

## 8. The Date-as-String Bug

Migrations leave scars in the data too, not only in the schema. SitoRuntime keeps `debug_time.php`, the diagnostics of a timezone incident. The article visibility rule compares `published_at <= now` **as strings**: if the server’s timezone and the date format don’t match, published articles vanish from the site.

```php
// SitoRuntime debug_time.php:23-24 — the "fix" that never reached production
// FIX: Use T separator to match DB
$now = date('Y-m-d\TH:i:s');   // 'T' separator
```

The revealing detail is that this fix was never applied to the runtime. The production code (`news.php`) uses the space, not the `T`, because the space is the correct format for MySQL’s DATETIME. The “solution” with the `T` stayed only in the diagnostic file, a record of a past bug and of a correction the real site, in the end, didn’t adopt.

> [!TIP]
> **Comparing dates as strings is a bug in waiting**
> Two dates compared as text match only if they have exactly the same format and the same timezone. It takes just a `T` in place of a space, or a server set to UTC while the content is written in local time, for a “published” article to stay invisible. The defense is to force the timezone explicitly (`date_default_timezone_set('Europe/Rome')`) and compare values in the same format as the database’s date type, or to delegate the comparison to the database with `NOW()`.

---

## 9. The Cure Without the Prevention

What remains is the most painful row of the §5 table: the backup. SitoRuntime has the defibrillator, `emergency_revert_wal.php`, the script that revives the site after the incident. But it doesn’t have the check-up: no automatic backup, no cron, no scheduled `mysqldump`. The only safety net is a `_BACKUP_BEFORE_OPTIMIZATION/` folder, a manual snapshot of the project committed to the repo before the risky operation. It’s a gesture, not a system, and on top of that it’s versioned noise.

The contrast with the other two is sharp. SimonePizziWebSite has the automatic backup written outside the document root, with rotation and a protected cron (Chapter 14). DISINTELLIGENZA makes a `.bak` before every destructive reset (Chapter 10). If SitoRuntime’s MySQL corrupts, there’s no recent dump to start over from.

> [!WARNING]
> **Having the defibrillator but not the fire alarm**
> It’s the paradox at the heart of the chapter. The site mapped precisely for its incidents is the one without the most basic safety net: a backup. It learned to *cure* the disaster, the emergency script is proof that the pain was real, but it didn’t learn to *prevent* it. Curing an emergency is reactive: it keeps you alive this time. An automatic backup is preventive: it keeps you alive for the next one, the one you didn’t see coming. The checklist below prescribes a backup, and it’s the ought-to-be; SitoRuntime tells you what happens when you skip it.

---

## 10. Migration Checklist

The sequence, in order, for a SQLite → MySQL move done right. The first point is also the one SitoRuntime didn’t have: it isn’t a detail, it’s the safety net.

- [ ] Make a full backup of the production `.sqlite` file, and archive it outside the repo.
- [ ] Create the MySQL database on the hosting provider.
- [ ] Upload and run `init_mysql.php` to create the schema, then remove it.
- [ ] Upload the `.sqlite` and `migrate_to_mysql.php` to the server.
- [ ] Run `migrate_to_mysql.php` and verify the counts in the summary.
- [ ] Replace `db.php` with the MySQL version and upload `db_credentials.php` with the real credentials.
- [ ] Add `db_credentials.php` to the `.gitignore` (before the project’s first commit).
- [ ] Test all the APIs in production, including those that assume migrations beyond the base schema.
- [ ] Delete `migrate_to_mysql.php` and the `.sqlite` file from the server.
- [ ] **Remove the old engine’s fossils from the repo** (`init_db.php` SQLite, `fix_*`, `optimize_db.php`, `emergency_revert_wal.php`): the migration isn’t finished while they remain.
- [ ] Configure an automatic MySQL backup, outside the document root: the cure doesn’t replace the prevention.

---

## In Summary

The engine migration isn’t a scaling rung everyone climbs sooner or later: it’s an event, and the *why* matters as much as the *how*. SitoRuntime fled SQLite after a bad night, and brought MySQL along without cleaning house, leaving behind six fossils, three versions of the same table, and no backup. DISINTELLIGENZA proves that SQLite in production holds up just fine, until you ask it for an optimization it can’t deliver on its own ground. SimonePizziWebSite made the same journey quietly, with a safety net underneath. The lesson isn’t “migrate to MySQL” and it isn’t “stay on SQLite” either: it’s that every schema evolution, and even more every engine change, has to be carried all the way through, with a registry of what you did and a backup of what you had before. What a migration leaves behind weighs more than what it carries forward.

> [!IMPORTANT]
> **The Canon**
> - Migrate engines only for a concrete constraint (recurring locks, hosting, remote access), not out of superstition; make the backup **first**, outside the repo.
> - An idempotent ETL (`ON DUPLICATE KEY UPDATE`) with count verification at the end of the move.
> - Once the migration is done, remove the old engine’s fossils from the repo.
> - A single definition for each table and a schema registry (`schema_version`); the emergency cure doesn’t replace prevention, that is, the automatic backup.

---
*Next Chapter: Portfolio & Projects Module. The universal module for portfolios and showcases, with drag-and-drop reordering and switch-based visibility.*
