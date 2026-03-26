# CAPITOLO 2: Architettura e Struttura Progetto (v1.2 - ADVANCED)

Questa sezione definisce l'architettura fisica e logica del sistema, garantendo sicurezza dei dati, portabilità e scalabilità.

## 1. Topologia delle Cartelle e Asset Separation
Il Modello Universale impone una separazione netta tra i file sorgente (Build-time) e i file di runtime (Persistent-data).

### 1.1 Struttura Fisica (Root)
```text
/
├── public/                 # Contenuto pubblico e Entry Point API
│   ├── .htaccess           # Routing SPA (Cruciale per React Router)
│   ├── index.php           # SEO Engine (Capitolo 11) — entry-point PHP
│   └── api/                # Core Backend PHP (Vedi 1.2)
├── src/                    # Frontend React 19 / TS
├── scripts/                # Utility Tools (Build, Clean, Migration)
├── .env.local              # Configurazione locale (VITE_API_URL)
├── package.json            # Gestione dipendenze e Script di automazione
└── clean-dist.js           # Script di sanitizzazione post-build (SECURITY)
```

### 1.2 Anatomia dell'Area API (public/api/)
La cartella `api/` deve essere configurata per gestire la persistenza senza dipendenze esterne:
- **.data/**: Contiene il database SQLite. Deve contenere un file `.htaccess` con `Deny from all`.
- **.cache/**: File JSON generati dinamicamente per le performance. Puliti automaticamente ad ogni scrittura.
- **uploads/**: Asset caricati dall'utente (immagini, audio). Deve essere esclusa dai backup del codice sorgente.

## 2. Meccanismi di Sicurezza in Build (The Clean-Dist Logic)
Uno dei rischi maggiori è il "Database Overwrite" durante il deploy. Il sistema implementa uno script `clean-dist.js` eseguito post-build che:
1. Analizza la cartella `dist/api/`.
2. Rimuove ricorsivamente ogni file con estensione `.sqlite`, `.sqlite3`, `.db` o `.bak`.
3. Notifica l'operatore con log di sicurezza (`🚨 SECURITY: Removed...`).
4. **Regola Progettuale**: La cartella `dist/` generata deve essere "database-free". Il DB deve essere inizializzato sul server o migrato manualmente, mai sovrascritto dalla build automatica.

Il pattern esatto del build script varia per sito:
- **SimonePizziWebSite**: `"postbuild": "node clean-dist.js"` (hook automatico npm)
- **DISINTELLIGENZA**: `"build": "tsc -b && vite build && node clean-dist.js && move dist\\index.html dist\\index_react.html"` (rinomina index.html per abilitare il SEO Engine PHP, vedi Capitolo 11)
- **SitoRuntime**: `"build": "tsc -b && vite build && node scripts/remove-db-from-dist.js"` (script dedicato in cartella scripts/)

## 3. Gestione del Routing e degli URL (SPA vs API)
Per permettere a React Router di funzionare in armonia con le API PHP su server Apache, lo standard prevede un `.htaccess` nella root pubblica:

```apacheconf
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  # Se la richiesta punta a un file o cartella reale, servilo direttamente (permette alle API di funzionare)
  RewriteCond %{REQUEST_FILENAME} -f [OR]
  RewriteCond %{REQUEST_FILENAME} -d
  RewriteRule ^ - [L]
  # Altrimenti, reindirizza tutto a index.html (o index.php se presente)
  RewriteRule ^ index.html [L]
</IfModule>
```

**Nota**: Apache serve `index.php` prima di `index.html` per priorità predefinita. Questo è il meccanismo che permette al SEO Engine (Capitolo 11) di intercettare le richieste senza modificare le regole di rewrite.

## 4. Inizializzazione Dinamica del File System
Il backend PHP non deve dare per scontato l'esistenza delle cartelle di runtime. Ogni script di inizializzazione (`init_db.php`) o la classe `Database` devono implementare la logica di **Auto-Scaffolding**:

```php
// Logica di creazione cartelle con permessi corretti (0755)
$paths = [__DIR__ . '/.data', __DIR__ . '/.cache', __DIR__ . '/uploads'];
foreach ($paths as $path) {
    if (!is_dir($path)) {
        mkdir($path, 0755, true);
        // Protezione immediata se è la cartella .data
        if (basename($path) === '.data') {
            file_put_contents($path . '/.htaccess', "Order allow,deny\nDeny from all");
        }
    }
}
```

In **SimonePizziWebSite** questo auto-scaffolding è integrato direttamente in `db.php` (connessione lazy), mentre in altri siti è in `init_db.php`. Entrambi i pattern sono validi; il primo è più robusto perché si attiva ad ogni connessione.

## 5. Gestione degli Ambienti (Env Strategy)
- **Local Dev**: React punta a `http://localhost/tuo-progetto/public/api`.
- **Production**: React punta a `/api` (percorso relativo, garantendo la compatibilità con SSL e domini diversi).
- **Vite Config**: Utilizzo del proxy in fase di sviluppo per evitare errori CORS continui.

## 6. Il Pattern Fork (FDCA / DISINTELLIGENZA)
FDCA e DISINTELLIGENZA condividono **identica struttura PHP** (stessi file, stessa logica). Questo è un pattern deliberato: quando due progetti condividono la stessa base funzionale (es. festival con votazioni), si parte da un fork del progetto più maturo.

**Vantaggi**: Nessuna dipendenza condivisa — ogni progetto evolve indipendentemente.
**Rischio**: Bugfix e miglioramenti vanno applicati manualmente a entrambi i fork. Per questo è fondamentale mantenere una documentazione (questo manuale) come fonte di verità comune.

---
*Prossimo Capitolo: Database Strategy - Dettagli avanzati su lock, indici, migrazioni e la vera storia del WAL.*
