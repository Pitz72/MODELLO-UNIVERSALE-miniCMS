# CAPITOLO 7: Media & Optimization (Terza Edizione)

Questo capitolo segue un file dal disco di chi lo carica al disco del server: come arriva, come viene controllato, come viene alleggerito, dove finisce e come viene riservito. È un percorso breve, e proprio per questo pericoloso. Nei tre siti lo scheletro è lo stesso (un `upload.php` che riceve un `multipart`, lo valida, lo ottimizza con GD e lo mette su disco), ma è il cluster in cui la sicurezza scala **all'inverso del buon senso**.

La difesa contro l'esecuzione di codice da un upload va da **tre barriere indipendenti** (SimonePizziWebSite) a **una sola** (SitoRuntime) a **quasi zero su un upload pubblico** (DISINTELLIGENZA), dove la catena che porta dall'immagine alla shell è verificata. E due dettagli ribaltano l'intuizione: il naming «più minimale» (SR, che butta via il nome del file) è il **più sicuro**, mentre quello «più gentile» (DIS, che conserva nome ed estensione) è ciò che apre la porta. La domanda che attraversa il capitolo è una sola: *quanto puoi togliere a un sistema di upload prima che diventi insicuro*. E DIS mostra cosa c'è un passo oltre quel limite, perché un upload aperto al pubblico cambia tutte le regole.

Una nota di campo: qui si parla di **media**, non di cache né di SEO. La cache delle liste di contenuti vive nel ciclo di vita del contenuto (CAP 9); il pre-rendering dei metadati per i bot è il capitolo dell'entry-point PHP (CAP 11). Questo capitolo resta sul file: caricarlo, validarlo, ottimizzarlo, servirlo.

---

## 1. Lo scheletro comune

Prima delle divergenze, i tratti che i tre siti condividono.

Un `upload.php` riceve **un file per volta**: solo `POST`, `multipart/FormData` (inviato dal client del CAP 6), `$_FILES['file']`. Niente libreria di gestione media, niente servizio esterno; il file arriva nello stesso request che lo elabora. L'ottimizzazione dell'immagine avviene **sincrona, dentro l'endpoint**, via GD, dietro una guardia `extension_loaded('gd')` che degrada con grazia se GD manca: niente coda, niente worker, niente cron. Il nome viene reso anti-collisione con `uniqid()`. La «libreria» e la «cancellazione» vivono in un file separato (`media.php`), distinto dall'upload vero. E il riferimento al file, dentro i contenuti, è sempre una **stringa URL** (`cover_image`, `audio_file`), non una relazione con chiave esterna.

Quest'ultimo tratto ha una conseguenza condivisa, il **dangling media**: cancellare un file non avvisa chi lo citava, e nessuno dei tre tiene un conteggio dei riferimenti. Un'immagine usata come copertina, una volta cancellata, lascia un `<img>` rotto e nessuno se ne accorge finché la pagina non si apre.

```php
// SPW upload.php — il flusso canonico: gate, valida, ottimizza, registra, rispondi
Auth::check();                                  // solo l'admin carica (SPW/SR; DIS NO, vedi §5)
// 1) valida estensione + byte reali  2) sceglie sottocartella  3) nome anti-collisione
// 4) resize/WebP via GD  5) INSERT in `media`  6) echo { status, url, id, name }
```

---

## 2. Validare un file: l'estensione non basta, e nemmeno il Content-Type

Il primo lavoro dell'endpoint è decidere se il file è davvero ciò che dichiara di essere. SPW e SR lo fanno a **due strati**: prima l'estensione contro una whitelist, poi i **byte reali** letti con `finfo`/`mime_content_type` contro una whitelist di MIME. È il principio «non fidarti del nome del file»: un `shell.php.jpg` supera il primo filtro ma viene fermato dal secondo, perché i suoi byte non sono quelli di un'immagine. Lo stesso MIME reale decide anche la sottocartella, così la classificazione non si fida mai dell'estensione dichiarata.

```php
// SPW upload.php:25-54 — due strati: estensione, poi i byte reali
$allowedExts = ['jpg','jpeg','png','webp','gif','pdf','zip','rar','mp3'];
if (!in_array($fileExt, $allowedExts)) { /* 400 */ }

$realMime = mime_content_type($file['tmp_name']);   // legge i byte, non l'estensione
$allowedMimes = ['image/jpeg','image/png','image/webp','image/gif','application/pdf','application/zip', /* … */];
if (!in_array($realMime, $allowedMimes)) { /* 400: contenuto camuffato bloccato */ }
```

DIS fa un'altra scelta, e qui comincia la storia di sicurezza del capitolo: si fida di `$_FILES['type']`, cioè del Content-Type che **dichiara il browser**. Nessun `finfo`, nessuna whitelist di estensioni, solo il valore che chi invia la richiesta controlla per intero.

```php
// DIS upload.php:100 — la "validazione" guarda il MIME dichiarato dal client (spoofabile)
if (!in_array($file['type'], $allowed)) {           // $file['type'] = header del browser
    http_response_code(400); die(json_encode(['status'=>'error','message'=>'Invalid file format']));
}
```

> [!WARNING]
> **`$_FILES['type']` non è una validazione**
> Il Content-Type dentro `$_FILES` non lo calcola il server: lo scrive il client nella richiesta `multipart`, e si falsifica con una riga di `curl`. Validare contro quel valore vuol dire chiedere all'attaccante se il suo file è ammesso. La difesa reale è leggere i byte iniziali del file (`finfo_file` / `mime_content_type`) e confrontarli con una whitelist di MIME, usando il tipo *reale* anche per decidere dove salvarlo. SPW e SR lo fanno; DIS no, e quel «no» è il primo anello di una catena che vedremo al §5.

---

## 3. Il nome del file è un vettore

Anche il nome con cui il file finisce su disco è una decisione di sicurezza, e i tre siti la prendono in tre modi che corrispondono esattamente a tre livelli di rischio. SPW antepone un `uniqid()` a una base ripulita dai punti, così non può mai nascere un `shell.php.jpg` eseguibile via `mod_mime`. SR fa la mossa più radicale: scarta del tutto il nome originale e usa un `uniqid()` puro, nessuna stringa dell'utente entra nel nome finale. DIS conserva nome **ed** estensione, e i punti restano nel set di caratteri ammessi.

```php
// SPW upload.php:73-75 — base SENZA punti interni, poi uniqid: niente doppia estensione
$safeBase = preg_replace('/[^A-Za-z0-9\-_]/', '', pathinfo($fileName, PATHINFO_FILENAME));
$newFileName = uniqid() . '-' . $safeBase . '.' . $fileExt;
```

```php
// SR upload.php:62 — elisione totale: il nome utente è buttato, resta solo uniqid + estensione tecnica
$baseId = uniqid('', true);                     // nessun input utente nel nome del file
```

```php
// DIS upload.php:110-111 — conserva nome ed estensione (i punti sono permessi): il più debole
$filename = uniqid() . '_' . basename($file['name']);
$filename = preg_replace('/[^a-zA-Z0-9_.-]/', '', $filename);   // il "." resta -> estensione preservata
```

> [!TIP]
> **Meno ti fidi del nome, più sei al sicuro: la scala dell'elisione**
> È il punto più controintuitivo del capitolo. La scelta «più gentile», conservare il nome che l'utente ha dato al file, è la più rischiosa, perché lascia all'attaccante il controllo dell'estensione finale. La scelta «più brutale», cancellare il nome e sostituirlo con un identificatore generato dal server, è la più sicura, perché toglie ogni appiglio. SR sta all'estremo protettivo non perché abbia aggiunto una difesa, ma perché ne ha tolta una superficie: il nome del file non è un dato da preservare, è un input da neutralizzare.

---

## 4. Difesa in profondità: tre barriere, una, zero

La validazione e il naming sono difese applicative, e vivono dentro `upload.php`. Ma cosa succede se quel punto viene aggirato, o se domani si aggiunge un secondo modo di scrivere nella cartella? Qui entra la barriera che non dipende dal codice PHP: l'`.htaccess` della cartella `uploads/` che **spegne il motore PHP**. Se Apache non interpreta più i `.php` lì dentro, un file malevolo caricato resta un file inerte, qualunque cosa sia successa prima.

```apacheconf
# SPW public/uploads/.htaccess — la PRIMA barriera anti-RCE: niente esecuzione PHP qui dentro
php_flag engine off
<FilesMatch "\.(php|phtml|phar|cgi|pl)$">
    Require all denied
</FilesMatch>
```

È facile guardare l'`.htaccess` di `uploads/` come una faccenda di **cache-control** (`Expires`, `max-age`), un dettaglio di prestazioni, e fermarsi lì. Il suo uso critico è un altro: è lo spegnimento di PHP, ed è la prima delle tre barriere indipendenti di SPW. Le altre due le abbiamo già viste: il naming che non genera nomi eseguibili (§3) e la validazione sui byte reali (§2). Tre reti per lo stesso rischio, e ognuna copre il buco dell'altra: se l'`.htaccess` non venisse letto, salva il naming; se il naming fallisse, salva l'`.htaccess`; il contenuto camuffato lo ferma il controllo MIME.

SR ha una sola di queste reti, la validazione applicativa: non esiste un `uploads/.htaccess` (la cartella è creata a runtime e non è nel repository), e l'`.htaccess` globale non spegne PHP. Finché `upload.php` resta l'unica via di scrittura, regge; ma non c'è la seconda rete. DIS non ha praticamente nessuna delle tre.

> [!WARNING]
> **Una sola barriera non è difesa in profondità**
> «Validare bene l'upload» è necessario, non sufficiente. La difesa in profondità significa che ogni singola barriera può fallire senza che il sistema cada, perché ce n'è un'altra dietro. Spegnere PHP nella cartella degli upload costa due righe di `.htaccess` e trasforma un'eventuale falla nella validazione da «esecuzione di codice» a «file inutile sul disco». È la barriera con il miglior rapporto tra costo e protezione di tutto il capitolo, ed è anche quella che SR e DIS non hanno.

---

## 5. La tempesta perfetta: la catena RCE da upload pubblico

Le condizioni viste finora, prese una alla volta, sarebbero gestibili. In DIS si sommano, e su un fronte che gli altri due siti non hanno: l'**upload pubblico**. Essendo un sito-festival, DIS accetta le tracce audio caricate dai partecipanti durante l'iscrizione, e per abbassare l'attrito quel caricamento non richiede login. Il gate è deciso per tipo, e per due tipi è semplicemente assente.

```php
// DIS upload.php:64-98 — il gate è per-tipo e INCOERENTE: audio_participant è pubblico
if ($type === 'image') {
    if (!isset($_SESSION['user_id'])) { http_response_code(401); die(...); }   // GATED
    $uploadDir = __DIR__ . '/../uploads/images/';
} elseif ($type === 'audio_participant') {
    $uploadDir = __DIR__ . '/../uploads/audio/participants/';                   // NESSUN gate auth
} elseif ($type === 'audio_podcast') {
    if (!isset($_SESSION['user_id'])) { http_response_code(401); die(...); }    // GATED
    $uploadDir = __DIR__ . '/../uploads/audio/podcasts/';
}
```

Adesso si mettono in fila i quattro anelli. Primo: `type=audio_participant` non chiede login. Secondo: la validazione guarda solo `$_FILES['type']`, il MIME dichiarato dal browser (§2), falsificabile. Terzo: il naming conserva nome ed estensione (§3). Quarto: non c'è `uploads/.htaccess` e l'`.htaccess` globale non spegne PHP (§4), nega soltanto i file `.sqlite` e `.bak`. Il risultato è una richiesta sola.

```bash
# La catena: una POST pubblica deposita uno script PHP eseguibile
curl -F 'type=audio_participant' -F 'file=@shell.php;type=audio/mpeg' https://sito/api/upload.php
#  -> nessun login richiesto  ->  il MIME "audio/mpeg" dichiarato passa la whitelist
#  -> salvato come /uploads/audio/participants/<uniqid>_shell.php  ->  Apache lo esegue
```

> [!WARNING]
> **L'upload pubblico cambia tutte le regole**
> Un upload dietro login è un problema di igiene; un upload pubblico è una superficie d'attacco aperta a Internet, e va trattato con la massima diffidenza. Le quattro debolezze di DIS, da sole, sarebbero rilievi minori. Insieme, su un endpoint senza autenticazione, producono l'esecuzione di codice remoto: il caso peggiore. La difesa non è una sola contromisura ma la loro somma: autenticare dove si può, validare sui byte reali, neutralizzare il nome, e soprattutto spegnere PHP nella cartella, così che anche se tutto il resto cede il file resti inerte (CAP 10). Quando l'upload è pubblico (le iscrizioni del festival, CAP 17), queste non sono raccomandazioni: sono il minimo.

C'è un corollario sgradevole. FDCA, il fork di DIS, ha un `upload.php` byte-identico: eredita la catena intatta, l'upload pubblico, il naming debole e l'assenza di PHP-off, immutati. Un difetto di sicurezza copiato con un `git clone` si moltiplica senza che nessuno lo riscriva. E si noti il ribaltamento rispetto al solito ritornello «più ingegnerizzato uguale più fragile»: qui il sito più scarno (SR, che ha tolto tutto il toglibile) è più sicuro del sito più «accogliente» (DIS, che ha aggiunto l'apertura al pubblico senza aggiungere le difese che quell'apertura richiede).

---

## 6. Ottimizzare l'immagine: WebP, resize, e cosa il libro prometteva di troppo

Superata la validazione, l'immagine viene alleggerita. Qui le scelte divergono, ed è facile appiattirle in una regola unica che il codice reale non rispetta.

SPW e SR **convertono** le raster in WebP via GD (qualità 82, ridimensionamento se la larghezza supera 1920px), poi cancellano l'originale. DIS **non converte**: ridimensiona soltanto, mantenendo il formato di partenza (un PNG resta un PNG, più piccolo). La «transcodifica WebP obbligatoria, standard ufficiale» è dunque il pattern di due siti su tre, non di tutti.

```php
// SPW upload.php:83-119 — conversione WebP + resize, sincrona nell'endpoint, dietro guardia GD
if (in_array($realMime, ['image/jpeg','image/png','image/gif']) && extension_loaded('gd') && function_exists('imagewebp')) {
    if ($origW > 1920) { /* imagecopyresampled a 1920px, alpha preservato */ }
    if (@imagewebp($img, $webpDestination, 82)) { unlink($destination); /* l'originale se ne va */ }
}
```

Tre dettagli meritano una precisazione netta. La GIF è una scelta, non un automatismo: SPW la appiattisce in un fotogramma (l'animazione si perde), SR la **preserva animata** escludendola dalla conversione. La ricodifica GD, come effetto collaterale, **strippa l'EXIF**: la geolocalizzazione e il modello del dispositivo spariscono senza che nessuno lo chieda, una piccola difesa di privacy ottenuta gratis (SR la annota, gli altri no). E il vincolo di dimensione tocca solo la **larghezza** sopra i 1920px: un limite in altezza non c'è, quindi un'immagine altissima e stretta resta enorme.

> [!NOTE]
> **WebP+resize nel thin stack: le varianti, e i suoi limiti**
> L'ottimizzazione è sincrona: avviene dentro il request di upload, senza coda né worker. Su un'immagine grande l'utente aspetta GD prima di vedere la risposta, ma per un sito a basso traffico (con la barra di avanzamento del client, CAP 6) è un compromesso ragionevole. Le varianti reali sono tre: converti in WebP appiattendo la GIF (SPW), converti preservando la GIF animata (SR), ridimensiona soltanto lasciando il formato com'è (DIS). Nessuna è «quella giusta» in assoluto; quella sbagliata è dichiarare universale una regola che due righe di codice contraddicono.

---

## 7. La libreria e la cancellazione: quando il disco è il database

Caricato il file, serve elencarlo e poterlo cancellare. Su questo asse SPW si separa dagli altri due. SPW tiene una tabella `media` con due colonne-nome: `file_path`, l'URL tecnico che carica il browser, e `filename`, il nome umano originale. Quel secondo nome serve a una cortesia: `download.php`, un proxy pubblico che fa lo streaming del file con `readfile`, restituisce all'utente `relazione.pdf` invece di `64f1a2-relazione.pdf`.

SR e DIS non hanno tabella: la libreria è il filesystem, letto con `scandir` (piatto in SR, ricorsivo in DIS). Il disco **è** il database dei media. Semplice, ma con un costo: niente nome originale, niente MIME salvato, ordinamento per data fisica del file. E il dangling media, comune a tutti, qui diventa pure impossibile da tracciare, perché manca persino un punto da cui partire per contare i riferimenti. In DIS gli orfani sono tracce di concorso: dati che si perdono.

La cancellazione è il punto più delicato, perché è una mutazione che tocca il disco, e va protetta su due fronti: il percorso e la richiesta. Sul percorso, i tre siti scalano di nuovo. SPW risolve il path con `realpath` e verifica che stia davvero dentro `/uploads/`, senza fidarsi nemmeno del proprio database. SR usa solo `basename()`. DIS si limita a rifiutare i `..` con uno `strpos`, poi tenta l'`unlink` su più percorsi candidati.

```php
// SPW media.php:31-39 — path-guard con realpath: non si fida nemmeno del DB
$physicalPath = realpath(__DIR__ . '/..' . $filePath);
$uploadsBase  = realpath(__DIR__ . '/../uploads');
if ($physicalPath && $uploadsBase && str_starts_with($physicalPath, $uploadsBase)) {
    unlink($physicalPath);                       // solo se DAVVERO contenuto in /uploads
}
```

```php
// SR media.php — niente auth_utils, sessione nuda, e NESSUN validateCsrf sulla delete
session_start();
if (!isset($_SESSION['user_id'])) { http_response_code(401); exit; }   // no CSRF, no controllo di ruolo
$filename = basename($input['filename'] ?? '');   // unica difesa traversal
if (file_exists($uploadDir.$filename)) unlink($uploadDir.$filename);
```

> [!WARNING]
> **La delete dei media: il path-guard e il token che manca**
> Sul secondo fronte, la richiesta, SR e DIS hanno lo stesso buco: la cancellazione **non ha protezione CSRF**. In SR `media.php` non include nemmeno il prelude di autenticazione del resto del sito, gira con una sessione nuda e non controlla il ruolo; in DIS la protezione CSRF non esiste affatto. Significa che un sito malevolo può far cancellare file all'amministratore loggato con una richiesta forgiata, mitigato solo dal `SameSite` del cookie (CAP 10). È l'incoerenza tipica: l'upload chiede il token, la delete no, eppure cancellare è distruttivo quanto caricare. Un endpoint che cambia lo stato va protetto come tale, sempre, anche quando vive in un file «di servizio» a cui si presta meno attenzione.

---

## 8. Far evolvere lo storage senza fermare il sito

Ogni sito porta le cicatrici di una migrazione dello storage: da raster a WebP, da cartella piatta a sottocartelle. Si leggono negli script one-shot, e raccontano la stessa sequenza: prima gli upload piatti, poi una conversione batch di ciò che c'era già, poi lo smistamento in sottocartelle, infine il riallineamento dei riferimenti rimasti puntati al vecchio percorso.

La differenza che conta è quanta protezione hanno questi script potenti, che spostano file e riscrivono il database. Quelli di SPW seguono il pattern «carica via FTP, esegui dal browser, cancella subito», con il dry-run attivo di default (si guarda prima di toccare). Quelli di SR vivono dentro `admin.php`, dietro il login. Quello di DIS, `migrate_media.php`, **non ha alcun gate**: chiunque, da Internet, può innescare lo spostamento massivo dei file e l'aggiornamento delle righe. La meccanica completa di queste migrazioni, e la disciplina che richiedono, è il capitolo sull'evoluzione del database (CAP 15); qui basta il sintomo, e l'avvertenza che la manutenzione potente esposta in HTTP è una porta sul retro quanto l'upload sul davanti.

---

## In sintesi

Il lato media dei tre siti parte dallo stesso scheletro e diverge su un solo asse che conta davvero: quante difese indipendenti stanno tra un file caricato e l'esecuzione di codice. SPW ne ha tre (PHP spento nella cartella, naming che non genera eseguibili, validazione sui byte reali), e ognuna copre il fallimento dell'altra. SR ne ha una, la validazione applicativa, robusta finché resta l'unica via di scrittura. DIS ne ha quasi nessuna, e per giunta su un upload pubblico: la somma di gate assente, MIME fidato dal client, nome conservato e PHP non spento è la catena RCE che il fork FDCA ha pure ereditato intatta. Le scelte di ottimizzazione (WebP o solo resize, GIF appiattita o animata) e di archiviazione (tabella `media` o filesystem nudo) contano per le prestazioni e per la manutenibilità, ma non spostano il rischio. Il rischio sta nel nome del file, nei byte che non controlli e nel motore che non hai spento. La regola del capitolo è che un upload non va reso «più ricco»: va reso ridondante, perché la prima barriera, prima o poi, cede.

---
*Prossimo Capitolo: Advanced Content Editing & Media Integration. L'editor del contenuto, e come l'HTML che produce viene tenuto al sicuro al momento di mostrarlo.*
