# PROSSIMA SESSIONE — prompt pronto da incollare

> ✅ FASE 1 (MAPPATURA) CONCLUSA. Si apre la FASE 2 (SINTESI). Questa è la prima unità della sintesi.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.

STATO: la FASE 1 (mappatura) è CONCLUSA — 4 siti, 29 card:
- SimonePizziWebSite (flagship contenuti, MySQL): 11 card (C1–C9, C11, C12)
- SitoRuntime (flagship scalabilità+incidenti, MySQL): 10 card (C1–C5, C7–C9, C12, C13)
- DISINTELLIGENZA (festival, SQLite vivo): 7 card (C1, C2, C4, C5, C9, C10, C12)
- FDCA (fork di DIS): 1 card di DIFF (backend identico, solo re-skin frontend)
Tutte le card sono in _cantiere-terza-edizione/mappatura/<sito>/ con §6 di confronto già scritti.

ORA: FASE 2 — SINTESI (ROADMAP §4). Obiettivo: da 29 card per-sito a un MANUALE. Sotto-fasi:
- S1 — Consolidamento: schede TEMATICHE cross-sito (un cluster alla volta, dedup pattern comuni + varianti)
- S2 — Inventario contenuti (cosa entra/aggiorna/nuovo/scarta nel libro vs i 19 capitoli esistenti)
- S3 — Scaletta/indice globale della Terza Edizione (mappa card→capitolo)
- S4 — Validazione indice con Simone (GATE prima della scrittura)

METODO (atomico, invariato): una unità per sessione. La sintesi S1 si fa UN CLUSTER PER SESSIONE
(non tutti insieme): ogni scheda tematica cross-sito è corposa (mette a confronto 2-4 siti su una
lente, con i GOLD già trovati). I §6 delle card sono il materiale grezzo già pronto.

UNITÀ DI QUESTA SESSIONE (proposta): S1-C1 — Scheda tematica cross-sito "Backend Core & Bootstrap".
Consolidare in UNA scheda il confronto già presente nei §6 di SPW-C1, SR-C1, DIS-C1 (+ nota FDCA):
- la connessione DB: PDO singleton in 3 salse (MySQL config.php / MySQL .env / SQLite file) — la
  tabella comparativa è già abbozzata in SR-C1 §6 e DIS-C1 §6.
- bootstrap endpoint: inline (SPW/DIS) vs prelude condiviso cors.php (SR).
- config/segreti: define() / parse_ini .env / nessuna (SQLite).
- init fossile dopo migrazione (pattern cross-confermato su SPW+SR+DIS, con la variante "init parziale" di DIS).
- versionamento schema: migratore one-shot / micro-migrazioni / nomi-file update_db_*.
- GOLD trasversali: password default (runtime2026 SR / random SPW / inesistente DIS), error handling
  connessione (500+log / 503 / die-leak), timezone forzato.

Fai così:
1. Rileggi i §6 e le sezioni rilevanti di SPW-C1, SR-C1, DIS-C1 (e la nota C1 di FDCA-DIFF).
2. Decidi un formato per le SCHEDE TEMATICHE (proponi un _TEMPLATE-SCHEDA.md in
   _cantiere-terza-edizione/sintesi/ se non esiste: titolo, "il pattern", "le varianti per sito",
   "tabella comparativa", "GOLD/box", "→ quale capitolo del libro"). Crea la cartella sintesi/.
3. Scrivi la scheda S1-C1 in _cantiere-terza-edizione/sintesi/S1-C1-backend-core.md
4. Mappa esplicitamente: questa scheda → quale/i capitolo/i dei 19 esistenti (vedi README/_master del
   manuale) va ad aggiornare o sostituire.

ATTENZIONE: questa è una DECISIONE DI IMPOSTAZIONE della FASE 2. Se Simone preferisce partire dalla
SCALETTA GLOBALE (S3) invece che dalle schede (S1) — per validare prima la struttura del libro e poi
riempirla — proporglielo all'inizio e lasciarlo scegliere. S4 (validazione indice) è comunque un GATE
prima della scrittura vera (FASE 3).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta S1-C1 in §4, aggiorna stato globale)
- aggiungi UNA riga a _cantiere-terza-edizione/LOG.md (più recente IN BASSO)
- (l'indice mappatura è chiuso; per la sintesi valutare un _INDICE-SINTESI.md in sintesi/)
- git add/commit/push (un commit) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima scheda (S1-C2 Security & Auth, o il
  cluster scelto con Simone).
