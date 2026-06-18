# Mappatura — DISINTELLIGENZA — C5: Media & Upload (lato server)

> **Stato:** COMPLETATO
> **Sessione:** 23 · **Data:** 2026-06-18 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `DISINTELLIGENZA/`)
> - `public/api/upload.php` (ricezione `$_FILES['file']`, gate **per-tipo** image/audio, validazione **solo-MIME client**, naming, resize GD, risposta `{status,url}`)
> - `public/api/media.php` (libreria FILESYSTEM-based ricorsiva: GET `scanDirRecursive` + POST `action=delete` multi-candidato; gate solo-sessione, no CSRF)
> - `public/api/migrate_media.php` (one-shot **NON gated**: sposta audio da flat → sottocartelle participants/podcasts, aggiorna DB)
> - `public/.htaccess` (deny `*.sqlite`/`*.bak`, routing — **VERIFICATO: nessun PHP-off su `uploads/`**)
> - `public/uploads/` (**VERIFICATO: nessun `.htaccess` di cartella**; solo `test.txt`)
> - confronto: `SR-C5-media-upload.md`, `SPW-C5-media-upload.md`

## 1. Cosa fa (sintesi narrativa)

C5 è il **lato server dei media** di DISINTELLIGENZA. Ma rispetto agli altri due siti ha uno scopo
**più largo e più pericoloso**: oltre alle immagini (cover di news/podcast), gestisce l'**audio** —
ed essendo un sito-festival, l'audio comprende **le tracce caricate dai partecipanti durante le
iscrizioni**. Questo apre la porta a un **upload pubblico non autenticato**, lo scenario che le card
SPW-C5 e SR-C5 si erano chieste ("festival con iscrizioni → possibile upload pubblico?"): **qui è
confermato e presente**.

Due endpoint + uno script one-shot:

1. **`upload.php`** — `POST` unico che gestisce **immagini e audio** smistando per un parametro
   `type` fornito dal client (`image`, `audio`, `audio_participant`, `audio_podcast`,
   `upload.php:65,76`). Il **gate è per-tipo e incoerente**: `image` e `audio_podcast` richiedono il
   login (`:69,84`), ma `audio_participant` e il generico `audio` **non hanno alcun controllo di
   auth** → **upload pubblico** (`:79-94`). La validazione è a **un solo strato e debole**: confronta
   `$file['type']` — il MIME **dichiarato dal browser**, spoofabile — contro una whitelist
   (`:100-103`); **niente `finfo`/magic bytes**, **niente whitelist di estensioni**. Il naming
   `uniqid().'_'.basename(nome)` **conserva il nome originale e l'estensione** (`:110-111`). Le
   immagini vengono ridimensionate via GD (max 1920, qualità 85) **mantenendo il formato** (niente
   WebP). Smista in sottocartelle (`uploads/images/`, `uploads/audio/participants/`,
   `uploads/audio/podcasts/`) decise dal `type` client. Risposta `{status,url}`, **nessun INSERT a
   DB** (non c'è tabella `media`).

2. **`media.php`** — la **libreria, basata sul filesystem** (come SR). `GET` fa una scansione
   **ricorsiva** (`scanDirRecursive`, `:14-36`) di `uploads/` e ritorna un array nudo di
   `{name,url,size,date,type}` con `mime_content_type` dal disco. `POST ?action=delete` cancella un
   file. Gate **solo-sessione** (`isset($_SESSION['user_id'])`, `:6`), **nessun CSRF**, **nessun
   ruolo**. Il path-guard della delete è **un solo `strpos($filename,'..')`** (`:49`) seguito da un
   tentativo di `unlink` su **più percorsi candidati** (`:56-78`).

3. **`migrate_media.php`** — script one-shot che sposta gli audio dal layout **piatto**
   `uploads/audio/` alle **sottocartelle** `participants/` e `podcasts/`, aggiornando
   `participants.audio_file` e `podcasts.audio_url`. **Non ha alcun gate** (`:1-16`: error reporting
   on, poi subito `Database::connect()`), quindi è eseguibile in HTTP da chiunque (coerente con gli
   `update_db_*` non protetti di DIS-C1).

## 2. Pattern miniCMS rilevanti

- **Upload multi-tipo (immagini + audio) con smistamento per parametro client** (`upload.php:65-98`):
  un solo endpoint serve cover immagini e tracce audio; la sottocartella è scelta dal `type` inviato
  dal client, non dal MIME reale (≠ SR/SPW che decidono da `finfo`). Più funzioni in un file, ma la
  fiducia nel parametro client è una debolezza (§4).
- **Sottocartelle per tipo** (`uploads/images/`, `uploads/audio/participants/`,
  `uploads/audio/podcasts/`, `upload.php:74,80,88,92`): DIS **ha** le sottocartelle (come SPW, ≠ flat
  di SR), create a runtime con `mkdir(0755, true)` (`:106-108`).
- **Resize GD che PRESERVA il formato (niente WebP)** (`upload.php:8-56,117-119`): `resizeImage()`
  ridimensiona jpeg/png/webp mantenendo il tipo originale (`imagejpeg`/`imagepng`/`imagewebp` a
  seconda dell'input) e preserva la trasparenza PNG/WebP. A differenza di SPW e SR (che **convertono**
  in WebP), DIS **non converte**: ottimizza solo le dimensioni. Più semplice, meno aggressivo sul
  peso. La conversione avviene **in-place** (`resizeImage($destination, $destination)`, `:118`).
- **Libreria media FILESYSTEM-based RICORSIVA** (`media.php:14-39`): nessuna tabella `media` (come
  SR); ma a differenza dello `scandir` piatto di SR, qui la scansione è **ricorsiva** sulle
  sottocartelle (`scanDirRecursive`) e include `mime_content_type` dal disco. Il disco **è** il
  database dei media, navigato ad albero.
- **Naming che CONSERVA il nome utente** (`upload.php:110-111`): `uniqid().'_'.basename($file['name'])`
  poi `preg_replace('/[^a-zA-Z0-9_.-]/', '', ...)`. È l'**opposto** delle due difese viste altrove:
  SPW ripulisce la base **togliendo i punti** (anti-doppia-estensione), SR **scarta del tutto** il
  nome (`uniqid` puro). DIS tiene nome **e** estensione (i punti sono nel set permesso) → è il naming
  **più debole dei tre** (§4, GOLD).
- **Path-guard minimale a una sola condizione** (`media.php:49`): la delete blocca solo i `..`
  (`strpos`), poi prova a cancellare su una lista di percorsi candidati. Più debole sia del `realpath`
  di SPW sia del `basename` di SR (che neutralizza il traversal trasformandolo, mentre qui si
  *rifiuta* e basta).
- **Script di manutenzione one-shot non protetto** (`migrate_media.php`): coerente con il pattern
  DIS-C1 (`update_db_*` per lo più senza gate). Racconta l'evoluzione storage: audio flat →
  sottocartelle.

## 3. Codice chiave (stralci con origine)

**GOLD — gate per-tipo INCOERENTE: `audio_participant` è PUBBLICO** — `upload.php:64-98`:

```php
$file = $_FILES['file'];
$type = $_POST['type'] ?? 'misc';

if ($type === 'image') {
     if (!isset($_SESSION['user_id'])) { http_response_code(401); die(...); }   // GATED
     $allowed = ['image/jpeg', 'image/png', 'image/webp'];
     $uploadDir = __DIR__ . '/../uploads/images/';
} elseif ($type === 'audio' || $type === 'audio_participant' || $type === 'audio_podcast') {
     $allowed = ['audio/mpeg', 'audio/aac', 'audio/mp4', 'audio/x-m4a'];
     if ($type === 'audio_participant') {
         $uploadDir = __DIR__ . '/../uploads/audio/participants/';            // <-- NESSUN gate auth!
     } elseif ($type === 'audio_podcast') {
         if (!isset($_SESSION['user_id'])) { http_response_code(401); die(...); }  // GATED
         $uploadDir = __DIR__ . '/../uploads/audio/podcasts/';
     } else {
         $uploadDir = __DIR__ . '/../uploads/audio/';                         // <-- generico: NESSUN gate
     }
}
```

**GOLD — validazione SOLO sul MIME dichiarato dal client + naming che tiene l'estensione** — `upload.php:100-114`:

```php
if (!in_array($file['type'], $allowed)) {          // $file['type'] = Content-Type del BROWSER (spoofabile)
    http_response_code(400);
    die(json_encode(['status' => 'error', 'message' => 'Invalid file format: ' . $file['type']]));
}
// ... mkdir ...
$filename = uniqid() . '_' . basename($file['name']);          // conserva il nome originale...
$filename = preg_replace('/[^a-zA-Z0-9_.-]/', '', $filename);  // ...e i punti (`.`) sono permessi -> estensione preservata
$destination = $uploadDir . $filename;
if (move_uploaded_file($file['tmp_name'], $destination)) {
    if ($type === 'image') { resizeImage($destination, $destination); }
    echo json_encode(['status' => 'success', 'url' => $publicPath . $filename]);
}
```

**Resize GD che preserva il formato (no WebP)** — `upload.php:47-55`:

```php
switch ($type) {                                   // $type qui = IMAGETYPE_* del file reale (getimagesize)
    case IMAGETYPE_JPEG: imagejpeg($dst, $destPath, $quality); break;   // resta JPEG
    case IMAGETYPE_PNG:  imagepng($dst, $destPath, 9); break;           // resta PNG
    case IMAGETYPE_WEBP: imagewebp($dst, $destPath, $quality); break;   // resta WebP
}
```

**Libreria filesystem ricorsiva (niente DB)** — `media.php:14-33`:

```php
function scanDirRecursive($dir, $prefix = '/uploads/') {
    $results = [];
    foreach (scandir($dir) as $item) {
        if ($item === '.' || $item === '..') continue;
        $path = $dir . $item;
        if (is_dir($path)) {
            $results = array_merge($results, scanDirRecursive($path . '/', $prefix . $item . '/'));
        } else {
            $results[] = ['name'=>$item, 'url'=>$prefix.$item, 'size'=>filesize($path),
                          'date'=>filemtime($path), 'type'=>mime_content_type($path)];
        }
    }
    return $results;
}
```

**Delete senza CSRF, path-guard solo `..`, unlink multi-candidato** — `media.php:46-78`:

```php
if ($action === 'delete') {
    $filename = $data['filename'];
    if (strpos($filename, '..') !== false) { http_response_code(400); die(...); }   // unica difesa traversal
    $candidates = [];
    $candidates[] = __DIR__ . '/../../public' . $filename;       // path "assoluto" da /uploads/...
    foreach (['', 'images/', 'audio/'] as $d) { $candidates[] = $baseDir . $d . $filename; }
    foreach ($candidates as $p) {
        $p = str_replace(['/', '\\'], DIRECTORY_SEPARATOR, $p);
        if (file_exists($p) && is_file($p)) { if (unlink($p)) { $deleted = true; break; } }
    }
}
```

## 4. Problemi riscontrati & soluzioni

- **GOLD sicurezza (1) — catena RCE da upload pubblico non autenticato.** È il rilievo più grave
  della coppia. Mettendo in fila ciò che è VERIFICATO: (a) `type=audio_participant` **non richiede
  login** (`upload.php:79-81`); (b) la validazione è **solo** su `$file['type']`, il Content-Type
  dichiarato dal browser, **spoofabile** (`:100`), senza `finfo` né whitelist di estensioni; (c) il
  naming **conserva nome ed estensione** originali (`:110-111`, i `.` sono nel set permesso); (d)
  **non esiste `uploads/.htaccess`** e il `public/.htaccess` **non spegne PHP** in `uploads/`
  (VERIFICATO: nega solo `*.sqlite`/`*.bak`). Conseguenza teorica: un attaccante invia una POST a
  `upload.php` con `type=audio_participant`, file `shell.php`, header `Content-Type: audio/mpeg` → la
  whitelist passa → il file viene salvato come `/uploads/audio/participants/<uniqid>_shell.php` →
  Apache lo eseguirebbe come PHP. È la difesa upload **a livello quasi-zero**, l'esatto opposto dei
  tre livelli di SPW. → Box problemi/soluzioni di **altissimo valore** "upload pubblico + MIME
  spoofabile + niente PHP-off = la tempesta perfetta" (ponte forte a SPW-C5 e SR-C5). *(Rilievo
  documentale: sola lettura, nessuna modifica al sito.)*
- **GOLD sicurezza (2) — validazione sul MIME client, non sui magic bytes.** A differenza di SPW e SR
  (che leggono i byte reali con `mime_content_type`/`finfo`), DIS si fida del `$file['type']` inviato
  dal client (`upload.php:100`). È il "non fidarti dell'estensione" **disatteso**: qui non ci si fida
  nemmeno dei byte, ci si fida di un header completamente controllato dall'attaccante. → Box "perché
  `$_FILES['type']` non è una validazione".
- **GOLD sicurezza (3) — `media.php` delete senza CSRF + path-guard a una condizione.** Come SR, la
  delete è una mutazione protetta solo dal cookie di sessione (niente `validateCsrf` — del resto DIS
  non ha CSRF, →C2) e senza check di ruolo. Il path-guard è più debole anche di SR: solo
  `strpos($filename,'..')` (`media.php:49`), poi `unlink` su più candidati incluso
  `__DIR__.'/../../public'.$filename`. Vulnerabile a CSRF; il rifiuto-su-`..` regge contro il
  traversal classico ma è fragile. → consolidare nel box "l'endpoint mutativo che si è dimenticato il
  token" (con SR-C5).
- **Naming il più debole dei tre siti.** SPW toglie i punti (anti-`shell.php.jpg`), SR scarta il nome
  (anti-tutto), DIS **tiene nome ed estensione** (`upload.php:110-111`). È la scelta che, combinata
  con la validazione debole, rende concreta la catena RCE del GOLD (1). → confluisce nel box
  "tre modi di nominare un upload, tre livelli di sicurezza".
- **Nessuna conversione WebP (solo resize).** DIS ottimizza le dimensioni ma **non** il formato
  (`upload.php:47-55`): un PNG da 3 MB resta PNG (ridimensionato). Niente risparmio di peso da WebP
  (≠ SPW/SR). Inoltre il resize avviene solo per `type=image`; gli audio non sono toccati (corretto).
  EXIF: la ri-codifica GD lo strippa comunque (effetto collaterale, come SR, ma non annotato nel
  codice).
- **Nessuna tabella `media`: dangling impossibili da tracciare.** Come SR: cancellare un file da
  `media.php` non aggiorna `news.cover_image`/`podcasts.cover_image`/`participants.audio_file` (che
  salvano la stringa URL, C4/C10). Senza tabella né reference-count, il legame URL↔file è solo
  testuale. Aggravante DIS: gli audio dei partecipanti sono dati di concorso — un file orfano o
  cancellato per errore è una traccia persa.
- **`migrate_media.php` non gated.** Lo script che sposta file e riscrive il DB
  (`participants.audio_file`, `podcasts.audio_url`) **non ha controllo di auth** (`migrate_media.php`
  parte diretto su `Database::connect()`): chiunque può triggerare lo spostamento massivo. Coerente
  con gli `update_db_*` non protetti di DIS-C1; stesso rischio (manutenzione potente esposta in HTTP).
- **Storia migratoria leggibile: audio flat → sottocartelle.** `migrate_media.php:46,72` mostra che
  prima gli audio stavano in `uploads/audio/` piatto e sono stati smistati in `participants/`/
  `podcasts/` (le query cercano file `LIKE '/uploads/audio/%' AND NOT LIKE '.../participants/%' AND
  NOT LIKE '.../podcasts/%'`). È il gemello dell'evoluzione storage di SPW (flat→sottocartelle), ma
  qui solo per l'audio. → eventuale DIS-C13.

## 5. Estetica / UX (moderna ma funzionale)

C5 è back-end, ma serve esperienze visibili:

- **Upload audio dei partecipanti = il cuore UX del festival.** La possibilità di caricare la propria
  traccia senza login (`audio_participant`) è una scelta UX deliberata: abbassa l'attrito
  dell'iscrizione (chiunque può candidarsi). Il costo è la sicurezza (§4) — è il classico trade-off
  "apertura vs hardening" da raccontare nel libro.
- **Resize automatico delle cover** (`upload.php:117-119`): l'admin carica un'immagine grande e viene
  ridotta a ≤1920 senza pensarci. Ottimizzazione invisibile (ma senza il salto di peso del WebP).
- **Libreria media ad albero** (`media.php` ricorsiva): la galleria admin mostra anche le
  sottocartelle (immagini, audio, partecipanti, podcast) — una vista d'insieme di tutti i materiali,
  utile per un festival con molti file eterogenei.

## 6. Differenze rispetto agli altri siti

Confronto a **TRE**: DIS-C5 (SQLite vivo, festival) vs SPW-C5 e SR-C5 (MySQL migrati).

| Aspetto | SimonePizziWebSite (SPW-C5) | SitoRuntime (SR-C5) | **DISINTELLIGENZA (questa card)** |
|---|---|---|---|
| **Scopo** | immagini + pdf/zip/mp3 | **solo immagini** | **immagini + audio** (tracce partecipanti, podcast) |
| **Upload pubblico** | no (gated `Auth::check`) | no (gated `isLoggedIn`+CSRF) | **SÌ** per `audio_participant`/`audio` (no auth) — GOLD |
| **Validazione** | estensione + magic bytes (`finfo`) | estensione + magic bytes (`finfo`) | **solo `$file['type']` client** (spoofabile), niente magic bytes/estensioni |
| **Naming** | `uniqid-base.ext` (punti tolti) | `uniqid` puro (nome scartato) | **`uniqid_nome.ext`** (nome + estensione conservati) — il più debole |
| **WebP** | sì (conversione + resize) | sì (conversione + resize, GIF animata) | **no**: solo resize, formato preservato |
| **Sottocartelle** | sì (per MIME reale) | flat | **sì** (per `type` client: images/audio/participants/podcasts) |
| **Tabella `media`** | sì (filename/path/mime/size) | no (scandir piatto) | **no** (scandir **ricorsivo**) |
| **`download.php`** | sì (proxy `readfile` + nome umano) | no (statici Apache) | **no** (statici Apache) |
| **Path-guard delete** | `realpath` + containment | `basename()` | **solo `strpos('..')`** + unlink multi-candidato (il più debole) |
| **CSRF delete** | `Auth::check()` | **assente** | **assente** (DIS non ha CSRF) |
| **`uploads/.htaccess` PHP-off** | **presente** (3 livelli) | assente (1 livello applicativo) | **assente** + validazione quasi-zero (≈0 livelli) — GOLD |
| **Gate gestione (media.php)** | `Auth::check()` | solo `$_SESSION['user_id']` | solo `$_SESSION['user_id']` (no ruolo) |
| **One-shot manutenzione** | gated da contesto/FTP | dentro `admin.php` (gated login) | `migrate_media.php` **non gated** |

**Sintesi.** Se SR-C5 era "il minimalismo spinto" e SPW-C5 "la difesa in profondità", **DIS-C5 è il
punto in cui il minimalismo incrocia il rischio reale**: l'apertura necessaria al festival (upload
pubblico delle tracce) si somma a una validazione che si fida del client e a una cartella upload
senza PHP-off, producendo la catena RCE del §4. È il caso-limite perfetto per il capitolo "quanto
puoi togliere a un sistema di upload prima che diventi insicuro": SR mostrava *fin dove* si può
sottrarre restando (a fatica) sicuri; **DIS mostra cosa succede un passo più in là**, e perché un
upload *pubblico* cambia tutte le regole. Allo stesso tempo DIS reintroduce due cose che SR aveva
tolto — le **sottocartelle** e una libreria **ricorsiva** — perché un festival con audio eterogenei
ne ha bisogno.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **Upload pubblico + MIME client + niente PHP-off = catena RCE** | Box problemi/soluzioni "la tempesta perfetta dell'upload pubblico" (ALTISSIMO valore, ponte SPW/SR-C5) |
| **`$_FILES['type']` non è validazione** (client vs magic bytes) | Box "non fidarti dell'estensione… né del Content-Type" |
| **Tre modi di nominare un upload** (punti tolti / nome scartato / nome+ext tenuti) | Box "il nome del file è un problema di sicurezza": la scala a tre |
| **Upload pubblico per le iscrizioni**: apertura vs hardening | Cap. "Festival logic": il trade-off dell'iscrizione senza attrito (ponte C10) |
| **Resize senza conversione WebP** vs conversione (SPW/SR) | Cap. "Image processing nel thin stack": variante "solo resize" |
| **Libreria media filesystem RICORSIVA** (niente DB) | confluisce in "quando il disco è il tuo database dei media" (3° caso) |
| **Delete senza CSRF + path-guard a una condizione** | consolidare con SR nel box "l'endpoint mutativo senza token" |
| **One-shot non gated** (`migrate_media.php`) | Box "manutenzione potente esposta in HTTP" (ponte DIS-C1 update_db_*) |
| **Evoluzione storage audio flat→sottocartelle** | confluisce in "far evolvere lo storage senza downtime" |

## 8. Note / domande aperte

- **Puntatori ad altri cluster** (annotati qui, NON mappati in questa card):
  - L'**upload pubblico delle tracce** è il punto d'incontro con **C10** (Festival Logic): `upload.php`
    `type=audio_participant` salva il file, poi `participants.php` (C10) crea la riga iscrizione con
    `audio_file`. La sicurezza/anti-frode dell'iscrizione → **C2/C10**; qui solo il *come* il file
    arriva su disco.
  - **Assenza di CSRF e meccanica di sessione** (`$_SESSION['user_id']`, ruoli) → **C2** (Security &
    Auth). La delete senza token e il gate per-tipo incoerente sono materia C2 per il quadro completo.
  - **`uploads/.htaccess` mancante + `public/.htaccess`** → l'hardening generale è **C2**; qui
    ri-contestualizzato per **dimostrare l'assenza** del PHP-off (VERIFICATO: confermato assente, come
    il dubbio chiuso in SR-C5 §8 ma qui con conseguenza più grave per via dell'upload pubblico).
  - **`cover_image`/`audio_url`/`audio_file` come stringa URL** in news/podcasts/participants →
    **C4** (mappato in coppia) e **C10**: C5 gestisce il file, il riferimento vive nei contenuti/entità.
  - **`migrate_media.php`** (storia migratoria audio flat→sottocartelle, non gated) → eventuale
    **DIS-C13** (DB/storage evolution & incidenti), se la apriremo.
- **Da verificare in C10:** esiste un limite di dimensione/durata sull'audio dei partecipanti?
  (`init_db.php` ha `participants.audio_duration`; upload non sembra validare la durata). Possibile
  vettore di abuso (file enormi caricati pubblicamente).
- **Da verificare in C2:** confermare che non esista alcun rate-limit sull'upload pubblico (in DIS-C1
  non ho visto `.cache/ratelimit` come SR) → upload pubblico **senza limiti** = vettore DoS/storage
  flooding oltre alla RCE.
- **Forma risposta:** `upload.php` → `{status,url}`; `media.php` GET → **array nudo** (coerente con la
  "busta zero" di DIS-C4). Nessun `id`/`name`/DB.
- Versione del sito al momento della mappatura: **0.5.x** (`package.json`).
