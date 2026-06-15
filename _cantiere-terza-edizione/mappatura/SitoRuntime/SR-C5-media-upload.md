# Mappatura — SitoRuntime — C5: Media & Upload (lato server)

> **Stato:** COMPLETATO
> **Sessione:** 15 · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `SitoRuntime/`)
> - `public/api/upload.php` (ricezione `$_FILES['file']`, validazione estensione + magic bytes, naming `uniqid`, conversione WebP via GD, risposta `{success,url}`)
> - `public/api/media.php` (libreria FILESYSTEM-based: GET lista `scandir`, POST `action=delete` con `unlink`; gate solo-sessione)
> - `public/api/admin.php:25-47` (`adminImageToWebP` — GD helper gemello di quello in upload.php) e `:347-371`, `:472-523` (one-shot `optimize_webp` e `fix_image_paths`)
> - `public/.htaccess` (hardening globale — **VERIFICA: nessun PHP-off su `uploads/`**)
> - `public/api/init_mysql.php` (schema — **conferma: nessuna tabella `media`**)
> - `src/api.ts:71-80` (firma client `uploadImage` — già mappata LATO CLIENT in SR-C3)

## 1. Cosa fa (sintesi narrativa)

C5 è il **lato server dei media** di SitoRuntime: come un'immagine caricata dalla dashboard arriva su
disco, viene validata e ottimizzata, e come la libreria media la elenca/cancella. Ma rispetto a
SPW-C5 il modello è **radicalmente più minimale**, ed è l'osservazione centrale: **non esiste una
tabella `media`, non esiste un `download.php`, non esistono sottocartelle, non esiste un
`uploads/.htaccess`.** Tutto si riduce a **due endpoint** che lavorano su una cartella piatta
`public/uploads/` creata a runtime.

Il flusso:

1. **`upload.php`** — riceve **un'immagine** (`$_FILES['file']`, dal client di SR-C3). Solo `POST`,
   **gated `isLoggedIn()` + `validateCsrf()` in testa** (`upload.php:8,13`). Validazione a **doppio
   strato**: estensione contro whitelist **solo-immagini** (`jpg/jpeg/png/webp/gif`, `upload.php:31`),
   poi `finfo` magic-bytes contro whitelist MIME (`upload.php:40-49`). Genera un nome **`uniqid('',true)`
   e basta** — il nome originale del file è **scartato del tutto** (`upload.php:62`). Se GD è
   disponibile e non è una GIF, **converte in WebP** (resize max 1920px, qualità 82, EXIF strippato),
   altrimenti tiene il formato originale. Salva nella cartella **piatta** `/uploads/` e risponde
   `{success:true, url}`. **Nessun INSERT a DB** (non c'è tabella).

2. **`media.php`** — la **libreria, ma basata sul filesystem**. `GET ?action=list` (default) fa
   `scandir('/uploads/')` e ritorna `{success, files:[{name,url,size,date}]}` ordinati per data disco
   discendente — **i metadati vengono dal filesystem, non da un DB**. `POST ?action=delete` cancella
   il file con `unlink` dopo un path-guard **minimale** (`basename($filename)`). Curiosità: `media.php`
   fa `require_once 'db.php'` ma **non usa mai il DB** (fossile/copia-incolla), e — punto critico —
   **non include `auth_utils.php`**: usa un `session_start()` nudo e controlla `$_SESSION['user_id']`
   a mano, **senza `validateCsrf()`** sulla delete (vedi §4, GOLD sicurezza).

Non c'è il terzo endpoint di SPW (`download.php`): i file sono serviti **direttamente da Apache** come
statici (il `.htaccess` globale ha `RewriteCond %{REQUEST_FILENAME} -f → [L]`, `public/.htaccess:63-64`),
senza proxy, senza `Content-Disposition`, senza nome "umano" (che del resto non esiste, vedi sotto).

## 2. Pattern miniCMS rilevanti

- **Validazione upload a doppio strato (estensione + magic bytes), ma solo-immagini.** `upload.php:31-49`:
  prima la whitelist di estensioni (`jpg/jpeg/png/webp/gif`), poi `finfo_file()` legge i byte reali e
  li confronta con la whitelist MIME (`image/jpeg|png|webp|gif`). Stesso principio "non fidarti
  dell'estensione" di SPW, ma il **dominio è ristretto alle immagini**: niente PDF/ZIP/MP3 (SitoRuntime
  carica solo cover/foto). Più semplice = meno superficie.
- **Naming per ELISIONE TOTALE del nome utente.** `upload.php:62` `$baseId = uniqid('', true)` e il
  file finale è `uniqid.webp` (o `uniqid.<ext>`). A differenza di SPW (`uniqid.'-'.baseRipulita.'.'.ext`,
  che conserva una versione pulita del nome), SitoRuntime **butta via il nome originale**. È
  l'anti-doppia-estensione portato all'estremo: non c'è nessuna stringa controllata dall'utente nel
  nome finale → impossibile costruire `shell.php.jpg`. Costo: si perde del tutto il nome "umano" (vedi
  §4, e il fatto che senza tabella `media` non c'è dove salvarlo comunque).
- **Conversione WebP + resize sincrona dentro l'endpoint** (`upload.php:63-89,94-123`): niente coda,
  niente worker. `imageToWebP()` (GD) converte jpeg/png/webp → WebP, ridimensiona se la larghezza
  supera 1920px (alpha PNG preservato), qualità 82. La **GIF è esclusa** dalla conversione
  (`$mime !== 'image/gif'`, `upload.php:63`) e tenuta com'è → anima preservata (scelta opposta-ma-equivalente
  a SPW, che la converte perdendo l'animazione). Degradazione graziosa: se `imagewebp` manca o GD
  fallisce, si tiene l'originale (`upload.php:63,76-78`).
- **EXIF strippato "gratis" dalla ri-codifica GD** (`upload.php:93` commento): passando l'immagine per
  `imagecreatefrom*` → `imagewebp`, i metadati EXIF (geolocalizzazione, device) **non sopravvivono**.
  È una difesa privacy *collaterale* della conversione, non cercata esplicitamente — ma reale e
  citabile. SPW non la annota.
- **Libreria media basata sul FILESYSTEM, non sul DB** (`media.php:24-49`): la lista non interroga una
  tabella, fa `scandir('/uploads/')` e ricava `name/url/size/date` da `filesize()`/`filemtime()`. È il
  "thin stack" all'estremo: il disco **è** il database dei media. Conseguenza: nessun `mime_type`
  salvato, nessun nome originale, nessuna data di "caricamento logico" (solo `mtime` del file).
- **Difesa upload a UN solo livello (applicativo).** A differenza dei tre livelli di SPW (.htaccess
  PHP-off + naming senza punti + MIME check), in SitoRuntime **manca del tutto l'`.htaccess` su
  `uploads/`** e il `.htaccess` globale non spegne PHP nella cartella. L'unica barriera è la
  validazione applicativa di `upload.php` (whitelist immagini + MIME + naming `uniqid.webp` che forza
  un'estensione immagine). Robusta *finché* `upload.php` è l'unica via di scrittura, ma senza la
  ridondanza "cintura e bretelle" di SPW (vedi §4, GOLD).
- **Path-guard minimale `basename()`** (`media.php:57`): la delete fa `basename($filename)` per
  neutralizzare `../`. Funziona contro il traversal classico, ma è più debole del path-guard
  `realpath + str_starts_with` di SPW (che verifica che il path risolto stia *davvero* dentro
  `/uploads/`). Qui `basename` impedisce di uscire dalla cartella, ma non c'è un secondo controllo.
- **WebP helper duplicato in due file** (`upload.php:94 imageToWebP` ≡ `admin.php:25 adminImageToWebP`):
  la stessa funzione GD (resize 1920 + qualità 82 + alpha PNG) è copia-incollata in `upload.php` (per
  i nuovi upload) e in `admin.php` (per l'one-shot `optimize_webp` sui file vecchi). Duplicazione
  classica del thin stack senza libreria condivisa.

## 3. Codice chiave (stralci con origine)

**Validazione doppio strato solo-immagini + gate in testa** — `upload.php:8-49`:

```php
if (!isLoggedIn()) { http_response_code(401); echo json_encode(['error'=>'Unauthorized']); exit; }
validateCsrf();
// ...
$allowedExts = ['jpg','jpeg','png','webp','gif'];
$ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
if (!in_array($ext, $allowedExts)) { /* 400 */ }

$finfo = finfo_open(FILEINFO_MIME_TYPE);
$mime  = finfo_file($finfo, $tmpName);          // magic bytes reali
finfo_close($finfo);
$allowedMimes = ['image/jpeg','image/png','image/webp','image/gif'];
if (!in_array($mime, $allowedMimes)) { /* 400: "Upload blocked for security." */ }
```

**Naming per elisione totale + WebP sincrona + flat /uploads/** — `upload.php:57-91`:

```php
$uploadDir = __DIR__ . '/../uploads/';          // <-- cartella PIATTA, nessuna sottocartella
$baseId  = uniqid('', true);                    // <-- il nome originale è SCARTATO
$useWebP = function_exists('imagewebp') && $mime !== 'image/gif';   // GIF esclusa (anima preservata)

if ($useWebP) {
    $tempPath = $uploadDir . $baseId . '.' . $ext;
    move_uploaded_file($tmpName, $tempPath);
    $destPath = $uploadDir . $baseId . '.webp';
    if (imageToWebP($tempPath, $destPath, $mime)) {
        unlink($tempPath);
        $publicUrl = '/uploads/' . $baseId . '.webp';
    } else { $publicUrl = '/uploads/' . $baseId . '.' . $ext; }   // GD fallita: tieni l'originale
} else {
    move_uploaded_file($tmpName, $uploadDir . $baseId . '.' . $ext);
    $publicUrl = '/uploads/' . $baseId . '.' . $ext;
}
echo json_encode(['success' => true, 'url' => $publicUrl]);       // NB: no id, no name, no DB
```

**Conversione WebP via GD (EXIF strippato dalla ri-codifica)** — `upload.php:93-123`:

```php
// Converte un'immagine in WebP via GD. EXIF strippato automaticamente da GD.
function imageToWebP(string $src, string $dest, string $mime, int $quality = 82): bool {
    $im = match ($mime) {
        'image/jpeg' => imagecreatefromjpeg($src),
        'image/png'  => imagecreatefrompng($src),
        'image/webp' => imagecreatefromwebp($src),
        default      => false,
    };
    if (!$im) return false;
    if (imagesx($im) > 1920) { /* imagecopyresampled a 1920px, alpha PNG preservato */ }
    $ok = imagewebp($im, $dest, $quality);
    imagedestroy($im);
    return $ok;
}
```

**Libreria FILESYSTEM (niente DB) + gate solo-sessione SENZA CSRF** — `media.php:1-57`:

```php
require_once 'db.php';        // <-- caricato ma MAI usato (fossile)
session_start();              // <-- NON include auth_utils.php
if (!isset($_SESSION['user_id'])) { http_response_code(401); /* ... */ exit; }

// GET list: i metadati vengono dal DISCO
foreach (scandir($uploadDir) as $file) {
    if ($file === '.' || $file === '..') continue;
    if (is_file($uploadDir.$file)) $files[] = [
        'name'=>$file, 'url'=>'/uploads/'.$file, 'size'=>filesize(...), 'date'=>filemtime(...)
    ];
}
echo json_encode(['success'=>true, 'files'=>$files]);

// POST delete: NESSUN validateCsrf(), path-guard solo basename()
$filename = basename($input['filename'] ?? '');     // unica difesa traversal
if (file_exists($uploadDir.$filename)) unlink($uploadDir.$filename);
```

**Verifica `.htaccess` globale: nessun PHP-off su uploads** — `public/.htaccess:32-35,62-64`:

```apache
# Blocca SOLO gli script di manutenzione (per prefisso), NON gli upload
<FilesMatch "^(debug_|test_|emergency_|migrate_|fix_|init_|rebuild_|setup_|optimize_)">
    Deny from all
</FilesMatch>
# Se il file esiste fisicamente → servilo direttamente (statico). Nessun "engine off" per /uploads/.
RewriteCond %{REQUEST_FILENAME} -f
RewriteRule ^ - [L]
```

## 4. Problemi riscontrati & soluzioni

- **GOLD sicurezza (1) — `media.php` delete senza CSRF + senza `auth_utils`.** `media.php` **non
  include** `auth_utils.php`: fa un `session_start()` nudo (`media.php:4`) e controlla solo
  `$_SESSION['user_id']` (`media.php:9`). Il ramo `POST ?action=delete` (`media.php:52`) **non chiama
  `validateCsrf()`**, a differenza di `upload.php` (`upload.php:13`) e di tutti i rami mutativi di
  `admin.php`/`speakers.php`/`podcasts.php` (SR-C2). Risultato: una mutazione di stato (cancellazione
  file) **protetta solo dal cookie di sessione**, quindi **vulnerabile a CSRF** — un sito malevolo può
  far cancellare file all'admin loggato con una POST cross-site (il cookie è `SameSite=Strict` di
  SR-C2, che mitiga ma è l'unica barriera; e manca anche il check `isAdmin`, basta un editor loggato).
  Incoerenza netta con la difesa CSRF a token del resto del sito. Box "l'endpoint che si è dimenticato
  il token" (alto valore, ponte SR-C2 §8).
- **GOLD sicurezza (2) — difesa upload a UN livello: manca `uploads/.htaccess` (PHP-off).** VERIFICATO
  (era il dubbio aperto di SR-C2 §8): **non esiste** `public/uploads/.htaccess` (la cartella non è
  nemmeno nel repo, è creata a runtime da `mkdir`), e il `.htaccess` globale **non spegne PHP** in
  `uploads/` (nessun `php_flag engine off` / `RemoveHandler` / `SetHandler`). L'unica protezione
  contro un eventuale `.php` caricato sono le **whitelist applicative** di `upload.php` (estensione
  immagini + MIME + naming `uniqid.webp`). Manca la ridondanza "cintura e bretelle" di SPW (3 livelli):
  qui se `upload.php` venisse aggirato (o si aggiungesse un secondo punto di scrittura non validato),
  non c'è una seconda barriera. Box "una sola barriera non è difesa in profondità" (ponte SPW-C5).
- **Nessuna tabella `media`: la libreria è il filesystem.** `init_mysql.php` non crea alcuna tabella
  `media` (≠ SPW). `media.php` elenca via `scandir`. Conseguenze pratiche: (a) **niente nome originale
  e niente `mime_type` salvati** (impossibili da recuperare: `upload.php` li ha scartati); (b)
  l'ordinamento è per `filemtime` (data fisica del file), non per una colonna `created_at`; (c) la
  "libreria" mostra **tutti** i file nella cartella, inclusi eventuali residui/temporanei. Semplice ma
  fragile. Box "quando il disco è il tuo database dei media".
- **Riferimenti pendenti (dangling) impossibili da tracciare.** Come in SPW, cancellare un file da
  `media.php` **non** aggiorna `news.cover_image`/`speakers.image`/`podcasts.image` (che salvano la
  stringa URL, C4). Ma qui è **peggio**: senza tabella `media` non c'è nemmeno un reference-count o un
  punto unico da cui partire — il legame URL↔file è puramente testuale e invisibile. Box "il costo di
  non avere nemmeno una tabella per i media".
- **Path-guard più debole (`basename` vs `realpath`).** `media.php:57` usa solo `basename($filename)`.
  Blocca `../../etc/passwd` (diventa `passwd`), ma non c'è il secondo controllo `realpath ∈ /uploads`
  di SPW. Combinato con l'assenza di CSRF, la delete è il punto più fragile di C5.
- **Storage piatto + storia migratoria negli one-shot di `admin.php`.** SitoRuntime non ha mai avuto
  sottocartelle: tutto in `/uploads/` piatto. L'evoluzione che si legge negli script one-shot di
  `admin.php` è **da raster a WebP**: `optimize_webp` (`admin.php:347-371`) converte i jpg/png già
  presenti in `.webp` e fa `UPDATE news SET content = REPLACE(content, '/uploads/x.jpg',
  '/uploads/x.webp')`; `fix_image_paths` (`admin.php:472-523`) riallinea `news.cover_image` e
  `speakers.image` ai `.webp` su disco. La sequenza (upload raster → batch WebP → fix dei riferimenti)
  è il gemello dell'evoluzione storage di SPW, ma **senza** il passaggio "sottocartelle". → la *logica*
  WebP è C5; la *storia migratoria* (e il fatto che vivano in `admin.php`) → **C13**.
- **`media.php` carica `db.php` inutilmente.** `require_once 'db.php'` (`media.php:3`) è un fossile:
  il file non apre mai una connessione. Innocuo (lazy, `Database::connect()` non è chiamato) ma è
  rumore che tradisce un copia-incolla da un template DB-based mai completato. → annotazione.
- **L'ottimizzazione sincrona blocca la risposta.** Come SPW: la conversione WebP avviene dentro il
  request di upload; su immagini grandi l'utente aspetta GD. Accettabile (sito a basso traffico, e
  il client SR-C3 ha solo uno spinner `uploading`, niente barra). Limite noto del thin stack.

## 5. Estetica / UX (moderna ma funzionale)

C5 è back-end, ma serve esperienze visibili:

- **WebP automatico = pagine leggere senza che l'admin ci pensi.** L'admin carica una foto speaker o
  una cover da qualche MB e sul sito finisce un WebP ≤1920px da poche centinaia di KB. Ottimizzazione
  invisibile (ponte allo spinner di upload di SR-C3).
- **EXIF strippato = privacy collaterale.** Caricando la foto di uno speaker, la ri-codifica GD
  rimuove i metadati (device, eventuale GPS) senza che nessuno lo chieda. Micro-cortesia di privacy
  costruita lato server, gratis.
- **GIF preservata animata.** A differenza di SPW (che appiattisce la GIF in un frame), SitoRuntime la
  tiene com'è → un meme/clip animata resta animata. Scelta UX opposta ma sensata per un sito radio
  "vivace".
- **Libreria media a griglia da `scandir`.** La galleria admin (SR-C3 `MediaGallery`) mostra tutto il
  contenuto di `/uploads/` ordinato per data: semplice, immediato, ma senza paginazione né filtri
  (cresce all'infinito).

## 6. Differenze rispetto agli altri siti

Il confronto con **SPW-C5** è il cuore della card: stessa filosofia di base (upload validato + WebP
via GD nel thin stack), ma **SitoRuntime è la versione "scarnificata"** su quasi ogni asse.

| Aspetto | SimonePizziWebSite (SPW-C5) | SitoRuntime (questa card) |
|---|---|---|
| **Tabella `media`** | **sì** (`filename` umano, `file_path`, `mime_type`, `size`, `created_at`) | **NO**: libreria = `scandir` del filesystem |
| **Tipi accettati** | immagini + `pdf/zip/rar/mp3` (con fallback octet-stream) | **solo immagini** (`jpg/jpeg/png/webp/gif`) |
| **Validazione** | doppio strato estensione + magic bytes | doppio strato estensione + `finfo` magic bytes (identico principio) |
| **Naming** | `uniqid.'-'.baseRipulita.'.'.ext` (conserva nome pulito, senza punti) | **`uniqid('',true)` e basta** (nome originale **scartato**) |
| **Sottocartelle** | `immagini`/`documenti`/`file` per MIME | **flat** `/uploads/` (mai avute sottocartelle) |
| **WebP** | GD sync, resize 1920 q82; GIF → frame statico | GD sync, resize 1920 q82; **GIF preservata animata** (esclusa); EXIF strippato (annotato) |
| **`download.php` proxy** | **sì** (pubblico, `readfile`, `Content-Disposition` nome umano, path-guard) | **NO**: file serviti statici da Apache (`-f → [L]`) |
| **Path-guard delete** | `realpath` + `str_starts_with($uploadsBase)` | **solo `basename()`** (più debole) |
| **CSRF sulla delete** | `Auth::check()` (gate completo) | **NESSUN `validateCsrf`**, solo `$_SESSION['user_id']` (vulnerabile, GOLD §4) |
| **Include auth** | `auth_helper.php` | `media.php` **non** include `auth_utils.php` (session nuda); `upload.php` sì |
| **`uploads/.htaccess` PHP-off** | **presente** (difesa in profondità a 3 livelli) | **ASSENTE** (difesa a 1 livello applicativo) — VERIFICATO |
| **Risposta upload** | `{status, url, id, name}` | `{success, url}` (no id/name, non c'è DB) |
| **Helper WebP** | uno solo | **duplicato** (`upload.php` ≡ `admin.php`) |

Sintesi: dove SPW-C5 è "difesa in profondità + tracciamento DB + download cortese", **SitoRuntime-C5
è minimalismo spinto**: niente tabella, niente proxy, niente sottocartelle, niente `.htaccess` di
cartella, naming che cancella il nome utente. Alcune scelte sono **più sicure per sottrazione** (il
naming `uniqid.webp` elimina ogni input utente dal nome file), altre **più fragili** (delete senza
CSRF, una sola barriera anti-RCE, path-guard `basename`). Il confronto è oro per il capitolo "quanto
puoi togliere a un sistema di upload prima che diventi insicuro".

Per DISINTELLIGENZA/FDCA (SQLite, festival): verificare se l'upload è gated come qui o più aperto
(iscrizioni → possibile upload pubblico di materiali). Termine di paragone "minimo" al pattern
sicurezza.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **Validazione upload a doppio strato, solo-immagini** | Cap. "Caricare file senza farsi bucare": variante ristretta |
| **Naming per elisione totale** (`uniqid` puro, nome utente scartato) | Box "il modo più sicuro di nominare un upload: non fidarsi affatto del nome" |
| **WebP + resize sincrona via GD** (helper duplicato) | Cap. "Image processing senza worker": SR vs SPW |
| **EXIF strippato dalla ri-codifica GD** | Box "la privacy che ottieni gratis convertendo in WebP" |
| **GIF preservata animata vs appiattita** | Box "una scelta di conversione, due esiti UX" (ponte SPW-C5) |
| **Libreria media = `scandir` del filesystem** (niente tabella) | Cap. "Quando il disco è il tuo database dei media" (alto valore) |
| **GOLD: delete senza CSRF + path-guard `basename`** | Box problemi/soluzioni "l'endpoint mutativo che si è dimenticato il token" (ponte SR-C2) |
| **GOLD: difesa upload a 1 livello (manca uploads/.htaccess)** | Box "una sola barriera non è difesa in profondità" (ponte SPW-C5 3 livelli) |
| **Dangling media senza tabella** | Box "il costo di non avere nemmeno una riga DB per i media" (ponte C4) |
| **Evoluzione storage raster→WebP negli one-shot di admin.php** | Box "far evolvere lo storage senza downtime" (ponte C13) |

## 8. Note / domande aperte

- **Puntatori ad altri cluster** (annotati qui, NON mappati in questa card):
  - **`cover_image`/`image` come stringa URL** in news/speakers/podcasts → **C4** (già mappato): C5
    conferma che il file è gestito qui ma il **riferimento** vive nei contenuti, senza tabella né FK
    (origine del dangling media, qui aggravato dall'assenza di una tabella `media`).
  - **One-shot `optimize_webp`/`fix_image_paths`** (`admin.php:347-371,472-523`): la *logica* di
    conversione WebP è C5 (qui mappata); la **storia migratoria** (raster→WebP, riallineamento
    riferimenti, il fatto che vivano dentro `admin.php` come azioni `?action=`) → **C13** (DB Evolution
    & Incidenti). Sono protetti da HTTP solo perché `admin.php` richiede login (non dal prefisso
    `.htaccess`, che blocca i file `optimize_`/`fix_` *standalone*, non le action interne).
  - **`.htaccess` globale** (`public/.htaccess`) → hardening generale già in **SR-C2**; qui
    ri-contestualizzato per **dimostrare l'assenza** del PHP-off su `uploads/` (dubbio aperto di
    SR-C2 §8, ora **chiuso: confermato assente**).
  - **`db.php`/`db_credentials.php`** (connessione) → **SR-C1**. `media.php` carica `db.php` ma non lo
    usa (fossile, §4).
  - **Embed immagini dentro il `content` dell'editor** (non solo cover/galleria) → **C6** (Editor): qui
    si mappa solo come il file finisce su disco; come viene inserito nel testo Tiptap è C6. Da
    verificare in C6 se l'editor riusa `uploadImage` (SR-C3 dice di sì, ramo upload di `ArticleEditor`).
- **Da verificare (DB, C1/C13):** confermato che `init_mysql.php` **non** crea `media`; verificare nei
  file di migrazione/incidenti (C13) se una tabella `media` sia mai esistita ed eliminata, o se il
  sito sia sempre stato filesystem-based.
- **Asimmetria di gate (riassunto):** `upload.php` = `isLoggedIn()` + `validateCsrf()` (corretto);
  `media.php` = solo `$_SESSION['user_id']`, **niente CSRF, niente `isAdmin`, niente `auth_utils.php`**
  (gap, §4). Due endpoint media, due livelli di protezione diversi → da uniformare (rilievo per il
  libro e per un'eventuale fix futura del sito, NON applicata qui: sola lettura).
- **Forma risposta:** `upload.php` → `{success,url}` (oggetto); `media.php` GET → `{success,files}`
  (oggetto con array dentro). Coerente con la mappa buste di SR-C4 (mosaico per-endpoint).
- **Nessuna credenziale/segreto** negli endpoint (connessione via `db.php` di SR-C1, qui peraltro
  inutilizzata in `media.php`).
- Versione del sito al momento della mappatura: **2.9.13** (coerente con SR-C1..C4); gli one-shot
  WebP sono marcati `v2.9.2`.
