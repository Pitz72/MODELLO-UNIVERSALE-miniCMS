# CAPITOLO 7: Media & Optimization (v1.3 - ADVANCED)

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
2. `.htaccess` -> nessun file fisico trovato -> passa a `index.php`
3. `index.php` interroga SQLite per `slug = 'mio-slug'`
4. Inietta meta tag nell'HTML di Vite via `str_replace('</head>', $seoBlock, $html)`
5. Serve HTML completo al browser/bot

## 3. Ottimizzazione Media & Smart Upload
Il miniCMS evolve verso una gestione professionale degli asset per massimizzare il punteggio PageSpeed e la sicurezza del server.

### 3.1 Smart Upload & Anti-Spoofing
Non è sufficiente controllare l'estensione del file. Il sistema implementa una **validazione MIME rigorosa**:
- **Anti-Spoofing**: Utilizzo di `finfo_file()` per verificare il magic byte reale del file, impedendo il caricamento di script malevoli mascherati da immagini (es. `shell.php.jpg`).
- **Sottocartelle Dinamiche**: Per evitare il rallentamento del file system (limitazione degli inode per cartella), gli upload vengono smistati automaticamente in cartelle basate sulla data: `uploads/YYYY/MM/`. Il database memorizza il path relativo completo.

### 3.2 Normalizzazione Immagini e Auto-WebP (PHP GD)
Non è permesso servire immagini "grezze" caricate dall'utente. Il backend PHP (script di upload) implementa due passi inderogabili:
- **Ridimensionamento geometrico**: Scale-down proporzionale automatico a **max 1920px** (larghezza) o 1080px (altezza). Questo abbatte il peso dei file caricati da smartphone o fotocamere professionali (spesso >10MB) a pochi KB.
- **Transcodifica obbligatoria WebP**: Conversione on-the-fly via PHP GD (`imagewebp()`). Il formato WebP garantisce una riduzione del peso del 30-50% rispetto a JPG/PNG mantenendo una qualità visiva eccellente.

### 3.3 Sharp (Node.js) per Image Processing Build-Time
**SimonePizziWebSite** introduce `sharp` come dipendenza Node.js per il processing di immagini in fase di build o come utility script. Sharp è più performante di PHP GD per batch processing e supporta formati moderni (AVIF, WebP) con qualità superiore. Non è un'alternativa al backend PHP per upload live — è complementare per pre-processing di asset statici.

### 3.4 Cache Control sui File Statici
Tramite `.htaccess`, i file nella cartella `uploads/` devono essere serviti con header di cache a lungo termine:
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
Il sistema include script protetti per operazioni straordinarie:
- **rebuild_seo_cache.php**: Rigenera i file JSON SEO.
- **optimize_db.php**: Esegue `VACUUM` e `ANALYZE` (SQLite) o `OPTIMIZE TABLE` (MySQL).

## 5. Portabilità Dati: Full Content Exporter
Per prevenire il vendor lock-in e facilitare i backup migratori, il miniCMS include un **Full Content Exporter** nell'area admin:
- **Meccanismo**: Genera dinamicamente un file **ZIP** contenente l'intero database (dump SQL o file .sqlite) e la cartella `uploads/` completa.
- **Sicurezza**: Lo script di export deve verificare i permessi admin e cancellare lo ZIP temporaneo dopo il download per non occupare spazio inutile e non esporre dati sensibili.

## 6. Benefici Tecnici
- **PageSpeed**: L'uso combinato di WebP, Resize e Caching JSON porta il punteggio LCP (Largest Contentful Paint) sotto i 1.2s.
- **Sicurezza**: La validazione MIME frena l'80% degli attacchi di tipo RCE (Remote Code Execution) legati agli upload.

---
*Prossimo Capitolo: Advanced Content Editing & Media Integration - L'editor definitivo.*
