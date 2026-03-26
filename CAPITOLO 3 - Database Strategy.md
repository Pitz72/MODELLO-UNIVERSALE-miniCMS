# CAPITOLO 3: Database Strategy (v1.2 - ADVANCED)

Il database è il cuore pulsante del miniCMS. Questa sezione definisce le strategie di ottimizzazione, integrità e migrazione per garantire performance "zero-latency" anche su hosting condivisi.

## 1. Architettura di Connessione (Agnostic PDO)
Il sistema utilizza un wrapper PDO che astrae il motore sottostante.

### 1.1 Configurazione Ottimale SQLite
Per evitare il problema dei "file lock" comuni su Apache/PHP, il Modello Universale impone:
- **Journal Mode: DELETE**: Più lento di WAL ma infinitamente più stabile su hosting condivisi dove il locking del file system è imprevedibile.
- **Busy Timeout**: Impostato a 5000ms per gestire tentativi di scrittura simultanei (es. Newsletter + Admin).

```php
// In db.php
self::$pdo = new PDO("sqlite:" . $dbPath);
self::$pdo->exec("PRAGMA journal_mode=DELETE;");
self::$pdo->exec("PRAGMA busy_timeout=5000;");
self::$pdo->exec("PRAGMA foreign_keys = ON;");
```

**⚠️ Perché DELETE e non WAL**: SitoRuntime ha tentato di usare `journal_mode=WAL` in produzione per migliorare le performance sotto carico. Il WAL ha causato problemi gravi su hosting condiviso Apache: il file di lock `.sqlite-wal` rimaneva "appeso" corrompendo le letture. È stato necessario uno script di emergenza (`emergency_revert_wal.php`) per tornare a DELETE. **Questa è la lezione: usare sempre DELETE mode su hosting condiviso.**

### 1.2 Auto-Scaffolding della Cartella .data
La classe `Database` in **SimonePizziWebSite** integra la creazione automatica della cartella `.data/` e del relativo `.htaccess` di protezione direttamente nella connessione lazy:

```php
public static function connect() {
    if (self::$pdo === null) {
        $dbPath = __DIR__ . '/.data/database.sqlite';
        $dir    = dirname($dbPath);

        // Crea la cartella se non esiste
        if (!is_dir($dir)) {
            mkdir($dir, 0777, true);
        }

        // Protezione immediata con .htaccess
        $htaccessPath = $dir . '/.htaccess';
        if (!file_exists($htaccessPath)) {
            file_put_contents($htaccessPath, "Require all denied\n");
        }

        try {
            self::$pdo = new PDO('sqlite:' . $dbPath);
            self::$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            self::$pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
            self::$pdo->exec('PRAGMA journal_mode = DELETE;');
            self::$pdo->exec('PRAGMA foreign_keys = ON;');
        } catch (PDOException $e) {
            http_response_code(500);
            echo json_encode(['status' => 'error', 'message' => 'Database connection failed']);
            exit;
        }
    }
    return self::$pdo;
}
```

## 2. Indicizzazione Strategica (Performance Engineering)
Le query di lettura devono essere istantanee. Il Modello Universale impone la creazione dei seguenti indici:

| Tabella | Colonna | Tipo | Scopo |
| :--- | :--- | :--- | :--- |
| `news` / `articles` | `slug` | UNIQUE | Ricerca articolo via URL (SEO) |
| `news` / `articles` | `published_at` | DESC | Ordinamento cronologico veloce |
| `news` / `articles` | `status` | INDEX | Filtraggio Bozza/Pubblicato |
| `speakers` | `sort_order` | ASC | Ordinamento manuale trascinabile |
| `podcasts` | `slug` | UNIQUE | Accesso rapido alle serie |
| `projects` | `category` | INDEX | Filtraggio per categoria portfolio |
| `projects` | `sort_order` | ASC | Ordinamento manuale portfolio |

**Comando di Manutenzione**: Periodicamente (o dopo caricamenti massivi) deve essere eseguito `ANALYZE;` per ricalcolare le statistiche di accesso e ottimizzare il piano di esecuzione delle query.

## 3. Ciclo di Vita delle Migrazioni (Safe-Schema Update)
Le modifiche allo schema devono essere atomiche e reversibili.
- **Atomicità**: Ogni script di migrazione deve utilizzare le transazioni (`beginTransaction`).
- **Idempotenza**: Lo script deve verificare l'esistenza di colonne o tabelle prima di tentare la creazione (`IF NOT EXISTS`, `PRAGMA table_info`).
- **Protezione**: Gli script di migrazione (`update_db_vX.X.X.php`) devono essere protetti da controllo sessione admin per evitare esecuzioni non autorizzate.
- **Nomenclatura**: Il pattern di naming dei siti reali: `update_db_v0.4.2.php`, `update_db_v0.5.4.php`. Numerazione semantica (Major.Minor.Patch) allineata alla versione del progetto in `package.json`.

## 4. Normalizzazione Dati (The "Round" Rule)
Per evitare errori di precisione nei calcoli (es. durata podcast o bitrate), il sistema impone la normalizzazione lato backend prima del salvataggio:
- **Date**: Formato ISO 8601 (`Y-m-d H:i:s`) per compatibilità SQL e JS.
- **Numerici**: Interi puri o arrotondati a zero decimali per evitare bug di virgola mobile tra PHP e SQLite.
- **Booleani**: Sempre `INTEGER` in SQLite (`0` o `1`). In MySQL `TINYINT(1)`.

## 5. Manutenzione e Integrità
- **VACUUM**: Da eseguire mensilmente o post-cancellazione massiva per ricostruire il file database e ridurne il peso fisico.
- **Backup**: Ogni operazione di migrazione deve essere preceduta da una copia fisica del file `.sqlite` in una cartella di backup protetta.
- **optimize_db.php**: SitoRuntime include uno script dedicato alla manutenzione (`VACUUM`, `ANALYZE`, verifica integrità) eseguibile manualmente dall'admin.

## 6. Quando Passare a MySQL
Vedi Capitolo 14 per la storia completa e il processo di migrazione. In sintesi: rimani su SQLite finché il traffico è gestibile (< 50 scritture/ora) e non ci sono vincoli di hosting. La migrazione è documentata con script reali, testati in produzione.

---
*Prossimo Capitolo: Frontend Dependencies - La matrice delle dipendenze, le regole di scelta e il costo di ogni libreria.*
