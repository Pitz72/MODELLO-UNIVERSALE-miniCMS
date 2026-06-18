# Scheda di Sintesi — S1-C2 — Security & Auth

> **Stato:** COMPLETATO
> **Cluster FASE 2:** S1-C2 · **Data:** 2026-06-19 · **Commit:** _(in corso)_
> **Fonti (card di mappatura, in particolare i §6):** SPW-C2, SR-C2, DIS-C2 (+ SPW-C11 per il `voter_hash`, DIS-C10 per il contesto del voto, FDCA-DIFF §3 "backend byte-identico a DIS")
> **Capitoli del libro toccati:** CAP 10 (Security & Auth) — principale · ponti a CAP 13 (Newsletter), CAP 11 (SEO/.htaccess), CAP 17 (Votazioni & anti-frode) → vedi §4

---

## 0. In una frase
La sicurezza è l'unica lente in cui i tre siti **non** scalano in parallelo all'ingegnerizzazione del
backend: lo stesso scheletro thin-stack (PHP nativo, sessione cookie, `.htaccess`) regge **tre
gradini di difesa decrescenti** — perimetro maturo (SPW) / parziale (SR) / grado-zero (DIS) — ma il
sito col backend più ingegnerizzato (SR) **non** è il più sicuro, e il sito più debole (DIS) è
l'unico a portare due idee di valore proprio (anti-frode di un'azione *pubblica* e backup
pre-distruttivo). La lezione del capitolo è leggere ogni difesa come una **scala di sottrazione**:
cosa resta — e cosa si rompe — quando togli un flag, un token, un contatore.

## 1. Il pattern comune — la filosofia "thin stack" su questa lente

Sotto le tre implementazioni divergenti, il perimetro di sicurezza dei tre siti è **lo stesso
oggetto**, e condivide cinque tratti che il libro deve raccontare prima delle varianti.

**1) Niente libreria di auth: solo primitive PHP native.** Nessun Passport, nessun pacchetto JWT,
nessun framework di sessione. Tutto poggia su `session_*`, `password_hash`/`password_verify`,
`random_bytes`, `hash_equals` e sulle regole Apache nei `.htaccess`. L'autenticazione è "fatta a
mano" — ed è la scelta fondante che rende ogni differenza tra i siti una scelta *visibile*, non una
configurazione nascosta dentro un vendor.

**2) Sessione cookie + `password_verify`: lo zoccolo identico.** Tutti e tre aprono una sessione PHP
nativa, cercano l'utente per `username`, verificano con `password_verify` contro un hash
`PASSWORD_DEFAULT`, e popolano `$_SESSION`. Il sistema non conosce mai la password in chiaro. È il
minimo comun denominatore che funziona ovunque allo stesso modo.

**3) Il gate è "una manciata di righe all'inizio dell'endpoint".** Non c'è middleware né router: la
protezione di un endpoint è qualche riga in cima al ramo mutativo che pretende una sessione valida
prima di toccare i dati. È la versione thin-stack del middleware — ma *quanto* fa quella manciata di
righe (solo sessione? + CSRF? + ruolo? + invalidazione?) è il primo grande asse di divergenza (§2).

**4) Difesa "JSON-first" anche sugli errori di sicurezza.** Un accesso negato non produce una pagina
di errore Apache: si imposta un codice HTTP semanticamente corretto (`401`/`403`/`429`) e si
restituisce `{status|success, message|error}`. Il frontend reagisce per codice. (Su *quanto* il
messaggio sia generico — e quindi sicuro — i siti divergono: vedi il leak di DIS in §3.)

**5) Hardening a livello server via `.htaccess`.** Tutti hanno almeno un `.htaccess` che mette header
di sicurezza e nega file sensibili. È il secondo strato — fuori dall'applicazione — e anche qui la
copertura va dal completo (HTTPS+HSTS+CSP+PHP-off) al minimo (deny di due estensioni).

A questi si aggiunge un tratto **negativo** condiviso: nessuno dei tre conserva un audit-log degli
accessi, e in due casi su tre il rate-limit del login non vive nel database (file o niente). Il
perimetro è sottile per costruzione — la domanda del capitolo è *quanto* sottile si può andare.

## 2. Le varianti per sito (tabella unica, deduplicata)

| Asse | SimonePizziWebSite | SitoRuntime | DISINTELLIGENZA | *(FDCA)* |
|---|---|---|---|---|
| **Modello di gate** | **unico** `Auth::check()` (sessione + CSRF + `session_version` insieme) | **componibile** `isLoggedIn()`/`isAdmin()` + `validateCsrf()` per-ramo | **inline grezzo** `isset($_SESSION['user_id'])` per-ramo | = DIS |
| **Anti-CSRF** | check `Origin`/`Referer` vs `SITE_URL` | **token sincronizzato** `X-CSRF-Token` + `hash_equals` | **ASSENTE** | = DIS |
| **Cookie di sessione** | HttpOnly + **Secure** + SameSite=**Strict**, centralizzati in `auth_helper` | HttpOnly + SameSite=Strict, **niente `Secure`** | **default `php.ini`** (nessun flag impostato) | = DIS |
| **Anti session-fixation** | **sì** (`session_regenerate_id(true)`) | no | no | = DIS |
| **`session_version` (logout-everywhere)** | **sì**, fail-closed sul DB | assente | assente | = DIS |
| **Recovery / reset password** | **completo** (`password_resets`, token 32B, scad. 1h, email da `SITE_URL`, enumeration-safe) | assente (solo `change_password` autenticato) | assente (solo `change_password`) | = DIS |
| **Ruoli** | uno (loggato = admin) | admin / editor | admin / editor (**ma gate spesso role-blind**, vedi §3) | = DIS |
| **Rate-limit login** | tabella **DB** `login_attempts` (riusata, namespacing) | **file** `.cache/ratelimit/<md5(ip)>.json` 5/15min + `sleep(1)` | **ASSENTE** | = DIS |
| **IP per il rate-limit** | `getClientIp()` anti-spoof | **`X-Forwarded-For` grezzo** → spoofabile | **`REMOTE_ADDR` grezzo** → non spoofabile (NAT-collision) | = DIS |
| **Seeding admin** (ponte S1-C1) | **random**, stampata una volta | **hardcoded `runtime2026`** (ricreabile; `.htaccess` nega l'accesso) | **nessuno**: admin vive solo nel `.sqlite` | = DIS |
| **Errore → client** | generico + `error_log` | generico, **niente log** | **`$e->getMessage()`** (leak) | = DIS |
| **CORS** | chiusa same-origin (`connect-src 'self'`; `Allow-Methods` cosmetico) | **aperta**: allowlist 4 origini + `Vary`, **no `Allow-Credentials`** | nessuna (same-origin via `.htaccess`) | = DIS |
| **HTTPS** | **301** + HSTS | **solo HSTS** (nessun redirect) | niente (né redirect né HSTS) | = DIS |
| **`.htaccess` hardening** | HTTPS/HSTS/CSP + **PHP-off negli upload** + `.data` deny | HSTS/CSP/X-Frame **DENY** + **deny by-prefix** script manutenzione, **no PHP-off upload** | deny **solo** `*.sqlite`/`*.bak`; gli `update_db_*` **non** protetti | = DIS |
| **Anti-frode azione pubblica** | reazioni: `voter_hash` SHA256(IP+UA) + rate-limit a 2 strati (C11) | — (nessuna azione pubblica scrivente) | **voto**: cookie cosmetico + IP/24h + master switch; **IP+UA in chiaro** | = DIS |
| **CSRF su azioni distruttive** | gated + CSRF | gated + `validateCsrf` | **gated ma SENZA CSRF** (reset a un clic) — **ma** backup pre-distruttivo | = DIS |

**Lettura della tabella.** Emerge la stessa scala a tre gradini di S1-C1, ma **ribaltata
nell'ordine di robustezza**. Sull'asse *maturità dell'identità* l'ordine è netto: **SPW** è il più
completo (Secure cookie, anti-fixation, `session_version`, recovery, IP anti-spoof), **SR** è
intermedio (ruoli e token CSRF ma cookie senza `Secure`, niente fixation, rate-limit bypassabile),
**DIS** è il grado-zero (niente CSRF, niente rate-limit, cookie di default, admin non
bootstrappabile). Ma due colonne rompono la scala. La prima è l'**IP grezzo**: ciò che in SR è un
buco (`X-Forwarded-For` falsificabile) in DIS è un *pregio* (`REMOTE_ADDR` non spoofabile), perché il
modello d'abuso è diverso — login da forzare vs voto pubblico da non duplicare. La seconda è il
**backup pre-distruttivo**: il sito più debole è l'unico a fare `copy()` del DB prima di un reset,
esattamente la prevenzione che mancava al flagship degli incidenti (SR-C13). **Più ingegnerizzato ≠
più sicuro, e più sicuro ≠ più completo su ogni singolo punto:** è la tesi forte del capitolo.

**FDCA è fuori scala.** Il fork ha il backend PHP **byte-identico** a DISINTELLIGENZA (FDCA-DIFF §3,
verificato file per file): `auth.php`, `votes.php`, `users.php`, `reset_*.php` — verbatim. Eredita
l'intera auth grado-zero **immutata** (zero CSRF, zero rate-limit, reset a un clic, IP/UA in chiaro):
è il caso-limite del *forking che moltiplica il debito di sicurezza* anziché ripagarlo, e vive nella
scheda dedicata al fork, non qui.

## 3. GOLD & box problemi-soluzioni

- **I tre gradini della difesa CSRF** — *(SPW vs SR vs DIS)* — il GOLD portante del cluster. Lo stesso
  problema (impedire che un sito terzo invii richieste mutative con il cookie dell'utente) risolto su
  tre livelli: **check `Origin`/`Referer`** vs `SITE_URL` (SPW — server-side, zero handshake col
  client, copre *automaticamente* ogni endpoint perché vive dentro `Auth::check()`); **token
  sincronizzato** `X-CSRF-Token` + `hash_equals` (SR — il pattern "da manuale", ma richiede che il
  client faccia l'handshake e che *ogni* ramo ricordi `validateCsrf()`); **niente** (DIS — le
  mutazioni sono protette dal solo cookie di sessione). Sottotesi: la soluzione più "da manuale" (SR)
  è anche la più facile da dimenticare, perché dipende dalla disciplina per-ramo; quella più semplice
  (SPW) copre di più proprio perché è centralizzata. → Box "CSRF nel thin stack: Origin/Referer, token
  sincronizzato, o niente".

- **I tre (o quattro) flag del cookie: cosa succede se ne togli uno** — *(SPW completo / SR senza
  Secure / DIS default)* — SPW imposta HttpOnly + **Secure** + SameSite=**Strict** prima di
  `session_start()`, in un file *condiviso* (regressione "cookie debole" corretta in v1.19.0 spostando
  gli `ini_set` da `auth.php` ad `auth_helper.php`). SR omette `Secure` **e** non forza il redirect a
  HTTPS — applica solo HSTS, che protegge *dopo* la prima visita HTTPS riuscita: c'è una finestra
  reale su HTTP al primo accesso. DIS non imposta **nessun** flag: il comportamento dipende interamente
  dal `php.ini` dell'hosting (dipendenza implicita silenziosa). → Box "I flag del cookie di sessione +
  perché HSTS non è il redirect HTTPS" (alto valore).

- **Dove vive il contatore brute-force: DB / file / da nessuna parte** — *(SPW vs SR vs DIS)* — stessa
  difesa (limitare i tentativi di login), tre sedi: tabella **DB** `login_attempts`, riusata anche dal
  recovery con namespacing della chiave (SPW); **file** `.cache/ratelimit/<md5(ip)>.json` 5/15min con
  `sleep(1)` anti-enumerazione, coerente con l'assenza di `login_attempts` nello schema MySQL di SR;
  **niente affatto** (DIS — il login si può martellare). → Box "Il contatore brute-force: file vs DB
  vs assenza".

- **Fidarsi dell'IP del client: quando il grezzo è più sicuro** — *(SPW vs SR vs DIS)* — il box più
  controintuitivo. SPW usa `getClientIp()`: si fida di `REMOTE_ADDR` se pubblico, accetta
  `X-Forwarded-For` (validato) **solo** dietro proxy interno → anti-spoof. SR prende
  `X-Forwarded-For` grezzo *e per primo* → un attaccante lo varia a ogni richiesta e il lockout non
  limita nulla. DIS usa `REMOTE_ADDR` grezzo per la barriera voto: **non** falsificabile a livello TCP
  → la barriera IP/24h regge (col rovescio NAT/CDN: stesso IP per molti utenti). Lezione: l'IP "giusto"
  dipende dal *modello d'abuso*, non da una regola fissa. → Box "Fidarsi dell'IP: il rate-limit che non
  limita" (contrappunto diretto SR↔DIS).

- **Anti-frode di un'azione PUBBLICA: il voto del festival** — *(DIS, con ponte a SPW-C11)* — DIS deve
  difendere un'azione che *non* è autenticata (il pubblico vota). La difesa è a strati con una sola
  barriera reale: master switch `voting_active` (difensivo su `'1' || 'true'` per coprire la propria
  seed incoerente, ponte DIS-C1) + cookie `dis_voted` **cosmetico** (azzerabile) + validazione 1–3
  preferenze + `in_current_round=1` + **la barriera vera**: `COUNT(DISTINCT session_id) ... WHERE
  ip_address=? AND created_at > datetime('now','-24 hours')`. Il parallelo è SPW-C11 (reazioni
  anonime), che risolve lo stesso problema "1 azione per identità" con `voter_hash = SHA256(IP+UA)` e
  un rate-limit a **due strati** (per-hash 20/min + solo-IP 30/min, riusando `login_attempts`
  namespaced `rea:`). → Box "Difendere un'azione pubblica: master switch + barriera IP" (il
  trattamento pieno va in CAP 17).

- **Anti-frode senza conservare PII: il `voter_hash`** — *(DIS anti-pattern vs SPW-C11 pattern)* — DIS
  salva `ip_address` e `user_agent` **in chiaro** nella tabella `votes`. SPW-C11 ottiene lo stesso
  anti-doppio-voto memorizzando solo `SHA256(IP+UA)`: il confronto regge, ma il dato personale non
  viene conservato. Stessa esigenza funzionale, due posture privacy opposte. → Box "Votare in
  anonimato: hash invece di IP in chiaro" (GDPR-by-design, ponte SPW-C11).

- **CSRF anche sulle azioni gated e distruttive: il reset a un clic** — *(DIS)* — `reset_system.php` e
  `reset_votes.php` sono gated admin **ma senza CSRF**: una `POST` cross-site verso `reset_system.php`
  innescata mentre l'admin è loggato cancella **tutti** i partecipanti, i voti e gli audio.
  Mitigazione unica: il `SameSite` *di default* del cookie (non impostato → dipende dalla versione di
  PHP). Contrappunto **positivo** dentro lo stesso file: `copy()` del `.sqlite` in `.data/backup_*.bak`
  **prima** del `DELETE` — la prevenzione che mancava a SR-C13 ("cura senza prevenzione"). → Box
  "Perché un'azione gated ha comunque bisogno del CSRF" + "Il backup giusto-in-tempo".

- **Credenziali di default: random / hardcoded / omessa** — *(SPW vs SR vs DIS — chiude il box aperto
  in S1-C1)* — lo stesso punto (il primo admin) risolto in tre modi, qui visto dal lato *sicurezza*:
  SPW genera una password **random stampata una volta** (corretto); SR la **hardcoda a `runtime2026`**
  nel codice committato — ricreabile da `fix_users_table.php` ma con il `.htaccess` che ne nega
  l'accesso HTTP, *e* senza alcun flusso che obblighi a cambiarla (account indovinabile se nessuno usa
  `change_password`); DIS **omette del tutto** il seeding → niente default indovinabile, ma l'admin
  vive solo nel `.sqlite` (non bootstrappabile). → Box "Credenziali di default: cosa NON fare" (qui si
  chiude definitivamente, era anticipato in S1-C1).

- **Gate role-blind: l'editor che può fare l'admin** — *(DIS, eco in SR)* — DIS ha i ruoli
  admin/editor ma diversi rami pubblici sensibili (`participants.php?update_status`/`update_round`)
  sono gated **solo** da `isset($_SESSION['user_id'])`, **non** da `isAdmin()`: un editor approva/
  respinge partecipanti, manda le email e sposta i round. È il rischio strutturale del gate
  *componibile/inline* (vale anche per SR, dove `list_users`/`create_user` stanno *prima* del blocco
  401 e si autoproteggono col solo check di ruolo): la sicurezza dipende dall'ordine dei rami e dalla
  disciplina, non da un gate unico. → Box "Middleware o disciplina? Il gate che si dimentica" (ponte a
  CAP 17 per le conseguenze sul festival).

- **Non rimandare l'eccezione al client** — *(DIS; consolida con DIS-C1)* — `auth.php`, `users.php`,
  `participants.php` rispediscono `$e->getMessage()` al client (dettagli DB): stesso anti-pattern del
  `die()` con leak di `db.php` (S1-C1). Information disclosure gratuita. → confluisce nel box "Errori
  di sicurezza: parlanti per l'utente, opachi per l'attaccante".

## 4. Mappa → capitolo/i del libro

| Materiale della scheda | Capitolo esistente | Azione |
|---|---|---|
| Gate del thin stack: `Auth::check()` unico / componibile / inline grezzo | **CAP 10 — Security & Auth §1–2** | **nuovo §**: oggi il capitolo non confronta i tre modelli di gate |
| **CSRF a tre gradini** (Origin/Referer / token sincronizzato / niente) | **CAP 10** | **nuovo box**: oggi CAP 10 **non parla affatto di CSRF** (gap importante) |
| I flag del cookie + anti session-fixation + `session_version` | **CAP 10 §1.1** | **aggiorna + nuovo box**: §1.1 oggi è una prescrizione, va confrontata con la realtà (vedi correzioni) |
| Recovery/reset password (token, scadenza, email da `SITE_URL`, enumeration-safe) | **CAP 10** | **nuovo §**: assente oggi; solo SPW lo implementa |
| Rate-limit brute-force: DB / file / assenza + IP anti-spoof | **CAP 10 §3** | **aggiorna**: §3 oggi riduce tutto a `sleep(1)`; va ampliato a sede del contatore + IP |
| `.htaccess`: HTTPS/HSTS/CSP, deny by-prefix, PHP-off upload | **CAP 11 — SEO/.htaccess** + **CAP 10 §4** | **aggiorna**: la parte header/HTTPS è cross con CAP 11; il deny by-prefix è nuovo |
| Protezione del DB-a-file (`.data/` + `.htaccess` runtime) + script `update_db_*` non protetti | **CAP 10 §4** | **aggiorna**: §4 è generico; aggiungere la generazione runtime (DIS) e il gap update_db |
| Rate-limit riusato anti-mail-bombing (riuso `login_attempts`) | **CAP 13 — Newsletter** (ponte) | **nuovo box** (rimando da CAP 10): SPW lo ricicla, SR/DIS no |
| **Anti-frode voto**: master switch + IP/24h + `REMOTE_ADDR` + CSRF-su-reset + backup | **CAP 17 — Votazioni & Anti-Frode** | **aggiorna/nuovo box**: trattamento pieno qui; CAP 10 tiene solo il box cross-cutting |
| **`voter_hash`** anti-frode senza PII | **CAP 17** + **CAP 19 (Reactions)** | **nuovo box**: ponte SPW-C11 ↔ DIS-voto |
| Credenziali di default: random/hardcoded/omessa | **CAP 10 §3** | **nuovo box** (chiude quello anticipato in S1-C1) |

**Correzioni al testo attuale (la mappatura smentisce / disallinea il libro):**
- **CAP 10 §1.1** presenta come "il sistema deve" un cookie con `cookie_secure = 1` e
  `cookie_samesite = 'Lax'`. È una **prescrizione, non una fotografia**, e su due punti diverge dalla
  realtà: (a) il `SameSite` reale di chi lo imposta è **`Strict`** (SPW *e* SR), non `Lax`; (b) **solo
  SPW** imposta davvero tutti e tre i flag — SR omette `Secure`, DIS non imposta nulla. Da riallineare:
  separare "ciò che il Modello *raccomanda*" da "ciò che i siti *fanno*", e usare `Strict` come valore
  reale (con nota sul trade-off `Lax`/`Strict`).
- **CAP 10 §1.2** mostra `check_auth` che legge `$_SESSION['username']` come se fosse sempre presente.
  In **SR** lo `username` **non** viene mai salvato in sessione → `check_auth` ritornerebbe
  `username: null` e l'autore degli articoli ripiega su `'Admin'`. In SPW e DIS è presente. Da
  segnalare come incoerenza reale, non come dato garantito.
- **CAP 10 §3 "Brute Force Mitigation"** riduce la difesa al solo `sleep(1)`. È **incompleto e
  SR-centrico**: `sleep(1)` è l'accorgimento di SR; la difesa vera è il **lockout** (SPW: tabella
  `login_attempts`, `429` dopo 5 tentativi / SR: file 5/15min / DIS: **niente**) e soprattutto **da
  quale IP** lo si conta (il box anti-spoof). Da ampliare.
- **CAP 10 §6** (il caso "DDoS a Runtime Radio") è materiale eccellente ma è in realtà **SEO/anti-DDoS
  da bot social** — appartiene più a CAP 11 (SEO pre-rendering, il vettore è proprio l'entry-point
  PHP). In CAP 10 resta pertinente solo la lezione trasversale "l'UA non è un gatekeeper di sicurezza".
  Da valutare se spostarlo/duplicarlo in FASE 3 (decisione di S3, non di questa scheda).

## 5. Cosa si scarta / dedup

- **Ripetizioni fuse:** i §6 delle tre card raccontavano la stessa scala da tre punti di vista (SPW
  "io vs SR", SR "io vs SPW" con tabella a 14 righe, DIS "io vs entrambi" con tabella a 15 righe). Qui
  la tabella comparativa è scritta **una volta sola** dal punto di vista neutro della scala a tre
  gradini, deduplicata.
- **Dettaglio per-sito che NON entra nel libro:** numeri di riga esatti, le finestre precise
  (900s, `+1 hour`), il nome `dis_voted` del cookie, la lista completa dei prefissi nel `FilesMatch`
  di SR, la sottigliezza `Allow-Methods` senza `Allow-Origin` (resta nelle card come fonte; nel libro
  basta il *pattern*).
- **Materiale che appartiene ad altre schede (per evitare doppioni a valle):**
  - flusso completo del festival (approvazione, round, classifica, `vote_count` denormalizzato,
    report dormiente) → **S1-C10 (Festival Logic)**; qui solo l'aspetto *sicurezza/identità/anti-frode*
    del voto e della registrazione.
  - motore email (`mail()` nativa vs PHPMailer/SMTP, double opt-in, `unsubscribe_token`, header
    injection) → **S1-C9 (Newsletter & Email)**; qui solo il *riuso del rate-limit* e l'anti-mail-bombing
    come ponte.
  - storia migratoria degli script (`fix_users_table` fossile SQLite, migrazioni a caldo, schema
    `password_resets` sparito con le migration cancellate) → **S1-C13 (DB Evolution)**; qui solo il
    *meccanismo* auth (il fossile ricrea l'admin di default), non la cronologia.
  - `AdminLayout`/guard-componente lato React, RBAC della sidebar → **S1-C12 (Admin Dashboard)**; qui
    solo il gate *server-side*.
  - upload pubblico non autenticato (catena RCE di DIS-C5) e form di registrazione senza validazione →
    **S1-C5 (Media)** e **S1-C10**; qui citati solo come superficie d'abuso che si salda all'auth
    grado-zero.
