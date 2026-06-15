# Mappatura — SitoRuntime — C13: DB Evolution & Incidenti

> **Stato:** COMPLETATO
> **Sessione:** 20 (SR-C13 da sola — **ULTIMA card di SitoRuntime**) · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `SitoRuntime/`)
> - `public/api/init_db.php` (init "fossile" **SQLite** con seed reale 24 speaker + admin `runtime2026`)
> - `public/api/init_mysql.php` (schema **MySQL** vivo — 5 tabelle)
> - `public/api/migrate_to_mysql.php` (migratore one-shot SQLite→MySQL: copia dati + `ON DUPLICATE KEY` + verifica conteggi)
> - `public/api/migrate_status.php` (micro-migrazione `news.status`, gemella one-shot di `apply_v291_status`)
> - `public/api/setup_podcasts.php` (scaffolding+seed `podcasts` idempotente, **SQLite-flavor**)
> - `public/api/fix_users_table.php` · `public/api/fix_newsletter_table.php` (micro-migrazioni **fossili SQLite**: `sqlite_master`/`PRAGMA`)
> - `public/api/optimize_db.php` (**la "ottimizzazione" che ha causato l'incidente WAL** — `PRAGMA journal_mode=DELETE` + indici SQLite)
> - `public/api/emergency_revert_wal.php` (**lo script di emergenza** — disattiva WAL, `VACUUM`)
> - `public/api/debug_time.php` (incidente fuso/formato-data, separatore `T`) · `test_index.php` (diagnostica proxy SEO)
> - `public/api/admin.php:373-396` (`apply_v293_newsletter`) · `:458-470` (`apply_v291_status`) · `:472-523` (`fix_image_paths`, storia raster→WebP)
> - `public/.htaccess:32-35` (deny by-prefix dei 9 prefissi di manutenzione)
> - **Archeologia repo:** `_BACKUP_BEFORE_OPTIMIZATION/` (snapshot pre-incidente, con `mysql.txt`), `_ARCHIVIO/pw_reset.php` (fossile reset password)
> - **Git:** `42e2b95` (migrazione MySQL) · `fb31c25` (l'incidente WAL, 2026-02-23 02:25) · `db.php:3` (data migrazione 24/02/2026)

---

## 1. Cosa fa (sintesi narrativa)

Questa card non mappa un *cluster funzionale* ma una **dimensione temporale**: come lo schema di
SitoRuntime è nato, è cambiato, si è rotto e come è stato riparato. È il capitolo che SPW non ha (lì
gli incidenti erano sparsi tra le card); qui SitoRuntime li **concentra**, perché il sito porta
addosso la cicatrice più visibile di tutte: una **migrazione di motore DB** (SQLite → MySQL)
avvenuta in produzione, preceduta di **un solo giorno** da un **crash del server**.

La cronologia ricostruita dal codice e da `git` è netta:

1. **Era SQLite.** Il sito nasce su SQLite (`init_db.php` con `INTEGER PRIMARY KEY AUTOINCREMENT`, il
   seed news dice *"CMS gestito da SQLite"*). Lo schema si evolve a colpi di `ALTER TABLE ADD COLUMN`
   dentro `try/catch` ("HOTFIXES" in `init_db.php:23-29,72-84`).
2. **L'incidente WAL (23/02/2026, 02:25).** Per "ottimizzare" si tocca il *journal mode* di SQLite.
   Su hosting condiviso la modalità **WAL** causa blocchi di file-locking → il sito va in **timeout /
   crash**. Il commit `fb31c25` — *"Risolto crash server e ottimizzate performance con switch SQLite
   WAL->DELETE…"*, fatto **alle 2 di notte** — è la pezza. Restano in repo i due script gemelli:
   `optimize_db.php` (che **forza** `journal_mode=DELETE`) e `emergency_revert_wal.php` (il pulsante
   rosso da premere "se il sito va in timeout dopo l'ottimizzazione").
3. **La migrazione a MySQL (24/02/2026).** Il giorno **dopo** il crash, si abbandona SQLite:
   `init_mysql.php` ricrea lo schema in dialetto MySQL, `migrate_to_mysql.php` travasa i dati
   (`db.php:3` data la migrazione "24/02/2026"; commit `42e2b95`). La migrazione di motore è quindi,
   con ogni probabilità, **la reazione diretta** all'incidente WAL: il modo definitivo di non avere
   più file-lock su hosting condiviso è smettere di usare un DB *a file*.
4. **L'era MySQL (oggi).** Lo schema continua a evolvere, ma con un **doppio binario**: micro-migrazioni
   `migrate_*` one-shot **e** le stesse migrazioni **self-healing dentro `admin.php`** (`apply_v291_status`,
   `apply_v293_newsletter`). Intanto in repo restano i **fossili SQLite** (`init_db.php`,
   `fix_users_table.php`, `fix_newsletter_table.php`, `optimize_db.php`, `emergency_revert_wal.php`,
   `setup_podcasts.php`): scritti per un motore che non esiste più, oggi **inerti o rotti** su MySQL,
   ma ancora caricati sul server (neutralizzati solo dal deny by-prefix di `.htaccess`).

Il valore per il manuale è enorme: SitoRuntime è il caso reale di **"come si evolve uno schema senza
strumento di migrazione"** e di **"cosa lascia indietro una migrazione di motore"**.

## 2. Pattern miniCMS rilevanti

- **Migrazione di motore "a mano" con verifica.** `migrate_to_mysql.php` è il pattern-chiave: apre
  *due* PDO (SQLite sorgente + MySQL destinazione), copia tabella per tabella con `INSERT … ON
  DUPLICATE KEY UPDATE` (idempotente, ri-eseguibile) e **chiude con un `COUNT(*)` di verifica** su
  ogni tabella MySQL. È la versione "thin stack" di un ETL: nessun tool, solo PHP + due connessioni +
  un riepilogo conteggi a video.
- **Micro-migrazione idempotente "ALTER + skip Duplicate".** Filosofia ricorrente: `ALTER TABLE …
  ADD COLUMN` in `try/catch`, e se l'errore contiene `Duplicate column` (MySQL 1060/42S21) lo si
  tratta come **successo** ("già presente"). Compare in `migrate_status.php`, `apply_v291_status`,
  `apply_v293_newsletter`. È "lo schema che si auto-ripara, eseguibile N volte senza danni".
- **Doppio binario one-shot vs self-healing.** La *stessa* migrazione esiste in due forme: come file
  da cancellare (`migrate_status.php`, gated `^migrate_`) **e** come azione `?action=` dentro
  `admin.php` (`apply_v291_status`, gated `isLoggedIn`). Due filosofie di delivery convivono nel
  sito: "script usa-e-getta" vs "console di manutenzione persistente dietro login".
- **Scaffolding idempotente con seed da costante.** `setup_podcasts.php` crea la tabella e
  re-inserisce i 37 podcast solo se lo `slug` non esiste già (SELECT-prima-di-INSERT) — il seed è la
  copia server-side di `constants.ts` del frontend.
- **`ALTER … ADD COLUMN` come unico strumento di evoluzione schema.** Non esiste un sistema di
  versioni di migrazione (niente tabella `migrations`/`schema_version`): la "versione" dello schema è
  **implicita** nel nome dell'azione (`apply_v291`, `apply_v293`) e nessuno tiene il conto di cosa è
  già stato applicato su un dato DB. La fonte di verità è dispersa.
- **Fossile di motore precedente lasciato in repo.** Pattern (anti-pattern) cross-sito già visto in
  SPW-C1 e SR-C1: dopo una migrazione di motore, l'`init` del vecchio motore **non** viene rimosso.
  Qui è amplificato: non un solo fossile ma **sei** (init + due fix + optimize + emergency + setup).

## 3. Codice chiave (stralci con origine)

**Il migratore di motore: due PDO, copia idempotente, verifica conteggi** — `migrate_to_mysql.php:37-72,199-209`:

```php
$sqlite = new PDO("sqlite:" . $sqlitePath);            // sorgente (file)
$mysql  = Database::connect();                          // destinazione (MySQL)
// …
$rows = $sqlite->query("SELECT * FROM news ORDER BY id ASC")->fetchAll();
$stmt = $mysql->prepare("INSERT INTO news (id, slug, …) VALUES (?, …)
                         ON DUPLICATE KEY UPDATE title=VALUES(title), …");   // ri-eseguibile
foreach ($rows as $r) { $stmt->execute([ $r['id'], $r['slug'], … ]); $count++; }
// … e alla fine, la verifica esplicita:
foreach (['news','users','subscribers','speakers','podcasts'] as $t) {
    $c = $mysql->query("SELECT COUNT(*) FROM $t")->fetchColumn();
    echo "  $t: $c record in MySQL\n";
}
```

**La micro-migrazione idempotente (il pattern "ALTER + skip Duplicate")** — `migrate_status.php:6-16`:

```php
$pdo->exec("ALTER TABLE news ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'published'");
// …
} catch (PDOException $e) {
    if ($e->getCode() == '42S21' || strpos($e->getMessage(), 'Duplicate column') !== false) {
        echo "OK: colonna 'status' già presente.\n";    // ri-esecuzione = no-op
    } else { echo "ERRORE: " . $e->getMessage() . "\n"; }
}
```

**La STESSA migrazione, ma self-healing dentro la console admin** — `admin.php:459-469` (`apply_v291_status`):

```php
if ($action === 'apply_v291_status' && $_SERVER['REQUEST_METHOD'] === 'GET') {
    try {
        getDB()->exec("ALTER TABLE news ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'published'");
        sendSuccess(['message' => "OK: colonna 'status' aggiunta…"]);
    } catch (PDOException $e) {
        if (strpos($e->getMessage(), 'Duplicate column') !== false) sendSuccess([…]);
        else sendError('Errore DB: ' . $e->getMessage(), 500);
    }
}
```

**La "ottimizzazione" che ha innescato l'incidente — è codice SQLite** — `optimize_db.php:17-22,34-39`:

```php
// WAL è performante ma spesso causa blocchi su hosting condivisi.
// Impostiamo DELETE per massima stabilità.
$pdo->exec("PRAGMA journal_mode=DELETE;");                       // ← PRAGMA: solo SQLite
// …
$pdo->exec("CREATE INDEX IF NOT EXISTS idx_news_slug ON news(slug)");   // ← sintassi SQLite
$pdo->exec("CREATE INDEX IF NOT EXISTS idx_news_published ON news(published_at DESC)");
```

**Il pulsante rosso d'emergenza (anch'esso SQLite, oggi fossile)** — `emergency_revert_wal.php:19-43`:

```php
// SCRIPT DI EMERGENZA PER DISABILITARE WAL MODE
// Eseguire questo script se il sito va in timeout dopo l'ottimizzazione.
$result = $pdo->query("PRAGMA journal_mode=DELETE");             // rimuove i file .wal/.shm
$mode = $result->fetchColumn();
if (strtoupper($mode) === 'DELETE') echo "SUCCESSO: …ripristinato…";
$pdo->exec("VACUUM;");                                            // ricostruzione DB
// catch: "potresti dover eliminare manualmente i file .wal e .shm via FTP"
```

**Il fossile che interroga lo schema con dialetto SQLite (rotto su MySQL)** — `fix_users_table.php:12,20`:

```php
$stmt = $pdo->query("SELECT name FROM sqlite_master WHERE type='table' AND name='users'");  // SQLite!
// …
$stmt = $pdo->query("PRAGMA table_info(users)");        // PRAGMA: su MySQL → errore di sintassi
$pdo->exec("UPDATE users SET created_at = datetime('now') WHERE created_at IS NULL"); // datetime() = SQLite
```

**La credenziale di default ricreabile dai fossili** — `init_db.php:421` ≡ `fix_users_table.php:57`:

```php
$defaultPass = password_hash('runtime2026', PASSWORD_DEFAULT); // hardcoded, "CHANGE THIS IMMEDIATELY!"
```

## 4. Problemi riscontrati & soluzioni

- **🔥 GOLD — L'incidente WAL: l'ottimizzazione che ha fatto crashare il sito.** È l'incidente
  centrale del sito e il motivo per cui SitoRuntime è il "flagship dei problemi/soluzioni". SQLite, di
  default, può usare la modalità di journaling **WAL** (Write-Ahead Logging), più veloce in scrittura
  ma che crea file collaterali `.wal`/`.shm` e richiede `mmap`/locking che **molti hosting condivisi
  non supportano bene** → lock che non si rilasciano → richieste in **timeout** → sito giù. Il commit
  `fb31c25` (2026-02-23, **02:25 di notte**) lo dice senza giri di parole: *"Risolto crash server …
  switch SQLite WAL->DELETE"*. La **cura** è doppia: (1) `optimize_db.php` che **forza**
  `journal_mode=DELETE` (il journal classico, file-based ma senza i lock del WAL) e (2)
  `emergency_revert_wal.php`, il "pulsante rosso" da eseguire via browser se il sito è già in timeout,
  che fa lo stesso `PRAGMA` + `VACUUM` e, nel `catch`, suggerisce di **cancellare a mano i file
  `.wal`/`.shm` via FTP**. → Box ad altissimo valore: *"Quando l'ottimizzazione è la causa del
  disastro: SQLite, WAL mode e l'hosting condiviso"*.

- **🔥 GOLD — La migrazione a MySQL come reazione all'incidente (la cura definitiva).** La cronologia
  è inequivocabile: crash WAL il **23/02**, migrazione a MySQL il **24/02** (`db.php:3`, commit
  `42e2b95`). Il modo per non avere *mai più* file-lock su hosting condiviso è smettere di usare un DB
  *a file*: MySQL è client/server, il locking lo gestisce il demone. La migrazione non è "scaling"
  pianificato ma **post-mortem**: il sito è scappato da SQLite **dopo** essersi fatto male. → Questo
  riallinea la narrazione di tutto SitoRuntime: il "flagship scalabilità" lo è diventato **per
  necessità**, non per disegno. Box "migrare di motore non è un upgrade, è a volte una fuga".

- **🔥 GOLD — Sei fossili SQLite in un repo MySQL: l'archeologia della migrazione.** Dopo lo switch,
  il vecchio strato non è stato rimosso. Restano:
  | Fossile | Dialetto/meccanismo | Stato oggi su MySQL |
  |---|---|---|
  | `init_db.php` | `INTEGER PRIMARY KEY AUTOINCREMENT`, seed 24 speaker | crea tipi sbagliati / parz. rotto |
  | `fix_users_table.php` | `sqlite_master`, `PRAGMA table_info`, `datetime('now')` | **rotto** (PRAGMA = errore) |
  | `fix_newsletter_table.php` | `sqlite_master`, `PRAGMA`, `AUTOINCREMENT` | **rotto** + schema a 4 col obsoleto |
  | `setup_podcasts.php` | `INTEGER … AUTOINCREMENT` | parz. funziona (CREATE IF NOT EXISTS innocuo) |
  | `optimize_db.php` | `PRAGMA journal_mode`, `CREATE INDEX IF NOT EXISTS` | **rotto** (no IF NOT EXISTS su index MySQL) |
  | `emergency_revert_wal.php` | `PRAGMA journal_mode`, `VACUUM` | **inerte** (PRAGMA ignorato/errore; WAL non esiste su MySQL) |
  Mitigazione unica: il deny by-prefix di `.htaccess:32-35` (`^(debug_|test_|emergency_|migrate_|fix_|init_|rebuild_|setup_|optimize_)`) impedisce di **eseguirli via HTTP**. Ma sono ancora **sul server** e ancora **nel repo**: rumore, confusione su quale sia la verità dello schema, e — se domani il deny saltasse — endpoint potenti raggiungibili. → Box "cosa lascia indietro una migrazione di motore: l'igiene del repo".

- **🔥 GOLD — La tabella che nessuno crea due volte uguale (i 3 schemi `subscribers`).** Consolidamento
  del ponte lasciato da SR-C9. La tabella `subscribers` ha **tre definizioni divergenti** nel codice:
  1. `init_mysql.php:49-55` — schema **base** MySQL, 4 colonne (`id, email, created_at, is_active`),
     pre-double-opt-in.
  2. `fix_newsletter_table.php` — fossile **SQLite** (`sqlite_master`/`PRAGMA`/`AUTOINCREMENT`) che
     ricrea le **stesse 4 colonne** minime: rotto su MySQL e comunque insufficiente.
  3. `apply_v293_newsletter` (`admin.php:378-391`) — la **vera** migrazione che aggiunge le 4 colonne
     del double opt-in (`confirmation_token`, `confirmed_at`, `subscribed_at`, `subscribed_ip`) e
     **conferma retroattivamente** gli iscritti storici con `HEX(RANDOM_BYTES(32))`.
  Solo l'ultima è allineata al runtime: `newsletter.php` **presuppone** lo schema esteso, quindi su un
  DB con solo lo schema base ogni query fallisce finché `apply_v293` non gira (dipendenza d'ordine non
  dichiarata). È il caso-studio perfetto di "schema sparso in tre verità". → Box "una tabella, tre
  CREATE diversi: la fonte di verità dello schema".

- **GOLD — L'incidente fuso orario / formato data (separatore `T`).** Già emerso in SR-C1/C4, qui
  consolidato come incidente. La regola di visibilità confronta `published_at <= now` **come stringhe**.
  Se il fuso del server e il formato non combaciano, gli articoli **spariscono**. La prova è
  `debug_time.php`: forza `Europe/Rome`, formatta "adesso" con `date('Y-m-d\TH:i:s')` e il commento
  *"FIX: Use T separator to match DB"* (`:23-24`), poi stampa `VISIBLE`/`HIDDEN` con la comparazione
  letterale. **Twist:** il runtime reale (`news.php`) NON usa il separatore `T` ma lo **spazio**
  (`date('Y-m-d H:i:s')`), che è il formato corretto del DATETIME MySQL (SR-C4). Quindi `debug_time.php`
  documenta un bug del passato e una "fix" (il `T`) che nel codice di produzione **non** è stata
  applicata — la versione `T` è rimasta solo nel file di diagnostica. → Box "confronti di date come
  stringhe: il bug che fa sparire i contenuti".

- **Doppio binario di delivery delle migrazioni = ambiguità.** La stessa migrazione `status` esiste sia
  in `migrate_status.php` (da cancellare) sia in `apply_v291_status` (in `admin.php`, persistente). Non
  c'è un registro di cosa è stato applicato: ri-eseguire è innocuo (idempotenza) ma **sapere lo stato**
  reale dello schema richiede di interrogare il DB, non il codice. Debito di osservabilità dello schema.

- **Migrazioni/manutenzione gated `isLoggedIn` ma NON `isAdmin` né CSRF** (ponte da SR-C12). Le azioni
  `apply_v291_status`, `apply_v293_newsletter`, `fix_image_paths` sono **GET** dietro il solo
  `isLoggedIn()`: un *editor* (non admin) potrebbe innescarle, e — essendo GET senza `validateCsrf` —
  sono teoricamente CSRF-able verso un admin loggato. Mitigate dal fatto che sono operazioni
  idempotenti/poco distruttive, ma è una falla di gate coerente con quella già notata in SR-C12.

- **L'ASSENZA di backup/cron — incidente latente (cura senza prevenzione)** (consolida SR-C12). Il sito
  che ha l'`emergency_revert_wal.php` (la **cura**) non ha **nessun** sistema di backup automatico né
  cron (grep negativo su `backup`/`cron`/`mysqldump`, init_mysql non crea nulla del genere). L'unica
  "rete" è `_BACKUP_BEFORE_OPTIMIZATION/` (vedi sotto): una **copia manuale una tantum** committata nel
  repo prima dell'intervento rischioso — non un sistema, un gesto. Il flagship degli incidenti sa
  curare il disastro ma non lo previene: se MySQL si corrompe, non c'è dump da cui ripartire. → Box "la
  cura senza la prevenzione".

- **Archeologia: `_BACKUP_BEFORE_OPTIMIZATION/` e `_ARCHIVIO/pw_reset.php`.** (1) La cartella
  `_BACKUP_BEFORE_OPTIMIZATION/` è uno **snapshot dell'intero progetto** (con `index.tsx`,
  `constants.ts`, una sotto-cartella `runtimeradio-backup/api/` con *tutti* gli endpoint, e un
  `mysql.txt`) preso **prima** dell'ottimizzazione che ha causato il crash: la prova materiale che
  qualcuno ha "fatto la foto" prima di toccare il motore — backup manuale, non automatico, e per
  giunta **versionato nel repo** (rumore + rischio di servire file vecchi). (2) `_ARCHIVIO/pw_reset.php`
  è un fossile di **reset password** — SR-C2 aveva annotato "niente recovery/reset": eccolo, archiviato
  fuori da `public/`, mai cablato. → Note di archeologia per il box "igiene del repo".

## 5. Estetica / UX (moderna ma funzionale)

Cluster infrastrutturale: nessuna UI di prodotto. La "UX" è quella degli **strumenti di manutenzione**:

- **Output da terminale curato e narrato.** `init_mysql.php`/`migrate_to_mysql.php` stampano un log
  passo-passo numerato ("1. Creazione tabella 'news'… OK", riepilogo + verifica conteggi);
  `optimize_db.php` ed `emergency_revert_wal.php` parlano in italiano con toni rassicuranti
  ("Impostato su DELETE (Sicuro)", "Il timeout dovrebbe essere risolto"). È la stessa cura "estetica nel
  backstage" di SR-C1: anche gli script usa-e-getta sono **leggibili e guidati**, pensati per un umano
  ansioso che li lancia da browser durante un incidente.
- **Tono d'emergenza.** `emergency_revert_wal.php` è scritto come un **kit di pronto soccorso**: spiega
  cos'è il WAL, perché si rompe, cosa fare se anche lo script fallisce (FTP manuale). Buona pratica di
  *runbook embedded* — la documentazione dell'incidente vive **nel** codice che lo risolve.
- **Console di manutenzione invece di tool.** Le migrazioni self-healing in `admin.php` rispondono in
  JSON (`{results: […]}`) pensato per essere innescato dalla UI admin: l'evoluzione DB è (in parte)
  diventata un **bottone nel pannello**, non più un file FTP-ato. È l'estetica "moderna ma funzionale"
  applicata alla manutenzione.

## 6. Differenze rispetto agli altri siti

Qui il confronto è **soprattutto interno/storico** — *SitoRuntime oggi vs SitoRuntime nelle sue
migrazioni passate* — perché **SPW non ha una card C13**: in SimonePizziWebSite gli incidenti erano
**sparsi** nelle singole card (l'`init_db.php` fossile in C1, le migration cancellate di C2, il batch
WebP di C5, l'invio sincrono di C9), senza un capitolo dedicato. SR invece li **concentra**.

**SitoRuntime nel tempo (confronto interno):**

| Asse | SR ieri (era SQLite) | SR oggi (era MySQL) |
|---|---|---|
| **Motore** | SQLite (DB a file) | MySQL (client/server) |
| **Journaling** | WAL → **crash** → DELETE forzato | gestito dal demone (problema sparito) |
| **Evoluzione schema** | `ALTER … ADD COLUMN` in `try/catch` dentro `init_db.php` ("HOTFIXES") | `migrate_*` one-shot **+** `apply_v29x` self-healing in `admin.php` |
| **Strumenti di crisi** | `optimize_db.php`, `emergency_revert_wal.php` (vivi) | gli stessi, ma **fossili inerti** |
| **Verità dello schema** | `init_db.php` (SQLite) | `init_mysql.php` + N micro-migrazioni (sparsa) |
| **Backup** | snapshot manuale `_BACKUP_BEFORE_OPTIMIZATION/` | **nessun** sistema |

**SR vs SPW (su come trattano gli incidenti):**

| Aspetto | SimonePizziWebSite | SitoRuntime |
|---|---|---|
| **Dove vivono gli incidenti** | sparsi nelle card funzionali (nessun C13) | **concentrati** in un capitolo (questo) |
| **Migrazione di motore** | SQLite→MySQL fatta *dentro* il migratore, init fossile lasciato | SQLite→MySQL come **reazione a un crash**, **sei** fossili lasciati |
| **Incidente "famoso"** | nessun crash documentato in commit | **crash server WAL** documentato in `fb31c25` (02:25 di notte) |
| **Backup** | **sì**, automatico fuori-docroot + rotazione (SPW-C12) | **no** (solo snapshot manuale una tantum) |
| **Self-healing migrations** | script deploy-and-delete | **doppio binario** (one-shot **e** in `admin.php`) |
| **Reset password** | recovery/reset implementati (SPW-C2) | solo fossile `_ARCHIVIO/pw_reset.php`, mai cablato |

Sintesi: SPW è il sito che gli incidenti li **previene e li disperde** (backup, reset, sanitizzazione
diffusa); SR è il sito che gli incidenti li **subisce e li raduna** — ha la storia più drammatica (un
crash vero, una migrazione di fuga) ma la prevenzione più debole (niente backup). È esattamente il
ruolo che la ROADMAP assegna a SitoRuntime: *flagship scalabilità + problemi/soluzioni*.

Per **DISINTELLIGENZA/FDCA** (festival, ancora **SQLite**) la C13 sarà speculare: lì il WAL e i
`PRAGMA` sono *vivi*, non fossili — termine di paragone "il motore che SR si è lasciato alle spalle".

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **L'incidente WAL** (SQLite + hosting condiviso + journal mode) e i due script di cura | **Cap. NUOVO "Quando l'ottimizzazione è il disastro"** (alto valore, apre la Parte "Problemi & Soluzioni") |
| **Migrare di motore come reazione a un crash** (SQLite→MySQL il giorno dopo) | Cap. "Migrazioni di motore DB" (il *perché* reale, non solo il *come*) |
| **Il migratore a mano con verifica conteggi** (`migrate_to_mysql.php`) | Box "ETL thin stack: due PDO e un COUNT" |
| **Il pattern `ALTER + skip Duplicate`** (idempotenza senza tool di migrazione) | Box "micro-migrazioni che si auto-riparano" |
| **Doppio binario one-shot vs self-healing in admin.php** | Box "dove far vivere una migrazione: file da cancellare o console persistente" |
| **I sei fossili SQLite in un repo MySQL** (tabella archeologica) | Box "igiene del repo dopo una migrazione di motore" |
| **Tre schemi `subscribers`** (init/fix-fossile/apply_v293) | Cap. "Una tabella, tre CREATE diversi: la fonte di verità dello schema" (consolida SR-C9) |
| **Confronto di date come stringhe** (`debug_time.php`, separatore `T`, fix mai applicata in prod) | Box "il bug del fuso che fa sparire i contenuti" (consolida SR-C1/C4) |
| **La cura senza la prevenzione** (emergency revert ma niente backup) | Box "avere il defibrillatore ma non il check-up" (consolida SR-C12) |
| **Il backup manuale committato nel repo** (`_BACKUP_BEFORE_OPTIMIZATION/`) | (stesso box igiene repo) "lo snapshot pre-intervento" |

## 8. Note / domande aperte

- **Ponti `→C13` lasciati dalle altre card: CHIUSI qui.**
  - SR-C1 §8: `migrate_to_mysql`, `migrate_status`, `fix_*`, `emergency_revert_wal`, `optimize_db`,
    schema frammentato, init fossile → **consolidati in §1/§4**. (`rebuild_seo_cache`→resta C7;
    `optimize_db` qui per l'incidente WAL, non per gli indici → l'aspetto "indici" lo eredita C13).
  - SR-C5: storia migratoria raster→WebP (`optimize_webp`/`fix_image_paths`) → `fix_image_paths`
    ispezionato (`admin.php:472-523`): allinea `cover_image`/`image` ai file `.webp` su disco + invalida
    cache. È una **migrazione di dati** (non di schema): legittima qui come "evoluzione del parco
    media". La conversione WebP in sé resta meccanica di C5.
  - SR-C9: i **3 schemi `subscribers`** → consolidati come GOLD in §4.
  - SR-C12: l'**assenza di backup/cron** + migrazioni gated `isLoggedIn` non `isAdmin` → consolidati in §4.
- **Puntatori ad altri cluster** (NON mappati qui):
  - DB-bootstrap/singleton/`db.php`/`db_credentials.php` = **C1** (qui solo l'*evoluzione*, non il
    singleton in sé).
  - Gate `isLoggedIn`/`isAdmin`/CSRF/`.cache` = **C2**; password default `runtime2026` = C2 (qui solo
    come "ricreabile dai fossili").
  - `rebuild_seo_cache.php` + seo-cache morta = **C7**; conversione WebP/upload = **C5**; UI admin delle
    azioni di manutenzione = **C12**.
- **Da verificare (debito segnalato, non risolvibile da read-only):** non esiste un percorso "pulito"
  per ricreare lo schema MySQL da zero (risposta alla domanda aperta di SR-C1 §8): oggi servirebbe
  `init_mysql.php` **+** la catena `migrate_status`/`apply_v291`/`apply_v293` in ordine. Nessun file
  unico rappresenta lo schema corrente completo. → debito di "schema as code" da raccontare nel libro.
- **Cronologia di riferimento (da `git`):** `677e07c` init SQLite → `fb31c25` (2026-02-23 02:25) crash
  WAL + switch DELETE → `42e2b95` migrazione MySQL (24/02/2026, `db.php:3`). Versione del sito alla
  mappatura: **2.9.13**.
- **Credenziali/segreti:** non letti né riportati valori reali (solo nomi/strutture).
- **Con questa card SitoRuntime è COMPLETO** (10 card: C1, C2, C3, C4, C5, C7, C8, C9, C12, C13).
  Prossimo sito: **DISINTELLIGENZA** (festival, SQLite — dove WAL/PRAGMA sono *vivi*).
