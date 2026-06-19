# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟨 FASE 2 (SINTESI) in corso. S1-C1 → S1-C11 ✅ COMPLETATE (11/14). L'ultima è stata una SESSIONE
> TRIPLA (C9+C10+C11 di fila, per non ricaricare il contesto). Restano: **S1-C12, S1-C13, S1-FORK**.
> Questa è la DODICESIMA scheda: **S1-C12 Admin Dashboard & Panels**. Ordine: S1 → S2 → S3 → S4.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md, _cantiere-terza-edizione/LOG.md e
_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md per il contesto.

STATO: FASE 1 (mappatura) CONCLUSA — 4 siti, 34 card. FASE 2 (SINTESI) in corso: **11/14 schede S1
completate** (S1-C1…C11 ✅). Metodo: UNA scheda tematica cross-sito per sessione (ma si possono fare
PIÙ schede di fila nella stessa sessione, come la tripla C9/C10/C11 — scriverle/committarle comunque
una alla volta). Fonde i 2-3 trattamenti per-sito in UNA visione comparata (pattern comune + tabella
varianti unica + GOLD + mappa→capitoli). Fonti = card di mappatura (specialmente i §6). NON si rilegge
il codice sorgente. Template: `_cantiere-terza-edizione/sintesi/_TEMPLATE-SCHEDA.md`; modelli già fatti:
`S1-C1` … `S1-C11` (seguine struttura e livello di dettaglio).

UNITÀ DI QUESTA SESSIONE: **S1-C12 — Scheda tematica cross-sito "Admin Dashboard & Panels"**.
Fonti primarie: SPW-C12, SR-C12, DIS-C12. Da consolidare (spunti dai §6 e dal LOG):
- **Scala a 3 modelli di dashboard:** SPW = dashboard che **MISURA** (stats.php + analytics a doppia
  personalità + 6 grafici Chart.js + selettore periodo 7/30/90 + AdminLayout con route-guard unico
  adminAuthLoader); SR = dashboard che **NON misura niente** = console CRUD pura (Admin.tsx mega-componente
  596 righe, "Dashboard" = section-switcher a 8 card senza dati/contatori/grafici, guard-componente
  checkAuth on mount); DIS = **via di mezzo** (AdminLayout come SPW + guard-componente come SR, dashboard
  che misura ma TESTUALE — stats.php senza Chart.js).
- **GOLD per sito:** SPW = (1) backup automatico FUORI dalla docroot (../db_backups_simonepizzi) perché
  clean-dist.js strippa .data/ → il .htaccess deny non arriva mai sul server, ricreato a runtime + nome
  random_bytes + chmod 0600 + rotazione 15; (2) pseudo-cron gated admin-OR-secret timing-safe hash_equals;
  (3) settings POST accetta chiavi arbitrarie no-whitelist; (4) optimize_db NON distruttivo nonostante
  intestazione "usa-e-getta". SR = (1) "la dashboard che non misura niente" (gemello del framing upload
  SR-C5); (2) NESSUN backup/export/cron — il flagship degli incidenti ha la cura (emergency_revert_wal
  S1-C13) ma non la prevenzione (vs backup fuori-docroot SPW); (3) change_password senza session_version →
  invalidazione client-side setTimeout. DIS = (1) la dashboard MISURA (≠ SR) ma testuale; (2) contacts
  WRITE-ONLY (mai letti da nessun pannello, l'admin li vede solo via email di notifica — chiude buco
  DIS-C9); (3) guard ROLE-BLIND (AdminLayout controlla solo login non role==admin → editor vede tutto);
  (4) reset distruttivi via fetch POST nudo senza CSRF (protezione = doppio window.confirm UX + gate admin).
- **Tre modi di fare un admin (architettura frontend):** mega-componente unico SR (1 rotta /admin, tutto
  dentro) / AdminLayout + loader react-router SPW (guard dichiarativo, N pagine figlie via Outlet) /
  AdminLayout + guard-componente DIS (struttura SPW ma guard imperativo SR). Ponte forte a S1-C3 (guard
  loader-vs-componente già consolidato lì) — qui l'architettura completa del pannello.
- **Ponti:** backup/cron/optimize_db → S1-C13 (DB evolution); analytics consumer delle reazioni → S1-C11;
  gate role-blind → S1-C2; consumer dei contenuti (NewsletterComposer, ArticleEditor, MediaManager) →
  S1-C4/C5/C6/C9 (qui solo come aggregati nel pannello, non ri-mappati).

Fai così:
1. Scrivi la scheda in `_cantiere-terza-edizione/sintesi/S1-C12-admin-dashboard.md` seguendo
   `_TEMPLATE-SCHEDA.md` (0 una-frase · 1 pattern comune · 2 tabella varianti UNICA · 3 GOLD/box · 4
   mappa→capitoli · 5 scarti/dedup).
2. Mappa esplicitamente → capitoli esistenti. ATTENZIONE: **non esiste un capitolo "Admin Dashboard"
   dedicato** nei 19 capitoli attuali (verifica: i capitoli admin sono spalmati — CAP 10 auth, CAP 18
   dashboard FESTIVAL, ecc.). Quindi questa scheda probabilmente segnala un GAP = un capitolo nuovo da
   proporre in S3 (Admin Dashboard generale, distinto dal CAP 18 festival-specifico). Verifica leggendo
   _master.md / l'indice dei capitoli e proponi dove collocare il materiale (nuovo CAP o sezione).
3. Aggiorna `_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md` (S1-C12 → ✅, contatore 12/14).

Criterio di STOP: scheda S1-C12 in stato COMPLETATO (pattern + varianti + GOLD + mappa/proposta capitolo).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna `_INDICE-SINTESI.md` (S1-C12 → ✅) + `ROADMAP.md` (§4 spunta S1-C12, §7 stato globale)
- aggiungi UNA riga a `LOG.md` (più recente IN BASSO)
- git add/commit/push (un commit) e verifica locale = origin/main
- riscrivi QUESTO file (root + _cantiere-terza-edizione/) con la prossima scheda: **S1-C13 (DB Evolution
  & Incidenti)** — fonti SR-C13 (princ.), DIS-C1 (meccanismo update_db_*), SPW-C1 (init fossile). Alto
  valore e corposo (l'incidente WAL notturno, la migrazione MySQL come reazione, i fossili SQLite, i 3
  schemi subscribers, cura-senza-prevenzione). → CAP 14. Dopo C13 resta solo **S1-FORK** (FDCA come caso
  fork/evoluzione, fonte FDCA-DIFF — non aggiunge pattern, backend = DIS) e poi S2/S3/S4.

Nota: si possono di nuovo fare PIÙ schede di fila se la sessione lo consente (C12 + C13, o C13 + FORK).
Valuta in base allo spazio di contesto. Le schede vanno comunque scritte e committate una alla volta.
