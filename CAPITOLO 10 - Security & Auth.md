# CAPITOLO 10: Security & Auth (Terza Edizione)

La sicurezza è l'unica lente di questo libro in cui i tre siti non scalano in parallelo con l'ingegnerizzazione del backend. Negli altri capitoli vale una regola intuitiva: più un sito è cresciuto, più la sua infrastruttura è ricca. Qui no. Lo stesso scheletro thin-stack (PHP nativo, sessione su cookie, regole Apache nei `.htaccess`) regge tre gradini di difesa decrescenti, ma il gradino più alto non è quello del sito col backend più sofisticato.

SimonePizziWebSite (SPW) ha il perimetro più maturo: cookie `Secure`, anti session-fixation, invalidazione globale delle sessioni, recupero password completo, IP anti-spoofing. SitoRuntime (SR), il sito più ingegnerizzato del trio, quello delle cicatrici di scalabilità, è solo a metà strada: ha ruoli e token CSRF, ma il cookie viaggia senza `Secure`, non rigenera la sessione al login e il suo rate-limit si aggira con un header. DISINTELLIGENZA (DIS) è l'autenticazione di grado zero: niente CSRF, niente rate-limit, cookie ai valori di default di PHP. Eppure è l'unico dei tre a portare due idee di sicurezza proprie e di valore, la difesa anti-frode di un'azione pubblica (il voto del festival) e il backup automatico prima di un'operazione distruttiva.

È la dimostrazione più netta della tesi che attraversa tutto il libro: più ingegnerizzato non significa più sicuro, e più sicuro non significa più completo su ogni singolo punto. Il modo giusto di leggere ogni difesa è come una scala di sottrazione: cosa resta, e cosa si rompe, quando togli un flag dal cookie, un token da una richiesta, un contatore da un endpoint di login.

> [!NOTE]
> **Una nota di metodo.** Tutti gli stralci di codice di questo capitolo vengono dallo stato reale dei tre siti, citati come `file:linea`. Quando il capitolo dice «il Modello raccomanda» sta prescrivendo; quando dice «SPW fa» o «SR fa» o «DIS fa» sta fotografando il codice in produzione. Le due cose non sempre coincidono, ed è proprio in quello scarto che si impara.

---

## 1. Il perimetro comune: sicurezza fatta a mano

Prima delle divergenze conviene fissare ciò che i tre siti condividono. Sotto le tre implementazioni c'è lo stesso oggetto, con cinque tratti ricorrenti.

**1) Nessuna libreria di autenticazione.** Niente Passport, niente pacchetto JWT, nessun framework di sessione. Tutto poggia su primitive PHP native: `session_*`, `password_hash`/`password_verify`, `random_bytes`, `hash_equals`, e sulle regole Apache nei `.htaccess`. L'auth è fatta a mano, ed è la scelta fondante che rende ogni differenza tra i siti una scelta visibile, non una configurazione sepolta dentro un vendor.

**2) Sessione su cookie più `password_verify`: lo zoccolo identico.** Tutti e tre aprono una sessione PHP nativa, cercano l'utente per `username`, verificano la password contro un hash `PASSWORD_DEFAULT`, e popolano `$_SESSION`. Il sistema non conosce mai la password in chiaro:

```php
// Lo schema comune ai tre siti: nessun segreto in chiaro
$hash = password_hash($password, PASSWORD_DEFAULT);   // alla creazione
// ...
if (password_verify($input, $user['password_hash'])) { /* login ok */ }
```

**3) Il gate è una manciata di righe in cima all'endpoint.** Non c'è middleware né router: la protezione di un endpoint sono poche righe all'inizio del ramo mutativo, che pretendono una sessione valida prima di toccare i dati. È la versione thin-stack del middleware. Ma quanto fa quella manciata di righe (solo sessione? più CSRF? più ruolo? più invalidazione?) è il primo grande asse di divergenza, e lo vediamo al §2.

**4) Difesa «JSON-first» anche sugli errori di sicurezza.** Un accesso negato non produce una pagina di errore di Apache: si imposta il codice HTTP semanticamente corretto (`401`/`403`/`429`) e si risponde con un oggetto `{status|success, message|error}`. Il frontend reagisce per codice.

**5) Hardening a livello server via `.htaccess`.** Tutti hanno almeno un `.htaccess` che imposta header di sicurezza e nega l'accesso a file sensibili. È il secondo strato, fuori dall'applicazione, e anche qui la copertura va dal completo (HTTPS forzato, HSTS, CSP, PHP-off) al minimo (deny di due estensioni).

A questi si aggiunge un tratto negativo condiviso: nessuno dei tre tiene un audit-log degli accessi, e in due casi su tre il contatore brute-force del login non vive nemmeno nel database. Il perimetro è sottile per costruzione. La domanda del capitolo è quanto sottile si può andare prima che qualcosa si rompa.

---

## 2. Il gate: middleware unico, gate componibile, gate inline

Proteggere un endpoint significa decidere, in cima al codice, se chi chiama ha diritto di proseguire. I tre siti risolvono lo stesso problema con tre architetture diverse, ed è il primo punto in cui la scala si fa visibile.

### 2.1 SPW: il gate unico `Auth::check()`

SPW concentra tutto in una classe inclusa da ogni endpoint protetto. Una sola riga, `Auth::check()`, fa tre cose in sequenza: esige una sessione valida, verifica l'anti-CSRF sui metodi mutativi, controlla l'invalidazione via `session_version`.

```php
// public/api/articles.php:238-239 — il consumatore tipico
elseif ($method === 'POST') {
    Auth::check();          // sessione + CSRF + session_version, tutto qui
    // ... da qui in poi si può scrivere
```

Il vantaggio è che la copertura è automatica: ogni nuovo endpoint che include `auth_helper.php` e chiama `Auth::check()` eredita tutte le difese insieme. Non c'è modo di ricordarsi la sessione e dimenticare il CSRF.

### 2.2 SR: il gate componibile a funzioni

SR scompone la stessa protezione in mattoni separati, autorizzazione da una parte e anti-CSRF dall'altra, che ogni endpoint compone a mano nell'ordine giusto:

```php
// public/api/auth_utils.php — i mattoni
function isLoggedIn() { return isset($_SESSION['user_id']); }
function isAdmin()    { return isLoggedIn() && ($_SESSION['role'] ?? '') === 'admin'; }

// public/api/upload.php:8-13 — il consumatore li compone
if (!isLoggedIn()) { http_response_code(401); echo json_encode([...]); exit; }
// ...
validateCsrf();
```

È più flessibile, e il gate a ruolo (`isAdmin()`) è gratis: arriva quel `admin`/`editor` che SPW non ha. Ma è anche più facile da dimenticare, perché la protezione dipende dalla disciplina del singolo endpoint.

### 2.3 DIS: il gate inline grezzo

DIS porta lo stesso schema all'estremo. Niente file di funzioni-mattone: il gate è ricostruito a mano in ogni ramo come un `isset()` nudo.

```php
// public/api/reset_votes.php:11 — il gate per intero, inline
if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'admin') {
    http_response_code(401); die(...);
}
```

> [!WARNING]
> **Middleware o disciplina? Il gate che si dimentica**
> Il gate componibile e quello inline hanno un rischio strutturale che il gate unico non ha: la sicurezza dipende dall'ordine dei rami e dalla memoria di chi scrive.
> In DIS i rami `participants.php?update_status` e `update_round` sono protetti dal solo `isset($_SESSION['user_id'])`, non da `isAdmin()`. Risultato: un editor, non un amministratore, può approvare o respingere partecipanti, mandare le email e spostare i round del festival. La stessa crepa si vede in SR, dove `list_users` e `create_user` stanno prima del blocco `401` e si autoproteggono solo con il check di ruolo locale.
> Funziona finché tutti i rami sono scritti con disciplina. Ma un gate unico (`Auth::check()`) non può essere dimenticato su un endpoint: o lo includi, o l'endpoint non parte. È questa la differenza vera tra middleware e convenzione. Le conseguenze sul festival si vedono al CAP 18.

---

## 3. CSRF: tre gradini di difesa

Il Cross-Site Request Forgery è il problema di impedire che un sito terzo invii richieste mutative sfruttando il cookie di sessione che il browser dell'utente allega in automatico. È la difesa portante di questo capitolo, e i tre siti la risolvono su tre livelli distinti.

### 3.1 SPW: controllo `Origin`/`Referer` (server-side, zero handshake)

SPW non usa token: dentro `Auth::check()`, sui metodi non-safe, confronta l'host di `Origin`/`Referer` con quello di `SITE_URL`.

```php
// public/api/auth_helper.php:21-37 (estratto)
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

Non richiede alcun handshake col client, perché il browser invia `Origin`/`Referer` da solo. E vivendo dentro `Auth::check()`, copre in automatico ogni endpoint che include la guardia.

### 3.2 SR: token sincronizzato `X-CSRF-Token`

SR adotta il pattern da manuale: un token casuale per sessione, restituito al client al login, rispedito dal client in un header e validato con `hash_equals` (confronto timing-safe).

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

### 3.3 DIS: niente

In DIS le mutazioni sono protette dal solo cookie di sessione. Un grep su tutta `public/api/` non trova nessun token CSRF, nessun check `Origin`/`Referer`: la difesa è assente.

> [!WARNING]
> **CSRF nel thin stack: Origin/Referer, token sincronizzato, o niente**
> C'è un sottotesto controintuitivo in questi tre gradini. La soluzione più «da manuale», il token sincronizzato di SR, è anche la più facile da indebolire, perché dipende dalla disciplina per-ramo: basta un endpoint mutativo che dimentichi `validateCsrf()` e il buco è aperto. La soluzione più semplice, il check `Origin`/`Referer` di SPW, copre di più proprio perché è centralizzata dentro il gate unico. Più codice non vuol dire più copertura. È la tesi di fondo del libro applicata al CSRF.

---

## 4. Il cookie di sessione e l'anti session-fixation

> [!NOTE]
> **Un errore comune sui cookie di sessione.** Verrebbe da prescrivere un cookie con `cookie_secure = 1` e `cookie_samesite = 'Lax'`. Guardando il codice reale, due cose vanno corrette: il `SameSite` giusto, e quello che i siti usano davvero, è `Strict`, non `Lax` (sia SPW sia SR); e solo SPW imposta davvero tutti e tre i flag.

I flag vanno impostati prima di `session_start()`, altrimenti non hanno effetto sul cookie corrente. È qui che la scala si vede meglio.

SPW imposta i tre flag in un file condiviso:
```php
// public/api/auth_helper.php:7-11
ini_set('session.cookie_httponly', 1);
ini_set('session.cookie_secure', 1);
ini_set('session.cookie_samesite', 'Strict');
session_start();
```

SR omette `Secure`:
```php
// public/api/auth_utils.php:4-9
ini_set('session.cookie_httponly', '1');
ini_set('session.cookie_samesite', 'Strict');
session_start();                       // NB: cookie_secure NON impostato
```

DIS non imposta nessun flag: il comportamento del cookie dipende interamente dal `php.ini` dell'hosting. Una dipendenza implicita e silenziosa.

A questo si aggiunge l'anti session-fixation, cioè rigenerare l'ID di sessione subito dopo il login per invalidare un ID eventualmente piantato prima dall'attaccante. Solo SPW lo fa:

```php
// public/api/auth.php:186-188 (estratto del ramo di successo)
if ($user && password_verify($password, $user['password_hash'])) {
    session_regenerate_id(true);     // anti session-fixation: una riga, spesso assente
    $_SESSION['user_id'] = $user['id'];
    // ...
}
```

SR e DIS non rigenerano: un ID di sessione fissato prima del login resta valido dopo.

> [!WARNING]
> **I flag del cookie, e perché HSTS non è il redirect HTTPS**
> Togliere `Secure` non è un dettaglio cosmetico. Senza `Secure`, il cookie di sessione può viaggiare anche su HTTP in chiaro. Si potrebbe pensare che HSTS protegga comunque, ma HSTS protegge solo dopo la prima visita HTTPS riuscita. SR applica HSTS ma non forza il redirect 301 a HTTPS: c'è una finestra reale di esposizione su HTTP al primo accesso. SPW chiude la finestra da entrambi i lati, con `cookie_secure=1` e con `RewriteCond %{HTTPS} !=on → 301`.
> La lezione: `Secure` sul cookie e redirect HTTPS forzato sono due difese distinte; HSTS non sostituisce nessuna delle due.
> Curiosità storica (SPW): fino alla v1.18 i flag stavano solo in `auth.php`, così un cookie emesso da un altro endpoint nasceva debole. La v1.19.0 ha spostato gli `ini_set` nel file condiviso `auth_helper.php`. La config di sicurezza della sessione va nel file incluso da tutti, non nell'endpoint di login.

---

## 5. `check_auth` e lo stato di sessione

Il frontend non deve mai conservare la password o lo stato di login in `localStorage`: interroga il server per sapere se la sessione è ancora valida.

```php
// schema di check_auth (SPW/DIS)
if (isset($_SESSION['user_id'])) {
    echo json_encode([
        'status' => 'success',
        'user'   => ['username' => $_SESSION['username'], 'role' => $_SESSION['role']]
    ]);
}
```

> [!NOTE]
> **Lo `username` non è garantito in sessione.** Verrebbe da leggere `$_SESSION['username']` come se fosse sempre presente. In SR non lo è: il login salva `user_id` e `role` ma non `username` (`admin.php:123-124`). La conseguenza è concreta: `check_auth` restituisce `username: null`, e il salvataggio articolo ripiega su `author = $_SESSION['username'] ?? 'Admin'`. In SPW e DIS lo `username` è in sessione e l'esempio regge. Non è un buco di sicurezza, ma un'incoerenza di stato reale: lo stesso campo non è garantito su tutti e tre i siti.

---

## 6. Le password e la difesa brute-force

L'hashing è l'unico punto in cui i tre siti sono identici e tutti corretti: `password_hash($pass, PASSWORD_DEFAULT)` alla creazione, `password_verify` alla verifica. Il sistema non conosce mai la password in chiaro, e l'algoritmo può evolvere (da bcrypt ad argon2) senza che si tocchi una riga di codice.

> [!NOTE]
> **La difesa brute-force non è un `sleep(1)`.** Verrebbe da ridurre la difesa brute-force a un `sleep(1)`, ma è una soluzione incompleta e tarata sul solo SR. Il `sleep(1)` è appena un accorgimento; la difesa vera è il lockout, e soprattutto conta da quale IP lo si misura.

La domanda non è «come rallento i tentativi» ma dove vive il contatore. Tre risposte. SPW lo tiene in una tabella DB `login_attempts`: dopo 5 tentativi falliti da un IP in 15 minuti scatta il `429`, e al login riuscito il contatore si azzera.

```php
// public/api/auth.php:177-211 (estratto)
if ($attempts >= 5) {
    http_response_code(429);
    echo json_encode(['status' => 'error', 'message' => 'Too many failed login attempts. Try again in 15 minutes.']);
    exit;
}
// ... su fallimento:
$pdo->prepare("INSERT INTO login_attempts (ip_address) VALUES (?)")->execute([$ip_address]);
```

SR lo tiene su file: un JSON per IP in `.cache/ratelimit/<md5(ip)>.json`, finestra 900 secondi, soglia 5, più `sleep(1)` sul fallimento. Niente tabella DB, coerente con lo schema MySQL che non contiene `login_attempts`. DIS non lo tiene da nessuna parte: il login si può martellare quanto si vuole.

> [!TIP]
> **Il contatore brute-force: file, DB, o assenza**
> Non c'è una sede giusta in assoluto. La tabella DB di SPW è transazionale e si presta al riuso (lo stesso `login_attempts` serve anche il recovery). Il file di SR evita di gravare sul database ma vive fuori dallo schema, quindi non compare in un dump né in una migrazione: è invisibile finché non lo cerchi nel filesystem. L'assenza di DIS è coerente con un sito-festival dove l'admin è uno solo e l'attrito su un login interno è basso, ma resta un'assenza, non una scelta documentata.

Il punto più sottile, però, è da quale variabile leggi l'IP. È il box-ancora di questo capitolo.

> [!WARNING]
> **Fidarsi dell'IP: il rate-limit che non limita** *(box-ancora, richiamato al CAP 18 e al CAP 20)*
> Un lockout «5 tentativi per IP» vale esattamente quanto la tua capacità di sapere qual è l'IP. E qui i tre siti divergono in modo istruttivo.
>
> SR si fida dell'header sbagliato. Prende l'IP da `X-Forwarded-For`, per primo e senza validazione:
> ```php
> // public/api/admin.php:106-107
> $ip = $_SERVER['HTTP_X_FORWARDED_FOR'] ?? $_SERVER['REMOTE_ADDR'] ?? 'unknown';
> $ip = trim(explode(',', $ip)[0]);   // ← l'attaccante controlla questo header
> ```
> Quell'header è scritto dal client. Un attaccante lo varia a ogni richiesta e il contatore non si incrementa mai: il lockout 5/15min si aggira.
>
> SPW si fida dell'IP TCP, e dell'header solo dietro proxy interno. La funzione `getClientIp()` usa `REMOTE_ADDR` se è già pubblico, e accetta `X-Forwarded-For` (validato `NO_PRIV_RANGE|NO_RES_RANGE`) solo quando `REMOTE_ADDR` è privato, cioè solo dietro un proxy fidato. Niente spoofing.
>
> DIS usa `REMOTE_ADDR` grezzo, e qui è un pregio. Per la barriera anti-doppio-voto (§12), `REMOTE_ADDR` non è falsificabile a livello TCP, quindi la barriera regge. Il rovescio è il NAT: dietro un proxy o una rete condivisa, molti utenti collassano sullo stesso IP.
>
> La lezione non è «usa sempre `REMOTE_ADDR`». È che l'IP giusto dipende dal modello d'abuso. Un login da forzare (vuoi che l'attaccante non possa cambiare la propria identità, quindi diffidi di `X-Forwarded-For`) è il problema opposto di un voto pubblico da non duplicare; eppure la conclusione è la stessa: l'header controllato dal client non è affidabile. Lo stesso `REMOTE_ADDR` grezzo è un buco in un contesto e una difesa nell'altro.

---

## 7. `session_version`: invalidare le sessioni a costo zero

C'è un problema classico dell'auth su sessione: come disconnetti tutte le sessioni di un utente, per esempio dopo un reset password, se non tieni uno store server-side delle sessioni attive? Solo SPW risolve, con un trucco a costo zero: un intero `session_version` in `users`, copiato in `$_SESSION` al login e confrontato a ogni richiesta protetta.

```php
// public/api/auth_helper.php:51-57 — dentro Auth::check()
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
    http_response_code(401);   // ← fail-closed: in caso di errore DB, NEGA
    echo json_encode(['status' => 'error', 'message' => 'Sessione non verificabile. Riprova.']);
    exit;
}
```

Basta incrementare `session_version` di un numero (lo fa il reset password, §8) e tutte le sessioni col numero vecchio diventano invalide al primo controllo. Logout-everywhere senza alcuno store di sessioni.

> [!TIP]
> **Fail-closed, non fail-open**
> Il dettaglio che distingue una difesa fatta bene è il ramo `catch`. Se il controllo di `session_version` solleva una `PDOException` (DB irraggiungibile), SPW nega l'accesso (`401`), non lo concede. La regola: quando una verifica di sicurezza non può essere completata, l'esito di default deve essere «negato». SR e DIS non hanno questo meccanismo, e in SR un cambio password non disconnette le altre sessioni; in DIS nemmeno.

---

## 8. Recovery e reset password fatti bene

È un'intera sezione che il capitolo prima non aveva, perché solo SPW implementa il recupero password self-service. SR e DIS hanno solo `change_password` autenticato, dove devi già essere dentro: password dimenticata uguale nessun rientro.

Il flusso di SPW ha quattro accortezze che vale la pena guardare una per una.

La prima è il token monouso casuale, con scadenza.
```php
// public/api/auth.php:98-106
$token   = bin2hex(random_bytes(32));               // 32 byte casuali
$expires = date('Y-m-d H:i:s', strtotime('+1 hour'));
$pdo->prepare("DELETE FROM password_resets WHERE user_id = ?")->execute([$user['id']]);   // invalida i precedenti
$pdo->prepare("INSERT INTO password_resets (user_id, token, expires_at) VALUES (?, ?, ?)")
    ->execute([$user['id'], $token, $expires]);
```

La seconda è il link costruito da URL canonico, non da `HTTP_HOST`. È la difesa contro il *password-reset poisoning*: se il link nell'email si costruisse da `HTTP_HOST` (controllabile con un header `Host` falsificato), l'attaccante potrebbe far recapitare alla vittima un link che punta al suo dominio e intercettare il token.
```php
// public/api/auth.php:227-230
$link = SITE_URL . "/admin/reset-password/{$token}";   // SITE_URL hardcoded, mai HTTP_HOST
```

La terza è l'essere enumeration-safe. La richiesta di recupero risponde sempre con lo stesso messaggio generico («se l'account esiste, riceverai un'email»), che l'utente esista o no, così non si può usare il form per scoprire quali email sono registrate. Lo stesso contatore `login_attempts` viene riusato qui con namespacing della chiave (`'rec:' + sha256(IP)`), per limitare anche gli abusi del recovery.

La quarta è che il reset invalida le sessioni. Applicando la nuova password, `session_version` viene incrementato, e per quanto visto al §7 tutte le sessioni aperte cadono:
```php
// public/api/auth.php:127-149 (estratto)
if (strlen($newPassword) < 12) { /* 400: "almeno 12 caratteri" */ }
// ... verifica token non scaduto ...
$hash = password_hash($newPassword, PASSWORD_DEFAULT);
$pdo->prepare("UPDATE users SET password_hash = ?, session_version = session_version + 1 WHERE id = ?")
    ->execute([$hash, $reset['user_id']]);
$pdo->prepare("DELETE FROM password_resets WHERE token = ?")->execute([$token]);   // token monouso
```

> [!NOTE]
> **Lo schema che non c'è.** La tabella `password_resets` è usata ovunque in `auth.php`, ma nessun file la crea: lo script di migrazione che la generò è stato cancellato dopo l'esecuzione in produzione. Lo stesso vale per la colonna `session_version`, aggiunta a caldo con un `ALTER TABLE` idempotente dentro `auth.php`. È un debito di tracciabilità: lo schema vero non è ricostruibile da un singolo file. Il tema delle migrazioni usa-e-getta torna al CAP 15 (Database Evolution).

---

## 9. Credenziali di default: random, hardcoded, omessa

Il primo amministratore è un problema di sicurezza spesso sottovalutato. I tre siti lo risolvono in tre modi, e qui si chiude un punto anticipato al CAP 5 (Backend Logic).

> [!WARNING]
> **Il seeding dell'admin: cosa NON fare**
> SPW la genera random e la stampa una volta. La password del primo admin è casuale e mostrata una sola volta in fase di setup. È la scelta corretta.
> SR la hardcoda a `runtime2026`. Il file di manutenzione `fix_users_table.php` ricrea l'utente `admin` con `password_hash('runtime2026', …)` se la tabella è vuota, e quella password è committata nel repo. La mitigazione reale è il `.htaccess`, che nega l'accesso HTTP a `fix_users_table.php` (§10); ma non esiste alcun flusso che obblighi a cambiare la default, e se nessuno usa `change_password` l'account admin resta indovinabile.
> DIS la omette del tutto. Non c'è nessun seeding: `init_db.php` ha eliso la creazione dell'admin, e `users.php` può creare utenti solo se sei già admin. Risultato: niente default indovinabile (il vantaggio), ma il primo admin vive solo nel file `.sqlite` e non è ricostruibile dal repo (lo svantaggio, con il classico problema dell'uovo e la gallina al primo deploy pulito).
> Tre posizioni sulla stessa scala: la random è la più sicura, l'omessa è la più spartana ma non insicura, l'hardcoded è l'unica davvero pericolosa. E non perché la password esista, ma perché niente costringe a cambiarla.

---

## 10. Proteggere il database-a-file e gli script di manutenzione

Quando il database è un file (`.sqlite`), o quando nel docroot vivono script potenti (migrazioni, fix, reset), il `.htaccess` diventa parte del perimetro di sicurezza.

Il primo compito è negare l'accesso diretto al DB-a-file. DIS tiene il `.sqlite` in una cartella `.data/` generata a runtime e protetta:
```apache
# DIS: deny dei file di dati e backup
<FilesMatch "\.(sqlite|bak)$">
    Require all denied
</FilesMatch>
```
La regola di base è quella che il capitolo già insegnava (file fuori dalla root pubblica, oppure `Require all denied` più nomi non prevedibili). La novità è che DIS la accoppia a una cartella `.data/` creata a runtime dal bootstrap, di cui parliamo al CAP 5.

Il secondo compito è negare gli script di manutenzione, ed è qui che SR ha il `.htaccess` più interessante dei tre, perché blocca un'intera famiglia di file per prefisso, prima ancora che PHP li veda:
```apache
# public/.htaccess:80-81 (SR)
<FilesMatch "^(debug_|test_|emergency_|migrate_|fix_|init_|rebuild_|setup_|optimize_)">
    Order allow,deny
    Deny from all
</FilesMatch>
# blocca anche gli URL tipici degli scanner, prima di PHP
RewriteRule ^(wp-|wordpress|xmlrpc|\.env|\.git|cgi-bin|phpmyadmin) - [R=404,L]
```
È questo deny a rendere non eseguibile via browser la `fix_users_table.php` con la password `runtime2026` del §9.

Il terzo compito riguarda gli upload. Se un attaccante riesce a caricare un `.php`, l'esecuzione va spenta a livello di cartella, come fa SPW:
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
> **Il deny che manca dove serve di più**
> Attenzione a non leggere queste regole come una checklist uniforme: la copertura è disomogenea. SR ha il deny by-prefix più sofisticato dei tre, ma non ha un `uploads/.htaccess` che spenga PHP nella cartella di caricamento. DIS protegge il `.sqlite` e i `.bak`, ma i suoi script `update_db_*` non rientrano in nessun pattern di deny e restano raggiungibili. Ogni sito ha blindato la porta che aveva visto, lasciandone aperta un'altra. La protezione dell'upload pubblico, e la catena d'abuso che ne nasce in DIS, è il cuore del CAP 7.

---

## 11. Errori parlanti per l'utente, opachi per l'attaccante

Un errore PHP non gestito che finisce nell'output può rivelare percorsi, query, struttura del database (è il cosiddetto *path/information disclosure*). Lo standard del Modello: codici HTTP semanticamente corretti, messaggi generici al client, dettaglio tecnico solo nel log.

```php
// SPW: il dettaglio va nel log, non al client
} catch (PDOException $e) {
    error_log('auth: ' . $e->getMessage());     // solo qui
    http_response_code(500);
    echo json_encode(['status' => 'error', 'message' => 'Errore interno. Riprova.']);
}
```

> [!WARNING]
> **Non rimandare l'eccezione al client**
> DIS fa l'opposto: `auth.php`, `users.php`, `participants.php` rispediscono `$e->getMessage()` direttamente al client.
> ```php
> // DIS auth.php:48 (anti-pattern)
> } catch (PDOException $e) {
>     echo json_encode(['status' => 'error', 'message' => $e->getMessage()]);   // leak dei dettagli DB
> }
> ```
> È information disclosure gratuita: un attaccante legge nomi di tabelle e colonne dai messaggi d'errore. La regola «parlante per l'utente, opaco per l'attaccante» non costa nulla, basta non saltarla.

---

## 12. Le azioni distruttive e pubbliche

L'ultimo fronte è il più scivoloso: cosa succede quando un'azione è protetta da login ma anche distruttiva, oppure è pubblica (nessun login) ma deve comunque difendersi dall'abuso.

### 12.1 Il reset a un clic: perché «gated» non basta

In DIS gli endpoint `reset_system.php` e `reset_votes.php` richiedono il login admin ma non hanno CSRF. Una `POST` cross-site verso `reset_system.php`, innescata mentre l'admin è loggato in un'altra scheda, cancella tutti i partecipanti, i voti e gli audio. L'unica mitigazione è il `SameSite` di default del cookie (non impostato, come visto al §4), che dipende dalla versione di PHP e non copre ogni caso.

> [!WARNING]
> **Perché un'azione gated ha comunque bisogno del CSRF**
> «È protetta da login» e «è protetta dal CSRF» sono garanzie diverse. Il login dice chi sei; il CSRF dice se sei stato tu a volerlo. Un'azione distruttiva ha bisogno di entrambe: senza CSRF, è la sessione legittima dell'admin a essere usata contro di lui. E una `confirm` JavaScript («sei sicuro?») non sostituisce il CSRF, perché gira sul client e l'attaccante la salta.

### 12.2 Il backup just-in-time: la difesa che DIS ha e SR no

E qui arriva la sorpresa che rompe la scala. Lo stesso DIS che non ha CSRF sul reset fa una cosa che il flagship degli incidenti, SR, non fa: copia il database prima di toccarlo.

```php
// public/api/reset_votes.php:18-21 — backup prima del distruttivo
$dbPath = __DIR__ . '/.data/database.sqlite';
if (file_exists($dbPath)) {
    copy($dbPath, __DIR__ . '/.data/backup_votes_' . date('Ymd_His') . '.sqlite.bak');
}
$pdo->exec("DELETE FROM votes");
```

È esattamente la prevenzione che mancava a SR (al CAP 15 la chiamiamo «cura senza prevenzione»): il sito più debole sull'identità è l'unico a fare il backup giusto-in-tempo. Più sicuro non significa più completo su ogni punto.

### 12.3 Anti-frode di un'azione pubblica, e privacy

Il voto del festival è un'azione che non è autenticata: è il pubblico a votare. DIS la difende a strati, con una sola barriera reale, la `REMOTE_ADDR`/24h vista al box IP del §6. Il trattamento completo dell'anti-frode voto (master switch, cookie cosmetico, `vote_count` denormalizzato) vive al CAP 18; qui interessa solo un punto trasversale: come si conserva l'identità di chi compie un'azione pubblica.

> [!TIP]
> **Votare in anonimato: hash invece di IP in chiaro** *(ponte al CAP 20)*
> DIS salva `ip_address` e `user_agent` in chiaro nella tabella `votes`. Funziona per l'anti-doppio-voto, ma conserva dati personali senza necessità. SPW, per le reazioni anonime (CAP 20), ottiene la stessa garanzia anti-frode memorizzando solo `voter_hash = SHA256(IP + UA)`: il confronto regge, ma il dato personale non viene mai scritto.
> Due posture privacy opposte sulla stessa esigenza funzionale. Nota però che l'hash di SPW non è salato e usa input a bassa entropia (IP e UA): è anti-collisione, non anonimato crittografico forte, perché un IP candidato si può ancora verificare per forza bruta. Il confronto pieno tra le due filosofie (sanitizzazione write-time contro render-time, e identità anonima) è al CAP 20.

Sul versante anti-abuso, c'è un ultimo dettaglio: lo stesso `login_attempts` di SPW viene riusato come rate-limit a due strati per le reazioni (per-hash 20/min più solo-IP 30/min): il primo strato si aggira ruotando lo User-Agent, il secondo è l'argine vero. Anche qui il dettaglio è al CAP 20.

---

## 13. Il lato client e una lezione sui bot

L'area Admin in React è protetta da un `AdminLayout` che, nel suo `useEffect` principale, interroga `check_auth`: se il server risponde `401`, il client distrugge lo stato locale e reindirizza al login, così non lampeggia contenuto sensibile. La sidebar e le rotte si generano in base al `role` ricevuto dal server (admin contro editor in SR e DIS).

> [!NOTE]
> **Il client non è la difesa.** Il logout client-side e il check `401` sono esperienza utente, non sicurezza: nascondono ciò che non devi vedere, ma è il gate server-side (§2) a impedirti di toccarlo. La differenza tra «logout sul client» e l'invalidazione vera via `session_version` (§7) è esattamente questa. L'architettura completa del pannello admin (le tre dashboard, le tre architetture di guardia, il posizionamento dei backup) è al CAP 14.

C'è infine una lezione che viene da un incidente reale e resta pertinente qui, anche se il caso completo è migrato altrove. Nel febbraio 2026 Runtime Radio è stato sommerso da bot che simulavano i crawler dei social (Telegram, Facebook, X) per colpire l'entry-point SEO in PHP, che a ogni richiesta interrogava il database. Lo User-Agent dei bot è falsificabile.

> [!WARNING]
> **Lo User-Agent non è un gatekeeper**
> Non si prendono mai decisioni di sicurezza in base allo User-Agent, perché si falsifica in un campo header. Lo si può usare per ottimizzare (servire una cache ai bot riconosciuti), mai come barriera d'accesso. Il racconto completo dell'attacco DDoS-da-bot e la soluzione (cache statica precompilata, percorso bot separato da quello umano) sono al CAP 11, perché il vettore è proprio l'entry-point SEO. Qui resta solo la massima.

---

## In sintesi

La sicurezza è la lente che smentisce l'intuizione «più grande uguale più robusto». SPW, che non è il sito più ingegnerizzato, ha il perimetro più maturo. SR, il più ricco, lascia tre buchi reali: cookie senza `Secure`, niente anti-fixation, rate-limit che si aggira. DIS, il grado zero, porta comunque due idee che agli altri mancano, l'anti-frode pubblica robusta e il backup pre-distruttivo. Letta come una scala di sottrazione, ogni difesa insegna due cose insieme: cosa fa, e cosa si rompe quando la togli.

> [!IMPORTANT]
> **Il Canone**
> - Sessioni con cookie `HttpOnly` + `SameSite=Strict` + `Secure` su HTTPS; password con `password_hash()`.
> - Token CSRF su tutte le mutazioni: un `confirm()` non è una difesa CSRF.
> - Autorizzazione per **ruolo** (`isAdmin`), non solo per login (`isLoggedIn`).
> - Lockout brute-force misurato su un IP affidabile, non su header controllati dal client (`X-Forwarded-For`).
> - `session_version` per invalidare le sessioni al cambio password; nessuna credenziale di default nel codice.

---
*Prossimo Capitolo: SEO Pre-rendering con PHP Entry-Point. Il motore SEO invisibile che trasforma una SPA in un sito indicizzabile, e il vettore dell'attacco DDoS-da-bot del febbraio 2026.*
