# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA sola unità atomica.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.
Leggi anche le card già fatte rilevanti per C8 (contesto indispensabile):
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C1-backend-core.md
  (singleton PDO Database::connect(), timezone Europe/Rome, struttura public/api).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C4-content-apis.md
  (articles.php: slug, status=published + published_at<=now, categoria, excerpt/content;
   contratto di visibilità pubblico/admin — STESSA regola che il feed RSS dovrà rispettare).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C6-advanced-editing.md
  (articles.content salvato GREZZO nel DB; difesa XSS-stored SOLO a render-time con DOMPurify
   in SingleArticle.tsx).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C7-seo-prerendering.md
  (GOLD: il prerender crawler in index.php:404 ri-emette content via strip_tags allowlist ≠ DOMPurify
   → buco XSS-stored a livello attributi. ATTENZIONE C8: VERIFICARE come rss.php emette il contenuto/
   description degli item — strip_tags? CDATA grezzo? htmlspecialchars? È il TERZO emettitore del
   content dopo render-React e prerender; chiude/estende il follow-up di sicurezza C6/C7).

Unità di QUESTA sessione (atomica, una sola): SPW-C8 — RSS & Feed Syndication
del sito SimonePizziWebSite (C:\Users\Utente\Documents\GitHub\SITI-WEB\SimonePizziWebSite).

Ambito C8: la generazione del feed RSS/Atom e la sindacazione dei contenuti. In particolare:
- public/api/rss.php (FILE PRINCIPALE già individuato): struttura del feed (RSS 2.0 vs Atom),
  header Content-Type, channel (title/link/description/language), come seleziona gli articoli
  (regola status/published_at come C4?), come costruisce <item> (title, link assoluto, guid/URN,
  pubDate, description/content:encoded), e SOPRATTUTTO con quale sanitizzazione emette il contenuto
  (ponte C6/C7: strip_tags? CDATA? escaping?). Cita sempre percorso/file:linea.
- Routing del feed: c'è una rewrite in .htaccess (es. feed.xml/rss.xml → rss.php) o si accede
  direttamente a /api/rss.php? (Nota: in .htaccess oggi c'è solo sitemap.xml/robots.txt; verificare
  se il feed è esposto con URL "pulito" o grezzo).
- Lato client/redazionale: dov'è linkato il feed? (grep ha trovato menzioni "rss/feed" in
  src/components/Header.tsx, ContactPage.tsx, CommunityHub.tsx, admin/ArticlesList.tsx,
  admin/ArticleEditor.tsx, admin/ProjectEditor.tsx, data/portfolioData.ts — verificare quali sono
  link al feed RSS reale e quali sono falsi positivi, es. "feed" come parola generica).
- feed_config / GUID / URN: esiste configurazione del feed (numero item, TTL, self-link Atom)?
  Come sono costruiti i GUID/permalink degli item (isPermaLink, URN stabile vs URL)?
Individua prima i file reali con glob/grep (rss, feed, atom, channel, item, guid, CDATA).

Fai così:
1. Ispeziona in modo microscopico i file dell'ambito C8 (cita sempre percorso/file:linea).
2. Compila una card seguendo _cantiere-terza-edizione/mappatura/_TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C8-rss-feed.md
3. NON sconfinare: backend/db=C1, auth=C2, frontend bridge=C3, contenuti=C4, media=C5,
   editor/sanitizzazione=C6, SEO/prerender/sitemap=C7 (già fatti); newsletter=C9, engagement=C11,
   admin=C12. Se trovi roba di altri cluster, annotala solo come puntatore nelle "Note / domande
   aperte". Qui interessa RSS/FEED e la SINDACAZIONE.
4. CHIUDI il follow-up di sicurezza C6/C7: rss.php emette articles.content/excerpt? Con quale
   sanitizzazione? (terzo emettitore dopo render-React e prerender crawler).
5. NON riportare credenziali/segreti.

Criterio di STOP: card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (aggiungi SPW-C8 → ✅)
- aggiungi una riga a _cantiere-terza-edizione/LOG.md
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta SPW-C8) e lo stato globale
- git add/commit/push e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: SPW-C9 — Newsletter & Email
