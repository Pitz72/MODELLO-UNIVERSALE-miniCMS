# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA sola unità atomica.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.

🎉 SimonePizziWebSite (flagship contenuti) è COMPLETO: tutte le card SPW-C1…C9, C11, C12
sono in stato COMPLETATO. Da questa sessione si passa al SECONDO sito.

Per impostare lo stile e il metodo, leggi come riferimento la card parallela già fatta:
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C1-backend-core.md
  (è il PARALLELO diretto di questa sessione: stesso cluster C1 sull'altro sito —
   singleton PDO Database::connect(), config/config.example, timezone Europe/Rome,
   struttura public/api, casi "fossile" come init_db.php). Usala per sapere cosa cercare
   e con che livello di dettaglio, MA ricorda che SitoRuntime è un altro codebase: non
   dare per scontato nulla, leggi i file veri.

Unità di QUESTA sessione (atomica, una sola): SR-C1 — Backend Core & Bootstrap
del sito SitoRuntime
(C:\Users\Utente\Documents\GitHub\SITI-WEB\SitoRuntime).
È la PRIMA card del flagship SCALABILITÀ (+ problemi/soluzioni): il sito con più storia
di incidenti DB (MySQL/WAL/emergency revert), che culminerà in SR-C13.

Ambito C1: il cuore backend e il bootstrap. Individua i FILE veri in public/api PRIMA
con glob/grep. Già intravisti (verifica e ispeziona):
- db.php + db_credentials.php (NB: qui le credenziali sembrano in un file SEPARATO,
  diversamente da SPW che usa config.php — primo punto di DIVERGENZA da mappare).
- init_db.php, init_mysql.php, migrate_to_mysql.php, migrate_status.php (evoluzione DB:
  qui c'è più materiale che in SPW — ATTENZIONE a non sconfinare in SR-C13: in C1 mappi
  SOLO bootstrap/connessione/config/struttura; l'EVOLUZIONE storica, gli incidenti WAL e
  emergency_revert_wal.php sono C13 → annotali solo come puntatori).
- lib/ (cartella presente in SitoRuntime e ASSENTE in SPW: cosa contiene? helper condivisi?
  → secondo punto di divergenza da indagare).
- cors.php (esiste come file dedicato: ma il CORS è C2 → solo puntatore).
In particolare verifica:
- Database::connect() è un singleton PDO come in SPW (SPW-C1)? Stesse opzioni PDO
  (ERRMODE_EXCEPTION, charset utf8mb4)? Timezone Europe/Rome forzato?
- Come sono gestite le credenziali (db_credentials.php vs config.php di SPW)? Esiste un
  .example committato? (NON riportare credenziali/segreti reali).
- Struttura di public/api: stesso pattern "un file = un endpoint" di SPW? C'è una cartella
  lib/ con codice condiviso (rottura del pattern flat di SPW)?
- Auto-scaffolding / init: init_db.php è un fossile (come in SPW-C1) o è vivo? init_mysql.php
  cosa crea? (lo SCHEMA dettagliato e la storia migratoria → puntatore C13, qui solo il
  meccanismo di bootstrap).

Fai così:
1. Ispeziona in modo microscopico i file dell'ambito C1 (cita sempre percorso/file:linea).
2. Compila una card seguendo _cantiere-terza-edizione/mappatura/_TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C1-backend-core.md
   (crea la cartella SitoRuntime/ se non esiste).
3. NON sconfinare: auth/CORS=C2, frontend bridge=C3, contenuti(news/speakers/podcasts)=C4,
   media=C5, SEO+cache=C7, RSS=C8, newsletter=C9, admin/dashboard=C12,
   EVOLUZIONE DB & INCIDENTI (WAL/emergency/migrazioni storiche)=C13.
   Se trovi roba di altri cluster, annotala SOLO come puntatore nelle "Note / domande aperte".
   Qui interessa BACKEND CORE / BOOTSTRAP / CONFIG / CONNESSIONE DB / STRUTTURA public/api.
4. Sezione §6 (Differenze rispetto agli altri siti): COMPILALA con cura — è la prima card
   del secondo sito, quindi il confronto con SPW-C1 è il vero valore (credenziali separate,
   cartella lib/, eventuale diverso pattern di connessione/scaffolding).
5. NON riportare credenziali/segreti.

Criterio di STOP: card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (SR-C1 → ✅)
- aggiungi una riga a _cantiere-terza-edizione/LOG.md (più recente IN BASSO)
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta SR-C1) e lo stato globale
- git add/commit/push e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: SR-C2 — Security & Auth
  (+ CORS) del sito SitoRuntime.
