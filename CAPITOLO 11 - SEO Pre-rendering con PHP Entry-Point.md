# CAPITOLO 11: SEO Pre-rendering con PHP Entry-Point (v1.0)

Il problema fondamentale delle Single Page Application (SPA) React è che i bot di Google, Facebook, Twitter e LinkedIn vedono solo un `<div id="root"></div>` vuoto: JavaScript non viene eseguito al momento della scansione. Il Modello Universale risolve questo problema con un **PHP Entry-Point** che inietta i meta tag corretti nell'HTML prima che arrivi al bot, senza rinunciare alla potenza di React.

Questo capitolo documenta il pattern reale implementato in **SimonePizziWebSite (v1.4.0)** e menzionato in forma più semplice in SitoRuntime.

## 1. Il Problema e la Soluzione

### Il Problema
```
Bot Google → richiede /videogiochi/mio-articolo
Server → serve index.html (solo <div id="root">)
Bot → "non c'è contenuto, ignoro"
```

### La Soluzione: The Swap Trick
```
Bot Google → richiede /videogiochi/mio-articolo
Server → Apache → index.php (invece di index.html!)
index.php → query SQLite → estrae title, description, image dell'articolo
index.php → legge index.html compilato da Vite → inietta meta tag → serve HTML completo
Bot → "ho trovato contenuto, indexo"
```

> [!WARNING]
> **I Limiti della Soluzione (Incidente "Sito Invisibile")**
> L'esperienza sul campo (SimonePizziWebSite v1.7.x) ha dimostrato che il trick dello Swap PHP è una soluzione eccellente per **Social Bot** (Telegram, Facebook, Twitter, iMessage) che si accontentano dei meta-tag nell'<head>. 
> Tuttavia, **NON è sufficiente per l'indicizzazione organica su Google (SEO puro)**. I moderni crawler come Googlebot cercano l'HTML renderizzato semantico nel `<body>`. Trovando solo un `<div id="root">`, Google indicizzerà pochissime pagine (es. 1 su 30). 
> Per risolvere l'indicizzazione SEO profonda di una SPA, l'architettura miniCMS consiglia l'integrazione di plugin per **Static Prerendering** in fase di build (come `vite-plugin-prerender`), pur mantenendo l'infrastruttura di deploy immutata.

## 2. Il Meccanismo: Build Rename Strategy

Il trick sta nel **rinominare** l'`index.html` generato da Vite in modo che `index.php` possa occupare quella posizione come entry-point principale.

### In DISINTELLIGENZA (build script in package.json):
```json
"build": "tsc -b && vite build && node clean-dist.js && move dist\\index.html dist\\index_react.html"
```
Vite genera `dist/index.html`, lo script di build lo rinomina in `dist/index_react.html`. L'`index.php` nella cartella sorgente viene poi copiato nella `dist/` durante il deploy. In questo modo Apache serve `index.php` come file predefinito.

### In SimonePizziWebSite (build script standard):
```json
"build": "tsc && vite build",
"postbuild": "node clean-dist.js"
```
Qui `index.php` è già nella cartella `public/` e Vite compila tutti gli asset statici nella stessa cartella (o la struttura è organizzata diversamente). Il risultato è identico: `index.php` è il file servito da Apache.

## 3. Il Codice di index.php (Analisi Completa)

```php
<?php
/**
 * SEO ENGINE SERVER-SIDE (v1.4.0)
 * Intercetta le richieste di React Router, interroga il database,
 * popola i meta tag HTML (OpenGraph/Twitter) e passa il controllo a React.
 */

// 1. META DI DEFAULT (Fallback per homepage e rotte sconosciute)
$protocol = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off' || $_SERVER['SERVER_PORT'] == 443)
    ? "https://" : "http://";
$metaTitle       = "Nome Sito - Tagline principale";
$metaDescription = "Descrizione generale del sito per SEO";
$metaImage       = $protocol . $_SERVER['HTTP_HOST'] . "/og-default.png";
$currentUrl      = $protocol . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI'];

// 2. ESTRAZIONE SLUG DALL'URL
$request_uri = trim($_SERVER['REQUEST_URI'], '/');
$uri_parts   = explode('/', $request_uri);
$slug = null;

// Escludere l'area admin dal match SEO (la SPA gestisce il suo routing)
if (isset($uri_parts[0]) && $uri_parts[0] === 'admin') {
    $slug = null;
} elseif (count($uri_parts) == 2) {
    // URL tipo /categoria/mio-slug → prende l'ultimo segmento
    $slug = end($uri_parts);
} elseif (count($uri_parts) == 1 && $uri_parts[0] !== '') {
    // URL corto tipo /mio-slug
    $slug = $uri_parts[0];
}

// 3. QUERY DATABASE (Connessione diretta, senza includere api/db.php)
$dbPath = __DIR__ . '/api/.data/database.sqlite';

if ($slug && file_exists($dbPath)) {
    try {
        $pdo = new PDO('sqlite:' . $dbPath);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        // Sanitizzazione: PHP 8.1+ ha deprecato FILTER_SANITIZE_STRING
        $cleanSlug = strip_tags(trim($slug));

        $stmt = $pdo->prepare(
            "SELECT title, excerpt, cover_image
             FROM articles
             WHERE slug = :slug AND status = 'published'
             LIMIT 1"
        );
        $stmt->execute([':slug' => $cleanSlug]);
        $article = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($article) {
            $metaTitle = htmlspecialchars($article['title'], ENT_QUOTES, 'UTF-8') . " | Nome Sito";
            $rawDesc   = $article['excerpt'] ?: "Leggi l'articolo completo.";
            $metaDescription = htmlspecialchars(strip_tags($rawDesc), ENT_QUOTES, 'UTF-8');

            if (!empty($article['cover_image'])) {
                $img = filter_var($article['cover_image'], FILTER_SANITIZE_URL);
                // Rendere il path assoluto se relativo (i bot richiedono URL assoluti)
                if (strpos($img, 'http') !== 0) {
                    $prefix    = (substr($img, 0, 1) !== '/') ? '/' : '';
                    $metaImage = $protocol . $_SERVER['HTTP_HOST'] . $prefix . $img;
                } else {
                    $metaImage = $img;
                }
            }
        }
    } catch (PDOException $e) {
        // Fallback silenzioso: proseguiamo con i meta default
        error_log("SEO Engine DB Error: " . $e->getMessage());
    }
}

// 4. LETTURA E INIEZIONE NELL'HTML DI VITE
$htmlFile = __DIR__ . '/index_react.html'; // o index.html se non rinominato

if (!file_exists($htmlFile)) {
    die("Error: Production HTML not found. Eseguire 'npm run build'.");
}

$htmlContent = file_get_contents($htmlFile);

// Costruzione del blocco SEO da iniettare
$seoInjection = "
    <title>{$metaTitle}</title>
    <meta name=\"title\" content=\"{$metaTitle}\" />
    <meta name=\"description\" content=\"{$metaDescription}\" />
    <meta property=\"og:type\" content=\"website\" />
    <meta property=\"og:url\" content=\"{$currentUrl}\" />
    <meta property=\"og:title\" content=\"{$metaTitle}\" />
    <meta property=\"og:description\" content=\"{$metaDescription}\" />
    <meta property=\"og:image\" content=\"{$metaImage}\" />
    <meta property=\"twitter:card\" content=\"summary_large_image\" />
    <meta property=\"twitter:url\" content=\"{$currentUrl}\" />
    <meta property=\"twitter:title\" content=\"{$metaTitle}\" />
    <meta property=\"twitter:description\" content=\"{$metaDescription}\" />
    <meta property=\"twitter:image\" content=\"{$metaImage}\" />
</head>";

// Operazione chirurgica: rimuove il <title> di Vite e inietta il pacchetto SEO
$htmlContent = preg_replace('/<title>.*?<\/title>/s', '', $htmlContent, 1);
$htmlContent = str_replace('</head>', $seoInjection, $htmlContent);

echo $htmlContent;
?>
```

## 4. Punti Critici del Pattern

### 4.1 Connessione Diretta al DB (No Include Esterno)
`index.php` non deve fare `require_once 'api/db.php'`. Connette direttamente tramite PDO per due motivi:
- Semplicità: evita dipendenze da path relativi che cambiano in base alla posizione del file.
- Performance: connessione read-only, niente sessioni, niente CORS headers.

### 4.2 Sanitizzazione dello Slug
L'uso di `strip_tags(trim($slug))` al posto del deprecato `FILTER_SANITIZE_STRING` garantisce:
- Compatibilità PHP 8.1+.
- Rimozione di eventuali tag HTML iniettati via URL.

### 4.3 Fallback Silenzioso
Il blocco `try-catch` intorno alla query NON mostra errori all'utente. Se il DB non è raggiungibile, serve i meta default. Questo è fondamentale: un errore del SEO Engine non deve rompere l'intera applicazione.

### 4.4 Bypass Admin
Le rotte `/admin/*` non vengono processate dal motore SEO. L'area admin non ha bisogno di Open Graph e include già il proprio ciclo di autenticazione React.

### 4.5 Immagine Assoluta
I bot di social richiedono URL assoluti per `og:image`. La logica trasforma i path relativi (come `/api/uploads/copertina.jpg`) in `https://dominio.com/api/uploads/copertina.jpg`.

## 5. Estensione a Più Entità

Il pattern si estende facilmente a più tipi di contenuto. Basta aggiungere query successive:

```php
// Prima: cercare tra gli articoli
$stmt = $pdo->prepare("SELECT title, excerpt, cover_image FROM articles WHERE slug=? AND status='published' LIMIT 1");

// Poi: se non trovato, cercare tra i progetti
if (!$article) {
    $stmt = $pdo->prepare("SELECT name as title, description as excerpt, cover_image FROM projects WHERE slug=? AND is_visible=1 LIMIT 1");
}
```

## 6. Configurazione Apache (.htaccess)

Il `.htaccess` del Modello Universale (Capitolo 2) gestisce già il routing. Apache serve `index.php` come documento predefinito se presente, prima di `index.html`. Non è necessario alcun aggiornamento delle regole RewriteRule.


## 7. Dynamic Sitemap & Robots.txt (v2.0)

L'evoluzione naturale dal prerendering statico è la generazione dinamica dei file di servizio SEO. Questo elimina la necessità di rigenerare file fisici ogni volta che un articolo viene pubblicato o modificato.

### 7.1 Mappatura via .htaccess
Invece di avere file sitemap.xml e obots.txt reali, usiamo Apache per dirottare le richieste verso script PHP:

`pache
# SEO Files — SEMPRE serviti da PHP (contenuto dinamico real-time)
RewriteRule ^sitemap\.xml$ sitemap.php [L,NC]
RewriteRule ^robots\.txt$ robots.php [L,NC]
`

### 7.2 Robots.php Dinamico
Garantisce che il link alla Sitemap punti sempre al dominio corretto, calcolato dinamicamente:

`php
header("Content-Type: text/plain; charset=utf-8");
 = (!empty(['HTTPS']) && ['HTTPS'] !== 'off') ? "https://" : "http://";
  =  . ['HTTP_HOST'];

echo "User-agent: *" . PHP_EOL;
echo "Allow: /" . PHP_EOL;
echo "Disallow: /admin/" . PHP_EOL;
echo PHP_EOL;
echo "Sitemap: /sitemap.xml" . PHP_EOL;
`

### 7.3 Sitemap.php Dinamica
Recupera categorie, sottocategorie e articoli direttamente dal database.

**Vantaggi Chiave:**
1.  **Real-time:** Un nuovo articolo appare nella sitemap istantaneamente.
2.  **Lastmod Preciso:** Il campo <lastmod> delle categorie viene calcolato in base alla data dell'ultimo articolo pubblicato in quella categoria.
3.  **Zero Manutenzione:** Non serve più uno script di prerendering o una build manuale per aggiornare la SEO.
4.  **BaseUrl Dinamico:** Lo stesso script funziona su localhost, staging e produzione senza modifiche.

---

*Prossimo Capitolo: RSS Feed & Syndication - Come generare feed XML per aggregatori e podcast app.*
