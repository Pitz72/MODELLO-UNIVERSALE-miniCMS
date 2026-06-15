# Mappatura — SitoRuntime — C1: Backend Core & Bootstrap

> **Stato:** COMPLETATO
> **Sessione:** 12 · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `SitoRuntime/`)
> - `public/api/db.php` (singleton PDO MySQL)
> - `public/api/db_credentials.php` (loader credenziali da `.env`)
> - `public/api/.env.example` (template versionato)
> - `.gitignore` (esclusione `.env`, eccezione `!.env.example`)
> - `public/api/cors.php` (prelude di bootstrap condiviso — logica CORS = C2)
> - `public/api/news.php:1-14` · `speakers.php:1-21` · `podcasts.php:1-21` · `admin.php:1-20` (pattern di bootstrap di una API)
> - `public/api/init_db.php` (init "fossile" SQLite, con seed reale)
> - `public/api/init_mysql.php` (scaffolding "vivo" dello schema MySQL)
> - `public/api/migrate_to_mysql.php` (migratore one-shot SQLite→MySQL — meccanismo; storia = C13)
> - `public/api/migrate_status.php` (micro-migrazione colonna `status`)
> - `public/api/debug_time.php` (diagnostica timezone / `published_at`)
> - `public/index.php:1-28` (entry-point SEO, bootstrap lato pagina — engine = C7)
> - `public/api/lib/` (PHPMailer vendored + `.htaccess` deny — uso = C9)
> - `package.json` (versione 2.9.13)

## 1. Cosa fa (sintesi narrativa)

Anche qui il "backend core" è **PHP puro senza framework**: ogni endpoint in `public/api/` è un
file autonomo che include all'avvio i suoi mattoni. Ma la **forma del bootstrap diverge** in modo
sistematico da SimonePizziWebSite (cfr. SPW-C1) — ed è la prima e più importante osservazione di
questa card.

La connessione vive in `db.php`, classe `Database` con PDO singleton (`Database::connect()`),
**identica nello spirito** a SPW ma con tre differenze concrete (vedi §2/§3): le credenziali
arrivano da un **file separato** `db_credentials.php` che a sua volta **legge un `.env`** via
`parse_ini_file()` (SPW usa invece `config.php` con `define()`), il DSN è **costruito con
`sprintf()`** includendo la `port`, e ci sono **due opzioni PDO extra** (`ATTR_TIMEOUT => 5` e
`MYSQL_ATTR_INIT_COMMAND` che riforza `SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci`).

Il **prelude di bootstrap di un endpoint** non è una sequenza inline come in SPW, ma è
**centralizzato in `cors.php`**: praticamente ogni API inizia con `require_once 'cors.php'`, che
imposta gli header CORS, il `Content-Type: application/json` e **gestisce il preflight `OPTIONS`**
uscendo subito. Solo dopo l'endpoint definisce una **funzione `getDB()` lazy** (PDO memoizzato in
una `static $pdo` locale che fa `require_once 'db.php'` solo al primo uso) — funzione che è
**copia-incollata identica** in `news.php`, `speakers.php`, `podcasts.php`, `admin.php`, … Quindi:
in SPW la connessione è *eager* (`$pdo = Database::connect()` in cima), qui è *lazy per-funzione*.

Il DB è **MySQL in produzione**, frutto di una migrazione da SQLite datata **24/02/2026**
(commento in `db.php:3`). A differenza di SPW, lo scaffolding dello schema MySQL ha un file
**dedicato e vivo**, `init_mysql.php` (5 tabelle: `news`, `users`, `subscribers`, `speakers`,
`podcasts`), affiancato al migratore dati one-shot `migrate_to_mysql.php` e al vecchio
`init_db.php` rimasto in **dialetto SQLite** (fossile, ma con dentro il **seed reale** di 24
speaker — vedi §4). L'evoluzione storica vera e propria (incidenti WAL, `emergency_revert_wal.php`)
è materiale di **SR-C13** e qui è solo annotata.

## 2. Pattern miniCMS rilevanti

- **Singleton PDO statico** (`db.php:5-34`): `private static $pdo`, una connessione per richiesta,
  niente pool/ORM. Stessa filosofia "thin stack" di SPW.
- **Ricetta PDO "sicura per default" + due rinforzi**: `ERRMODE_EXCEPTION`, `FETCH_ASSOC`,
  `EMULATE_PREPARES => false` (come SPW) **più** `ATTR_TIMEOUT => 5` (fail-fast sulla connessione)
  e `MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"` (charset coerente a
  livello di connessione, non solo nel DSN). È la "ricetta canonica" del progetto, più paranoica
  di quella di SPW.
- **Config separata in due livelli, fuori da git**: `db_credentials.php` (committato, è solo il
  *loader*) → `.env` (gitignorato, contiene i segreti) → `.env.example` (template versionato,
  whitelistato con `!public/api/.env`). Pattern dodici-fattori più "ortodosso" di SPW (che usa un
  `config.php` con `define()` direttamente).
- **`db_credentials.php` come hub di TUTTI i segreti**, non solo DB: oltre a `DB_*` espone
  `TELEGRAM_BOT_TOKEN` e il blocco `SMTP_*` (host/port/user/pass/from-name). È il punto unico di
  configurazione dei servizi esterni (ponte a C9 newsletter / bot Telegram).
- **Prelude di bootstrap condiviso (`cors.php`)**: invece di ripetere header inline in ogni file,
  SitoRuntime fattorizza CORS + `Content-Type` + short-circuit `OPTIONS` in un unico include
  montato per primo. Rottura del pattern "tutto inline" di SPW.
- **Connessione lazy per-endpoint (`getDB()`)**: il PDO si apre solo se serve davvero, così un
  ramo che risponde da cache o respinge un `OPTIONS`/401 non paga la connessione. Buona idea,
  realizzata però con **copia-incolla** della stessa funzione in N file (vedi §4).
- **Timezone forzato per-richiesta** (`date_default_timezone_set('Europe/Rome')`): presente come in
  SPW per neutralizzare l'orario del server, ma **applicato in modo incoerente** (vedi §4).
- **Degradazione "JSON-first" degli errori di connessione**: `connect()` fallito → `http 503` +
  `{"error":"Database Connection Error"}` e `die()`. Stessa idea di SPW ma codice **503** (Service
  Unavailable) invece di 500, e messaggio generico senza dettaglio (qui **non** viene loggato, vedi §4).

## 3. Codice chiave (stralci con origine)

**Singleton PDO + credenziali da file separato + opzioni rinforzate** — `public/api/db.php:5-34`:

```php
class Database {
    private static $pdo = null;

    public static function connect() {
        if (self::$pdo === null) {
            try {
                $config = require __DIR__ . '/db_credentials.php';

                $dsn = sprintf(
                    "mysql:host=%s;dbname=%s;port=%d;charset=utf8mb4",
                    $config['DB_HOST'], $config['DB_NAME'], $config['DB_PORT']
                );

                self::$pdo = new PDO($dsn, $config['DB_USER'], $config['DB_PASS'], [
                    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
                    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                    PDO::ATTR_EMULATE_PREPARES   => false, // prepared nativi
                    PDO::ATTR_TIMEOUT            => 5,
                    PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"
                ]);
            } catch (PDOException $e) {
                http_response_code(503);
                die(json_encode(['error' => 'Database Connection Error']));
            }
        }
        return self::$pdo;
    }
}
```

**Loader segreti da `.env` (12-factor senza librerie)** — `public/api/db_credentials.php:6-32`:

```php
$envFile = __DIR__ . '/.env';
if (!file_exists($envFile)) {
    http_response_code(503);
    die(json_encode(['error' => 'Server configuration missing. Contact administrator.']));
}
$env = parse_ini_file($envFile);
// ...
return [
    'TELEGRAM_BOT_TOKEN' => $env['TELEGRAM_BOT_TOKEN'] ?? '',
    'DB_HOST' => $env['DB_HOST'] ?? '', 'DB_NAME' => $env['DB_NAME'] ?? '',
    'DB_USER' => $env['DB_USER'] ?? '', 'DB_PASS' => $env['DB_PASS'] ?? '',
    'DB_PORT' => (int)($env['DB_PORT'] ?? 3306),
    'SMTP_HOST' => $env['SMTP_HOST'] ?? '', 'SMTP_PORT' => (int)($env['SMTP_PORT'] ?? 587),
    // ... SMTP_USER, SMTP_PASS, SMTP_FROM_NAME
];
```

**Bootstrap-tipo di un endpoint (prelude condiviso + lazy DB)** — `public/api/speakers.php:1-21`
(identico in `podcasts.php`, `admin.php`; `news.php` mette il timezone *prima* di `cors.php`):

```php
require_once 'cors.php';        // CORS + Content-Type:json + short-circuit OPTIONS
require_once 'auth_utils.php';  // → C2
header("Cache-Control: no-cache, no-store, must-revalidate");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { exit(0); }

// Lazy DB Connection (copia-incollata in ogni endpoint)
function getDB() {
    static $pdo = null;
    if ($pdo === null) {
        require_once 'db.php';
        $pdo = Database::connect();
    }
    return $pdo;
}
```

**Prelude condiviso che fa anche da bootstrap** — `public/api/cors.php:23-30` (allowlist origini =
dettaglio di **C2**; qui interessa che imposta `Content-Type` e gestisce il preflight per tutti):

```php
header("Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, X-CSRF-Token");
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit(0);
}
```

**Scaffolding "vivo" dello schema MySQL** — `public/api/init_mysql.php:18-91` (estratto della
tabella centrale `news`, il mini-CMS vero e proprio; nota gli `INDEX` definiti inline):

```php
$pdo->exec("CREATE TABLE IF NOT EXISTS news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slug VARCHAR(255) NOT NULL UNIQUE,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    content LONGTEXT,
    cover_image VARCHAR(500),
    author VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    category VARCHAR(100) DEFAULT 'News',
    INDEX idx_news_slug (slug),
    INDEX idx_news_published (published_at),
    INDEX idx_news_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");
```

Tabelle create dallo schema MySQL vivo (`init_mysql.php`): `news`, `users`, `subscribers`,
`speakers` (con colonne **`JSON`** native `tags`/`programs`/`social_urls`), `podcasts`. La colonna
`news.status` **non** è nello schema base: è stata aggiunta a posteriori da `migrate_status.php`
(vedi §4) — debito di schema da segnalare.

## 4. Problemi riscontrati & soluzioni

- **`init_db.php` fossile SQLite — GOLD (parallelo perfetto a SPW-C1).** `init_db.php:9-21` crea le
  tabelle in dialetto **SQLite** (`INTEGER PRIMARY KEY AUTOINCREMENT`, commento "CMS gestito da
  SQLite" nella seed news), mentre la produzione è MySQL. Eseguito oggi su MySQL fallirebbe / darebbe
  tipi sbagliati. È lo stesso "script di bootstrap fossilizzato dopo la migrazione di motore" visto
  in SPW — qui però lo scaffolding vivo si è spostato in **un file nuovo dedicato** (`init_mysql.php`),
  non dentro il migratore come in SPW. Lezione confermata cross-sito: **dopo una migrazione di DB
  l'init va riscritto o rimosso**, non lasciato ambiguo.
- **Password admin di default HARDCODED — GOLD sicurezza (DIVERGENZA forte da SPW).**
  `init_db.php:421-424` crea l'utente `admin` con password **`runtime2026` in chiaro nel codice**
  (`password_hash('runtime2026', …)`) e stampa "CHANGE THIS IMMEDIATELY!". SPW invece genera una
  **password temporanea casuale stampata una sola volta**. È una credenziale di default committata e
  prevedibile: se l'init è stato eseguito e nessuno ha cambiato la password, è un account
  amministrativo indovinabile. → Box "credenziali di default" ad alto valore didattico
  (cosa NON fare vs il pattern random di SPW). Ponte a C2.
- **`getDB()` duplicata per copia-incolla.** La stessa identica funzione lazy compare in
  `news.php`, `speakers.php`, `podcasts.php`, `admin.php` (e altri). Una modifica alla strategia di
  connessione va replicata N volte. → Esempio di "fattorizzazione mancata" — il candidato naturale
  sarebbe spostarla accanto a `Database::connect()` in `db.php`. Contrasto con il singleton, che
  invece *è* fattorizzato.
- **Timezone forzato in modo incoerente.** `news.php:3` e `index.php:20` chiamano
  `date_default_timezone_set('Europe/Rome')`, ma `speakers.php`/`podcasts.php`/`admin.php` **no**:
  dipendono dal default del server. Poiché la regola di visibilità degli articoli confronta
  `published_at <= NOW` come **stringhe** (`news.php:24-25`), un fuso sbagliato sposta la soglia.
- **Incidente timezone/formato data documentato in codice — GOLD.** Esiste un file di diagnostica
  dedicato, `debug_time.php`, che confronta `published_at` del DB con `date('Y-m-d\TH:i:s')` usando
  il **separatore `T`** ("FIX: Use T separator to match DB", `:23-24`) e stampa `VISIBLE`/`HIDDEN`.
  È la prova di un bug reale: articoli che sparivano perché il confronto stringa tra `published_at`
  e "adesso" non combaciava (formato/fuso). → Box "fuso orario, formato data e confronti stringa"
  ad alto valore. (La cronologia completa degli incidenti = C13.)
- **Errore di connessione non loggato.** `db.php:28-31` su `PDOException` fa `http 503` + `die(json)`
  ma **non** scrive in `error_log` (SPW invece logga il dettaglio). In produzione un guasto DB qui
  non lascia traccia diagnostica lato server. → Nota di osservabilità.
- **Schema frammentato in micro-migrazioni.** La colonna `news.status` non è nello schema di
  `init_mysql.php` ma viene aggiunta da `migrate_status.php` (ALTER idempotente con gestione del
  duplicate-column 1060/42S21). La "fonte di verità" dello schema è quindi sparsa tra
  `init_mysql.php` + una serie di file `migrate_*`/`fix_*` (puntatore a C13).
- **Script con credenziali eseguibili via browser da eliminare.** `init_mysql.php`,
  `migrate_to_mysql.php`, `migrate_status.php` ripetono nell'header "ELIMINARE dal server dopo l'uso".
  Stesso rischio di SPW: se dimenticati online, sono endpoint potenti raggiungibili in HTTP.

## 5. Estetica / UX (moderna ma funzionale)

Cluster prevalentemente infrastrutturale: nessuna UI diretta. Note:
- **Output dei tool da terminale curato**: `init_mysql.php` e `migrate_to_mysql.php` stampano un
  log testuale passo-passo ("1. Creazione tabella 'news'... OK", riepilogo + verifica conteggi),
  un'esperienza CLI/browser leggibile e guidata. Cura UX anche nel backstage.
- **Contratto di errore JSON uniforme** (`{"error": "..."}`) con messaggi generici verso il client
  → coerenza delle risposte come base dell'estetica "pulita".
- **Primo avvio guidato** (come SPW) ma con la pecca della password fissa (§4): l'intento UX di
  "guidare il primo accesso" c'è, l'esecuzione è insicura.

## 6. Differenze rispetto agli altri siti

Questa è la **prima card del secondo sito**: il confronto con **SPW-C1** è il valore centrale.

| Aspetto | SimonePizziWebSite (SPW-C1) | SitoRuntime (questa card) |
|---|---|---|
| **Caricamento credenziali** | `config.php` con `define()` (gitignorato) + `config.example.php` | `db_credentials.php` *loader* (committato) → `.env` via `parse_ini_file()` (gitignorato) + `.env.example` |
| **Segreti gestiti** | DB + `BACKUP_CRON_SECRET` + `SITE_URL` | DB + `TELEGRAM_BOT_TOKEN` + blocco `SMTP_*` (hub unico) |
| **Costruzione DSN** | DSN intero in `config.php` | DSN via `sprintf()` in `db.php`, include `port` |
| **Opzioni PDO** | ERRMODE/FETCH/no-emulate | + `ATTR_TIMEOUT=>5` + `MYSQL_ATTR_INIT_COMMAND` (SET NAMES) |
| **Errore connessione** | `500` + JSON + **`error_log`** | `503` + JSON + **niente log** |
| **Prelude bootstrap** | inline in ogni file (`require db`+`auth_helper`, header) | **centralizzato in `cors.php`** (CORS+Content-Type+OPTIONS) |
| **Apertura connessione** | *eager*: `$pdo = Database::connect()` in cima | *lazy*: funzione `getDB()` con `static`, **duplicata** per file |
| **Scaffolding schema MySQL** | dentro il migratore `migrate_to_mysql.php` (FASE 1) | file **dedicato `init_mysql.php`** + micro-migrazioni `migrate_*`/`fix_*` |
| **Init fossile** | `init_db.php` SQLite (fossile) | `init_db.php` SQLite (fossile) **+ seed reale 24 speaker** |
| **Password admin di default** | **random** stampata una volta | **hardcoded `runtime2026`** (insicura) |
| **Cartella `lib/`** | assente | presente: **PHPMailer vendored** + `.htaccess` deny (uso = C9) |
| **`SITE_URL` anti host-poisoning** | sì, costante canonica | **assente**: `index.php:27` deriva `baseUrl` da `HTTP_HOST` (nota per C7) |
| **Timezone** | forzato in ogni endpoint | forzato **solo** in `news.php`/`index.php` (incoerente) |

Sintesi: stessa **filosofia** (PHP puro, PDO singleton, config fuori da git, init fossile post-
migrazione, migratore usa-e-getta), ma SitoRuntime è più "ingegnerizzato" su alcuni assi
(prelude condiviso, lazy DB, `.env`, opzioni PDO rinforzate, scaffolding dedicato) e **più fragile**
su altri (password di default hardcoded, niente `error_log`, niente `SITE_URL` canonico, `getDB()`
duplicata, timezone incoerente).

Per DISINTELLIGENZA/FDCA (SQLite) il confronto si farà alle rispettive card C1.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| Singleton PDO: ricetta opzioni — variante "paranoica" (TIMEOUT + INIT_COMMAND) vs base SPW | Cap. "Backend Core / Connessione DB" (aggiornare con la tabella di confronto) |
| Due stili di config segreta: `config.php`/`define()` (SPW) vs `.env`/`parse_ini_file` (SR) | Cap. "Configurazione & segreti nel thin stack" (arricchire con la 2ª variante) |
| Prelude di bootstrap condiviso (`cors.php`) vs bootstrap inline | Cap./Box "Strutturare gli endpoint: inline vs prelude condiviso" (nuovo) |
| Connessione lazy `getDB()` vs eager + il debito del copia-incolla | Box "Lazy connection e fattorizzazione mancata" |
| **Password admin di default hardcoded** vs random | Box sicurezza "Credenziali di default: cosa non fare" (alto valore, ponte C2) |
| **`init_db.php` fossile dopo migrazione SQLite→MySQL** (confermato su 2 siti) | Box "Migrazioni di motore DB: l'init fossile" (rafforza il caso SPW) |
| Scaffolding dedicato (`init_mysql.php`) vs scaffolding nel migratore | Box "Dove vive lo schema dopo una migrazione" |
| **Fuso orario + formato data + confronto stringa** (`debug_time.php`, separatore `T`) | Box "Fuso orario, server remoti e confronti di date" (alto valore) |

## 8. Note / domande aperte

- **Puntatori ad altri cluster** (annotati qui, NON mappati in questa card):
  - `cors.php` (allowlist origini, header CSRF) e `auth_utils.php` (`generateCsrfToken`, gate auth) → **C2**.
    In C1 li ho guardati solo perché `cors.php` fa da prelude di bootstrap comune.
  - `public/index.php` = **SEO Engine v3.0 / Dynamic Rendering** → **C7** (qui solo per bootstrap/
    timezone). Nota per C7: `baseUrl` deriva da `HTTP_HOST` (a differenza del `SITE_URL` di SPW).
  - `public/api/lib/phpmailer/` (PHPMailer vendored, protetto da `.htaccess` "Deny from all") e
    blocco `SMTP_*` in `.env` → **C9** (Newsletter & Email).
  - `TELEGRAM_BOT_TOKEN` in `.env` → consumer da individuare (probabile RSS/notifiche, **C8/C9**).
  - `migrate_to_mysql.php`, `migrate_status.php`, `fix_newsletter_table.php`, `fix_users_table.php`,
    `emergency_revert_wal.php`, `optimize_db.php`, `rebuild_seo_cache.php` → **EVOLUZIONE DB &
    INCIDENTI = C13** (qui solo il *meccanismo* di bootstrap di init/migrazione; storia WAL/incidenti
    e schema dettagliato → C13). `optimize_db.php`→anche C12, `rebuild_seo_cache.php`→C7.
  - `setup_podcasts.php` → scaffolding/seed della tabella `podcasts`, logica contenuti → **C4** (qui
    solo notato che `podcasts` è nello schema core di `init_mysql.php`).
  - `test_index.php`, `debug_seo.php` → diagnostica (C7/varie); `debug_time.php` rientra in C1 perché
    riguarda il timezone.
- **Da verificare in C13:** esiste un percorso "pulito" per ricreare lo schema MySQL da zero oltre a
  `init_mysql.php` + la catena di `migrate_*`/`fix_*`? Oggi lo schema è **frammentato** (base + micro-
  migrazioni sparse). Possibile debito tecnico da documentare nel cluster incidenti.
- **Da verificare:** il `.env` reale è presente nel working copy locale (`public/api/.env`, 300 byte,
  gitignorato) — **non** ne ho letto/riportato il contenuto (segreti).
- Versione del sito al momento della mappatura: **2.9.13** (`package.json`).
