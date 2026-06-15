# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA sola unità atomica.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.
Leggi anche le card già fatte rilevanti per C11 (contesto indispensabile):
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C1-backend-core.md
  (singleton PDO Database::connect(), timezone Europe/Rome, struttura public/api).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C2-security-auth.md
  (Auth::check gate, CSRF Origin/Referer, rate limiting riusato login_attempts, cookie HttpOnly/Secure;
   ATTENZIONE C11: reactions/messages sono gated o pubblici? c'è rate limit anti-spam? CSRF sui POST?).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C4-content-apis.md
  (endpoint-router su REQUEST_METHOD con Auth::check sui rami mutativi — STESSO pattern atteso in C11).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C9-newsletter-email.md
  (GOLD: rate-limit per-IP che ricicla login_attempts; messages.php già intravisto come C11; difesa
   input pubblico via htmlspecialchars/strip_tags — verifica come C11 tratta il testo dei messaggi pubblici).

Unità di QUESTA sessione (atomica, una sola): SPW-C11 — Engagement & Social
(reactions/messages) del sito SimonePizziWebSite
(C:\Users\Utente\Documents\GitHub\SITI-WEB\SimonePizziWebSite).

Ambito C11: reazioni/like agli articoli e messaggi/contatti dai visitatori. In particolare:
- Endpoint reali: cerca con glob/grep (reactions, reaction, like, vote, message, messages, contact,
  guestbook, comment). Individua i FILE veri in public/api prima (es. messages.php già visto in C9).
- Reactions: come si reagisce? per articolo? anti-doppio-voto (IP/cookie/fingerprint)? rate limit?
  gating Auth::check sui rami admin (es. azzeramento conteggi)?
- Messages/contatti: come arriva un messaggio? validazione/sanitizzazione del testo (input PUBBLICO →
  XSS-stored se mostrato in admin senza escaping)? rate limit anti-spam (riusa login_attempts come C2/C9)?
  notifica email all'admin (intreccio con C9: usa mail()?)? lettura/eliminazione lato admin.
- Lato client/admin: componenti reazione sugli articoli (SingleArticle?), form contatti (ContactPage?),
  pannello admin messaggi. Verifica i falsi positivi come fatto in C8/C9.
Individua prima i file reali con glob/grep.

Fai così:
1. Ispeziona in modo microscopico i file dell'ambito C11 (cita sempre percorso/file:linea).
2. Compila una card seguendo _cantiere-terza-edizione/mappatura/_TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C11-engagement-social.md
3. NON sconfinare: backend/db=C1, auth=C2, frontend bridge=C3, contenuti=C4, media=C5,
   editor/sanitizzazione=C6, SEO/prerender=C7, RSS/feed=C8, newsletter/email=C9 (già fatti); admin=C12.
   Se trovi roba di altri cluster, annotala solo come puntatore nelle "Note / domande aperte".
   Qui interessa ENGAGEMENT/SOCIAL (reactions + messages/contatti).
4. Follow-up sicurezza: il testo PUBBLICO dei messaggi/contatti viene sanitizzato? Dove (server o
   render admin)? È un potenziale XSS-stored mostrato nel pannello admin? (parallelo al filo "emettitori"
   chiuso in C9, ma qui la fonte è input pubblico, non admin).
5. NON riportare credenziali/segreti.

Criterio di STOP: card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (SPW-C11 → ✅)
- aggiungi una riga a _cantiere-terza-edizione/LOG.md
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta SPW-C11) e lo stato globale
- git add/commit/push e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: SPW-C12 — Admin Dashboard & Panels
  (ULTIMA card di SimonePizziWebSite; poi si passa a SitoRuntime SR-C1).
