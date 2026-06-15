# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA sola unità atomica.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.
Leggi anche le card già fatte (contesto indispensabile per C6):
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C1-backend-core.md
  (bootstrap endpoint, singleton PDO, config, struttura public/api).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C2-security-auth.md
  (gate Auth::check; CSP nell'.htaccess; sanitizzazione lato sicurezza).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C3-frontend-bridge.md
  (api.ts: uploadMedia/uploadMediaWithProgress riusati dall'editor per inserire media nel testo).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C4-content-apis.md
  (articles/projects salvano `content` HTML e `cover_image` come stringa URL; sanitizeUrl dei CTA
   è qui rimandato a C6).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C5-media-upload.md
  (LATO SERVER dei media: come il file finisce su disco/DB. L'EMBED del media DENTRO il contenuto
   dell'editor è C6: verificare se l'editor riusa uploadMedia/uploadMediaWithProgress).

Unità di QUESTA sessione (atomica, una sola): SPW-C6 — Advanced Editing / Editor
del sito SimonePizziWebSite (C:\Users\Utente\Documents\GitHub\SITI-WEB\SimonePizziWebSite).

Ambito C6: l'editor di contenuti ricchi e la sanitizzazione del testo. In particolare:
- src/components/admin/RichTextEditor.tsx: che editor è (Quill / custom / contenteditable?),
  toolbar, formati ammessi, come produce l'HTML salvato in `articles.content`/`projects.content`.
- src/pages/admin/ArticleEditor.tsx e src/pages/admin/ProjectEditor.tsx: il form di editing,
  gestione cover_image, inserimento media nel corpo, bozza/pubblicazione, validazione lato client.
- Inserimento media nel testo: l'editor riusa api.uploadMedia/uploadMediaWithProgress (C3/C5)?
  Come incorpora l'URL ritornato (img/link)? Dove avviene il sanitize (client? server? entrambi?).
- Sanitizzazione: DOMPurify o simili lato client; eventuale sanitizzazione/escape lato server;
  il sanitizeUrl dei CTA visto in C4 (articles.php) come pezzo della stessa difesa XSS-stored.
- Come il content HTML viene poi RENDERIZZATO lato pubblico (dangerouslySetInnerHTML?) — il ponte
  XSS stored end-to-end (editor → DB → render).
Individua prima i file reali con glob/grep (src/components/admin, src/pages/admin).

Fai così:
1. Ispeziona in modo microscopico i file dell'ambito C6 (cita sempre percorso/file:linea).
2. Compila una card seguendo _cantiere-terza-edizione/mappatura/_TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C6-advanced-editing.md
3. NON sconfinare: backend/db=C1, auth=C2, frontend bridge=C3, contenuti=C4, media lato server=C5
   (già fatti); SEO=C7, RSS=C8, newsletter=C9, engagement=C11, admin=C12.
   Se trovi roba di altri cluster, annotala solo come puntatore nelle "Note / domande aperte".
   Qui interessa l'EDITING dei contenuti ricchi e la SANITIZZAZIONE.
4. NON riportare credenziali/segreti.

Criterio di STOP: card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (SPW-C6 → ✅)
- aggiungi una riga a _cantiere-terza-edizione/LOG.md
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta SPW-C6) e lo stato globale
- git add/commit/push e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: SPW-C7 — SEO & Prerendering
