# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA sola unità atomica.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.
Leggi anche le card già fatte rilevanti per C9 (contesto indispensabile):
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C1-backend-core.md
  (singleton PDO Database::connect(), timezone Europe/Rome, struttura public/api).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C2-security-auth.md
  (Auth::check gate, CSRF Origin/Referer, rate limiting riusato login_attempts, cookie HttpOnly/Secure;
   ATTENZIONE C9: l'iscrizione newsletter e l'invio sono gated? c'è doppio opt-in/token? rate limit?).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C4-content-apis.md
  (articles.php: regola di visibilità status=published + published_at<=now — STESSA regola che un
   eventuale invio newsletter "ultimi articoli" dovrebbe rispettare).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C6-advanced-editing.md
  (articles.content salvato GREZZO; difesa XSS-stored SOLO a render-time con DOMPurify).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C7-seo-prerendering.md
  (prerender ri-emette content via strip_tags allowlist ≠ DOMPurify → buco attributi).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C8-rss-feed.md
  (GOLD: rss.php è il TERZO emettitore ma NON emette articles.content — solo excerpt+htmlspecialchars,
   "sicurezza-per-sottrazione". Il ponte C6/C7 resta aperto SOLO per C9: la newsletter è l'ULTIMO
   possibile emettitore di articles.content e il rischio XSS in un'email è da verificare con cura).

Unità di QUESTA sessione (atomica, una sola): SPW-C9 — Newsletter & Email
del sito SimonePizziWebSite (C:\Users\Utente\Documents\GitHub\SITI-WEB\SimonePizziWebSite).

Ambito C9: iscrizione, gestione iscritti, composizione e invio email. In particolare:
- Endpoint reali: cerca con glob/grep (newsletter, newsletter_send, subscribers, subscribe,
  unsubscribe, contact, mail, smtp, phpmailer, send). Individua i FILE veri in public/api prima.
- Iscrizione: come avviene il subscribe? c'è doppio opt-in / token di conferma? validazione email?
  rate limit / anti-spam (riusa login_attempts come C2)? gating Auth::check sui rami di invio?
- Invio: come si compone l'email? template HTML? SE inietta articles.content/excerpt → con quale
  sanitizzazione (CHIUSURA DEFINITIVA del ponte C6/C7/C8: quarto/ultimo emettitore del contenuto)?
- Disiscrizione: link unsubscribe, token, GUID/URN stabile dell'iscritto?
- Trasporto: mail() nativa, SMTP, PHPMailer, servizio esterno? credenziali (NON riportarle).
- Lato client/admin: form di iscrizione (footer? ContactPage? CommunityHub?), pannello admin invio.
  Verifica i falsi positivi come fatto in C8.
Individua prima i file reali con glob/grep.

Fai così:
1. Ispeziona in modo microscopico i file dell'ambito C9 (cita sempre percorso/file:linea).
2. Compila una card seguendo _cantiere-terza-edizione/mappatura/_TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C9-newsletter-email.md
3. NON sconfinare: backend/db=C1, auth=C2, frontend bridge=C3, contenuti=C4, media=C5,
   editor/sanitizzazione=C6, SEO/prerender=C7, RSS/feed=C8 (già fatti); engagement/reactions/messages=C11,
   admin=C12. Se trovi roba di altri cluster, annotala solo come puntatore nelle "Note / domande aperte".
   Qui interessa NEWSLETTER/EMAIL e l'iscrizione/invio.
4. CHIUDI DEFINITIVAMENTE il follow-up di sicurezza C6/C7/C8: la newsletter emette
   articles.content/excerpt? Con quale sanitizzazione? (quarto e ultimo emettitore del contenuto —
   il più delicato perché renderizzato in un client email).
5. NON riportare credenziali/segreti (chiavi SMTP, password, API key).

Criterio di STOP: card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (SPW-C9 → ✅)
- aggiungi una riga a _cantiere-terza-edizione/LOG.md
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta SPW-C9) e lo stato globale
- git add/commit/push e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: SPW-C11 — Engagement & Social
  (reactions/messages) — oppure SPW-C12 Admin se più sensato dopo C9.
