# Mappatura — SitoRuntime — C2: Security & Auth (+ CORS)

> **Stato:** COMPLETATO
> **Sessione:** 13 · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `SitoRuntime/`)
> - `public/api/cors.php` (prelude CORS condiviso: allowlist origini, header, short-circuit `OPTIONS`)
> - `public/api/auth_utils.php` (sessione + `isLoggedIn`/`isAdmin` + CSRF a token `generateCsrfToken`/`validateCsrf`)
> - `public/api/admin.php` (endpoint di login/logout/check_auth/change_password + gestione utenti + rate-limiting file-based)
> - `public/api/fix_users_table.php` (manutenzione tabella `users` — fossile SQLite, ricrea admin di default)
> - `public/.htaccess` (security headers HSTS/CSP/X-Frame, deny file sensibili, deny script di manutenzione, rewrite)
> - `public/api/.cache/.htaccess` + `public/api/lib/.htaccess` (`Deny from all`)
> - Consumatori del gate (per la mappa di copertura, non per la loro logica):
>   `public/api/upload.php:8,13` · `newsletter.php:177,211…295` · `podcasts.php:42,43,101,102` ·
>   `speakers.php:124,125,186,187` · `feed_config.php:8`

## 1. Cosa fa (sintesi narrativa)

Il perimetro di sicurezza di SitoRuntime è — come in SimonePizziWebSite — **PHP nativo senza
framework** (`session_*`, `password_*`, `random_bytes`, `hash_equals`) più regole Apache nei
`.htaccess`. Ma rispetto a SPW-C2 il modello **diverge su quasi ogni asse implementativo**, pur
condividendo la stessa filosofia thin-stack. È la prima e più importante osservazione della card:
SitoRuntime adotta una **CSRF a token esplicito** (sincronizzato per sessione) dove SPW usa il
controllo `Origin`/`Referer`, e una **CORS realmente attiva** (allowlist multi-dominio) dove SPW
resta same-origin.

Tre file portano il peso, ma in modo molto più frammentato che in SPW (dove c'erano i due file
canonici `auth.php` + `auth_helper.php`):

- **`auth_utils.php`** è il **prelude di sessione condiviso**: incluso subito dopo `cors.php` in ogni
  endpoint, apre la sessione PHP con i flag cookie (`HttpOnly`, `SameSite=Strict`, lifetime 1h) e
  offre quattro funzioni-mattone: `isLoggedIn()`, `isAdmin()` (gate a ruoli), `generateCsrfToken()`
  (token a 32 byte memoizzato in `$_SESSION['csrf_token']`) e `validateCsrf()` (confronto
  `hash_equals` tra `$_SESSION['csrf_token']` e l'header `X-CSRF-Token`). **Non** esiste un singolo
  `Auth::check()` onnicomprensivo come in SPW: il gate è composto a mano in ogni endpoint come
  `if (!isLoggedIn()/!isAdmin()) …; validateCsrf();`.
- **`admin.php`** è l'**endpoint di autenticazione e gestione admin** (uno script `?action=` che
  scorre i rami dall'alto al basso, ognuno termina con `exit`). Contiene login, logout, check_auth,
  change_password, e la gestione utenti (list/create/delete con gate a ruolo `admin`). Il login fa
  `password_verify`, e in caso di successo popola `$_SESSION['user_id']`/`['role']` e **restituisce
  il token CSRF nel body**. La protezione brute-force è **file-based** (non DB): un JSON per IP in
  `.cache/ratelimit/`, 5 tentativi / 15 minuti.
- **`cors.php`** (già visto in SR-C1 come prelude di bootstrap) è il punto unico di policy CORS:
  **allowlist statica di 4 origini** (`runtimeradio.com`/`.it` + `www`), riflessione condizionale
  dell'`Origin`, `Vary: Origin`, dichiarazione di `X-CSRF-Token` tra gli header consentiti, e
  short-circuit del preflight `OPTIONS` con `204`.

Il modello di sessione è cookie-based ma **più debole di SPW su due punti critici** (vedi §4):
manca il flag `Secure` sul cookie e manca `session_regenerate_id()` dopo il login (niente difesa
anti session-fixation). Non esiste alcun flusso di **recovery/reset password** pubblico (solo
`change_password` autenticato), né un meccanismo `session_version` per l'invalidazione globale.

## 2. Pattern miniCMS rilevanti

- **Prelude di sicurezza in due include** (`cors.php` + `auth_utils.php`): ogni endpoint apre con
  questi due `require_once`. `cors.php` decide la policy di rete (CORS/preflight), `auth_utils.php`
  apre la sessione e mette a disposizione i mattoni auth/CSRF. È la fattorizzazione che SPW NON ha
  (lì i flag cookie stavano dentro `auth_helper.php`/`auth.php`).
- **Gate "componibile" a due funzioni invece del middleware unico.** Dove SPW ha la riga unica
  `Auth::check()` (sessione + CSRF + session_version insieme), SitoRuntime separa **autorizzazione**
  (`isLoggedIn()`/`isAdmin()`) da **anti-CSRF** (`validateCsrf()`), chiamate esplicitamente e
  **in ordine** in ogni ramo mutativo. Più flessibile (gate a ruolo gratuito), ma **più facile da
  dimenticare**: la protezione dipende dalla disciplina del singolo endpoint.
- **CSRF synchronizer token pattern** (`auth_utils.php:20-35`): token random per sessione, esposto
  al client nel body di login/check_auth, rispedito dal client nell'header `X-CSRF-Token`, validato
  con `hash_equals` (timing-safe). È la **divergenza forte** da SPW (Origin/Referer). Vedi §3/§6.
- **Autorizzazione a ruoli** (`role` in `$_SESSION`): `admin` vs `editor`. `isAdmin()` e i controlli
  `$_SESSION['role'] !== 'admin'` separano le azioni di gestione utenti dalle azioni di contenuto.
  SPW ha un solo livello (loggato = admin); qui c'è una gerarchia.
- **Rate-limiting brute-force file-based** (`admin.php:62-101`): un file `.cache/ratelimit/<md5(ip)>.json`
  con `{attempts, first_attempt}`, finestra 900s, soglia 5. È l'equivalente della tabella
  `login_attempts` di SPW ma **senza DB** — coerente con l'osservazione di SR-C1 che lo schema MySQL
  non contiene `login_attempts`. Aggiunto `sleep(1)` su fallimento/lockout (anti-enumeration timing).
- **Hardening HTTP centralizzato in `public/.htaccess`**: HSTS (1 anno, `includeSubDomains`), CSP
  ricca (con `frame-src` YouTube e `frame-ancestors 'none'`), `X-Frame-Options: DENY`, `nosniff`,
  `Referrer-Policy`, `Permissions-Policy`; deny dei file sensibili (`.env`/`.sqlite`/`.log`) e —
  pattern assente in SPW — **deny by-prefix di tutti gli script di manutenzione** (`debug_`,
  `migrate_`, `fix_`, `init_`, `setup_`, `optimize_`, `rebuild_`, `test_`, `emergency_`).
- **Difesa "JSON-first" anche sugli errori di sicurezza**: `403` token CSRF non valido, `401`
  unauthorized, `429` rate limit, sempre come `{success:false, error:…}`.

## 3. Codice chiave (stralci con origine)

**Sessione + CSRF a token (synchronizer pattern)** — `public/api/auth_utils.php:4-35`:

```php
if (session_status() === PHP_SESSION_NONE) {
    ini_set('session.gc_maxlifetime', 3600);
    ini_set('session.cookie_lifetime', 3600);
    ini_set('session.cookie_httponly', '1');
    ini_set('session.cookie_samesite', 'Strict');
    session_start();                       // NB: manca cookie_secure (vedi §4)
}
function isLoggedIn() { return isset($_SESSION['user_id']); }
function isAdmin()    { return isLoggedIn() && ($_SESSION['role'] ?? '') === 'admin'; }

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

**Login con rate-limit file-based + ritorno token CSRF nel body** — `public/api/admin.php:105-131`:

```php
if ($action === 'login' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $ip = $_SERVER['HTTP_X_FORWARDED_FOR'] ?? $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $ip = trim(explode(',', $ip)[0]); // primo IP se dietro proxy  ← spoofabile (§4)

    if (!checkRateLimit($ip)) { sleep(1); sendError('Troppi tentativi. Riprova tra 15 minuti.', 429); }

    $stmt = getDB()->prepare("SELECT * FROM users WHERE username = ?");
    $stmt->execute([$input['username'] ?? '']);
    $user = $stmt->fetch();

    if ($user && password_verify($input['password'] ?? '', $user['password_hash'])) {
        clearRateLimit($ip);
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['role']    = $user['role'];     // NB: NON salva 'username' (§4)
        sendSuccess(['message' => 'Login successful', 'csrf_token' => generateCsrfToken(),
                     'user' => ['username' => $user['username'], 'role' => $user['role']]]);
    } else {
        recordFailedAttempt($ip); sleep(1); sendError('Invalid credentials', 401);
    }
}
```

**Rate-limiting su file system (niente tabella `login_attempts`)** — `public/api/admin.php:62-96`:

```php
function getRateLimitFile($ip) {
    $dir = __DIR__ . '/.cache/ratelimit';
    if (!is_dir($dir)) mkdir($dir, 0755, true);
    return $dir . '/' . md5($ip) . '.json';
}
function checkRateLimit($ip) {
    $file = getRateLimitFile($ip);
    if (!file_exists($file)) return true;
    $data = json_decode(file_get_contents($file), true);
    if (!$data || (time() - $data['first_attempt']) > 900) { unlink($file); return true; }
    return $data['attempts'] < 5;
}
```

**CORS allowlist multi-dominio + header CSRF + preflight** — `public/api/cors.php:5-30`:

```php
$allowedOrigins = [
    'https://runtimeradio.com', 'https://www.runtimeradio.com',
    'https://runtimeradio.it',  'https://www.runtimeradio.it',
];
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if (in_array($origin, $allowedOrigins, true)) {
    header("Access-Control-Allow-Origin: $origin");
    header("Vary: Origin");
}                                  // origine non in lista → nessun header → il browser blocca
header("Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, X-CSRF-Token");
header('Content-Type: application/json');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit(0); }
```

**Gate componibile nel consumatore tipico** — `public/api/upload.php:8-13` (stesso schema in
`speakers.php`, `podcasts.php`, `newsletter.php`, `feed_config.php`):

```php
if (!isLoggedIn()) { http_response_code(401); echo json_encode([...]); exit; }
// ...
validateCsrf();
```

**Hardening HTTP + deny degli script di manutenzione** — `public/.htaccess:4-35,80-81`:

```apache
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
Header always set X-Frame-Options "DENY"
Header always set Content-Security-Policy "default-src 'self'; script-src 'self'; ...
    frame-src https://www.youtube.com https://www.youtube-nocookie.com;
    frame-ancestors 'none'; base-uri 'self'; form-action 'self';"
# Blocca per PREFISSO tutti gli script potenti raggiungibili via HTTP
<FilesMatch "^(debug_|test_|emergency_|migrate_|fix_|init_|rebuild_|setup_|optimize_)">
    Order allow,deny
    Deny from all
</FilesMatch>
# Blocca URL tipici di scanner PRIMA di PHP
RewriteRule ^(wp-|wordpress|xmlrpc|\.env|\.git|cgi-bin|phpmyadmin) - [R=404,L]
```

## 4. Problemi riscontrati & soluzioni

- **Cookie di sessione SENZA flag `Secure` — GOLD sicurezza (divergenza da SPW).**
  `auth_utils.php:7-8` imposta `cookie_httponly` e `cookie_samesite=Strict` ma **non**
  `session.cookie_secure`. Il cookie di sessione può quindi viaggiare anche su HTTP. Aggravante:
  il `.htaccess` (vedi sotto) **non forza il redirect a HTTPS**, applica solo HSTS — che protegge
  solo *dopo* la prima visita HTTPS riuscita. SPW invece imposta `cookie_secure=1` **e** forza il
  301 a HTTPS. → Box "i tre flag del cookie: cosa succede se ne dimentichi uno" (alto valore,
  parallelo diretto alla regressione cookie-debole di SPW v1.18→v1.19).
- **Nessuna difesa anti session-fixation — GOLD (divergenza da SPW).** Dopo il login riuscito
  (`admin.php:121-125`) la sessione **non** viene rigenerata: manca `session_regenerate_id(true)`
  che SPW chiama esplicitamente. Un ID di sessione fissato prima del login resta valido dopo. →
  Aggancia il box "anti session-fixation: una riga che spesso manca".
- **Rate-limit brute-force aggirabile via header `X-Forwarded-For` — GOLD (divergenza forte da SPW).**
  `admin.php:106-107` prende l'IP da `HTTP_X_FORWARDED_FOR` **per primo e senza validazione**
  (`$ip = $_SERVER['HTTP_X_FORWARDED_FOR'] ?? $_SERVER['REMOTE_ADDR']`). Poiché quell'header è
  controllato dal client, un attaccante può variarlo a ogni richiesta e azzerare il contatore →
  il lockout 5/15min è bypassabile. SPW risolve esattamente questo con `getClientIp()`, che si fida
  di `REMOTE_ADDR` se pubblico e valida `X-Forwarded-For` solo dietro proxy interno. → Box
  "fidarsi dell'IP del client: il rate-limit che non limita" (contrappunto a SPW-C2).
- **Niente flusso di recovery/reset password — solo `change_password` autenticato.**
  `admin.php:151-172` permette il cambio password solo a sessione attiva (verifica vecchia password
  + CSRF). **Non** esiste `request-recovery`/`reset-password` con token via email, né tabella
  `password_resets`, né `session_version` per invalidare le sessioni dopo il cambio. Conseguenza:
  password dimenticata = nessun self-service; e un cambio password **non** disconnette le altre
  sessioni (SPW sì, via `session_version + 1`). → Nota: il modello di account di SitoRuntime è più
  semplice (multi-utente con ruoli ma senza ciclo di vita password completo).
- **Password admin di default `runtime2026` ancora viva e ricreabile — GOLD (ponte da SR-C1 §4).**
  `fix_users_table.php:54-60` ricrea l'utente `admin` con `password_hash('runtime2026', …)` se la
  tabella è vuota — la stessa credenziale hardcoded già emersa in `init_db.php` (SR-C1). Mitigazione
  reale: il `.htaccess` (`FilesMatch ^fix_`) **nega l'accesso HTTP** a `fix_users_table.php`, quindi
  non è eseguibile dal browser in produzione (a differenza di quanto temuto in SR-C1, qui c'è una
  rete di sicurezza). Resta il fatto che **non esiste alcun flusso che obblighi a cambiare la
  password di default**: se nessuno ha usato `change_password`, l'account admin è indovinabile.
- **`fix_users_table.php` è un fossile SQLite — GOLD (terzo fossile cross-confermato).** Usa
  `sqlite_master` e `PRAGMA table_info(users)` (`:12,20`): scritto per SQLite, **fallirebbe su
  MySQL** (la produzione attuale). È il terzo script "fossilizzato dopo la migrazione di motore"
  dello stesso sito (dopo `init_db.php` e l'init SQLite di SR-C1). Rafforza la lezione cross-sito:
  dopo una migrazione di motore gli script di manutenzione vanno riscritti o rimossi. (storia
  migratoria completa → C13).
- **Niente redirect HTTPS forzato nel `.htaccess`.** `public/.htaccess` imposta HSTS ma — a
  differenza di SPW (`RewriteCond %{HTTPS} !=on → 301`) — **non** ha la regola di redirect a HTTPS.
  Con il cookie privo di `Secure`, la finestra di esposizione su HTTP è reale al primo accesso. →
  collegato al primo punto.
- **`username` mai salvato in sessione (bug minore, ricaduta su attribuzione/UX).** Il login salva
  `user_id` e `role` ma **non** `$_SESSION['username']` (`admin.php:123-124`). Però `check_auth`
  (`:135-139`) ed il salvataggio articolo (`:284`, `author = $_SESSION['username'] ?? 'Admin'`) lo
  leggono: `check_auth` restituisce `username: null` e l'autore degli articoli è sempre `'Admin'`.
  Non è un buco di sicurezza, ma una incoerenza di stato di sessione. → Nota.
- **CORS senza `Access-Control-Allow-Credentials` su auth cookie-based (sottigliezza).** `cors.php`
  riflette l'`Origin` ammesso ma **non** emette `Access-Control-Allow-Credentials: true`. Poiché
  l'autenticazione è basata su cookie di sessione, una richiesta **cross-origin con credenziali**
  da una delle origini in allowlist verrebbe comunque bloccata dal browser (cookie non inviato/
  risposta non leggibile). In pratica la CORS aperta serve solo le **letture pubbliche non
  autenticate** dal dominio alternativo (`.it` ↔ `.com`); le operazioni admin restano de facto
  same-origin. → Nota didattica: "Allow-Origin senza Allow-Credentials non abilita le sessioni
  cross-site" (specularità inversa rispetto alla nota CORS di SPW-C2).
- **Azioni admin con gate per-ramo: rischio di dimenticanza strutturale.** Il gate è ricostruito in
  ogni ramo (`if (!isLoggedIn())…; validateCsrf();`). Le azioni di contenuto (`save`/`delete`) sono
  protette dal blocco `if (!isLoggedIn()) sendError(401)` a `admin.php:231` **più** `validateCsrf()`
  locale; ma `list_users`/`create_user`/`delete_user` (`:176,188,215`) stanno **prima** di quel
  blocco e si autoproteggono solo con `$_SESSION['role'] !== 'admin'`. Funziona (role assente →
  Forbidden), ma la sicurezza dipende dall'ordine dei rami e dalla disciplina, non da un gate unico.
  → Contrasto col middleware `Auth::check()` di SPW: un punto unico vs N punti da non scordare.

## 5. Estetica / UX (moderna ma funzionale)

- **Contratto di risposta uniforme** `{success:bool, …}` / `{success:false, error}` su tutti i rami,
  con codici HTTP semanticamente corretti (`401`/`403`/`429`/`404`/`500`): il frontend può reagire
  per codice. Messaggi utente in italiano e parlanti ("Token di sicurezza non valido. Ricarica la
  pagina.", "Troppi tentativi. Riprova tra 15 minuti.").
- **Token CSRF restituito esplicitamente** a login e check_auth: l'handshake è trasparente per il
  client (riceve il token, lo rispedisce nell'header), un'esperienza di integrazione pulita.
- **`sleep(1)` sui fallimenti di login**: piccolo accorgimento UX-di-sicurezza (rallenta enumerazione
  e brute-force senza messaggi diversi tra "utente inesistente" e "password errata" — entrambi
  `Invalid credentials`).
- **Diagnostica admin curata** (`action=test_smtp`, `apply_v29x_*`): output JSON ricco per il
  pannello admin, gated dietro login/ruolo. (la logica è C9/C12/C13 — qui solo notato che è gated).

## 6. Differenze rispetto agli altri siti

Il confronto con **SPW-C2** è il cuore di questa card: stessa filosofia (PHP nativo, sessione
cookie, niente librerie auth), **implementazione divergente su quasi tutto**.

| Aspetto | SimonePizziWebSite (SPW-C2) | SitoRuntime (questa card) |
|---|---|---|
| **Anti-CSRF** | controllo `Origin`/`Referer` vs `SITE_URL` (in `Auth::check`) | **token sincronizzato**: `generateCsrfToken` + header `X-CSRF-Token`, `hash_equals` |
| **Gate auth** | **unico** `Auth::check()` (sessione+CSRF+session_version) | **componibile**: `isLoggedIn()`/`isAdmin()` + `validateCsrf()` per-ramo |
| **Ruoli** | uno solo (loggato = admin) | **`admin` vs `editor`** (`isAdmin`, `role` in sessione) |
| **Cookie `Secure`** | **sì** (`cookie_secure=1`) | **NO** (solo HttpOnly + SameSite=Strict) |
| **Anti session-fixation** | **sì** (`session_regenerate_id(true)`) | **NO** (nessuna rigenerazione al login) |
| **`session_version` (logout-everywhere)** | **sì**, fail-closed sul DB | **assente** |
| **Recovery/reset password** | completo (token, scadenza 1h, email canonica, enumeration-safe) | **assente**: solo `change_password` autenticato |
| **Rate-limit brute force** | tabella **DB** `login_attempts` (riusata login+recovery, namespacing) | **file system** `.cache/ratelimit/<md5(ip)>.json`, 5/15min + `sleep(1)` |
| **IP del client** | `getClientIp()` anti-spoof (XFF validato solo dietro proxy) | **`X-Forwarded-For` grezzo e per primo → spoofabile** |
| **CORS** | chiusa, same-origin (`connect-src 'self'`); `Allow-Methods` cosmetico | **aperta**: allowlist 4 origini, riflessione `Origin`+`Vary`, preflight 204 |
| **`Allow-Credentials`** | n/a (CORS chiusa) | **non impostato** (auth cookie cross-origin di fatto non abilitata) |
| **HTTPS forzato** | **sì** (`RewriteCond %{HTTPS} !=on` → 301) + HSTS | **solo HSTS**, nessun redirect 301 |
| **CSP** | restrittiva, `connect-src 'self'` | restrittiva ma `connect-src 'self' https:`; `frame-ancestors 'none'`; `frame-src` YouTube |
| **PHP-off negli upload** | sì (`uploads/.htaccess` php_flag engine off) | **non rilevato** un `uploads/.htaccess` (→ verificare in C5) |
| **Deny script manutenzione** | non per-prefisso | **sì**, `<FilesMatch ^(debug_|migrate_|fix_|init_|…)>` Deny |

Sintesi: SPW è **più maturo sul ciclo di vita dell'identità** (Secure cookie + anti-fixation +
session_version + recovery password + IP anti-spoof), SitoRuntime è **più ricco sul modello di
accesso** (ruoli admin/editor, CSRF a token, CORS multi-dominio, deny by-prefix degli script).
I tre buchi più rilevanti di SR rispetto a SPW: **cookie senza `Secure` + nessun redirect HTTPS**,
**niente anti session-fixation**, **rate-limit bypassabile via `X-Forwarded-For`**.

Per DISINTELLIGENZA/FDCA (SQLite, con anti-frode voto) il confronto si farà alle rispettive card C2.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **CSRF: token sincronizzato (SR) vs check Origin/Referer (SPW)** — due scuole nel thin stack | Cap. "CSRF nel thin stack" (arricchire con la 2ª variante a token, `hash_equals`) |
| Gate unico `Auth::check()` vs gate componibile `isLoggedIn`/`validateCsrf` per-ramo | Box "Middleware o disciplina? Due modi di proteggere un endpoint" (nuovo) |
| Autorizzazione a ruoli (`admin`/`editor`) vs single-level | Box "Ruoli minimi senza framework" |
| **I tre flag del cookie di sessione** — cosa succede se manca `Secure` (caso SR) | Box sicurezza (alto valore, parallelo alla regressione cookie SPW) |
| **Anti session-fixation: la riga `session_regenerate_id` che manca** (caso SR) | Box "Una riga che spesso si dimentica" |
| **Rate-limit bypassabile via `X-Forwarded-For`** (SR) vs `getClientIp()` (SPW) | Box "Fidarsi dell'IP: il rate-limit che non limita" (alto valore) |
| Rate-limit **file-based** (SR) vs tabella **DB** (SPW) | Box "Dove vive il contatore brute-force: file vs DB" |
| **CORS multi-dominio fatta a mano** (allowlist + riflessione + Vary + preflight) | Cap. "CORS senza librerie" (nuovo) + nota su `Allow-Credentials` |
| Hardening `.htaccess`: HSTS/CSP/headers, **deny by-prefix** degli script di manutenzione | Cap. "Hardening a livello server" (aggiungere il pattern by-prefix) |
| **HTTPS: HSTS senza redirect 301** — perché non basta | Box "HSTS non è il redirect HTTPS" |
| Password admin di default `runtime2026` + assenza di flusso che obblighi a cambiarla | Box "Credenziali di default: cosa non fare" (rafforza SR-C1) |

## 8. Note / domande aperte

- **Puntatori ad altri cluster** (annotati qui, NON mappati in questa card):
  - **PHP-off sugli upload (C5):** non ho trovato un `public/uploads/.htaccess` (la glob `**/.htaccess`
    elenca solo `public/.htaccess`, `api/.cache/.htaccess`, `api/lib/.htaccess`). La regola rewrite
    serve i file esistenti senza passare da PHP, ma **non disabilita** l'esecuzione PHP nella dir
    upload come fa SPW. **Da verificare in C5** se esiste protezione equivalente (potenziale buco).
  - **Logica contenuti/upload/newsletter in `admin.php`** (rami `save`/`delete`/`optimize_webp`/
    `apply_v29x_*`/`test_smtp`/`fix_image_paths`) → C4/C5/C9/C12/C13. Qui mappati **solo** come rami
    gated (gate auth + CSRF), non per la loro logica.
  - **`logAndSendDbError()`** in `auth_utils.php:37-41` (helper di logging errori DB) → osservabilità,
    usato dagli endpoint contenuti; qui solo notato che vive nel file auth.
  - **Migrazioni a caldo dietro `admin.php?action=apply_v29x_*`** (status, newsletter double opt-in) →
    **C13** (evoluzione DB). Qui interessa solo che sono **gated** dietro login.
  - **`fix_users_table.php`** = manutenzione schema `users` → la *storia* migratoria è C13; in C2 ho
    mappato solo il meccanismo auth (ricrea admin di default `runtime2026`, è un fossile SQLite).
  - **`feed_config.php`/`newsletter.php`/`speakers.php`/`podcasts.php`/`upload.php`** → consumatori del
    gate; logica = C4/C5/C8/C9. Qui solo la mappa di copertura del gate (§1 file ispezionati).
- **Da verificare (C13/C1):** il rate-limit scrive in `.cache/ratelimit/` con `mkdir(0755)`; la dir
  `.cache` è protetta da `RewriteRule ^api/\.cache(/.*)?$ - [F,L]` e da `.cache/.htaccess`
  (`Deny from all`) — i file di rate-limit non sono leggibili via HTTP. OK.
- **Da verificare:** non ho letto i valori del `.env` (segreti, gitignorato) — solo la *struttura*
  dei consumatori (già coperta in SR-C1).
- **Conferma cross-sito:** `fix_users_table.php` è il **terzo** script SQLite fossile dello stesso
  sito (con `init_db.php` e l'init SQLite di SR-C1) → materiale forte per il box "fossili post-migrazione".
- Versione del sito al momento della mappatura: **2.9.13** (`package.json`, vedi SR-C1).
