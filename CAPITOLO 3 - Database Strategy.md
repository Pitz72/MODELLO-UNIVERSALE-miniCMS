# CAPITOLO 3: Database Strategy (Terza Edizione)

Il database è il cuore del miniCMS. Questo capitolo definisce le strategie di connessione, integrità e migrazione, distinguendo con cura due cose che è facile confondere: ciò che il Modello **raccomanda** e ciò che i siti reali **fanno davvero**. Non sempre coincidono, e dirlo apertamente è più utile che spacciare una prescrizione per una fotografia.

## 1. Architettura di Connessione (PDO, un motore alla volta)

Il sistema usa PDO con un singleton memoizzato (la connessione si apre una sola volta per richiesta, Capitolo 5). Il motore sotto, però, non è astratto: SQLite e MySQL aprono la connessione con opzioni diverse, e i tre siti le scelgono su tre livelli.

### 1.1 Le opzioni di connessione: la fotografia

Prima della prescrizione, cosa accade nel codice reale. I tre siti impostano set di opzioni PDO di crescente paranoia, e questo è un buon esempio della scala a tre gradini del Capitolo 1.

| Sito | Motore | Opzioni PDO reali |
|---|---|---|
| **DISINTELLIGENZA** | SQLite (vivo) | **solo** `ERRMODE=EXCEPTION` + `DEFAULT_FETCH_MODE=ASSOC`, via `setAttribute()`. Nessun `PRAGMA` nel `connect()`. |
| **SimonePizziWebSite** | MySQL | `ERRMODE` + `FETCH` + `EMULATE_PREPARES=false` (prepared statement veri) |
| **SitoRuntime** | MySQL | `ERRMODE` + `FETCH` + `ATTR_TIMEOUT=5` + `MYSQL_ATTR_INIT_COMMAND` (`SET NAMES`) |

Il dato che sorprende è la prima riga: l'unico sito che oggi gira **davvero** su SQLite (DISINTELLIGENZA) non imposta nessuno dei `PRAGMA` «ottimali» che la maggior parte dei manuali dà per scontati. Apre il file e basta, con due sole opzioni. È una scelta minimale che funziona per il suo carico, ma non è la configurazione più robusta possibile, ed è il motivo per cui la prescrizione che segue va presa per quello che è: un consiglio, non una descrizione del codice esistente.

### 1.2 Le opzioni di connessione: la prescrizione

Per un deploy SQLite su hosting condiviso, il Modello raccomanda tre `PRAGMA` in aggiunta alle opzioni base:

```php
// RACCOMANDATO per SQLite su hosting condiviso (non è ciò che DIS imposta oggi)
self::$pdo = new PDO("sqlite:" . $dbPath);
self::$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
self::$pdo->exec("PRAGMA journal_mode = DELETE;");   // più stabile di WAL su hosting condiviso
self::$pdo->exec("PRAGMA busy_timeout = 5000;");     // attende invece di fallire sotto scrittura concorrente
self::$pdo->exec("PRAGMA foreign_keys = ON;");       // integrità referenziale (off di default in SQLite)
```

Il `busy_timeout` a 5000ms fa aspettare una scrittura concorrente invece di farla fallire subito (utile quando newsletter e admin scrivono insieme). Il `foreign_keys = ON` serve perché SQLite, a differenza di MySQL, lascia le chiavi esterne disattivate per default. Ma la riga che porta una cicatrice è la prima.

> [!WARNING]
> **Perché `DELETE` e non `WAL`: la lezione arriva da un incidente**
> SitoRuntime, quando ancora girava su SQLite, ha provato a usare `journal_mode = WAL` in produzione per migliorare le prestazioni sotto carico. Su hosting condiviso Apache il WAL ha fatto danni: il file di lock `.sqlite-wal` restava appeso e corrompeva le letture. È servito uno script d'emergenza (`emergency_revert_wal.php`) per tornare a `DELETE`, e poco dopo quel disastro ha spinto la migrazione a MySQL (la storia completa è al Capitolo 15). La lezione, valida per chi resta su SQLite: su hosting condiviso scegli `DELETE`, non `WAL`. È una raccomandazione nata da un guasto vero, non una preferenza di stile.

### 1.3 Nascondere il database-a-file (solo SQLite)

Chi usa SQLite ha un problema che chi usa MySQL non ha: il database è un file dentro le cartelle del sito, e un file raggiungibile via web è il database intero scaricabile da chiunque. La difesa, in **DISINTELLIGENZA**, è generata a runtime dal codice di connessione: alla prima `connect()`, se la cartella `.data/` non esiste, viene creata e ci si scrive dentro un `.htaccess` di `Deny from all`.

```php
// DISINTELLIGENZA db.php — la protezione del DB-a-file è creata dall'app, non pre-deployata
$dir = dirname($dbPath);                                  // .../.data
if (!is_dir($dir)) mkdir($dir, 0755, true);
$htaccessPath = $dir . '/.htaccess';
if (!file_exists($htaccessPath)) {
    file_put_contents($htaccessPath, "Require all denied\n");   // seconda rete: <Files> nel .htaccess globale
}
```

Questo pattern appartiene ai siti SQLite, non a quelli su MySQL. SimonePizziWebSite e SitoRuntime sono migrati a MySQL: non hanno alcuna cartella `.data/` con il database dentro, perché i loro dati vivono sul server MySQL, fuori dalla docroot per natura. Generare la protezione a runtime, anziché affidarla a un file committato, ha una ragione concreta che ritorna al Capitolo 14: lo script di build può rimuovere la cartella `.data/` dalla distribuzione, e con essa l'`.htaccess` di deny, che quindi non arriverebbe mai sul server.

---

## 2. Indicizzazione Strategica

Le query di lettura devono essere istantanee. Il Modello prevede questi indici:

| Tabella | Colonna | Tipo | Scopo |
| :--- | :--- | :--- | :--- |
| `news` / `articles` | `slug` | UNIQUE | Ricerca articolo via URL (SEO) |
| `news` / `articles` | `published_at` | DESC | Ordinamento cronologico veloce |
| `news` / `articles` | `status` | INDEX | Filtraggio bozza/pubblicato |
| `speakers` | `sort_order` | ASC | Ordinamento manuale trascinabile |
| `podcasts` | `slug` | UNIQUE | Accesso rapido alle serie |
| `projects` | `category` | INDEX | Filtraggio per categoria portfolio |
| `projects` | `sort_order` | ASC | Ordinamento manuale portfolio |

Dopo caricamenti massivi è utile eseguire `ANALYZE;` per ricalcolare le statistiche di accesso e ottimizzare il piano delle query.

---

## 3. Ciclo di Vita delle Migrazioni

Le modifiche allo schema devono essere atomiche, idempotenti e protette. Sono i requisiti; i siti reali li rispettano in modo diseguale, e la differenza conta.

- **Atomicità**: ogni migrazione usa una transazione (`beginTransaction`).
- **Idempotenza**: lo script verifica l'esistenza di colonne o tabelle prima di crearle (`IF NOT EXISTS`, `PRAGMA table_info`), così rieseguirlo non rompe niente.
- **Protezione**: gli script di migrazione **dovrebbero** essere irraggiungibili da web non autenticato. Qui la realtà diverge: SitoRuntime li nega per prefisso nel `.htaccess` o li tiene dentro `admin.php` (gated), mentre DISINTELLIGENZA lascia i suoi `update_db_*.php` e `migrate_media.php` raggiungibili in HTTP senza gate. È un debito di sicurezza reale (Capitolo 15), non un dettaglio.
- **Nomenclatura**: nessun sito ha una tabella `schema_version`. La versione vive nei **nomi dei file** (`update_db_v0.4.2.php`, `update_db_v0.5.4.php`), allineati alla versione in `package.json`. La storia delle migrazioni si legge dalla cartella, non da un registro nel database.

---

## 4. Normalizzazione dei Dati

Per evitare incoerenze tra PHP, JS e il database, il Modello normalizza prima del salvataggio:
- **Date**: formato `Y-m-d H:i:s` per compatibilità SQL e JS. Attenzione al fuso: il confronto di visibilità `published_at <= NOW` è fatto su stringhe, e una data scritta con il separatore sbagliato sposta la soglia (Capitolo 5 e Capitolo 9).
- **Numerici**: interi o arrotondati a zero decimali, per evitare i bug di virgola mobile.
- **Booleani**: `INTEGER` (0 o 1) in SQLite, `TINYINT(1)` in MySQL.

---

## 5. Manutenzione e Integrità

- **VACUUM**: da eseguire dopo cancellazioni massive per ricompattare il file e ridurne il peso (rilevante su SQLite).
- **Backup**: ogni migrazione **dovrebbe** essere preceduta da una copia del database in una cartella protetta. Anche qui la realtà non è uniforme: SimonePizziWebSite ha un backup automatico fuori docroot, DISINTELLIGENZA fa una copia `.bak` prima delle azioni distruttive, SitoRuntime (il sito che ha sofferto il crash) non ha alcun backup automatico. Il paradosso «cura senza prevenzione» è al Capitolo 14.
- **`optimize_db.php`**: SitoRuntime include uno script di manutenzione (`VACUUM`, `ANALYZE`, verifica integrità); nonostante l'intestazione «usa e getta» è in realtà non distruttivo (aggiunge solo indici idempotenti).

---

## 6. Quando Passare a MySQL

La storia completa, con gli script reali, è al Capitolo 15. Un punto va chiarito subito, perché è una mezza verità diffusa: la migrazione di SitoRuntime **non** è stata decisa da una soglia di traffico raggiunta con calma. È stata la reazione a un incidente (il crash del WAL della notte) che ha reso SQLite improvvisamente inaffidabile su quell'hosting. La soglia non era un numero su un grafico, era un database corrotto alle tre di notte.

Il contrappunto è altrettanto istruttivo: DISINTELLIGENZA, un festival con votazioni pubbliche, gira **ancora oggi su SQLite** in produzione, senza problemi. SQLite non è un gradino da abbandonare appena possibile: è la scelta giusta finché regge, e «finché regge» dipende dal carico e dall'hosting, non da una regola universale. Si passa a MySQL quando un vincolo concreto lo impone, non per scaramanzia.

### 6.1 I numeri, con onestà

«Finché regge» non è una risposta che si può lasciare al sentimento. Servono ordini di grandezza, con l'avvertenza che restano tali: dipendono dall'hardware, dal disco dell'hosting condiviso e dalla forma delle query, e vanno misurati sul proprio caso, non presi come garanzie.

Il punto chiave è che in SQLite **lettura e scrittura non scalano allo stesso modo**. Le letture sono concorrenti e velocissime: un sito a prevalenza di lettura (un blog, un portfolio, una radio con news e podcast) regge senza fatica migliaia di letture al secondo dalla cache di pagina e centinaia di query di lettura al secondo dirette al file, perché più richieste possono leggere lo stesso database insieme. Le scritture, invece, sono **serializzate**: SQLite ammette un solo scrittore alla volta e blocca l'intero file durante la scrittura. È lì che si trova il soffitto.

In pratica, su un tipico hosting condiviso:

| Segnale | SQLite è a suo agio | Conviene valutare MySQL |
| :--- | :--- | :--- |
| **Scritture concorrenti** | fino a qualche decina al minuto, sporadiche | decine al secondo sostenute, o picchi concorrenti regolari |
| **Profilo di carico** | lettura dominante (90%+), scritture isolate | scrittura frequente e simultanea (form, voti, code) |
| **Concorrenza in scrittura** | un processo per volta basta | più processi scrivono insieme (newsletter + admin + pubblico) |
| **Topologia** | un solo server applicativo | serve scalare su più nodi che condividono i dati |
| **Sintomo nei log** | nessun `database is locked` | `busy timeout` o `database is locked` ricorrenti |

La soglia vera non è un numero ma un **sintomo**: quando nei log compaiono errori di lock o di `busy timeout` nonostante il `busy_timeout` configurato, il database ti sta dicendo che la contesa in scrittura ha superato quello che un file-database regge su quell'hosting. È il momento di MySQL, e non un istante prima. Runtime Radio ci è arrivato per un incidente (Capitolo 15); la maggior parte dei siti non ci arriva mai, ed è giusto così.

> [!IMPORTANT]
> **Il Canone**
> - SQLite con `journal_mode=DELETE` (mai WAL su hosting condiviso), `busy_timeout`, `foreign_keys=ON`; PDO in `ERRMODE_EXCEPTION`.
> - Indicizza `slug` (UNIQUE), `published_at` (DESC), `status`; `ANALYZE` dopo i caricamenti massivi.
> - Migrazioni atomiche, idempotenti e irraggiungibili da web non autenticato; tieni una tabella `schema_version` (i siti reali non ce l'hanno: è un debito da non ereditare).
> - Backup prima di ogni migrazione, in una cartella protetta fuori docroot.
> - Passa a MySQL quando i log mostrano `database is locked`/`busy timeout` ricorrenti, non per scaramanzia.

---
*Prossimo Capitolo: Frontend Dependencies. La matrice delle dipendenze, le regole di scelta e il costo di ogni libreria.*
