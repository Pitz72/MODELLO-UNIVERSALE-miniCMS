# CHAPTER 10: Security & Auth

Security is the only lens in this book where the three sites don’t scale in step with how engineered their backend is. In every other chapter an intuitive rule holds: the more a site has grown, the richer its infrastructure. Not here. The same thin-stack skeleton (native PHP, cookie-based sessions, Apache rules in the `.htaccess` files) holds up three descending rungs of defense, but the top rung doesn’t belong to the site with the most sophisticated backend.

SimonePizziWebSite (SPW) has the most mature perimeter: `Secure` cookies, anti session-fixation, global session invalidation, full password recovery, IP anti-spoofing. SitoRuntime (SR), the most engineered site of the trio, the one with the scalability scars, is only halfway there: it has roles and CSRF tokens, but the cookie travels without `Secure`, it doesn’t regenerate the session at login, and its rate limit can be sidestepped with a header. DISINTELLIGENZA (DIS) is base-rung authentication: no CSRF, no rate limit, cookies at PHP’s default values. And yet it’s the only one of the three to bring two security ideas of its own that are genuinely worth something: anti-fraud defense for a public action (the festival vote) and an automatic backup before a destructive operation.

It’s the sharpest demonstration of the thesis that runs through the whole book: more engineered doesn’t mean more secure, and more secure doesn’t mean more complete on every single point. The right way to read each defense is as a scale of subtraction: what’s left, and what breaks, when you remove a flag from the cookie, a token from a request, a counter from a login endpoint.

> [!NOTE]
> **A note on method.** Every code excerpt in this chapter comes from the real state of the three sites, cited as `file:line`. When the chapter says “the Model recommends,” it’s prescribing; when it says “SPW does” or “SR does” or “DIS does,” it’s photographing the code in production. The two don’t always line up, and it’s precisely in that gap that you learn.

---

## 1. The Common Perimeter: Security by Hand

Before the divergences, it’s worth pinning down what the three sites share. Under the three implementations there’s the same object, with five recurring traits.

**1) No authentication library.** No Passport, no JWT package, no session framework. Everything rests on native PHP primitives: `session_*`, `password_hash`/`password_verify`, `random_bytes`, `hash_equals`, and on the Apache rules in the `.htaccess` files. Auth is built by hand, and it’s the founding choice that makes every difference between the sites a visible choice, not a configuration buried inside a vendor.

**2) Cookie session plus `password_verify`: the identical base.** All three open a native PHP session, look the user up by `username`, verify the password against a `PASSWORD_DEFAULT` hash, and populate `$_SESSION`. The system never knows the password in cleartext:

```php
// The scheme common to the three sites: no secret in cleartext
$hash = password_hash($password, PASSWORD_DEFAULT);   // at creation
// ...
if (password_verify($input, $user['password_hash'])) { /* login ok */ }
```

**3) The gate is a handful of lines at the top of the endpoint.** There’s no middleware and no router: protecting an endpoint is a few lines at the start of the mutating branch, demanding a valid session before touching the data. It’s the thin-stack version of middleware. But how much that handful of lines does (session only? plus CSRF? plus role? plus invalidation?) is the first major axis of divergence, and we’ll see it in §2.

**4) “JSON-first” defense even on security errors.** A denied access doesn’t produce an Apache error page: you set the semantically correct HTTP code (`401`/`403`/`429`) and respond with a `{status|success, message|error}` object. The frontend reacts by code.

**5) Server-level hardening via `.htaccess`.** All of them have at least one `.htaccess` that sets security headers and denies access to sensitive files. It’s the second layer, outside the application, and here too the coverage ranges from complete (forced HTTPS, HSTS, CSP, PHP off) to minimal (a deny on two extensions).

To these is added one shared negative trait: none of the three keeps an access audit log, and in two cases out of three the login’s brute-force counter doesn’t even live in the database. The perimeter is thin by construction. The chapter’s question is how thin you can go before something breaks.

---

## 2. The Gate: Single Middleware, Composable Gate, Inline Gate

Protecting an endpoint means deciding, at the top of the code, whether the caller has the right to proceed. The three sites solve the same problem with three different architectures, and it’s the first point where the scale becomes visible.

### 2.1 SPW: the Single Gate `Auth::check()`

SPW concentrates everything in a class included by every protected endpoint. A single line, `Auth::check()`, does three things in sequence: it demands a valid session, verifies anti-CSRF on the mutating methods, and checks invalidation via `session_version`.

```php
// public/api/articles.php:238-239 — the typical consumer
elseif ($method === 'POST') {
    Auth::check();          // session + CSRF + session_version, all here
    // ... from here on you can write
```

The advantage is that coverage is automatic: every new endpoint that includes `auth_helper.php` and calls `Auth::check()` inherits all the defenses together. There’s no way to remember the session and forget the CSRF.

### 2.2 SR: the Composable Function Gate

SR breaks the same protection into separate bricks, authorization on one side and anti-CSRF on the other, which each endpoint composes by hand in the right order:

```php
// public/api/auth_utils.php — the bricks
function isLoggedIn() { return isset($_SESSION['user_id']); }
function isAdmin()    { return isLoggedIn() && ($_SESSION['role'] ?? '') === 'admin'; }

// public/api/upload.php:8-13 — the consumer composes them
if (!isLoggedIn()) { http_response_code(401); echo json_encode([...]); exit; }
// ...
validateCsrf();
```

It’s more flexible, and the role gate (`isAdmin()`) comes for free: you get that `admin`/`editor` distinction SPW doesn’t have. But it’s also easier to forget, because protection depends on the discipline of each individual endpoint.

### 2.3 DIS: the Raw Inline Gate

DIS takes the same scheme to the extreme. No file of brick functions: the gate is rebuilt by hand in every branch as a bare `isset()`.

```php
// public/api/reset_votes.php:11 — the whole gate, inline
if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'admin') {
    http_response_code(401); die(...);
}
```

> [!WARNING]
> **Middleware or discipline? The gate you forget**
> The composable gate and the inline gate carry a structural risk the single gate doesn’t: security depends on the order of the branches and on the memory of whoever writes them.
> In DIS the `participants.php?update_status` and `update_round` branches are protected by `isset($_SESSION['user_id'])` alone, not by `isAdmin()`. The result: an editor, not an administrator, can approve or reject participants, send the emails, and move the festival rounds. The same crack shows up in SR, where `list_users` and `create_user` sit before the `401` block and protect themselves only with the local role check.
> It works as long as every branch is written with discipline. But a single gate (`Auth::check()`) can’t be forgotten on an endpoint: either you include it, or the endpoint doesn’t start. That’s the real difference between middleware and convention. The consequences for the festival show up in Chapter 18.

---

## 3. CSRF: Three Rungs of Defense

Cross-Site Request Forgery is the problem of preventing a third-party site from sending mutating requests by exploiting the session cookie that the user’s browser attaches automatically. It’s the load-bearing defense of this chapter, and the three sites solve it at three distinct levels.

### 3.1 SPW: `Origin`/`Referer` Check (Server-Side, Zero Handshake)

SPW doesn’t use tokens: inside `Auth::check()`, on the non-safe methods, it compares the host of `Origin`/`Referer` with that of `SITE_URL`.

```php
// public/api/auth_helper.php:21-37 (excerpt)
$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';
if (!in_array($method, ['GET', 'HEAD', 'OPTIONS'], true)) {
    $source = $_SERVER['HTTP_ORIGIN'] ?? $_SERVER['HTTP_REFERER'] ?? '';
    if ($source !== '') {
        $sourceHost  = parse_url($source, PHP_URL_HOST);
        $allowedHost = parse_url(SITE_URL, PHP_URL_HOST);
        $isLocalDev  = in_array($sourceHost, ['localhost', '127.0.0.1'], true);
        if ($sourceHost !== $allowedHost && !$isLocalDev) {
            http_response_code(403);
            echo json_encode(['status' => 'error', 'message' => 'Origine della richiesta non valida']);
            exit;
        }
    }
}
```

It requires no handshake with the client, because the browser sends `Origin`/`Referer` on its own. And living inside `Auth::check()`, it automatically covers every endpoint that includes the guard.

### 3.2 SR: the Synchronized `X-CSRF-Token`

SR adopts the by-the-book pattern: a random token per session, returned to the client at login, sent back by the client in a header and validated with `hash_equals` (a timing-safe comparison).

```php
// public/api/auth_utils.php:20-35
function generateCsrfToken(): string {
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}
function validateCsrf(): void {
    $incoming = $_SERVER['HTTP_X_CSRF_TOKEN'] ?? '';
    $stored   = $_SESSION['csrf_token'] ?? '';
    if (!$stored || !hash_equals($stored, $incoming)) {
        http_response_code(403);
        echo json_encode(['success' => false, 'error' => 'Token di sicurezza non valido. Ricarica la pagina.']);
        exit;
    }
}
```

### 3.3 DIS: Nothing

In DIS the mutations are protected by the session cookie alone. A grep across all of `public/api/` finds no CSRF token and no `Origin`/`Referer` check: the defense is absent.

> [!WARNING]
> **CSRF in the thin stack: Origin/Referer, synchronized token, or nothing**
> There’s a counterintuitive subtext in these three rungs. The most “by-the-book” solution, SR’s synchronized token, is also the easiest to weaken, because it depends on per-branch discipline: one mutating endpoint that forgets `validateCsrf()` and the hole is open. The simplest solution, SPW’s `Origin`/`Referer` check, covers more precisely because it’s centralized inside the single gate. More code doesn’t mean more coverage. It’s the book’s underlying thesis applied to CSRF.

---

## 4. The Session Cookie and Anti Session-Fixation

> [!NOTE]
> **A common mistake about session cookies.** You’d be tempted to prescribe a cookie with `cookie_secure = 1` and `cookie_samesite = 'Lax'`. Looking at the real code, two things need correcting: the right `SameSite`, and the one the sites actually use, is `Strict`, not `Lax` (both SPW and SR); and only SPW actually sets all three flags.

The flags have to be set before `session_start()`, otherwise they have no effect on the current cookie. This is where the scale is clearest.

SPW sets the three flags in a shared file:
```php
// public/api/auth_helper.php:7-11
ini_set('session.cookie_httponly', 1);
ini_set('session.cookie_secure', 1);
ini_set('session.cookie_samesite', 'Strict');
session_start();
```

SR omits `Secure`:
```php
// public/api/auth_utils.php:4-9
ini_set('session.cookie_httponly', '1');
ini_set('session.cookie_samesite', 'Strict');
session_start();                       // NB: cookie_secure NOT set
```

DIS sets no flags at all: the cookie’s behavior depends entirely on the hosting’s `php.ini`. An implicit, silent dependency.

On top of this there’s anti session-fixation, that is, regenerating the session ID right after login to invalidate an ID an attacker may have planted earlier. Only SPW does it:

```php
// public/api/auth.php:186-188 (excerpt of the success branch)
if ($user && password_verify($password, $user['password_hash'])) {
    session_regenerate_id(true);     // anti session-fixation: one line, often missing
    $_SESSION['user_id'] = $user['id'];
    // ...
}
```

SR and DIS don’t regenerate: a session ID fixed before login stays valid afterward.

> [!WARNING]
> **The cookie flags, and why HSTS isn’t the HTTPS redirect**
> Dropping `Secure` isn’t a cosmetic detail. Without `Secure`, the session cookie can also travel over plain HTTP. You might think HSTS protects you anyway, but HSTS only protects after the first successful HTTPS visit. SR applies HSTS but doesn’t force the 301 redirect to HTTPS: there’s a real window of exposure over HTTP on the first access. SPW closes the window on both sides, with `cookie_secure=1` and with `RewriteCond %{HTTPS} !=on → 301`.
> The lesson: `Secure` on the cookie and a forced HTTPS redirect are two distinct defenses; HSTS doesn’t replace either of them.
> A historical aside (SPW): until v1.18 the flags were only in `auth.php`, so a cookie issued by another endpoint was born weak. v1.19.0 moved the `ini_set` calls into the shared file `auth_helper.php`. The session’s security config belongs in the file everyone includes, not in the login endpoint.

---

## 5. `check_auth` and the Session State

The frontend must never store the password or the login state in `localStorage`: it asks the server whether the session is still valid.

```php
// check_auth scheme (SPW/DIS)
if (isset($_SESSION['user_id'])) {
    echo json_encode([
        'status' => 'success',
        'user'   => ['username' => $_SESSION['username'], 'role' => $_SESSION['role']]
    ]);
}
```

> [!NOTE]
> **`username` isn’t guaranteed in the session.** You’d be tempted to read `$_SESSION['username']` as if it were always present. In SR it isn’t: login saves `user_id` and `role` but not `username` (`admin.php:123-124`). The consequence is concrete: `check_auth` returns `username: null`, and the article save falls back to `author = $_SESSION['username'] ?? 'Admin'`. In SPW and DIS the `username` is in the session and the example holds. It isn’t a security hole, but a real state inconsistency: the same field isn’t guaranteed across all three sites.

---

## 6. Passwords and Brute-Force Defense

Hashing is the only point where the three sites are identical and all correct: `password_hash($pass, PASSWORD_DEFAULT)` at creation, `password_verify` at verification. The system never knows the password in cleartext, and the algorithm can evolve (from bcrypt to argon2) without touching a line of code.

> [!NOTE]
> **Brute-force defense isn’t a `sleep(1)`.** You’d be tempted to reduce brute-force defense to a `sleep(1)`, but that’s an incomplete solution calibrated on SR alone. The `sleep(1)` is barely a stopgap; the real defense is lockout, and above all what matters is which IP you measure it from.

The question isn’t “how do I slow down the attempts” but where the counter lives. Three answers. SPW keeps it in a DB table `login_attempts`: after 5 failed attempts from an IP within 15 minutes the `429` kicks in, and on a successful login the counter resets.

```php
// public/api/auth.php:177-211 (excerpt)
if ($attempts >= 5) {
    http_response_code(429);
    echo json_encode(['status' => 'error', 'message' => 'Too many failed login attempts. Try again in 15 minutes.']);
    exit;
}
// ... on failure:
$pdo->prepare("INSERT INTO login_attempts (ip_address) VALUES (?)")->execute([$ip_address]);
```

SR keeps it on file: one JSON per IP in `.cache/ratelimit/<md5(ip)>.json`, a 900-second window, a threshold of 5, plus a `sleep(1)` on failure. No DB table, consistent with the MySQL schema that doesn’t contain `login_attempts`. DIS doesn’t keep it anywhere: the login can be hammered as much as you like.

> [!TIP]
> **The brute-force counter: file, DB, or absence**
> There’s no absolutely right home. SPW’s DB table is transactional and lends itself to reuse (the same `login_attempts` also serves recovery). SR’s file avoids burdening the database but lives outside the schema, so it doesn’t show up in a dump or a migration: it’s invisible until you go looking for it in the filesystem. DIS’s absence is consistent with a festival site where there’s a single admin and the friction on an internal login is low, but it remains an absence, not a documented choice.

The subtlest point, though, is which variable you read the IP from. It’s the anchor box of this chapter.

> [!WARNING]
> **Trusting the IP: the rate limit that doesn’t limit** *(anchor box, referenced in Chapter 18 and Chapter 20)*
> A “5 attempts per IP” lockout is worth exactly as much as your ability to know what the IP is. And here the three sites diverge in an instructive way.
>
> SR trusts the wrong header. It takes the IP from `X-Forwarded-For`, first and without validation:
> ```php
> // public/api/admin.php:106-107
> $ip = $_SERVER['HTTP_X_FORWARDED_FOR'] ?? $_SERVER['REMOTE_ADDR'] ?? 'unknown';
> $ip = trim(explode(',', $ip)[0]);   // ← the attacker controls this header
> ```
> That header is written by the client. An attacker varies it on every request and the counter never increments: the 5/15min lockout is sidestepped.
>
> SPW trusts the TCP IP, and the header only behind an internal proxy. The `getClientIp()` function uses `REMOTE_ADDR` if it’s already public, and accepts `X-Forwarded-For` (validated `NO_PRIV_RANGE|NO_RES_RANGE`) only when `REMOTE_ADDR` is private, that is, only behind a trusted proxy. No spoofing.
>
> DIS uses raw `REMOTE_ADDR`, and here it’s a virtue. For the anti-double-vote barrier (§12), `REMOTE_ADDR` can’t be forged at the TCP level, so the barrier holds. The downside is NAT: behind a proxy or a shared network, many users collapse onto the same IP.
>
> The lesson isn’t “always use `REMOTE_ADDR`.” It’s that the right IP depends on the abuse model. A login to be brute-forced (you want the attacker unable to change their own identity, so you distrust `X-Forwarded-For`) is the opposite problem from a public vote not to be duplicated; and yet the conclusion is the same: the client-controlled header isn’t trustworthy. That same raw `REMOTE_ADDR` is a hole in one context and a defense in the other.

---

## 7. `session_version`: Invalidating Sessions at Zero Cost

There’s a classic problem with session-based auth: how do you log out all of a user’s sessions, for example after a password reset, if you don’t keep a server-side store of the active sessions? Only SPW solves it, with a zero-cost trick: a `session_version` integer in `users`, copied into `$_SESSION` at login and compared on every protected request.

```php
// public/api/auth_helper.php:51-57 — inside Auth::check()
try {
    $stmt = $pdo->prepare("SELECT session_version FROM users WHERE id = ?");
    $stmt->execute([$_SESSION['user_id']]);
    $row = $stmt->fetch();
    if (!$row || (int)$row['session_version'] !== (int)($_SESSION['session_version'] ?? -1)) {
        session_destroy();
        http_response_code(401);
        echo json_encode(['status' => 'error', 'message' => 'Sessione scaduta. Effettua nuovamente il login.']);
        exit;
    }
} catch (PDOException $e) {
    error_log('session_version check failed: ' . $e->getMessage());
    http_response_code(401);   // ← fail-closed: on a DB error, DENY
    echo json_encode(['status' => 'error', 'message' => 'Sessione non verificabile. Riprova.']);
    exit;
}
```

You just increment `session_version` by one (the password reset does it, §8) and all the sessions with the old number become invalid on the first check. Logout-everywhere without any session store.

> [!TIP]
> **Fail-closed, not fail-open**
> The detail that sets a well-built defense apart is the `catch` branch. If the `session_version` check raises a `PDOException` (DB unreachable), SPW denies access (`401`), it doesn’t grant it. The rule: when a security check can’t be completed, the default outcome must be “denied.” SR and DIS don’t have this mechanism, and in SR a password change doesn’t log out the other sessions; in DIS, not even that.

---

## 8. Recovery and Password Reset Done Right

This is a whole section the earlier chapter didn’t have, because only SPW implements self-service password recovery. SR and DIS only have authenticated `change_password`, where you have to be inside already: a forgotten password means no way back in.

SPW’s flow has four precautions worth looking at one by one.

The first is the single-use random token, with an expiry.
```php
// public/api/auth.php:98-106
$token   = bin2hex(random_bytes(32));               // 32 random bytes
$expires = date('Y-m-d H:i:s', strtotime('+1 hour'));
$pdo->prepare("DELETE FROM password_resets WHERE user_id = ?")->execute([$user['id']]);   // invalidate the previous ones
$pdo->prepare("INSERT INTO password_resets (user_id, token, expires_at) VALUES (?, ?, ?)")
    ->execute([$user['id'], $token, $expires]);
```

The second is the link built from a canonical URL, not from `HTTP_HOST`. It’s the defense against *password-reset poisoning*: if the link in the email were built from `HTTP_HOST` (controllable with a forged `Host` header), the attacker could have the victim delivered a link pointing to their own domain and intercept the token.
```php
// public/api/auth.php:227-230
$link = SITE_URL . "/admin/reset-password/{$token}";   // SITE_URL hardcoded, never HTTP_HOST
```

The third is being enumeration-safe. The recovery request always responds with the same generic message (“if the account exists, you’ll receive an email”), whether the user exists or not, so the form can’t be used to discover which emails are registered. The same `login_attempts` counter is reused here with key namespacing (`'rec:' + sha256(IP)`), to limit recovery abuse too.

The fourth is that the reset invalidates the sessions. Applying the new password, `session_version` is incremented, and by what we saw in §7 every open session falls:
```php
// public/api/auth.php:127-149 (excerpt)
if (strlen($newPassword) < 12) { /* 400: "almeno 12 caratteri" */ }
// ... verify the token hasn't expired ...
$hash = password_hash($newPassword, PASSWORD_DEFAULT);
$pdo->prepare("UPDATE users SET password_hash = ?, session_version = session_version + 1 WHERE id = ?")
    ->execute([$hash, $reset['user_id']]);
$pdo->prepare("DELETE FROM password_resets WHERE token = ?")->execute([$token]);   // single-use token
```

> [!NOTE]
> **The schema that isn’t there.** The `password_resets` table is used everywhere in `auth.php`, but no file creates it: the migration script that generated it was deleted after running in production. The same goes for the `session_version` column, added on the fly with an idempotent `ALTER TABLE` inside `auth.php`. It’s a traceability debt: the real schema can’t be reconstructed from a single file. The theme of throwaway migrations returns in Chapter 15 (Database Evolution).

---

## 9. Default Credentials: Random, Hardcoded, Omitted

The first administrator is an often-underestimated security problem. The three sites solve it in three ways, and here a point anticipated in Chapter 5 (Backend Logic) closes.

> [!WARNING]
> **Seeding the admin: what NOT to do**
> SPW generates it randomly and prints it once. The first admin’s password is random and shown only once during setup. It’s the correct choice.
> SR hardcodes it to `runtime2026`. The maintenance file `fix_users_table.php` recreates the `admin` user with `password_hash('runtime2026', …)` if the table is empty, and that password is committed in the repo. The real mitigation is the `.htaccess`, which denies HTTP access to `fix_users_table.php` (§10); but there’s no flow that forces changing the default, and if no one uses `change_password` the admin account stays guessable.
> DIS omits it entirely. There’s no seeding: `init_db.php` elided the admin creation, and `users.php` can create users only if you’re already admin. The result: no guessable default (the upside), but the first admin lives only in the `.sqlite` file and can’t be reconstructed from the repo (the downside, with the classic chicken-and-egg problem on the first clean deploy).
> Three positions on the same scale: the random one is the most secure, the omitted one is the most spartan but not insecure, the hardcoded one is the only one that’s truly dangerous. And not because the password exists, but because nothing forces you to change it.

---

## 10. Protecting the File-Based Database and the Maintenance Scripts

When the database is a file (`.sqlite`), or when powerful scripts live in the docroot (migrations, fixes, resets), the `.htaccess` becomes part of the security perimeter.

The first task is denying direct access to the file-based DB. DIS keeps the `.sqlite` in a `.data/` folder generated at runtime and protected:
```apache
# DIS: deny of the data and backup files
<FilesMatch "\.(sqlite|bak)$">
    Require all denied
</FilesMatch>
```
The base rule is the one the chapter already taught (files outside the public root, or `Require all denied` plus unpredictable names). What’s new is that DIS pairs it with a `.data/` folder created at runtime by the bootstrap, which we discuss in Chapter 5.

The second task is denying the maintenance scripts, and this is where SR has the most interesting `.htaccess` of the three, because it blocks a whole family of files by prefix, before PHP even sees them:
```apache
# public/.htaccess:80-81 (SR)
<FilesMatch "^(debug_|test_|emergency_|migrate_|fix_|init_|rebuild_|setup_|optimize_)">
    Order allow,deny
    Deny from all
</FilesMatch>
# also blocks the typical scanner URLs, before PHP
RewriteRule ^(wp-|wordpress|xmlrpc|\.env|\.git|cgi-bin|phpmyadmin) - [R=404,L]
```
It’s this deny that makes the `fix_users_table.php` with the `runtime2026` password from §9 non-executable via the browser.

The third task concerns uploads. If an attacker manages to upload a `.php`, execution has to be turned off at the folder level, as SPW does:
```apache
# public/uploads/.htaccess (SPW)
<IfModule mod_php.c>
  php_flag engine off
</IfModule>
<FilesMatch "\.(php|phtml|php[0-9]|phps|cgi|pl|py|sh)$">
  Require all denied
</FilesMatch>
```

> [!WARNING]
> **The deny that’s missing where it’s needed most**
> Be careful not to read these rules as a uniform checklist: the coverage is uneven. SR has the most sophisticated by-prefix deny of the three, but it doesn’t have an `uploads/.htaccess` that turns PHP off in the upload folder. DIS protects the `.sqlite` and the `.bak` files, but its `update_db_*` scripts don’t fall under any deny pattern and stay reachable. Each site bolted the door it had seen, leaving another one open. Protecting the public upload, and the abuse chain that grows out of it in DIS, is the heart of Chapter 7.

---

## 11. Errors That Speak to the User, Opaque to the Attacker

An unhandled PHP error that ends up in the output can reveal paths, queries, database structure (the so-called *path/information disclosure*). The Model’s standard: semantically correct HTTP codes, generic messages to the client, technical detail only in the log.

```php
// SPW: the detail goes in the log, not to the client
} catch (PDOException $e) {
    error_log('auth: ' . $e->getMessage());     // only here
    http_response_code(500);
    echo json_encode(['status' => 'error', 'message' => 'Errore interno. Riprova.']);
}
```

> [!WARNING]
> **Don’t send the exception back to the client**
> DIS does the opposite: `auth.php`, `users.php`, and `participants.php` send `$e->getMessage()` straight back to the client.
> ```php
> // DIS auth.php:48 (anti-pattern)
> } catch (PDOException $e) {
>     echo json_encode(['status' => 'error', 'message' => $e->getMessage()]);   // leaks DB details
> }
> ```
> It’s information disclosure for free: an attacker reads table and column names from the error messages. The rule “speak to the user, opaque to the attacker” costs nothing; you just have to not skip it.

---

## 12. Destructive and Public Actions

The last front is the slipperiest: what happens when an action is protected by login but also destructive, or is public (no login) yet still has to defend itself from abuse.

### 12.1 The One-Click Reset: Why “Gated” Isn’t Enough

In DIS the `reset_system.php` and `reset_votes.php` endpoints require admin login but have no CSRF. A cross-site `POST` to `reset_system.php`, triggered while the admin is logged in on another tab, deletes all the participants, the votes, and the audio. The only mitigation is the cookie’s default `SameSite` (not set, as we saw in §4), which depends on the PHP version and doesn’t cover every case.

> [!WARNING]
> **Why a gated action still needs CSRF**
> “It’s protected by login” and “it’s protected by CSRF” are different guarantees. Login says who you are; CSRF says whether it was actually you who wanted it. A destructive action needs both: without CSRF, it’s the admin’s legitimate session being used against him. And a JavaScript `confirm` (“are you sure?”) doesn’t replace CSRF, because it runs on the client and the attacker skips it.

### 12.2 The Just-in-Time Backup: the Defense DIS Has and SR Doesn’t

And here comes the surprise that breaks the scale. The same DIS that has no CSRF on the reset does something the incident flagship, SR, doesn’t: it copies the database before touching it.

```php
// public/api/reset_votes.php:18-21 — backup before the destructive op
$dbPath = __DIR__ . '/.data/database.sqlite';
if (file_exists($dbPath)) {
    copy($dbPath, __DIR__ . '/.data/backup_votes_' . date('Ymd_His') . '.sqlite.bak');
}
$pdo->exec("DELETE FROM votes");
```

It’s exactly the prevention SR was missing (in Chapter 15 we call it “treatment without prevention”): the site weakest on identity is the only one to do the just-in-time backup right. More secure doesn’t mean more complete on every point.

### 12.3 Anti-Fraud for a Public Action, and Privacy

The festival vote is an action that isn’t authenticated: it’s the public that votes. DIS defends it in layers, with a single real barrier, the `REMOTE_ADDR`/24h one seen in the IP box of §6. The full treatment of vote anti-fraud (master switch, cosmetic cookie, denormalized `vote_count`) lives in Chapter 18; here only one cross-cutting point matters: how you preserve the identity of whoever performs a public action.

> [!TIP]
> **Voting anonymously: a hash instead of a cleartext IP** *(bridge to Chapter 20)*
> DIS saves `ip_address` and `user_agent` in cleartext in the `votes` table. It works for anti-double-vote, but it stores personal data without need. SPW, for the anonymous reactions (Chapter 20), gets the same anti-fraud guarantee by storing only `voter_hash = SHA256(IP + UA)`: the comparison holds, but the personal data is never written.
> Two opposite privacy postures on the same functional need. Note, though, that SPW’s hash isn’t salted and uses low-entropy input (IP and UA): it’s anti-collision, not strong cryptographic anonymity, because a candidate IP can still be verified by brute force. The full comparison between the two philosophies (write-time vs. render-time sanitization, and anonymous identity) is in Chapter 20.

On the anti-abuse side, there’s one last detail: the same SPW `login_attempts` is reused as a two-layer rate limit for the reactions (per-hash 20/min plus IP-only 30/min): the first layer is sidestepped by rotating the User-Agent, the second is the real bulwark. Here too the detail is in Chapter 20.

---

## 13. The Client Side and a Lesson About Bots

The Admin area in React is protected by an `AdminLayout` that, in its main `useEffect`, queries `check_auth`: if the server responds `401`, the client destroys the local state and redirects to login, so it doesn’t flash sensitive content. The sidebar and the routes are generated from the `role` received from the server (admin vs. editor in SR and DIS).

> [!NOTE]
> **The client isn’t the defense.** Client-side logout and the `401` check are user experience, not security: they hide what you shouldn’t see, but it’s the server-side gate (§2) that keeps you from touching it. The difference between “logout on the client” and real invalidation via `session_version` (§7) is exactly this. The full architecture of the admin panel (the three dashboards, the three guard architectures, the placement of the backups) is in Chapter 14.

There’s finally a lesson that comes from a real incident and stays relevant here, even though the full case has migrated elsewhere. In February 2026 Runtime Radio was swamped by bots that mimicked the social crawlers (Telegram, Facebook, X) to hit the PHP SEO entry point, which queried the database on every request. The bots’ User-Agent is forgeable.

> [!WARNING]
> **The User-Agent isn’t a gatekeeper**
> You never make security decisions based on the User-Agent, because it’s forged in a header field. You can use it to optimize (serving a cache to recognized bots), never as an access barrier. The full account of the bot-DDoS attack and the solution (a precompiled static cache, a bot path separate from the human one) is in Chapter 11, because the vector is precisely the SEO entry point. Here only the maxim remains.

---

## In Summary

Security is the lens that disproves the intuition that “bigger equals sturdier.” SPW, which isn’t the most engineered site, has the most mature perimeter. SR, the richest, leaves three real holes: a cookie without `Secure`, no anti-fixation, a rate limit that can be sidestepped. DIS, the base rung, still brings two ideas the others lack: robust public anti-fraud and the pre-destructive backup. Read as a scale of subtraction, every defense teaches two things at once: what it does, and what breaks when you remove it.

> [!IMPORTANT]
> **The Canon**
> - Sessions with `HttpOnly` + `SameSite=Strict` + `Secure` cookies over HTTPS; passwords with `password_hash()`.
> - A CSRF token on all mutations: a `confirm()` isn’t a CSRF defense.
> - Authorization by **role** (`isAdmin`), not just by login (`isLoggedIn`).
> - Brute-force lockout measured on a trustworthy IP, not on client-controlled headers (`X-Forwarded-For`).
> - `session_version` to invalidate sessions on a password change; no default credentials in the code.

---
*Next Chapter: SEO Pre-rendering with a PHP Entry Point. The invisible SEO engine that turns a SPA into an indexable site, and the vector of the February 2026 bot-DDoS attack.*
