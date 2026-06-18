# Mappatura — DISINTELLIGENZA — C1: Backend Core & Bootstrap

> **Stato:** COMPLETATO
> **Sessione:** 22 · **Data:** 2026-06-18 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `DISINTELLIGENZA/`)
> - `public/api/db.php` (singleton PDO **SQLite**, auto-creazione cartella `.data/`)
> - `public/api/init_db.php` (scaffolding schema SQLite — **fossile parziale**, fermo a "v0.3.6")
> - `public/api/update_db_0_1_3.php` · `update_db_0_1_4.php` · `update_db_maintenance.php`
> - `public/api/update_db_registration.php` · `update_db_v0.4.2.php` · `update_db_v0.5.4.php`
> - `public/api/update_db_voting.php` · `update_db_security_move.php` (lo spostamento del DB in `.data/`)
> - `public/api/news.php:1-13` · `auth.php:1-13` (pattern di bootstrap di una API)
> - `public/index.php:1-20` (entry-point SEO proxy, bootstrap lato pagina — engine = C7)
> - `public/.htaccess` (routing + deny `.sqlite`/`.bak`)
> - `.gitignore` (esclusione `*.sqlite`, `public/api/*.sqlite`)
> - `fix_api.cjs` / `fix_api.js` (root — build-tooling per `src/api.ts`, **non** bootstrap → C3)
> - `package.json` (versione 0.5.x), `DATABASESOLOPERCONSULTAZIONE/database.sqlite` (copia di consultazione)

## 1. Cosa fa (sintesi narrativa)

Questa è la **prima card del terzo sito** e introduce la variante più importante dell'intera
mappatura: **DISINTELLIGENZA gira ancora su SQLite, vivo**. Tutto ciò che in SitoRuntime (SR-C13)
era un *fossile* inerte — `PRAGMA`, `sqlite_master`, `AUTOINCREMENT`, `datetime()`, il DB-a-file —
qui è il **motore reale e attuale**. Per il libro è il termine di paragone "dal vivo": come appare
il thin-stack quando il DB-a-file è ancora la scelta corrente, non una cicatrice da migrazione.

Anche qui il backend è **PHP puro senza framework**: ogni endpoint in `public/api/` è un file
autonomo che all'avvio include i suoi mattoni. Il cuore è `db.php` (`public/api/db.php:2-28`),
classe `Database` con PDO singleton (`Database::connect()`) — **stesso spirito** di SPW/SR ma
**radicalmente più scarno**, perché SQLite elimina interi strati:

- **Niente file di configurazione, niente segreti.** Non esiste `config.php`, non esiste `.env`,
  non esiste `db_credentials.php`. SQLite non ha host/utente/password: la "connessione" è solo un
  **percorso di file hardcoded** dentro `db.php` (`$dbPath = __DIR__ . '/.data/database.sqlite'`,
  `db.php:9`). L'intero livello "config 12-fattori" di SPW-C1/SR-C1 qui semplicemente **non esiste**.
- **Il bootstrap auto-crea la sua cartella protetta.** Al primo `connect()`, se `.data/` non
  esiste, `db.php:13-17` la crea con `mkdir(...,0755,true)` e ci scrive dentro un `.htaccess`
  (`Deny from all`) — la difesa del DB è **generata a runtime dal codice stesso**, non
  pre-deployata.
- **Bootstrap di endpoint inline e minimale.** Ogni API fa la stessa sequenza fissa:
  `require_once 'db.php'; session_start(); header('Content-Type: application/json');
  $pdo = Database::connect();` (vedi `news.php:1-7`, `auth.php:1-12`). **Non c'è `cors.php`**
  (nessun CORS: l'`.htaccess` instrada `/api/` nativamente same-origin) e **non c'è `auth_helper`
  centralizzato**: la sessione si apre a mano in ogni file. È il bootstrap **più semplice dei tre
  siti** — più inline ancora di SPW, lontanissimo dal prelude condiviso di SR.

La "fonte di verità" dello schema **non** è un singolo file: è il **`.sqlite` stesso**, su cui si
sono stratificate nel tempo una serie di script `update_db_*.php` eseguiti a mano dal browser. Lo
scaffolding iniziale (`init_db.php`) è un **fossile parziale e disallineato** (vedi §4).

## 2. Pattern miniCMS rilevanti

- **Singleton PDO statico** (`db.php:3-26`): `private static $pdo`, una connessione per richiesta,
  niente pool/ORM. Stessa filosofia "thin stack" dei tre siti.
- **Ricetta PDO minimale**: solo `ERRMODE_EXCEPTION` + `FETCH_ASSOC`, impostati via `setAttribute()`
  **dopo** il costruttore (`db.php:20-21`). **Assenti** `EMULATE_PREPARES=>false` (SPW/SR), `TIMEOUT`
  e `INIT_COMMAND` (SR): per SQLite molte di queste opzioni non hanno senso (niente charset di
  connessione, niente timeout di rete), ma la mancata disattivazione dell'emulazione dei prepared è
  una differenza reale di robustezza.
- **DB-come-file con auto-provisioning della cartella** (`db.php:9-19`): il percorso è interno alla
  docroot ma in una **cartella nascosta `.data/`** auto-creata e auto-protetta con `.htaccess`. È il
  pattern "metti il file fuori portata HTTP" realizzato *dentro* l'app invece che nel deploy.
- **Bootstrap inline per-endpoint** (`news.php:1-7`, `auth.php:1-12`): nessun prelude condiviso,
  nessun lazy `getDB()` — connessione **eager** in cima a ogni file (come SPW, non come SR).
- **`session_start()` in ogni endpoint**: la sessione PHP nativa è il meccanismo di auth (dettaglio
  = C2); qui rileva solo che fa parte del bootstrap di praticamente ogni file.
- **Versionamento schema "per nome-file"**: nessuna tabella `schema_version`, nessun registro
  migrazioni. La storia è codificata nei **nomi dei file** (`update_db_0_1_3`, `0_1_4`, `v0.4.2`,
  `v0.5.4`) e nel pattern idempotente "controlla con `PRAGMA table_info` → `ALTER ADD` se manca"
  oppure "`INSERT OR IGNORE`" (vedi §3). È il **cugino SQLite** dell'ALTER+skip-Duplicate di SR.
- **Timezone forzato `Europe/Rome`** ma **solo in `index.php:7`** — gli endpoint API **non** lo
  impostano (dipendono dal default del server). Stessa **incoerenza** rilevata in SR-C1.
- **`baseUrl` da `HTTP_HOST`** (`index.php:10`): nessun `SITE_URL` canonico (come SR, a differenza
  di SPW). Nota anti host-poisoning per C7.

## 3. Codice chiave (stralci con origine)

**Singleton PDO SQLite + auto-creazione della cartella protetta** — `public/api/db.php:5-27`:

```php
public static function connect() {
    if (self::$pdo === null) {
        try {
            // Database protetto all'interno della cartella nascosta .data
            $dbPath = __DIR__ . '/.data/database.sqlite';

            $dir = dirname($dbPath);
            if (!is_dir($dir)) {
                mkdir($dir, 0755, true);
                // Forza la protezione di apache per la cartella .data
                file_put_contents($dir . '/.htaccess', "Order allow,deny\nDeny from all");
            }

            self::$pdo = new PDO("sqlite:" . $dbPath);
            self::$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            self::$pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
        } catch (PDOException $e) {
            die("Connection failed: " . $e->getMessage());
        }
    }
    return self::$pdo;
}
```

**Bootstrap-tipo di un endpoint (inline, eager, niente CORS)** — `public/api/news.php:1-7`
(stessa forma in `auth.php`, `participants.php`, …):

```php
require_once 'db.php';
session_start();
header('Content-Type: application/json');

$method = $_SERVER['REQUEST_METHOD'];
$pdo = Database::connect();
```

**Versionamento schema "per nome-file" — pattern idempotente ALTER+PRAGMA** —
`public/api/update_db_v0.4.2.php:10-17`:

```php
// Check users table for 'role' column
$columns = $pdo->query("PRAGMA table_info(users)")->fetchAll(PDO::FETCH_COLUMN, 1);
if (!in_array('role', $columns)) {
    $pdo->exec("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'editor'");
    $logs[] = "Added 'role' column to users table.";
} else {
    $logs[] = "'role' column already exists in users table.";
}
```

**Variante idempotente per i settings — `INSERT OR IGNORE`** — `update_db_0_1_4.php:20-24`:

```php
foreach ($defaults as $key => $val) {
    // Insert only if not exists to avoid overwriting current config
    $stmt = $pdo->prepare("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)");
    $stmt->execute([$key, $val]);
}
```

**Lo spostamento del DB in `.data/` (la migrazione di sicurezza, gated admin)** —
`public/api/update_db_security_move.php:8-35`:

```php
if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'admin') {
    http_response_code(403);
    die("<h1>Accesso Negato</h1> ...");
}
$oldPath = __DIR__ . '/database.sqlite';
$secureDir = __DIR__ . '/.data';
// ... mkdir + .htaccess Deny ...
copy($oldPath, $secureDir . '/database_backup_' . date('Ymd_His') . '.sqlite.bak');
if (rename($oldPath, $newPath)) { /* SUCCESSO: DB invisibile in .data/ */ }
```

## 4. Problemi riscontrati & soluzioni

- **`init_db.php` è un fossile PARZIALE e auto-dichiarato — GOLD.** Lo script di scaffolding è
  committato (`f66aebf`) con dentro commenti segnaposto che **ammettono** di aver omesso pezzi:
  `init_db.php:85` "`// ... [Admin creation ignored for brevity in repl, assuming context holds] ...`"
  e `:87` "`// ... [Other migrations] ...`". Il messaggio finale dichiara "schema updated to
  **v0.3.6**" (`:119`) mentre il sistema vivo è alla **v0.5.4**. Quindi `init_db.php` **non** ricrea
  un DB funzionante (manca la creazione dell'utente admin e diverse migrazioni) ed è fermo a una
  versione vecchia. È il parente SQLite del "init fossile dopo migrazione" di SPW/SR, ma con una
  torsione nuova: qui il fossile **non** è dovuto a un cambio di motore — il motore è sempre SQLite —
  bensì al fatto che la verità si è spostata **nel file `.sqlite`** e negli `update_db_*`, lasciando
  l'init come abbozzo. → Box "Quando l'init mente: scaffolding parziale e disallineato".
- **Nessun registro migrazioni: la storia è nei nomi dei file — GOLD.** Otto script `update_db_*`,
  eseguiti a mano dal browser, senza tabella `schema_version` né ordine garantito. La cronologia
  ricostruibile: `0_1_3` (newsletter/contacts/campaigns + cartelle upload) → `0_1_4` (settings voto)
  → `registration` (settings iscrizioni) → `maintenance` (modalità manutenzione) → `voting`
  (`in_current_round` + settings voto) → `v0.4.2` (colonne `role`/`cover_image`/`edition`) →
  `v0.5.4` (normalizzazione `status` `scheduled`→`published`) → `security_move` (DB in `.data/`).
  A differenza di SR-C13 (dove la timeline si leggeva da **git**), qui **git non aiuta** (4 commit
  totali, init in un solo "Initial commit - v0.4.0"): la storia vive interamente nei nomi-file.
  → Box "Versionare lo schema senza un sistema di migrazioni".
- **Doppio schema per la tabella `settings` — GOLD (eco del SR "tabella che nessuno crea due volte
  uguale").** `init_db.php:25-31` definisce `settings(id, key, value, type, description)`; ma
  `update_db_0_1_4.php:9-12` definisce `settings(key PRIMARY KEY, value)` (due colonne, niente `id`).
  Due definizioni divergenti della stessa tabella nello stesso repo: chi crea per primo vince
  (`CREATE TABLE IF NOT EXISTS`). Stessa patologia dei 3 schemi `subscribers` di SitoRuntime.
- **Default di `voting_active` incoerente.** `update_db_0_1_4.php:16` lo inizializza a `'false'`
  (stringa), `update_db_voting.php:29` a `'0'`. Entrambi `INSERT OR IGNORE` → il primo eseguito
  vince, ma la rappresentazione del booleano è ambigua (stringa `'false'` vs `'0'`). Logica voto =
  C10; qui rileva solo come debito di bootstrap dei settings.
- **Colonna `news.status` fuori dallo schema base.** `update_db_v0.5.4.php:19` fa
  `UPDATE news SET status = 'published' WHERE status = 'scheduled'`, ma `init_db.php` (tab. `news`,
  `:34-44`) **non** ha alcuna colonna `status`. È stata aggiunta altrove (probabile self-heal in
  `news.php` → C4). Schema frammentato come in SR (`news.status` aggiunto da micro-migrazione).
- **Script di migrazione per lo più NON protetti.** Solo `update_db_security_move.php` (gate admin)
  e `update_db_v0.5.4.php` (gate login) controllano la sessione; gli altri sei (`0_1_3`, `0_1_4`,
  `maintenance`, `registration`, `v0.4.2`, `voting`) fanno solo `require_once 'db.php'` e sono
  **eseguibili in HTTP da chiunque** (creano tabelle, inseriscono settings). A differenza di SR
  (deny `.htaccess` by-prefix su `migrate_`/`fix_`/`init_`), qui l'`.htaccess` di `public/` **non**
  nega questi file: l'unica protezione è "non conoscerne il nome". → Nota sicurezza, ponte a C2.
- **Errore di connessione: `die()` con messaggio grezzo — GOLD sicurezza (regressione vs SPW/SR).**
  `db.php:23` fa `die("Connection failed: " . $e->getMessage())`: espone il **dettaglio
  dell'eccezione** al client (path del file, motivo), non è JSON, niente `http_response_code`, niente
  `error_log`. SPW degrada a 500+JSON+log, SR a 503+JSON: DIS è il più rozzo dei tre (information
  disclosure). → Box "Come NON gestire un errore di connessione".
- **`database.sqlite` "vecchio" ancora nel working copy ma non più usato.** Sul disco esistono
  `public/api/database.sqlite` (57 KB) **e** `DATABASESOLOPERCONSULTAZIONE/database.sqlite` (stessa
  taglia), ma `db.php` legge da `.data/database.sqlite` (che **non esiste ancora** localmente: verrà
  auto-creato al primo run). Entrambi i `.sqlite` sono **gitignorati** (`.gitignore`: `*.sqlite`,
  `public/api/*.sqlite`) → **non sono nel repo git** (`git ls-files` non ne elenca nessuno). Quindi
  la frase "il DB è presente nel repo" va precisata: è presente **nel working copy**, non in git, ed
  è il file *pre-`security_move`* lasciato lì come residuo. Il `.htaccess` di `public/` nega comunque
  ogni `*.sqlite` e `*.bak` via `<Files>` (`.htaccess:1-9`) come seconda rete.

## 5. Estetica / UX (moderna ma funzionale)

Cluster prevalentemente infrastrutturale: nessuna UI diretta. Note:

- **Output dei tool curato e in italiano.** `update_db_security_move.php` (`:13-46`) stampa una
  pagina HTML passo-passo ("Creata cartella protetta", "Creato Backup di sicurezza", "**SUCCESSO!**"
  in verde, errori in rosso) con link finale "Torna alla Dashboard Admin". Gli `update_db_*` JSON
  restituiscono `{status, message, logs[]}` leggibili. Cura UX anche nel backstage, come SPW/SR.
- **Auto-provisioning "a prova di principiante".** Sia `db.php` (cartella `.data/`) sia
  `update_db_0_1_3.php:36-45` (cartelle `uploads/images`, `uploads/audio`) creano da soli ciò che
  manca: il sito "si ripara" al primo avvio senza setup manuale. Coerente con l'estetica "funzionale
  ma accessibile" del progetto.
- **Contratto di errore incoerente.** A fronte di JSON puliti negli `update_db_*`, `db.php`
  degrada a una stringa `die()` grezza: l'estetica "pulita" delle risposte si rompe proprio nel
  punto più basso (vedi §4).

## 6. Differenze rispetto agli altri siti

Confronto a **TRE**: DIS-C1 (SQLite **vivo**) vs SPW-C1 e SR-C1 (entrambi **MySQL migrati**). Il
valore è "il sito che NON ha migrato": come appare il DB-a-file quando è ancora la scelta corrente.

| Aspetto | SimonePizziWebSite (SPW-C1) | SitoRuntime (SR-C1) | **DISINTELLIGENZA (questa card)** |
|---|---|---|---|
| **Motore DB** | MySQL (migrato v1.7.0) | MySQL (migrato 24/02/2026) | **SQLite VIVO** (mai migrato) |
| **Config / segreti** | `config.php` `define()` + example | `db_credentials.php`→`.env` + example | **nessuna**: path file hardcoded in `db.php:9` |
| **"Connessione"** | DSN MySQL (host/user/pass) | DSN via `sprintf()` + port | `new PDO("sqlite:".$path)` (un file) |
| **Opzioni PDO** | ERRMODE+FETCH+no-emulate | + `TIMEOUT=5` + `INIT_COMMAND` | **solo** ERRMODE+FETCH (via `setAttribute`) |
| **Errore connessione** | 500 + JSON + `error_log` | 503 + JSON (no log) | **`die()` stringa grezza con `getMessage()`** (peggiore) |
| **Prelude bootstrap** | inline in ogni file | **`cors.php` condiviso** + lazy `getDB()` | **inline minimale**, eager, **niente CORS** |
| **Apertura connessione** | eager | lazy `getDB()` (duplicata) | **eager** (`$pdo = Database::connect()`) |
| **Posizione del DB** | server MySQL (fuori docroot per natura) | server MySQL | **file in `.data/` auto-creata** dentro la docroot |
| **Protezione DB** | n/a (è un server) | n/a | `.htaccess` Deny **generato a runtime** + `<Files>` in `public/.htaccess` |
| **Scaffolding schema** | nel migratore `migrate_to_mysql.php` | file dedicato `init_mysql.php` + micro-migr. | **`init_db.php` fossile parziale (v0.3.6)** + catena `update_db_*` |
| **Storia migrazioni** | (poca) | leggibile da **git** (SR-C13) | **nei nomi-file** `update_db_*` (git inutile: 4 commit) |
| **Registro versioni** | no | no (ALTER+skip-Duplicate) | no (`PRAGMA table_info`+ALTER / `INSERT OR IGNORE`) |
| **Password admin default** | random stampata 1 volta | **hardcoded `runtime2026`** | creazione admin **omessa** in init (fossile parziale) → C2 |
| **Timezone** | forzato in ogni endpoint | solo `news.php`/`index.php` (incoerente) | **solo `index.php:7`** (incoerente, come SR) |
| **`SITE_URL` canonico** | sì | assente (HTTP_HOST) | assente (`index.php:10` da `HTTP_HOST`) |

**Sintesi.** DIS è la **versione "grado zero"** del backend core: SQLite cancella l'intero livello
config/segreti (niente host/credenziali), riduce le opzioni PDO al minimo e rende il DB un file da
nascondere dentro la docroot. È **più semplice di SPW** (bootstrap inline ancora più scarno, nessun
CORS) e l'esatto **opposto di SR** sull'asse "ingegnerizzazione" (SR ha prelude condiviso, `.env`,
lazy DB, opzioni rinforzate; DIS non ha nulla di tutto questo). Ma è anche il **più fragile** sui
fondamentali: errore di connessione che fa leak via `die()`, script di migrazione non protetti, init
fossile *parziale*. Soprattutto, DIS dimostra "dal vivo" perché SR è **fuggito** da SQLite (SR-C13):
qui WAL/PRAGMA non sono fossili ma il motore — e con essi convivono gli stessi rischi (file-lock su
hosting condiviso) che a SitoRuntime causarono il crash notturno e la migrazione a MySQL.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| Singleton PDO **SQLite** (la 3ª variante): `new PDO("sqlite:...")`, niente config/segreti | Cap. "Backend Core / Connessione DB" (estendere la tabella con la colonna SQLite) |
| **DB-a-file vivo vs fossile**: DIS (vivo) come specchio di SR-C13 (migrato per necessità) | Cap. "Database Evolution" / Box "Perché si scappa da SQLite (e quando va benissimo restare)" |
| Auto-provisioning della cartella `.data/` + `.htaccess` Deny generato a runtime | Box "Nascondere il DB-a-file dentro la docroot" (alto valore, pattern hosting condiviso) |
| **Versionare lo schema senza sistema di migrazioni**: nomi-file `update_db_*` + idempotenza | Box "Migrazioni fai-da-te: PRAGMA+ALTER e INSERT OR IGNORE" (nuovo) |
| **Init fossile *parziale*** (commenti "ignored for brevity", v0.3.6 vs v0.5.4) | Box "Quando l'init mente" (rafforza il caso SPW/SR dell'init fossile) |
| **Doppio schema `settings`** (5 col vs 2 col) | Box "La tabella che nessuno crea due volte uguale" (consolidare con SR subscribers) |
| **`die()` con `getMessage()`** sul fallimento connessione | Box "Come NON gestire l'errore di connessione" (anti-pattern, contrasto SPW/SR) |
| Bootstrap inline minimale vs prelude condiviso (`cors.php` di SR) | Box "Strutturare gli endpoint: i tre stili" (DIS=grado zero, SPW=inline, SR=prelude) |
| Timezone forzato solo in `index.php` | confluisce nel Box "Fuso orario e server remoti" (3° caso) |

## 8. Note / domande aperte

- **Puntatori ad altri cluster** (annotati qui, NON mappati in questa card):
  - `auth.php`, `users.php`, `session_start()` per-endpoint, gate `$_SESSION['role']` admin/editor,
    e l'**assenza di protezione `.htaccess`** sugli script `update_db_*` → **C2** (Security & Auth +
    anti-frode voto). In C1 li ho visti solo per il bootstrap (session + gate degli script migrazione).
  - **Creazione utente admin omessa in `init_db.php`** (commento "ignored for brevity"): dove viene
    creato l'admin? Verosimilmente in un blocco eliso o a mano nel `.sqlite` → **C2** (credenziali di
    default — verificare se esiste un hardcoded come SR `runtime2026`).
  - `public/index.php` = **SEO proxy / Open Graph injection** per i crawler → **C7** (qui solo per
    bootstrap/timezone). Nota per C7: `baseUrl` da `HTTP_HOST`, nessun `SITE_URL`.
  - `news.php` (lista/dettaglio, slug, paginazione, colonna `status` self-heal?) → **C4**.
  - `participants.php`, `votes.php`, `reset_votes.php`, `settings.php` (master switch voto),
    `stats.php`, `reset_system.php` → **C10** (Festival Logic). Le tabelle `participants`/`votes` e i
    settings `voting_*`/`registration_*` sono creati qui (bootstrap), ma la logica è C10.
  - `media.php`, `upload.php`, `migrate_media.php`, cartelle `uploads/images|audio` (create da
    `update_db_0_1_3.php`) → **C5**.
  - `newsletter.php`, `contact.php`, tabelle `newsletter_subscribers`/`contacts`/
    `newsletter_campaigns` (create da `update_db_0_1_3.php`) → **C9**.
  - `feed.php`, `podcasts.php` → **C8/C4**.
  - L'intera catena `update_db_*` + `security_move` + i `.sqlite` residui + WAL/PRAGMA dal vivo →
    candidato a una eventuale **DIS-C13** (DB Evolution & Incidenti), se la apriremo: qui ho mappato
    solo il **meccanismo** di bootstrap/versionamento, non la cronologia dettagliata.
- **Coppie naturali per DISINTELLIGENZA (proposta dopo aver visto C1):** la geografia conferma che
  il valore distintivo del sito è il **festival** (participants/votes/settings/stats) — cluster denso
  e coeso. Proposta: tenere **C2 da sola** (auth + anti-frode voto = alto valore), poi valutare la
  coppia **C4+C9** (Content/news + Newsletter, entrambi "contenuto editoriale" leggero) e **C10 da
  sola** (Festival Logic, il cuore). Decisione finale nel prompt della prossima sessione.
- **Da verificare in C2/C10:** il `voter_hash`/anti-doppio-voto di DIS (qui la tab. `votes` ha
  `session_id`+`ip_address`+`user_agent`, `init_db.php:62-70`) — confronto con il toggle SHA256 di
  SPW-C11 e con l'anti-frode.
- Versione del sito al momento della mappatura: **0.5.x** (`package.json`); ultimo `update_db` è
  `v0.5.4`.
