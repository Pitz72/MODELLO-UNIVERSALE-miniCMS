# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA unità (da 2026-06-15: può essere una COPPIA
> accorpata di cluster accoppiati — vedi ROADMAP §0.1). Questa volta è una card SINGOLA — la PRIMA
> del 3° sito DISINTELLIGENZA, che APRE il sito.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.

METODO (ROADMAP §0.1): si accorpano nella stessa sessione SOLO coppie di cluster già accoppiati. Per
DISINTELLIGENZA NON sono ancora state definite coppie: la PRIMA card (DIS-C1, backend core) va fatta
DA SOLA, perché è quella che fissa lo stile/metodo dell'intero sito e perché è ad alta densità (db.php,
init_db, e — sorpresa — una lunga catena di `update_db_*`). Le eventuali coppie le decideremo DOPO aver
visto la geografia del sito in C1.

Stato: i PRIMI DUE siti (i due flagship) sono COMPLETI.
- SimonePizziWebSite (flagship contenuti): COMPLETO (11 card).
- SitoRuntime (flagship scalabilità + incidenti): COMPLETO (10 card: C1, C2, C3, C4, C5, C7, C8, C9, C12, C13).
Si apre ora il 3° sito: DISINTELLIGENZA (base festival, votazioni/iscrizioni). 21/~30 card totali fatte.

DIFFERENZA CHIAVE rispetto ai primi due siti: DISINTELLIGENZA gira ancora su SQLITE *VIVO*
(public/api/database.sqlite presente nel repo, più una cartella DATABASESOLOPERCONSULTAZIONE). Tutto ciò
che in SitoRuntime SR-C13 era "fossile" (PRAGMA, WAL, sqlite_master, AUTOINCREMENT, datetime()) qui è il
MOTORE REALE. Questo rende DIS il termine di paragone "dal vivo" del DB-a-file: leggi SR-C13 prima di
iniziare, ti servirà per il §6 (DIS-C1 vs i due flagship migrati a MySQL).

Unità di QUESTA sessione: DIS-C1 (Backend Core & Bootstrap) del sito DISINTELLIGENZA
(C:\Users\Utente\Documents\GitHub\SITI-WEB\DISINTELLIGENZA). UNA card. PRIMA del sito.

Ambito DIS-C1 (Backend Core & Bootstrap):
- public/api/db.php (connessione PDO a SQLite: come apre il file, opzioni, singleton? confronto con i
  due db.php MySQL già mappati). Verifica dove vive il file .sqlite e come viene referenziato.
- public/api/init_db.php (schema SQLite VIVO + eventuale seed): qui NON è un fossile, è la fonte di
  verità. Mappa le tabelle del festival (participants/votes/settings/users/news/...) ma SOLO per il
  bootstrap — la logica festival è C10, news è C4, auth è C2.
- la catena update_db_*.php (update_db_0_1_3 / 0_1_4 / maintenance / registration / security_move /
  v0.4.2 / v0.5.4 / voting): è la storia migratoria del sito. In C1 mappa il MECCANISMO di bootstrap e
  versionamento schema (c'è un registro versioni? un pattern ALTER+skip come SR? nomi con numero di
  versione?); la cronologia incidenti dettagliata sarà la C13 di DIS (se la apriremo).
- config/timezone/struttura public/api: prelude di bootstrap (c'è un cors.php condiviso come SR o
  bootstrap inline come SPW?), gestione errori connessione, eventuale config/segreti. Nota: in root ci
  sono anche fix_api.cjs/fix_api.js — verifica se toccano il bootstrap o sono build-tooling.
- NON sconfinare: security/auth=C2, frontend=C3, content/news=C4, media/upload=C5, newsletter=C9,
  festival logic (participants/votes/settings/reset_votes/stats)=C10, admin=C12, evoluzione DB &
  incidenti dettagliati=C13. In C1 solo db.php + init_db + il meccanismo di migrazione + bootstrap.

Fai così:
1. Ispeziona in modo microscopico i file di C1 (cita sempre percorso/file:linea).
2. Compila UNA card seguendo _TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/DISINTELLIGENZA/DIS-C1-backend-core.md
   (crea la cartella DISINTELLIGENZA/ dentro mappatura/ — è la prima card del sito).
3. §6: confronto a TRE — DIS-C1 (SQLite vivo) vs SPW-C1 e SR-C1 (entrambi MySQL migrati). Il valore è
   "il sito che NON ha migrato": come appare il DB-a-file quando è ancora la scelta corrente, non un
   fossile. Riusa la cronologia SR-C13 (WAL/PRAGMA) come specchio.
4. Lascia puntatori nelle "Note / domande aperte" per C2/C4/C5/C9/C10/C12/C13.

Criterio di STOP: card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (DIS-C1 → ✅)
- aggiungi UNA riga a _cantiere-terza-edizione/LOG.md (più recente IN BASSO — attento all'ordine cronologico)
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta DIS-C1, aggiorna stato globale)
- git add/commit/push (un commit) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: verosimilmente DIS-C2 (Security &
  Auth + anti-frode voto), DA SOLA — oppure, se in DIS-C1 emergono coppie naturali, proponile.
