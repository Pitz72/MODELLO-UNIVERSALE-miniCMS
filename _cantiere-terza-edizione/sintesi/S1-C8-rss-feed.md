# Scheda di Sintesi — S1-C8 — RSS & Feed Syndication

> **Stato:** COMPLETATO
> **Cluster FASE 2:** S1-C8 · **Data:** 2026-06-19 · **Commit:** _(in corso)_
> **Fonti (card di mappatura, in particolare i §6):** SPW-C8, SR-C8, DIS-C8 (+ FDCA-DIFF: backend = DIS, feed podcast ereditato → fuori scala)
> **Capitoli del libro toccati:** CAP 12 (RSS Feed & Syndication) — principale · ponti a CAP 8/11 (gli altri emettitori del `content` → da S1-C6/C7), CAP 10 (il proxy inbound di SR e l'anti-open-proxy/SSRF), CAP 13 (Newsletter, l'ultimo emettitore → S1-C9), CAP 9 (regola di visibilità) → vedi §4

---

## 0. In una frase
Il feed è **l'emettitore più sicuro del `content`** — perché o **non lo emette** (SPW: solo `excerpt`;
DIS: feed podcast, non tocca le news) o lo **escapa totalmente** (SR: `strip_tags`+`htmlspecialchars`) —
e così **chiude il "quadro dei quattro emettitori"** aperto in S1-C6 e sviluppato in S1-C7: il buco
XSS-attributi del prerender qui **non si riapre**. Ma sotto questa convergenza sulla sicurezza i tre siti
divergono su tutto il resto — **un file vs un trittico vs un feed podcast** — e sulla disciplina del
GUID si vede una **regressione storica** (SPW lo risolve con un URN stabile, SR e DIS lo re-introducono).

## 1. Il pattern comune — la filosofia "thin stack" su questa lente

Sotto le differenze, l'emissione del feed nei tre siti condivide cinque tratti.

**1) Un feed real-time in un solo file, zero infrastruttura.** Nessun cron, nessun `.xml`
materializzato su disco, nessuna libreria di serializzazione: un `GET` su un endpoint PHP
(`rss.php` / `feed_news_rss.php` / `feed.php`) interroga il DB e `echo`-a l'XML al volo. Un contenuto
pubblicato compare nel feed **al primo refresh**. È la stessa filosofia "la freschezza è gratis se
generi al volo" già vista in S1-C7 per `sitemap.php`/`robots.php`.

**2) Escaping disciplinato di (quasi) ogni campo dinamico.** `title`, `link`, `enclosure url` passano
sempre da `htmlspecialchars` prima di finire nell'XML: nessun campo "ovvio" finisce crudo nel feed.
La cura è uniforme — *tranne* su un singolo campo per sito (la `description`/`CDATA`), che è esattamente
dove si gioca la sicurezza (§3).

**3) Il fuso forzato nel singolo endpoint, dove serve.** I siti che emettono news (SPW, SR) ri-chiamano
`date_default_timezone_set('Europe/Rome')` dentro il file del feed, invece di fidarsi del timezone di
`db.php` (S1-C1): ogni file che confronta date col DB si auto-protegge dal server in fuso sbagliato.
È il pattern "difesa ridondante sul fuso" già visto in S1-C4/C7.

**4) `pubDate` in RFC-822 via `DATE_RSS`.** Tutti convertono la data di pubblicazione con
`date(DATE_RSS, strtotime(...))` — il formato che RSS 2.0 pretende (`Mon, 24 Mar 2026 10:00:00 +0100`),
mai ISO 8601.

**5) Routing grezzo, nessun URL pulito.** A differenza di `sitemap.xml`→`sitemap.php` (S1-C7), nessun
sito fa una rewrite `feed.xml`→…: il feed si raggiunge sempre all'URL **grezzo** del file PHP
(`/api/rss.php`, `/api/feed_news_rss.php`, `/api/feed.php`). Piccola asimmetria con la cura SEO degli
altri asset, identica in tutti e tre.

A questi tratti si aggiunge il filo che entra da S1-C6→C7: il `content` salvato grezzo, sanitizzato solo
nel render React e ri-emesso col buco `strip_tags` nel prerender, **viene riletto anche qui**. *Come* il
feed tratta quel campo decide se il buco XSS si riapre — ed è la spina dorsale della scheda. La risposta,
stavolta, è confortante: **nessuno dei tre feed riapre il buco** (§3, il quadro dei quattro emettitori).

## 2. Le varianti per sito (tabella unica, deduplicata)

| Asse | SimonePizziWebSite | SitoRuntime | DISINTELLIGENZA | *(FDCA)* |
|---|---|---|---|---|
| **Cosa sindaca** | **news** (RSS 2.0) | **news** (+ proxy podcast esterni) | **solo podcast** (RSS 2.0 + iTunes) | = DIS |
| **Geografia dei file** | **un file** `rss.php` | **trittico**: `feed_news_rss.php` (emette) + `rss.php` (proxy inbound) + `feed_config.php` (dispenser) | **un file** `feed.php` | = DIS |
| **Emette `content`?** | **NO** — solo `excerpt` (`htmlspecialchars`) | **SÌ** — preview 500c (`SUBSTRING`) se manca `summary` | **NO** — è feed podcast, non tocca le news | = DIS |
| **Sicurezza del feed** | **per sottrazione** (non emette il campo pericoloso) | **per escape totale** (`strip_tags`+`htmlspecialchars`) | **per sottrazione** (non emette news) | = DIS |
| **Buco XSS riaperto?** | **no** | **no** | **no** (caveat: `description` podcast grezza in CDATA, admin-authored) | = DIS |
| **GUID** | `urn:simonepizzi:article:<id>` `isPermaLink="false"` (**anti-ripubblicazione**) | **permalink** `isPermaLink="true"` → ripubblica al cambio slug | **`audio_url`** → cambia se l'audio si sposta (il meno stabile) | = DIS |
| **`baseUrl`** | da `HTTP_HOST` (host-derived) | **hardcoded** `https://www.runtimeradio.com` | da `HTTP_HOST` | = DIS |
| **Regola visibilità (`status`)** | **riusa** `status='published' AND published_at<=now` | **dimenticata**: solo `published_at<=now` → **bozze nel feed** | **N/A** (i podcast non hanno `status`; `SELECT *` senza WHERE) | = DIS |
| **Config canale** | hardcoded + TODO "dai settings" (mai arrivato) | hardcoded (`FEED_TITLE`/`FEED_URL`) | `settings.podcast_*` lette ma **mai popolate** → default hardcoded | = DIS |
| **Gestione errori** | `catch` **vuoto** → feed troncato con **HTTP 200** | `catch PDOException` → **HTTP 500 + `<error>`** (meglio) | `catch` vuoto → feed senza item (channel emesso) | = DIS |
| **`enclosure` MIME** | hardcoded `image/jpeg` | indovinato (jpeg/png), **niente webp** | `audio/mpeg` + `length="0"` hardcoded | = DIS |
| **"Galateo" RSS** | RSS 2.0 puro (no `lastBuildDate`/`generator`/`atom:self`) | `lastBuildDate`+`generator` (atom:self **commentato**) | iTunes completo (`owner`/`category`/`image`) | = DIS |
| **Proxy feed inbound** | **assente** | `rss.php`: allowlist host + https-only + cache + stale fallback (anti-open-proxy/SSRF) | assente | = DIS |
| **"Feed privato"** | bottone admin "Copia RSS" (onesto) | `feed_config.php` gata l'URL ma il feed è **pubblico** (*security theater*) | nessuno | = DIS |

**Lettura della tabella.** Su un asse — **la sicurezza** — i tre siti **convergono**: nessuno dei feed
è un vettore XSS-stored, ma per **tre strade diverse**. SPW e DIS sono sicuri *per sottrazione* (non
emettono il campo pericoloso: SPW dà solo l'`excerpt`, DIS è un feed podcast e non tocca le news); SR è
sicuro *per escape totale* (emette una preview del `content`, ma `strip_tags` toglie **tutti** i tag e
`htmlspecialchars` neutralizza il resto). È l'opposto del prerender di S1-C7, dove `strip_tags`-allowlist
lasciava passare gli attributi: qui SR non usa l'allowlist, quindi nessun buco. **Il feed è il punto in
cui il quadro dei quattro emettitori si chiude bene** (§3).

Su **tutti gli altri assi** invece i siti divergono, e lo spettro è "un file → un trittico → un feed
podcast". SPW è il **feed news minimale ma rigoroso** (un file, GUID stabile, regola di visibilità
riusata, config in debito ma onesta). SR è il **più ricco e più frammentato**: aggiunge un **proxy
inbound** che SPW non ha (perché consuma feed podcast altrui Spreaker/AzuraCast) e un **dispenser gated**
che è solo apparenza di privatezza — ma sul feed proprio fa due scelte *peggiori* di SPW (emette il
`content`, anche se in sicurezza; GUID instabile) e due *migliori* (errore HTTP 500 esplicito,
`lastBuildDate`/`generator`). DIS è il **più specializzato e ridotto**: niente RSS di news, solo un feed
**podcast iTunes** che gira sui default perché i suoi settings non sono mai popolati. E sulla
**disciplina del GUID** la tabella racconta una **regressione nel tempo**: SPW aveva risolto il
problema della ripubblicazione con un `urn:` stabile; SR torna al permalink, DIS scende fino all'URL del
file audio — il meno stabile di tutti.

**FDCA è fuori scala:** fork di DIS col backend PHP byte-identico → eredita `feed.php` (stesso feed
podcast, stessi default hardcoded, stesso GUID instabile). Caso fork, nessun pattern nuovo.

## 3. GOLD & box problemi-soluzioni

- **Il quadro dei QUATTRO emettitori del `content` — qui si chiude** — *(cross-sito; salda
  S1-C6→C7→C8, ponte a S1-C9)* — è il GOLD portante e il valore trasversale della scheda. Lo stesso
  campo (`content`, salvato grezzo, S1-C6) viene riletto e ri-emesso da **quattro** punti, ciascuno con
  **una policy diversa e nessuna condivisa**. Il feed è il terzo/quarto e — a differenza del prerender —
  **non riapre il buco**:

  | # | Emettitore | Cosa emette del `content` | Sanitizzazione | Esito |
  |---|---|---|---|---|
  | 1 | **Render React** (`SingleArticle`/`Article`/`NewsDetail`, S1-C6) | `content` pieno | **DOMPurify** (tag + attributi + hook iframe) — *DIS ne è privo* | ✅ pieno e sicuro (⚠️ scoperto in DIS) |
  | 2 | **Prerender crawler** (`index.php`, S1-C7) | `content` pieno | `strip_tags` **allowlist** (solo tag) | ⚠️ sicuro sui tag, **buco sugli attributi** (SPW, SR; DIS immune) |
  | 3 | **Feed RSS** (`rss.php`/`feed_news_rss.php`/`feed.php`, **questa scheda**) | **niente** (SPW/DIS) · **preview 500c** (SR) | — / `strip_tags`+`htmlspecialchars` (escape totale) | ✅ **sicuro** (sottrazione o escape) |
  | 4 | **Newsletter / email** (S1-C9) | → da consolidare in S1-C9 | → S1-C9 | → S1-C9 |

  La riga 3 è il cuore: **il feed è sempre l'emettitore più sicuro**, per sottrazione (SPW non emette
  `content`, DIS non emette news) o per escape totale (SR). La lezione resta quella di S1-C6/C7
  rovesciata di segno: *quando la difesa XSS vive in un solo render, ogni altro emettitore deve
  ri-sanitizzare* — e il feed dimostra che farlo (o non emettere affatto) **funziona**. → Box "Una
  sanitizzazione, quattro render-path: dove il feed chiude il quadro" (**altissimo valore**, perno
  S1-C6/C7/C9).

- **Sicurezza per sottrazione vs sicurezza per escape: due modi di rendere sicuro un feed** —
  *(SPW/DIS vs SR)* — SPW non emette mai `articles.content` (colonna SELECTata ma mai `echo`-ata; la
  `<description>` usa l'`excerpt` escapato) → **sicuro per sottrazione**. SR *rompe* la sottrazione
  (quando `summary` è vuoto ripiega sui primi 500 caratteri del `content`) ma lo neutralizza con
  `strip_tags`+`htmlspecialchars` → **sicuro per escape**. Stesso esito, filosofie opposte. Il prezzo è
  diverso: la sottrazione è *lossy ma robusta* (non c'è campo pericoloso da sbagliare), l'escape è
  *più informativo ma fragile* (basta cambiare `strip_tags` in un `strip_tags`-allowlist — come nel
  prerender — per riaprire il buco). → Box "Due modi di rendere sicuro un feed: non emettere o escapare".

- **`feed_config.php` è *security theater*: il lucchetto sulla porta accanto** — *(SR)* — il commento
  promette *"l'URL del feed RSS privato solo ad admin… il token non viene mai esposto nel bundle"*. Ma
  **non esiste alcun token**, e il `feed_url` ritornato è `<origin>/api/feed_news_rss.php` — un endpoint
  **completamente pubblico** (`feed_news_rss.php` non include nemmeno `auth_utils.php`). Il gate
  `isAdmin()` protegge *l'atto di scoprire un URL che è comunque pubblico e indovinabile*: gatare il
  *dispenser* di un URL non rende privato l'*endpoint* che l'URL raggiunge. È quasi certamente il fossile
  di un'intenzione mai realizzata — un feed news *autenticato con token* per il bot Telegram, coerente
  col `TELEGRAM_BOT_TOKEN` nei segreti di S1-C1 (S1-C2) e con la storia "Telegram fossile" — mai
  costruita. → Box "Il lucchetto sulla porta accanto: gatare l'URL non protegge l'endpoint"
  (**altissimo valore**, ponte CAP 10 e S1-C13).

- **Il GUID che ripubblica: una buona idea persa nel tempo** — *(SPW → SR → DIS, regressione)* — SPW
  sceglie deliberatamente `urn:simonepizzi:article:<id>` con `isPermaLink="false"`: l'identità dell'item
  è l'ID di DB, **disaccoppiata dall'URL**, così un cambio di slug/categoria **non** fa ri-pubblicare
  l'articolo come nuovo sui consumatori (aggregatori, **bot Telegram**). È la stessa preoccupazione che
  in `.htaccess` giustifica i Redirect 301 (S1-C1): *la stabilità dell'identità*, risolta su due fronti
  (URL lato SEO, GUID lato feed). SR la perde (GUID = permalink `isPermaLink="true"` → ripubblica al
  cambio slug, **e non ha nemmeno i 301**); DIS scende ancora (GUID = `audio_url` → cambia appena
  `migrate_media.php` sposta l'audio, S1-C5). Tre siti, tre gradini di stabilità decrescente per la
  *stessa* lezione. → Box "L'identità stabile di un articolo nel feed: GUID URN, non il permalink"
  (perno; CAP 12 §2.5 lo raccomanda già — vedi §4).

- **La regola `status` dimenticata anche nel feed** — *(SR)* — la regola di pubblicazione di S1-C4
  (`status='published' AND published_at<=now`) **non** è riusata in `feed_news_rss.php`, che filtra
  *solo* `published_at<=now`. Identico al buco di `index.php`/`sitemap.php` (S1-C7): una bozza con data
  passata è nascosta nella lista pubblica `news.php` ma **trapela nel feed RSS** — terzo file, dopo
  index e sitemap, che dimentica il filtro `status`. SPW invece la riusa anche qui (quarta volta
  consecutiva, S1-C4/C7). Due idee diverse di "pubblico" nello stesso sito. (DIS è N/A: i podcast non
  hanno `status`, il feed è "tutto o niente".) → confluisce nel box "Due idee di 'pubblico'" già aperto
  in S1-C4/C7 (ponte CAP 9).

- **Il proxy CORS inbound: quando il thin stack consuma feed altrui invece di produrne** — *(SR)* —
  `rss.php` in SR **non genera** un feed: è un **proxy server-side** che scarica i feed podcast esterni
  (Spreaker, AzuraCast `player.runtimeradio.com`) per aggirare la mancanza di header CORS dell'upstream.
  È il gemello *inbound* del feed *outbound*: stesso sito, due direzioni di sindacazione. La parte
  didattica è la **difesa**: **allowlist di host** + **https-only** ("nessun open proxy") contro
  SSRF/abuso, **cache su disco** `rss_<md5>.xml` (TTL 30′) con **stale fallback** ("una cache scaduta è
  meglio di niente") per la resilienza. Caveat: il *consumer client* (`rss.ts`) ripiega, se il proxy del
  sito fallisce, su **proxy pubblici di terzi** (CodeTabs, AllOrigins) — bypassando l'allowlist: una
  dipendenza da terzi non dichiarata, resilienza-contro-controllo. → Box "Consumare feed altrui senza
  CORS: il proxy del thin stack (allowlist + stale cache)" (nuovo, SR-only; ponte CAP 10 per SSRF).

- **Errori che il client vede / non vede: il `catch` vuoto vs l'HTTP 500** — *(SPW/DIS vs SR)* — in SPW
  e DIS il `catch` è **vuoto**: header e `<channel>` sono già stati emessi con **HTTP 200**, quindi un DB
  giù produce un feed **ben formato ma vuoto/troncato**, *senza* segnale (niente log, niente 5xx) — il
  client lo vede come "feed senza novità". SR fa meglio: `catch PDOException` → **HTTP 500 + `<error>`**
  (copertura però parziale: un'eccezione non-PDO sfugge). È lo stesso anti-pattern del "fallback
  silenzioso" già visto altrove: *un errore mascherato da risposta valida*. → Box "Il fallback
  silenzioso che nasconde un DB down".

- **I monologhi dell'AI nel sorgente di produzione** — *(DIS)* — `feed.php:26-34` è il caso più estremo
  del repo di codice AI-assistito che **discute con sé stesso** dentro la sorgente live: l'autore si
  chiede se la tabella `podcasts` esista, valuta di crearla al volo, conclude *"No, bad practice on GET"*
  e tira a indovinare *"I'll assume it exists"*. È lo stesso tell di `init_db.php` ("ignored for brevity
  in repl", S1-C1) e di `api.ts` (S1-C3): il ritratto più nitido di un codebase generato in
  conversazione con un LLM **e mai ripulito** prima del deploy. → Box "Quando il codice ti racconta i
  suoi dubbi: i monologhi dell'AI nel sorgente" (alto valore, tema ricorrente DIS; ponte S1-C13/altezza
  editoriale).

- **Il setting che nessuno popola: la configurabilità aspirazionale** — *(DIS, eco SPW)* — `feed.php`
  legge `settings.podcast_*` (title/description/image/author) ma **nessun `update_db_*`** crea quelle
  chiavi e nessuna UI le scrive (S1-C10/C12) → il canale gira **sempre sui default hardcoded**. È il
  gemello del TODO di SPW (`rss.php`: *"per ora hardcodiamo, assumiamo venga dai settings"* — config mai
  arrivata). Due siti, stessa storia: codice "pronto a essere configurabile" ma mai cablato. → Box "Il
  TODO che diventa permanente: config dichiarata e mai arrivata".

- **L'`enclosure` MIME sbagliato sulle cover WebP** — *(SPW + SR)* — `enclosure type="image/jpeg"` è
  hardcoded in SPW (e indovinato solo jpeg/png in SR), ma l'upload converte le cover in **WebP** (S1-C5):
  il MIME dichiarato è quindi sbagliato per la maggior parte delle immagini → reader pignoli scartano la
  miniatura. Bug di correttezza minore, identico ai due flagship. (DIS: `enclosure length="0"` hardcoded
  sull'audio — stesso genere di "valore finto" in un attributo che qualche client usa davvero.) → nota
  in CAP 12 §2.4 (ponte S1-C5).

## 4. Mappa → capitolo/i del libro

| Materiale della scheda | Capitolo esistente | Azione |
|---|---|---|
| **Il quadro dei 4 emettitori del `content`** (DOMPurify / strip_tags-allowlist / strip_tags+escape / newsletter) | **CAP 12** (box) + ponti **CAP 8/11/13** | **nuovo box** ad altissimo valore: la tabella dei 4 emettitori, con il feed che chiude il quadro (assente oggi) |
| **Sicurezza per sottrazione vs per escape** (feed che non emette `content` vs lo escapa) | **CAP 12** | **nuovo box**: due modi di rendere sicuro un feed |
| **`feed_config.php` security theater** (gatare l'URL di un endpoint pubblico) | **CAP 12** + **CAP 10** | **nuovo box** "il lucchetto sulla porta accanto" (altissimo valore) |
| **Il proxy CORS inbound** (`rss.php` SR: allowlist + https-only + stale cache) | **CAP 12 §3** (nuova sez.) + **CAP 10** (SSRF) | **nuova sezione**: consumare feed altrui senza CORS (oggi assente) |
| **GUID URN stabile vs permalink vs audio_url** (regressione SPW→SR→DIS) | **CAP 12 §2.5** | **amplia**: §2.5 già raccomanda l'URN; aggiungere che SR/DIS NON lo seguono (regressione reale) |
| **La regola `status` dimenticata nel feed** (SR) | **CAP 12** + **CAP 9** | **nuovo box** condiviso con S1-C4/C7 "due idee di 'pubblico'" |
| **Errore HTTP 500 esplicito vs catch silenzioso** | **CAP 12 §2** | **nuovo box** "il fallback silenzioso che nasconde un DB down" (oggi il capitolo *insegna* il catch vuoto — vedi correzioni) |
| **I monologhi dell'AI nel sorgente** (DIS `feed.php`) | **CAP 12** (aneddoto) + altezza editoriale | **nuovo box**: ripulire il codice generato in conversazione |
| **Config aspirazionale** (settings mai popolati / TODO hardcoded) | **CAP 12 §1** | **aggiungi nota**: il TODO che diventa permanente |
| **Feed podcast iTunes** (DIS, non SR!) | **CAP 12 §3** | **correggi attribuzione** (vedi sotto) + completa |
| **UX "Copia RSS" / dashboard feed-url** | **CAP 12 §5** + ponte CAP admin | **aggiungi**: consegnare il feed ai distributori |

**Correzioni al testo attuale (la mappatura smentisce / disallinea il libro):**
- **CAP 12 §3 attribuisce il feed podcast a SitoRuntime: è SBAGLIATO.** Il capitolo dice *"SitoRuntime
  implementa anche un feed per podcast nel formato Apple Podcasts / Spotify"*. In realtà **SR non genera
  alcun feed podcast**: il suo `rss.php` è un **proxy inbound** che *consuma* i feed podcast esterni
  (Spreaker/AzuraCast). Il sito che **genera** un feed podcast RSS 2.0 + iTunes è **DISINTELLIGENZA**
  (`feed.php`). Da correggere l'attribuzione e da aggiungere la distinzione **produrre vs consumare** un
  feed podcast (sono due cose opposte, ed è proprio il contrasto SR↔DIS).
- **CAP 12 §1 insegna il `catch` vuoto come pattern ("Fallback silenzioso: il feed rimane valido anche
  senza articoli").** È invece l'**anti-pattern** documentato in SPW/DIS: header e `<channel>` già
  emessi con HTTP 200 → un DB giù produce un feed troncato che il client scambia per "nessuna novità",
  senza log né 5xx. Da riscrivere mostrando la variante migliore di SR (`catch PDOException` →
  HTTP 500 + `<error>`) come pattern raccomandato, e il catch vuoto come trappola.
- **CAP 12 §4 elenca `/api/feed.php` come "alias alternativo" di `rss.php`.** Fuorviante: `feed.php`
  **non è un alias** del feed news — è il **feed podcast di DIS**, un endpoint con scopo diverso (iTunes,
  tabella `podcasts`). Da distinguere i tre nomi reali per ruolo (`rss.php` = feed news SPW **oppure**
  proxy inbound SR; `feed_news_rss.php` = feed news SR; `feed.php` = feed podcast DIS), non come sinonimi.
- **CAP 12 omette interamente:** il **quadro dei 4 emettitori** e il ruolo del feed nel chiuderlo (il
  tema di sicurezza centrale); il **proxy CORS inbound** con allowlist/stale-cache (S1-C10); il
  **security theater** di `feed_config.php`; la **regola `status` dimenticata** (bozze nel feed); il
  bug **MIME WebP** sull'`enclosure`; la **config aspirazionale**. Sono dimensioni reali del cluster
  assenti dal capitolo.
- **CAP 12 §2.5 (GUID URN) è corretto e ben scritto** (allineato a SPW, "Incidente v1.7.3"): va solo
  **ampliato** segnalando che è una best practice che **SR e DIS non seguono** — il capitolo la presenta
  come acquisita, la realtà mostra una regressione su due siti su tre.

## 5. Cosa si scarta / dedup

- **Ripetizioni fuse:** i §6 di SPW-C8 e SR-C8 erano lo stesso confronto da due lati (il "cuore della
  card" di SR era la tabella vs SPW); DIS-C8 aggiungeva la colonna "podcast". Qui la comparazione è
  scritta **una volta sola**, sulla tabella unica del §2, e il "quadro dei 4 emettitori" — che le tre
  card riportavano ciascuna a modo suo (SPW a 3 righe, SR a 4, DIS a parole) — è consolidato in **una
  sola tabella** nel §3.
- **Dettaglio per-sito che NON entra nel libro:** numeri di riga, il limite esatto del feed (50 SPW /
  20 SR), la lista precisa degli host in allowlist del proxy, le tre strategie di fetch in cascata di
  `rss.ts`, il parsing iTunes lato client, il testo esatto dei default hardcoded di DIS, l'header
  diagnostico `X-Cache: HIT|MISS|STALE`. Restano nelle card come fonte.
- **Materiale che appartiene ad altre schede:**
  - **`content` salvato grezzo + DOMPurify a render-time** → **S1-C6** (qui solo il *riuso* del content
    nel feed e la conferma che il buco **non** si riapre).
  - **il prerender che riapre il buco `strip_tags`-allowlist** → **S1-C7** (qui solo come riga 2 del
    quadro dei 4 emettitori).
  - **la newsletter come 4° emettitore + double opt-in/unsubscribe_token + mail-bombing** → **S1-C9**
    (qui solo la riga 4, da consolidare lì; è l'unica casella aperta del quadro).
  - **la regola `status`/`published_at`, gli slug, il contratto di lista** → **S1-C4**.
  - **`cover_image` come enclosure / conversione WebP / `migrate_media` che sposta l'audio** → **S1-C5**.
  - **il gate `isAdmin` di `feed_config.php` come *meccanica*** → **S1-C2**; qui solo il *cosa* protegge
    (e che non protegge nulla).
  - **`SITE_URL` vs `HTTP_HOST`, timezone, singleton PDO, Telegram fossile/`TELEGRAM_BOT_TOKEN`** →
    **S1-C1/C2** (già consolidati); qui solo consumati.
  - **i monologhi dell'AI come *fenomeno di codebase* e la storia delle migrazioni** → **S1-C13**; qui
    solo il *sintomo* in `feed.php`.
