# CAPITOLO 14: Database Evolution - Da SQLite a MySQL (v1.0)

Questo capitolo documenta il percorso reale vissuto dal progetto **SitoRuntime (Runtime Radio)** nella migrazione da SQLite a MySQL, avvenuta il 24 febbraio 2026. È una storia concreta di sfide, soluzioni e lezioni apprese — non un manuale teorico.

## 1. Quando e Perché Migrare

SQLite è perfetto per progetti leggeri o in fase di sviluppo: zero configurazione, file unico, deployabile in pochi secondi. Ma esistono soglie oltre le quali inizia a mostrare i propri limiti su hosting condivisi Apache/PHP:

- **Traffico crescente**: più utenti simultanei = più richieste di scrittura = file lock frequenti.
- **Hosting restrittivi**: alcuni provider limitano o bloccano SQLite per policy interne.
- **Necessità di accesso remoto al DB**: tools di gestione visuale (es. phpMyAdmin) richiedono MySQL.
- **Performance su query complesse**: MySQL gestisce meglio join e aggregazioni su tabelle grandi.

**Regola pratica**: Finché il sito ha < 50 scritture/ora, SQLite è più che sufficiente. Sopra quella soglia, o in presenza di file lock ricorrenti in produzione, valutare MySQL.

## 2. La Storia del WAL (Warning reale)

Prima della migrazione definitiva, SitoRuntime aveva tentato di risolvere i problemi di file lock attivando il **WAL mode** (Write-Ahead Logging) di SQLite — teoricamente più veloce e meno soggetto a lock. In pratica su hosting condiviso Apache con PHP, il WAL ha causato problemi peggiori: il file di lock WAL (`.sqlite-wal`) rimaneva "appeso" e corrompeva le letture.

Esiste ancora in repo il file `emergency_revert_wal.php`, uno script d'emergenza che forza il ritorno al `journal_mode=DELETE`. Questa è la ragione per cui il **Capitolo 3 impone DELETE mode e non WAL**: la lezione è stata appresa a caro prezzo in produzione.

## 3. Architettura della Migrazione (Il Pattern a 3 Script)

La migrazione da SQLite a MySQL è stata eseguita con 3 script dedicati, ciascuno con un ruolo preciso:

### 3.1 `db_credentials.php` — Il File dei Segreti
```php
<?php
// ATTENZIONE: Aggiungere questo file al .gitignore.
// NON committare credenziali nel repository.
return [
    'DB_HOST'  => 'mysql.tuohoster.com',
    'DB_NAME'  => 'nome_database',
    'DB_USER'  => 'utente_mysql',
    'DB_PASS'  => 'password_sicura',
    'DB_PORT'  => 3306,
];
```
**Principio**: Le credenziali non devono mai essere hardcodate in `db.php` o in qualsiasi file committato. Il pattern `require __DIR__ . '/db_credentials.php'` carica un file separato, escluso dal version control tramite `.gitignore`.

### 3.2 `db.php` con MySQL — Il Connettore Agnostico
```php
<?php
class Database {
    private static $pdo = null;

    public static function connect() {
        if (self::$pdo === null) {
            try {
                $config = require __DIR__ . '/db_credentials.php';

                $dsn = sprintf(
                    "mysql:host=%s;dbname=%s;port=%d;charset=utf8mb4",
                    $config['DB_HOST'],
                    $config['DB_NAME'],
                    $config['DB_PORT']
                );

                self::$pdo = new PDO($dsn, $config['DB_USER'], $config['DB_PASS'], [
                    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
                    PDO::ATTR_DEFAULT_FETCH_MODE  => PDO::FETCH_ASSOC,
                    PDO::ATTR_EMULATE_PREPARES    => false, // Prepared statements nativi MySQL
                    PDO::ATTR_TIMEOUT             => 5,
                    PDO::MYSQL_ATTR_INIT_COMMAND  => "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"
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

**Differenze chiave rispetto a SQLite**:
- `PDO::ATTR_EMULATE_PREPARES => false`: Usa prepared statements nativi di MySQL. In SQLite era impostazione di default, in MySQL va forzata esplicitamente.
- `charset=utf8mb4` nel DSN + `SET NAMES utf8mb4`: Garantisce il corretto encoding di emoji e caratteri speciali.
- `PDO::ATTR_TIMEOUT => 5`: Timeout connessione di 5 secondi. Con SQLite non serviva (accesso locale al file); con MySQL (rete) è essenziale.
- Niente `PRAGMA journal_mode` o `busy_timeout`: Queste sono direttive SQLite-only.

### 3.3 `init_mysql.php` — Creazione Schema
Script che crea tutte le tabelle nel database MySQL da zero. Va eseguito **una volta sola** prima della migrazione dati. Deve essere protetto da autenticazione o IP whitelist e va eliminato dopo l'uso.

### 3.4 `migrate_to_mysql.php` — Il Trasloco Dati
Script ONE-SHOT che:
1. Apre una connessione a MySQL (destinazione).
2. Apre il file SQLite caricato temporaneamente sul server (sorgente).
3. Migra tabella per tabella con `INSERT ... ON DUPLICATE KEY UPDATE` (idempotente: ri-eseguibile senza duplicati).
4. Stampa un riepilogo con conteggi di verifica.

**Strategia di sicurezza**:
- Lo script viene caricato sul server solo per il tempo strettamente necessario.
- Dopo l'esecuzione, sia lo script che il file `.sqlite` vengono eliminati dal server.
- Il `set_time_limit(120)` previene i timeout su database grandi.

```php
// Esempio di migrazione idempotente (tabella news)
$stmt = $mysql->prepare("
    INSERT INTO news (id, slug, title, summary, content, cover_image, published_at, category)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON DUPLICATE KEY UPDATE
        title=VALUES(title),
        summary=VALUES(summary),
        content=VALUES(content),
        updated_at=NOW()
");
```

## 4. Differenze Strutturali SQLite vs MySQL

| Aspetto | SQLite | MySQL |
| :--- | :--- | :--- |
| Connessione | File locale | Rete (host:port) |
| PRAGMA | `journal_mode`, `busy_timeout`, `foreign_keys` | Non applicabili |
| Charset | Configurabile per file | `utf8mb4` per emoji e accenti |
| AUTO_INCREMENT | `INTEGER PRIMARY KEY AUTOINCREMENT` | `INT AUTO_INCREMENT PRIMARY KEY` |
| Boolean | `INTEGER` (0/1) | `TINYINT(1)` |
| JSON | Stored as TEXT | Tipo nativo `JSON` disponibile |
| Prepared Statements | Emulati di default | Nativi con `EMULATE_PREPARES=false` |
| Concurrent writes | File lock (problematico) | Gestione nativa row-level locking |
| Backup | Copia del file `.sqlite` | `mysqldump` o tool dedicati |

## 5. Il Pattern di Credenziali (Sicurezza)

Il file `db_credentials.php` deve essere aggiunto al `.gitignore` **prima del primo commit** del progetto:

```
# .gitignore
public/api/db_credentials.php
```

In produzione il file viene caricato manualmente sul server via FTP/SFTP, mai tramite pipeline automatiche o repository pubblici. Se per errore viene committato con credenziali reali, cambiare immediatamente la password del database.

## 6. Checklist di Migrazione

- [ ] Fare un backup completo del file `.sqlite` di produzione.
- [ ] Creare il database MySQL sul provider hosting.
- [ ] Caricare e eseguire `init_mysql.php` per creare lo schema.
- [ ] Caricare il `.sqlite` e `migrate_to_mysql.php` sul server.
- [ ] Eseguire `migrate_to_mysql.php` e verificare i conteggi nel riepilogo.
- [ ] Aggiornare `db.php` con la versione MySQL.
- [ ] Caricare `db_credentials.php` con le credenziali reali.
- [ ] Testare tutte le API in produzione.
- [ ] Eliminare `migrate_to_mysql.php` e il file `.sqlite` dal server.
- [ ] Aggiungere `db_credentials.php` al `.gitignore`.

---
*Prossimo Capitolo: Portfolio & Projects Module - Il modulo universale per portfolio e showcase, con ordinamento drag-and-drop.*
