# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟨 FASE 2 (SINTESI) in corso. S1-C1 (Backend Core) ✅, S1-C2 (Security & Auth) ✅ e
> S1-C3 (Frontend Bridge) ✅ COMPLETATE. Questa è la QUARTA scheda di sintesi:
> **S1-C4 Content APIs**. Ordine confermato: S1 → S2 → S3 → S4 (nessuna deviazione).

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md, _cantiere-terza-edizione/LOG.md e
_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md per il contesto.

STATO: FASE 1 (mappatura) CONCLUSA — 4 siti, 34 card, copertura COMPLETA. FASE 2 (SINTESI) in corso:
**3/14 schede S1 completate** (S1-C1 Backend Core ✅, S1-C2 Security & Auth ✅, S1-C3 Frontend Bridge
✅). Metodo: UNA scheda tematica cross-sito per sessione, che fonde i 2-3 trattamenti per-sito di un
cluster in UNA visione comparata (pattern comune + varianti per sito in tabella unica + GOLD +
mappa→capitoli). Le fonti sono le card di mappatura (specialmente i loro §6, già a confronto). NON si
rilegge il codice sorgente: si consolida ciò che è già mappato. Il template è
`_cantiere-terza-edizione/sintesi/_TEMPLATE-SCHEDA.md`; i modelli già fatti sono
`S1-C1-backend-core.md`, `S1-C2-security-auth.md` e `S1-C3-frontend-bridge.md` (seguine struttura e
livello di dettaglio).

UNITÀ DI QUESTA SESSIONE: **S1-C4 — Scheda tematica cross-sito "Content APIs"**.
Fonti primarie: SPW-C4, SR-C4, DIS-C4. Da consolidare (spunti dai §6 già scritti):
- **Forma dell'endpoint:** SPW = endpoint-router su `REQUEST_METHOD` con `Auth::check` sui rami
  mutativi (un file per risorsa: articles/categories/navigation/tags/projects/search); SR = geografia
  FRAMMENTATA (lettura news pubblica in `news.php` GET-only con cache su file, ma CRUD news in
  `admin.php?action=list/get/save/delete`; speakers/podcasts router classici); DIS = endpoint-router
  CRUD in UN file su `REQUEST_METHOD` (GET pubblico + POST admin), strutturalmente come SPW.
- **Il contratto di risposta — chiude il filo aperto in S1-C3:** SPW = Double Read CHIUSO lato server
  (SOLO `articles` lista ritorna `{data,total}`, tutto il resto array nudo → il client legge due volte
  perché MESCOLA le due famiglie nei loader); SR = TRE buste diverse (`{success,data,meta}` news /
  `{success,articles,total}` list / array NUDO speakers+podcasts) = mosaico per-endpoint, radice del
  non-Double-Read di SR-C3; DIS = "busta zero" sempre nuda (array/oggetto diretto), il più semplice.
- **Paginazione:** SPW backend-driven COUNT+LIMIT/OFFSET con PARAM_INT; SR `total_pages` pre-calcolato
  server + cache file `.cache/news_*.json` TTL 300s X-Cache HIT/MISS; DIS niente paginazione-meta
  (array nudo, no total).
- **Visibilità published_at — saldare coi fusi di S1-C1:** SPW `status=published AND published_at<=now`;
  SR separatore SPAZIO (query corretta) + `status='published' OR status IS NULL` (status fuori schema
  base, cicatrice migrazione v2.9.1); DIS `CURRENT_TIMESTAMP` SQLite (UTC) vs published_at nel fuso
  server (sfasamento), e interroga ANCORA `status='scheduled'` (residuo migrazione v0.5.4 non ripulito).
- **Slug:** SPW normalizzazione accenti; SR TRE filosofie nello stesso sito (news senza accenti /
  podcast iconv ASCII//TRANSLIT / speaker senza slug=id client); DIS senza accenti + unicità
  PREVENTIVA (count+'-'.time()).
- **Tassonomia:** SPW categorie gerarchiche (IN sottocategorie) + tag M:N `article_tags` a doppia
  scrittura + cache CSV legacy; SR/DIS category = stringa libera (default 'News'/'generale'), molto più
  piatti, niente tag relazionali.
- **GOLD schema-vivo (DIS):** news SELECTa/INSERTa `category`+`status` ma init_db.php non le ha e
  nessun update_db_* le crea → colonne solo nel `.sqlite` (prova pratica del "init mente" di S1-C1);
  podcasts CREATE TABLE inline senza slug ma INSERT con slug ("tabella che nessuno crea uguale").
- **GOLD author (SR):** author SEMPRE 'Admin' (username non in sessione → filo S1-C2/C3 chiuso);
  ricerca: SPW LIKE unificata articoli+progetti con campo `type`; SR/DIS più piatti.

Fai così:
1. Scrivi la scheda in `_cantiere-terza-edizione/sintesi/S1-C4-content-apis.md` seguendo
   `_TEMPLATE-SCHEDA.md` (0 una-frase · 1 pattern comune · 2 tabella varianti UNICA e deduplicata · 3
   GOLD/box · 4 mappa→capitoli · 5 scarti/dedup). La tabella comparativa va scritta UNA volta, pulita.
2. Mappa esplicitamente → capitoli esistenti: soprattutto **CAP 9 (Content Lifecycle)**, con ponti a
   CAP 6 (Frontend Bridge, qui si CHIUDE il contratto che il client legge "due volte"), CAP 3
   (visibilità/fusi/schema), CAP 15 (Portfolio & Projects, per la ricerca unificata SPW).
   Segnala eventuali CORREZIONI al testo attuale (come fatto per CAP 3/10/6 nelle schede precedenti).
3. Aggiorna `_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md` (S1-C4 → ✅, contatore 4/14).

Criterio di STOP: scheda S1-C4 in stato COMPLETATO (pattern + varianti + GOLD + mappa capitolo).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna `_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md` (S1-C4 → ✅)
- aggiorna `_cantiere-terza-edizione/ROADMAP.md` (spunta S1-C4 in §4, aggiorna §7 stato globale)
- aggiungi UNA riga a `_cantiere-terza-edizione/LOG.md` (più recente IN BASSO)
- git add/commit/push (un commit) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md, sia root sia in _cantiere-terza-edizione/) con la
  prossima scheda: **S1-C5 (Media & Upload)** — fonti SPW-C5, SR-C5, DIS-C5 (difesa upload a 3 livelli
  SPW / minimale 1 livello SR / catena RCE da upload pubblico DIS; WebP+resize, sottocartelle vs flat,
  naming anti-doppia-estensione).
