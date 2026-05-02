# CAPITOLO 14: Database Evolution - Da SQLite a MySQL (v1.1)

Questo capitolo documenta il percorso reale di migrazione da SQLite a MySQL, focalizzandosi sulle best practice di connessione e sulla sicurezza dei dati sensibili.

## 1. Quando e Perchè Migrare

SQLite è perfetto per progetti leggeri. MySQL diventa essenziale quando:
- **Traffico crescente**: Più utenti simultanei richiedono la gestione nativa dei lock a livello di riga.
- **Accesso Remoto**: Necessità di gestire il DB tramite tool esterni (phpMyAdmin, TablePlus).
- **Scalabilità**: Necessità di separare il server web dal server database.

## 2. La Lezione del WAL Mode
In produzione (hosting Apache), il WAL mode di SQLite può causare corruzione dei dati se il file di lock non viene rilasciato correttamente. Il Modello Universale impone il `journal_mode=DELETE` come standard di massima affidabilità su hosting condiviso.

## 3. Best Practice di Connessione MySQL
La transizione a MySQL richiede una configurazione PDO rigorosa per garantire sicurezza e performance.

### 3.1 Il File dei Segreti (`db_credentials.php`)
Le credenziali **non devono mai essere committate**. Il file `db_credentials.php` deve essere escluso dal controllo di versione.
```php
<?php
// public/api/db_credentials.php
return [
    'DB_HOST'  => 'localhost',
    'DB_NAME'  => 'miocms_db',
    'DB_USER'  => 'admin',
    'DB_PASS'  => 'password_molto_sicura',
    'DB_PORT'  => 3306,
];
```

### 3.2 Configurazione PDO Avanzata
Nel file `db.php`, la connessione deve includere parametri specifici:
- **Charset `utf8mb4`**: Essenziale per il supporto completo a emoji e caratteri speciali (unicode).
- **`EMULATE_PREPARES => false`**: Forza l'uso dei prepared statements nativi di MySQL. Questo è il pilastro della **sicurezza contro le SQL Injection**, poiché la query e i dati vengono inviati separatamente al server.
- **Error Mode Exception**: Per intercettare e loggare correttamente i problemi di rete o autenticazione.

```php
self::$pdo = new PDO($dsn, $config['DB_USER'], $config['DB_PASS'], [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE  => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES    => false, // Sicurezza: Prepared statements nativi
    PDO::MYSQL_ATTR_INIT_COMMAND  => "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"
]);
```

## 4. Checklist di Migrazione

- [ ] **Backup**: Export completo del file `.sqlite`.
- [ ] **Schema**: Esecuzione di `init_mysql.php` per creare le tabelle.
- [ ] **Migrazione Dati**: Uso di `migrate_to_mysql.php` con logica `ON DUPLICATE KEY UPDATE` per l'idempotenza.
- [ ] **Sicurezza**: Verificare che `db_credentials.php` sia nel `.gitignore`.
- [ ] **Bonifica**: Eliminazione degli script di migrazione e del file `.sqlite` dal server dopo il completamento.

## 5. Evoluzione MySQL e Sicurezza
L'adozione di MySQL permette di implementare policy di backup automatici (es. cronjob con `mysqldump`) e di limitare l'accesso al database solo a specifici indirizzi IP (Whitelist), aumentando drasticamente il livello di sicurezza rispetto a un file `.sqlite` potenzialmente scaricabile se non protetto correttamente via `.htaccess`.

---
*Prossimo Capitolo: Portfolio & Projects Module - Il modulo universale per portfolio e showcase.*
