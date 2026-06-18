# PROSSIMA SESSIONE — prompt pronto da incollare

> ✅ FASE 1 (MAPPATURA) CONCLUSA + gap colmati. Si apre la FASE 2 (SINTESI). Ordine confermato con
> l'utente: S1 → S2 → S3 → S4 (nessuna deviazione). Questa è la PRIMA scheda di sintesi: S1-C1.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.

STATO: FASE 1 (mappatura) CONCLUSA — 4 siti, 34 card, copertura COMPLETA (matrice in
_cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md). SPW 11 · SR 11 · DIS 11 · FDCA 1 (diff).
Ogni card ha un §6 di confronto cross-sito già scritto: è il materiale grezzo della sintesi.

FASE 2 — SINTESI (ROADMAP §4), ordine confermato:
- S1 Consolidamento: da card per-sito a SCHEDE TEMATICHE cross-sito (un cluster per sessione)
- S2 Inventario: cosa entra/aggiorna/è nuovo/si scarta vs i 19 capitoli esistenti
- S3 Scaletta/indice globale (mappa card→capitolo)
- S4 Validazione indice con Simone (GATE prima della scrittura, FASE 3)

METODO (atomico, invariato): UNA scheda tematica per sessione. La scheda fonde i 2-3 trattamenti
per-sito di un cluster in UNA visione comparata (pattern comune + varianti per sito + GOLD + tabella).
Le fonti sono le card di mappatura (specialmente i loro §6, già a confronto). NON si rilegge il codice
sorgente: si consolida ciò che è già mappato.

UNITÀ DI QUESTA SESSIONE: S1-C1 — Scheda tematica cross-sito "Backend Core & Bootstrap".
Fonti: SPW-C1, SR-C1, DIS-C1 (+ nota FDCA-DIFF §3 "C1 identico"). Da consolidare:
- Connessione DB = PDO singleton in 3 salse: MySQL via config.php/define (SPW) · MySQL via
  .env/parse_ini (SR) · SQLite file-in-.data (DIS). Ricetta opzioni PDO (base SPW vs "paranoica" SR
  vs minimale DIS).
- Config & segreti: define() / .env loader / NESSUNA (SQLite non ha credenziali).
- Bootstrap endpoint: inline (SPW/DIS) vs prelude condiviso cors.php (SR); eager vs lazy getDB().
- Init fossile post-migrazione (pattern cross-confermato SPW+SR+DIS; variante "init parziale" di DIS).
- Versionamento schema: migratore one-shot (SPW) / file init_mysql + micro-migrazioni (SR) /
  nomi-file update_db_* (DIS).
- GOLD trasversali: password admin default (random SPW / hardcoded runtime2026 SR / inesistente DIS),
  errore connessione (500+log / 503 / die-leak), SITE_URL canonico (solo SPW), timezone forzato.

Fai così:
1. Crea la cartella _cantiere-terza-edizione/sintesi/ e, se non esiste, proponi un
   _TEMPLATE-SCHEDA.md con la struttura: «Titolo cluster · 1) Il pattern comune (la filosofia thin
   stack su questa lente) · 2) Le varianti per sito (tabella) · 3) GOLD/box problemi-soluzioni · 4)
   Mappa → capitolo/i del libro (esistente da aggiornare / nuovo) · 5) Cosa si scarta/dedup».
2. Scrivi la scheda in _cantiere-terza-edizione/sintesi/S1-C1-backend-core.md seguendo il template.
   Deduplica le ripetizioni dei §6 (la tabella comparativa va scritta UNA volta, pulita).
3. Mappa esplicitamente: questa scheda → quale/i dei 19 capitoli esistenti aggiorna o sostituisce
   (leggi il README/_master del manuale per l'elenco capitoli attuale).
4. Crea/aggiorna _cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md con lo stato delle schede S1-Cx.

Criterio di STOP: scheda S1-C1 in stato COMPLETATO (pattern + varianti + GOLD + mappa capitolo).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md (S1-C1 → ✅)
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta S1-C1 in §4, aggiorna stato globale)
- aggiungi UNA riga a _cantiere-terza-edizione/LOG.md (più recente IN BASSO)
- git add/commit/push (un commit) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima scheda: S1-C2 (Security & Auth
  cross-sito) — fonti SPW-C2, SR-C2, DIS-C2 (+ SPW-C11 per il voter_hash, DIS-C2/C10 per l'anti-frode).
