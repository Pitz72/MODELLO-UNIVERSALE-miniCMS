# Mappatura — SimonePizziWebSite — C8: RSS & Feed Syndication

> **Stato:** COMPLETATO
> **Sessione:** 8 · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `SimonePizziWebSite/`)
> - `public/api/rss.php` (**FILE PRINCIPALE e UNICO** del cluster — generazione del feed RSS 2.0 real-time, ~75 righe)
> - `public/.htaccess:21-34` (verifica routing: **nessuna** rewrite per il feed; `/api/` escluso dal front controller React)
> - `src/components/Header.tsx:180-195` (icona RSS nell'header pubblico → link diretto `/api/rss.php`)
> - `src/pages/admin/ArticlesList.tsx:129-139` (bottone admin "Copia RSS" → copia l'URL del feed negli appunti)
> - `public/api/db.php:20` (controprova: `PDO::FETCH_ASSOC` di default → accesso `$article['campo']`)
> - `dist/api/rss.php` (build artifact: **identico** al sorgente `public/api/rss.php`, nessuna divergenza deployata)
> - **Controprova falsi positivi** grep `rss|/feed|RSS`: `src/data/portfolioData.ts:477` = prosa generica ("i feed RSS" dentro un articolo), **non** un link al feed. Le menzioni "feed" ipotizzate in `ContactPage.tsx`/`CommunityHub.tsx`/`ArticleEditor.tsx`/`ProjectEditor.tsx` **non esistono** (grep negativo): erano falsi positivi sulla parola "feed".

## 1. Cosa fa (sintesi narrativa)

C8 è la parte **più piccola e più disciplinata** dei contenuti SPW: un **singolo file PHP** (`rss.php`)
che, ad ogni richiesta, genera in tempo reale un **feed RSS 2.0** con gli ultimi 50 articoli pubblicati.
Niente cache, niente file `.xml` su disco, niente libreria: è la stessa filosofia "thin stack real-time"
già vista in C7 per sitemap/robots, applicata alla sindacazione.

Il flusso è lineare (`rss.php:1-74`):
1. include `db.php` (singleton PDO di **C1**), manda `Content-Type: application/rss+xml; charset=utf-8`
   (`:4`);
2. calcola `base_url` da `HTTP_HOST` + schema HTTPS (`:8-10`) — stesso pattern host-derivato di C7,
   funziona su qualunque dominio/staging;
3. **forza il fuso `Europe/Rome`** (`:13`, commento V1.5.5: "Bypass orario server Los Angeles per
   pubblicazione tempestiva") e fotografa `$ita_now_str` per il confronto di pubblicazione;
4. apre il `<channel>` con `title`/`link`/`description`/`language` **hardcoded** (`:19-29`);
5. interroga `articles` con **la stessa identica regola di visibilità di C4/C7**
   (`status='published' AND (published_at IS NULL OR published_at <= :ita_now)`), ordina per
   `published_at DESC`, `LIMIT 50` (`:33-41`);
6. per ogni articolo emette un `<item>` con `title`, `link` assoluto, `description`, `enclosure`
   (immagine), `pubDate` RFC-822 e un **GUID stabile a URN** (`:43-68`);
7. chiude `</channel></rss>` (`:73-74`). Un `try/catch` avvolge solo la query/loop con **fallback
   silenzioso** (`:69-71`).

**Il punto più importante per la sicurezza (chiusura del ponte C6/C7):** `rss.php` **NON emette mai
`articles.content`**. La colonna `content` è inclusa nella SELECT (`:33`) ma **non viene mai stampata**;
la `<description>` dell'item usa **solo `excerpt`**, passato per `htmlspecialchars()` (`:58`). Quindi
il feed è il **terzo emettitore del contenuto** dopo render-React e prerender crawler, ma è anche
**il più sicuro**: non c'è `content:encoded`, niente `CDATA` grezzo, niente `strip_tags` — solo testo
breve (`excerpt`) interamente escapato. Vedi §4.

## 2. Pattern miniCMS rilevanti

- **Feed real-time in un solo file, zero infrastruttura.** Come sitemap/robots in C7, il feed è
  generato ad ogni `GET /api/rss.php` direttamente dal DB. Nessun cron, nessun `.xml` materializzato,
  nessuna invalidazione cache: un articolo pubblicato compare nel feed **al primo refresh**. Incarna
  la filosofia thin stack ("la freschezza è gratis se generi al volo").
- **Una sola regola di pubblicazione, ora su QUATTRO file.** La clausola
  `status='published' AND (published_at IS NULL OR published_at <= now)` (`rss.php:35`) è la **stessa**
  di `articles.php` (C4), `index.php` (prerender C7) e `sitemap.php` (C7). Bozze e post programmati
  restano fuori anche dal feed. Coerenza di dominio replicata a mano in quattro punti → candidato forte
  per il box "una regola, N emettitori" (rischio: va cambiata in N posti).
- **GUID stabile a URN, disaccoppiato dall'URL** (`rss.php:49-53,66`): l'identità dell'item è
  `urn:simonepizzi:article:<id>` con `isPermaLink="false"`, **non** il permalink. Scelta dichiarata
  (v1.7.3) per evitare che un cambio di categoria/slug faccia **ri-pubblicare** l'articolo come nuovo
  su sistemi di integrazione (es. **bot Telegram**). È lo stesso identico problema che in `.htaccess:38-47`
  giustifica i "Redirect 301 permanenti per URL articoli riorganizzati": **una sola preoccupazione
  — la stabilità dell'identità dell'articolo — risolta su due fronti** (URL lato SEO, GUID lato feed).
- **Timezone forzato nel singolo endpoint** (`rss.php:13`): invece di affidarsi al timezone impostato
  in `db.php` (C1), `rss.php` ri-chiama `date_default_timezone_set('Europe/Rome')` per conto suo.
  Difesa ridondante ("ogni file che confronta date col DB si auto-protegge dal server in fuso sbagliato").
- **Escaping uniforme via `htmlspecialchars`** su ogni dato dinamico che entra nell'XML: `title`,
  `link`, `description`/`excerpt`, `enclosure url` (`:26-28,56-62`). Nessun campo dinamico finisce
  crudo nel feed. (Il GUID `:66` è l'unico non escapato, ma è costruito da `(int)$article['id']` →
  non iniettabile.)
- **Limite nominato** `define('RSS_FEED_LIMIT', 50)` (`:17`) — costante con commento di manutenzione,
  micro-pattern di leggibilità tipico del codice di Simone.

## 3. Codice chiave (stralci con origine)

**La stessa regola di visibilità di C4/C7, ora nel feed** — `rss.php:32-41`:

```php
// [v1.7.3] Aggiunto id nella query per generare GUID stabile disaccoppiato dalla URL
$query = "SELECT id, title, slug, excerpt, content, cover_image, category, published_at
          FROM articles
          WHERE status = 'published' AND (published_at IS NULL OR published_at <= :ita_now)
          ORDER BY published_at DESC
          LIMIT " . RSS_FEED_LIMIT;
$stmt = $pdo->prepare($query);
$stmt->execute([':ita_now' => $ita_now_str]);
$articles = $stmt->fetchAll();
```

**Il cuore di C8: l'item — `content` SELECTato ma MAI emesso, `description` = solo `excerpt` escapato**
— `rss.php:43-67`:

```php
foreach ($articles as $article) {
    $pubDate  = date(DATE_RSS, strtotime($article['published_at'] ?? 'now'));      // RFC-822
    $item_url = $base_url . '/' . rawurlencode($article['category']) . '/' . rawurlencode($article['slug']);

    // GUID stabile su ID numerico, isPermaLink="false" → non è un URL navigabile
    $stable_guid = 'urn:simonepizzi:article:' . (int)$article['id'];

    echo '  <item>' . "\n";
    echo '    <title>' . htmlspecialchars($article['title']) . '</title>' . "\n";
    echo '    <link>' . htmlspecialchars($item_url) . '</link>' . "\n";
    echo '    <description>' . htmlspecialchars($article['excerpt']) . '</description>' . "\n";  // ← excerpt, NON content
    if (!empty($article['cover_image'])) {
        $image_url = (str_starts_with($article['cover_image'], 'http'))
            ? $article['cover_image'] : $base_url . '/' . ltrim($article['cover_image'], '/');
        echo '    <enclosure url="' . htmlspecialchars($image_url) . '" type="image/jpeg" />' . "\n";
    }
    echo '    <pubDate>' . $pubDate . '</pubDate>' . "\n";
    echo '    <guid isPermaLink="false">' . $stable_guid . '</guid>' . "\n";
    echo '  </item>' . "\n";
}
```

> Nota microscopica: `content` compare nella SELECT (`:33`) ma **non c'è alcun `echo` di `$article['content']`**
> in tutto il file. È una colonna **caricata e mai usata** → conferma forte che il feed espone solo `excerpt`.

**Channel hardcoded (debito di config dichiarato)** — `rss.php:19-29`:

```php
// Assumiamo che il nome del feed venga dai settings, per ora hardcodiamo un title di base
$site_title = "Simone Pizzi - Blog & Portfolio";
$site_description = "Le ultime pubblicazioni di Simone Pizzi";
// …
echo '  <title>' . htmlspecialchars($site_title) . '</title>' . "\n";
echo '  <link>' . htmlspecialchars($base_url) . '</link>' . "\n";
echo '  <description>' . htmlspecialchars($site_description) . '</description>' . "\n";
echo '  <language>it-IT</language>' . "\n";
```

**Routing: nessun URL pulito — il feed si raggiunge GREZZO** — `public/.htaccess:30-34`:

```apache
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_URI} !^/api/ [NC]      # /api/* escluso dal front controller React
RewriteRule ^(.*)$ /index.php [L,QSA]
```
> A differenza di `sitemap.xml→sitemap.php` e `robots.txt→robots.php` (C7), **non esiste** una rewrite
> `feed.xml`/`rss.xml → rss.php`. Il feed è esposto solo all'URL grezzo **`/api/rss.php`**, ed è quello
> che usano sia l'header pubblico sia il bottone admin (§5).

## 4. Problemi riscontrati & soluzioni

- **GOLD — CHIUSURA del ponte di sicurezza C6/C7: il feed NON è un vettore XSS-stored.**
  C6 aveva stabilito che `articles.content` è salvato **grezzo** e difeso **solo** a render-time
  (DOMPurify in `SingleArticle.tsx`); C7 aveva mostrato che il prerender crawler (`index.php:404`)
  lo ri-emette con `strip_tags` allowlist (buco a livello **attributi**). Il terzo emettitore — il feed —
  **chiude il follow-up nel modo migliore possibile**:
  - **`rss.php` non emette `articles.content` affatto.** La `<description>` usa **`excerpt`**
    (`:58`), passato per **`htmlspecialchars()`**. Niente `content:encoded`, niente `CDATA`, niente
    `strip_tags`.
  - Risultato: anche se `excerpt` contenesse markup ostile, `htmlspecialchars` lo trasforma in entità
    (`&lt;script&gt;`) → **nessuna esecuzione** in un reader RSS. **Il feed è il più sicuro dei tre
    emettitori.**
  - **Quadro completo dei TRE emettitori dello stesso contenuto** (gold per il libro):
    | Emettitore | Cosa emette | Sanitizzazione | Esito |
    |---|---|---|---|
    | React `SingleArticle.tsx` (C6) | `content` pieno | **DOMPurify** (tag + attributi + hook iframe) | ✅ pieno e sicuro |
    | Prerender crawler `index.php:404` (C7) | `content` pieno | `strip_tags` allowlist (solo tag) | ⚠️ sicuro sui tag, **buco sugli attributi** |
    | Feed `rss.php:58` (C8) | **solo `excerpt`** | `htmlspecialchars` (escape totale) | ✅ sicuro (ma lossy) |
  - **Morale per il manuale:** tre render-path dello stesso dato, tre policy diverse, **nessuna
    condivisa**. Il feed è "sicuro per sottrazione" (non emette il campo pericoloso), non per una difesa
    progettata. Rafforza la tesi di C6/C7: serve **una funzione di sanitizzazione server-side condivisa**
    da tutti gli emettitori PHP del contenuto, invece di N policy ad hoc.

- **Il feed espone solo l'`excerpt`, non l'articolo completo (limite di prodotto, non bug).** Senza
  `content:encoded`, i lettori RSS e i sistemi di integrazione (bot Telegram) ricevono **solo il
  sommario**. Per un "blog feed" è una scelta legittima (drive-to-site), ma è il rovescio della medaglia
  della sicurezza-per-sottrazione: per emettere il contenuto pieno servirebbe prima risolvere la
  sanitizzazione server-side. → Box "il trade-off tra feed completo e superficie XSS".

- **`enclosure type="image/jpeg"` hardcoded mentre le cover sono WebP (C5).** `rss.php:62` dichiara
  sempre `type="image/jpeg"`, ma in C5 l'upload **converte le immagini in WebP**. Il MIME dichiarato
  nell'`<enclosure>` è quindi **sbagliato** per la maggior parte delle cover (`.webp`) → reader pignoli
  potrebbero rifiutare/non mostrare la miniatura. Bug di correttezza minore. Fix: derivare il type
  dall'estensione reale.

- **`title`/`description` del channel hardcoded malgrado l'intento "dai settings".** Il commento
  `rss.php:19` ("Assumiamo che il nome del feed venga dai settings, per ora hardcodiamo") dichiara un
  **debito**: non esiste alcun `feed_config` né lettura da una tabella `settings`. Cambiare il nome del
  feed richiede editare il PHP. → Traccia "config che doveva esistere e non è mai arrivata".

- **`pubDate` instabile per articoli con `published_at` NULL.** `rss.php:45` fa
  `strtotime($article['published_at'] ?? 'now')`: poiché la query ammette `published_at IS NULL`
  (articoli pubblicati senza data), per quegli item il `pubDate` diventa **l'istante di generazione del
  feed** e **cambia ad ogni fetch**. Un reader potrebbe vederli sempre come "nuovi". Minore, ma reale.

- **`catch (Exception)` con fallback silenzioso → feed potenzialmente troncato senza segnale.**
  `rss.php:69-71`: in caso di errore DB il `catch` è **vuoto**. Header e `<channel>` sono già stati
  emessi (`:4,25`) con HTTP 200; `</channel></rss>` sono **fuori** dal `try` → l'XML resta ben formato
  ma **vuoto/parziale** e il client riceve comunque 200. Nessun log, nessun 5xx. → Box "il fallback
  silenzioso che nasconde un DB down".

- **Nessun URL "pulito" per il feed (incoerenza con C7).** C7 dà URL puliti a sitemap/robots via
  rewrite; il feed resta a `/api/rss.php`. Non è un problema funzionale (header e admin linkano l'URL
  grezzo), ma è un'**asimmetria** con la cura SEO degli altri asset → nota di coerenza.

- **Mancano elementi RSS "di galateo": `lastBuildDate`, `ttl`, `atom:link rel="self"`.** Il feed è
  RSS 2.0 **puro**, senza namespace Atom e senza self-link (best practice per i validatori/aggregatori).
  Funziona, ma un validatore W3C Feed segnalerebbe warning. Minore.

## 5. Estetica / UX (moderna ma funzionale)

- **Doppio punto d'accesso, due platee.**
  - **Pubblico** (`Header.tsx:180-195`): icona RSS SVG nell'header con micro-interazione di hover
    (colore `#6a9070` → arancio `#f97316` su `onMouseEnter`/`Leave`), `target="_blank"` +
    `rel="noopener noreferrer"`, `title`/`aria-label="Feed RSS"`. Discreta ma presente.
  - **Redazionale** (`ArticlesList.tsx:129-139`): bottone **"Copia RSS"** che fa
    `navigator.clipboard.writeText(window.location.origin + '/api/rss.php')` + `alert` di conferma,
    con `title="Copia l'indirizzo del Feed RSS da dare ai distributori"`. UX pensata per **consegnare
    il feed ai sistemi di sindacazione** (bot Telegram, aggregatori) senza copiarlo a mano.
- **Coerenza dell'URL**: entrambi i punti puntano allo stesso `/api/rss.php` — nessuna divergenza
  client (a differenza dei due canonical SEO di C7).

## 6. Differenze rispetto agli altri siti

(Da consolidare in FASE 2. Ipotesi/puntatori:)
- **SitoRuntime (SR-C8 RSS & Feed)**: SR ha **podcast** (ROADMAP SR-C4 "news + speakers + podcasts").
  Un feed podcast richiede `<enclosure>` **audio** + namespace iTunes (`<itunes:*>`) → probabilmente un
  RSS molto più ricco e con MIME corretto sull'enclosure. Confronto chiave: SPW = feed blog minimale
  (excerpt, enclosure immagine fissa jpeg); SR potrebbe avere il feed più "serio" dei due. Verificare
  se SR emette `content:encoded` (e con quale sanitizzazione → estende il quadro a 3 emettitori anche lì).
- **DISINTELLIGENZA/FDCA (festival, SQLite)**: ROADMAP segna DIS-C4 "Content APIs (news/**feed**)" ma
  **nessun** cluster C8 dedicato → probabilmente feed assente o minimale. Termine di paragone "minimo".
- Verificare se il pattern **GUID a URN stabile `isPermaLink="false"`** è copiato tra i siti (firma
  anti-ripubblicazione per le integrazioni Telegram) o specifico di SPW.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **Il feed RSS in un solo file, real-time dal DB** (zero cache, zero .xml su disco) | Cap./box "sindacazione thin stack: un endpoint, niente infrastruttura" (gemello di sitemap/robots di C7) |
| **I TRE emettitori dello stesso `content`** (React+DOMPurify / prerender+strip_tags / feed+excerpt-escaped) | Box problemi/soluzioni "una sanitizzazione, tanti render-path" (**chiude il ponte C6→C7→C8, altissimo valore**) |
| **Sicurezza-per-sottrazione vs sicurezza progettata** (il feed è sicuro perché NON emette `content`) | Box "non emettere il campo pericoloso è una difesa… finché qualcuno non aggiunge `content:encoded`" |
| **GUID a URN stabile `isPermaLink="false"`** (anti-ripubblicazione su bot Telegram) + parallelo coi Redirect 301 di `.htaccess` | Box "l'identità stabile di un articolo: GUID nel feed, 301 nell'URL" (ponte C7) |
| **Una regola di pubblicazione `published_at<=now` replicata su 4 file** (articles/index/sitemap/rss) | Box "DRY infranto di proposito: la stessa WHERE in quattro posti" (ponte C4/C7) |
| **Il fallback silenzioso del `catch` vuoto** (feed vuoto con HTTP 200) | Box "errori che il client non vede mai" |
| **Config dichiarata e mai arrivata** (`title`/`description` hardcoded "per ora dai settings") | Aneddoto "il TODO che diventa permanente" |
| **UX redazionale "Copia RSS"** (dare il feed ai distributori in un click) | Cap. admin/UX (ponte C12) |

## 8. Note / domande aperte

- **Ponte di sicurezza C6→C7→C8: CHIUSO.** Il follow-up aperto in C6 §8 e ribadito in C7 §4/§8
  ("RSS emette `content`? con quale sanitizzazione?") ha risposta definitiva: **no, `rss.php` non emette
  `content`** (colonna SELECTata ma mai stampata, `:33` vs assenza di echo); la `<description>` usa
  **`excerpt` + `htmlspecialchars`**. Il feed è il **più sicuro** dei tre emettitori. Resta aperto **solo**
  per **C9 (Newsletter)**: la newsletter è l'ultimo possibile emettitore di `articles.content` — lì il
  rischio XSS-stored sarebbe **più alto** (l'HTML email viene renderizzato in un client di posta che
  esegue meno JS ma può subire altri vettori). **Verificare in C9 se la newsletter inietta `content`
  e con quale sanitizzazione.**
- **Puntatori ad altri cluster** (annotati, NON mappati qui):
  - `Database::connect()` / singleton PDO / `FETCH_ASSOC` / timezone `Europe/Rome` → **C1**
    (qui solo consumati; nota: `rss.php:13` ri-forza il timezone per conto suo).
  - Schema `articles` e regola `status`/`published_at` → **C4** (qui solo consumati per il feed).
  - `cover_image` solo-URL + conversione WebP (che rende sbagliato `type="image/jpeg"`) → **C5**.
  - Bottone "Copia RSS" e UX della lista articoli admin → **C12** (Admin).
  - Integrazione **bot Telegram** come consumatore del feed (citata nei commenti `:52` e `.htaccess:41`)
    → fuori roadmap SPW; è un sistema **esterno** che spiega le scelte GUID/301. Solo puntatore.
- **Assenze confermate (per scelta/debito, non per dimenticanza):** nessuna tabella/file `feed_config`;
  nessun feed **Atom**; nessuna rewrite per URL pulito del feed; nessun `content:encoded`, `lastBuildDate`,
  `ttl`, `atom:link rel="self"`; nessuna lettura del titolo feed da `settings` (hardcoded con TODO).
- **`dist/api/rss.php` = copia identica** del sorgente (build artifact): nessuna versione deployata
  divergente da ispezionare.
- **Nessuna credenziale/segreto** presente nei file di C8.
- Versione di riferimento: sito **1.21.0**; tracce di versione nei commenti del feed: **V1.5.5**
  (timezone), **v1.5.10** (limite 50 + security headers), **v1.7.3** (GUID stabile a URN).
