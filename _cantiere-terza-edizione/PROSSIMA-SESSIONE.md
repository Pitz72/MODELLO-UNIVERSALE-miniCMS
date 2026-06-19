# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟨 FASE 2 (SINTESI) in corso. S1-C1 ✅, S1-C2 ✅, S1-C3 ✅, S1-C4 ✅ COMPLETATE.
> Questa è la QUINTA scheda di sintesi: **S1-C5 Media & Upload**. Ordine confermato:
> S1 → S2 → S3 → S4 (nessuna deviazione).

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md, _cantiere-terza-edizione/LOG.md e
_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md per il contesto.

STATO: FASE 1 (mappatura) CONCLUSA — 4 siti, 34 card, copertura COMPLETA. FASE 2 (SINTESI) in corso:
**4/14 schede S1 completate** (S1-C1 Backend Core ✅, S1-C2 Security & Auth ✅, S1-C3 Frontend Bridge
✅, S1-C4 Content APIs ✅). Metodo: UNA scheda tematica cross-sito per sessione, che fonde i 2-3
trattamenti per-sito di un cluster in UNA visione comparata (pattern comune + varianti per sito in
tabella unica + GOLD + mappa→capitoli). Le fonti sono le card di mappatura (specialmente i loro §6,
già a confronto). NON si rilegge il codice sorgente: si consolida ciò che è già mappato. Il template è
`_cantiere-terza-edizione/sintesi/_TEMPLATE-SCHEDA.md`; i modelli già fatti sono
`S1-C1-backend-core.md`, `S1-C2-security-auth.md`, `S1-C3-frontend-bridge.md` e
`S1-C4-content-apis.md` (seguine struttura e livello di dettaglio).

UNITÀ DI QUESTA SESSIONE: **S1-C5 — Scheda tematica cross-sito "Media & Upload"**.
Fonti primarie: SPW-C5, SR-C5, DIS-C5. Da consolidare (spunti dai §6 già scritti):
- **La scala della difesa upload — il GOLD portante:** SPW = difesa a **3 livelli** (estensione +
  magic bytes `finfo` + `uploads/.htaccess` PHP-off); SR = **1 livello** applicativo (estensione +
  magic bytes ma NIENTE `uploads/.htaccess` → PHP non spento sugli upload); DIS = **≈0 livelli** +
  **upload PUBBLICO** non autenticato (`type=audio_participant`) + validazione solo su `$_FILES['type']`
  client (spoofabile) + naming che conserva nome+estensione + no PHP-off = **catena RCE verificata**.
  → "quanto puoi togliere a un sistema di upload prima che diventi insicuro": SR mostra il limite, DIS
  cosa c'è un passo oltre (e perché un upload *pubblico* cambia tutte le regole).
- **Naming anti-doppia-estensione (3 modi, 3 livelli di sicurezza):** SPW `uniqid-base.ext` con i punti
  TOLTI dal nome; SR `uniqid` puro (nome utente SCARTATO del tutto); DIS `uniqid_nome.ext` (nome ed
  estensione CONSERVATI — il più debole, abilita la RCE).
- **Image processing:** SPW WebP+resize 1920 sincrono via GD (INSERT in tabella `media`); SR WebP+resize
  con GIF animata preservata + EXIF strippato dalla ri-codifica; DIS **solo resize, NO WebP** (formato
  preservato), resize solo per `type=image`.
- **Modello storage:** SPW sottocartelle per MIME reale + tabella `media` + `download.php` proxy
  (readfile + nome umano + path-guard realpath); SR **flat** `/uploads/`, NESSUNA tabella media
  (scandir piatto), nessun download.php; DIS sottocartelle per `type` CLIENT + NESSUNA tabella (scandir
  RICORSIVO) + nessun download.php.
- **Delete & path-guard:** SPW `Auth::check` + `realpath`+containment; SR `basename()` SENZA CSRF
  (media.php non include auth_utils, sessione nuda); DIS solo `strpos('..')` + unlink multi-candidato
  SENZA CSRF (il più debole). Ponte S1-C2.
- **Dangling media:** comune a SR/DIS (nessuna tabella né reference-count: il legame URL↔file è solo
  testuale, cancellare non aggiorna cover_image/audio_file); SPW ha la tabella ma il dangling resta
  possibile da cover_image solo-URL senza FK.
- **One-shot manutenzione:** SPW optimize_uploads/fix_uploads_subfolder (dry-run); SR optimize_webp/
  fix_image_paths dentro admin.php (gated login); DIS `migrate_media.php` **NON gated** (chiunque
  triggera lo spostamento massivo + riscrittura DB). Storia storage flat→sottocartelle in tutti e tre.
- **GOLD DoS (DIS):** upload pubblico SENZA rate-limit né limite size/durata audio = storage flooding
  oltre alla RCE (salda con participants.php pubblico di S1-C2/C10).

Fai così:
1. Scrivi la scheda in `_cantiere-terza-edizione/sintesi/S1-C5-media-upload.md` seguendo
   `_TEMPLATE-SCHEDA.md` (0 una-frase · 1 pattern comune · 2 tabella varianti UNICA e deduplicata · 3
   GOLD/box · 4 mappa→capitoli · 5 scarti/dedup). La tabella comparativa va scritta UNA volta, pulita.
2. Mappa esplicitamente → capitoli esistenti: soprattutto **CAP 7 (Media & Optimization)**, con ponti
   a CAP 10 (Security, upload come superficie d'attacco / PHP-off / delete senza CSRF), CAP 16-17
   (Festival, upload pubblico delle tracce) e CAP 14 (storia storage flat→sottocartelle).
   Segnala eventuali CORREZIONI al testo attuale (come fatto per CAP 3/10/6/9 nelle schede precedenti).
3. Aggiorna `_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md` (S1-C5 → ✅, contatore 5/14).

Criterio di STOP: scheda S1-C5 in stato COMPLETATO (pattern + varianti + GOLD + mappa capitolo).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna `_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md` (S1-C5 → ✅)
- aggiorna `_cantiere-terza-edizione/ROADMAP.md` (spunta S1-C5 in §4, aggiorna §7 stato globale)
- aggiungi UNA riga a `_cantiere-terza-edizione/LOG.md` (più recente IN BASSO)
- git add/commit/push (un commit) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md, sia root sia in _cantiere-terza-edizione/) con la
  prossima scheda: **S1-C6 (Advanced Editing / Editor)** — fonti SPW-C6, SR-C6, DIS-C6 (Tiptap-blindato
  SPW / Tiptap + shim migrazione Quill→Tiptap SR / contentEditable+execCommand senza DOMPurify DIS;
  difesa XSS-stored render-time, guardie link, la scala a 3 gradini dell'editor).
