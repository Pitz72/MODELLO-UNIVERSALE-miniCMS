# APPENDIX A — Boilerplate Checklist: Starting a New miniCMS Project

This checklist sums up the practical steps to initialize a new web project (Site or Web App) based on the standards of the “Universal miniCMS Model.” For implementation details, refer to the chapters indicated. The `(Ch. N)` cross-references follow the numbering of the Third Edition (20 chapters + Appendices A and B).

---

## Phase 1: Environment Setup and Initial Security
- [ ] Create the base folder structure (`public/api/`, `src/`, `scripts/`). *(Ch. 2)*
- [ ] Create the `public/.htaccess` file for SPA routing (React Router). *(Ch. 2)*
- [ ] Scaffold the database: a `public/api/.data/` folder with an `.htaccess` → `Deny from all`. *(Ch. 2, 3)*
- [ ] Create the media folder (`public/api/uploads/`) and the cache (`public/api/.cache/`).
- [ ] Configure `vite.config.ts` with the correct proxy to avoid CORS locally. *(Ch. 6)*
- [ ] Create `.env.local` with the development variables (`VITE_API_URL=http://localhost/...`).
- [ ] Add `db_credentials.php` and `.env.local` to `.gitignore` (never commit credentials). *(Ch. 15)*

## Phase 2: Core Backend Configuration (PHP)
- [ ] Implement `db.php` with a lazy connection to SQLite (`PRAGMA journal_mode=DELETE`, `busy_timeout=5000`, `PRAGMA foreign_keys=ON`). Do **not** use WAL on shared hosting. *(Ch. 3, 15)*
- [ ] Include the auto-scaffolding in `db.php`: creation of the `.data/` folder and the deny `.htaccess` if they don’t exist. *(Ch. 3)*
- [ ] Create `init_db.php` to generate the tables and the default admin user with `password_hash()` (and change its password right away). *(Ch. 3, 10)*
- [ ] Create `auth_helper.php` or `auth.php` with the `Auth::check()` class that handles `session_start()` and the JSON headers. *(Ch. 5)*
- [ ] Configure secure session cookies (`httponly`, `samesite=Strict`, `secure` if HTTPS). *(Ch. 10)*
- [ ] Apply `date_default_timezone_set('Europe/Rome')` in **every** endpoint with time logic (a timezone inconsistency makes scheduled content disappear). *(Ch. 5, 12, 15)*
- [ ] Hide errors in production (`display_errors = 0` or a global `try-catch`): a `die($e->getMessage())` on a connection failure is a leak. *(Ch. 10)*

## Phase 3: Core Frontend Configuration (React)
- [ ] Implement `src/api.ts` with the reading of the payload’s shape (the “Double Read” pattern = read the success envelope, don’t clone the response) to intercept server errors. *(Ch. 6)*
- [ ] Configure `AdminLayout.tsx` with the auth guard (route-guard loader or check on mount) and the “Hard Logout” (`window.location.reload()`). *(Ch. 14)*
- [ ] Enable the “Role-Based UI” to show only the items allowed to the connected role (Admin vs. Editor): hiding the page is UX, **blocking the action is security and has to be done on the server**. *(Ch. 10, 14)*
- [ ] Use `key={item.id}` in the editor component to force the rich text editor to reset when the article changes. *(Ch. 8)*

## Phase 4: Media and Content Integration
- [ ] Implement `upload.php` with automatic GD resizing and name sanitization (`uniqid()`, the extension rebuilt, not the client’s). *(Ch. 7)*
- [ ] Add the `MediaPicker` component for the direct upload of audio and images. *(Ch. 8)*
- [ ] Use the editor (Tiptap) with HTML as the source of truth saved raw; the protection against XSS is sanitization **at the render** (DOMPurify), not paste-time cleaning, which is only cosmetic. *(Ch. 8)*
- [ ] Implement the slug logic with normalization of Italian accents if the content is in Italian. *(Ch. 5)*

## Phase 5: SEO and Syndication
- [ ] Create `public/index.php` as the SEO Engine: a DB query → injection of the meta tags into Vite’s HTML (Dynamic Rendering with UA-sniff). *(Ch. 11)*
- [ ] Add the rename of `index.html` → `index_react.html` in the build script if `index.php` lives in `public/`. *(Ch. 2, 11)*
- [ ] Create `api/rss.php` with a valid RSS 2.0 feed (correct header, RFC 822 dates, absolute URLs, escaped content). *(Ch. 12)*
- [ ] Add the `<link rel="alternate" type="application/rss+xml">` tag in the HTML `<head>`. *(Ch. 12)*

## Phase 6: Optimization and Deploy
- [ ] Configure “Real Scheduling” via a SQL query on `published_at` (comparison **in the same format/timezone**, or delegated to `NOW()`). *(Ch. 9)*
- [ ] Configure the JSON cache with a 300s TTL for heavy listing queries. *(Ch. 9)*
- [ ] Set up `clean-dist.js` in the build process to remove the `.sqlite` files from the `dist/` folder (and recreate at runtime the static defenses the build strips). *(Ch. 2, 14)*
- [ ] Configure the `Cache-Control: max-age=31536000` header for the files in `uploads/` via `.htaccess`. *(Ch. 7)*

## Phase 7: Security (the Nets That Emerged from the Real Cases)
*The items in this phase are the defenses that, missing in at least one of the mapped sites, produced the flaws told in the book.*
- [ ] **Upload with PHP-off**: in the upload folder, an `.htaccess` that disables PHP execution (the first anti-RCE barrier), plus validation by magic bytes (`finfo`), not by the MIME the client declares. *(Ch. 7)*
- [ ] **Three-rung CSRF**: a token generated server-side, sent to the client and validated on every state-changing request (POST/PUT/DELETE/admin actions). A `confirm()` is not a CSRF defense. *(Ch. 10, 14)*
- [ ] **Newsletter double opt-in**: two distinct tokens (confirmation and unsubscribe); the unsubscribe link needs a secret, the email in cleartext isn’t enough (it isn’t GDPR-compliant). *(Ch. 13)*
- [ ] **Automatic backup outside the document root**, with rotation and an unguessable name; a cron protected by a timing-safe secret and fail-closed. Having the emergency script doesn’t replace the backup. *(Ch. 14, 15)*
- [ ] **Shared server-side sanitization**: the four `content` emitters (render, SEO prerender, RSS feed, newsletter) must pass through the same cleaning; just one that forgets reopens the XSS hole. *(Ch. 8, 11, 12, 13)*
- [ ] **Gate by role, not just by login**: the admin endpoints verify `isAdmin`, not just `isLoggedIn`; powerful actions aren’t GETs without a token. *(Ch. 10, 14)*

## Phase 8: Specific to Site Type

### For Sites with a Newsletter (SitoRuntime pattern)
- [ ] Create the `subscribers` table with the **complete** double opt-in schema (`email UNIQUE`, `is_active`, `confirmation_token`, `confirmed_at`, `subscribed_at`, `subscribed_ip`, `created_at`): one table, a single `CREATE`. *(Ch. 13, 15)*
- [ ] Implement `newsletter.php` with an admin gate + public actions (subscribe, confirm, unsubscribe). *(Ch. 13)*
- [ ] Use the `{EMAIL_PLACEHOLDER}` pattern for the personalized unsubscribe link with a token. *(Ch. 13)*
- [ ] Distinguish the **throttle** from the **rate limit**: `usleep(500000)` every 10 emails paces the send (throttle), but does **not** protect against mail-bombing; for that you need a real rate limit on the subscribe action. *(Ch. 13)*

### For Portfolio/Personal Site (SimonePizziWebSite pattern)
- [ ] Add the `projects` table with `sort_order`, `is_visible`, `button_a`, `button_b`. *(Ch. 16)*
- [ ] Implement `projects.php` with the 5 HTTP methods, including PATCH for the visibility toggle and reordering. *(Ch. 16)*
- [ ] Create the `PortfolioGrid.tsx`, `ProjectEditor.tsx`, and `ProjectsList.tsx` components. *(Ch. 16)*

### For Festival/Contest (DISINTELLIGENZA / FDCA pattern)
- [ ] Add the `participants`, `votes`, and `settings` tables with the `registration_active` and `voting_active` master switches. *(Ch. 17, 18)*
- [ ] Implement `participants.php` with the pending → approved/rejected workflow. *(Ch. 17)*
- [ ] Implement `votes.php` with the real anti-fraud: the barrier is the **IP + 24h window** constraint (the cookie is only cosmetic). *(Ch. 18)*
- [ ] If the festival is born as a **fork**, secure the backend from scratch: the fork inherits every flaw, and the fix doesn’t follow it. *(Appendix B)*

### For SQLite → MySQL Migration (SitoRuntime pattern)
- [ ] Back up the `.sqlite` **before** touching the engine, and archive it outside the repo. *(Ch. 15)*
- [ ] Create a separate `db_credentials.php` (add it to `.gitignore`). *(Ch. 15)*
- [ ] Update `db.php` with the MySQL PDO connection (`utf8mb4`, `EMULATE_PREPARES=false`, `ATTR_TIMEOUT`). *(Ch. 15)*
- [ ] Run `init_mysql.php` to create the MySQL schema on the server, then remove it. *(Ch. 15)*
- [ ] Run `migrate_to_mysql.php` for the data move (ONE-SHOT with a count check, delete afterward). *(Ch. 15)*
- [ ] Once the migration is done, **remove the old engine’s fossils** from the repo (`init_db.php` SQLite, `fix_*`, `optimize_db.php`, `emergency_revert_wal.php`). *(Ch. 15)*

---
*This checklist accompanies the Third Edition of the Universal miniCMS Model. For implementation details, refer to the `.md` files of the corresponding chapters and appendices.*
