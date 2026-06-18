# Scheda di Sintesi — S1-C1 — Backend Core & Bootstrap

> **Stato:** COMPLETATO
> **Cluster FASE 2:** S1-C1 · **Data:** 2026-06-19 · **Commit:** _(in corso)_
> **Fonti (card di mappatura, in particolare i §6):** SPW-C1, SR-C1, DIS-C1 (+ nota FDCA-DIFF §3 "backend byte-identico a DIS")
> **Capitoli del libro toccati:** CAP 3 (Database Strategy), CAP 5 (Backend Logic PHP), CAP 14 (Database Evolution) → vedi §4

---

## 0. In una frase
Tutti e tre i siti hanno lo **stesso scheletro** — PHP puro senza framework, un singleton PDO per
richiesta, config fuori da git, init "fossile" dopo che la verità dello schema si è spostata altrove
— ma lo declinano su tre gradini di una scala: **SQLite grado-zero** (DIS), **MySQL essenziale**
(SPW), **MySQL ingegnerizzato** (SR). La lezione del capitolo Backend Core è proprio questa scala:
*quanto puoi togliere — o aggiungere — allo stesso scheletro prima che cambi natura.*

## 1. Il pattern comune — la filosofia "thin stack" su questa lente

Sotto le differenze, il backend core dei tre siti è **lo stesso oggetto**. Cinque tratti lo
definiscono, ed è questa la spina dorsale che il libro deve raccontare prima di ogni variante.

**1) Niente framework: ogni endpoint è un file PHP autonomo.** Non c'è Laravel, non c'è un router
centrale, non c'è un kernel. Ogni file in `public/api/` include all'avvio i suoi mattoni e gestisce
da sé la richiesta. È la scelta fondante del miniCMS: il "thin stack" è letteralmente sottile.

**2) Connessione = singleton PDO memoizzato.** Il cuore è sempre una classe `Database` con
`private static $pdo` e un metodo `connect()` che apre la connessione **una sola volta per
richiesta** e poi restituisce sempre la stessa istanza. Niente pool, niente ORM. Identico nei tre
siti, parola per parola nello spirito.

**3) Errori di connessione "JSON-first".** Un guasto del DB non deve mai produrre uno stack-trace in
pagina: il pattern canonico è intercettare la `PDOException`, impostare un codice HTTP e restituire
un messaggio generico. (Su *quanto* generico — e quanto sicuro — i siti divergono: vedi §3, è uno dei
GOLD.)

**4) Configurazione separata dal codice e fuori da git.** I segreti non stanno nel sorgente
versionato: vivono in un file ignorato da git, affiancato da un template committato
(`*.example`). È il principio dei "dodici fattori" applicato **senza librerie** — con una sola,
radicale eccezione: chi usa SQLite non ha *nessun* segreto da gestire (vedi §2).

**5) L'init di scaffolding è un fossile.** In tutti e tre i siti lo script che "dovrebbe" creare lo
schema da zero (`init_db.php`) è **disallineato dalla realtà**: la fonte di verità dello schema si è
spostata altrove (in un migratore, in un file dedicato, o direttamente nel file `.sqlite`), ma il
vecchio init è rimasto lì come abbozzo ingannevole. È un pattern cross-confermato sui tre siti, e una
delle lezioni più solide del cluster: **dopo che lo schema evolve, l'init va riscritto o rimosso, non
lasciato ambiguo.**

A questi si aggiungono due dettagli minori ma onnipresenti: il **timezone forzato** per-richiesta
(`date_default_timezone_set('Europe/Rome')`) per neutralizzare l'orario del server d'hosting, e il
**versionamento dello schema senza un registro** (nessuna tabella `schema_version` in nessuno dei
tre siti).

## 2. Le varianti per sito (tabella unica, deduplicata)

| Asse | SimonePizziWebSite | SitoRuntime | DISINTELLIGENZA | *(FDCA)* |
|---|---|---|---|---|
| **Motore DB** | MySQL (migrato v1.7.0) | MySQL (migrato 24/02/2026) | **SQLite VIVO** (mai migrato) | = DIS |
| **Config / segreti** | `config.php` + `define()` (gitignorato) + `config.example.php` | `db_credentials.php` *loader* → `.env` via `parse_ini_file()` + `.env.example` | **nessuna**: path file hardcoded in `db.php` | = DIS |
| **Hub segreti** | DB + `BACKUP_CRON_SECRET` + `SITE_URL` | DB + `TELEGRAM_BOT_TOKEN` + blocco `SMTP_*` | — (SQLite non ha credenziali) | = DIS |
| **Costruzione "connessione"** | DSN MySQL intero in config | DSN via `sprintf()` con `port` | `new PDO("sqlite:".$path)` (un file) | = DIS |
| **Opzioni PDO** | ERRMODE + FETCH + `EMULATE_PREPARES=>false` (base) | + `ATTR_TIMEOUT=>5` + `MYSQL_ATTR_INIT_COMMAND` (paranoica) | **solo** ERRMODE + FETCH via `setAttribute()` (minimale) | = DIS |
| **Errore connessione** | `500` + JSON + `error_log` | `503` + JSON, **niente log** | **`die()` stringa grezza con `getMessage()`** (leak) | = DIS |
| **Prelude bootstrap** | inline in ogni file (`require db`+`auth_helper`+header) | **`cors.php` condiviso** (CORS+Content-Type+OPTIONS) | inline minimale, **niente CORS** (same-origin via `.htaccess`) | = DIS |
| **Apertura connessione** | *eager* (`$pdo = Database::connect()` in cima) | *lazy* (`getDB()` con `static`, **duplicata** per file) | *eager* | = DIS |
| **Posizione del DB** | server MySQL (fuori docroot per natura) | server MySQL | **file in `.data/` auto-creata** dentro la docroot | = DIS |
| **Protezione DB** | n/a (è un server) | n/a | `.htaccess` Deny **generato a runtime** + `<Files>` in `public/.htaccess` | = DIS |
| **Scaffolding schema "vivo"** | dentro il migratore `migrate_to_mysql.php` | file dedicato `init_mysql.php` + micro-migrazioni `migrate_*`/`fix_*` | catena `update_db_*` (8 file, idempotenti) | = DIS |
| **Init fossile** | `init_db.php` SQLite | `init_db.php` SQLite **+ seed reale 24 speaker** | `init_db.php` SQLite **parziale** (fermo a v0.3.6, admin elide) | = DIS |
| **Storia migrazioni** | (poca) | leggibile da **git** (→ SR-C13) | **nei nomi-file** `update_db_*` (git inutile: 4 commit) | = DIS |
| **Password admin default** | **random**, stampata una volta | **hardcoded `runtime2026`** | creazione admin **omessa** (vive solo nel `.sqlite`) | = DIS |
| **`SITE_URL` canonico** | **sì** (anti host-poisoning) | assente (`baseUrl` da `HTTP_HOST`) | assente (da `HTTP_HOST`) | = DIS |
| **Timezone** | forzato in **ogni** endpoint | solo `news.php`/`index.php` (incoerente) | solo `index.php` (incoerente) | = DIS |

**Lettura della tabella.** Emerge una scala su due assi. Sull'asse *motore/complessità*: DIS è il
**grado-zero** (SQLite cancella interi strati: config, segreti, charset di connessione, timeout di
rete), SPW è l'**essenziale pulito**, SR è il **più ingegnerizzato** (prelude condiviso, `.env`,
lazy DB, opzioni PDO rinforzate, scaffolding dedicato). Ma c'è un secondo asse, *robustezza dei
fondamentali*, dove l'ordine **non** coincide: SPW è il più solido (random password, `error_log`,
`SITE_URL` canonico, timezone ovunque), mentre SR — pur più ingegnerizzato — è più fragile su alcuni
punti (password hardcoded, niente log, niente `SITE_URL`, `getDB()` copia-incollata), e DIS è il più
fragile in assoluto sull'errore di connessione (`die()` con leak). **Più ingegnerizzato ≠ più
robusto:** è una delle tesi forti del capitolo.

**FDCA è fuori scala.** Il fork ha il backend PHP **byte-identico** a DISINTELLIGENZA (verificato
file per file, FDCA-DIFF §3): `db.php`, `init_db.php`, l'intera catena — verbatim. Non aggiunge una
variante al pattern; è un **caso di studio sul forking** (eredita tutto il debito immutato) che vive
nella scheda dedicata al fork, non qui.

## 3. GOLD & box problemi-soluzioni

- **L'init fossile dopo l'evoluzione dello schema** — *(SPW, SR, DIS — cross-confermato sui tre)* — il
  GOLD portante del cluster. In SPW e SR il fossile nasce da una **migrazione di motore**
  (SQLite→MySQL) che ha spostato la verità nel migratore/`init_mysql.php`; in DIS nasce **senza
  cambio di motore** — la verità è scivolata dentro il `.sqlite` e negli `update_db_*`, e l'init è
  rimasto un abbozzo *parziale* che ammette in un commento di aver omesso pezzi
  ("`[Admin creation ignored for brevity]`", fermo a v0.3.6 mentre il vivo è v0.5.4). → Box "Quando
  l'init mente". Lezione: dopo che lo schema evolve, l'init va riscritto o rimosso.

- **Credenziali di default: i tre modi (giusto, sbagliato, assente)** — *(SPW vs SR vs DIS)* — lo
  stesso punto del codice (creazione del primo admin) risolto in tre modi: SPW genera una password
  **random stampata una volta** (corretto); SR la **hardcoda a `runtime2026`** in chiaro nel codice
  committato, con tanto di "CHANGE THIS IMMEDIATELY!" (anti-pattern: credenziale prevedibile e
  versionata); DIS **omette del tutto** la creazione, così il primo admin vive solo nel `.sqlite`
  (non bootstrappabile, ma niente default indovinabile). → Box "Credenziali di default: cosa NON
  fare" (ponte a S1-C2 Security).

- **Le tre risposte all'errore di connessione** — *(SPW vs SR vs DIS)* — `500` + JSON + `error_log`
  (SPW, completo) / `503` + JSON ma **senza log** (SR, perde la diagnostica) / `die("Connection
  failed: ".$e->getMessage())` (DIS, **information disclosure**: espone path ed eccezione al client,
  non-JSON, niente codice HTTP). Tre gradini di degradazione, dal pulito al pericoloso. → Box "Come
  (non) gestire l'errore di connessione".

- **Nascondere il DB-a-file dentro la docroot** — *(DIS)* — pattern positivo e specifico di SQLite:
  al primo `connect()`, se `.data/` non esiste, il codice la crea con `mkdir()` e ci scrive dentro un
  `.htaccess` `Deny from all` — **la protezione è generata a runtime dall'app**, non pre-deployata,
  con `<Files>` in `public/.htaccess` come seconda rete. → Box "Il DB-a-file su hosting condiviso"
  (alto valore; si lega all'incidente WAL di SR-C13 / S1 futuro).

- **`SITE_URL` canonico vs `HTTP_HOST`** — *(solo SPW)* — solo SimonePizziWebSite definisce una
  costante `SITE_URL` e **non deriva mai** gli URL da `HTTP_HOST` (difesa contro host-header / link
  poisoning nelle email). SR e DIS prendono `baseUrl` da `HTTP_HOST`. → Box sicurezza, ponte a
  S1-C9 (Newsletter/email).

- **Versionare lo schema senza un registro** — *(tutti, con picco in DIS)* — nessuno dei tre ha una
  tabella `schema_version`. SR legge la storia da git; DIS la codifica **nei nomi dei file**
  (`update_db_0_1_3` → `0_1_4` → `v0.4.2` → `v0.5.4` → `security_move`), con idempotenza via
  `PRAGMA table_info`+`ALTER` o `INSERT OR IGNORE`. → Box "Migrazioni fai-da-te" (il grosso del tema
  evolutivo va però in S1 dedicata a C13/DB Evolution, qui solo il *meccanismo* di bootstrap).

- **Fuso orario forzato in modo incoerente** — *(SR, DIS)* — il timezone è forzato `Europe/Rome` ma
  solo in *alcuni* endpoint (in SR e DIS solo `index.php`/`news.php`), mentre la regola di visibilità
  confronta `published_at <= NOW` come stringhe → una soglia che si sposta col fuso. SR ha persino un
  `debug_time.php` che documenta l'incidente del separatore `T`. → confluisce nel box "Fuso orario e
  server remoti" (già abbozzato in CAP 5; la parte data/confronto-stringa è materiale di Content/C4).

## 4. Mappa → capitolo/i del libro

| Materiale della scheda | Capitolo esistente | Azione |
|---|---|---|
| Singleton PDO + ricetta opzioni (3 varianti: minimale DIS / base SPW / paranoica SR) | **CAP 3 — Database Strategy** | **aggiorna**: la tabella delle opzioni PDO diventa a 3 colonne |
| Auto-scaffolding `.data/` + `.htaccess` runtime (è di **DIS**, non SPW) | **CAP 3 — Database Strategy §1.2** | **correggi attribuzione** (vedi sotto) |
| `journal_mode=DELETE` / `busy_timeout` / incidente WAL | **CAP 3 §1.1** + **CAP 14** | mantieni in CAP 3; il racconto incidente → scheda C13/DB-Evolution |
| Bootstrap di un endpoint: i 3 stili (inline SPW / prelude `cors.php` SR / inline-minimale DIS) | **CAP 5 — Backend Logic (PHP)** | **nuovo box/§**: "Strutturare gli endpoint: inline vs prelude condiviso" |
| Errore di connessione: 500+log / 503 / die-leak | **CAP 5** | **nuovo box** "Come (non) gestire l'errore di connessione" |
| Timezone forcing per-richiesta + incoerenza | **CAP 5 §2** | **aggiorna**: aggiungi le varianti incoerenti SR/DIS al box esistente |
| Config & segreti: `define()` / `.env` / nessuna (3-factor senza librerie) | **CAP 2 (Architettura)** o **CAP 5** | **nuovo §**: oggi il tema non ha un capitolo proprio (gap) |
| `SITE_URL` canonico anti host-poisoning (solo SPW) | **CAP 10 — Security & Auth** (ponte) | **nuovo box** sicurezza (rimando da CAP 5) |
| Init fossile + versionamento per nomi-file + scaffolding "vivo" | **CAP 14 — Database Evolution** | **aggiorna**: il "init che mente" è materiale forte; pieno trattamento → scheda C13 |
| Password admin default: random/hardcoded/omessa | **CAP 10 — Security & Auth** | **anticipa** in box (trattazione piena in S1-C2) |

**Correzioni al testo attuale (la mappatura smentisce il libro):**
- **CAP 3 §1.2** attribuisce l'auto-scaffolding della cartella `.data/` con `.htaccess` a
  **SimonePizziWebSite**. È **errato**: SPW gira su **MySQL** (non ha alcun `.data/`); quel pattern è
  di **DISINTELLIGENZA** (SQLite vivo). Da correggere in fase di scrittura (FASE 3).
- **CAP 3 §1.1** presenta `journal_mode=DELETE` + `busy_timeout=5000` + `foreign_keys=ON` come la
  "configurazione ottimale SQLite" del Modello. Nessuno dei tre siti reali applica oggi questo set:
  DIS (l'unico SQLite vivo) imposta **solo** ERRMODE+FETCH via `setAttribute()`, senza PRAGMA nel
  `connect()`. Il `journal_mode=DELETE` è la **cura** dell'incidente WAL di SR (quando SR era ancora
  SQLite), non una configurazione presente nel codice attuale. → Il capitolo va riallineato: separare
  "ciò che il Modello *raccomanda*" da "ciò che i siti *fanno davvero*" (oppure marcarlo come
  prescrizione, non come fotografia).

## 5. Cosa si scarta / dedup

- **Dettaglio per-sito che NON entra nel libro:** numeri di riga esatti, nomi dei singoli
  `migrate_*`/`fix_*`/`update_db_*` file (restano nelle card di mappatura come fonte; nel libro basta
  il *pattern*), il residuo `database.sqlite` 57KB gitignorato di DIS, il dettaglio `sprintf()` del
  DSN di SR.
- **Ripetizioni fuse:** i §6 delle tre card raccontavano la stessa scala da tre punti di vista (SPW
  "io vs SR", SR "io vs SPW", DIS "io vs entrambi"). Qui la tabella comparativa è scritta **una volta
  sola** dal punto di vista neutro della scala a tre gradini.
- **Materiale che appartiene ad altre schede (per evitare doppioni a valle):**
  - cronologia incidenti WAL, `emergency_revert_wal`, migrazione-per-necessità di SR, timeline git →
    **scheda DB-Evolution/C13** (qui solo il *meccanismo* di bootstrap/init, non la storia).
  - CORS/allowlist di `cors.php`, gate `auth_utils`/`auth_helper`, protezione `.htaccess` degli
    script di migrazione, password di default trattata a fondo, anti host-poisoning lato email →
    **S1-C2 (Security & Auth)** e **S1-C9 (Newsletter)**.
  - `news.status` fuori schema, regola di visibilità `published_at`/confronto-stringa, slug →
    **schede Content (C4)**.
  - `TELEGRAM_BOT_TOKEN` / `SMTP_*` consumer, PHPMailer vendored → **S1-C8/C9**.
