# Mappatura — SimonePizziWebSite — C2: Security & Auth

> **Stato:** COMPLETATO
> **Sessione:** 2 · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `SimonePizziWebSite/`)
> - `public/api/auth.php` (login/logout/check, recupero+reset password, rate limiting, invio email)
> - `public/api/auth_helper.php` (classe `Auth::check()`: gate sessione + difesa CSRF + session_version)
> - `public/api/articles.php:3,125,239,278,322,333` (consumatore tipico del gate `Auth::check()`)
> - `public/.htaccess` (HTTPS forzato, HSTS, CSP, header anti-clickjacking/sniffing)
> - `public/uploads/.htaccess` + `dist/uploads/.htaccess` (PHP engine off nella dir upload)
> - `public/api/.data/.htaccess` (`Require all denied`)
> - `scripts/server-tools/migrate_to_mysql.php:97-101,228-231` (schema/migrazione `login_attempts`)
> - `docs/changelogs/1.8.x/1.8.0.md` (origine della tabella `password_resets`)

## 1. Cosa fa (sintesi narrativa)

C2 è l'unico vero perimetro di sicurezza del thin stack: niente framework, niente libreria di
auth, solo PHP nativo (`session_*`, `password_*`, `random_bytes`) e regole Apache nei `.htaccess`.

Due file portano tutto il peso:

- **`auth.php`** è l'endpoint pubblico (`POST` only). Smista per `action`:
  `check` (sei loggato?), `logout`, `request-recovery` (chiedi reset), `reset-password`
  (applica nuova password con token), e — senza `action` — il **login standard**.
  Login: cerca l'utente per username, verifica con `password_verify`, e in caso di successo
  **rigenera l'ID di sessione** (`session_regenerate_id(true)`, anti session-fixation) e popola
  `$_SESSION`. Difesa brute-force via tabella `login_attempts` (max 5 tentativi falliti per IP in
  15 minuti → `429`).
- **`auth_helper.php`** è la guardia che ogni endpoint protetto include: `Auth::check()` è la
  riga unica che gli endpoint mutativi (`articles.php`, `media.php`, `settings.php`, …) chiamano
  prima di toccare i dati. Fa tre cose in sequenza: (1) esige una sessione valida, (2) su metodi
  mutativi controlla l'origine (CSRF in profondità), (3) verifica `session_version` contro il DB
  per invalidare al volo sessioni di utenti la cui password è stata resettata.

Il modello di sessione è cookie-based con i tre flag canonici (`HttpOnly`, `Secure`,
`SameSite=Strict`) impostati **prima** di `session_start()` in entrambi i file — così nessun
cookie nasce "debole" da un endpoint diverso da `auth.php` (regressione corretta in v1.19.0).

Il recupero password (v1.8.0/v1.7.18, indurito in v1.19.0) usa token monouso da 32 byte casuali,
scadenza 1 ora, tabella `password_resets`, email con link ad **URL canonico** (`SITE_URL`, mai
`HTTP_HOST`) per prevenire il *password-reset poisoning*.

## 2. Pattern miniCMS rilevanti

- **Auth come "una riga di include + una riga di gate".** Il contratto di protezione di un
  endpoint è `require_once 'auth_helper.php';` + `Auth::check();` all'inizio del ramo mutativo.
  È la versione thin-stack del middleware: nessun router, nessun decoratore, ma lo stesso effetto.
- **Flag cookie centralizzati e *fail-safe by default*** (`auth_helper.php:7-9`, `auth.php:5-7`):
  i tre `ini_set` precedono sempre `session_start()`. Dopo la regressione v1.19.0 stanno in
  `auth_helper.php`, incluso ovunque, così la difesa CSRF di base (`SameSite=Strict`) è universale.
- **Difesa in profondità CSRF** (`auth_helper.php:21-37`): oltre a `SameSite`, sui metodi
  non-safe si confronta l'host di `Origin`/`Referer` con quello di `SITE_URL`; assenza di entrambi
  (client non-browser) → pass; mismatch → `403`. Whitelist `localhost`/`127.0.0.1` per il dev.
- **Invalidazione globale delle sessioni via `session_version`** (numero in `users`, copia in
  `$_SESSION`): reset password fa `session_version + 1`, e `Auth::check()` confronta DB vs sessione
  ad ogni richiesta protetta. Logout-everywhere senza store di sessioni server-side.
- **Anti session-fixation** esplicito: `session_regenerate_id(true)` subito dopo login riuscito.
- **Rate limiting "riusato"**: una sola tabella `login_attempts` serve sia il login (chiave =
  IP grezzo, soglia 5) sia il recovery (chiave = `'rec:' + sha256(IP)` troncata, soglia 3),
  con namespacing per non far interferire i due contatori.
- **IP del client robusto** (`getClientIp()`, `auth.php:15-29`): si fida di `REMOTE_ADDR` se è già
  pubblico; ricorre a `X-Forwarded-For` (primo hop, validato `NO_PRIV_RANGE|NO_RES_RANGE`) solo se
  `REMOTE_ADDR` è privato (dietro proxy interno). Evita lo spoofing del rate-limit via header.
- **Enumeration-safe**: `request-recovery` risponde sempre con messaggio generico ("se l'account
  esiste…") a prescindere dall'esistenza dell'utente.
- **Fail-closed sul DB**: se il check di `session_version` solleva `PDOException`, l'accesso è
  negato (`401`), non concesso (`auth_helper.php:51-57`).
- **Hardening a livello server (`.htaccess`)**: HTTPS forzato (301), HSTS 1 anno, CSP restrittiva
  (`connect-src 'self'` → niente CORS cross-origin), `X-Frame-Options SAMEORIGIN`, `nosniff`,
  `Referrer-Policy`, `Permissions-Policy`; PHP engine **off** nella dir uploads; `.data` negata.

## 3. Codice chiave (stralci con origine)

**Login: anti-fixation + rate-limit + hashing** — `public/api/auth.php:180-211`:

```php
if ($attempts >= 5) {
    http_response_code(429); // Too Many Requests
    echo json_encode(['status' => 'error', 'message' => 'Too many failed login attempts. Try again in 15 minutes.']);
    exit;
}
$stmt = $pdo->prepare("SELECT id, username, password_hash, session_version FROM users WHERE username = ?");
$stmt->execute([$username]);
$user = $stmt->fetch();

if ($user && password_verify($password, $user['password_hash'])) {
    session_regenerate_id(true);                       // anti session-fixation
    $_SESSION['user_id'] = $user['id'];
    $_SESSION['username'] = $user['username'];
    $_SESSION['session_version'] = (int)$user['session_version'];
    $pdo->prepare("DELETE FROM login_attempts WHERE ip_address = ?")->execute([$ip_address]);
    echo json_encode(['status' => 'success', 'message' => 'Login effettuato']);
} else {
    $pdo->prepare("INSERT INTO login_attempts (ip_address) VALUES (?)")->execute([$ip_address]);
    http_response_code(401);
    echo json_encode(['status' => 'error', 'message' => 'Credenziali non valide']);
}
```

**Il gate riusabile: sessione + CSRF + session_version** — `public/api/auth_helper.php:14-58`:

```php
public static function check() {
    if (!isset($_SESSION['user_id'])) {
        http_response_code(401);
        echo json_encode(['status' => 'error', 'message' => 'Non autorizzato']);
        exit;
    }
    // CSRF in profondità: su metodi mutativi, Origin/Referer deve combaciare con SITE_URL
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
    // session_version: una password resettata invalida la sessione corrente (fail-closed)
    try {
        $pdo = Database::connect();
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
        error_log('auth_helper.php session_version check failed: ' . $e->getMessage());
        http_response_code(401);   // fail-closed
        echo json_encode(['status' => 'error', 'message' => 'Sessione non verificabile. Riprova.']);
        exit;
    }
}
```

**Consumo del gate in un endpoint** — `public/api/articles.php:238-239` (identico su PUT/DELETE/PATCH e sul GET per `id`):

```php
elseif ($method === 'POST') {
    Auth::check();
    ...
```

**Cookie di sessione hardened, prima di session_start** — `public/api/auth_helper.php:7-11`:

```php
ini_set('session.cookie_httponly', 1);
ini_set('session.cookie_secure', 1);
ini_set('session.cookie_samesite', 'Strict');
session_start();
```

**Reset password: requisito robustezza + invalidazione sessioni** — `public/api/auth.php:127-149`:

```php
if (strlen($newPassword) < 12) { /* 400: "almeno 12 caratteri" */ }
$stmt = $pdo->prepare("SELECT user_id FROM password_resets WHERE token = ? AND expires_at > NOW()");
$stmt->execute([$token]);
$reset = $stmt->fetch();
if (!$reset) { /* 400: token non valido o scaduto */ }
$hash = password_hash($newPassword, PASSWORD_DEFAULT);
$pdo->prepare("UPDATE users SET password_hash = ?, session_version = session_version + 1 WHERE id = ?")
    ->execute([$hash, $reset['user_id']]);
$pdo->prepare("DELETE FROM password_resets WHERE token = ?")->execute([$token]);
```

**Recovery: token casuale, scadenza 1h, invalida i precedenti, email enumeration-safe** — `public/api/auth.php:98-106`:

```php
$token = bin2hex(random_bytes(32));
$expires = date('Y-m-d H:i:s', strtotime('+1 hour'));
$pdo->prepare("DELETE FROM password_resets WHERE user_id = ?")->execute([$user['id']]);
$pdo->prepare("INSERT INTO password_resets (user_id, token, expires_at) VALUES (?, ?, ?)")
    ->execute([$user['id'], $token, $expires]);
```

**Link email da URL canonico (anti reset-poisoning)** — `public/api/auth.php:227-230`:

```php
// URL canonico hardcoded (SITE_URL), mai da HTTP_HOST
$host = parse_url(SITE_URL, PHP_URL_HOST);
$link = SITE_URL . "/admin/reset-password/{$token}";
```

**Hardening Apache (estratto)** — `public/.htaccess:17-19,57-90`:

```apache
RewriteCond %{HTTPS} !=on
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [R=301,L]   # HTTPS forzato
Header always set Strict-Transport-Security "max-age=31536000" env=HTTPS
Header always set X-Frame-Options "SAMEORIGIN"
Header always set Content-Security-Policy "default-src 'self'; script-src 'self'; ... connect-src 'self'; object-src 'none'; frame-ancestors 'self'; base-uri 'self'"
```

**PHP disattivato nella dir upload** — `public/uploads/.htaccess` (e copia in `dist/uploads/`):

```apache
<IfModule mod_php.c>
  php_flag engine off
</IfModule>
<FilesMatch "\.(php|phtml|php[0-9]|phps|cgi|pl|py|sh)$">
  Require all denied
</FilesMatch>
```

## 4. Problemi riscontrati & soluzioni

- **Regressione "cookie debole" e sua correzione (GOLD).** Fino a v1.18.x i flag
  `HttpOnly/Secure/SameSite` stavano **solo** in `auth.php`: un cookie di sessione emesso da un
  altro endpoint (es. `articles.php`) nasceva senza protezioni, indebolendo l'unica difesa CSRF.
  v1.19.0 sposta i `ini_set` in `auth_helper.php` (incluso da tutti gli endpoint). → Lezione:
  la config di sicurezza della sessione va nel file *condiviso*, non nell'endpoint di login.
  Riferimento esplicito nel commento `auth_helper.php:4-6`.
- **Schema `password_resets` non più nel codice (debito di tracciabilità).** La tabella è citata e
  usata in `auth.php` ma **nessun file la crea**: lo script di migrazione che la generò è stato
  cancellato dopo l'esecuzione in produzione (changelog v1.8.0, "Cleanup: rimozione script di
  migrazione"). Anche `migrate_to_mysql.php` non la include. Idem `session_version`, aggiunta a
  caldo con un `ALTER TABLE ... ADD COLUMN` idempotente *dentro* `auth.php:33-35`. → Lo schema vero
  non è ricostruibile da un singolo file: pattern "migrazioni distruttive usa-e-getta" da
  documentare (ponte a C1/C13). Per il libro: come tracciare lo schema quando le migration spariscono.
- **Migrazione di schema "a caldo" nel percorso di richiesta.** `auth.php` esegue un `ALTER TABLE`
  ad ogni invocazione (in try/catch silenzioso). Funziona ed è idempotente, ma accoppia evoluzione
  schema e traffico utente. → Box "migrazioni lazy nel thin stack: pro/contro".
- **Login con username solo.** Il login cerca per `username` (`auth.php:187`), mentre il recovery
  accetta username *o* email. Asimmetria minore da segnalare, non un bug.
- **`Access-Control-Allow-Methods` senza `Allow-Origin`.** Diversi endpoint (es.
  `articles.php:6`) emettono l'header dei metodi ma **nessuno** emette `Access-Control-Allow-Origin`
  (grep negativo su tutta `public/api`). Risultato: la CORS resta chiusa (same-origin), coerente con
  `connect-src 'self'` della CSP. L'header dei metodi è quindi cosmetico/innocuo. → Nota didattica:
  CORS si apre solo con `Allow-Origin`, non con `Allow-Methods`.

## 5. Estetica / UX (moderna ma funzionale)

- **Email di recupero brandizzata** (`auth.php:238-248`): HTML scuro coerente col sito
  (`#0a0a0a`/`#22c55e`), CTA a pulsante, micro-copy rassicurante ("se non hai richiesto tu…").
  Subject codificato `=?UTF-8?B?…?=` per gli accenti. Cura del dettaglio anche in un canale tecnico.
- **Messaggi d'errore JSON uniformi** (`{status, message}`) con testi parlanti lato utente
  ("Sessione scaduta. Effettua nuovamente il login.") e dettaglio tecnico solo in `error_log`.
- **Stati HTTP semanticamente corretti**: `400` (input mancante), `401` (non auth/sessione),
  `403` (origine CSRF), `429` (rate limit), `405` (metodo) — il frontend può reagire per codice.
- **UX di sicurezza trasparente**: il requisito "almeno 12 caratteri" è comunicato in chiaro al
  momento del reset, non come fallimento opaco.

## 6. Differenze rispetto agli altri siti

(Da consolidare in FASE 2. Ipotesi/puntatori:)
- ROADMAP segna per **SitoRuntime** un cluster "SR-C2 Security **+ CORS**": è probabile che lì la
  CORS sia realmente aperta (multi-dominio?), a differenza di qui dove resta same-origin. Da
  confrontare con la CSP `connect-src` di SR.
- Per **DISINTELLIGENZA/FDCA** il C2 include "anti-frode voto" (assente qui, sito senza festival):
  il modello di abuso è diverso (1 voto/identità vs brute-force login). La tabella `login_attempts`
  riusata per più scopi sarà un buon confronto col rate-limit dei voti.
- Da verificare se gli altri siti adottano lo stesso pattern `session_version` e il gate
  `Auth::check()` come include unico, o soluzioni diverse.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| Gate auth come "include + `Auth::check()`": il middleware del thin stack | Cap. "Security & Auth / Proteggere un endpoint" (nuovo) |
| Sessioni PHP indurite: flag cookie prima di `session_start`, anti-fixation | Cap. "Sessioni sicure senza librerie" |
| **Regressione cookie debole → fix centralizzato in `auth_helper`** | Box problemi/soluzioni (alto valore) |
| Difesa CSRF in profondità (SameSite + check Origin/Referer) | Box "CSRF nel thin stack" |
| `session_version`: logout-everywhere senza store di sessioni | Box "invalidare sessioni a costo zero" |
| Rate limiting con una tabella riusata (login + recovery, namespacing) | Cap. "Difesa brute-force / rate limiting" |
| `getClientIp()` robusto vs spoofing `X-Forwarded-For` | Box "fidarsi dell'IP dietro proxy" |
| Recupero password: token casuali, scadenza, enumeration-safe, anti-poisoning | Cap. "Reset password fatto bene" |
| `.htaccess`: HTTPS/HSTS/CSP/headers + PHP-off negli upload | Cap. "Hardening a livello server" |
| **Schema sparito con le migration cancellate** | Box "tracciabilità dello schema" (ponte C1/C13) |

## 8. Note / domande aperte

- **Puntatori ad altri cluster** (annotati qui, NON mappati in questa card):
  - `sendRecoveryEmail()` usa `mail()` nativo (`auth.php:226-257`) → la **C9** (Newsletter & Email)
    dovrà mappare il "motore email" del miniCMS; qui guardato solo come consumatore per il reset.
  - Tabelle `users` (campo `email`, `password_hash`, `session_version`) e `password_resets` →
    lo **schema** è competenza C1/C13; qui solo l'uso lato auth. `session_version` è aggiunta a
    caldo in `auth.php`, non in `migrate_to_mysql.php`.
  - `Auth::check()` è consumato da quasi tutti gli endpoint (`articles`, `media`, `settings`,
    `backup`, `subscribers`, `newsletter_send`, `analytics`, `stats`, `reactions`, `messages`,
    `tags`, `projects`, `categories`, `optimize_db`) → la *logica* di quegli endpoint è di
    C4/C5/C9/C11/C12; qui interessa solo che li gatea.
  - CSP/`.htaccess` toccano anche SEO/embed (`frame-src youtube-nocookie`, `connect-src`) →
    intersezione con **C7**; qui letti per gli header di sicurezza.
- **Da verificare:** esiste un punto unico che crea `password_resets` per un ambiente nuovo? Oggi
  no (script di migrazione cancellato) — possibile trappola al primo deploy pulito. Follow-up in
  C13.
- **Da verificare:** `auth.php` (login) **non** include `auth_helper.php`, quindi i flag cookie li
  reimposta da sé (`auth.php:5-7`). Coerenti, ma duplicati: candidato a refactor (non urgente).
- Credenziali reali di `config.php` non riportate (redatte come in [SPW-C1]).
- Versione del sito al momento della mappatura: **1.21.0** (`package.json`), hardening auth
  consolidato in **v1.19.0**.
