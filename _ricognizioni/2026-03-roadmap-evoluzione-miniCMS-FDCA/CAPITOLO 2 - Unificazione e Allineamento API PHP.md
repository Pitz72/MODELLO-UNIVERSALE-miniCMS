# CAPITOLO 2: Unificazione e Allineamento API PHP

FDCA deve adottare la stessa logica di gestione dati di `DISINTELLIGENZA` per essere compatibile con i componenti React di admin.

## 1. Allineamento Database (db.php)
Assicurarsi che la classe `Database` punti alla nuova cartella protetta:
```php
$dbPath = __DIR__ . '/.data/database.sqlite';
```

## 2. Allineamento Logica News (news.php)
Modificare `news.php` affinché utilizzi il filtro temporale evoluto:
- **Pubblico**: `WHERE status = 'published' AND published_at <= CURRENT_TIMESTAMP`
- **Admin**: Bypass del filtro tramite controllo sessione `$_SESSION['role'] === 'admin'`.

## 3. Inizializzazione Dati (init_db.php)
FDCA richiede una tabella `news` e una tabella `users` perfettamente compatibili con le chiamate React:
- La password dell'admin deve essere hashata con `password_hash('password', PASSWORD_DEFAULT)`.
- La tabella `news` deve includere i campi `status` (draft/published), `published_at` (datetime) e `slug` (unique).

## 4. Gestione Media (upload.php)
Il file `upload.php` deve includere la funzione di **Auto-Resize** delle immagini e deve saper distinguere tra upload audio e immagini tramite il parametro `$_POST['type']`.

---
*Obiettivo: Rendere il backend uno specchio perfetto di DISINTELLIGENZA, pronto per essere consumato dall'admin.*
