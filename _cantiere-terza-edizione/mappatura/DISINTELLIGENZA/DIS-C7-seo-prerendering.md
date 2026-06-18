# Mappatura — DISINTELLIGENZA — C7: SEO & Prerendering (OG proxy)

> **Stato:** COMPLETATO · **(card aggiunta in FASE 1-bis: colmatura gap di copertura, 2026-06-18)**
> **Sessione:** 29 · **Data:** 2026-06-18 · **Commit:** _(in corso)_ · **(coppia con DIS-C8)**
> **File sorgente ispezionati:** (percorso relativo al sito `DISINTELLIGENZA/`)
> - `public/index.php` (SEO proxy: iniezione meta/OG/Twitter in `index_react.html`)
> - `public/.htaccess` (routing non-`/api/` → `index.php`, DIS-C1)
> - richiami: `news.php` (fonte dati, DIS-C4), `db.php` (DIS-C1)
> - confronto: `SPW-C7-seo-prerendering.md`, `SR-C7-seo-prerendering.md`

## 1. Cosa fa (sintesi narrativa)

C7 è il **proxy SEO** di DISINTELLIGENZA: `public/index.php` intercetta ogni richiesta di pagina
(l'`.htaccess` instrada tutto ciò che non è `/api/` qui, DIS-C1), **inietta i meta tag corretti**
(title, description, Open Graph, Twitter Card) dentro l'HTML statico di React, e lo rimanda. Lo scopo
dichiarato (`index.php:2-4`) è preciso e **più ristretto** di SPW/SR: *"risolve l'incapacità dei
crawler (es. Facebook, Telegram) di eseguire JavaScript"* — cioè le **anteprime social**, non un
prerendering SEO completo.

Da qui le due differenze che danno identità alla card rispetto a SPW-C7/SR-C7:

1. **Niente UA-sniffing.** DIS **non** distingue bot da umani: serve a *tutti* lo stesso
   `index_react.html` con i meta iniettati, e lascia che React idrati sopra. SPW e SR invece fanno
   `isCrawler()` e servono HTML diverso ai bot. DIS è più semplice e **non fa cloaking**.
2. **Inietta SOLO i meta, NON pre-renderizza il body.** DIS non stampa il testo dell'articolo
   nell'HTML: mette i meta (tutti `htmlspecialchars`) e basta. SPW/SR invece pre-renderizzano il
   **corpo** dell'articolo per i bot — ed è lì che riaprivano il buco XSS (strip_tags allowlist).
   Non emettendo il body, DIS **evita quel buco** (sicuro per sottrazione), al prezzo di un SEO meno
   completo per i crawler che non eseguono JS.

## 2. Pattern miniCMS rilevanti

- **Entry-point PHP che avvolge la SPA** (`index.php`): stesso pattern dei tre siti — un file PHP
  legge il build React (`index_react.html`), lo modifica e lo serve. Il build è **rinominato**
  (`index_react.html`, `:82`) per non farlo intercettare dal `DirectoryIndex` dell'`.htaccess`
  (DIS-C1).
- **Iniezione meta via regex con escape totale** (`injectTag`, `:93-109`): per ogni tag, se il
  `<meta>`/`<title>` esiste lo sostituisce, altrimenti lo inserisce prima di `</head>`. **Tutti** i
  valori passano da `htmlspecialchars($content)` (`:97,102`). È la difesa chiave: l'iniezione è
  **sicura per escape**, niente HTML grezzo nei meta.
- **Routing PHP speculare alle pagine React** (`:38-73`): `/news/:slug` (carica la news), `/filosofia`,
  `/press`, `/regolamento` con meta **hardcoded** per pagina; default = Home. Mappa ridotta (le pagine
  "festival" come `/vota`/`/iscriviti` non hanno meta dedicati).
- **Description "intelligente" con fallback** (`:45-47`): per le news usa `excerpt` se presente,
  altrimenti `strip_tags($content)` troncato a 160 char + `…`. Legge il `content` ma **solo** per la
  description (stripped + escaped), non lo emette come HTML.
- **Immagine OG con fix percorsi relativi** (`:49-54`): se `cover_image` non inizia per `http`, la
  prefissa con `$base_url` (le immagini OG devono essere assolute). Stessa cura vista nella newsletter
  (DIS-C9).
- **`baseUrl` da `HTTP_HOST`** (`:10`): nessun `SITE_URL` canonico (come SR e DIS-C1) → gli URL OG si
  derivano dall'Host della richiesta. Nota anti host-poisoning.
- **Timezone `Europe/Rome` forzato qui** (`:7`): è l'**unico** punto del backend che lo forza (DIS-C1/
  C4) — gli endpoint API no.
- **Degradazione graziosa** (`:75-77,85-89`): errore DB → prosegue coi meta di default senza bloccare;
  `index_react.html` mancante → `500` con messaggio "Missing Entry Point".

## 3. Codice chiave (stralci con origine)

**Niente UA-sniff: si inietta per tutti** — `index.php:79-125` (nessun `isCrawler()`, a differenza di SPW/SR):

```php
$html_path = __DIR__ . '/index_react.html';            // build React rinominato
if (!file_exists($html_path)) { http_response_code(500); die('... Missing Entry Point'); }
$html = file_get_contents($html_path);
// ... injectTag(...) per title/description/og:*/twitter:* ...
echo $html;                                            // SEMPRE l'HTML React+meta; React idrata sopra
```

**Iniezione meta sicura per escape (htmlspecialchars su tutto)** — `index.php:93-109`:

```php
function injectTag($html, $tag, $content, $property = null) {
    if (!$content) return $html;
    if ($tag === 'title')
        return preg_replace('/<title>.*?<\/title>/s', "<title>".htmlspecialchars($content)."</title>", $html);
    $attr = $property ? "property" : "name";
    $replacement = '<meta '.$attr.'="'.$tag.'" content="'.htmlspecialchars($content).'" />';  // ← escape totale
    // sostituisce il meta se c'è, altrimenti lo inserisce prima di </head>
}
```

**Description dal content ma solo stripped+troncata (NON si emette il body)** — `index.php:42-54`:

```php
$meta['title'] = $article['title'] . ' | Disintelligenza Naturale';
$desc = $article['excerpt'] ?: strip_tags($article['content']);   // legge content SOLO per la description
$meta['description'] = mb_substr(trim($desc), 0, 160) . '...';     // poi injectTag lo escapa
$image = $article['cover_image'] ?? '';
if ($image && strpos($image, 'http') !== 0) $image = $base_url . $image;   // OG image assoluta
```

## 4. Problemi riscontrati & soluzioni

- **GOLD sicurezza (per sottrazione) — DIS NON pre-renderizza il body, e i meta sono escaped.** SPW-C7
  e SR-C7 pre-renderizzano il **corpo** dell'articolo per i bot con `strip_tags` allowlist, riaprendo
  il buco XSS a livello di attributi (raggiungibile via UA-spoof). DIS **non lo fa**: inietta solo
  meta, tutti via `htmlspecialchars` (`injectTag`), e lascia il body a React. Quindi il proxy SEO di
  DIS è **più sicuro** di quello di SR su questo asse — non per una difesa migliore, ma perché **emette
  di meno**. È il contraltare positivo dell'assenza di DOMPurify (DIS-C6): qui il "non emettere" salva.
  → Box "il prerender che non stampa il corpo: sicuro per sottrazione" (ponte SR-C7/SPW-C7).
- **GOLD — niente UA-sniffing (niente cloaking).** A differenza di `isCrawler()` di SPW/SR, DIS serve
  a tutti lo stesso HTML. Vantaggio: nessun rischio di "cloaking" (contenuto diverso per bot/umani,
  penalizzato dai motori) e codice più semplice. Svantaggio: i crawler che **non** eseguono JS (alcuni
  social, scraper) vedono solo meta + shell React vuota, **non** il testo dell'articolo → SEO testuale
  debole per quei bot. Scelta consapevole: il commento mira esplicitamente alle **anteprime social**
  (OG/Telegram), che dei meta si accontentano. → Box "OG-proxy leggero vs Dynamic Rendering completo".
- **`baseUrl` da `HTTP_HOST` (host-poisoning).** `index.php:10` deriva `$base_url` dall'Host →
  un Host falsificato finirebbe negli URL OG (`og:url`, `og:image` relative). Stesso rilievo di SR-C7/
  DIS-C1 (manca `SITE_URL` canonico). Rischio basso (i meta non sono link cliccabili come le email),
  ma presente. → nota.
- **Mappa meta incompleta.** Solo `/news/:slug`, `/filosofia`, `/press`, `/regolamento` hanno meta
  dedicati; le pagine cuore del festival (`/vota`, `/iscriviti`, `/manifesto`, `/edizioni`...) cadono
  sui meta di default (Home). Anteprime social generiche per quelle pagine. → nota.
- **Nessun `sitemap.php`/`robots.php` dinamici** (≠ SPW/SR che li generano via rewrite). DIS non ha
  gestione sitemap/robots lato proxy (verificato: solo `index.php`). SEO infrastrutturale minimo.
  → nota.
- **`status`/visibilità non considerati nel proxy.** `fetchNewsBySlug` (`:21-29`) carica la news per
  slug **senza** il filtro `(status='published') AND published_at<=now` di `news.php` (DIS-C4): il
  proxy SEO potrebbe generare meta per una bozza/programmata se qualcuno ne conosce lo slug. Fuga di
  metadati minore (titolo/excerpt), non del contenuto. → nota (ponte DIS-C4).

## 5. Estetica / UX (moderna ma funzionale)

- **Anteprime social curate**: title con suffisso "| Disintelligenza Naturale", description tagliata a
  160 char con `…`, immagine assoluta — le condivisioni su Telegram/Facebook mostrano card pulite.
  L'estetica qui è quella delle **anteprime fuori dal sito**.
- **Brand voice anche nei meta** (`:60,66,71`): "Siamo scimmie con un microfono in mano…", "Regole
  d'ingaggio, divieti assoluti sull'uso dell'IA…" — il tono del festival arriva fino alle card social.
- **Degradazione invisibile**: se il DB cade, l'utente riceve comunque la Home con meta di default
  (`:75-77`), senza errori. Robustezza percepita.

## 6. Differenze rispetto agli altri siti

Confronto a **TRE** sul proxy SEO (coppia con DIS-C8 per gli "emettitori").

| Aspetto | SimonePizziWebSite (SPW-C7) | SitoRuntime (SR-C7) | **DISINTELLIGENZA (questa card)** |
|---|---|---|---|
| **Tipo** | Dynamic Rendering (SEO Engine v2.0) | Dynamic Rendering (v3.0) | **OG-proxy leggero** (solo anteprime social) |
| **UA-sniffing** | sì (`isCrawler`) | sì (`isCrawler`) | **no** (stesso HTML per tutti) |
| **Pre-render del body** | sì (HTML completo ai bot) | sì | **no** (solo meta; React rende il body) |
| **Buco XSS attributi** | sì (strip_tags allowlist) | sì (idem) | **no** (meta `htmlspecialchars`, body non emesso) |
| **Iniezione meta** | meta + JSON-LD | meta + JSON-LD | **meta OG/Twitter** (no JSON-LD) |
| **`baseUrl`** | `SITE_URL` canonico | `HTTP_HOST` | **`HTTP_HOST`** (come SR) |
| **sitemap/robots dinamici** | sì | sì | **no** |
| **seo-cache** | no | sì (ma morta, SR-C7) | **no** |
| **Regola visibilità** | sì | dimenticata (bozze nei meta) | **dimenticata** (bozze nei meta via slug) |

**Sintesi.** DIS-C7 è il gradino **minimo** del prerender: non un "Dynamic Rendering engine" come
SPW/SR, ma un **proxy di anteprime social** che inietta meta escaped e nient'altro. Paradossalmente è
**più sicuro** di SR-C7 (non emette il body, quindi non riapre l'XSS) ed evita il cloaking (no
UA-sniff), ma è **meno capace** sul SEO testuale (i crawler senza JS non vedono il contenuto) e privo
di sitemap/robots/JSON-LD. È coerente con la filosofia DIS: fare poco, ma il poco escapato.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **OG-proxy leggero vs Dynamic Rendering completo** (i tre gradini del prerender) | Cap. "SEO & prerendering nel thin stack": la scala (alto valore) |
| **Iniezione meta sicura per escape** (`htmlspecialchars`) vs prerender del body | Box "perché non stampare il corpo dell'articolo ti salva dall'XSS" (ponte SR-C7/DIS-C6) |
| **Niente UA-sniff = niente cloaking** | Box "servire lo stesso HTML a bot e umani" |
| **`HTTP_HOST` vs `SITE_URL` negli OG** | confluisce nel box host-poisoning (ponte DIS-C1) |
| **Visibilità dimenticata nel proxy** (bozze nei meta) | confluisce nel box "la regola di pubblicazione dimenticata" (ponte DIS-C4) |

## 8. Note / domande aperte

- **Puntatori ad altri cluster:**
  - Fonte dati `news` (slug, excerpt, content, cover) → **C4** (già mappato); il proxy non applica il
    filtro visibilità di `news.php`.
  - `content` letto solo per la description (stripped+escaped) → **C6** (editor): qui **non** si
    riapre il buco XSS perché il body non è emesso (a differenza di SPW/SR).
  - `db.php`, timezone, `HTTP_HOST` → **C1** (già mappato).
  - RSS/feed → **DIS-C8** (coppia, vedi card gemella).
- **Conferma (chiude il puntatore DIS-C1):** `index.php` è il proxy SEO, mappato qui; in DIS-C1 era
  solo annotato come bootstrap lato pagina.
- Versione del sito: **0.5.x** (`package.json`).
