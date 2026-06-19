# CAPITOLO 11: SEO Pre-rendering con PHP Entry-Point (Terza Edizione)

Una Single Page Application ha un problema di nascita con i motori di ricerca. Il bot di Google, o il crawler di Telegram che genera l'anteprima di un link, riceve dal server un `index.html` quasi vuoto: un `<div id="root"></div>` e un bundle JavaScript. Il contenuto vero arriva solo dopo che quel JavaScript gira, e molti crawler non lo eseguono. Il risultato è una pagina che per il bot non ha né titolo sensato, né descrizione, né immagine di anteprima, né testo da indicizzare.

Il Modello risolve senza un framework SSR, senza Next.js, senza Node. Mette un file PHP davanti alla SPA, gli fa interrogare il database e gli fa iniettare nei posti giusti i meta tag corretti, prima che l'HTML arrivi al bot. È la versione thin-stack del server-side rendering: qualche centinaio di righe di PHP e zero infrastruttura nuova.

Ma questo capitolo ha tre fili da tenere insieme. Il primo è una storia di tentativi: il pattern vincente non è il primo che è stato provato, e i due flagship hanno scartato per strada una soluzione che la Seconda Edizione ancora raccomandava. Il secondo è una scala a tre gradini: i due flagship fanno un Dynamic Rendering completo, DIS si ferma a un proxy di anteprime social, e il gradino più capace porta con sé tre debiti. Il terzo è il filo della sicurezza aperto al CAP 8: il prerender è l'emettitore del `content` dove il buco XSS dei «quattro emettitori» è **ancora vivo**.

> [!NOTE]
> **Correzione rispetto alla Seconda Edizione.** Il capitolo precedente descriveva la sola iniezione dei meta e, in un riquadro, consigliava di aggiungere uno **Static Prerendering** in build (tipo `vite-plugin-prerender`) per l'indicizzazione profonda. Ma quella è **esattamente la SSG con Puppeteer che SimonePizziWebSite ha provato e poi abbandonato** (§1): oggi nel suo repo è solo codice morto, con tanto di post-mortem. La soluzione realmente adottata dai flagship è il **Dynamic Rendering**, che il vecchio capitolo non descriveva. Inoltre lo snippet «implementato in SimonePizziWebSite» si connetteva a un file `.sqlite`: ma SPW gira su MySQL. Quella forma con SQLite e connessione diretta è il proxy di DIS, non il motore di SPW.

---

## 1. Il problema, e tre tentativi di risolverlo

La storia del prerendering in SPW è un percorso a tre tappe, e raccontarla spiega come si è arrivati al pattern finale.

La prima tappa (v1.7.3) iniettava soltanto titolo, descrizione e Open Graph nell'`<head>`. Bastava per le anteprime social, ma non per Google: il crawler trovava i meta corretti e un `<body>` ancora vuoto, e indicizzava pochissime pagine.

La seconda tappa fu la **SSG con Puppeteer**: uno script Node che, in fase di build, prerenderizzava ogni rotta in un file HTML statico su disco. Tecnicamente funzionava. Ma era concettualmente sbagliata per un CMS, e il post-mortem lo dice chiaro: rompeva il flusso «modifica online, pubblica» (serviva una build locale e un upload FTP a ogni articolo), congelava i dati al momento della build, e si portava dietro una catena di complicazioni (un bridge anti-CORS, un buffer `dist-static`, gli eventi di render). Fu abbandonata.

La terza tappa, quella attuale, è il **Dynamic Rendering**: niente build, niente file statici. Un solo `index.php`, in tempo reale, decide cosa servire a seconda di chi chiede.

> [!TIP]
> **Il codice che resta dopo che la strategia è cambiata**
> Della SSG abbandonata, in SPW, è rimasta l'impronta fossile: `prerender.php` è deprecato (risponde solo un avviso), `prerender.js` e `prerender-routes.js` sono codice morto (il `postbuild` esegue `clean-dist.js`, non loro), e una costante `IS_PRERENDERING` protegge dei rami che nessuno definisce più. SR, arrivato dopo, è andato dritto al Dynamic Rendering e non ha fossili. È un piccolo promemoria archeologico: quando si cambia strategia, il codice della strategia vecchia raramente sparisce: resta lì, inerte, finché qualcuno non si fida abbastanza da cancellarlo. La Seconda Edizione di questo manuale raccomandava proprio quella strategia fossile.

---

## 2. Dynamic Rendering: tutto in un solo `index.php`

Il pattern vincente concentra tutto in `public/index.php`, che `.htaccess` mette davanti a `index.html` e a cui dirotta ogni URL virtuale di React Router. Per ogni richiesta, in tempo reale, il file fa quattro cose: deduce dal percorso che tipo di pagina è, interroga il database per i dati reali, e poi sceglie tra due strade in base a chi sta chiedendo.

La scelta passa da `isCrawler()`, che annusa lo `User-Agent`:

```php
// public/index.php:46-86 (SPW) — lo snodo crawler vs umano
function isCrawler(): bool {
    $ua = $_SERVER['HTTP_USER_AGENT'] ?? '';
    if (empty($ua)) return false;
    $crawlers = ['Googlebot', 'Bingbot', 'facebookexternalhit', 'Twitterbot',
                 'TelegramBot', 'WhatsApp', 'Discordbot', /* … */];
    foreach ($crawlers as $bot) { if (stripos($ua, $bot) !== false) return true; }
    return false;
}
$isCrawler = isCrawler();
if ($isCrawler && $pageType !== 'admin') { /* HTML completo server-side per il bot */ }
else { /* index.html di Vite + meta iniettati nell'head; il body lo fa React */ }
```

All'utente vero arriva l'`index.html` di Vite con i meta e il JSON-LD iniettati nell'`<head>`, e il `<body>` lo costruisce React come sempre. Al crawler, invece, arriva un HTML già completo, con titolo, meta e il **corpo dell'articolo** scritto direttamente nel `<body>`, così il bot indicizza senza eseguire una riga di JavaScript. Il file rivendica esplicitamente che non è cloaking: il contenuto servito al bot è lo stesso che l'utente vede dopo l'idratazione di React.

Perché funzioni, il PHP deve conoscere le rotte quanto le conosce React Router, e qui sta il primo costo del metodo:

```php
// public/index.php:133-154 (SPW) — routing server-side speculare a React Router
if (count($uri_parts) === 0)             $pageType = 'homepage';
elseif ($uri_parts[0] === 'admin')       $pageType = 'admin';      // niente SEO per l'area admin
elseif ($uri_parts[0] === 'tutti-i-progetti') $pageType = 'projects';
elseif (count($uri_parts) === 2) { $pageType = 'article';  $catSlug = $uri_parts[0]; $slug = $uri_parts[1]; }
elseif (count($uri_parts) === 1) { $pageType = 'category'; $catSlug = $uri_parts[0]; }
```

> [!WARNING]
> **Il prezzo di non avere un framework SSR: la doppia verità delle rotte**
> Le rotte ora vivono in due posti: in `App.tsx` per React, e in `index.php` per i bot. Aggiungere una pagina pubblica significa toccarle entrambe. Una rotta nuova che il PHP non conosce ricade nel ramo di default, e il bot riceve i meta sbagliati senza che nessuno se ne accorga. È il compromesso del Dynamic Rendering fatto a mano: nessuna infrastruttura, ma una mappa da tenere allineata a mano in due linguaggi diversi.

L'iniezione vera e propria è un'operazione chirurgica sull'HTML compilato da Vite: si rimuove il `<title>` generato dal build e si inserisce il blocco SEO prima di `</head>`.

```php
// public/index.php:576-614 (SPW) — iniezione meta + rimozione del title di Vite
$seoInjection = '<title>' . $metaTitle . '</title>'
    . '<meta name="description" content="' . esc($metaDesc) . '" />'
    . '<link rel="canonical" href="' . esc($canonicalUrl) . '" />';   // + OG/Twitter
if ($jsonLd) { $seoInjection .= '<script type="application/ld+json">' . json_encode($jsonLd) . '</script>'; }
$htmlContent = preg_replace('/<title>.*?<\/title>/s', '', $htmlContent, 1);  // evita il title doppio
$htmlContent = str_replace('</head>', $seoInjection . '</head>', $htmlContent);
```

Ogni valore che arriva dal database passa per un `esc()` (cioè `htmlspecialchars`) prima di finire in un attributo. Tutti i valori, con un'eccezione che è il cuore del §4: il corpo dell'articolo.

---

## 3. La scala a tre gradini: Dynamic Rendering o OG-proxy

I due flagship fanno la stessa cosa. SR ha copiato il motore di SPW quasi alla lettera: stesso `isCrawler()`, stessi helper (`esc`, `truncateText`, `absImageUrl`), stessa iniezione. La differenza più visibile è cosmetica (SR deriva `baseUrl` da `$_SERVER['HTTP_HOST']`, SPW usa il suo `SITE_URL` canonico) e il tipo di dati strutturati: SPW emette `Article` e `CollectionPage`, SR aggiunge un `RadioStation` adatto al suo dominio. Ma l'impianto è lo stesso.

DIS sta su un altro gradino. Il suo `index.php` non è un Dynamic Rendering engine: è un proxy di anteprime social, e lo dichiara. Non annusa lo `User-Agent`, quindi serve a tutti lo stesso HTML (niente rischio di cloaking) e inietta soltanto i meta, lasciando il corpo a React. E i meta li scrive passando ogni valore per `htmlspecialchars`:

```php
// public/index.php:93-109 (DIS) — iniezione meta sicura per escape, nessun corpo prerenderizzato
function injectTag($html, $tag, $content, $property = null) {
    if (!$content) return $html;
    if ($tag === 'title')
        return preg_replace('/<title>.*?<\/title>/s', "<title>".htmlspecialchars($content)."</title>", $html);
    $attr = $property ? "property" : "name";
    return /* inserisce */ '<meta '.$attr.'="'.$tag.'" content="'.htmlspecialchars($content).'" />';
}
```

> [!TIP]
> **Dynamic Rendering completo o OG-proxy leggero**
> Sono due risposte diverse alla stessa domanda. Il Dynamic Rendering (SPW, SR) indicizza meglio sui crawler che non eseguono JavaScript, perché serve loro anche il corpo dell'articolo; in cambio è più complesso, mantiene una doppia mappa di rotte, e (lo vedremo) riapre un buco di sicurezza. L'OG-proxy (DIS) è semplice e onesto: niente cloaking, niente corpo da riemettere, solo meta escaped; in cambio la SEO testuale per i bot no-JS è debole. Non c'è un vincitore assoluto: un sito-festival che vive di anteprime social su Telegram sta benissimo col proxy leggero; un sito di contenuti che vuole posizionarsi su Google ha bisogno del corpo prerenderizzato. La scelta segue cosa devi far vedere, e a chi.

---

## 4. Il prerender riapre il buco XSS: la falla viva dei quattro emettitori

Al CAP 8 abbiamo fissato il quadro dei quattro emettitori del `content`: lo stesso HTML salvato grezzo nel database esce verso il mondo da quattro punti diversi, e la sanitizzazione che vive nel render React non copre gli altri tre. Il prerender SEO è il punto dove quel buco è **ancora aperto**.

Per servire al bot un corpo indicizzabile, il ramo crawler riemette il `content` dell'articolo. Ma non lo passa per DOMPurify (che vive solo nel render React): lo passa per `strip_tags` con una allowlist di tag.

```php
// public/index.php:403-405 (SPW) — il corpo per il crawler: strip_tags allowlist, NON DOMPurify
<div>' . strip_tags($article['content'],
        '<p><br><h2><h3><h4><ul><ol><li><strong><em><a><blockquote><pre><code>') . '</div>
```

La differenza non è teorica. `strip_tags` con allowlist rimuove i tag pericolosi a livello di elemento: `<script>`, `<iframe>`, `<svg>` non sono in lista, quindi spariscono. Ma `strip_tags` **non guarda gli attributi** dei tag che lascia passare. Un `<a href="javascript:...">` o un `<p onmouseover="...">` sopravvive intatto. DOMPurify quei due li avrebbe rimossi; `strip_tags` no.

E il ramo crawler è raggiungibile da chiunque, perché `isCrawler()` si fida solo dello `User-Agent`. Basta presentarsi con `User-Agent: Googlebot` per ricevere il corpo passato dal solo `strip_tags`. La superficie è stretta (perché di norma è la vittima a dover avere un UA da crawler, e i bot non eseguono JavaScript), ma è un secondo percorso di render del contenuto utente che non condivide la difesa del primo.

> [!WARNING]
> **Quando copi un pattern, copi anche la sua falla**
> SR-C7 è SPW-C7 quasi verbatim: stesso `isCrawler`, stessi helper, **stesso identico** `strip_tags` con la stessa allowlist. Copiando il pattern-firma del Dynamic Rendering, SR ne ha copiato anche il buco. E nel copiarlo ha perso un pezzo (la regola di visibilità, §5) introducendo un bug nuovo. DIS, che non prerenderizza il corpo, è l'unico immune: non per una difesa migliore, ma perché emette di meno. È il rovescio esatto della sua mancanza di DOMPurify vista al CAP 8: là il «non difendere» faceva male, qui il «non emettere» salva.
> La lezione chiude il filo aperto al CAP 8: quando la difesa XSS vive in un solo render, ogni altro emettitore deve ri-sanitizzare per conto suo, e prima o poi uno se ne dimentica. La soluzione giusta non è aggiungere `strip_tags` qui e DOMPurify là, ma **una sola funzione di sanitizzazione lato server**, usata da tutti gli emettitori PHP del `content`. Il filo si chiuderà al CAP 12 (il feed, che escapa) e al CAP 13 (la newsletter, che non emette).

---

## 5. La SEO che indicizza le bozze

C'è una seconda regola che il prerender dovrebbe condividere con il resto del sistema, e che SR e DIS dimenticano. Al CAP 9 il ciclo di vita stabilisce che un contenuto è pubblico solo se `status = 'published'` **e** la sua data di pubblicazione è passata. SPW riusa questa regola nelle query SEO e perfino nella sitemap. SR e DIS filtrano solo sulla data:

```php
// public/index.php:130-135 (SR) — manca il filtro su status
$stmt = $pdo->prepare(
    "SELECT id, title, slug, summary, content, cover_image, published_at
     FROM news WHERE slug = ? AND published_at <= ? LIMIT 1");   // ← niente "AND status = 'published'"
```

La conseguenza è una crepa tra due idee di «pubblico». Un articolo in bozza con una data passata è invisibile nell'API e nella lista pubblica, ma trapela nei meta, nell'HTML servito al crawler, nel blocco «ultime notizie» della homepage e, in SR, perfino nella sitemap, che lo consegna a Google.

> [!WARNING]
> **Due idee di «pubblico» nello stesso sito**
> «Pubblico per l'utente» e «pubblico per il bot» dovrebbero essere la stessa cosa, ma quando la regola di visibilità è scritta a mano in ogni query, è facile che un percorso la applichi e un altro no. SPW la tiene allineata in tre file (API, prerender, sitemap); SR la perde proprio nel file che la dà in pasto ai motori di ricerca. Anche qui la radice è la stessa del buco XSS: una regola di dominio che non vive in un punto solo finisce per divergere tra i suoi consumatori.

---

## 6. La seo-cache che sopravvive al suo lettore

SR, a differenza di SPW, ha una cache SEO: a ogni salvataggio scrive un file `.cache/seo_news_<md5(slug)>.json`, lo rigenera in blocco con uno script dedicato, lo cancella quando elimini il contenuto. Tutto perfettamente mantenuto, tranne un dettaglio: **nessuno la legge**.

Una ricerca su tutto il codice non trova un solo punto che apra quei file. Il motore v3.0 interroga il database direttamente. E la prova del delitto è scritta nel codice stesso: il banner di `index.php` dichiara di aver sostituito «il proxy cache-file della v2», e uno script di rigenerazione contiene un commento che tradisce il lettore scomparso:

```php
// public/api/rebuild_seo_cache.php:67-79 (SR)
$seoData = [
    'title' => $speaker['name'],
    'description' => $speaker['role'] . ' - ' . substr($speaker['bio'] ?? '', 0, 150) . '...',
    'name' => $speaker['name'], // Injected for consistency with index.php reader  ← il reader non esiste più
];
file_put_contents($cacheDir . '/seo_speaker_' . md5($speaker['id']) . '.json', json_encode($seoData));
```

La versione 2 era un proxy che leggeva quei JSON; la v3.0 ha riscritto il motore con la query diretta e ha rimosso il lettore senza spegnere gli scrittori. Ogni salvataggio paga ancora il costo di scrivere un file che nessuno aprirà. È l'opposto di SPW, che la cache SEO non l'ha mai avuta, per scelta.

> [!TIP]
> **La cache che sopravvive al suo lettore**
> È un modo specifico in cui il codice marcisce: riscrivi il consumatore di qualcosa e dimentichi di spegnerne i produttori. La cache resta, viene aggiornata, invalidata, rigenerata, e non serve a niente. Vale anche come correzione a un punto del CAP 7, che citava lo script `rebuild_seo_cache` come utile per le migrazioni: oggi rigenera una cache morta. Il prossimo paragrafo dà a questa cache un risvolto meno innocente di così.

---

## 7. Quando l'entry-point diventa un bersaglio

C'è un motivo per cui una cache che serve i bot senza toccare il database non è solo un'ottimizzazione. Lo ha imparato Runtime Radio, e la lezione è abbastanza importante da avere una casa in questo capitolo: il vettore dell'attacco è esattamente l'entry-point SEO che abbiamo appena descritto.

Tra il 23 e il 27 febbraio 2026 il sito ha vissuto due crisi sovrapposte. La prima fu il collasso del database SQLite sotto un carico cresciuto per mesi, risolto con una migrazione d'emergenza a MySQL in meno di un giorno (la racconta il CAP 15). La seconda arrivò mentre l'infrastruttura era ancora instabile: un'ondata di richieste che restituivano errori 503 e 500, con picchi di traffico verticali, impossibili da spiegare con la crescita organica.

Il vettore era elegante. Migliaia di bot ostili **simulavano i crawler dei social**, mandando uno `User-Agent` da Telegram o Facebook. E ogni richiesta con quell'UA colpiva `index.php`, che per costruzione interrogava il database per estrarre i meta. Il motore SEO, progettato per far apparire bene i link condivisi, era diventato una leva: una richiesta a costo quasi zero per l'attaccante forzava una query sul database appena migrato e ancora fragile.

```
Bot ostile → User-Agent: TelegramBot → richiesta a /news/uno-slug
→ index.php → query al DB per i meta → risposta
→ il bot scarta e ripete, mille volte al secondo
→ il DB cede → 503/500
```

La risposta separò il percorso dei bot da quello degli utenti. Le risposte per i crawler social vennero servite da **file JSON statici precompilati**, scritti al momento della pubblicazione di un articolo: il bot riceve i meta in pochi millisecondi, senza che il database venga mai interrogato. Solo gli utenti veri, con un browser che esegue JavaScript, percorrono la strada normale. E il servizio core, lo streaming audio, restò attivo dietro una pagina di manutenzione statica anche mentre il resto era offline.

Quei file JSON precompilati hanno un nome familiare: `.cache/seo_*.json`. Sono la stessa seo-cache del paragrafo precedente. È difficile non leggere i due fatti insieme: la cache nacque come scudo anti-DDoS, un percorso per i bot che non toccava il database; poi la riscrittura v3.0 del motore tornò alla query diretta e rimosse il lettore, lasciando la cache scritta-ma-mai-letta. Lo scudo è ancora lì, viene ancora lucidato a ogni salvataggio, ma non è più imbracciato da nessuno.

> [!WARNING]
> **Ogni endpoint pubblico che interroga il DB è un bersaglio; lo User-Agent non è un gatekeeper**
> Tre cose da portarsi a casa. La prima: qualunque endpoint non autenticato che, per rispondere, interroga il database, è una leva d'attacco volumetrico. Se la risposta a una richiesta ripetitiva può venire da una cache statica, quella cache non è solo performance, è un layer di sicurezza. La seconda, già incontrata al CAP 10: i bot social si riconoscono dallo `User-Agent`, e lo `User-Agent` si falsifica. Lo si può usare per *ottimizzare* (servire una cache ai bot riconosciuti), mai come barriera d'accesso. La terza, la più scomoda: una difesa che funziona può essere smontata senza farlo apposta, in una riscrittura che guarda solo alle funzionalità. La seo-cache di Runtime Radio non è stata «tolta»: è stata orfanata, e con lei la protezione che dava.

---

## 8. sitemap, robots e dati strutturati

Resta l'infrastruttura SEO di contorno, che il vecchio capitolo liquidava come «già gestita dall'`.htaccess`». In realtà c'è un pattern preciso: `sitemap.xml` e `robots.txt` non sono file fisici, ma rewrite verso `sitemap.php` e `robots.php`, generati in tempo reale.

```apache
# public/.htaccess (SPW) — niente file fisici: sitemap e robots sono PHP
DirectoryIndex index.php index.html                 # il SEO Engine prima di index.html
RewriteRule ^sitemap\.xml$ sitemap.php [L,NC]
RewriteRule ^robots\.txt$  robots.php  [L,NC]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_URI} !^/api/ [NC]
RewriteRule ^(.*)$ /index.php [L,QSA]                # ogni URL virtuale React → SEO Engine
```

Così la sitemap è sempre fresca senza prerendering, e il suo `baseUrl` si deriva dall'host della richiesta, quindi lo stesso file funziona su produzione e staging. Il `robots.php` di SR ci aggiunge una piccola personalità editoriale: blocca i crawler SEO commerciali (Ahrefs, Semrush, DotBot) e impone un `Crawl-delay`, per non sprecare banda con strumenti che non portano lettori.

Sui dati strutturati, entrambi i flagship costruiscono il JSON-LD come array PHP, scegliendo il tipo in base alla pagina: `Article` o `NewsArticle` per gli articoli, `CollectionPage` per gli elenchi, e in homepage un `@graph` che descrive il sito e l'autore (o, per Runtime Radio, una `RadioStation`). DIS, fedele al suo gradino, non emette JSON-LD: si ferma ai meta.

---

## In sintesi

Indicizzare una SPA senza un framework SSR si può, con un PHP che fa da front controller, annusa il bot e gli serve un HTML completo. Ma il Dynamic Rendering non è gratis: duplica la mappa delle rotte, e soprattutto riapre il buco XSS dei contenuti, perché riemette il `content` con uno strumento (`strip_tags`) più debole del DOMPurify del render. SPW lo fa bene, SR ne ha copiato anche i difetti e ne ha aggiunti di propri (le bozze indicizzate, la cache orfana), DIS evita i problemi facendo di meno. E la storia del DDoS di febbraio chiude il cerchio: l'entry-point che rende il sito visibile è lo stesso che, sotto sforzo, lo fa cadere, e la cache che lo salvò è oggi un attrezzo dimenticato in un angolo.

> [!IMPORTANT]
> **Il Canone**
> - Indicizza la SPA con Dynamic Rendering da un entry-point PHP (UA-sniff), non con una SSG fragile.
> - Il prerender riemette il `content`: sanitizzalo con la **stessa** difesa del render, perché `strip_tags` con allowlist lascia passare gli attributi (`onerror`, `href="javascript:"`).
> - Rispetta lo `status` anche nel ramo crawler: non indicizzare le bozze.
> - `sitemap`/`robots` dinamici; lo User-Agent non è un gatekeeper di sicurezza.

---
*Prossimo Capitolo: RSS Feed & Syndication. Il feed è l'emettitore più sicuro del contenuto, quello che chiude il filo dei quattro emettitori, e insieme il luogo dove si annidano un proxy CORS e un po' di teatro della sicurezza.*
