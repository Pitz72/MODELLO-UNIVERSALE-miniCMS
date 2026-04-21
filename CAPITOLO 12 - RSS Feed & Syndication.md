# CAPITOLO 12: RSS Feed & Syndication (v1.0)

Il feed RSS è il canale di distribuzione automatica dei contenuti verso aggregatori, lettori di notizie, podcast app e motori di ricerca. Tutti i siti del Modello Universale implementano almeno un feed: **SimonePizziWebSite** (`rss.php`), **SitoRuntime** (`feed_news_rss.php`), **DISINTELLIGENZA** e **FDCA** (`feed.php`). Questo capitolo consolida il pattern standard.

## 1. Struttura del Feed RSS Standard

Un feed RSS valido richiede un header HTTP preciso e una struttura XML rigorosa:

```php
<?php
require_once 'db.php';

// Header fondamentale: senza questo, i lettori RSS rifiutano il feed
header('Content-Type: application/rss+xml; charset=utf-8');

$pdo = Database::connect();

// Recupero dinamico del protocollo e del dominio
$protocol = (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on') ? 'https' : 'http';
$host     = $_SERVER['HTTP_HOST'];
$base_url = $protocol . '://' . $host;

// Forzatura del fuso orario per siti su hosting internazionali (es. Los Angeles)
date_default_timezone_set('Europe/Rome');
$now_str = date('Y-m-d H:i:s');

define('RSS_FEED_LIMIT', 50); // Numero massimo di articoli nel feed

$site_title       = "Nome del Sito";
$site_description = "Descrizione del sito per il feed RSS";

echo '<?xml version="1.0" encoding="UTF-8" ?>' . "\n";
echo '<rss version="2.0">' . "\n";
echo '<channel>' . "\n";
echo '  <title>' . htmlspecialchars($site_title) . '</title>' . "\n";
echo '  <link>' . htmlspecialchars($base_url) . '</link>' . "\n";
echo '  <description>' . htmlspecialchars($site_description) . '</description>' . "\n";
echo '  <language>it-IT</language>' . "\n";

try {
    $stmt = $pdo->prepare(
        "SELECT id, title, slug, excerpt, content, cover_image, category, published_at
         FROM articles
         WHERE status = 'published'
           AND (published_at IS NULL OR published_at = '' OR published_at <= :now)
         ORDER BY published_at DESC
         LIMIT " . RSS_FEED_LIMIT
    );
    $stmt->execute([':now' => $now_str]);
    $articles = $stmt->fetchAll();

    foreach ($articles as $article) {
        // Formato data secondo RFC 822 (obbligatorio per RSS 2.0)
        $pubDate  = date(DATE_RSS, strtotime($article['published_at'] ?? 'now'));
        $item_url = $base_url . '/' . rawurlencode($article['category']) . '/' . rawurlencode($article['slug']);
        $guid     = 'urn:tuosito:article:' . $article['id'];

        echo '  <item>' . "\n";
        echo '    <title>' . htmlspecialchars($article['title']) . '</title>' . "\n";
        echo '    <link>' . htmlspecialchars($item_url) . '</link>' . "\n";
        echo '    <description>' . htmlspecialchars($article['excerpt']) . '</description>' . "\n";
        echo '    <pubDate>' . $pubDate . '</pubDate>' . "\n";
        echo '    <guid isPermaLink="false">' . htmlspecialchars($guid) . '</guid>' . "\n";

        // Enclosure per immagine (utile per aggregatori che mostrano preview)
        if (!empty($article['cover_image'])) {
            $img_url = str_starts_with($article['cover_image'], 'http')
                ? $article['cover_image']
                : $base_url . '/' . ltrim($article['cover_image'], '/');
            echo '    <enclosure url="' . htmlspecialchars($img_url) . '" type="image/jpeg" />' . "\n";
        }

        echo '  </item>' . "\n";
    }
} catch (Exception $e) {
    // Fallback silenzioso: il feed rimane valido anche senza articoli
}

echo '</channel>' . "\n";
echo '</rss>';
```

## 2. Dettagli Tecnici Critici

### 2.1 Il Problema del Fuso Orario
Su hosting internazionali (es. server fisicamente a Los Angeles), `date()` e `strtotime()` usano il timezone del server. Un articolo programmato alle **10:00 ora italiana** risulterebbe pubblicato alle **01:00 Pacific Time**, rompendo la logica di filtro `published_at <= NOW()`.

**Soluzione**: `date_default_timezone_set('Europe/Rome')` all'inizio del file. Questa istruzione deve precedere qualsiasi uso di `date()` o `time()`. Pattern valido anche in `articles.php`, `news.php` e qualsiasi endpoint con logica temporale.

```php
// All'inizio del file, prima di qualsiasi uso di date()
date_default_timezone_set('Europe/Rome');
$ita_now_str  = date('Y-m-d H:i:s'); // Ora italiana corretta
$ita_now_time = time();               // Timestamp Unix corretto
```

### 2.2 Formato Data RFC 822
RSS 2.0 richiede date nel formato RFC 822. PHP fornisce la costante `DATE_RSS` che genera il formato corretto:
```
Mon, 24 Mar 2026 10:00:00 +0100
```
Non usare mai ISO 8601 (`Y-m-d\TH:i:s`) in un feed RSS: molti lettori lo rifiutano.

### 2.3 URL degli Articoli nel Feed
L'URL deve essere **assoluto e correttamente encodato**:
```php
$item_url = $base_url . '/' . rawurlencode($article['category']) . '/' . rawurlencode($article['slug']);
```
`rawurlencode()` gestisce spazi, accenti e caratteri speciali nei category slug. Non usare `urlencode()` (sostituisce gli spazi con `+` invece che `%20`).

### 2.4 Enclosure per Immagini
Il tag `<enclosure>` permette agli aggregatori di mostrare l'immagine di anteprima dell'articolo nel feed. Richiede URL assoluto — i path relativi (`/api/uploads/...`) non funzionano:
```php
$img_url = str_starts_with($article['cover_image'], 'http')
    ? $article['cover_image']                                   // Già assoluto
    : $base_url . '/' . ltrim($article['cover_image'], '/');    // Rendi assoluto
```

### 2.5 GUID Univoco
Il tag `<guid>` identifica univocamente ogni articolo nel feed. **Mai usare l'URL dell'articolo come GUID**. 
L'esperienza reale (Incidente Titan Desktop v1.7.3) ha dimostrato che qualora vi sia in futuro un refactoring delle URL (es. cambio struttura categorie nel CMS), i bot degli aggregatori e i bot di Telegram considereranno tutti gli articoli con nuova URL come contenuti "nuovi", ri-pubblicandoli e generando spam gravissimo.

**Soluzione Definitiva**: Usare uno standard URN crittografico, totalmente svincolato dal nome dominio o dal percorso cartelle, basato sull'ID nativo di database: 
`<guid isPermaLink="false">urn:tuosito:article:{id}</guid>`.
In questo modo anche se l'URL e le tassonomie cambiano 100 volte, il bot tratterà il contenuto come "entità già vista".

## 3. Feed RSS per Podcast (Podcast App)

SitoRuntime implementa anche un feed per podcast nel formato Apple Podcasts / Spotify. Il feed podcast ha requisiti aggiuntivi rispetto al feed news:

```php
// Namespace iTunes obbligatorio per podcast app
echo '<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">' . "\n";
echo '<channel>' . "\n";
echo '  <itunes:author>Nome Autore</itunes:author>' . "\n";
echo '  <itunes:category text="Technology" />' . "\n";

// Per ogni episodio:
echo '  <item>' . "\n";
echo '    <title>' . htmlspecialchars($ep['title']) . '</title>' . "\n";
echo '    <enclosure url="' . $audio_url . '" type="audio/mpeg" length="' . $ep['file_size'] . '" />' . "\n";
echo '    <itunes:duration>' . $ep['duration'] . '</itunes:duration>' . "\n";
echo '  </item>' . "\n";
```

## 4. Registrazione del Feed nel Routing

Il feed deve essere accessibile tramite URL dedicato. Con il `.htaccess` del Modello Universale (che reindirizza tutto a `index.php`), i file PHP fisici sono già serviti direttamente — non servono configurazioni aggiuntive per `rss.php` o `feed.php`.

**URL consigliati**:
- `/api/rss.php` — feed notizie standard
- `/api/feed.php` — alias alternativo
- `/api/feed_news_rss.php` — naming esplicito SitoRuntime

## 5. Integrazione nel Frontend (Discovery)

Il feed RSS deve essere **annunciato** nell'`<head>` HTML per permettere ai browser e ai lettori RSS di scoprirlo automaticamente. Il blocco va aggiunto all'`index.php` (SEO engine) o all'`index.html` base:

```html
<link rel="alternate" type="application/rss+xml"
      title="Nome Sito - Feed Notizie"
      href="/api/rss.php" />
```

---
*Prossimo Capitolo: Newsletter & Email System - La lista email come asset posseduto, indipendente dalle piattaforme.*
