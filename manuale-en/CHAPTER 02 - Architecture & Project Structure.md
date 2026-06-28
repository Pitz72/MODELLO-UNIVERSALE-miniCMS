# CHAPTER 2: Architecture & Project Structure

This chapter defines the physical and logical architecture of the system: how the folders are laid out, where the secrets live, how a request finds its PHP file, and which defenses are wired into the structure itself rather than bolted on afterward.

## 1. Folder Topology and Asset Separation

The Universal Model enforces a clean separation between source files (build-time) and runtime files (the data that persists).

### 1.1 Physical Structure (Root)
```text
/
├── public/                 # Public content and API entry point
│   ├── .htaccess           # SPA routing (crucial for React Router)
│   ├── index.php           # SEO Engine (Chapter 11) — PHP entry point
│   └── api/                # Core PHP backend (see 1.2)
├── src/                    # React 19 / TS frontend
├── scripts/                # Utilities (build, clean, migration)
├── .env.local              # Local configuration (VITE_API_URL)
├── package.json            # Dependencies and automation scripts
└── clean-dist.js           # Post-build sanitization (SECURITY)
```

### 1.2 Anatomy of the API Area (`public/api/`)

The first thing to understand about this folder is what it *doesn’t* contain: a router. There’s no dispatching `index.php`, no kernel, no route table. Every endpoint is **a standalone PHP file**: `articles.php`, `upload.php`, `reactions.php`. Each one pulls in its building blocks at startup (the database connection, the session prelude if there is one, the headers) and handles its own request. This is the founding choice of the miniCMS, and the one that makes the “thin stack” literally thin: the URL `/api/articles.php` is the file `articles.php`, with nothing in between. The price is some repetition across files (the same `require` at the top of each); the payoff is that every endpoint reads, tests, and moves on its own, without forcing you to understand a routing system.

Alongside the endpoints live the runtime folders, which change depending on the database engine you choose:
- **`.data/`**: holds the **SQLite** database, so it exists only on the sites that use SQLite (like DISINTELLIGENZA). It must contain an `.htaccess` with `Deny from all`, because a `.sqlite` file reachable over the web is the entire database, downloadable by anyone. Sites migrated to MySQL don’t have this folder: their database lives on the MySQL server, outside the docroot by nature.
- **`.cache/`**: JSON files generated for performance (the content lists, see Chapter 9), invalidated on every write.
- **`uploads/`**: the assets uploaded by users (images, audio). It should be excluded from source-code backups, and on the better-defended sites it hosts its own `.htaccess` that **turns PHP off** (the first anti-RCE barrier, Chapter 7).

### 1.3 Configuration and Secrets: Three Approaches Without Libraries

Secrets never sit in versioned source. But the way to keep them out is a small scale of its own, and the three sites occupy it at three different points, all without a configuration library.

```php
// SPW config.php (gitignored) — paired with a versioned config.example.php
define('DB_HOST', 'localhost');
define('DB_NAME', '...');
define('SITE_URL', 'https://...');     // canonical constant, anti host-poisoning
```

```ini
; SR .env (gitignored) — read by db_credentials.php via parse_ini_file(); alongside it, .env.example
DB_HOST=localhost
TELEGRAM_BOT_TOKEN=...
SMTP_HOST=...        ; the .env is the hub for ALL the site's secrets
```

SimonePizziWebSite uses a `config.php` with `define()` calls, ignored by git and accompanied by a `config.example.php` committed as a reference. SitoRuntime uses a `.env` file read with `parse_ini_file()`, and it’s the hub for all its secrets (database, Telegram token, SMTP credentials). DISINTELLIGENZA has **no** configuration at all: the path to the SQLite file is written directly into `db.php`, because a file-based database has no credentials to guard. It’s the “twelve-factor” principle (configuration separated from code) applied without any library, with one radical exception: whoever sits at the base rung of the scale has no secret to manage in the first place.

---

## 2. Security at Build Time: The Clean-Dist Logic

One of the biggest risks is overwriting the production database during deployment. The system prevents this with a script (`clean-dist.js`) run after the build, which:
1. scans the `dist/api/` folder;
2. recursively removes every file with a `.sqlite`, `.sqlite3`, `.db`, or `.bak` extension;
3. warns the operator with a security log (`🚨 SECURITY: Removed...`);
4. guarantees, as a **design rule**, that the `dist/` is “database-free.” The database is initialized on the server or migrated by hand, never overwritten by the automatic build.

The exact pattern varies by site:
- **SimonePizziWebSite**: `"postbuild": "node clean-dist.js"` (automatic npm hook);
- **DISINTELLIGENZA**: `"build": "tsc -b && vite build && node clean-dist.js && move dist\\index.html dist\\index_react.html"` (renames `index.html` to enable the PHP SEO Engine, Chapter 11);
- **SitoRuntime**: `"build": "tsc -b && vite build && node scripts/remove-db-from-dist.js"` (dedicated script).

> [!WARNING]
> **The build can remove defenses too, not just databases**
> This script has a side effect that comes back in Chapter 14: by removing the `.data/` folder from the distribution, it also carries away the `Deny from all` `.htaccess` committed inside it. The static defense never reaches the server, and has to be recreated at runtime. The lesson holds for any build pipeline: always ask what the build *removes*, not just what it adds.

---

## 3. URL Routing: SPA vs. API

For React Router to coexist with the PHP APIs on Apache, the standard calls for an `.htaccess` in the public root:

```apacheconf
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  # If the request points to a real file or directory, serve it directly (so the APIs work)
  RewriteCond %{REQUEST_FILENAME} -f [OR]
  RewriteCond %{REQUEST_FILENAME} -d
  RewriteRule ^ - [L]
  # Otherwise route everything to index.html (or index.php if present)
  RewriteRule ^ index.html [L]
</IfModule>
```

Apache serves `index.php` before `index.html` by default priority. This is the mechanism that lets the SEO Engine (Chapter 11) intercept bot requests without touching the rewrite rules.

---

## 4. Dynamic File-System Initialization

The PHP backend doesn’t take the runtime folders for granted: it creates them when they’re needed.

```php
// Auto-scaffolding: create the runtime folders, and immediately protect the DB one
$paths = [__DIR__ . '/.data', __DIR__ . '/.cache', __DIR__ . '/uploads'];
foreach ($paths as $path) {
    if (!is_dir($path)) {
        mkdir($path, 0755, true);
        if (basename($path) === '.data') {                          // only the file-based DB
            file_put_contents($path . '/.htaccess', "Order allow,deny\nDeny from all");
        }
    }
}
```

The site that runs on SQLite (DISINTELLIGENZA) generates the `.data/` folder and its `Deny from all` `.htaccess` **at runtime**, inside the connection code: the protection is produced by the application, not pre-deployed, with a `<Files>` block in the global `.htaccess` as a second safety net. The MySQL sites have no file-based database to hide, but they apply the same principle (create at runtime what the deploy doesn’t bring) to `cache`, `uploads`, and the backups folder (Chapter 14). The shared rule: don’t trust that a folder exists, and don’t trust that a static defense makes it all the way to the server.

---

## 5. Environment Management

- **Development**: the frontend runs on the Vite dev server, which proxies to the local PHP to avoid CORS errors. SimonePizziWebSite, which in development goes through a different port (`localhost:8888`), is the only one that has to handle this on the client side too (Chapter 6).
- **Production**: the frontend points to `/api`, a relative same-origin path, so cookie authentication works without CORS and without domain configuration.

---

## 6. The Fork Pattern (FDCA from DISINTELLIGENZA)

FDCA and DISINTELLIGENZA share an **identical** PHP structure: same files, same logic, because FDCA was born from a fork of the more mature project. It’s a deliberate choice: when two projects have the same functional base (a festival with voting), you start from a copy of what already works.

The advantage is independence: no shared dependency, each project evolves on its own. The risk is the exact flip side of that advantage: every bugfix and every improvement has to be reapplied by hand on both branches, and when the fix concerns security, forgetting it means leaving a hole open in one site while you close it in the other. That’s exactly what happened here (the upload RCE chain from Chapter 7 was mapped on DISINTELLIGENZA but lives unchanged in FDCA), and the reason the life of a fork deserves an appendix of its own.

> [!IMPORTANT]
> **The Canon**
> - One file per endpoint, no central router: every PHP endpoint pulls in its building blocks and stands on its own.
> - Keep secrets out of versioned code (`config.php`/`.env` in `.gitignore`, with a committed `.example`).
> - Keep the file-based database and sensitive folders outside the docroot, or protected by a deny `.htaccess` generated at runtime: the build can remove static defenses.
> - Separate the `dist/` from the sources and have `clean-dist` strip the `.sqlite` files from the distribution.

---
*Next Chapter: Database Strategy. Locks, indexes, migrations, and the real story of the WAL.*
