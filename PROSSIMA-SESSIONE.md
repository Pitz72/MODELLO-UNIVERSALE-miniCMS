# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA unità (da 2026-06-15: può essere una COPPIA
> accorpata di cluster accoppiati — vedi ROADMAP §0.1). Questa volta è una card SINGOLA.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.

METODO (ROADMAP §0.1): si accorpano nella stessa sessione SOLO coppie di cluster già accoppiati. Per
SitoRuntime le coppie erano C4+C5 (fatta) e C7+C8 (fatta); C9, C12, C13 restano DA SOLE. Questa
sessione è SR-C9 (Newsletter & Email) DA SOLA: UNA sola card.

Stato: SimonePizziWebSite (flagship contenuti) è COMPLETO. Su SitoRuntime sono fatte SR-C1 (Backend
Core), SR-C2 (Security & Auth + CORS), SR-C3 (Frontend Bridge & State), la coppia SR-C4 (Content APIs)
+ SR-C5 (Media & Upload) e la coppia SR-C7 (SEO/seo-cache) + SR-C8 (RSS & Feed). Da questa sessione si
prosegue con SR-C9 — Newsletter & Email. Restano poi SR-C12 (Admin) e SR-C13 (DB Evolution & Incidenti),
entrambe da sole → SitoRuntime si chiude in 3 sessioni / 3 card.

Per impostare stile e metodo, leggi le card di riferimento:
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C9-newsletter-email.md (parallelo C9:
  subscribers.php endpoint-router GET/POST/PATCH/DELETE con double opt-in confirm_token monouso +
  unsubscribe_token stabile random_bytes(32); rate-limit per-IP che RICICLA login_attempts di C2;
  newsletter_send.php gated; trasporto mail() nativa; form GDPR doppio checkbox. GOLD: CHIUSURA del
  ponte XSS C6/C7/C8 — la newsletter è il 4°/ultimo emettitore ma NON emette articles.content [solo
  title/excerpt via buildArticleHtml client + body grezzo via buildNewsletterHtml ZERO sanitizzazione,
  il meno sanitizzato dei 4], ponte chiuso a rischio basso perché dietro Auth::check e l'unico input
  pubblico — name — è escapato. Bug: invio sincrono foreach mail() senza coda, unsubscribe GET
  prefetch-able, confirm_token senza TTL).
- _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C8-rss-feed.md (la card appena fatta: il PONTE
  XSS è chiuso per il feed — feed_news_rss.php emette un preview di content ESCAPATO; resta aperto SOLO
  C9. Il quadro dei QUATTRO emettitori del content [DOMPurify/strip_tags-allowlist/strip_tags+escape/
  newsletter] va CHIUSO qui verificando come la newsletter di SR emette il contenuto. NB: TELEGRAM_BOT_TOKEN
  nei segreti SR-C1 + il "token" fossile di feed_config.php → l'eventuale invio Telegram è C9, verificalo qui).
- (facoltativo) SR-C2 per il rate-limit FILE-BASED .cache/ratelimit/ e il riciclo dei meccanismi auth;
  SR-C1 per SMTP_* nei segreti (.env via db_credentials.php) e PHPMailer vendored in lib/ con .htaccess deny.

Unità di QUESTA sessione: SR-C9 (Newsletter & Email) del sito SitoRuntime
(C:\Users\Utente\Documents\GitHub\SITI-WEB\SitoRuntime). UNA card.

Ambito SR-C9 (Newsletter & Email):
- newsletter.php: endpoint pubblico di iscrizione? Double opt-in (confirm_token) o iscrizione diretta?
  unsubscribe_token? Schema subscribers (init_mysql.php lo prevede — SR-C1). Rate-limit (riusa il
  .cache/ratelimit/ FILE-BASED di SR-C2 o altro)? Gate sui rami admin (lista/invio)?
- fix_newsletter_table.php: micro-migrazione dello schema subscribers (one-shot, gated .htaccess
  by-prefix ^fix_). Cosa aggiunge/ripara? → traccia anche C13.
- l'INVIO della newsletter: c'è un newsletter_send equivalente? Dentro admin.php (apply_v293_newsletter
  citato in SR-C4 §8) o in un file a sé? Trasporto: mail() nativa o PHPMailer (lib/ vendored, SR-C1)?
  SMTP_* dai segreti? Invio sincrono foreach o coda?
- test_smtp / contact.php: contact.php è il form contatti (invio mail redazione)? test_smtp (citato in
  SR-C4 §8) diagnostica SMTP? Marca cosa è C9 e cosa è puntatore.
- IL PONTE XSS (chiusura definitiva): la newsletter EMETTE news.content? Con quale sanitizzazione?
  È il 4°/ultimo emettitore — chiudi il quadro dei quattro emettitori iniziato in C6 e ribadito in
  C7/C8. Confronta con SPW-C9 (body grezzo buildNewsletterHtml ZERO sanitizzazione ma dietro Auth).
- Telegram: TELEGRAM_BOT_TOKEN nei segreti — c'è un invio Telegram delle news/newsletter qui? (il
  "token" di feed_config.php in C8 era un fossile). Verifica se C9 è il punto dove il bot vive.

Fai così:
1. Ispeziona in modo microscopico i file di C9 (cita sempre percorso/file:linea).
2. Compila UNA card seguendo _TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C9-newsletter-email.md
3. NON sconfinare: core/DB=C1, security/CORS/rate-limit-meccanica=C2, frontend/client=C3,
   content/slug=C4, media/upload=C5, editor/sanitizzazione-render=C6, SEO/seo-cache=C7 (fatto),
   RSS/feed=C8 (fatto), admin UI=C12, EVOLUZIONE DB & INCIDENTI=C13. Puntatori nelle "Note / domande
   aperte" per il resto.
4. §6: confronto con SPW-C9 (double opt-in, riciclo login_attempts, mail() nativa, body newsletter
   non sanitizzato ma dietro Auth, unsubscribe GET prefetch-able). ATTENZIONE al PONTE XSS-stored: in
   SR la sanitizzazione è render-time client (DOMPurify in Article.tsx, SR-C3/C6) — verifica se la
   newsletter ri-emette news.content GREZZO (riaprendo il buco) oppure no. CHIUDI il quadro dei 4
   emettitori.

Criterio di STOP: card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (SR-C9 → ✅)
- aggiungi UNA riga a _cantiere-terza-edizione/LOG.md (più recente IN BASSO — attento all'ordine cronologico)
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta SR-C9) e lo stato globale
- git add/commit/push (un commit) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: SR-C12 (Admin Dashboard & Panels)
  del sito SitoRuntime, DA SOLA (vedi ROADMAP §0.1: C12, C13 restano singole).
