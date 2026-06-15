# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA unità (da 2026-06-15: può essere una COPPIA
> accorpata di cluster accoppiati — vedi ROADMAP §0.1).

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.

NOVITÀ METODO (ROADMAP §0.1): da ora si accorpano nella stessa sessione SOLO coppie di cluster già
accoppiati, mantenendo DUE file-card separati + DUE righe LOG separate. Questa sessione è la prima
coppia: SR-C4 + SR-C5.

Stato: SimonePizziWebSite (flagship contenuti) è COMPLETO. Su SitoRuntime sono fatte SR-C1 (Backend
Core), SR-C2 (Security & Auth + CORS) e SR-C3 (Frontend Bridge & State). Da questa sessione si
prosegue con la COPPIA C4+C5 — Content APIs + Media/Upload (logica SERVER).

Per impostare stile e metodo, leggi le card di riferimento:
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C4-content-apis.md (parallelo C4) e
  _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C5-media-upload.md (parallelo C5: upload
  a doppio strato estensione+magic bytes, naming uniqid anti-doppia-estensione, smistamento
  sottocartelle su MIME reale, WebP+resize sincrono via GD, media.php libreria, download proxy
  path-guarded, uploads/.htaccess PHP-off, difesa in profondità a 3 livelli, path traversal "dal DB").
- _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C3-frontend-bridge.md (la card client appena
  fatta: ti dà le BUSTE che ora mappi lato server — news.php={success,data,meta},
  admin.php?action=list={success,articles,total}, speakers/podcasts=array NUDO, e l'upload client
  uploadImage→upload.php con X-CSRF-Token ma SENZA progress).
- (facoltativo) SR-C1 per il vocabolario (getDB() lazy, schema init_mysql.php news/speakers[col
  JSON]/podcasts, incidente fuso/formato-data debug_time.php — confronto stringa published_at<=NOW
  con separatore 'T', che è LOGICA C4 di visibilità) e SR-C2 (gate isLoggedIn/validateCsrf per-ramo).

Unità di QUESTA sessione: COPPIA SR-C4 + SR-C5 del sito SitoRuntime
(C:\Users\Utente\Documents\GitHub\SITI-WEB\SitoRuntime). Due card separate.

Ambito SR-C4 (Content APIs — logica server di news/speakers/podcasts):
- news.php: lista pubblica paginata {success,data,meta} (COUNT + LIMIT/OFFSET?), lookup per slug, e
  SOPRATTUTTO la regola di VISIBILITÀ status=published AND published_at<=NOW: com'è scritto il
  confronto data/ora? È il confronto-stringa con separatore 'T' dell'incidente di SR-C1? Post
  programmato (published_at futuro).
- admin.php rami contenuto (action=list/get/save/delete): forma {success,articles,total}, generazione
  slug (normalizzazione accenti?), campo author (SR-C2/C3: $_SESSION['username'] non salvato →
  author='Admin'), draft vs published, gating isLoggedIn/CSRF.
- speakers.php: colonna JSON (programs/social?), flag founder, forma ARRAY NUDO in lettura vs
  {success,...} in errore (perché la guardia Array.isArray lato client), GET/POST/DELETE.
- podcasts.php: forma array nudo, struttura feed/episodi (solo lettura/scrittura DB; il feed RSS
  syndication è C8 → puntatore).
- categorie/tag/ricerca/navigazione: ci sono o SitoRuntime è più piatto (category stringa libera)?
  Mappa quello che c'è, marca N/A il resto.

Ambito SR-C5 (Media & Upload — logica server):
- upload.php: validazione (estensione? magic bytes/MIME reale come SPW?), naming dei file,
  destinazione/sottocartelle, conversione/resize immagini (WebP via GD? sincrono?), risposta
  {success,url,...}, gate isLoggedIn+validateCsrf (SR-C2 ha già visto upload.php:8,13).
- media.php (libreria: lista {success,files}, eliminazione con unlink? path-guard?).
- download/proxy se presente; uploads/.htaccess PHP-off (SR-C2 NON l'ha trovato → VERIFICARE qui se
  esiste protezione equivalente: è un potenziale buco annotato in SR-C2 §8).
- script one-shot optimize_*/fix_image_paths (se di C5; storia migratoria media → puntatore C13).

Fai così:
1. Ispeziona in modo microscopico i file di C4 e C5 (cita sempre percorso/file:linea).
2. Compila DUE card seguendo _TEMPLATE.md e salvale in
   _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C4-content-apis.md e
   _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C5-media-upload.md
3. NON sconfinare: core/DB=C1, security/CORS=C2, frontend/client=C3 (fatti), editor/sanitizzazione=C6,
   SEO+cache=C7, RSS/feed=C8, newsletter=C9, admin UI=C12, EVOLUZIONE DB & INCIDENTI=C13. Puntatori
   nelle "Note / domande aperte" per il resto. Tieni C4 e C5 distinti: la logica contenuti (query,
   slug, visibilità, buste) in C4; lo storage/file (validazione, magic bytes, WebP, sottocartelle,
   PHP-off) in C5.
4. §6 di ENTRAMBE le card: confronto con SPW-C4 e SPW-C5 (Double Read vs buste eterogenee; categoria
   gerarchica+tag M:N vs category piatta; published_at<=NOW e incidente 'T'; difesa upload a 3 livelli
   e uploads/.htaccess PHP-off presente/assente).

Criterio di STOP: ENTRAMBE le card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (SR-C4 → ✅, SR-C5 → ✅)
- aggiungi DUE righe a _cantiere-terza-edizione/LOG.md (una per card, più recenti IN BASSO)
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta SR-C4 e SR-C5) e lo stato globale
- git add/commit/push (un commit per la coppia) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: COPPIA SR-C7 + SR-C8
  (SEO & Prerendering + seo-cache · RSS & Feed) del sito SitoRuntime.
