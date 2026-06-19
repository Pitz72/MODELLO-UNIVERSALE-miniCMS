# Scheda di Sintesi — S1-C5 — Media & Upload

> **Stato:** COMPLETATO
> **Cluster FASE 2:** S1-C5 · **Data:** 2026-06-19 · **Commit:** _(in corso)_
> **Fonti (card di mappatura, in particolare i §6):** SPW-C5, SR-C5, DIS-C5 (+ FDCA-DIFF: backend byte-identico a DIS → eredita la catena RCE immutata)
> **Capitoli del libro toccati:** CAP 7 (Media & Optimization) — principale · ponti a CAP 10 (Security, upload come superficie d'attacco), CAP 16-17 (Festival, upload pubblico), CAP 14 (storia storage) → vedi §4

---

## 0. In una frase
Tutti e tre i siti caricano i file con lo **stesso scheletro** — un `upload.php` che riceve un
`multipart`, lo valida, lo ottimizza con GD e lo mette su disco — ma è il cluster in cui la
**sicurezza scala all'inverso del buon senso**: la difesa anti-RCE va da **tre barriere indipendenti**
(SPW) a **una sola** (SR) a **quasi zero su un upload PUBBLICO** (DIS), e proprio il naming "più
minimale" (SR, che butta via il nome utente) risulta il **più sicuro**, mentre quello "più gentile"
(DIS, che conserva nome ed estensione) abilita la catena RCE. La lezione del capitolo è una sola
domanda: *quanto puoi togliere a un sistema di upload prima che diventi insicuro* — e DIS mostra cosa
c'è **un passo oltre** quel limite, perché un upload *pubblico* cambia tutte le regole.

## 1. Il pattern comune — la filosofia "thin stack" su questa lente

Sotto le divergenze, il lato media dei tre siti condivide cinque tratti.

**1) Un `upload.php` che riceve un file per volta.** Solo `POST`, `multipart/FormData` (inviato dal
client di S1-C3), `$_FILES['file']`. Niente librerie di gestione media, niente servizio esterno: il
file arriva nello stesso request che lo elabora. È il thin stack applicato all'I/O dei file.

**2) Ottimizzazione immagini sincrona via GD, dentro l'endpoint.** Niente coda, niente worker, niente
cron: il resize (e, dove c'è, la conversione) avviene **nello stesso request**, dietro una guardia
`extension_loaded('gd')` con degradazione graziosa se GD manca. Il resize vincola la larghezza a
≤1920px. L'admin carica un'immagine grande e sul sito ne finisce una alleggerita, senza pensarci.

**3) Naming anti-collisione con `uniqid()`.** Nessun sito conserva il nome utente "così com'è": tutti
antepongono o sostituiscono con un `uniqid()` per evitare sovrascritture e nomi prevedibili. *Quanto*
del nome originale sopravviva è però il primo asse di sicurezza (§2/§3).

**4) Una "libreria" e una "delete" separate dall'upload.** `media.php` elenca i file e ne cancella
uno (con `unlink` fisico); l'upload vero vive solo in `upload.php`. La lettura della libreria è gated;
la cancellazione fa sempre un controllo di percorso prima dell'`unlink` — ma la *robustezza* di quel
controllo (e se ci sia un token) varia molto (§3).

**5) Il riferimento al file è una stringa URL, non una relazione.** Cover, immagini, audio sono
salvati come **percorso testuale** dentro i contenuti/entità (S1-C4: `cover_image`, `audio_file`),
senza foreign key. Conseguenza comune: il **dangling media** — cancellare un file non aggiorna chi lo
referenzia, e nessun sito ha un reference-count.

A questi si aggiunge un tratto di evoluzione condiviso: ogni sito porta i segni di una **migrazione
dello storage** (da raster a WebP, da flat a sottocartelle) sotto forma di script one-shot — con
livelli di protezione molto diversi (§3).

## 2. Le varianti per sito (tabella unica, deduplicata)

| Asse | SimonePizziWebSite | SitoRuntime | DISINTELLIGENZA | *(FDCA)* |
|---|---|---|---|---|
| **Scopo / tipi** | immagini + `pdf/zip/rar/mp3` | **solo immagini** | **immagini + audio** (tracce partecipanti, podcast) | = DIS |
| **Upload pubblico** | no (gated `Auth::check`) | no (gated `isLoggedIn`+CSRF) | **SÌ** per `audio_participant`/`audio` (no auth) | = DIS |
| **Validazione** | estensione **+ magic bytes** (`finfo`) | estensione **+ magic bytes** (`finfo`) | **solo `$_FILES['type']` client** (spoofabile), niente magic/estensioni | = DIS |
| **Naming** | `uniqid-base.ext` (punti **tolti**) | **`uniqid` puro** (nome **scartato**) | **`uniqid_nome.ext`** (nome + estensione **conservati**) | = DIS |
| **Livelli difesa anti-RCE** | **3** (magic bytes + naming + `uploads/.htaccess` PHP-off) | **1** (sole whitelist applicative, **no** PHP-off) | **≈0** → **catena RCE verificata** | = DIS |
| **Image processing** | WebP + resize 1920 q82; GIF → frame statico | WebP + resize; **GIF preservata animata**; EXIF strippato | **solo resize, NO WebP** (formato preservato); solo `type=image` | = DIS |
| **Sottocartelle** | sì, per **MIME reale** (`immagini/documenti/file`) | **flat** `/uploads/` | sì, per **`type` client** (`images/audio/participants/podcasts`) | = DIS |
| **Tabella `media`** | **sì** (`filename` umano, path, mime, size) | **no** (`scandir` piatto) | **no** (`scandir` **ricorsivo**) | = DIS |
| **`download.php` proxy** | **sì** (`readfile` + nome umano + path-guard) | no (statici Apache) | no (statici Apache) | = DIS |
| **Path-guard delete** | `realpath` + containment | `basename()` | **solo `strpos('..')`** + unlink multi-candidato | = DIS |
| **CSRF / gate `media.php`** | `Auth::check()` | **niente CSRF**, sessione nuda (`$_SESSION['user_id']`) | **niente CSRF** (DIS non ne ha), solo `user_id`, no ruolo | = DIS |
| **`uploads/.htaccess` PHP-off** | **presente** | **assente** | **assente** | = DIS |
| **Rate-limit / size-limit** | n/a (gated) | n/a (gated) | **nessuno** + pubblico → storage flooding/DoS | = DIS |
| **One-shot manutenzione** | `optimize_uploads`/`fix_uploads_subfolder` (dry-run, FTP-and-forget) | `optimize_webp`/`fix_image_paths` **in `admin.php`** (gated login) | **`migrate_media.php` NON gated** | = DIS |

**Lettura della tabella.** Sull'asse *sicurezza dell'upload* la scala è netta e va al contrario della
"ricchezza": **SPW** è la difesa in profondità (tre barriere indipendenti, tabella `media`, download
cortese); **SR** è il minimalismo "scarnificato" (niente tabella, niente proxy, niente sottocartelle,
niente `.htaccess` di cartella); **DIS** è il punto in cui il minimalismo incrocia il **rischio
reale**. Ma due caselle ribaltano l'intuizione. La prima è il **naming**: il modo *più minimale* (SR,
`uniqid` puro che cancella ogni input utente) è il **più sicuro**, mentre quello *più gentile* (DIS,
che conserva nome ed estensione) è ciò che abilita la RCE — *meno fiducia nel nome = più sicurezza*.
La seconda è che **DIS reintroduce** due cose che SR aveva tolto — le **sottocartelle** e una libreria
**ricorsiva** — non per sicurezza ma per necessità: un festival con audio eterogenei ne ha bisogno.
Il filo rosso del cluster è che SR mostra *fin dove* si può sottrarre restando (a fatica) sicuri, e
**DIS cosa succede un passo più in là**, su un upload aperto al pubblico.

**FDCA** ha `upload.php` **byte-identico** a DIS (FDCA-DIFF §3): eredita la catena RCE, l'upload
pubblico, il naming debole e l'assenza di PHP-off **immutati**. È il caso del *fork che moltiplica il
debito di sicurezza* → scheda fork.

## 3. GOLD & box problemi-soluzioni

- **La tempesta perfetta dell'upload pubblico: la catena RCE** — *(DIS, verificata)* — il GOLD
  assoluto del cluster. Quattro condizioni che da sole sarebbero gestibili, insieme producono
  l'esecuzione di codice remoto: (a) `type=audio_participant` **non richiede login** (upload pubblico
  per abbassare l'attrito dell'iscrizione); (b) la validazione guarda **solo** `$_FILES['type']`, cioè
  il Content-Type dichiarato dal *browser*, spoofabile; (c) il naming **conserva** nome ed estensione
  (`uniqid_shell.php`); (d) **nessun `uploads/.htaccess`** e il `.htaccess` globale non spegne PHP
  (nega solo `*.sqlite`/`*.bak`). Risultato: una `POST` con `type=audio_participant`, file `shell.php`
  e `Content-Type: audio/mpeg` deposita `/uploads/audio/participants/<uniqid>_shell.php` **eseguibile**.
  → Box "L'upload pubblico cambia tutte le regole" (altissimo valore; ponte CAP 10/16-17).

- **Difesa in profondità: cintura e bretelle (3) vs una barriera (1) vs zero** — *(SPW vs SR vs DIS)*
  — lo stesso rischio (RCE da upload) affrontato con un numero diverso di barriere **indipendenti**.
  SPW ne ha tre: `uploads/.htaccess` che spegne il motore PHP, naming senza punti interni
  (niente `shell.php.jpg`), validazione magic-bytes che ferma il contenuto camuffato — e ognuna copre
  il buco dell'altra (se l'`.htaccess` non viene letto, il naming salva; se il naming fallisse,
  l'`.htaccess` salva). SR ne ha **una sola** (le whitelist applicative di `upload.php`): se quel punto
  venisse aggirato, non c'è seconda rete. DIS non ne ha praticamente nessuna. → Box "Una sola barriera
  non è difesa in profondità".

- **Tre modi di nominare un upload, tre livelli di sicurezza** — *(SPW vs SR vs DIS)* — il box più
  controintuitivo. SPW ripulisce la base dai punti e antepone `uniqid` (`uniqid-base.ext`); SR
  **scarta del tutto** il nome utente (`uniqid` puro) — *elisione totale*, il più sicuro perché nessun
  input utente entra nel nome file; DIS **conserva** nome ed estensione (`uniqid_nome.ext`), il più
  debole, ed è la (c) della catena RCE. Lezione: *il nome del file è un problema di sicurezza*, e meno
  ti fidi, meglio stai. → Box "Il nome del file è un vettore: la scala dell'elisione".

- **`$_FILES['type']` non è validazione** — *(DIS anti-pattern vs SPW/SR pattern)* — il Content-Type
  in `$_FILES` è dichiarato dal client e si falsifica banalmente. La difesa reale è leggere i **byte
  reali** con `finfo`/`mime_content_type()` e confrontarli con una whitelist MIME (SPW e SR), usando
  il MIME *reale* anche per decidere la sottocartella. DIS si fida del client. → Box "Non fidarti
  dell'estensione… né del Content-Type" (ponte alla validazione a doppio strato).

- **Il path-guard della delete: `realpath` vs `basename` vs `strpos`** — *(SPW vs SR vs DIS)* — prima
  di `unlink`/`readfile`, quanto controlli che il percorso sia legittimo? SPW: `realpath` risolto +
  containment dentro `realpath(/uploads)` (non si fida **nemmeno del proprio DB**); SR: solo
  `basename()` (blocca `../../etc/passwd` ma niente containment); DIS: solo `strpos('..')` + unlink di
  più candidati (il più debole). E qui si salda l'altro GOLD: in **SR e DIS la delete non ha CSRF**
  (`media.php` gira con la sessione nuda, senza token) → una mutazione di stato attivabile cross-site,
  mitigata solo dal `SameSite` del cookie. → Box "La delete media: path-guard e il token che manca"
  (ponte S1-C2).

- **Quando il disco è il tuo database dei media** — *(SR/DIS vs SPW)* — SPW ha una tabella `media`
  (due colonne-nome: `file_path` tecnico e `filename` umano, usata da `download.php` per restituire
  `relazione.pdf` invece di `64f1-relazione.pdf`). SR e DIS **non hanno tabella**: la libreria è
  `scandir` (piatto in SR, ricorsivo in DIS), niente nome originale, niente mime salvato, ordinamento
  per `filemtime`. Il **dangling media** è comune a tutti (riferimento solo-URL senza FK), ma senza
  tabella è pure **impossibile da tracciare** — e in DIS gli audio orfani sono *dati di concorso*
  persi. → Box "Il costo di salvare un percorso invece di una relazione" (ponte S1-C4).

- **WebP non è universale (e la GIF è una scelta)** — *(SPW/SR vs DIS)* — SPW e SR convertono le raster
  in WebP via GD (con scelta opposta sulla GIF: SPW la appiattisce in un frame, SR la **preserva
  animata**; SR strippa pure l'EXIF gratis); DIS fa **solo resize**, formato preservato. La
  "transcodifica WebP obbligatoria" del libro è quindi il pattern di due siti su tre. → Box "WebP +
  resize nel thin stack: le varianti" (corregge CAP 7 §3.1, vedi §4).

- **Manutenzione potente esposta in HTTP** — *(DIS vs SR vs SPW)* — gli script che spostano file e
  riscrivono il DB hanno protezioni molto diverse: `migrate_media.php` di **DIS non è gated** (chiunque
  triggera lo spostamento massivo, coerente con gli `update_db_*` esposti di S1-C1); gli one-shot di
  **SR** vivono dentro `admin.php` (gated login); quelli di **SPW** sono FTP-and-forget con **dry-run**
  di default. Tutti raccontano l'**evoluzione dello storage** (flat → WebP batch → sottocartelle → fix
  dei riferimenti), ma con superfici d'attacco diverse. → Box "Far evolvere lo storage senza downtime"
  + nota sicurezza (ponte S1-C13).

## 4. Mappa → capitolo/i del libro

| Materiale della scheda | Capitolo esistente | Azione |
|---|---|---|
| **Sicurezza dell'upload** (scala 3/1/0, magic bytes, naming, path-guard) | **CAP 7** (nuova sezione) + **CAP 10** | **nuova sezione**: oggi CAP 7 NON parla di sicurezza upload (lacuna grave, vedi correzioni) |
| **La catena RCE da upload pubblico** (DIS) | **CAP 7** (box) + **CAP 16-17** (festival) | **nuovo box** ad alto valore (e ponte al festival, dove l'upload è pubblico) |
| Validazione a doppio strato (estensione + magic bytes) | **CAP 7 §3** | **aggiorna**: integra la validazione *prima* dell'ottimizzazione |
| Naming anti-doppia-estensione: i tre modi | **CAP 7 §3** | **nuovo box** |
| Image processing WebP+resize: SPW/SR convertono, DIS solo resize | **CAP 7 §3.1** | **correggi**: WebP non è universale (vedi correzioni) |
| `uploads/.htaccess`: prima di tutto PHP-off, non solo cache | **CAP 7 §3.3** + **CAP 10** | **riscrivi §3.3**: oggi è solo cache-control (vedi correzioni) |
| Tabella `media` vs filesystem (`scandir`) + dangling media | **CAP 7** + **CAP 9** (ponte) | **nuovo box**: "quando il disco è il database dei media" |
| `download.php` proxy (nome umano, path-guard) vs file statici | **CAP 7** | **nuovo box**: "due nomi per un file" + "quando un endpoint media NON va protetto" |
| Delete senza CSRF + path-guard debole (SR/DIS) | **CAP 10** (ponte da CAP 7) | **nuovo box** sicurezza |
| Evoluzione storage (flat→WebP→sottocartelle) + one-shot non gated | **CAP 14** | **ponte**: storia migratoria + nota sui maintenance script esposti |
| Upload pubblico delle tracce: apertura vs hardening | **CAP 16-17** (Festival) | **nuovo box** (il trade-off dell'iscrizione senza attrito) |

**Correzioni al testo attuale (la mappatura smentisce / disallinea il libro):**
- **CAP 7 ignora quasi del tutto la SICUREZZA dell'upload.** Il capitolo tratta l'upload solo come
  problema di *ottimizzazione* (WebP, resize, cache-control). Mancano completamente: la validazione
  magic-bytes vs estensione, il naming anti-doppia-estensione, il path-guard, la delete senza CSRF e —
  soprattutto — la **catena RCE da upload pubblico** che è il GOLD dell'intero cluster. È la lacuna più
  grave del capitolo: va aggiunta una sezione "Sicurezza dell'upload" con la scala a 3/1/0 barriere e
  il box RCE di DIS.
- **CAP 7 §3.3 — `uploads/.htaccess` è presentato SOLO come cache-control.** Il suo uso *critico* (in
  SPW) è il **PHP-off**: spegnere il motore PHP nella cartella upload è la **prima barriera anti-RCE**,
  non un dettaglio di performance. E SR/DIS **non ce l'hanno affatto**. Da riscrivere: l'`.htaccess` di
  `uploads/` è prima di tutto sicurezza; la cache-control è secondaria; e non è universale.
- **CAP 7 §3.1 — la "transcodifica WebP obbligatoria, standard ufficiale" non vale per tutti.** SPW e
  SR convertono in WebP; **DIS fa solo resize** (formato preservato). Da correggere: WebP+resize è il
  pattern di due siti, "solo resize" è il terzo. Inoltre il libro dichiara il vincolo "max 1920px
  larghezza **o 1080px altezza**": il codice reale (tutti e tre) vincola **solo la larghezza** >1920 —
  un'immagine altissima e stretta resta enorme. Prescrizione non rispettata dal codice.
- **CAP 7 §4 — gli script di manutenzione non sono sempre "protetti".** Il libro li dà per "script
  protetti": in realtà la protezione varia (SPW FTP-and-forget + dry-run; SR dentro `admin.php` gated;
  **DIS `migrate_media.php` non gated affatto**). Da annotare con ponte a S1-C2 (manutenzione esposta
  in HTTP).
- **Nota di scope (per S3, non da risolvere qui):** CAP 7 §1 (caching TTL) e §2 (SEO pre-rendering)
  appartengono a CAP 9 (cache di contenuto, già toccata in S1-C4) e CAP 11 (SEO). Il capitolo "Media"
  è oggi mis-scoped: andrà ribilanciato verso l'upload/ottimizzazione media in fase di scaletta (S3).

## 5. Cosa si scarta / dedup

- **Ripetizioni fuse:** i §6 delle tre card confrontavano lo stesso flusso (SR tabella 12 righe vs
  SPW, DIS tabella a TRE 12 righe). Qui la comparazione è scritta **una volta sola**, deduplicata,
  attorno alla scala difesa-in-profondità 3→1→0 e al ribaltamento del naming.
- **Dettaglio per-sito che NON entra nel libro:** numeri di riga, il fallback `octet-stream`→`zip` di
  SPW, l'helper WebP duplicato di SR (`upload.php` ≡ `admin.php`), il `require db.php` fossile e
  inutilizzato di `media.php` in SR, il commento stale "SQLite" in `media.php` di SPW, le query `LIKE`
  esatte di `migrate_media.php`. Restano nelle card come fonte.
- **Materiale che appartiene ad altre schede (per evitare doppioni a valle):**
  - **lato client** dell'upload (`FormData`, XHR-progress vs spinner, `credentials`) → **S1-C3
    (Frontend Bridge)**; qui solo come il file arriva e viene elaborato lato server.
  - **gate, CSRF, `.htaccess` come hardening, ruoli, l'upload pubblico come superficie d'abuso** →
    **S1-C2 (Security & Auth)**; qui solo la *meccanica* media (validazione, naming, path-guard) con i
    rimandi.
  - **`cover_image`/`audio_file` come stringa-URL nei contenuti/entità** → **S1-C4 (Content)** e
    **S1-C10 (Festival)**; qui solo l'origine del dangling.
  - **embed di immagini dentro il `content` dell'editor** (non solo cover/galleria) → **S1-C6
    (Editor)**; qui solo come il file finisce su disco, non come entra nel testo.
  - **storia delle migrazioni storage** (raster→WebP, flat→sottocartelle, tabella `media` mai esistita
    in SR) → **S1-C13 (DB/Storage Evolution)**; qui solo il *sintomo* (gli one-shot e la loro
    protezione).
  - **upload pubblico delle tracce come parte del flusso iscrizione/concorso** → **S1-C10 (Festival
    Logic)**; qui solo il deposito del file su disco e la catena RCE che ne deriva.
