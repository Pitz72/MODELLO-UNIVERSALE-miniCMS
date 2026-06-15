# Mappatura — SitoRuntime — C8: RSS & Feed Syndication

> **Stato:** COMPLETATO
> **Sessione:** 16 (coppia SR-C7 + SR-C8) · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `SitoRuntime/`)
> - `public/api/feed_news_rss.php` (**il feed RSS 2.0 delle news**, real-time dal DB — l'emettitore proprio del sito)
> - `public/api/rss.php` (**proxy server-side inbound** dei feed podcast esterni Spreaker/AzuraCast: NON genera un feed, lo *consuma*; cache su disco + stale fallback)
> - `public/api/feed_config.php` (dispenser admin-gated dell'URL del feed news: ritorna `{success, feed_url}`)
> - `src/utils/rss.ts` (parser/consumer client dei feed podcast: prova `rss.php` poi proxy pubblici di emergenza)
> - `src/api.ts:236-238` (`getFeedConfig` — fetch SENZA credentials, contratto `{success, feed_url}`)
> - `src/pages/Admin.tsx:105-110` (uso admin: carica `feed_url` e lo mostra in dashboard, gemello "Copia RSS" di SPW)
> - `public/.htaccess:74` (routing: `^api/` → `[L]`, nessuna rewrite per URL pulito del feed → si raggiunge GREZZO)
> - `public/api/db_credentials.php:21` (controprova: `TELEGRAM_BOT_TOKEN` esiste nei segreti ma **nessun file di C8 lo usa** → invio Telegram = C9)
> - **Controprova grep** (`feed_news_rss|feed_config|telegram` su `*.php`): l'unico consumatore noto di `feed_news_rss.php` è esterno; nessun binding Telegram nel codice del feed.

## 1. Cosa fa (sintesi narrativa)

In SitoRuntime "RSS & Feed" **non è un file solo** come in SPW (`rss.php` unico): è un **trittico di
file con tre ruoli opposti**, ed è l'osservazione centrale della card.

1. **`feed_news_rss.php` — l'emettitore PROPRIO del sito.** Genera, ad ogni richiesta, un **feed RSS 2.0
   real-time** con gli ultimi 20 articoli pubblicati (`feed_news_rss.php:18`). È il diretto omologo di
   `rss.php` di SPW-C8: include `db.php` (C1), forza `Europe/Rome`, manda `Content-Type:
   application/rss+xml`, apre un `<channel>` con titolo/descrizione **hardcoded** + `lastBuildDate` +
   `generator`, e per ogni articolo emette un `<item>` con `title`/`link`/`description`/`pubDate`/
   `guid`/`enclosure`.

2. **`rss.php` — un PROXY, non un generatore.** Qui il nome inganna: `rss.php` **non produce** alcun
   feed del sito. È un **proxy server-side inbound** che scarica i feed RSS dei **podcast esterni**
   (Spreaker, e l'AzuraCast `player.runtimeradio.com` che ospita gli Show Extra Nox/MONO) per aggirare
   la **mancanza di header CORS** dell'upstream (`rss.php:2-3`). Ha un'**allowlist di host** (no open
   proxy), una **cache su disco** `rss_<md5>.xml` (TTL 30′) e un **fallback stale** se l'upstream è giù.
   È il lato *consumo* della sindacazione podcast: i player del sito leggono i feed altrui **attraverso**
   questo proxy (`src/utils/rss.ts:8-14`).

3. **`feed_config.php` — il dispenser dell'URL del feed news.** Endpoint **gated `isAdmin()`** che
   ritorna `{success, feed_url}` dove `feed_url = <origin>/api/feed_news_rss.php` (`feed_config.php:17-20`).
   Serve alla dashboard (`Admin.tsx:106`) per mostrare all'admin l'indirizzo del feed da dare ai
   distributori — **gemello funzionale del bottone "Copia RSS" di SPW-C8**. Ma il suo commento promette
   più di quanto faccia (§4 GOLD: è *security theater*).

Quindi la geografia di C8 in SR è **frammentata** come quella di C4: l'emissione del feed news, il
consumo dei feed podcast esterni e la "configurazione" stanno in tre file con responsabilità diverse.
La **syndication dei podcast del network è esterna** (Spreaker/AzuraCast) e arriva *dentro* il sito via
proxy — non c'è un feed RSS *generato* dei podcast (i podcast nel DB sono record-link, SR-C4).

## 2. Pattern miniCMS rilevanti

- **Feed news real-time in un solo file, zero infrastruttura** (`feed_news_rss.php`): come SPW, il feed
  è generato ad ogni `GET /api/feed_news_rss.php` direttamente dal DB, nessun `.xml` materializzato,
  nessun cron. Un articolo pubblicato compare al primo refresh. Filosofia thin stack identica.
- **Proxy CORS come "thin stack inbound"** (`rss.php`): il problema "il browser non può leggere un feed
  cross-origin senza CORS" risolto con ~80 righe di PHP che fanno da intermediario same-origin, con
  cache e allowlist. È il **gemello inbound** del feed outbound: stesso sito, due direzioni di
  sindacazione. Pattern citabile ("quando il thin stack consuma feed altrui invece di produrne").
- **Allowlist di host + https-only nel proxy** (`rss.php:13-20`): `['www.spreaker.com', 'spreaker.com',
  'player.runtimeradio.com']`, scheme deve essere `https`, altrimenti `400 Feed URL not allowed`.
  Difesa anti-SSRF/open-proxy esplicita — *"nessun open proxy"* nel commento. (Il commit più recente
  `494046a` ha **esteso** questa allowlist a `player.runtimeradio.com` per gli Show Extra.)
- **Cache su disco con stale fallback** (`rss.php:22-33,60-73`): `rss_<md5(url)>.xml`, TTL 1800s,
  header `X-Cache: HIT|MISS|STALE`. Se l'upstream è irraggiungibile, **serve la cache scaduta** ("una
  cache scaduta è meglio di niente", `:61`) invece di fallire. Resilienza che SPW (feed solo proprio)
  non aveva bisogno di avere.
- **Escaping uniforme nel feed news** (`feed_news_rss.php:36,40,51`): `title`, `description`,
  `enclosure url` passano da `htmlspecialchars`; la `description` in più fa `strip_tags` prima
  dell'escape. Nessun campo dinamico finisce crudo nell'XML.
- **`lastBuildDate` + `generator` + namespace Atom dichiarato** (`feed_news_rss.php:23,29-30`): il feed
  SR è più "di galateo" di quello SPW (che non li aveva), anche se l'`atom:link rel="self"` resta
  **commentato** come TODO (`:32-33`).
- **Gating dell'URL-dispenser, non del feed** (`feed_config.php:8`): `isAdmin()` protegge *chi può
  leggere l'indirizzo del feed*, non il feed stesso. Pattern interessante (e fallace, §4).

## 3. Codice chiave (stralci con origine)

**Il feed news: stessa regola di visibilità INCOMPLETA di C7 (manca `status`), e — a differenza di SPW — EMETTE un preview di `content`** — `feed_news_rss.php:16-20,35-41`:

```php
$now = date('Y-m-d H:i:s');
// SUBSTRING() for MySQL (substr() was SQLite) — NB: filtra solo published_at<=now, NIENTE status (come index.php)
$stmt = $pdo->prepare("SELECT id, title, slug, summary, SUBSTRING(content, 1, 500) as content_preview, published_at, cover_image
                       FROM news WHERE published_at <= ? ORDER BY published_at DESC LIMIT 20");
$stmt->execute([$now]);
// …
foreach ($articles as $article) {
    $title = htmlspecialchars($article['title']);
    $descriptionText = $article['summary'] ?: $article['content_preview'] . '...';   // ← usa content se summary vuoto!
    $description = htmlspecialchars(strip_tags($descriptionText));                    // …ma strip_tags + escape totale
    $link = $FEED_URL . "/news/" . $article['slug'];
    $guid = $link;                                                                    // GUID = permalink
```

**Channel hardcoded + `FEED_URL` hardcoded (non host-derived)** — `feed_news_rss.php:7-9,25-30,59`:

```php
$FEED_TITLE = "Runtime Radio News";
$FEED_DESCRIPTION = "Ultime notizie da Runtime Radio";
$FEED_URL = "https://www.runtimeradio.com";          // ← hardcoded (≠ HTTP_HOST di sitemap/index)
// …
echo "    <lastBuildDate>" . date(DATE_RSS) . "</lastBuildDate>\n";
echo "    <generator>Runtime MiniCMS</generator>\n";
// …
echo "        <guid isPermaLink=\"true\">{$guid}</guid>\n";   // ← isPermaLink TRUE (≠ urn:false di SPW)
```

**Gestione errori: 500 esplicito (meglio del catch vuoto di SPW)** — `feed_news_rss.php:67-70`:

```php
} catch (PDOException $e) {
    http_response_code(500);
    echo "<error>Database Error</error>";   // segnala il guasto (ma solo PDOException, non Exception)
}
```

**Il proxy podcast: allowlist + https-only + cache + stale fallback** — `rss.php:13-20,27-33,60-73`:

```php
$allowedHosts = ['www.spreaker.com', 'spreaker.com', 'player.runtimeradio.com'];
if ($scheme !== 'https' || !in_array($host, $allowedHosts, true)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Feed URL not allowed']); exit;   // niente open proxy
}
// … cache HIT (TTL 1800s) → readfile + X-Cache: HIT …
if ($xml === false || $httpCode !== 200 || strpos(ltrim($xml), '<') !== 0) {
    if (file_exists($cacheFile)) {            // upstream giù → cache scaduta meglio di niente
        header('X-Cache: STALE'); readfile($cacheFile); exit;
    }
    http_response_code(502); /* … */
}
```

**Il dispenser admin-gated dell'URL — e la promessa che non mantiene** — `feed_config.php:3-20`:

```php
// Restituisce l'URL del feed RSS privato solo ad admin autenticati.
// Il token non viene mai esposto nel bundle JavaScript pubblico.   ← MA: nessun token, e il feed è PUBBLICO
require_once 'auth_utils.php';
if (!isAdmin()) { http_response_code(403); echo json_encode(['success'=>false,'error'=>'Forbidden']); exit; }
$origin = (… 'https' : 'http') . '://' . $_SERVER['HTTP_HOST'];
echo json_encode(['success' => true, 'feed_url' => $origin . '/api/feed_news_rss.php']);
```

**Il consumer client: prima il proxy del sito, poi proxy pubblici di emergenza** — `src/utils/rss.ts:8-29`:

```ts
const proxies = [
    // Strategy 1: proxy PHP del sito (F7) — same-origin, con cache server-side
    async (url) => { const res = await fetch(`/api/rss.php?url=${encodeURIComponent(url)}`); /* … */ },
    // Strategy 2/3: CodeTabs / AllOrigins — fallback di emergenza (proxy PUBBLICI di terzi)
    async (url) => fetch(`https://api.codetabs.com/v1/proxy?quest=${encodeURIComponent(url)}`),
    async (url) => fetch(`https://api.allorigins.win/get?url=${encodeURIComponent(url)}`),
];
```

## 4. Problemi riscontrati & soluzioni

- **GOLD — `feed_config.php` è *security theater*: gata un URL pubblico promettendo un "feed privato con
  token".** Il commento (`feed_config.php:3-4`) recita *"Restituisce l'URL del feed RSS privato solo ad
  admin autenticati. Il token non viene mai esposto nel bundle JavaScript pubblico."* Ma:
  - **Non esiste alcun token.** Il `feed_url` ritornato è `<origin>/api/feed_news_rss.php` (`:19`),
    nudo, senza query string segreta.
  - **Il feed è completamente pubblico.** `feed_news_rss.php` **non include** `auth_utils.php`, non
    chiama `isAdmin()`/`isLoggedIn()`: chiunque, senza login, può `GET /api/feed_news_rss.php` e leggere
    tutte le news. Il gate `isAdmin()` di `feed_config.php` protegge *l'atto di scoprire un URL che è
    comunque pubblico e indovinabile*. La "privatezza" è inesistente.
  - → Box problemi/soluzioni "il lucchetto sulla porta accanto": gatare il *dispenser* di un URL non
    rende privato l'*endpoint* che l'URL raggiunge. Probabile fossile di un'intenzione mai realizzata
    (un feed news *autenticato* con token per il bot Telegram — coerente col `TELEGRAM_BOT_TOKEN` nei
    segreti di SR-C1 — che non è mai stato costruito). Alto valore didattico.

- **GOLD — Il feed news EMETTE `content`, a differenza di SPW (che non lo tocca) — ma in modo sicuro.**
  SPW-C8 era "sicuro per sottrazione": `rss.php` non emetteva mai `articles.content` (colonna nemmeno
  stampata), `description = excerpt` escapato. SitoRuntime **rompe la sottrazione**: quando `summary` è
  vuoto, la `<description>` ripiega sui **primi 500 caratteri di `content`** (`feed_news_rss.php:18,39`).
  Quindi il feed **è il quarto emettitore** del contenuto utente dopo React+DOMPurify (C6), il prerender
  crawler (C7) e — qui — il feed. **MA** lo emette con **`strip_tags` + `htmlspecialchars`** (`:40`):
  - `strip_tags` rimuove **tutti** i tag (no allowlist, a differenza del prerender C7), `htmlspecialchars`
    trasforma il resto in entità → la `description` è **testo puro escapato**, nessuna esecuzione in un
    reader RSS. **Sicuro.**
  - Quadro completo dei **QUATTRO emettitori** dello stesso `content` in SitoRuntime (gold per il libro):
    | Emettitore | Cosa emette | Sanitizzazione | Esito |
    |---|---|---|---|
    | React `Article.tsx` (C6) | `content` pieno | **DOMPurify** (tag+attributi) | ✅ pieno e sicuro |
    | Prerender crawler `index.php:318` (C7) | `content` pieno | `strip_tags` **allowlist** (solo tag) | ⚠️ sicuro sui tag, **buco sugli attributi** |
    | Feed news `feed_news_rss.php:40` (C8) | **preview 500c** di `content` (se manca summary) | `strip_tags` (tutti i tag) + `htmlspecialchars` | ✅ sicuro (testo escapato, lossy) |
    | (newsletter/email) | da verificare | — | → **C9** |
  - **Morale:** SR ha **quattro** render-path dello stesso dato con **quattro** policy diverse, nessuna
    condivisa. Il feed è sicuro non *per sottrazione* (come SPW) ma *per escape totale*: scelta diversa,
    esito ugualmente sicuro. Rafforza la tesi C6/C7: serve una sanitizzazione server-side condivisa.
    **Chiude il ponte XSS per C8** (il feed non apre il buco), lascia aperto **solo C9**.

- **Stessa regola di visibilità INCOMPLETA di C7: il feed pubblica le bozze.** `feed_news_rss.php:18`
  filtra **solo** `published_at <= ?`, **senza** `AND (status='published' OR status IS NULL)` (la regola
  di C4). Identico al buco di `index.php`/`sitemap.php` (SR-C7 §4): una bozza con `published_at` passato
  **compare nel feed RSS** pur essendo nascosta nella lista pubblica `news.php`. Terzo file (dopo index
  e sitemap) che dimentica il filtro `status`. → ponte C4/C7, stesso box "due idee di 'pubblico'".

- **GUID = permalink con `isPermaLink="true"` → regressione rispetto a SPW.** `feed_news_rss.php:43,59`
  usa il **link** come GUID (`isPermaLink="true"`). SPW-C8 aveva scelto deliberatamente
  `urn:simonepizzi:article:<id>` con `isPermaLink="false"` proprio per **non** ri-pubblicare un articolo
  quando cambia slug/categoria (anti-doppione sui consumatori, es. bot Telegram). In SR, **un cambio
  slug cambia il GUID** → i sistemi di integrazione vedono l'articolo come **nuovo** e lo ri-pubblicano.
  È il problema che SPW aveva risolto e SR si re-introduce. → Box "il GUID che ripubblica" (ponte SR-C7
  per la stabilità dell'identità: nota che SR **non** ha nemmeno i Redirect 301 di SPW).

- **`FEED_URL` hardcoded `https://www.runtimeradio.com`** (`feed_news_rss.php:9`): a differenza di
  `sitemap.php`/`index.php` (host-derived), il feed hardcoda il dominio `.com` **con `www`**. Su
  staging o su `runtimeradio.it`, i `<link>`/`<guid>` degli item puntano al dominio sbagliato. Stessa
  incoerenza host-derived vs hardcoded notata in SR-C7 §4 (lato `SEO.tsx`).

- **`enclosure` MIME indovinato a metà** (`feed_news_rss.php:48-51`): default `image/jpeg`, con un
  `if strpos('.png')` per il PNG. Ma in SR-C5 l'upload converte le cover in **WebP**: una cover `.webp`
  viene dichiarata `image/jpeg` → reader pignoli rifiutano la miniatura. Meglio di SPW (che hardcodava
  sempre jpeg), ma ancora incompleto. Fix: derivare il type dall'estensione reale (incluso webp).

- **Errore gestito solo per `PDOException`, non per `Exception`** (`feed_news_rss.php:67`): il `catch`
  intercetta `PDOException` → `http 500 + <error>` (**meglio** del catch vuoto-200 di SPW). Ma un errore
  non-PDO (es. problema in `db.php`) non è catturato e produrrebbe un 500 PHP grezzo. Copertura parziale.

- **Il consumer client cade su proxy pubblici di terzi** (`src/utils/rss.ts:15-28`): se `rss.php`
  fallisce, il client ritenta via `api.codetabs.com` e `api.allorigins.win` — **proxy pubblici esterni**
  a cui passa l'URL del feed podcast. Per feed Spreaker pubblici il rischio è basso (URL già pubblici),
  ma è una **dipendenza da terzi non dichiarata** che bypassa l'allowlist del proxy del sito. → nota di
  resilienza-vs-controllo.

- **Routing grezzo (come SPW): nessun URL pulito per i feed.** `.htaccess:74` manda `^api/` ai file PHP
  (`[L]`) senza rewrite `feed.xml`→`feed_news_rss.php` (a differenza di `sitemap.xml`→`sitemap.php` di
  C7). Sia il feed news sia il proxy si raggiungono agli URL grezzi `/api/feed_news_rss.php` e
  `/api/rss.php?url=…`. Stessa asimmetria SEO-curata/feed-grezzo di SPW-C8.

## 5. Estetica / UX (moderna ma funzionale)

- **Dashboard admin che mostra il feed URL** (`Admin.tsx:105-110`): al login l'admin carica
  `getFeedConfig()` e memorizza `feedUrl` per mostrarlo in pannello — gemello del "Copia RSS" di SPW,
  pensato per **consegnare l'indirizzo del feed ai distributori** senza scriverlo a mano. Degradazione
  graziosa: se la chiamata fallisce, `console.error` e si prosegue (`:108-109`).
- **`X-Cache: HIT|MISS|STALE` nel proxy** (`rss.php:30,65,78`): header diagnostico a tre stati che
  rende visibile (a chi ispeziona) se il feed podcast arriva da cache fresca, è stato appena scaricato,
  o è una copia scaduta servita perché l'upstream è giù. Micro-trasparenza operativa.
- **Player podcast resiliente** (`rss.ts`): tre strategie di fetch in cascata + parsing che gestisce sia
  i tag iTunes (`itunes:image`/`itunes:duration`/`itunes:author`) sia quelli standard → i feed Spreaker
  "ricchi" vengono resi bene. È il lato UX del consumo podcast (dettaglio player = C3/pagine, qui solo
  annotato perché spiega *perché* esiste il proxy).

## 6. Differenze rispetto agli altri siti

Il confronto con **SPW-C8** è il cuore della card.

| Aspetto | SimonePizziWebSite (SPW-C8) | SitoRuntime (questa card) |
|---|---|---|
| **Geografia** | **un file** `rss.php` (solo feed proprio) | **tre file**: `feed_news_rss.php` (emette), `rss.php` (proxy inbound), `feed_config.php` (dispenser) |
| **Feed news** | RSS 2.0 real-time, 50 item | RSS 2.0 real-time, 20 item, + `lastBuildDate`/`generator` |
| **Emette `content`?** | **NO** (solo `excerpt`, sicuro per sottrazione) | **SÌ** (preview 500c se manca summary) ma `strip_tags`+`htmlspecialchars` → sicuro per escape |
| **GUID** | `urn:…:article:<id>` `isPermaLink="false"` (anti-ripubblicazione) | **permalink** `isPermaLink="true"` → **ripubblica al cambio slug** (regressione) |
| **`baseUrl`** | da `HTTP_HOST` | **hardcoded** `https://www.runtimeradio.com` |
| **Gestione errori** | `catch` vuoto → feed parziale con **HTTP 200** | `catch PDOException` → **HTTP 500 + `<error>`** (meglio) |
| **`enclosure` MIME** | hardcoded `image/jpeg` | indovinato (jpeg/png), ancora niente webp |
| **Proxy feed esterni** | **assente** | `rss.php` proxy Spreaker/AzuraCast con allowlist+cache+stale (consumo podcast) |
| **"Feed privato"** | bottone "Copia RSS" onesto | `feed_config.php` gata l'URL ma il feed è pubblico (**security theater**) |
| **Podcast** | N/A (no podcast) | syndication **esterna** (proxata), nessun feed podcast *generato* |
| **URL pulito** | no (`/api/rss.php` grezzo) | no (`/api/feed_news_rss.php` grezzo) — identica asimmetria vs sitemap |

Sintesi: SR-C8 è **più ricco e più frammentato** di SPW-C8. Aggiunge un **proxy inbound** (`rss.php`)
che SPW non ha — perché SR consuma feed podcast altrui (Spreaker/AzuraCast) — e un **dispenser gated**
(`feed_config.php`) che però è solo apparenza di privatezza. Sul feed proprio, SR fa **due scelte
peggiori** di SPW (emette `content` — anche se in modo sicuro — e usa un GUID instabile che
ripubblica) e **due migliori** (errore HTTP 500 esplicito, `lastBuildDate`/`generator`). Dove SPW è
"feed minimale ma rigoroso", SR è "feed più completo ma con qualche regressione".

Per **DISINTELLIGENZA/FDCA** (festival, SQLite) la ROADMAP non prevede un C8 dedicato → feed
probabilmente assente o minimale: termine di paragone "minimo".

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **Il trittico RSS** (emettitore + proxy inbound + dispenser) | Cap. "Sindacazione thin stack: produrre, consumare, configurare" (vs il file unico di SPW) |
| **Il proxy CORS server-side** (`rss.php` con allowlist+cache+stale) | Cap./box "consumare feed altrui senza CORS: il proxy del thin stack" (nuovo, SR non-in-SPW) |
| **`feed_config.php` security theater** (gatare l'URL di un endpoint pubblico) | Box problemi/soluzioni "il lucchetto sulla porta accanto" (**altissimo valore**) |
| **I QUATTRO emettitori dello stesso `content`** (DOMPurify / strip_tags-allowlist / strip_tags+escape / newsletter) | Box "una sanitizzazione, quattro render-path" (**chiude il ponte C6→C7→C8**, ponte SPW) |
| **Sicurezza per escape vs per sottrazione** (SR emette content escapato, SPW non lo emette) | Box "due modi di rendere sicuro un feed" |
| **Il GUID che ripubblica** (`isPermaLink=true` vs urn stabile di SPW) | Box "l'identità instabile di un articolo nel feed" (ponte SR-C7) |
| **La regola `status` dimenticata anche nel feed** | (stesso box di SR-C7) "due idee di 'pubblico'" (ponte C4) |
| **Errore HTTP 500 esplicito vs catch silenzioso** | Box "errori che il client vede / non vede" (contrasto con SPW-C8) |
| **Resilienza a cascata** (proxy sito → proxy pubblici di terzi) | Box "tre proxy in fila: resilienza contro controllo" |

## 8. Note / domande aperte

- **Ponte di sicurezza C6→C7→C8: chiuso per il feed.** Il feed news (`feed_news_rss.php:40`) emette un
  preview di `content` ma con `strip_tags`+`htmlspecialchars` (escape totale) → **non** è un vettore
  XSS-stored (a differenza del prerender C7 che lascia il buco sugli attributi). Resta aperto **solo
  C9 (Newsletter & Email)**: è l'ultimo possibile emettitore di `news.content`; lì il rischio sarebbe
  più alto (HTML email renderizzato in un client di posta). **Verificare in C9** se la newsletter
  inietta `content` e con quale sanitizzazione. (È l'unità della prossima sessione.)
- **Telegram:** `TELEGRAM_BOT_TOKEN` esiste nei segreti (SR-C1, `db_credentials.php:21`) e
  `isCrawler()` lista `TelegramBot`, ma **nessun file di C8 usa il token**: l'invio Telegram (e il
  consumo del feed da parte di un bot) è dominio **C9**. `feed_news_rss.php` è *ciò che* un bot esterno
  consumerebbe; il "token" nel commento di `feed_config.php` è probabilmente il fossile di
  un'integrazione bot mai costruita. Puntatore a C9.
- **Puntatori ad altri cluster** (annotati, NON mappati qui):
  - `Database::connect()` / singleton PDO / timezone `Europe/Rome` (`feed_news_rss.php:3,12-13`) → **C1**.
  - Schema `news` e regola `status`/`published_at` → **C4** (qui solo consumati; il filtro `status`
    manca, come in C7).
  - `cover_image` come stringa URL + conversione WebP (che rende sbagliato `image/jpeg`) → **C5**.
  - `podcasts` come record-link (la *generazione* di un feed podcast non esiste; si **consumano** i feed
    Spreaker/AzuraCast via `rss.php`) → **C4** per i record, qui per il consumo.
  - `getFeedConfig` lato client (fetch senza credentials, contratto `{success,feed_url}`) → già in **C3**;
    qui mappato l'endpoint server.
  - Player podcast / parsing iTunes / pagine ShowExtra → **C3** (UI) — qui solo il proxy che li alimenta.
  - Gate `isAdmin` di `feed_config.php` → meccanica in **C2**; qui osservato il *cosa* protegge.
- **Assenze confermate:** nessun feed **podcast generato** (solo proxato); nessun `content:encoded`
  (il feed news dà solo description); nessun URL pulito per i feed; nessun token reale dietro
  `feed_config.php`; nessun `atom:link rel="self"` (commentato come TODO).
- **Nessuna credenziale/segreto** stampato nei file di C8 (il `TELEGRAM_BOT_TOKEN` è citato solo come
  controprova: non usato qui).
- Versione di riferimento: sito **2.9.13**; il commit più recente del repo è proprio
  `494046a fix(rss): v2.9.13 — whitelist proxy estesa a player.runtimeradio.com` (riguarda `rss.php`,
  il proxy podcast).
