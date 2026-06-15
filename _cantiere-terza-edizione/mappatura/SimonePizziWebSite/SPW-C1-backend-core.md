# Mappatura — SimonePizziWebSite — C1: Backend Core & Bootstrap

> **Stato:** COMPLETATO
> **Sessione:** 1 · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `SimonePizziWebSite/`)
> - `public/api/db.php`
> - `public/api/config.php` (credenziali reali — **non riportate**, redatte)
> - `public/api/config.example.php`
> - `scripts/init_db.php`
> - `scripts/server-tools/migrate_to_mysql.php` (FASE 1: schema MySQL)
> - `public/api/articles.php:1-15` (pattern di bootstrap di una API)
> - `public/index.php:1-40` (entry-point SEO, bootstrap lato pagina)
> - `.gitignore:37` (esclusione `config.php`)
> - `package.json` (versione 1.21.0)

## 1. Cosa fa (sintesi narrativa)

Il "backend core" del sito è volutamente minimale: **non c'è un framework**, solo PHP puro che
ogni endpoint include all'inizio. Il cuore è la coppia `config.php` (credenziali, segreti) +
`db.php` (classe `Database` con connessione PDO singleton). Ogni file API fa
`require_once 'db.php'`, chiama `Database::connect()` e ottiene la stessa istanza PDO per tutta
la richiesta.

Il bootstrap di un endpoint è una sequenza fissa di poche righe (vedi `articles.php:1-15`):
1. `require_once 'db.php'` (+ eventuale `auth_helper.php`);
2. header `Content-Type: application/json` (e `Access-Control-Allow-Methods` dove serve);
3. `$pdo = Database::connect()`;
4. **forzatura del fuso orario** `date_default_timezone_set('Europe/Rome')` per neutralizzare
   l'orario del server (storicamente Los Angeles dell'host);
5. lettura di `$_SERVER['REQUEST_METHOD']` e dispatch manuale per metodo.

Il DB è **MySQL in produzione** (`mysql.runtimeradio.it`, db `simonepizzidb`, `utf8mb4`), frutto di
una migrazione da SQLite avvenuta alla v1.7.0. Lo scaffolding "vivo" del nuovo schema vive in
`migrate_to_mysql.php` (FASE 1); lo storico `scripts/init_db.php` è rimasto fermo allo schema
SQLite ed è oggi **disallineato** (vedi §4).

## 2. Pattern miniCMS rilevanti

- **Singleton PDO statico** (`db.php:12-32`): una sola connessione per richiesta, memoizzata in
  `private static $pdo`. Niente pool, niente ORM — coerente con la filosofia "thin stack".
- **PDO in modalità sicura per default**: `ERRMODE_EXCEPTION`, `FETCH_ASSOC`,
  `EMULATE_PREPARES => false` (prepared statement reali lato server). Stesso identico set di
  opzioni replicato in `migrate_to_mysql.php:26-30` → è la "ricetta" canonica del progetto.
- **Config separata dal codice e fuori da git**: `config.php` (segreti) è in `.gitignore:37`;
  `config.example.php` è il template versionato. Pattern dodici-fattori applicato senza librerie.
- **`SITE_URL` come costante canonica** definita in `db.php:8-10` con default di produzione e
  override opzionale da `config.php`: gli URL nelle email **non** si derivano mai da `HTTP_HOST`
  (difesa contro host-header / link poisoning). Ponte verso C2/C9.
- **Timezone forzato per-richiesta** anziché in un php.ini condiviso: ogni entry-point se lo
  imposta da sé (`Europe/Rome`), così il comportamento è indipendente dall'host.
- **Degradazione "JSON-first" degli errori di connessione**: un fallimento di `connect()` non
  produce uno stack-trace ma `500` + JSON `{status:error}` con messaggio generico (il dettaglio
  va solo in `error_log`).

## 3. Codice chiave (stralci con origine)

**Singleton PDO + degrado a JSON** — `public/api/db.php:12-32`:

```php
class Database {
    private static $pdo = null;

    public static function connect() {
        if (self::$pdo === null) {
            try {
                self::$pdo = new PDO(DB_DSN, DB_USER, DB_PASS, [
                    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
                    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                    PDO::ATTR_EMULATE_PREPARES   => false,
                ]);
            } catch (PDOException $e) {
                http_response_code(500);
                error_log('db.php connection failed: ' . $e->getMessage());
                echo json_encode(['status' => 'error', 'message' => 'Errore interno del server.']);
                exit;
            }
        }
        return self::$pdo;
    }
}
```

**URL canonico anti host-poisoning** — `public/api/db.php:4-10`:

```php
// [v1.19.0] URL canonico, mai derivato da HTTP_HOST (un Host falsificato
// finirebbe nei link delle email legittime → link poisoning).
if (!defined('SITE_URL')) {
    define('SITE_URL', 'https://simonepizzi.runtimeradio.it');
}
```

**Config separata dal codice** — `public/api/config.example.php:9-14` (template versionato;
`config.php` con credenziali reali è in `.gitignore:37` e **non** viene riportato qui):

```php
define('DB_DSN',  'mysql:host=YOUR_HOST;dbname=YOUR_DATABASE;charset=utf8mb4');
define('DB_USER', 'YOUR_USERNAME');
define('DB_PASS', 'YOUR_PASSWORD');
define('BACKUP_CRON_SECRET', 'SOSTITUIRE_CON_STRINGA_CASUALE_64_CHAR');
```

**Bootstrap-tipo di un endpoint** — `public/api/articles.php:1-13`:

```php
require_once 'db.php';
require_once 'auth_helper.php';
header('Content-Type: application/json');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, PATCH');
$pdo = Database::connect();
$method = $_SERVER['REQUEST_METHOD'];
// [V1.5.5] Forzatura Fuso Orario Italiano (Bypass orario server Los Angeles)
date_default_timezone_set('Europe/Rome');
```

**Schema reale di produzione (MySQL)** — `scripts/server-tools/migrate_to_mysql.php:60-148`.
Estratto della tabella centrale `articles` (il mini-CMS vero e proprio):

```php
'articles' => "CREATE TABLE IF NOT EXISTS articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title TEXT NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    content LONGTEXT,
    excerpt TEXT,
    cover_image TEXT,
    category VARCHAR(100),
    tags TEXT,
    is_featured TINYINT(1) DEFAULT 0,
    button_a_label VARCHAR(255), button_a_link TEXT,
    button_b_label VARCHAR(255), button_b_link TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    published_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
```

Tabelle del cluster core create dallo stesso schema (`:60-148`): `users`, `articles`, `media`,
`login_attempts`, `projects`, `messages`, `subscribers`, `categories`, `article_views`
(+ altre oltre la r.148, di pertinenza di altri cluster).

## 4. Problemi riscontrati & soluzioni

- **`init_db.php` disallineato (SQLite vs MySQL) — GOLD per il libro.** `scripts/init_db.php`
  crea ancora le tabelle in dialetto **SQLite** (`INTEGER PRIMARY KEY AUTOINCREMENT`,
  `:11-90`), mentre la produzione è MySQL (`config.php` → DSN MySQL; schema reale in
  `migrate_to_mysql.php`). Eseguito su MySQL fallirebbe / produrrebbe tipi sbagliati. È il
  classico "script di bootstrap fossilizzato" dopo una migrazione di motore: lo scaffolding vivo
  si è spostato nel migratore, ma il vecchio init è rimasto come trappola. → Lezione: **dopo una
  migrazione di DB, l'init di scaffolding va riscritto o rimosso**, non lasciato ambiguo.
- **Schema divergente tra i due file.** Lo schema MySQL ha campi/tabelle assenti nell'init SQLite
  (`projects`, `categories`, `article_views`, colonna `updated_at` su `articles`). Conferma che
  la "fonte di verità" dello schema è `migrate_to_mysql.php`, non `init_db.php`.
- **Credenziali reali nel working copy.** `config.php` contiene utente/password/DSN e
  `BACKUP_CRON_SECRET` in chiaro; è correttamente escluso da git (`.gitignore:37`), ma vive sul
  filesystem del repo locale. Mitigazione di progetto: header in cima al file ("NON committare,
  NON eliminare dopo la migrazione"). → Nel manuale: come gestire i segreti in un thin stack
  senza vault (template versionato + file reale gitignorato).
- **Migratore one-shot da eliminare.** `migrate_to_mysql.php:9` istruisce esplicitamente di
  **cancellare il file dal server subito dopo l'uso** (è uno script con credenziali eseguibile via
  browser). Rischio se dimenticato online. → Pattern "script di manutenzione usa-e-getta".

## 5. Estetica / UX (moderna ma funzionale)

Cluster prevalentemente infrastrutturale: nessuna UI diretta. Note rilevanti:
- **Messaggi d'errore JSON uniformi** (`{status, message}`) con messaggi generici verso l'utente
  e dettaglio solo nei log → l'estetica "pulita" parte dal contratto delle risposte.
- L'init mostra cura UX anche in un contesto da terminale/JSON: l'utente admin viene creato con
  **password temporanea casuale stampata una sola volta** e istruzione a cambiarla
  (`init_db.php:22-27`) — esperienza di primo avvio guidata invece di una password hardcoded.

## 6. Differenze rispetto agli altri siti

(Da consolidare in FASE 2 quando saranno mappati gli altri siti. Ipotesi/puntatori per ora:)
- SimonePizziWebSite è **MySQL migrato** (come SitoRuntime), a differenza di DISINTELLIGENZA/FDCA
  che restano **SQLite** (cfr. ROADMAP §1). Il pattern `Database::connect()` singleton + opzioni
  PDO è probabilmente condiviso e sarà un buon candidato a "scheda cross-sito".
- Da verificare se gli altri siti forzano anche loro `Europe/Rome` per-richiesta e se hanno la
  stessa costante `SITE_URL` anti host-poisoning.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| Singleton PDO + ricetta opzioni sicure (`ERRMODE_EXCEPTION`/`FETCH_ASSOC`/no emulate) | Cap. "Backend Core / Connessione DB" (esistente, da aggiornare) |
| Config segreta fuori da git + template versionato | Cap. "Configurazione & segreti nel thin stack" |
| `SITE_URL` canonico anti host-header poisoning | Box sicurezza (ponte a C2/C9 email) |
| Timezone forzato per-richiesta (`Europe/Rome`) | Box "fuso orario e server remoti" |
| **Caso `init_db.php` fossile dopo migrazione SQLite→MySQL** | Box problemi/soluzioni "Migrazioni di motore DB" (alto valore) |
| Migratore usa-e-getta con credenziali da eliminare | Box "script di manutenzione one-shot" |

## 8. Note / domande aperte

- **Puntatori ad altri cluster** (annotati qui, NON mappati in questa card):
  - `auth_helper.php` / `auth.php` → **C2** (Security & Auth). `articles.php` lo include nel
    bootstrap; la tabella `login_attempts` (rate limiting) è creata nel core ma è logica C2.
  - `public/index.php` è l'**SEO engine v2.0 / Dynamic Rendering** → **C7** (qui guardato solo per
    il pattern di bootstrap/timezone). Nota: il commento dichiara `prerender.php` ormai obsoleto.
  - `BACKUP_CRON_SECRET` e `backup.php` → **C12** (Admin/backup).
  - Tabelle `categories`/`article_views`/`projects` → schema toccato qui ma logica in **C4/C12**.
- **Da verificare in C13/altra sessione:** esiste un init "vivo" per ricreare lo schema MySQL da
  zero oltre a `migrate_to_mysql.php`? Oggi sembra di no — lo scaffolding è accoppiato al
  migratore one-shot. Possibile debito tecnico da documentare.
- Versione del sito al momento della mappatura: **1.21.0** (`package.json`).
