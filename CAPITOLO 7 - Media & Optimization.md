# CAPITOLO 7: Media & Optimization (v1.2 - ADVANCED)

Per garantire un'esperienza utente istantanea e un'indicizzazione SEO perfetta, il Modello Universale adotta strategie di caching aggressivo e pre-rendering dei metadati.

## 1. Architettura di Caching (The TTL Strategy)
Il database non deve essere interrogato per query di sola lettura ripetitive. Il sistema implementa un caching basato su file JSON.

### 1.1 Cache Paginata (Listings)
Ogni richiesta di lista (es. `news.php?page=1`) genera un file univoco in `.cache/` (es. `news_p1_l10.json`).
- **Validità**: Il file viene servito direttamente se creato meno di 300 secondi fa.
- **Header di Tracciamento**: Il sistema deve inviare `X-Cache: HIT` o `X-Cache: MISS` per monitorare l'efficienza del sistema.

### 1.2 Invalidazione Intelligente
Ad ogni operazione di scrittura (`POST`), il backend deve pulire la cartella `.cache/` per garantire che il pubblico veda immediatamente le nuove modifiche, evitando il "vizio" dei dati obsoleti.

## 2. SEO & Social Pre-rendering
Le Single Page Application (SPA) hanno problemi di SEO. Il Modello Universale risolve questo problema con un **PHP Entry-Point** (non una cache file JSON separata come in approcci precedenti).

### 2.1 Il Meccanismo (Riferimento Completo: Capitolo 11)
L'`index.php` nella root pubblica intercetta tutte le richieste, estrae lo slug dall'URL, interroga direttamente il database SQLite, e inietta i meta tag `og:title`, `og:description` e `og:image` nell'HTML generato da Vite prima di servirlo. I bot di social e i motori di ricerca ricevono HTML completo con meta tag corretti.

**Flusso**:
1. Apache riceve richiesta `/categoria/mio-slug`
2. `.htaccess` → nessun file fisico trovato → passa a `index.php`
3. `index.php` interroga SQLite per `slug = 'mio-slug'`
4. Inietta meta tag nell'HTML di Vite via `str_replace('</head>', $seoBlock, $html)`
5. Serve HTML completo al browser/bot

### 2.2 Il Rebuild Cache SEO (Per Retrocompatibilità)
SitoRuntime include ancora `rebuild_seo_cache.php`, uno script di manutenzione che rigenera file JSON di cache SEO per entità pre-esistenti nel database. Utile per migrazioni e fix straordinari. Da eliminare dopo l'uso in produzione.

## 3. Ottimizzazione Media & Compression
### 3.1 Normalizzazione delle Immagini (PHP GD)
Non è permesso servire immagini "grezze" caricate dall'utente. Il backend PHP deve:
- Ridimensionare a max 1920px (larghezza) o 1080px (altezza).
- Applicare una compressione del 85% per JPEG/WebP.
- Convertire (opzionale) in formati moderni come WebP per ridurre il peso del 30-50% rispetto al JPEG.

### 3.2 Sharp (Node.js) per Image Processing Build-Time
**SimonePizziWebSite** introduce `sharp` come dipendenza Node.js per il processing di immagini in fase di build o come utility script. Sharp è più performante di PHP GD per batch processing e supporta formati moderni (AVIF, WebP) con qualità superiore. Non è un'alternativa al backend PHP per upload live — è complementare per pre-processing di asset statici.

```json
// package.json
"dependencies": {
    "sharp": "^0.34.5"
}
```

### 3.3 Cache Control sui File Statici
Tramite `.htaccess`, i file nella cartella `uploads/` devono essere serviti con header di cache a lungo termine (`Expires`, `Cache-Control: max-age=31536000`), poiché una volta caricati non cambiano mai nome (grazie all'hash `uniqid()`).

```apacheconf
<IfModule mod_expires.c>
    ExpiresActive On
    <FilesMatch "\.(jpg|jpeg|png|gif|webp|svg|ico)$">
        ExpiresDefault "access plus 1 year"
        Header set Cache-Control "max-age=31536000, public"
    </FilesMatch>
</IfModule>
```

## 4. Manutenzione e Rebuilding
Il sistema deve includere script protetti (`rebuild_seo_cache.php`, `optimize_db.php`) per operazioni di manutenzione straordinaria:
- **rebuild_seo_cache.php**: Rigenera i file JSON SEO per tutte le entità del database. Da eseguire dopo una migrazione o un cambio di struttura metadati.
- **optimize_db.php**: Esegue `VACUUM` e `ANALYZE` sul database. Riduce il peso del file e ottimizza i piani di query.

**Entrambi vanno eliminati dal server dopo l'uso** — includono output HTML non JSON e possono esporre informazioni interne se accessibili pubblicamente.

---
*Prossimo Capitolo: Advanced Content Editing & Media Integration - L'editor definitivo.*
