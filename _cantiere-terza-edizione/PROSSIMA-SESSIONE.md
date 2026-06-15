# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA unità (da 2026-06-15: può essere una COPPIA
> accorpata di cluster accoppiati — vedi ROADMAP §0.1).

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.

METODO (ROADMAP §0.1): si accorpano nella stessa sessione SOLO coppie di cluster già accoppiati,
mantenendo DUE file-card separati + DUE righe LOG separate. Questa sessione è la SECONDA coppia di
SitoRuntime: SR-C7 + SR-C8 (sono i due "emettitori" dello stesso contenuto news → SEO e RSS).

Stato: SimonePizziWebSite (flagship contenuti) è COMPLETO. Su SitoRuntime sono fatte SR-C1 (Backend
Core), SR-C2 (Security & Auth + CORS), SR-C3 (Frontend Bridge & State) e la coppia SR-C4 (Content
APIs) + SR-C5 (Media & Upload). Da questa sessione si prosegue con la COPPIA C7+C8 — SEO/Prerendering
e RSS/Feed.

Per impostare stile e metodo, leggi le card di riferimento:
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C7-seo-prerendering.md (parallelo C7: SEO
  Engine v2.0 = Dynamic Rendering ibrido in public/index.php, isCrawler() UA-sniff, sitemap.php/
  robots.php dinamici via rewrite senza file fisici, JSON-LD per tipo pagina, SEO.tsx client con
  canonical NON parametrizzato, SeoScorePanel; GOLD: index.php:404 ri-emette content via strip_tags
  allowlist ≠ DOMPurify → buco XSS-stored a livello ATTRIBUTI via UA spoofing).
- _cantiere-terza-edizione/mappatura/SimonePizziWebSite/SPW-C8-rss-feed.md (parallelo C8: rss.php
  feed RSS 2.0 real-time, RFC822, GUID urn:…isPermaLink=false, enclosure; GOLD: rss.php NON emette
  articles.content → il PIÙ SICURO dei 3 emettitori, sicurezza-per-sottrazione).
- _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C4-content-apis.md (la card appena fatta: ti dà
  la regola di visibilità published_at<=date('Y-m-d H:i:s') AND (status='published' OR status IS
  NULL) che C7/C8 devono RIUSARE; e la CACHE su file .cache/news_*.json + seo_news_*.json già scritta
  dentro admin.php su save — è il PONTE diretto a C7, da mappare qui come strategia).
- (facoltativo) SR-C1 per index.php "SEO Engine v3.0" e SITE_URL canonico ASSENTE (baseUrl da
  HTTP_HOST), e SR-C5 per il fatto che cover_image è una stringa URL (open graph image).

Unità di QUESTA sessione: COPPIA SR-C7 + SR-C8 del sito SitoRuntime
(C:\Users\Utente\Documents\GitHub\SITI-WEB\SitoRuntime). Due card separate.

Ambito SR-C7 (SEO & Prerendering + seo-cache):
- public/index.php: c'è un "SEO Engine" (SR-C1 lo marca v3.0)? È Dynamic Rendering UA-sniff come SPW
  o un meccanismo diverso? Come deriva baseUrl (HTTP_HOST, visto SITE_URL canonico assente in SR-C1)?
  Inietta meta/JSON-LD? Routing PHP speculare a React Router?
- rebuild_seo_cache.php: cosa rigenera, e come si lega ai file seo_news_*.json / seo_speaker_*.json
  già scritti da admin.php:292-297,309 e speakers.php:158-159,172-173 (questa è la seo-cache; in C4
  ho mappato solo CHE viene scritta/invalidata, qui la STRATEGIA). È uno script one-shot o un
  endpoint? Gated?
- debug_seo.php: diagnostica SEO (cosa ispeziona).
- sitemap.php + robots.php (se esiste): dinamici via rewrite .htaccess (public/.htaccess:77-78 li
  serve da PHP) senza file fisici? baseUrl da HTTP_HOST? Stessa regola di visibilità di C4?
- meta/OG/JSON-LD lato client: c'è un SEO.tsx (SR-C3 cita SEO.tsx in News.tsx/Article.tsx)? Canonical
  parametrizzato o no (in SPW era sempre la homepage)?
- la cache di CONTENUTO news_*.json (mappata in C4) vs la seo-cache: distinguere i due livelli.

Ambito SR-C8 (RSS & Feed):
- feed_news_rss.php: feed RSS 2.0 delle news? Real-time o da cache? Content-Type, timezone, limite,
  channel title/description (hardcoded o da settings?). RIUSA la regola published_at<=now+status di
  C4? Formato pubDate (RFC822?), GUID/URN, enclosure per cover_image. EMETTE news.content o solo
  summary/excerpt (è il punto GOLD di SPW-C8: sicurezza-per-sottrazione)?
- feed_config.php: SR-C3 dice che ritorna {success, feed_url}. Cos'è? Configurazione di un feed
  esterno (Telegram?) o del feed RSS interno? C'è un legame col bot Telegram (SR-C1 cita
  TELEGRAM_BOT_TOKEN nei segreti)?
- podcasts: NON è qui la syndication degli episodi (in C4 ho mappato podcasts come record-link
  esterni); verificare se esiste un feed RSS dei podcast o se è solo news. Marca N/A il resto.
- routing del feed (URL pulito via .htaccess o grezzo /api/feed_news_rss.php?).

Fai così:
1. Ispeziona in modo microscopico i file di C7 e C8 (cita sempre percorso/file:linea).
2. Compila DUE card seguendo _TEMPLATE.md e salvale in
   _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C7-seo-prerendering.md e
   _cantiere-terza-edizione/mappatura/SitoRuntime/SR-C8-rss-feed.md
3. NON sconfinare: core/DB=C1, security/CORS=C2, frontend/client=C3, content/buste/slug=C4 (fatti),
   media/upload=C5 (fatto), editor/sanitizzazione=C6, newsletter/email/Telegram-invio=C9, admin UI=C12,
   EVOLUZIONE DB & INCIDENTI=C13. Puntatori nelle "Note / domande aperte" per il resto. Tieni C7 e C8
   distinti: prerendering/meta/sitemap/seo-cache in C7; il feed XML (RSS) in C8.
4. §6 di ENTRAMBE le card: confronto con SPW-C7 e SPW-C8 (Dynamic Rendering UA-sniff e il buco
   strip_tags vs DOMPurify; sitemap/robots dinamici; canonical non parametrizzato; RSS che NON emette
   content = sicurezza-per-sottrazione; SITE_URL assente in SR → baseUrl da HTTP_HOST). ATTENZIONE al
   ponte XSS-stored: in SR la sanitizzazione è render-time client (DOMPurify in Article.tsx, SR-C3/C6)
   — verificare se index.php/feed_news_rss.php ri-emettono news.content GREZZO (riaprendo il buco come
   in SPW) oppure no.

Criterio di STOP: ENTRAMBE le card in stato COMPLETATO (tutte le voci compilate o N/A).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (SR-C7 → ✅, SR-C8 → ✅)
- aggiungi DUE righe a _cantiere-terza-edizione/LOG.md (una per card, più recenti IN BASSO — attento
  all'ordine cronologico)
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta SR-C7 e SR-C8) e lo stato globale
- git add/commit/push (un commit per la coppia) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: SR-C9 (Newsletter & Email) del
  sito SitoRuntime, DA SOLA (vedi ROADMAP §0.1: C9, C12, C13 restano singole).
