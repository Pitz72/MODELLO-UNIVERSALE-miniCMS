# CHAPTER 5: Backend Logic (PHP)

The miniCMS backend is the engine that processes the data and stands guard. This chapter defines what an endpoint is made of, how it starts up, and how it handles identifiers, the time zone, and errors. The through-line is always the same: no framework, one PHP file per responsibility, and three ways of shaping the same skeleton depending on how much the site has chosen to engineer.

## 1. Identifier Handling (Slugs)

URLs have to be readable and unique. The Model generates the slug on the server and guarantees its uniqueness against collisions.

### 1.1 Base algorithm
```php
function createSlug($string) {
    // lowercase, trim, and strip non-alphanumeric characters (except the hyphen)
    return strtolower(trim(preg_replace('/[^A-Za-z0-9-]+/', '-', $string)));
}
```

### 1.2 Advanced algorithm (normalizing Italian accents)

The base pattern produces malformed slugs for accented words (`caffè` becomes `caff-`). The **SimonePizziWebSite** variant solves it with an explicit map before the cleanup:

```php
function generateSlug($title, $pdo) {
    $accents      = ['à','è','é','ì','ò','ù','À','È','É','Ì','Ò','Ù','â','ê','î','ô','û','ä','ë','ï','ö','ü'];
    $replacements = ['a','e','e','i','o','u','a','e','e','i','o','u','a','e','i','o','u','a','e','i','o','u'];
    $title = str_replace($accents, $replacements, $title);
    $slug  = strtolower(trim(preg_replace('/[^A-Za-z0-9-]+/', '-', $title)));

    // anti-collision: if the slug already exists, append a timestamp suffix
    $stmt = $pdo->prepare("SELECT COUNT(*) FROM articles WHERE slug = ?");
    $stmt->execute([$slug]);
    if ($stmt->fetchColumn() > 0) $slug .= '-' . time();
    return $slug;
}
```

For sites with Italian content, always use the advanced pattern. (The three slug philosophies across the sites, accents kept or stripped, are detailed in Chapter 9.)

## 2. Time Zone Handling

On international hosting (a server in Los Angeles, say), `date()` and `time()` use the server’s time zone, and that breaks the `published_at <= NOW` visibility logic, which for an Italian site has to reason in Italian time.

```php
// at the start of every endpoint with time logic
date_default_timezone_set('Europe/Rome');
$ita_now_str = date('Y-m-d H:i:s');   // Italian time for the SQL comparisons
```

The rule is simple, applying it isn’t. SimonePizziWebSite forces the time zone in **every** endpoint; SitoRuntime and DISINTELLIGENZA do it only in some (`index.php`, `news.php`), and not elsewhere. The result is a publication threshold that shifts depending on which file evaluates it.

> [!WARNING]
> **Force the time zone everywhere, or it’s useless**
> Forcing the time zone in a single endpoint gives a false sense of safety: a scheduled article can read as already published to one file and still in the future to another, because the same `published_at` string is compared against a `NOW` computed in different zones. SitoRuntime carries the scar of this in a `debug_time.php` that documents an incident over the date separator (the space turning into a `T`). The logic of comparing dates, and the three ways to get it wrong, is in Chapter 9; here the bootstrap rule is enough: if you force the time zone, do it in the shared prelude, not endpoint by endpoint.

## 3. Anatomy of an Endpoint: the Router on `REQUEST_METHOD`

There’s no central router. Every file in `public/api/` is a standalone endpoint, and it dispatches on its own based on the request’s HTTP verb. It’s the pattern that makes the thin stack readable: the URL `/api/articles.php` is the file `articles.php`, and inside that file is everything that concerns it.

```php
$method = $_SERVER['REQUEST_METHOD'];

if      ($method === 'GET')    { /* read: page, limit, slug, id, category, admin */ }
elseif  ($method === 'POST')   { Auth::check(); /* create */ }
elseif  ($method === 'PUT')    { Auth::check(); /* full replacement */ }
elseif  ($method === 'PATCH')  { Auth::check(); /* partial update: toggle is_visible, sort_order */ }
elseif  ($method === 'DELETE') { Auth::check(); /* delete */ }
```

The gate isn’t uniform across the file but **selective per branch**: the read `GET` stays public, and the branches that mutate state go through `Auth::check()`. In the older projects (DISINTELLIGENZA, SitoRuntime before the refactor), the mutations all traveled as `POST` with an `action` field in the body; the pattern with separate verbs is more readable and pairs better with an expressive TypeScript client.

## 4. The Three Bootstrap Styles

Before dispatching the request, an endpoint has to start up: open the connection, start the session, send the headers, handle the CORS preflight if there is one. Here the three sites occupy three rungs, and it’s a good portrait of the scale from Chapter 1.

**SimonePizziWebSite: inline prelude.** Every file includes its building blocks at the top (`require 'db.php'`, `require 'auth_helper.php'`, the headers) and opens the connection right away. The `auth_helper.php` wraps `session_start()`, the `Content-Type`, and the `Auth` class:

```php
// auth_helper.php — session, headers, and Auth in a single include
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

Concentrating `session_start()` and `header()` in a single file reduces the risk of “headers already sent” from stray spaces or BOMs scattered across files.

**SitoRuntime: shared `cors.php` prelude.** The site serves a frontend that in development comes from a different origin, so it puts a `cors.php` ahead of everything to handle headers, the `Content-Type`, and the `OPTIONS` preflight, then opens the connection lazily (`getDB()` with a `static`, copied into every file). The actual CORS is **not** open to everyone: it’s an allowlist of known origins, reflecting the `Origin` when it’s allowed.

```php
// cors.php — shared prelude: an allowlist, not "*"; answers the preflight and exits
$allowed = ['https://runtimeradio.com', 'https://www.runtimeradio.com', 'https://runtimeradio.it'];
$origin  = $_SERVER['HTTP_ORIGIN'] ?? '';
if (in_array($origin, $allowed, true)) {
    header("Access-Control-Allow-Origin: $origin");
    header('Vary: Origin');
}
header('Content-Type: application/json');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }
```

**DISINTELLIGENZA: minimal inline, no CORS.** It develops and ships same-origin, so it has no need for CORS headers: the `.htaccess` ensures the frontend and the API sit on the same origin, and the session cookie travels on its own. The bootstrap is pared to the bone.

> [!NOTE]
> **`Access-Control-Allow-Origin: *` almost never**
> The asterisk is fine only for a public, read-only API with no cookies. The moment there’s a session, reflecting an allowlist of origins is the right choice, and it has to come with an explicit decision about `Access-Control-Allow-Credentials` (SitoRuntime doesn’t emit it, and as a result authentication stays de facto same-origin: the detail, with its effect on the client, is in Chapters 6 and 10).

### The connection error: three responses

What happens when the database doesn’t answer is a small maturity test, and the three sites pass it differently.

```php
// SPW: correct HTTP code + JSON + log for diagnosis
catch (PDOException $e) {
    http_response_code(500);
    error_log('DB: ' . $e->getMessage());                 // stays in the logs, never goes to the client
    echo json_encode(['status' => 'error', 'message' => 'Database non disponibile']);
    exit;
}
```

SimonePizziWebSite answers `500`, in JSON, and writes the exception to the server logs. SitoRuntime answers `503` in JSON but **doesn’t log**, and so it loses the diagnostics exactly when they’d be useful. DISINTELLIGENZA does the thing you shouldn’t: `die("Connection failed: " . $e->getMessage())`, which prints the exception message (paths included) to the client, with no HTTP code and outside the JSON format.

> [!WARNING]
> **A connection error must never speak to the client**
> A `PDOException` message can contain filesystem paths, database names, details that come in handy to an attacker. The rule: the correct HTTP code (`500` or `503`), a generic message to the client, and the real detail only in the server logs via `error_log()`. Printing `$e->getMessage()` to the page, the way DISINTELLIGENZA does, is information disclosure for free.

## 5. Media Processing

Uploading a file isn’t a simple `move_uploaded_file`, it’s a transformation. The upload’s `type` maps to different folders, each with its own policy: images are public and resized, podcast audio goes through admin only, and participant audio goes to an isolated folder that (in the festival’s case) is openly accessible. Every admin image is normalized to a maximum width (1920px), preserving the alpha channel of PNG and WebP. The full treatment, including the security pitfalls of uploads (validating the real bytes, the naming, the RCE chain of the public upload), is in Chapter 7: here it’s enough to know that the file passes through GD before it lands on disk.

## 6. Input and Output Security

- **File names**: every upload is renamed with `uniqid()` and cleaned of special characters, so the user doesn’t get control over the name (and therefore the extension). The why is in Chapter 7.
- **JSON integrity**: every response is preceded by `header('Content-Type: application/json')`, and on an error it carries the right HTTP code (`400`, `401`, `403`, `500`) along with a descriptive JSON message.
- **`FILTER_SANITIZE_STRING` is deprecated** (as of PHP 8.1): in its place, `strip_tags(trim($var))`.

## 7. Buffer Handling

A PHP `Notice` or `Warning` printed in the middle of a response makes it invalid JSON, and the frontend breaks. The defense is twofold: `display_errors = 0` in production (errors go to the logs, not the page) and, where needed, `ob_start()` to control what goes out. It’s the same principle as the connection error in §4: the client gets clean data, the diagnostics stay on the server.

> [!IMPORTANT]
> **The Canon**
> - One file per endpoint with a router on `REQUEST_METHOD`; a gate that’s selective per branch (public GET, mutations behind `Auth::check`).
> - CORS via an allowlist of origins with `Vary`, never `*` together with credentials.
> - A connection error is written to the logs and answers the client generically: never `getMessage()` in cleartext.
> - Force the time zone in **every** endpoint with time logic, and in production `display_errors = 0`.

---
*Next Chapter: Frontend Bridge (API.ts). The connection between React and PHP, and the three ways to read a payload that has no stable contract.*
