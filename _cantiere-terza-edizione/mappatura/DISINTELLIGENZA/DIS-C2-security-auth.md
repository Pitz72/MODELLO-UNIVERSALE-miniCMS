# Mappatura — DISINTELLIGENZA — C2: Security & Auth (+ anti-frode voto)

> **Stato:** COMPLETATO
> **Sessione:** 24 · **Data:** 2026-06-18 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `DISINTELLIGENZA/`)
> - `public/api/auth.php` (login/logout/check_auth — niente recovery, niente rate-limit, niente CSRF)
> - `public/api/users.php` (gestione utenti gated: list/create/delete + change_password; ruoli admin/editor)
> - `public/api/votes.php` (**anti-frode voto**: master switch + cookie + IP/24h + transazione)
> - `public/api/participants.php` (registrazione **pubblica** + update_status/update_round gated)
> - `public/api/reset_votes.php` · `reset_system.php` (operazioni distruttive admin + **backup automatico**)
> - `public/.htaccess` (deny `*.sqlite`/`*.bak`, routing — già visto in DIS-C1)
> - grep negativo su tutta `public/api/`: **nessun** `csrf`, `X-Forwarded-For`, `getClientIp`, `session_regenerate_id`, `cookie_httponly/samesite/secure`, **nessun seeding admin**
> - confronto: `SR-C2-security-auth.md`, `SPW-C2-security-auth.md`, `SPW-C11` (voter_hash)

## 1. Cosa fa (sintesi narrativa)

C2 è il perimetro di sicurezza di DISINTELLIGENZA. Come negli altri due siti è **PHP nativo senza
framework** (`session_*`, `password_*`), ma è la versione **più spartana dei tre**: dove SR-C2 aveva
CSRF a token, rate-limit file-based, ruoli e CORS, e SPW-C2 aveva CSRF Origin/Referer, recovery,
`session_version` e anti-fixation, **DISINTELLIGENZA non ha quasi nulla di tutto questo**. È
l'autenticazione "grado zero", coerente con il bootstrap grado-zero di DIS-C1.

Due assi:

1. **Auth (`auth.php` + `users.php`).** `auth.php` è l'endpoint pubblico `?action=login|logout|
   check_auth`: `password_verify`, popola `$_SESSION` con `user_id`/`username`/`role`, risponde JSON.
   **Nessun rate-limit** sul login (niente tabella `login_attempts`, niente `.cache/ratelimit` come
   SR), **nessun `session_regenerate_id`** (session fixation aperta), **nessun CSRF**, **nessun
   recovery password**. `users.php` gestisce gli utenti (list/create/delete admin-only +
   change_password self/admin) con il gate `$_SESSION['role']`, modello a **ruoli admin/editor** (come
   SR). Punto chiave (filo da DIS-C1): **non esiste alcun seeding dell'admin** in tutto il repo —
   `init_db.php` ne aveva eliso la creazione ("[Admin creation ignored for brevity in repl]") e
   `users.php` può creare utenti **solo se sei già admin**. Quindi il primo admin **vive solo nel
   `.sqlite`** (uovo-e-gallina), confermando il tema DIS-C1 "la verità è nel file".

2. **Anti-frode voto (`votes.php`) — la parte ad alto valore e specifica del sito.** Il voto è
   **pubblico** (non serve login: è il pubblico del festival che vota). La difesa anti-doppio-voto è a
   strati: (a) **master switch** `settings.voting_active`; (b) **cookie** `dis_voted` (cosmetico,
   azzerabile); (c) validazione **1–3 preferenze**; (d) i partecipanti devono essere
   `in_current_round = 1`; (e) **rate-limit per IP**: un voto per IP ogni 24h. I voti memorizzano
   **IP e User-Agent in chiaro** (≠ il `voter_hash` SHA256 di SPW-C11). A latere, le operazioni
   distruttive (`reset_votes`, `reset_system`) sono gated admin e — sorpresa positiva — fanno un
   **backup automatico** del `.sqlite` prima di cancellare (vedi §4, divergenza da SR-C13).

## 2. Pattern miniCMS rilevanti

- **Auth a sessione nuda, senza prelude condiviso.** Ogni endpoint fa `session_start()` a mano
  (`auth.php:5`, `users.php:3`, …); non c'è un `auth_utils.php`/`auth_helper.php` con funzioni-mattone
  (SR/SPW) né una classe `Auth::check()`. Il gate è ricostruito inline ramo per ramo come
  `if (!isset($_SESSION['user_id'])) { 401 }` (+ `$_SESSION['role'] !== 'admin'` dove serve). È il
  modello "disciplina pura" portato all'estremo (ancora più di SR, che almeno aveva le funzioni).
- **Ruoli admin/editor** (`users.php:12,19`; `news.php`/`podcasts.php` di C4): gerarchia a due livelli
  come SR. `username` **è** salvato in sessione (`auth.php:24`), a differenza di SR (dove l'assenza
  causava `author='Admin'`).
- **Master switch del voto difensivo sulle due rappresentazioni** (`votes.php:14`):
  `return $res === '1' || $res === 'true'`. Accetta **entrambe** le forme del booleano — ed è la
  conseguenza diretta dell'incoerenza di DIS-C1 (i settings `voting_active` seminati come `'false'` in
  `update_db_0_1_4` e come `'0'` in `update_db_voting`): il codice **si difende dalla propria seed
  incoerente**. Chiusura cross-card con DIS-C1.
- **Anti-frode voto a strati con barriera reale = IP/24h** (`votes.php:28-62`): il cookie `dis_voted`
  è solo cosmetico (bypassabile); la barriera vera è `SELECT COUNT(DISTINCT session_id) FROM votes
  WHERE ip_address = ? AND created_at > datetime('now','-24 hours')`. NB: `datetime('now')` di SQLite
  è **UTC** (stesso pattern di DIS-C4) e l'IP viene da `REMOTE_ADDR` **grezzo** (`votes.php:50`) —
  che, a differenza dell'`X-Forwarded-For` grezzo di SR-C2, **non è spoofabile** lato client (ma
  collide su NAT/IP condivisi).
- **Voto raggruppato + contatore denormalizzato in transazione** (`votes.php:64-78`): un
  `session_id = uniqid()` lega i voti della stessa sessione; la transazione fa l'INSERT in `votes` e
  l'`UPDATE participants SET vote_count = vote_count + 1`. Il `vote_count` è un contatore
  denormalizzato (può divergere dalla tabella `votes`; `reset_votes` li riallinea entrambi).
- **Registrazione pubblica gated da setting** (`participants.php:106-113`): la submit pubblica è
  aperta solo se `settings.registration_active` ∈ {`'1'`,`'true'`} (stesso pattern del voto).
- **Backup automatico prima delle operazioni distruttive** (`reset_votes.php:18-21`,
  `reset_system.php:24-27`): `copy()` del `.sqlite` in `.data/backup_*.sqlite.bak` **prima** di
  cancellare. È prevenzione attiva — e finisce dentro la `.data/` protetta da DIS-C1.
- **Conferma a due passi sull'operazione catastrofica** (`reset_system.php:14-20`): senza
  `action=confirm_reset` lo script ritorna solo un avviso, non cancella. Safety UX.

## 3. Codice chiave (stralci con origine)

**Login: niente rate-limit, niente regenerate, niente CSRF, errore che fa leak** — `auth.php:14-48`:

```php
if ($action === 'login') {
    $stmt = $pdo->prepare("SELECT id, username, password_hash, role FROM users WHERE username = ?");
    $stmt->execute([$username]);
    $user = $stmt->fetch();
    if ($user && password_verify($password, $user['password_hash'])) {
        $_SESSION['user_id']  = $user['id'];
        $_SESSION['username'] = $user['username'];   // <-- username SÌ in sessione (≠ SR)
        $_SESSION['role']     = $user['role'];
        // NB: nessun session_regenerate_id(true) -> session fixation aperta
        echo json_encode(['status'=>'success', 'user'=>['username'=>$user['username'],'role'=>$user['role']]]);
    } else {
        http_response_code(401);
        echo json_encode(['status'=>'error','message'=>'Invalid credentials']);   // enumeration-safe (msg unico)
    }
}
// ... catch (PDOException $e) { ... 'message' => $e->getMessage() }  <-- info disclosure
```

**Anti-frode voto: master switch difensivo + cookie + IP/24h** — `votes.php:10-62`:

```php
function isVotingActive($pdo) {
    $stmt = $pdo->prepare("SELECT value FROM settings WHERE key = 'voting_active'");
    $stmt->execute();
    $res = $stmt->fetchColumn();
    return $res === '1' || $res === 'true';        // <-- difesa sulle DUE forme (incoerenza DIS-C1)
}
// ...
if (isset($_COOKIE['dis_voted'])) { /* 400 'Hai già votato.' */ }      // cosmetico, bypassabile
if (!is_array($votes) || count($votes) < 1 || count($votes) > 3) { /* 400 */ }
// participants in_current_round = 1 ...
$ip = $_SERVER['REMOTE_ADDR'];                                          // grezzo MA non spoofabile (≠ XFF di SR)
$stmt = $pdo->prepare("SELECT COUNT(DISTINCT session_id) FROM votes
                       WHERE ip_address = ? AND created_at > datetime('now', '-24 hours')");
$stmt->execute([$ip]);
if ($stmt->fetchColumn() > 0) { /* 400 'Hai già votato da questo IP oggi.' */ }   // barriera REALE
```

**Voto in transazione + IP/UA in chiaro + contatore denormalizzato** — `votes.php:64-81`:

```php
$session_id = uniqid();
$pdo->beginTransaction();
$stmt = $pdo->prepare("INSERT INTO votes (participant_id, session_id, ip_address, user_agent) VALUES (?, ?, ?, ?)");
$updateCount = $pdo->prepare("UPDATE participants SET vote_count = vote_count + 1 WHERE id = ?");
foreach ($votes as $pid) { $stmt->execute([$pid, $session_id, $ip, $ua]); $updateCount->execute([$pid]); }
$pdo->commit();
setcookie('dis_voted', '1', time() + (86400 * 30), "/");   // IP+UA salvati in CHIARO (≠ voter_hash SPW)
```

**Operazione distruttiva: gate admin + backup automatico + reset master switch** — `reset_votes.php:11-33`:

```php
if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'admin') { http_response_code(401); die(...); }
// SECURITY: Backup automatico prima dell'operazione distruttiva sui voti
$dbPath = __DIR__ . '/.data/database.sqlite';
if (file_exists($dbPath)) { copy($dbPath, __DIR__ . '/.data/backup_votes_' . date('Ymd_His') . '.sqlite.bak'); }
$pdo->exec("DELETE FROM votes");
$pdo->exec("DELETE FROM sqlite_sequence WHERE name='votes'");   // SQLite vivo
$pdo->exec("UPDATE participants SET vote_count = 0");
$pdo->exec("UPDATE settings SET value = 'false' WHERE key = 'voting_active'");
// NB: nessun CSRF -> una POST cross-site dell'admin loggato può azzerare i voti
```

**Gestione utenti: gate a ruolo + "non puoi cancellare te stesso"** — `users.php:50-62`:

```php
} elseif ($action === 'delete') {
    if ($currentUserRole !== 'admin') { http_response_code(403); die(...); }
    $id = $data['id'];
    if ($id == $_SESSION['user_id']) { http_response_code(400); die('Cannot delete yourself'); }  // anti-suicidio
    $pdo->prepare("DELETE FROM users WHERE id = ?")->execute([$id]);
}
```

## 4. Problemi riscontrati & soluzioni

- **GOLD — auth "grado zero": niente CSRF, niente rate-limit, niente anti-fixation, niente recovery.**
  Verificato per grep negativo su tutta `public/api/`: **nessun** token CSRF né check Origin/Referer
  (≠ entrambi gli altri siti); **nessun** rate-limit sul login (≠ tabella DB di SPW e file di SR);
  **nessun** `session_regenerate_id` (session fixation, come SR ma senza nemmeno il resto);
  **nessun** `session_version`/recovery. Tutte le mutazioni gated sono protette **solo dal cookie di
  sessione** — e il cookie è quello **di default** di PHP (nessun `cookie_httponly`/`samesite`/
  `secure` impostato: dipende interamente dal `php.ini` dell'hosting). È il perimetro più debole dei
  tre. → Box "l'auth minima: cosa resta quando togli tutto" (contrappunto a SR-C2/SPW-C2).
- **GOLD — l'admin non è bootstrappabile dal repo (chiude il filo #1 di DIS-C1).** Non c'è **nessun**
  seeding admin: `init_db.php` crea la tabella `users` ma ha **eliso** la creazione dell'admin
  ("ignored for brevity in repl", DIS-C1), e `users.php?action=create` richiede di **essere già
  admin** (`users.php:31`). Quindi il primo amministratore esiste **solo nel file `.sqlite` vivo**,
  inserito a mano o da codice non versionato. Lato positivo: **niente password di default hardcoded**
  come il `runtime2026` di SR-C1/C2. Lato negativo: lo schema/identità non è ricostruibile dal repo
  (ennesima conferma di "la verità è nel `.sqlite`"). → Box "l'admin che vive solo nel database".
- **GOLD — CSRF assente su operazioni distruttive = catastrofe a un clic.** `reset_system.php` (gated
  admin, ma **senza CSRF**) cancella **tutti** i partecipanti, i voti e i file audio. Una POST
  cross-site verso `reset_system.php?` (anzi `action=confirm_reset`) eseguita mentre l'admin è loggato
  la innescherebbe; l'unica mitigazione è il `SameSite` **di default** del cookie (non impostato
  esplicitamente → dipende dalla versione di PHP, che dal 7.3 default `Lax` — che però **non** copre
  le POST top-level cross-site in tutti i casi). Idem `reset_votes.php`, `users.php` delete, e tutte
  le mutazioni del sito. → Box "perché un'azione distruttiva ha bisogno del CSRF anche se è gated".
- **GOLD positivo — backup automatico prima del distruttivo (divergenza DA SR-C13).** SR-C13 era
  "cura senza prevenzione" (emergency revert ma **zero backup/cron**). DIS **previene**:
  `reset_votes.php:20` e `reset_system.php:26` fanno `copy()` del `.sqlite` in `.data/backup_*.bak`
  prima di toccare i dati, dentro la cartella protetta di DIS-C1. È il pattern di sicurezza dati che a
  SitoRuntime mancava — su un sito molto più piccolo. → Box "il backup giusto-in-tempo prima di
  un'azione distruttiva" (contrappunto positivo a SR-C13).
- **GOLD — anti-frode voto: IP `REMOTE_ADDR` grezzo è qui un PREGIO (contrappunto a SR-C2).** SR-C2
  prendeva l'IP da `X-Forwarded-For` grezzo → rate-limit **spoofabile**. DIS usa `REMOTE_ADDR`
  (`votes.php:50`), che il client **non può falsificare** a livello TCP → la barriera IP/24h regge.
  Il rovescio: dietro CDN/proxy `REMOTE_ADDR` può essere l'IP del proxy (tutti gli utenti = stesso
  IP), e su NAT/rete condivisa un solo voto blocca l'intera rete. Trade-off, non bug. → Box
  "`REMOTE_ADDR` vs `X-Forwarded-For`: quando il grezzo è più sicuro".
- **GOLD privacy — voti con IP e UA in chiaro (≠ voter_hash di SPW-C11).** `votes.php:74` salva
  `ip_address` e `user_agent` **in chiaro** nella tabella `votes`. SPW-C11 (reazioni) usava
  `voter_hash = SHA256(IP+UA)` proprio per non conservare PII. Qui l'IP/UA grezzi restano nel DB:
  dato personale conservato senza necessità (il confronto anti-doppio-voto si potrebbe fare anche su
  hash). → Box "anti-frode senza conservare PII: il voter_hash" (ponte SPW-C11).
- **Cookie `dis_voted` puramente cosmetico.** `votes.php:28` blocca chi ha il cookie, ma è
  banalmente azzerabile (incognito/clear cookies). Onestamente è solo UX ("eviti il doppio click"),
  la sicurezza vera è l'IP/24h. → nota.
- **`participants.php` submit pubblica senza validazione/anti-abuso.** La registrazione
  (`participants.php:102-145`) valida solo la presenza di `name/email/audio_file` (`:122`): **nessun**
  controllo formato email, **nessuna** sanitizzazione, **nessun** rate-limit/CAPTCHA. Combinato con
  l'upload pubblico di DIS-C5, è un vettore di **iscrizioni-spam di massa** + storage flooding. → Box
  "il form pubblico che si fida di tutto" (ponte DIS-C5, C9).
- **`update_status`/`update_round` gated solo `isset(user_id)`, NON `isAdmin`.** `participants.php:153,
  205` proteggono con la sola presenza di sessione: un **editor** (non admin) può approvare/respingere
  partecipanti, inviare le email e spostarli nel round. Asimmetria di gate (come la news-editor di SR
  ma qui su azioni di concorso più sensibili). → nota ruoli, ponte C10.
- **Errore che fa leak (`$e->getMessage()`).** `auth.php:48`, `users.php:47`, `participants.php:148`
  rimandano al client il messaggio d'eccezione (dettagli DB). Stesso anti-pattern del `die()` di
  `db.php` (DIS-C1). → consolidare nel box "non rimandare l'eccezione al client".
- **`change_password` senza min-length e senza invalidazione sessioni.** `users.php:64-82`: nessun
  vincolo di lunghezza server-side (≠ SPW min12), e il cambio non invalida le altre sessioni (niente
  `session_version`; SR lo simulava client-side, DIS non fa nulla). → nota.

## 5. Estetica / UX (moderna ma funzionale)

- **Conferma a due passi sul reset totale** (`reset_system.php:14-20`): senza `confirm_reset` lo
  script spiega cosa farà e non esegue. Piccola rete di sicurezza UX su un'azione irreversibile.
- **Messaggi di voto parlanti e in italiano** ("Le votazioni sono chiuse.", "Seleziona da 1 a 3
  preferenze.", "Hai già votato da questo IP oggi. Riprova domani.", `votes.php:21,36,61`): l'utente
  capisce sempre perché è stato bloccato.
- **Email del festival con voce editoriale forte** (`participants.php:27-60`): i template di conferma/
  approvazione/rifiuto sono scritti in tono comico-dissacrante ("il server ha appena ingerito la tua
  candidatura", "Purtroppo sei dei nostri"). La sicurezza/registrazione qui è anche **brand voice**
  (la logica email = C9, qui notata perché vive in `participants.php`).
- **Login enumeration-safe**: messaggio unico "Invalid credentials" (`auth.php:29`) senza distinguere
  utente inesistente da password errata — l'unica buona prassi di sicurezza presente "di serie".

## 6. Differenze rispetto agli altri siti

Confronto a **TRE**: DIS-C2 (SQLite vivo, voto pubblico) vs SPW-C2 e SR-C2 (MySQL migrati).

| Aspetto | SimonePizziWebSite (SPW-C2) | SitoRuntime (SR-C2) | **DISINTELLIGENZA (questa card)** |
|---|---|---|---|
| **Anti-CSRF** | Origin/Referer vs SITE_URL | token sincronizzato `X-CSRF-Token` | **ASSENTE** (nessuna difesa CSRF) |
| **Gate** | unico `Auth::check()` | componibile `isLoggedIn`/`isAdmin`+`validateCsrf` | **inline grezzo** `isset($_SESSION['user_id'])` per-ramo |
| **Ruoli** | uno (loggato=admin) | admin/editor | **admin/editor** (come SR) |
| **`username` in sessione** | sì | **no** (→ author 'Admin') | **sì** |
| **Cookie hardening** | HttpOnly+Secure+SameSite | HttpOnly+SameSite (no Secure) | **nessuno esplicito** (default php.ini) |
| **Anti session-fixation** | sì (`regenerate_id`) | no | **no** |
| **Rate-limit login** | tabella DB `login_attempts` | file `.cache/ratelimit` 5/15min | **ASSENTE** |
| **Recovery/`session_version`** | completo | assente | **assente** |
| **Seeding admin** | random stampata 1 volta | hardcoded `runtime2026` (ricreabile) | **nessuno** (admin solo nel `.sqlite`) |
| **Errore → client** | generico + log | generico | **`$e->getMessage()`** (leak) |
| **CORS** | chiusa same-origin | aperta allowlist 4 origini | **nessuna** (same-origin via .htaccess) |
| **HTTPS/HSTS** | 301 + HSTS | solo HSTS | **niente** (né redirect né HSTS) |
| **Anti-frode voto** | — (reazioni: `voter_hash` SHA256, C11) | — | **cookie + IP/24h (REMOTE_ADDR grezzo) + master switch; IP/UA in CHIARO** |
| **IP per il rate-limit** | `getClientIp()` anti-spoof | `X-Forwarded-For` grezzo (spoofabile) | **`REMOTE_ADDR` grezzo** (non spoofabile, NAT-collision) |
| **Backup pre-distruttivo** | backup fuori docroot (C12) | **assente** (SR-C13: cura senza prevenzione) | **sì**: `copy()` del `.sqlite` in `.data/` prima del reset |

**Sintesi.** DIS-C2 è il perimetro **più debole sull'identità** (zero CSRF, zero rate-limit, cookie
di default, niente fixation/recovery, admin non bootstrappabile) — la naturale prosecuzione del
"grado zero" di DIS-C1. Ma ha **due tratti propri di valore**: (1) un **anti-frode voto** reale e ben
congegnato per un'azione *pubblica* (master switch difensivo + IP/24h con `REMOTE_ADDR` non
spoofabile — paradossalmente più robusto del rate-limit *autenticato* di SR perché non si fida di
XFF), con però il difetto privacy dell'IP/UA in chiaro (che SPW-C11 risolveva con `voter_hash`); e
(2) il **backup automatico prima del distruttivo**, esattamente la prevenzione che mancava a SR-C13.
Il rischio sistemico è la combinazione **azioni distruttive/pubbliche + zero CSRF + zero rate-limit**:
su un sito-festival aperto al pubblico (voto, registrazione, upload di DIS-C5) la superficie d'abuso è
ampia.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **L'auth minima**: cosa resta togliendo CSRF/rate-limit/fixation/recovery | Cap. "Security & Auth": il terzo gradino (DIS) sotto SR e SPW (alto valore) |
| **L'admin che vive solo nel DB** (nessun seeding nel repo) | Box "bootstrap dell'admin: random / hardcoded / inesistente" (ponte DIS-C1, SR-C1) |
| **Anti-frode voto pubblico a strati** (master switch + cookie + IP/24h) | Cap. "Festival logic": come si difende un voto pubblico (ponte C10) |
| **`REMOTE_ADDR` vs `X-Forwarded-For`** | Box "quando l'IP grezzo è più sicuro" (contrappunto diretto a SR-C2) |
| **Anti-frode senza PII: il `voter_hash`** | Box "votare in anonimato: hash invece di IP in chiaro" (ponte SPW-C11) |
| **Backup just-in-time prima del distruttivo** | Box "prevenzione vs cura" (contrappunto positivo a SR-C13) |
| **CSRF anche sulle azioni gated/distruttive** | Box "perché il cookie da solo non basta su un reset" |
| **Il form pubblico che si fida di tutto** (registrazione senza validazione/limit) | Box "validare e limitare gli input pubblici" (ponte DIS-C5, C9) |
| **Master switch difensivo sulle due forme del booleano** | Box "difendersi dalla propria seed incoerente" (ponte DIS-C1) |
| **Errore d'eccezione rimandato al client** | consolidare nel box "non fare leak dell'eccezione" (DIS-C1) |

## 8. Note / domande aperte

- **Puntatori ad altri cluster** (annotati qui, NON mappati in questa card):
  - **Logica festival** (conteggi, round, stats, master switch come *funzione*) → **C10**: qui ho
    mappato solo l'aspetto **sicurezza/identità/anti-frode** del voto e della registrazione; il flusso
    completo (approvazione, round, classifiche) è C10. `update_status`/`update_round` gated solo
    `isset(user_id)` (non isAdmin) → rilievo ruoli per C10.
  - **Email** (`sendEmail`, template, `mail()` nativa, `INSERT OR IGNORE` newsletter all'approvazione)
    in `participants.php` → **C9** (Newsletter & Email): qui solo notato che la registrazione le
    innesca. Consenso/GDPR all'iscrizione newsletter = C9.
  - **Upload pubblico** (`audio_file` arriva da `upload.php` type=audio_participant) → **C5** (già
    mappato): la catena RCE/DoS di DIS-C5 si salda qui con la registrazione pubblica senza limiti.
  - **`reset_system`/`reset_votes`/`migrate_media`/`update_db_*`** come *meccanica DB/manutenzione* e
    cronologia → eventuale **DIS-C13**: qui solo l'aspetto auth (gate admin + backup + niente CSRF).
  - **`.htaccess`** generale → hardening = parte di C2 ma già descritto in DIS-C1 (deny `.sqlite`/
    `.bak`, routing); qui ri-contestualizzato per l'**assenza** di HSTS/redirect HTTPS/PHP-off.
- **Da verificare in C10:** lo schema `votes` (`participant_id`/`session_id`/`ip_address`/`user_agent`)
  e `vote_count` denormalizzato — coerenza tra i due, e se esiste un'altra via di voto oltre
  `votes.php`. Verificare anche se `in_current_round` è gestito solo da `participants.php?update_round`.
- **Da verificare:** il comportamento reale del cookie di sessione dipende dal `php.ini` dell'hosting
  (default `cookie_httponly`/`samesite`): non impostandolo, DIS eredita i default del server — da
  segnalare come dipendenza implicita.
- **Conferma cross-card:** la difesa `'1' || 'true'` di `isVotingActive` (`votes.php:14`) e lo stesso
  pattern in `participants.php:110` confermano l'incoerenza delle seed dei settings di DIS-C1.
- Versione del sito al momento della mappatura: **0.5.x** (`package.json`).
