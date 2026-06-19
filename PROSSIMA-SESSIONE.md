# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟨 FASE 2 (SINTESI) in corso. S1-C1 → S1-C7 ✅ COMPLETATE (7/14). S1-C6 ed S1-C7 sono state
> accorpate in una sessione. Questa è l'OTTAVA scheda di sintesi: **S1-C8 RSS & Feed**.
> Ordine confermato: S1 → S2 → S3 → S4 (nessuna deviazione).

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md, _cantiere-terza-edizione/LOG.md e
_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md per il contesto.

STATO: FASE 1 (mappatura) CONCLUSA — 4 siti, 34 card, copertura COMPLETA. FASE 2 (SINTESI) in corso:
**7/14 schede S1 completate** (S1-C1 Backend Core ✅, S1-C2 Security & Auth ✅, S1-C3 Frontend Bridge
✅, S1-C4 Content APIs ✅, S1-C5 Media & Upload ✅, S1-C6 Editor ✅, S1-C7 SEO & Prerendering ✅).
Metodo: UNA scheda tematica cross-sito per sessione (eccezionalmente DUE se unite da un filo, come
C6+C7). Fonde i 2-3 trattamenti per-sito di un cluster in UNA visione comparata (pattern comune +
varianti per sito in tabella unica + GOLD + mappa→capitoli). Fonti = card di mappatura (specialmente i
§6). NON si rilegge il codice sorgente. Template: `_cantiere-terza-edizione/sintesi/_TEMPLATE-SCHEDA.md`;
modelli già fatti: `S1-C1` … `S1-C7` (seguine struttura e livello di dettaglio).

UNITÀ DI QUESTA SESSIONE: **S1-C8 — Scheda tematica cross-sito "RSS & Feed Syndication"**.
Fonti primarie: SPW-C8, SR-C8, DIS-C8. Da consolidare (spunti dai §6 già scritti):
- **CHIUDE il "quadro dei 4 emettitori del content"** (aperto in S1-C6, sviluppato in S1-C7): editor/
  render (DOMPurify) → prerender (strip_tags-allowlist, buco attributi) → **RSS (questa scheda)** →
  newsletter (S1-C9). Tesi chiave del feed: è l'emettitore PIÙ sicuro perché o NON emette il content o
  lo ESCAPA totalmente. SPW: rss.php NON emette articles.content (description=excerpt+htmlspecialchars)
  = "sicuro per sottrazione"; SR: feed_news_rss.php EMETTE content (preview 500c SUBSTRING) ma con
  strip_tags+htmlspecialchars (escape totale) = "sicuro per escape"; DIS: feed.php è PODCAST (non
  emette news.content), escape parziale (description grezza in CDATA).
- **Struttura del feed:** SPW = file UNICO rss.php (RSS 2.0 news real-time, GUID urn:...:article:ID
  isPermaLink=false anti-ripubblicazione); SR = TRITTICO (feed_news_rss.php EMETTE news + rss.php è
  PROXY INBOUND dei feed podcast esterni Spreaker/AzuraCast con allowlist host + cache stale + no
  open-proxy + feed_config.php dispenser admin-gated dell'URL); DIS = feed.php = feed PODCAST RSS 2.0 +
  iTunes (NON news: DIS non sindaca le news), canale da settings podcast_* MAI POPOLATI → default
  hardcoded.
- **GOLD per sito:** SPW = GUID urn anti-doppione (vs ripubblicazione bot Telegram), enclosure
  type=image/jpeg hardcoded vs cover WebP, pubDate instabile su published_at NULL, catch vuoto = feed
  troncato con HTTP 200; SR = (1) feed_config.php SECURITY THEATER (promette "feed privato con token"
  ma ritorna URL di endpoint PUBBLICO senza token = fossile integrazione bot Telegram mai costruita),
  (2) GUID=permalink isPermaLink=true (ripubblica al cambio slug, regressione vs urn:false di SPW),
  (3) catch PDOException→500+<error> (meglio del catch-vuoto-200 di SPW); DIS = commenti "ragionamento
  ad alta voce" più estremi del repo (feed.php:26-34 l'autore si chiede se la tabella esista, "bad
  practice on GET", "I'll assume it exists") = ritratto di codebase AI-assistito non ripulito, GUID=
  audio_url instabile, enclosure length=0 hardcoded.
- **Regola visibilità (filo da S1-C4/C7):** la regola status dimenticata anche nei feed (bozze nel
  feed) in SR; SPW pubDate su published_at NULL; verificare per-sito.
- **Telegram fossile (ponte S1-C1):** GUID urn di SPW è parallelo ai 301 .htaccess per il bot Telegram;
  in SR il TELEGRAM_BOT_TOKEN è fossile (bot manuale via copia-URL), feed_config.php ne è il relitto.

Fai così:
1. Scrivi la scheda in `_cantiere-terza-edizione/sintesi/S1-C8-rss-feed.md` seguendo
   `_TEMPLATE-SCHEDA.md` (0 una-frase · 1 pattern comune · 2 tabella varianti UNICA e deduplicata · 3
   GOLD/box · 4 mappa→capitoli · 5 scarti/dedup). La tabella comparativa va scritta UNA volta, pulita.
   COMPLETA esplicitamente la "mappa dei 4 emettitori del content" (DOMPurify/strip_tags-allowlist/
   strip_tags+escape/newsletter) come tabella o box riassuntivo — è il valore trasversale di questa scheda.
2. Mappa esplicitamente → capitoli esistenti: soprattutto **CAP 12 (RSS Feed & Syndication)**, con
   ponti a CAP 8/11 (gli altri emettitori del content), CAP 10 (il proxy inbound di SR e l'anti-open-
   proxy), CAP 13 (Newsletter, l'ultimo emettitore). Segnala eventuali CORREZIONI al testo attuale
   (come fatto per CAP 3/10/6/9/7/8/11 nelle schede precedenti).
3. Aggiorna `_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md` (S1-C8 → ✅, contatore 8/14).

Criterio di STOP: scheda S1-C8 in stato COMPLETATO (pattern + varianti + GOLD + mappa capitolo).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna `_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md` (S1-C8 → ✅)
- aggiorna `_cantiere-terza-edizione/ROADMAP.md` (spunta S1-C8 in §4, aggiorna §7 stato globale)
- aggiungi UNA riga a `_cantiere-terza-edizione/LOG.md` (più recente IN BASSO)
- git add/commit/push (un commit) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md, sia root sia in _cantiere-terza-edizione/) con la
  prossima scheda: **S1-C9 (Newsletter & Email)** — fonti SPW-C9, SR-C9, DIS-C9 (double opt-in +
  unsubscribe_token SPW / PHPMailer SMTP + un solo token SR / mail() nativa senza double opt-in né
  token DIS; CHIUDE definitivamente il quadro dei 4 emettitori; rate-limit anti-mail-bombing, header
  injection, invio sincrono). Valuta se accorpare C9 con C13 o lasciarla sola.

Nota: scheda S1-C8 = SOLA (non accorpata). L'accorpamento C6+C7 è stato eccezionale (filo "content
grezzo"); valuta caso per caso solo quando due cluster sono genuinamente uniti da un filo tematico.
