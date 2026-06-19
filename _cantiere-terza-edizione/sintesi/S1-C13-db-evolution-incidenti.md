# Scheda di Sintesi — S1-C13 — DB Evolution & Incidenti

> **Stato:** COMPLETATO
> **Cluster FASE 2:** S1-C13 · **Data:** 2026-06-19 · **Commit:** _(in corso)_
> **Fonti (card di mappatura, in particolare i §6):** SR-C13 (principale, il sito con la cicatrice), DIS-C1 (SQLite VIVO: il motore che SR si è lasciato alle spalle), SPW-C1/C12 (migrato in silenzio, ma con backup) · consolida i ponti →C13 da SR-C1/C5/C9/C12
> **Capitoli del libro toccati:** CAP 14 (Database Evolution — Da SQLite a MySQL) — principale · ponti a CAP 3 (Database Strategy → S1-C1), CAP 10 (script di manutenzione gated → S1-C2), CAP 13 (i 3 schemi `subscribers` → S1-C9), CAP 18/admin (backup → S1-C12) → vedi §4

---

## 0. In una frase
L'evoluzione dello schema nel miniCMS avviene **senza alcuno strumento di migrazione** — niente
`migrations/`, niente `schema_version`, solo `ALTER … ADD COLUMN` idempotenti — e i tre siti mostrano
**tre rapporti diversi con la stessa tecnica**: DIS la usa ancora su **SQLite vivo** (il motore che gli
altri hanno abbandonato), SPW e SR hanno **migrato a MySQL** ma con un abisso di differenza nel *perché*
e nel *dopo* — SR ci è arrivato in **fuga da un crash notturno** (l'incidente WAL) lasciandosi dietro
**sei fossili** e **nessun backup**, SPW in silenzio e con una rete di salvataggio. La lezione del
capitolo non è "come si migra" ma **cosa una migrazione lascia indietro** e perché *il flagship degli
incidenti è quello meno attrezzato a sopravvivere al prossimo*.

## 1. Il pattern comune — la filosofia "thin stack" su questa lente

I tre siti condividono **quattro modi** di far evolvere uno schema senza strumenti.

**1) `ALTER TABLE … ADD COLUMN` in `try/catch`, idempotente.** È l'unico strumento di evoluzione: si
aggiunge la colonna e, se l'errore dice "Duplicate column" (MySQL) o la colonna esiste già (controllo
`PRAGMA`/`table_info` in SQLite), lo si tratta come **successo**. Risultato: la stessa migrazione si può
rieseguire N volte senza danni — "lo schema che si auto-ripara". Presente identico nei tre siti.

**2) Nessun registro delle migrazioni.** Non esiste una tabella `schema_version` né un elenco di "cosa è
già stato applicato". La versione dello schema è **implicita**: nei **nomi dei file** (DIS:
`update_db_0_1_3` → `0_1_4` → `v0.5.4`; SR: `apply_v291`/`apply_v293`), o leggibile solo da **git** (SR).
La fonte di verità dello schema corrente è **dispersa**: nessun file singolo la rappresenta.

**3) Lo scaffolding "vivo" è separato dall'init "fossile".** Come consolidato in **S1-C1**, l'`init_db.php`
che dovrebbe creare lo schema da zero è disallineato dalla realtà in tutti e tre i siti — la verità si è
spostata in un migratore, in un file dedicato o nel `.sqlite`. Qui (C13) interessa la *conseguenza
temporale*: ogni evoluzione aumenta la distanza tra l'init e il vivo.

**4) Lo strumento di manutenzione è un endpoint, non un tool.** Le migrazioni e le riparazioni sono
**file PHP** (`migrate_*`, `fix_*`, `update_db_*`) lanciati da browser o azioni `?action=` nella console
admin — nessun CLI, nessun runner. Output "da terminale" narrato in italiano, pensato per un umano che li
esegue a mano (a volte durante un incidente).

Su questa base condivisa, la *storia* dei tre siti diverge radicalmente: chi è rimasto su SQLite, chi ha
migrato in silenzio, chi è migrato in fuga.

## 2. Le varianti per sito (tabella unica, deduplicata)

| Asse | SitoRuntime | DISINTELLIGENZA | SimonePizziWebSite | *(FDCA)* |
|---|---|---|---|---|
| **Motore oggi** | **MySQL** (migrato 24/02/2026) | **SQLite VIVO** (mai migrato) | MySQL (migrato v1.7.0) | = DIS (SQLite vivo) |
| **Perché ha migrato** | **fuga da un crash** (incidente WAL il giorno prima) | — (non ha migrato) | scaling silenzioso (nessun incidente documentato) | — |
| **Incidente "famoso"** | **crash server WAL** (commit `fb31c25`, 23/02 **02:25 di notte**) | nessuno (SQLite gli basta) | nessuno | — |
| **WAL / `PRAGMA journal_mode`** | **fossile** (codice SQLite inerte su MySQL) | **vivo e rilevante** (DB-a-file su hosting condiviso) | n/a (MySQL) | = DIS |
| **Evoluzione schema** | `migrate_*` one-shot **+** `apply_v29x` self-healing in `admin.php` (doppio binario) | catena `update_db_*` (8 file, idempotenti) | dentro il migratore + poche micro-migrazioni | = DIS |
| **Migratore di motore** | `migrate_to_mysql.php` (2 PDO + `ON DUPLICATE KEY` + COUNT di verifica) | — | dentro `migrate_to_mysql.php` (init fossile lasciato) | — |
| **Fossili lasciati** | **SEI** (init + 2 fix + optimize + emergency + setup), SQLite-flavor su MySQL | n/a (il "fossile" è ancora vivo) | pochi (init_db SQLite) | = DIS |
| **Schema `subscribers`** | **3 verità divergenti** (init base / fix_ fossile SQLite / apply_v293 self-healing) | minimale (un `update_db_*`) | completo (un migrate one-shot) | = DIS |
| **Backup / prevenzione** | **NESSUN sistema** (solo snapshot manuale `_BACKUP_BEFORE_OPTIMIZATION/` committato nel repo) | backup `.bak` **pre-distruttivo** prima dei reset (S1-C2) | **backup auto** fuori-docroot + rotazione (S1-C12) | = DIS |
| **Cura degli incidenti** | `emergency_revert_wal.php` (il "pulsante rosso") | — | n/a | = DIS |
| **Bug data/fuso** | `debug_time.php` (separatore `T`, fix mai applicata in prod) | `CURRENT_TIMESTAMP` UTC vs fuso server (S1-C4) | `Europe/Rome` forzato ovunque | = DIS |

**Lettura della tabella.** L'asse portante è il **rapporto con la migrazione di motore**. **DIS** è il
termine di paragone "prima": SQLite **vivo**, dove WAL e `PRAGMA` non sono fossili ma preoccupazioni
reali — eppure il sito **non è mai crashato**, perché evolve piano e fa backup `.bak` prima del
distruttivo. **SR** è la cicatrice: ha migrato a MySQL **il giorno dopo** un crash da WAL su hosting
condiviso (il commit di riparazione è delle **2:25 di notte**), e si è lasciato dietro sei fossili SQLite
e — paradosso — **nessun backup**. **SPW** ha fatto la stessa migrazione **in silenzio** (nessun
incidente in git) e ha la prevenzione più solida (backup automatico fuori-docroot, S1-C12). Il
ribaltamento cross-edizione (gemello di S1-C2/C5/C9/C12): **il sito che ha sofferto di più — SR — è
quello senza rete di salvataggio**; ha imparato a *curare* il disastro (`emergency_revert_wal`) ma non a
*prevenirlo*. E la migrazione di SR smentisce la narrazione "si migra per scaling": SR ha migrato **per
necessità**, in fuga — il "flagship scalabilità" lo è diventato per incidente, non per disegno.

**FDCA è fuori scala:** fork col backend byte-identico a DIS → eredita lo stesso SQLite vivo e la stessa
catena `update_db_*`, immutati. Caso fork.

## 3. GOLD & box problemi-soluzioni

- **L'incidente WAL: quando l'ottimizzazione è il disastro** — *(SR; DIS come contrappunto vivo)* — il
  GOLD portante. SQLite può usare il journaling **WAL** (Write-Ahead Logging), più veloce in scrittura ma
  che crea file collaterali `.wal`/`.shm` e richiede locking che **molti hosting condivisi non gestiscono
  bene** → lock che non si rilasciano → richieste in **timeout** → sito giù. Il commit `fb31c25`
  (2026-02-23, **02:25**) lo dice senza giri: *"Risolto crash server … switch SQLite WAL→DELETE"*. La
  cura è doppia e vive **dentro il codice che la spiega**: `optimize_db.php` (forza
  `journal_mode=DELETE`) e `emergency_revert_wal.php`, il "pulsante rosso" da browser che fa lo stesso
  `PRAGMA` + `VACUUM` e nel `catch` suggerisce di **cancellare i file `.wal`/`.shm` via FTP**. Il
  contrappunto: **DIS gira ancora su SQLite** senza crashare — la differenza non è il motore ma *toccare
  il journal mode su hosting condiviso*. → Box "Quando l'ottimizzazione è la causa del disastro: SQLite,
  WAL e l'hosting condiviso" (altissimo valore, apre la Parte "Problemi & Soluzioni").

- **Migrare di motore non è un upgrade: a volte è una fuga** — *(SR)* — la cronologia è inequivocabile:
  crash WAL il **23/02**, migrazione a MySQL il **24/02** (`db.php:3`, commit `42e2b95`). Il modo per non
  avere *mai più* file-lock su hosting condiviso è smettere di usare un DB *a file*. La migrazione non è
  scaling pianificato ma **post-mortem**. Questo riallinea la narrazione di tutto SitoRuntime e **corregge
  il CAP 14**, che la presenta tra le "soglie di traffico" (vedi §4): il *perché reale* è un incidente,
  non un grafico di crescita. → Box "Migrare di motore come reazione, non come piano".

- **Cosa lascia indietro una migrazione di motore: i sei fossili** — *(SR)* — dopo lo switch, lo strato
  SQLite non è stato rimosso. Restano **sei** file SQLite-flavor in un repo MySQL:

  | Fossile | Meccanismo SQLite | Stato su MySQL |
  |---|---|---|
  | `init_db.php` | `AUTOINCREMENT`, seed 24 speaker | crea tipi sbagliati / parz. rotto |
  | `fix_users_table.php` | `sqlite_master`, `PRAGMA`, `datetime('now')` | **rotto** |
  | `fix_newsletter_table.php` | `sqlite_master`, `PRAGMA`, schema a 4 col | **rotto** + obsoleto |
  | `setup_podcasts.php` | `AUTOINCREMENT` | parz. innocuo |
  | `optimize_db.php` | `PRAGMA journal_mode`, `CREATE INDEX IF NOT EXISTS` | **rotto** |
  | `emergency_revert_wal.php` | `PRAGMA`, `VACUUM` | **inerte** (WAL non esiste su MySQL) |

  Mitigazione unica: il **deny by-prefix** di `.htaccess` (`^(debug_|test_|emergency_|migrate_|fix_|init_|rebuild_|setup_|optimize_)`) impedisce di eseguirli via HTTP. Ma sono ancora **sul server** e **nel
  repo**: rumore, confusione su quale sia la verità dello schema, e — se il deny saltasse — endpoint
  potenti raggiungibili. → Box "L'igiene del repo dopo una migrazione di motore" (alto valore; ponte
  S1-C2 per il deny by-prefix).

- **Una tabella, tre `CREATE` diversi (i 3 schemi `subscribers`)** — *(SR; consolida S1-C9)* — la stessa
  tabella ha **tre definizioni divergenti**: `init_mysql.php` (base, 4 colonne, pre-opt-in);
  `fix_newsletter_table.php` (fossile SQLite, ricrea le 4 colonne, rotto su MySQL); `apply_v293_newsletter`
  in `admin.php` (la **vera** migrazione double opt-in + conferma retroattiva degli storici). Solo
  l'ultima è allineata al runtime, che **presuppone** lo schema esteso → su un DB con solo lo schema base
  ogni query fallisce finché `apply_v293` non gira (dipendenza d'ordine non dichiarata). È il volto
  "evoluzione" del filo già aperto in S1-C9. → Box "Una tabella, tre `CREATE`: dove vive la verità dello
  schema".

- **Il doppio binario di delivery: one-shot vs self-healing** — *(SR)* — la *stessa* migrazione esiste in
  due forme: come file da cancellare (`migrate_status.php`, gated `^migrate_`) **e** come azione
  `?action=apply_v291_status` dentro `admin.php` (gated `isLoggedIn`, persistente). Due filosofie
  convivono: "script usa-e-getta FTP-ato" vs "console di manutenzione dietro login". Senza un registro,
  però, sapere lo stato reale dello schema richiede di interrogare il DB, non il codice — debito di
  **osservabilità dello schema**. → Box "Dove far vivere una migrazione: file da cancellare o console
  persistente".

- **La cura senza la prevenzione** — *(SR vs SPW vs DIS; consolida S1-C12)* — SR ha il defibrillatore
  (`emergency_revert_wal`) ma non il check-up: **nessun** backup automatico né cron (grep negativo). L'unica
  "rete" è `_BACKUP_BEFORE_OPTIMIZATION/`, uno **snapshot manuale committato nel repo** prima
  dell'intervento rischioso — un *gesto*, non un sistema (e per giunta rumore versionato). Il contrasto è
  netto: **SPW** ha backup automatico fuori-docroot con rotazione (S1-C12), **DIS** fa un `.bak`
  pre-distruttivo prima di ogni reset (S1-C2). Se il MySQL di SR si corrompe, non c'è dump da cui
  ripartire. → Box "Avere il defibrillatore ma non il check-up" (alto valore; ponte S1-C12/C2).

- **Il bug del fuso che fa sparire i contenuti** — *(SR; consolida S1-C1/C4)* — la regola di visibilità
  confronta `published_at <= now` **come stringhe**: se il fuso del server e il formato non combaciano,
  gli articoli **spariscono**. `debug_time.php` documenta l'incidente e una "fix" (separatore `T`,
  `date('Y-m-d\TH:i:s')`) che però **nel runtime di produzione non è stata applicata** (`news.php` usa lo
  spazio, il formato DATETIME MySQL corretto): la fix `T` è rimasta solo nel file di diagnostica. → Box
  "Confronti di date come stringhe: il bug del fuso" (consolida S1-C1/C4; qui come *incidente* con la sua
  diagnostica).

- **Il migratore a mano con verifica: l'ETL del thin stack** — *(SR, SPW)* — `migrate_to_mysql.php` apre
  **due PDO** (SQLite sorgente + MySQL destinazione), copia tabella per tabella con `INSERT … ON DUPLICATE
  KEY UPDATE` (idempotente, ri-eseguibile) e **chiude con un `COUNT(*)` di verifica** su ogni tabella. È
  un ETL senza tool: due connessioni, un loop, un riepilogo conteggi a video. Pattern positivo e
  citabile. → Box "ETL thin stack: due PDO e un COUNT".

## 4. Mappa → capitolo/i del libro

| Materiale della scheda | Capitolo esistente | Azione |
|---|---|---|
| **L'incidente WAL** (cause + i due script di cura) | **CAP 14 §2** | **espandi**: §2 lo accenna ("Warning reale"); va il box completo (causa→crash→cura) |
| **Migrazione come reazione a un crash** | **CAP 14 §1-2** | **correggi/riallinea**: §1 la motiva con soglie di traffico, ma il caso reale è l'incidente (vedi sotto) |
| **DIS = SQLite VIVO** (il motore che SR ha lasciato) | **CAP 14 §1** | **aggiungi**: oggi il capitolo è SR-only; DIS dimostra che SQLite in prod regge se non tocchi il WAL |
| **I sei fossili lasciati indietro** | **CAP 14** (nuovo §) | **nuovo box**: l'igiene del repo dopo la migrazione (assente oggi) |
| **Una tabella, tre `CREATE`** (`subscribers`) | **CAP 14** + **CAP 13** | **nuovo box** (consolida S1-C9) |
| **Doppio binario one-shot vs self-healing** | **CAP 14 §3** | **aggiungi**: §3 mostra il pattern a 3 script ma non le due filosofie di delivery |
| **Cura senza prevenzione** (SR niente backup; SPW/DIS sì) | **CAP 14 §6** | **correggi**: la checklist §6 *prescrive* il backup, ma SR non ce l'ha — raccontare il gap |
| **ETL a 2 PDO + COUNT di verifica** | **CAP 14 §3.4** | **ok** (già presente); collega alla verifica conteggi |
| **Bug data-stringa / fuso** (`debug_time.php`) | **CAP 14** + **CAP 3** | **nuovo box** (consolida S1-C1/C4) |
| **`schema_version` assente / schema-as-code mancante** | **CAP 14** | **nuovo §**: il debito "nessun file rappresenta lo schema corrente" |

**Correzioni al testo attuale (la mappatura smentisce / disallinea il libro):**
- **CAP 14 §1 motiva la migrazione con "soglie di traffico" (< 50 scritture/ora).** Il caso reale di SR
  **non** è una soglia di scaling: è la **reazione diretta a un crash da WAL** (la migrazione è del giorno
  *dopo* l'incidente). Il §1 e il §2 vanno saldati: la regola pratica sul traffico resta utile come
  *linea guida generale*, ma la storia di SR è "fuga da un incidente", non "crescita pianificata" — ed è
  proprio questo che la rende preziosa.
- **CAP 14 §6 (checklist) prescrive "Fare un backup completo del `.sqlite"` ma SR non ha un sistema di
  backup.** L'unica rete reale era uno snapshot manuale committato nel repo. Da raccontare il gap (la
  checklist è il *dover essere*, non il *fu*) e collegarlo alla "cura senza prevenzione".
- **CAP 14 è interamente SR-centrico** e non dice che **DISINTELLIGENZA gira ancora su SQLite in
  produzione** senza incidenti. Aggiungere DIS come prova che "SQLite in prod regge" — il problema non era
  SQLite ma il WAL su hosting condiviso — qualifica e rafforza la lezione.
- **CAP 14 omette:** i sei fossili lasciati indietro (igiene del repo), i tre schemi `subscribers`, il
  doppio binario one-shot/self-healing, il bug data-stringa, e il debito "nessun file rappresenta lo
  schema corrente completo" (oggi servono `init_mysql.php` + la catena `apply_v29x` in ordine). Sono le
  dimensioni che trasformano CAP 14 da "come si migra" a "cosa una migrazione lascia indietro".

## 5. Cosa si scarta / dedup

- **Materiale già consolidato altrove (richiamato, non ri-mappato):**
  - **init fossile, versionamento senza registro, scaffolding "vivo", credenziali default, singleton
    PDO/opzioni** → **S1-C1** (qui solo la *conseguenza temporale*: l'evoluzione che allarga la distanza
    init↔vivo, e la migrazione di motore come evento).
  - **i tre schemi `subscribers` lato newsletter** → **S1-C9** (qui come caso di *schema sparso*).
  - **l'assenza di backup nel pannello, il backup fuori-docroot di SPW, il backup `.bak` pre-reset di
    DIS** → **S1-C12 / S1-C2** (qui come *prevenzione mancante* nel quadro incidenti).
  - **il deny by-prefix `.htaccess` degli script di manutenzione, il gate `isLoggedIn`-non-`isAdmin`
    sulle migrazioni** → **S1-C2** (qui solo come *mitigazione* dei fossili).
  - **`fix_image_paths`/conversione WebP come migrazione di dati** → **S1-C5** (qui solo notato come
    "evoluzione del parco media").
  - **il confronto data-stringa / regola di visibilità** → **S1-C4** (qui come incidente con diagnostica).
- **Dettaglio per-sito che NON entra nel libro:** hash di commit, nomi esatti dei singoli `update_db_*`/
  `migrate_*`/`fix_*`, il contenuto di `_BACKUP_BEFORE_OPTIMIZATION/`, il fossile `_ARCHIVIO/pw_reset.php`,
  i numeri di riga. Restano nelle card (SR-C13 soprattutto) come fonte.
- **Perché la scheda è cross-sito pur avendo una fonte principale (SR):** SR è l'unico con una card C13
  dedicata, ma la *lezione* è cross-sito — DIS è il "prima" (SQLite vivo), SPW il "dopo riuscito"
  (migrato + backup), SR il "dopo traumatico" (migrato in fuga, senza rete). È il confronto a tre che dà
  senso al capitolo, non la sola cronaca di SR.
