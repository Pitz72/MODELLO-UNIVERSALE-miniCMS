# CAPITOLO 2: Architettura e Struttura Progetto

Questo capitolo definisce l'architettura fisica e logica del sistema: come sono disposte le cartelle, dove vivono i segreti, come una richiesta trova il suo file PHP, e quali difese sono cablate nella struttura stessa invece che aggiunte dopo.

## 1. Topologia delle Cartelle e Separazione degli Asset

Il Modello Universale impone una separazione netta tra i file sorgente (build-time) e i file di runtime (i dati che persistono).

### 1.1 Struttura Fisica (Root)
```text
/
├── public/                 # Contenuto pubblico ed entry-point delle API
│   ├── .htaccess           # Routing SPA (cruciale per React Router)
│   ├── index.php           # SEO Engine (Capitolo 11) — entry-point PHP
│   └── api/                # Core backend PHP (vedi 1.2)
├── src/                    # Frontend React 19 / TS
├── scripts/                # Utility (build, clean, migration)
├── .env.local              # Configurazione locale (VITE_API_URL)
├── package.json            # Dipendenze e script di automazione
└── clean-dist.js           # Sanitizzazione post-build (SECURITY)
```

### 1.2 Anatomia dell'Area API (`public/api/`)

La prima cosa da capire di questa cartella è cosa *non* contiene: un router. Non c'è un `index.php` che smista, non c'è un kernel, non c'è una tabella di rotte. Ogni endpoint è **un file PHP autonomo**: `articles.php`, `upload.php`, `reactions.php`. Ciascuno include all'avvio i suoi mattoni (la connessione al database, l'eventuale prelude di sessione, gli header) e gestisce da sé la propria richiesta. È la scelta fondante del miniCMS, e quella che rende il «thin stack» letteralmente sottile: l'URL `/api/articles.php` è il file `articles.php`, senza intermediari. Il prezzo è qualche ripetizione tra file (lo stesso `require` in cima a ognuno); il guadagno è che ogni endpoint si legge, si testa e si sposta da solo, senza dover capire un sistema di routing.

Accanto agli endpoint vivono le cartelle di runtime, che cambiano a seconda del motore di database scelto:
- **`.data/`**: contiene il database **SQLite**, e quindi esiste solo nei siti che usano SQLite (come DISINTELLIGENZA). Deve contenere un `.htaccess` con `Deny from all`, perché un file `.sqlite` raggiungibile via web è il database intero scaricabile da chiunque. I siti migrati a MySQL non hanno questa cartella: il loro database vive sul server MySQL, fuori dalla docroot per natura.
- **`.cache/`**: file JSON generati per le performance (le liste di contenuti, vedi Capitolo 9), invalidati a ogni scrittura.
- **`uploads/`**: gli asset caricati dall'utente (immagini, audio). Va esclusa dai backup del codice sorgente, e nei siti più difesi ospita un proprio `.htaccess` che **spegne PHP** (la prima barriera anti-RCE, Capitolo 7).

### 1.3 Configurazione e Segreti: Tre Approcci senza Librerie

I segreti non stanno mai nel sorgente versionato. Ma il modo di tenerli fuori è una piccola scala a sé, e i tre siti la occupano in tre punti diversi, tutti senza una libreria di configurazione.

```php
// SPW config.php (gitignorato) — affiancato da config.example.php versionato
define('DB_HOST', 'localhost');
define('DB_NAME', '...');
define('SITE_URL', 'https://...');     // costante canonica, anti host-poisoning
```

```ini
; SR .env (gitignorato) — letto da db_credentials.php via parse_ini_file(); accanto, .env.example
DB_HOST=localhost
TELEGRAM_BOT_TOKEN=...
SMTP_HOST=...        ; l'.env è l'hub di TUTTI i segreti del sito
```

SimonePizziWebSite usa un `config.php` con delle `define()`, ignorato da git e accompagnato da un `config.example.php` committato come traccia. SitoRuntime usa un file `.env` letto con `parse_ini_file()`, ed è l'hub di tutti i suoi segreti (database, token Telegram, credenziali SMTP). DISINTELLIGENZA non ha **nessuna** configurazione: il percorso del file SQLite è scritto direttamente in `db.php`, perché un database-a-file non ha credenziali da custodire. È il principio dei «dodici fattori» (configurazione separata dal codice) applicato senza alcuna libreria, con un'eccezione radicale: chi sta al grado-zero della scala non ha proprio un segreto da gestire.

---

## 2. Sicurezza in Build: la Logica del Clean-Dist

Uno dei rischi maggiori è sovrascrivere il database di produzione durante il deploy. Il sistema lo previene con uno script (`clean-dist.js`) eseguito dopo la build, che:
1. analizza la cartella `dist/api/`;
2. rimuove ricorsivamente ogni file con estensione `.sqlite`, `.sqlite3`, `.db` o `.bak`;
3. avvisa l'operatore con un log di sicurezza (`🚨 SECURITY: Removed...`);
4. garantisce, come **regola progettuale**, che la `dist/` sia «database-free». Il database va inizializzato sul server o migrato a mano, mai sovrascritto dalla build automatica.

Il pattern esatto varia per sito:
- **SimonePizziWebSite**: `"postbuild": "node clean-dist.js"` (hook automatico npm);
- **DISINTELLIGENZA**: `"build": "tsc -b && vite build && node clean-dist.js && move dist\\index.html dist\\index_react.html"` (rinomina `index.html` per abilitare il SEO Engine PHP, Capitolo 11);
- **SitoRuntime**: `"build": "tsc -b && vite build && node scripts/remove-db-from-dist.js"` (script dedicato).

> [!WARNING]
> **Il build può togliere anche le difese, non solo i database**
> Questo script ha un effetto collaterale che ritorna al Capitolo 14: rimuovendo la cartella `.data/` dalla distribuzione, porta via anche l'`.htaccess` di `Deny from all` committato lì dentro. La difesa statica non arriva mai sul server, e va ricreata a runtime. La lezione vale per ogni pipeline di build: chiediti sempre cosa il build *toglie*, non solo cosa aggiunge.

---

## 3. Routing degli URL: SPA contro API

Perché React Router conviva con le API PHP su Apache, lo standard prevede un `.htaccess` nella root pubblica:

```apacheconf
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  # Se la richiesta punta a un file o cartella reale, servilo direttamente (così le API funzionano)
  RewriteCond %{REQUEST_FILENAME} -f [OR]
  RewriteCond %{REQUEST_FILENAME} -d
  RewriteRule ^ - [L]
  # Altrimenti reindirizza tutto a index.html (o index.php se presente)
  RewriteRule ^ index.html [L]
</IfModule>
```

Apache serve `index.php` prima di `index.html` per priorità predefinita. È il meccanismo che permette al SEO Engine (Capitolo 11) di intercettare le richieste dei bot senza toccare le regole di rewrite.

---

## 4. Inizializzazione Dinamica del File System

Il backend PHP non dà per scontata l'esistenza delle cartelle di runtime: le crea quando servono.

```php
// Auto-scaffolding: crea le cartelle di runtime, e protegge subito quella del DB
$paths = [__DIR__ . '/.data', __DIR__ . '/.cache', __DIR__ . '/uploads'];
foreach ($paths as $path) {
    if (!is_dir($path)) {
        mkdir($path, 0755, true);
        if (basename($path) === '.data') {                          // solo il DB-a-file
            file_put_contents($path . '/.htaccess', "Order allow,deny\nDeny from all");
        }
    }
}
```

Chi sta su SQLite (DISINTELLIGENZA) genera la cartella `.data/` e il suo `.htaccess` di `Deny from all` **a runtime**, dentro il codice di connessione: la protezione è prodotta dall'applicazione, non pre-deployata, con un `<Files>` nel `.htaccess` globale come seconda rete. I siti su MySQL non hanno un database-a-file da nascondere, ma applicano lo stesso principio (creare a runtime ciò che il deploy non porta) a `cache`, `uploads` e alla cartella dei backup (Capitolo 14). La regola condivisa: non fidarti che una cartella esista, e non fidarti che una difesa statica arrivi fin sul server.

---

## 5. Gestione degli Ambienti

- **Sviluppo**: il frontend gira sul dev-server Vite, che fa da proxy verso il PHP locale per evitare gli errori CORS. SimonePizziWebSite, che in sviluppo attraversa una porta diversa (`localhost:8888`), è l'unico a dover gestire la cosa anche lato client (Capitolo 6).
- **Produzione**: il frontend punta a `/api`, percorso relativo same-origin, così l'autenticazione via cookie funziona senza CORS e senza configurazione di dominio.

---

## 6. Il Pattern Fork (FDCA da DISINTELLIGENZA)

FDCA e DISINTELLIGENZA condividono una struttura PHP **identica**: stessi file, stessa logica, perché FDCA nasce da un fork del progetto più maturo. È una scelta deliberata: quando due progetti hanno la stessa base funzionale (un festival con votazioni), si parte da una copia di quello che già funziona.

Il vantaggio è l'indipendenza: nessuna dipendenza condivisa, ogni progetto evolve per conto suo. Il rischio è il rovescio esatto di quel vantaggio: ogni bugfix e ogni miglioramento vanno riapplicati a mano su entrambi i rami, e quando il fix riguarda la sicurezza, dimenticarlo significa lasciare una falla aperta in un sito mentre la chiudi nell'altro. È esattamente quello che è successo qui (la catena RCE dell'upload del Capitolo 7 è stata mappata su DISINTELLIGENZA ma vive immutata in FDCA), e il motivo per cui il ciclo di vita di un fork merita un'appendice tutta sua.

> [!IMPORTANT]
> **Il Canone**
> - Un file per endpoint, niente router centrale: ogni endpoint PHP include i suoi mattoni ed è autonomo.
> - Tieni i segreti fuori dal codice versionato (`config.php`/`.env` nel `.gitignore`, con un `.example` committato).
> - Database-a-file e cartelle sensibili fuori dalla docroot, o protetti da un `.htaccess` di deny generato a runtime: il build può rimuovere le difese statiche.
> - Separa la `dist/` dai sorgenti e fa' che `clean-dist` tolga i `.sqlite` dalla distribuzione.

---
*Prossimo Capitolo: Database Strategy. Lock, indici, migrazioni e la vera storia del WAL.*
