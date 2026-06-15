# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA sola unità atomica.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.
Leggi anche le card già fatte (contesto indispensabile per C7):
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C1-backend-core.md
  (bootstrap endpoint, singleton PDO, config, struttura public/api, timezone Europe/Rome).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C3-frontend-bridge.md
  (api.ts client; loaders.ts data layer react-router; App.tsx router/SEO via react-helmet-async;
   prerender*.js menzionati come C7).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C4-content-apis.md
  (articles.php: slug, status published + published_at<=now, visibilità pubblico/admin; ricerca LIKE).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C6-advanced-editing.md
  (content HTML grezzo nel DB; sanitizzazione XSS-stored SOLO a render-time con DOMPurify in
   SingleArticle.tsx. ATTENZIONE C7: VERIFICARE se il prerender emette articles.content senza
   DOMPurify — potenziale riapertura del buco XSS-stored fuori da React; SeoScorePanel è C7).

Unità di QUESTA sessione (atomica, una sola): SPW-C7 — SEO & Prerendering
del sito SimonePizziWebSite (C:\Users\Utente\Documents\GitHub\SITI-WEB\SimonePizziWebSite).

Ambito C7: la generazione SEO/meta e il prerendering statico per crawler. In particolare:
- Componente SEO lato client: src/components/SEO.tsx + react-helmet-async (vedi App.tsx) —
  quali meta/OG/Twitter/canonical/JSON-LD vengono iniettati e da quali dati (title/excerpt/cover).
- src/components/admin/SeoScorePanel.tsx: l'analisi SEO live nell'editor (che cosa valuta,
  euristiche, punteggio) — è il lato "redazionale" della SEO.
- Prerendering: gli script prerender*.js (cerca in root, scripts/, build) e/o entry-point PHP che
  servono HTML statico ai bot. Come scoprono le rotte/slug, come iniettano meta e CONTENUTO.
  VERIFICA DI SICUREZZA (ponte C6): il prerender stampa articles.content? Con quale sanitizzazione?
- rebuild_seo_cache / debug_seo / seo-cache: endpoint o script di cache SEO lato server (cerca in
  public/api e scripts). Come viene costruita/invalidata la cache, cosa contiene.
- Sitemap/robots: esistono sitemap.xml dinamica, robots.txt, meta robots per bozze/programmati?
Individua prima i file reali con glob/grep (SEO, prerender, helmet, sitemap, robots, seo-cache).

Fai così:
1. Ispeziona in modo microscopico i file dell'ambito C7 (cita sempre percorso/file:linea).
2. Compila una card seguendo _cantiere-terza-edizione/mappatura/_TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C7-seo-prerendering.md
3. NON sconfinare: backend/db=C1, auth=C2, frontend bridge=C3, contenuti=C4, media=C5,
   editor/sanitizzazione=C6 (già fatti); RSS=C8, newsletter=C9, engagement=C11, admin=C12.
   Se trovi roba di altri cluster, annotala solo come puntatore nelle "Note / domande aperte".
   Qui interessa META/SEO, PRERENDERING e la CACHE SEO.
4. NON riportare credenziali/segreti.

Criterio di STOP: card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (SPW-C7 → ✅)
- aggiungi una riga a _cantiere-terza-edizione/LOG.md
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta SPW-C7) e lo stato globale
- git add/commit/push e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: SPW-C8 — RSS & Feed
