# CAPITOLO 15: Database Evolution - Da SQLite a MySQL

Il 23 febbraio 2026, alle 2:25 di notte, un commit di SitoRuntime porta un messaggio asciutto: «Risolto crash server e ottimizzate performance con switch SQLite WAL->DELETE». Il giorno dopo, il 24, il sito abbandona SQLite e passa a MySQL. Le due date, a un giorno di distanza, raccontano da sole la storia di questo capitolo: la migrazione non è stata un upgrade pianificato, è stata una fuga.

È la differenza che cambia tutto. Si potrebbe descrivere il passaggio da SQLite a MySQL come una soglia di crescita: più traffico, più scritture, più contesa sul file, e a un certo punto si cambia motore. È una linea guida ragionevole, e più avanti la diamo anche noi. Ma non è la storia vera di SitoRuntime, e raccontarla così farebbe perdere la lezione più preziosa. SitoRuntime è migrato perché si era fatto male, e questo capitolo non parla di «come si migra» ma di **cosa una migrazione lascia indietro** e di chi è attrezzato a sopravvivere alla prossima notte storta.

I tre siti del Modello hanno tre rapporti diversi con la stessa tecnica. DISINTELLIGENZA gira **ancora oggi su SQLite, in produzione, senza essere mai caduta**: è la prova vivente che il problema non era il motore. SimonePizziWebSite è migrato a MySQL in silenzio, senza un incidente in git, e con una rete di salvataggio sotto. SitoRuntime è migrato in fuga, di notte, e si è lasciato dietro sei fossili e nessun backup. È lo stesso ribaltamento che attraversa tutto il libro: il sito che ha sofferto di più è quello meno preparato a soffrire di nuovo.

---

## 1. La notte del WAL: quando l'ottimizzazione è il disastro

Prima della migrazione, SitoRuntime era su SQLite e voleva andare più veloce. SQLite, di suo, può usare un journaling chiamato **WAL** (Write-Ahead Logging): più rapido in scrittura, perché accoda le modifiche in un file collaterale invece di riscrivere subito il database. Sulla carta è un'ottimizzazione. In pratica, su un hosting condiviso Apache/PHP, il WAL crea due file di servizio (`.sqlite-wal` e `.sqlite-shm`) e ha bisogno di un locking che molti hosting condivisi non gestiscono bene. I lock non si rilasciano, le richieste vanno in timeout, il sito cade.

La cura vive dentro il codice che la spiega, ed è doppia. Uno script forza il ritorno al journaling classico:

```php
// SitoRuntime optimize_db.php:17-22 — l'"ottimizzazione" che ha innescato il crash, è codice SQLite
// WAL è performante ma spesso causa blocchi su hosting condivisi.
// Impostiamo DELETE per massima stabilità.
$pdo->exec("PRAGMA journal_mode=DELETE;");   // ← PRAGMA: direttiva solo SQLite
```

E un secondo script è il pulsante rosso, da premere dal browser se il sito è già in timeout:

```php
// SitoRuntime emergency_revert_wal.php:19-43 — il kit di pronto soccorso
$result = $pdo->query("PRAGMA journal_mode=DELETE");   // rimuove i file .wal/.shm
$mode = $result->fetchColumn();
if (strtoupper($mode) === 'DELETE') echo "SUCCESSO: …ripristinato…";
$pdo->exec("VACUUM;");                                  // ricostruzione del file DB
// nel catch: "potresti dover eliminare manualmente i file .wal e .shm via FTP"
```

> [!WARNING]
> **Quando l'ottimizzazione è la causa del disastro**
> Il WAL non è un errore: in molti contesti è la scelta giusta. Ma su hosting condiviso, dove il filesystem e il locking sono fuori dal tuo controllo, toccare il `journal_mode` di un database a file è un cambiamento ad alto rischio mascherato da miglioria. È il motivo per cui il Capitolo 3 prescrive `journal_mode=DELETE` e non WAL: non è una preferenza estetica, è una lezione pagata in produzione, di notte. La regola generale: un'ottimizzazione che cambia il modo in cui il motore scrive su disco va trattata come una modifica rischiosa, con un backup prima e un piano di rientro pronto, non come un interruttore da premere e dimenticare.

La diagnosi corretta non è «SQLite non regge». È «toccare il WAL su hosting condiviso non regge». La prova arriva dal sito accanto.

---

## 2. DISINTELLIGENZA: SQLite vivo, in produzione, senza cicatrici

Mentre SitoRuntime fuggiva, DISINTELLIGENZA restava. Gira oggi su SQLite, con il database in un file dentro `.data/`, sullo stesso tipo di hosting condiviso, e non è mai caduta. Tutto ciò che in SitoRuntime è un fossile inerte (`PRAGMA`, `sqlite_master`, `AUTOINCREMENT`, il database a file) qui è il motore reale e corrente. La differenza non è il motore: è che DISINTELLIGENZA non ha mai toccato il journal mode per spremere prestazioni che non le servivano, e fa un backup `.bak` prima di ogni operazione distruttiva (CAP 10).

Questo qualifica la regola pratica, invece di smentirla. SQLite resta perfetto per i progetti leggeri o in sviluppo: zero configurazione, un file solo, deploy in pochi secondi. La soglia oltre cui conviene valutare MySQL esiste davvero, e si riconosce da segnali concreti più che da un numero:

- **scritture concorrenti frequenti**: più utenti che scrivono nello stesso istante significano più contesa sul lock del file;
- **hosting che limita o blocca SQLite** per policy interne;
- **bisogno di accesso esterno al database**, per esempio da phpMyAdmin o da strumenti di gestione visuale, che parlano con un server, non con un file;
- **query complesse su tabelle grandi**, dove MySQL gestisce join e aggregazioni meglio.

Come linea di massima, finché un sito sta sotto le poche decine di scritture all'ora e non mostra lock ricorrenti, SQLite gli basta. DISINTELLIGENZA è in quella fascia e ci resta bene. SitoRuntime ne è uscito non perché avesse superato la soglia di traffico, ma perché un'ottimizzazione sbagliata gli aveva fatto venire voglia di non avere più un database a file. Sono due strade diverse verso MySQL, e solo una delle due è quella dei manuali.

---

## 3. Far evolvere uno schema senza strumenti di migrazione

C'è un tratto che i tre siti condividono, ed è il vero contesto di tutto il capitolo: **nessuno di loro ha uno strumento di migrazione**. Niente cartella `migrations/`, niente tabella `schema_version`, niente runner che tenga il conto di cosa è già stato applicato. Lo schema evolve con un solo attrezzo, lo stesso ovunque.

L'attrezzo è `ALTER TABLE … ADD COLUMN` dentro un `try/catch`, reso idempotente. Si aggiunge la colonna, e se l'errore dice che esiste già la si tratta come successo. Su MySQL il segnale è il codice `Duplicate column`:

```php
// SitoRuntime migrate_status.php:6-16 — la micro-migrazione che si auto-ripara
$pdo->exec("ALTER TABLE news ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'published'");
// …
} catch (PDOException $e) {
    if ($e->getCode() == '42S21' || strpos($e->getMessage(), 'Duplicate column') !== false) {
        echo "OK: colonna 'status' già presente.\n";   // ri-esecuzione = nessun danno
    } else { echo "ERRORE: " . $e->getMessage() . "\n"; }
}
```

Su SQLite la stessa filosofia cambia dialetto: si interroga `PRAGMA table_info` e si aggiunge la colonna solo se manca.

```php
// DISINTELLIGENZA update_db_v0.4.2.php:10-17 — stesso pattern, dialetto SQLite
$columns = $pdo->query("PRAGMA table_info(users)")->fetchAll(PDO::FETCH_COLUMN, 1);
if (!in_array('role', $columns)) {
    $pdo->exec("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'editor'");
    $logs[] = "Added 'role' column to users table.";
} else {
    $logs[] = "'role' column already exists in users table.";
}
```

Il prezzo di questa semplicità è che **nessun file rappresenta lo schema corrente**. La versione è implicita, scritta nei nomi dei file: DISINTELLIGENZA ha una catena `update_db_0_1_3` → `0_1_4` → `v0.4.2` → `v0.5.4`, SitoRuntime ha `apply_v291` e `apply_v293`. Per sapere com'è fatta davvero una tabella oggi, non basta leggere un file: bisogna interrogare il database, oppure ricostruire la storia dai nomi e dall'ordine in cui sono stati eseguiti.

> [!WARNING]
> **Senza un registro, la verità dello schema vive solo nel database**
> Versionare lo schema con i nomi dei file funziona finché c'è una persona sola che ricorda l'ordine. Ma non esiste un percorso pulito per ricreare il database da zero: in SitoRuntime servirebbe `init_mysql.php` più la catena `apply_v29x` applicata nell'ordine giusto, e l'`init_db.php` di partenza è un fossile fermo a una versione vecchia. È il debito «schema-as-code» del thin stack: il prezzo da pagare per non aver adottato un sistema di migrazioni. Se il progetto cresce, una tabella `schema_version` con un elenco di migrazioni applicate costa poco e ripaga al primo disaster recovery.

A questo si aggiunge una doppiezza di consegna. La stessa migrazione spesso esiste in due forme: come file usa-e-getta da caricare e cancellare, e come azione persistente dentro la console admin. La colonna `status` di SitoRuntime, per esempio, vive sia in `migrate_status.php` sia come azione `?action=apply_v291_status` dentro `admin.php`:

```php
// SitoRuntime admin.php:459-469 — la stessa migrazione, ma self-healing dietro il login
if ($action === 'apply_v291_status' && $_SERVER['REQUEST_METHOD'] === 'GET') {
    try {
        getDB()->exec("ALTER TABLE news ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'published'");
        sendSuccess(['message' => "OK: colonna 'status' aggiunta…"]);
    } catch (PDOException $e) {
        if (strpos($e->getMessage(), 'Duplicate column') !== false) sendSuccess([/* … */]);
        else sendError('Errore DB: ' . $e->getMessage(), 500);
    }
}
```

Due filosofie convivono: lo script da FTP-are e poi rimuovere, e la console di manutenzione dietro login. Sono entrambe legittime, ma senza un registro nessuna delle due ti dice, guardandola, se quella migrazione è già passata su un certo database. Sono GET protette dal solo `isLoggedIn`, non dal ruolo né da un token CSRF: la loro innocuità dipende dall'essere idempotenti, non da una vera barriera (è lo stesso buco di gate visto al CAP 14).

---

## 4. Il trasloco di motore: il pattern a tre script

Quando la migrazione di motore è stata decisa, SitoRuntime l'ha eseguita con tre script dedicati, ciascuno con un ruolo preciso. È un ETL fatto a mano, senza strumenti, ed è un pattern positivo e citabile.

Il primo è il file dei segreti, tenuto fuori dal version control:

```php
// db_credentials.php — da aggiungere SUBITO al .gitignore, mai committare credenziali reali
<?php
return [
    'DB_HOST' => 'mysql.tuohoster.com',
    'DB_NAME' => 'nome_database',
    'DB_USER' => 'utente_mysql',
    'DB_PASS' => 'password_sicura',
    'DB_PORT' => 3306,
];
```

Il secondo è il connettore MySQL, che sostituisce la versione SQLite di `db.php`:

```php
// db.php (versione MySQL) — il singleton di connessione
$config = require __DIR__ . '/db_credentials.php';
$dsn = sprintf("mysql:host=%s;dbname=%s;port=%d;charset=utf8mb4",
               $config['DB_HOST'], $config['DB_NAME'], $config['DB_PORT']);
self::$pdo = new PDO($dsn, $config['DB_USER'], $config['DB_PASS'], [
    PDO::ATTR_ERRMODE           => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES   => false,   // prepared statement nativi: su SQLite era il default, qui va forzato
    PDO::ATTR_TIMEOUT            => 5,        // SQLite leggeva un file locale; MySQL è in rete, il timeout serve
    PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"
]);
```

Tre dettagli del passaggio meritano attenzione. `EMULATE_PREPARES => false` attiva i prepared statement nativi, che su SQLite erano impliciti. Il `charset=utf8mb4` nel DSN più il `SET NAMES` garantiscono che emoji e accenti sopravvivano. E il `PDO::ATTR_TIMEOUT` compare per la prima volta: con un file locale non serviva, con un server in rete è essenziale. Spariscono invece tutte le direttive `PRAGMA`: `journal_mode`, `busy_timeout`, `foreign_keys` erano linguaggio SQLite e su MySQL non hanno senso.

Il terzo script, `init_mysql.php`, ricrea lo schema da zero in dialetto MySQL, va eseguito una volta sola, protetto da autenticazione e poi rimosso. E il quarto, il vero trasloco, è l'ETL: apre due connessioni, copia tabella per tabella in modo idempotente, e chiude con una verifica esplicita.

```php
// SitoRuntime migrate_to_mysql.php:37-72,199-209 — due PDO, copia idempotente, verifica conteggi
$sqlite = new PDO("sqlite:" . $sqlitePath);   // sorgente: il file
$mysql  = Database::connect();                 // destinazione: MySQL
$rows = $sqlite->query("SELECT * FROM news ORDER BY id ASC")->fetchAll();
$stmt = $mysql->prepare("INSERT INTO news (id, slug, title, summary, content, …)
                         VALUES (?, ?, ?, ?, ?, …)
                         ON DUPLICATE KEY UPDATE title=VALUES(title), …");   // ri-eseguibile
foreach ($rows as $r) { $stmt->execute([$r['id'], $r['slug'], …]); $count++; }
// alla fine, la prova del nove tabella per tabella:
foreach (['news','users','subscribers','speakers','podcasts'] as $t) {
    $c = $mysql->query("SELECT COUNT(*) FROM $t")->fetchColumn();
    echo "  $t: $c record in MySQL\n";
}
```

> [!TIP]
> **L'ETL del thin stack: due PDO e un COUNT**
> Per spostare i dati tra due motori non serve uno strumento dedicato: bastano due connessioni PDO, un loop che copia con `ON DUPLICATE KEY UPDATE` (così la copia si può ripetere senza creare doppioni) e un `COUNT(*)` finale che conferma quanti record sono arrivati a destinazione. È la versione minimale, leggibile e verificabile di una migrazione di dati. Lo script poi va caricato sul server solo per il tempo necessario e cancellato insieme al file `.sqlite`: restare in giro è un rischio, non una comodità.

---

## 5. Cosa cambia, riga per riga, tra i due motori

Il passaggio tocca decine di micro-decisioni. La tabella le riassume.

| Aspetto | SQLite | MySQL |
| :--- | :--- | :--- |
| Connessione | file locale | rete (host:port) |
| Direttive di motore | `PRAGMA journal_mode`, `busy_timeout`, `foreign_keys` | non applicabili |
| Charset | configurabile per file | `utf8mb4` per emoji e accenti |
| Auto-increment | `INTEGER PRIMARY KEY AUTOINCREMENT` | `INT AUTO_INCREMENT PRIMARY KEY` |
| Boolean | `INTEGER` (0/1) | `TINYINT(1)` |
| JSON | salvato come `TEXT` | tipo nativo `JSON` |
| Prepared statement | nativi di default | nativi con `EMULATE_PREPARES=false` |
| Scritture concorrenti | lock sul file (problematico) | locking a livello di riga, gestito dal demone |
| Backup | copia del file `.sqlite` | `mysqldump` o strumenti dedicati |

L'ultima riga è quella che fa più male a SitoRuntime, e ci arriviamo tra poco.

---

## 6. I sei fossili: l'igiene del repo dopo una migrazione

Dopo lo switch, lo strato SQLite non è stato rimosso. Restano in un repository MySQL **sei file scritti per un motore che non esiste più**: inerti nel migliore dei casi, rotti nel peggiore.

| Fossile | Meccanismo SQLite | Stato su MySQL |
| :--- | :--- | :--- |
| `init_db.php` | `AUTOINCREMENT`, seed dei 24 speaker | crea tipi sbagliati, parzialmente rotto |
| `fix_users_table.php` | `sqlite_master`, `PRAGMA`, `datetime('now')` | **rotto** (PRAGMA dà errore di sintassi) |
| `fix_newsletter_table.php` | `sqlite_master`, `PRAGMA`, schema a 4 colonne | **rotto** e obsoleto |
| `setup_podcasts.php` | `AUTOINCREMENT` | parzialmente innocuo |
| `optimize_db.php` | `PRAGMA journal_mode`, `CREATE INDEX IF NOT EXISTS` | **rotto** |
| `emergency_revert_wal.php` | `PRAGMA`, `VACUUM` | **inerte** (il WAL non esiste su MySQL) |

Il fossile più velenoso è il primo. `fix_users_table.php` interroga lo schema con dialetto SQLite, su un database che ormai è MySQL:

```php
// SitoRuntime fix_users_table.php:12,20 — codice che parla la lingua del motore sbagliato
$stmt = $pdo->query("SELECT name FROM sqlite_master WHERE type='table' AND name='users'");  // SQLite!
$stmt = $pdo->query("PRAGMA table_info(users)");        // su MySQL → errore di sintassi
$pdo->exec("UPDATE users SET created_at = datetime('now') WHERE created_at IS NULL");        // datetime() = SQLite
```

L'unica rete che li tiene a freno è il deny by-prefix di `.htaccess`, che blocca l'esecuzione via HTTP di tutti gli script con un nome di manutenzione:

```apache
# SitoRuntime public/.htaccess:32-35 — l'unico argine ai fossili
RewriteRule ^(debug_|test_|emergency_|migrate_|fix_|init_|rebuild_|setup_|optimize_) - [F,L]
```

> [!WARNING]
> **Una migrazione di motore va completata anche cancellando**
> Quegli script sono ancora sul server e ancora nel repo. Producono tre danni: rumore (chi apre il progetto non sa quali file contano), confusione sulla verità dello schema, e una superficie d'attacco latente, perché se un giorno il deny dell'`.htaccess` saltasse, sarebbero endpoint potenti raggiungibili. Migrare di motore non è finito quando i dati sono passati: è finito quando il codice del motore vecchio è stato rimosso. Tenere i fossili «per sicurezza» è il contrario della sicurezza.

---

## 7. Una tabella, tre `CREATE` diversi

Il debito «nessun file rappresenta lo schema» ha un volto concreto nella tabella `subscribers` di SitoRuntime, che nel codice esiste in **tre definizioni divergenti**:

1. `init_mysql.php` la crea con quattro colonne, lo schema base, precedente al double opt-in.
2. `fix_newsletter_table.php`, il fossile SQLite, ricrea le stesse quattro colonne, ed è rotto su MySQL e comunque insufficiente.
3. `apply_v293_newsletter`, dentro `admin.php`, è la **vera** migrazione: aggiunge le colonne del double opt-in (`confirmation_token`, `confirmed_at`, `subscribed_at`, `subscribed_ip`) e conferma retroattivamente gli iscritti storici.

Solo la terza è allineata al runtime. Il codice della newsletter (CAP 13) **presuppone** lo schema esteso, quindi su un database che ha solo lo schema base ogni query fallisce finché `apply_v293` non gira. È una dipendenza d'ordine non dichiarata: lo schema giusto esiste, ma solo se hai eseguito la migrazione giusta, che nessun file ti dice di eseguire.

> [!WARNING]
> **Dove vive la verità di una tabella**
> Quando la stessa tabella ha tre `CREATE` sparsi in tre file, e solo uno è quello buono, la fonte di verità non è il codice ma il database in esecuzione. È un sintomo dello schema versionato per nomi-file: la definizione corretta esiste, ma è nascosta nella catena delle migrazioni invece che in un punto solo. Lo si paga il giorno in cui qualcuno ricrea il database dal file sbagliato e tutto sembra a posto finché il runtime non comincia a fallire.

---

## 8. Il bug della data come stringa

Le migrazioni lasciano cicatrici anche nei dati, non solo nello schema. SitoRuntime conserva `debug_time.php`, la diagnostica di un incidente di fuso orario. La regola di visibilità degli articoli confronta `published_at <= adesso` **come stringhe**: se il fuso del server e il formato della data non combaciano, gli articoli pubblicati spariscono dal sito.

```php
// SitoRuntime debug_time.php:23-24 — la "fix" che non è mai arrivata in produzione
// FIX: Use T separator to match DB
$now = date('Y-m-d\TH:i:s');   // separatore 'T'
```

Il dettaglio rivelatore è che questa fix non è mai stata applicata al runtime. Il codice di produzione (`news.php`) usa lo spazio, non la `T`, perché lo spazio è il formato corretto del DATETIME di MySQL. La «soluzione» con la `T` è rimasta solo nel file di diagnostica, documento di un bug del passato e di una correzione che il sito reale, alla fine, non ha adottato.

> [!TIP]
> **Confrontare date come stringhe è un bug in agguato**
> Due date confrontate come testo coincidono solo se hanno esattamente lo stesso formato e lo stesso fuso. Basta una `T` al posto di uno spazio, o un server impostato su UTC mentre i contenuti sono scritti in ora locale, perché un articolo «pubblicato» resti invisibile. La difesa è forzare il fuso in modo esplicito (`date_default_timezone_set('Europe/Rome')`) e confrontare valori nello stesso formato del tipo data del database, oppure delegare il confronto al database con `NOW()`.

---

## 9. La cura senza la prevenzione

Resta la riga più dolorosa della tabella del §5: il backup. SitoRuntime ha il defibrillatore, l'`emergency_revert_wal.php`, lo script che rianima il sito dopo l'incidente. Ma non ha il check-up: nessun backup automatico, nessun cron, nessun `mysqldump` schedulato. L'unica rete è una cartella `_BACKUP_BEFORE_OPTIMIZATION/`, uno snapshot manuale del progetto committato nel repo prima dell'intervento rischioso. È un gesto, non un sistema, e per giunta è rumore versionato.

Il contrasto con gli altri due è netto. SimonePizziWebSite ha il backup automatico scritto fuori dalla document root, con rotazione e un cron protetto (CAP 14). DISINTELLIGENZA fa un `.bak` prima di ogni reset distruttivo (CAP 10). Se il MySQL di SitoRuntime si corrompe, non c'è un dump recente da cui ripartire.

> [!WARNING]
> **Avere il defibrillatore ma non l'allarme antincendio**
> È il paradosso al cuore del capitolo. Il sito mappato proprio per i suoi incidenti è quello senza la rete più elementare: un backup. Ha imparato a *curare* il disastro, lo script di emergenza è la prova che il dolore è stato vero, ma non ha imparato a *prevenirlo*. Curare un'emergenza è reattivo: ti tiene in vita per questa volta. Un backup automatico è preventivo: ti tiene in vita per la prossima, quella che non hai previsto. La checklist qui sotto prescrive un backup, ed è il dover essere; SitoRuntime racconta cosa succede a saltarlo.

---

## 10. Checklist di migrazione

La sequenza, in ordine, per un passaggio SQLite → MySQL fatto bene. Il primo punto è anche quello che SitoRuntime non aveva: non è un dettaglio, è la rete.

- [ ] Fare un backup completo del file `.sqlite` di produzione, e archiviarlo fuori dal repo.
- [ ] Creare il database MySQL sul provider di hosting.
- [ ] Caricare ed eseguire `init_mysql.php` per creare lo schema, poi rimuoverlo.
- [ ] Caricare il `.sqlite` e `migrate_to_mysql.php` sul server.
- [ ] Eseguire `migrate_to_mysql.php` e verificare i conteggi nel riepilogo.
- [ ] Sostituire `db.php` con la versione MySQL e caricare `db_credentials.php` con le credenziali reali.
- [ ] Aggiungere `db_credentials.php` al `.gitignore` (prima del primo commit del progetto).
- [ ] Testare tutte le API in produzione, comprese quelle che presuppongono migrazioni successive allo schema base.
- [ ] Eliminare dal server `migrate_to_mysql.php` e il file `.sqlite`.
- [ ] **Rimuovere dal repo i fossili del vecchio motore** (`init_db.php` SQLite, `fix_*`, `optimize_db.php`, `emergency_revert_wal.php`): la migrazione non è finita finché restano.
- [ ] Configurare un backup automatico del MySQL, fuori dalla document root: la cura non sostituisce la prevenzione.

---

## In sintesi

La migrazione di motore non è un gradino di scaling che prima o poi tutti salgono: è un evento, e il *perché* conta quanto il *come*. SitoRuntime è scappato da SQLite dopo una notte storta, e ha portato MySQL con sé senza ripulire la casa, lasciandosi dietro sei fossili, tre versioni della stessa tabella e nessun backup. DISINTELLIGENZA dimostra che SQLite in produzione regge benissimo, finché non gli si chiede un'ottimizzazione che non sa dare sul suo terreno. SimonePizziWebSite ha fatto lo stesso viaggio in silenzio, con la rete sotto. La lezione non è «migra a MySQL» e nemmeno «resta su SQLite»: è che ogni evoluzione di schema, e ancora di più ogni cambio di motore, va completata fino in fondo, con un registro di cosa hai fatto e un backup di cosa avevi prima. Quello che una migrazione lascia indietro pesa più di quello che porta avanti.

> [!IMPORTANT]
> **Il Canone**
> - Migra di motore solo per un vincolo concreto (lock ricorrenti, hosting, accesso remoto), non per scaramanzia; fai il backup **prima**, fuori dal repo.
> - ETL idempotente (`ON DUPLICATE KEY UPDATE`) con verifica dei conteggi a fine trasloco.
> - A migrazione conclusa, rimuovi i fossili del vecchio motore dal repo.
> - Una sola definizione per ogni tabella e un registro dello schema (`schema_version`); la cura d'emergenza non sostituisce la prevenzione, cioè il backup automatico.

---
*Prossimo Capitolo: Portfolio & Projects Module. Il modulo universale per portfolio e showcase, con riordinamento drag-and-drop e visibilità a interruttore.*
