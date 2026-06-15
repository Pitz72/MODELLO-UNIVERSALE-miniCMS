# Mappatura — SimonePizziWebSite — C5: Media & Upload (lato server)

> **Stato:** COMPLETATO
> **Sessione:** 5 · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `SimonePizziWebSite/`)
> - `public/api/upload.php` (ricezione `multipart/FormData`, validazione estensione + magic bytes, smistamento sottocartella, naming anti-collisione, conversione/resize WebP, INSERT in `media`)
> - `public/api/media.php` (libreria: GET lista, DELETE con unlink fisico + path-guard)
> - `public/api/download.php` (proxy di download pubblico col nome originale, streaming `readfile`, path-guard)
> - `public/uploads/.htaccess` (PHP-off / hardening cartella upload — già citato in C2, qui ri-contestualizzato)
> - `scripts/optimize_uploads.php` (one-shot batch: converte in WebP gli upload già presenti, aggiorna `media`)
> - `scripts/server-tools/fix_uploads_subfolder.php` (one-shot migration: rimappa `cover_image` da `/uploads/` a `/uploads/immagini/`)
> - `scripts/server-tools/migrate_to_mysql.php:88-95, 223-226` (schema tabella `media` + migrazione SQLite→MySQL — letto per la forma del record)
> - `src/api.ts:438-471` (firme client `uploadMedia`/`getMedia`/`deleteMedia`, lette come consumatori — dettaglio LATO CLIENT già mappato in C3)

## 1. Cosa fa (sintesi narrativa)

C5 è il **lato server dei media**: come un file caricato dalla dashboard arriva su disco, viene
validato, ottimizzato, registrato a DB e poi servito ai visitatori. Tre endpoint, due script di
manutenzione, una tabella (`media`). Tutto nello stesso "thin stack" di C4: un file PHP per
responsabilità, `Database::connect()` (C1) per il DB, `Auth::check()` (C2) per il gate.

Il flusso canonico è:

1. **`upload.php`** — riceve **un** file (`$_FILES['file']`, multipart inviato dal client di C3).
   Solo `POST`, **gated `Auth::check()` in testa** (solo admin carica). Validazione a **doppio
   strato**: prima l'**estensione** contro una whitelist (`jpg/jpeg/png/webp/gif/pdf/zip/rar/mp3`),
   poi il **contenuto reale** via `mime_content_type()` (magic bytes) contro una whitelist MIME —
   per battere lo spoofing tipo `shell.php.jpg`. In base al MIME reale sceglie la **sottocartella**
   (`immagini` / `documenti` / `file`), genera un **nome anti-collisione** (`uniqid()` + base
   ripulita + estensione, **senza punti interni** per non creare doppie estensioni eseguibili),
   sposta il file, e — se è un'immagine raster (jpeg/png/gif) e GD è disponibile — la **converte in
   WebP** (qualità 82, resize a max 1920px di larghezza), cancellando l'originale. Infine **registra
   il file in `media`** (filename, file_path pubblico, mime, size) e risponde
   `{status, url, id, name}`.

2. **`media.php`** — la **libreria**. `GET` (gated) ritorna **tutti** i media in array nudo,
   ordinati per data discendente. `DELETE?id=` (gated) cancella la riga e **fa l'`unlink` del file
   fisico**, ma solo dopo aver verificato che il `file_path` salvato a DB punti davvero dentro
   `/uploads/` (path-guard con `realpath` + `str_starts_with`). Nessuna paginazione, nessun POST/PUT
   (l'upload vero vive in `upload.php`).

3. **`download.php`** — il **proxy di download** pubblico. Dato `?id=`, recupera il record,
   ricostruisce il path fisico (stesso path-guard di `media.php`), e fa lo **streaming** del file con
   `readfile()` impostando `Content-Disposition: attachment` col **nome originale pulito** (quello
   in `media.filename`, senza il prefisso `uniqid`). È **l'unico endpoint media senza
   `Auth::check()`**: i file sono distribuiti ai visitatori (es. download di uno ZIP). La difesa è
   tutta nel path-guard: l'unica fonte di verità è il DB, niente path traversal.

A latere, due **script one-shot** (pattern "carica via FTP, esegui da browser, cancella subito",
come `init_db.php`): `optimize_uploads.php` (converte in WebP gli upload **già esistenti** prima che
`upload.php` lo facesse in automatico) e `fix_uploads_subfolder.php` (rimappa i `cover_image` da
`/uploads/` piatto a `/uploads/immagini/` quando è stato introdotto lo smistamento per sottocartella).

## 2. Pattern miniCMS rilevanti

- **Validazione upload a doppio strato (estensione + magic bytes).** `upload.php:25-54` non si fida
  dell'estensione: la whitelist di estensioni (`:26`) è solo il primo filtro, poi `mime_content_type()`
  legge i byte reali (`:35`) e li confronta con una whitelist MIME (`:42-48`). Il MIME reale è anche
  ciò che decide la sottocartella (`:56-62`), non l'estensione dichiarata. È IL pattern "non fidarti
  del nome del file" — gold per il capitolo upload sicuri.
- **Naming anti-collisione e anti-doppia-estensione.** `upload.php:73-75`: la base del nome è
  ripulita con `preg_replace('/[^A-Za-z0-9\-_]/', '', …)` (**niente punti**, niente spazi), poi
  `uniqid() . '-' . base . '.' . ext`. Il commento `:71-72` è esplicito: rimuovere i punti interni
  evita `shell.php.jpg` eseguibile via `AddHandler/mod_mime` di Apache. Difesa applicativa **in
  aggiunta** all'`.htaccess` (vedi sotto): cintura e bretelle.
- **Difesa in profondità a tre livelli sulla cartella upload.** (1) `.htaccess` in `public/uploads/`
  spegne il motore PHP e nega le estensioni eseguibili (`uploads/.htaccess:4-16`, v1.19.0); (2) il
  naming non genera mai nomi eseguibili; (3) la validazione MIME blocca il contenuto camuffato. Tre
  barriere indipendenti per lo stesso rischio (RCE da upload). Ponte diretto a C2.
- **Path-guard con `realpath` contro il path traversal "dal DB".** `media.php:33-37` e
  `download.php:38-49`: anche se il `file_path` arriva dal DB (fidato in teoria), prima di fare
  `unlink`/`readfile` si verifica `str_starts_with($filePath, '/uploads/')` **e** che il `realpath`
  risolto stia dentro la base `realpath(.../uploads)`. Stesso identico schema duplicato nei due file
  (v1.19.0). Pattern "non fidarti nemmeno del tuo DB" — gold.
- **Ottimizzazione inline a costo zero (WebP + resize) dentro l'endpoint.** `upload.php:83-119`:
  niente coda, niente worker, niente cron. La conversione avviene **sincrona** nello stesso request
  dell'upload, gated dietro `extension_loaded('gd') && function_exists('imagewebp')` (degradazione
  graziosa se GD manca: il file resta com'è). È il "thin stack" applicato all'image processing.
- **Separazione URL pubblico vs nome utente.** Il record `media` tiene **due** colonne: `file_path`
  (URL tecnico `/uploads/immagini/uniqid-nome.webp`, quello che il browser carica) e `filename` (il
  nome "umano" originale). `download.php` usa il secondo per il `Content-Disposition`, così l'utente
  riscarica `relazione.pdf` e non `64f1a2-relazione.pdf`. Pattern "due nomi per un file".
- **Endpoint pubblico vs gated, deciso per risorsa.** Lista/cancellazione media = admin
  (`Auth::check()`); download del singolo file = pubblico. La distinzione non è per-verbo come in C4
  ma **per-endpoint**, perché il download è parte dell'esperienza del visitatore.
- **Script one-shot "usa e cancella".** `optimize_uploads.php:1-26` e `fix_uploads_subfolder.php`
  seguono il pattern del progetto (come `init_db.php`): file di manutenzione caricati via FTP,
  eseguiti dal browser, da **eliminare subito** (warning ripetuto in testa e in coda). Il secondo
  ha pure il **dry-run di default** (`?go=1` per applicare) — pattern "guarda prima di toccare".

## 3. Codice chiave (stralci con origine)

**Validazione a doppio strato: estensione poi magic bytes** — `upload.php:25-54`:

```php
$allowedExts = ['jpg','jpeg','png','webp','gif','pdf','zip','rar','mp3'];
if (!in_array($fileExt, $allowedExts)) { /* 400 */ }

$realMime = mime_content_type($file['tmp_name']);   // legge i byte reali, non l'estensione
// Fallback: ZIP/RAR a volte rilevati come octet-stream
if ($realMime === 'application/octet-stream' && in_array($fileExt, ['zip','rar'])) {
    $realMime = 'application/zip';
}
$allowedMimes = ['image/jpeg','image/png','image/webp','image/gif','application/pdf',
                 'application/zip', /* … */ 'audio/mpeg'];
if (!in_array($realMime, $allowedMimes)) { /* 400: "Spoofing bloccato" */ }
```

**Smistamento per sottocartella + naming anti-doppia-estensione** — `upload.php:56-79`:

```php
$subFolder = 'file';
if (strpos($realMime, 'image/') === 0)      $subFolder = 'immagini';
elseif ($realMime === 'application/pdf')    $subFolder = 'documenti';

$uploadDir = __DIR__ . '/../uploads/' . $subFolder . '/';
if (!is_dir($uploadDir)) mkdir($uploadDir, 0755, true);

// [v1.19.0] base SENZA punti → niente shell.php.jpg
$safeBase = preg_replace('/[^A-Za-z0-9\-_]/', '', pathinfo($fileName, PATHINFO_FILENAME));
if ($safeBase === '') $safeBase = 'file';
$newFileName = uniqid() . '-' . $safeBase . '.' . $fileExt;
$publicUrl   = '/uploads/' . $subFolder . '/' . $newFileName;
```

**Conversione WebP + resize sincrona nell'endpoint** — `upload.php:83-119`:

```php
$imageMimes = ['image/jpeg','image/png','image/gif'];
if (in_array($realMime, $imageMimes) && extension_loaded('gd') && function_exists('imagewebp')) {
    // imagecreatefromjpeg/png/gif …
    if ($origW > 1920) { /* imagecopyresampled a 1920px, alpha preservato */ }
    $webpDestination = $uploadDir . preg_replace('/\.[^.]+$/', '.webp', $newFileName);
    if (@imagewebp($img, $webpDestination, 82)) {
        unlink($destination);                 // butta l'originale
        $publicUrl = '/uploads/' . $subFolder . '/' . $webpNewFileName;
        $fileName  = preg_replace('/\.[^.]+$/', '.webp', $fileName);
    }
}
```

**Path-guard condiviso (media.php DELETE e download.php)** — `media.php:31-39`:

```php
$filePath = $media['file_path'];
if (str_starts_with($filePath, '/uploads/')) {
    $physicalPath = realpath(__DIR__ . '/..' . $filePath);
    $uploadsBase  = realpath(__DIR__ . '/../uploads');
    if ($physicalPath && $uploadsBase && str_starts_with($physicalPath, $uploadsBase)) {
        unlink($physicalPath);                // solo se DAVVERO dentro /uploads
    }
}
```

**Download proxy: nome originale pulito + streaming** — `download.php:51-68`:

```php
$cleanName = str_replace(['"','\\',"\r","\n"], '', $media['filename']);  // header-safe
if (ob_get_level()) ob_end_clean();                                     // file grandi
header('Content-Type: ' . $media['mime_type']);
header('Content-Disposition: attachment; filename="' . $cleanName . '"');
header('Content-Length: ' . filesize($physicalPath));
header('Cache-Control: no-store, no-cache, must-revalidate');
readfile($physicalPath);
```

**Schema tabella `media`** — `scripts/server-tools/migrate_to_mysql.php:88-95`:

```sql
CREATE TABLE IF NOT EXISTS media (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename   VARCHAR(255),   -- nome umano originale (per il download)
    file_path  TEXT,           -- URL pubblico /uploads/<sub>/<uniqid>-<nome>.<ext>
    mime_type  VARCHAR(100),
    size       INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 4. Problemi riscontrati & soluzioni

- **RCE da upload (il rischio numero uno) — risolto a tre livelli.** È la storia centrale di C5.
  Soluzione stratificata: `.htaccess` PHP-off (C2) + naming senza punti interni + validazione magic
  bytes. Ognuno copre un buco dell'altro (se l'`.htaccess` non venisse letto, il naming salva; se il
  naming fallisse, l'`.htaccess` salva; lo spoofing del contenuto è fermato dal MIME check). Gold
  assoluto per il box "rendere sicura una cartella di upload".
- **Riferimenti pendenti dopo la cancellazione (dangling media).** `media.php` DELETE cancella la
  riga `media` e il file fisico, ma **non tocca** `articles.cover_image` / `projects.cover_image` né
  gli embed dentro il `content` (che salvano la **stringa URL**, vedi C4 §8). Cancellare un media
  usato come copertina lascia un `<img>` rotto. Nessuna FK, nessun reference-count: il legame
  URL↔file è solo testuale. Box "il costo di salvare un percorso invece di una relazione".
- **L'ottimizzazione sincrona blocca la risposta.** La conversione WebP (`upload.php:83-119`) avviene
  dentro il request di upload: su immagini grandi l'utente aspetta GD prima di vedere il 200. Accettabile
  per un blog a basso traffico (e c'è la barra di progresso lato C3), ma è un limite del thin stack —
  niente coda/worker. Box "quando l'elaborazione sincrona basta e quando no".
- **Perdita dell'animazione GIF e niente vincolo verticale.** La conversione tratta la GIF come raster
  statico (`imagecreatefromgif` → un solo frame): una GIF animata diventa un WebP fermo. Il resize
  vincola solo la **larghezza** > 1920 (`:95`); un'immagine altissima e stretta resta enorme in
  altezza. Bordi da conoscere.
- **Doppio binario di ottimizzazione (archeologia v1.x).** `optimize_uploads.php` scrive i WebP in
  `/uploads/<file>.webp` **piatto** (`:123`), mentre `upload.php` oggi usa `/uploads/immagini/…`. Lo
  script batch **precede** lo smistamento per sottocartella; `fix_uploads_subfolder.php` esiste
  proprio per **rimappare** i `cover_image` rimasti sul layout piatto al nuovo `/immagini/`. La
  sequenza degli script racconta l'evoluzione: prima upload piatto → batch WebP one-shot → poi
  sottocartelle in `upload.php` → migration dei riferimenti. Gold per "evoluzione incrementale dello
  storage senza downtime".
- **Commento stale "Rimozione riga DB SQLite".** `media.php:41` dice "SQLite" ma il DB è MySQL
  (migrazione di C1/C13). Fossile testuale, innocuo, ma da segnalare → puntatore C13.
- **`optimize_uploads.php` aggiorna il DB per `file_path` esatto.** `optimize_uploads.php:145-157`:
  cerca il record con `WHERE file_path = '/uploads/<file>'`; se il record non esiste (file su disco
  ma non tracciato a DB) logga "ATTENZIONE record non trovato" e converte comunque il file, lasciando
  il DB disallineato. Limite noto dello script one-shot.

## 5. Estetica / UX (moderna ma funzionale)

C5 è back-end, ma serve esperienze visibili:

- **WebP automatico = pagine leggere senza che l'admin ci pensi.** L'admin carica un PNG da 3 MB e
  sul sito finisce un WebP da poche centinaia di KB, ridimensionato a 1920px. L'ottimizzazione delle
  prestazioni è **invisibile** all'autore (ponte alla UX di caricamento di C3 con barra di progresso).
- **Download con nome "umano".** Il visitatore che scarica un allegato riceve `portfolio-2026.pdf`,
  non `64f1c2a-portfolio2026.pdf`. La pulizia del nome (`download.php:52`) è una micro-cortesia UX
  costruita lato server.
- **Smistamento in sottocartelle** (`immagini`/`documenti`/`file`): più che estetica è
  manutenibilità — la cartella upload resta navigabile via FTP per tipo.

## 6. Differenze rispetto agli altri siti

(Da consolidare in FASE 2. Ipotesi/puntatori:)
- **SitoRuntime (SR-C5)**: avrà media per news/speaker/podcast — verificare se usa lo **stesso**
  `upload.php` (validazione doppio strato + WebP) o una variante; se i podcast (audio grandi) hanno
  un flusso di upload/streaming diverso da `download.php` con `readfile`. Possibile divergenza su
  range requests / file > limite memoria.
- **DISINTELLIGENZA/FDCA (SQLite)**: la conversione WebP via GD è indipendente dal DB, quindi
  probabilmente identica; la tabella `media` su SQLite cambia solo nei tipi. Verificare se lì l'upload
  è gated come qui o più aperto (festival con iscrizioni → possibile upload pubblico di materiali?).
  Termine di paragone "minimo" interessante per il pattern sicurezza.
- Verificare se altrove esiste lo **smistamento per sottocartella** o se restano tutti piatti
  (SPW ci è arrivato per migrazione, non da subito).

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **Validazione upload a doppio strato** (estensione + magic bytes) | Cap. "Caricare file senza farsi bucare" (centrale, alto valore) |
| **Difesa in profondità a 3 livelli sulla cartella upload** (.htaccess + naming + MIME) | Box "cintura e bretelle: tre barriere per un upload" (ponte C2) |
| **Naming anti-doppia-estensione** (`uniqid` + base senza punti) | Box "perché il nome del file è un problema di sicurezza" |
| **Path-guard con `realpath`** (non fidarti nemmeno del DB) | Box "il path traversal che arriva dal tuo stesso database" |
| **Ottimizzazione WebP + resize sincrona nell'endpoint** | Cap. "Image processing senza worker: GD nel thin stack" |
| **Due nomi per un file** (`file_path` tecnico vs `filename` umano) | Box "l'URL pubblico e il nome che vede l'utente" |
| **Download proxy pubblico** (gated vs non-gated per endpoint) | Box "quando un endpoint media NON va protetto" |
| **Dangling media** (cancello il file, resta l'URL in cover_image) | Box problemi/soluzioni "il costo di salvare un percorso invece di una relazione" (ponte C4) |
| **Script one-shot usa-e-cancella + dry-run** | Box "manutenzione FTP-and-forget: il pattern degli script monouso" |
| **Evoluzione storage** (flat → WebP batch → sottocartelle → migration riferimenti) | Box "far evolvere lo storage senza downtime" (ponte C13) |

## 8. Note / domande aperte

- **Puntatori ad altri cluster** (annotati qui, NON mappati in questa card):
  - L'embed di immagini **dentro il contenuto** dell'editor (non solo cover/media library) → **C6**
    (Advanced Editing): qui si mappa solo come il file finisce su disco e a DB, non come viene
    inserito nel testo. Da verificare in C6 se l'editor riusa `uploadMedia`/`uploadMediaWithProgress`.
  - `cover_image` come stringa URL in `articles`/`projects` → **C4** (già mappato): C5 conferma che il
    file è gestito qui ma il **riferimento** vive nei contenuti, senza FK (origine del dangling media).
  - La migrazione `media` SQLite→MySQL e il commento stale "SQLite" in `media.php:41` → **C13** (DB
    Evolution): qui solo annotati.
  - `.htaccess` di `public/uploads/` → **C2** (già mappato come parte dell'hardening); ri-contestualizzato
    in C5 come prima barriera della difesa in profondità sull'upload.
  - `optimize_db.php`, `backup.php` (manutenzione DB/backup, non media) → **C12** (Admin/manutenzione):
    fuori ambito C5.
- **Da verificare (DB, C1/C13):** se la tabella `media` ha vincoli/indici oltre alla PK; non risulta
  alcuna FK verso `articles`/`projects` (coerente col legame solo-URL).
- **Asimmetria gate:** `upload.php` e `media.php` gated `Auth::check()`; `download.php` pubblico per
  scelta esplicita (file distribuiti ai visitatori). Documentato nel commento `download.php:10-12`.
- **Forma risposta (chiusura Double Read anche qui):** `media.php` GET ritorna **array nudo**
  (`media.php:16`), coerente con la mappa di C4 (solo `articles.php` lista usa `{data,total}`).
  `upload.php` ritorna un **oggetto** `{status,url,id,name}` (non lista, non soggetto al pattern).
- **Versione di riferimento:** allineata a SPW-C1..C4 (sito **1.21.0**); le difese chiave dell'upload
  (naming senza punti, path-guard, `.htaccess` PHP-off) sono marcate **v1.19.0**; smistamento
  sottocartelle e ottimizzazione WebP precedenti (`mkdir 0755` marcato v1.5.10, download proxy v1.6.1).
- Nessuna credenziale/segreto negli endpoint (connessione via `db.php`/`config.php` di C1).
