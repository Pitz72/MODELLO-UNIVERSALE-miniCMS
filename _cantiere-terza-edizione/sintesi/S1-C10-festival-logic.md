# Scheda di Sintesi — S1-C10 — Festival Logic (modulo concorso a voto pubblico)

> **Stato:** COMPLETATO
> **Cluster FASE 2:** S1-C10 · **Data:** 2026-06-19 · **Commit:** _(in corso)_
> **Fonti (card di mappatura, in particolare i §6):** DIS-C10 (unico sito con festival) · FDCA-DIFF (eredita il backend byte-identico) · contrappunti: SPW-C11 (reactions = engagement senza concorso), S1-C2 (anti-frode voto già consolidato)
> **Capitoli del libro toccati:** CAP 16 (Iscrizioni & Workflow Approvazione), CAP 17 (Votazioni & Anti-Frode), CAP 18 (Dashboard, Settings & Reporting) — i tre capitoli festival · ponti a CAP 10 (anti-frode → S1-C2), CAP 13 (consenso newsletter → S1-C9), CAP 9 (visibilità) → vedi §4

---

## 0. In una frase
Il "festival" è un **modulo opzionale** del miniCMS presente in **un solo sito** (DISINTELLIGENZA; FDCA
ne è il fork che lo eredita immutato): un **concorso a voto pubblico** gestito non da una macchina a
stati rigorosa ma da **interruttori booleani** (`status` + `in_current_round` + master switch in
`settings`) e da un **contatore denormalizzato** (`vote_count`) che *è* la fonte di verità della
classifica. La lezione cross-edizione è che i tre capitoli del libro (CAP 16-18) descrivono una
versione **idealizzata** del modulo, mentre il codice reale mostra le crepe tipiche del "fatto a
interruttori": report finale **costruito e disabilitato**, stato `finalist` **vestigiale**, e una
classifica che può **derivare in silenzio** dal conteggio reale dei voti.

## 1. Il pattern comune — la filosofia "thin stack" su questa lente

Essendo un cluster mono-sito, il "pattern comune" non è la media di tre implementazioni ma la **forma
canonica del modulo concorso** così come DIS la realizza — ed è comunque coerente con la filosofia thin
stack vista negli altri cluster.

**1) Una pipeline a stati gestita da colonne booleane, non da una macchina a stati.** Il ciclo è:
iscrizione pubblica (`participants.php?submit` → `pending`, se `registration_active`) → selezione
admin/editor (`update_status` → `approved`/`rejected`, con email di esito + iscrizione newsletter) →
voto pubblico 1-3 preferenze **solo** per chi è `approved AND in_current_round=1` (se `voting_active`) →
classifica → reset turno o reset totale. Non c'è un campo "stato del concorso": ci sono **flag** che
l'admin accende e spegne.

**2) I master switch come "quadro elettrico" pubblico-in-lettura.** La tabella `settings`
(chiave/valore) tiene `voting_active`/`registration_active`/`maintenance` + periodo: **GET pubblico**
(il frontend legge gli stati per mostrare/nascondere i form) e **POST admin** con UPSERT SQLite
(`ON CONFLICT(key) DO UPDATE`). Un interruttore in `settings` apre o chiude un'intera fase per tutti.

**3) Il contatore denormalizzato come fonte di verità della classifica.** Ogni voto è una **transazione**
`INSERT votes` + `UPDATE participants SET vote_count = vote_count + 1`: la classifica (e il report) si
ordinano per `vote_count`, **non** per `COUNT(votes)`. La denormalizzazione è la scelta di performance
del thin stack (classifica = una `SELECT … ORDER BY vote_count`), col rovescio del drift (§3).

**4) Round "manuali" via flag booleano.** Le eliminatorie/semifinali/finale non sono entità: sono il
flag `in_current_round` acceso su un sottoinsieme di partecipanti. L'admin "fa girare" il concorso
spostando il flag, e `reset_votes` azzera i voti del turno mantenendo gli iscritti. Nessuna eliminazione
automatica, nessuna storicizzazione per-turno.

**5) Voto pubblico difeso all'origine, non con account.** Il concorso non ha utenti registrati lato
pubblico: l'anti-frode è una barriera **IP/24h** (`REMOTE_ADDR` grezzo) + cookie cosmetico + validazione
1-3 + master switch — già consolidata in **S1-C2** (qui solo richiamata, non ri-mappata).

## 2. Le varianti (tabella: il modulo reale vs il testo idealizzato vs il fork)

Non essendoci tre siti, la tabella confronta **il modulo come lo descrive il libro (CAP 16-18)**, **come
lo realizza davvero DIS**, e **come lo eredita FDCA**.

| Asse | CAP 16-18 (testo idealizzato) | DISINTELLIGENZA (codice reale) | FDCA (fork) |
|---|---|---|---|
| **Macchina a stati iscrizione** | pipeline `pending→approved/rejected` "obbligatoria" | sì, ma gate `update_status` solo `isset(user_id)` → **anche un editor approva** (S1-C2) | = DIS (backend byte-identico) |
| **Round** | "interruttore booleano per attivare gruppi" | `in_current_round` flag booleano; **nessuna** eliminazione automatica né storia per-turno | = DIS |
| **Stato `finalist`** | "selezionare i finalisti da spostare nel round" | enum presente ma **MAI impostato dal codice** (vestigiale) → i round usano il flag, non lo stato | = DIS |
| **Classifica** | "ordinata per `vote_count`" | `vote_count` **denormalizzato** = fonte di verità; nessuna reconciliation → **drift silenzioso** possibile | = DIS |
| **Anti-frode voto** | cookie + IP/24h + UA | IP/24h `REMOTE_ADDR` grezzo = **barriera reale**; cookie `dis_voted` = **cosmetico**; UA salvato; IP+UA in chiaro (PII) → S1-C2 | = DIS |
| **Master switch** | "quadro elettrico" admin | `settings` GET **pubblico** (no allowlist) + POST admin UPSERT; difesa `'1'\|\|'true'` contro seed incoerente | = DIS |
| **Reporting finale** | "il backend può inviare il report Top 20" | `sendVotingReport` **COSTRUITO ma DISABILITATO/commentato** ("Phase 2") = feature dormiente | = DIS |
| **Reset** | (non discusso) | `reset_votes` (azzera voti+contatore, tiene iscritti) vs `reset_system` (totale); **backup `.bak` pre-distruttivo** (S1-C2) | = DIS |
| **Consenso newsletter** | "garantisce la crescita del DB marketing" (CAP 16 §4) | iscrizione **implicita** all'approvazione (`INSERT OR IGNORE`) **senza consenso esplicito** → problema GDPR (S1-C9) | = DIS |
| **Visibilità** | (non discusso) | doppia condizione `approved AND in_current_round=1` per il voto; `settings` espone gli stati al frontend | = DIS |

**Lettura della tabella.** Il modulo è **funzionante e coerente con la sua filosofia** (interruttori
semplici, contatore veloce, voto pubblico difeso all'origine), ma il testo del libro lo descrive nella
sua versione *aspirazionale*: tre punti che il codice contraddice — **report dormiente**, **`finalist`
mai usato**, **drift della classifica** — più due framing da correggere (il consenso newsletter
presentato come "strategia di crescita" è in realtà un buco GDPR; il cookie presentato come "protezione"
è cosmetico). FDCA non aggiunge nulla: avendo il backend PHP byte-identico, **eredita il modulo intatto,
crepe comprese** — è il caso "fork che congela anche i difetti", già visto in S1-C5 (RCE ereditata) e
S1-C2.

## 3. GOLD & box problemi-soluzioni

- **Round "a interruttore", non a macchina a stati** — *(DIS)* — è il GOLD portante e il tratto che
  definisce il modulo. Non esiste un'entità "turno" né una transizione di stato del concorso: c'è il
  flag `in_current_round` acceso/spento su gruppi di partecipanti. Pro: semplicità totale (l'admin
  gestisce le fasi con un toggle). Contro: nessuna eliminazione automatica, e soprattutto **`reset_votes`
  CANCELLA i voti del turno precedente** → la storia per-turno è persa, salvo il backup `.bak`. → Box
  "Gestire le fasi di un concorso con un flag booleano: semplicità e prezzo" (alto valore).

- **Lo stato che racconta un piano abbandonato: `finalist` vestigiale** — *(DIS)* — l'enum dei
  partecipanti include `finalist`, ma **nessuna riga di codice lo imposta mai**: i round si fanno col
  flag booleano, non con lo stato. È lo **schema che documenta un'intenzione mai realizzata** — gemello
  del `TELEGRAM_BOT_TOKEN` fossile (S1-C9) e dei settings `podcast_*` mai popolati (S1-C8). Il CAP 18 §3
  parla di "spostare i finalisti": descrive il piano, non il codice. → Box "Lo schema che racconta un
  piano abbandonato" (corregge CAP 18 §3).

- **La classifica che deriva in silenzio: il contatore denormalizzato** — *(DIS)* — `vote_count` è la
  fonte di verità di classifica e report, **non** `COUNT(votes)`. La transazione lo mantiene coerente e
  il reset lo riallinea, ma **manca una reconciliation**: se una scrittura va storta (transazione
  parziale, import manuale, fix sul DB) il contatore e i voti reali divergono → **classifica sbagliata
  senza alcun segnale**. È il classico trade-off della denormalizzazione: lettura veloce, verità fragile.
  → Box "Denormalizzare un contatore: performance contro verità" (alto valore, ponte CAP 18).

- **Il report costruito e mai acceso** — *(DIS)* — `sendVotingReport` (Top 20 via email allo staff alla
  chiusura del voto) è **interamente scritto ma disabilitato/commentato** ("Phase 2"). Il CAP 18 §4 lo
  presenta come capacità attiva ("il backend *può* innescare l'invio"): vero come *codice presente*,
  falso come *funzione operante*. È un altro "fossile in attesa" (come `finalist`). → confluisce nel box
  "feature dormiente" + correzione CAP 18 §4.

- **Il master switch che si difende dalla propria seed** — *(DIS)* — `isVotingActive` accetta sia `'1'`
  sia `'true'` perché il bulk update di `settings` salva i booleani come stringhe `'true'/'false'`
  mentre altrove ci si aspetta `'1'`: la lettura difensiva `'1'||'true'` **compensa un'incoerenza di
  formato introdotta dalla scrittura**. È la stessa ambiguità `'1'/'true'` che torna in DIS-C1/C2. Da un
  lato robustezza, dall'altro il sintomo di una convenzione non fissata. → Box "Quando il lettore deve
  difendersi da come scrive lo scrittore".

- **Il consenso che arriva di lato** — *(DIS; ponte S1-C9)* — all'approvazione di un partecipante il suo
  indirizzo è iscritto alla newsletter con `INSERT OR IGNORE`, **senza un consenso esplicito** alla
  newsletter (i commenti nel sorgente mostrano lo sviluppatore in dubbio). Il CAP 16 §4 lo presenta come
  "Newsletter Sync Strategy" che "garantisce la crescita del database marketing… solo utenti reali e
  validati": framing da rovesciare — è un **problema di base giuridica GDPR** (consenso al concorso ≠
  consenso al marketing). → confluisce nel box di **S1-C9** "consenso come effetto collaterale";
  corregge CAP 16 §4.

- **Il gate che confonde "loggato" con "admin"** — *(DIS; rimando S1-C2)* — `update_status`/
  `update_round` sono protetti solo da `isset($_SESSION['user_id'])`, **non** da `isAdmin()`: un editor
  può approvare/respingere partecipanti e cambiare round. È già consolidato in **S1-C2** (gate
  role-blind); qui solo richiamato perché è proprio il punto di controllo del workflow festival. → ponte
  S1-C2.

## 4. Mappa → capitolo/i del libro

| Materiale della scheda | Capitolo esistente | Azione |
|---|---|---|
| **Round a flag booleano** (semplicità + reset distrugge la storia) | **CAP 17 §3** | **amplia**: §3 descrive bene il toggle ma non dice che `reset_votes` cancella i voti del turno |
| **`finalist` vestigiale** | **CAP 18 §3** | **correggi**: §3 parla di "spostare i finalisti" — stato mai usato nel codice |
| **Contatore denormalizzato + drift** | **CAP 18 §3** (Ranking) | **nuovo box**: la classifica per `vote_count` e il rischio di drift (oggi assente) |
| **Report finale dormiente** | **CAP 18 §4** | **correggi**: §4 lo dà come capacità attiva; è costruito ma disabilitato ("Phase 2") |
| **Master switch + difesa `'1'\|\|'true'`** | **CAP 18 §1** + **CAP 17 §4** | **aggiungi nota**: `settings` GET pubblico (no allowlist) + lettura difensiva |
| **Consenso newsletter all'approvazione** | **CAP 16 §4** | **correggi**: "Newsletter Sync Strategy" → è un problema di consenso GDPR (ponte CAP 13) |
| **Anti-frode (IP/24h, cookie cosmetico, IP in chiaro)** | **CAP 17 §2** | **rimanda a S1-C2** + **correggi**: il cookie `dis_voted` è cosmetico, la barriera reale è IP/24h |
| **Gate role-blind su approvazione/round** | **CAP 16 §1 / CAP 18 §3** | **rimanda a S1-C2** (editor può approvare) |
| **Backup `.bak` pre-reset** | **CAP 18** | **rimanda a S1-C2** (prevenzione pre-distruttiva) |
| **Festival come MODULO OPZIONALE + eredità FDCA** | **CAP 16 (intro)** | **inquadra**: presente in 1 sito su 4; FDCA lo eredita immutato (fork che congela i difetti) |

**Correzioni al testo attuale (la mappatura smentisce / disallinea il libro):**
- **CAP 18 §4 presenta il report finale come capacità attiva** ("il backend può innescare l'invio di
  un'email di report finale… Top 20"). Nel codice `sendVotingReport` è **costruito ma
  disabilitato/commentato** ("Phase 2"): è una feature dormiente, da segnalare come tale (non come
  funzione operante).
- **CAP 18 §3 dice di "selezionare i finalisti da spostare nel round successivo".** Lo stato `finalist`
  esiste nell'enum ma **non è mai impostato**: i round sono fatti col flag `in_current_round`. Da
  correggere descrivendo il meccanismo reale (flag booleano) e segnalando lo stato vestigiale.
- **CAP 16 §4 ("Newsletter Sync Strategy") presenta l'iscrizione automatica come pregio.** È invece un
  **problema di consenso GDPR**: l'utente acconsente al *concorso*, non alla *newsletter*; l'`INSERT OR
  IGNORE` all'approvazione non raccoglie un consenso marketing esplicito. Da riformulare con il caveat
  (ponte CAP 13 / S1-C9).
- **CAP 17 §2 presenta cookie + IP + UA come tre protezioni equivalenti.** In realtà il cookie
  `dis_voted` è **cosmetico** (client-side, aggirabile) e lo UA è solo **registrato** per analisi: la
  **sola barriera reale** è l'IP/24h (`REMOTE_ADDR` grezzo — qui un pregio anti-spoof, vedi S1-C2, ma con
  collisione NAT). Da gerarchizzare le difese.
- **CAP 18 §3 (Ranking) non avverte del drift** del contatore denormalizzato: la classifica per
  `vote_count` è veloce ma senza reconciliation può divergere dal conteggio reale. Da aggiungere.
- **Inquadramento generale:** i CAP 16-18 trattano il festival come se fosse un componente standard del
  Modello; va detto che è un **modulo opzionale** presente in **un solo sito** (DIS) e che FDCA lo
  **eredita immutato** (backend byte-identico) — utile per non far credere che sia parte del core CMS.

## 5. Cosa si scarta / dedup

- **Materiale già consolidato altrove (richiamato, non ri-mappato):**
  - **l'intera meccanica anti-frode del voto** (master switch difensivo, barriera IP/24h, `voter_hash`
    di SPW come contrappunto privacy, reset-a-un-clic senza CSRF, backup pre-distruttivo) → **S1-C2**,
    dove è già il GOLD #4/#5/#6. Qui solo il *contesto festival* in cui quella meccanica vive.
  - **l'iscrizione newsletter implicita + il trasporto `mail()` dei template di concorso** → **S1-C9**
    (qui solo il *trigger*: l'approvazione).
  - **lo schema `participants`/`votes`/`settings`, il versionamento `update_db_*`, l'IP in chiaro come
    PII** → **S1-C1/C2/C4** (qui solo consumati).
  - **l'upload pubblico delle tracce dei partecipanti (catena RCE)** → **S1-C5** (qui solo: l'asset
    audio che l'admin pre-ascolta prima di approvare).
  - **la dashboard che MISURA (`stats.php`) e l'inbox `contacts` write-only** → **S1-C12** (admin).
- **Dettaglio per-sito che NON entra nel libro:** numeri di riga, i nomi esatti delle azioni
  (`update_status`/`update_round`/`reset_votes`/`reset_system`/`confirm_reset`), il bug `$count`
  undefined nel messaggio di reset, i microcopy comici dei template ("Leggi Peggio", brand voice del
  festival). Restano nella card DIS-C10 come fonte.
- **Perché la scheda è più corta:** il cluster è mono-sito e gran parte del suo "peso di sicurezza" è
  già stato assorbito da S1-C2 (anti-frode) e S1-C9 (consenso/email). Qui resta il **cuore logico** del
  modulo (stati, round, contatore, master switch, reporting) e l'allineamento col testo idealizzato dei
  CAP 16-18.
