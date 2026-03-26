# BOILERPLATE CHECKLIST: Avvio Nuovo Progetto miniCMS (v2.0)

Questa checklist riassume i passi pratici per inizializzare un nuovo progetto Web (Sito o Web App) basato sugli standard definiti nel "Modello Universale miniCMS". Per i dettagli implementativi, fare riferimento ai capitoli indicati.

---

## Fase 1: Setup Ambiente e Sicurezza Iniziale
- [ ] Creare la struttura base delle cartelle (`public/api/`, `src/`, `scripts/`).
- [ ] Creare il file `public/.htaccess` per il routing della SPA (React Router). *(Cap. 2)*
- [ ] Eseguire lo scaffolding del database: cartella `public/api/.data/` con `.htaccess` → `Deny from all`. *(Cap. 2)*
- [ ] Creare la cartella media (`public/api/uploads/`) e la cache (`public/api/.cache/`).
- [ ] Configurare `vite.config.ts` con il proxy corretto per evitare CORS in locale.
- [ ] Creare `.env.local` con le variabili di sviluppo (`VITE_API_URL=http://localhost/...`).
- [ ] Aggiungere `db_credentials.php` e `.env.local` al `.gitignore` (mai committare credenziali). *(Cap. 14)*

## Fase 2: Configurazione Backend Core (PHP)
- [ ] Implementare `db.php` con connessione Lazy a SQLite (`PRAGMA journal_mode=DELETE`, `busy_timeout=5000`, `PRAGMA foreign_keys=ON`). *(Cap. 3)*
- [ ] Includere Auto-Scaffolding in `db.php`: creazione cartella `.data/` e `.htaccess` se non esistono. *(Cap. 3)*
- [ ] Creare `init_db.php` per generare le tabelle e l'utente admin di default con `password_hash()`.
- [ ] Creare `auth_helper.php` o `auth.php` con classe `Auth::check()` che gestisce `session_start()` e header JSON. *(Cap. 5)*
- [ ] Configurare i cookie di sessione sicuri (`httponly`, `samesite=Lax`, `secure` se HTTPS). *(Cap. 10)*
- [ ] Applicare `date_default_timezone_set('Europe/Rome')` in tutti gli endpoint con logica temporale. *(Cap. 5, 12)*
- [ ] Nascondere gli errori in produzione (`display_errors = 0` o `try-catch` globale). *(Cap. 10)*

## Fase 3: Configurazione Frontend Core (React)
- [ ] Implementare `src/api.ts` con il pattern "Double Read" per intercettare gli errori del server. *(Cap. 6)*
- [ ] Configurare `AdminLayout.tsx` con logica di auth check e "Hard Logout" (`window.location.reload()`). *(Cap. 10)*
- [ ] Abilitare il "Role-Based UI" per mostrare solo le voci consentite al ruolo connesso (Admin vs Editor). *(Cap. 10)*
- [ ] Usare `key={item.id}` nel componente editor per forzare il reset del rich text editor al cambio articolo. *(Cap. 9)*

## Fase 4: Integrazione Media e Contenuti
- [ ] Implementare `upload.php` con ridimensionamento automatico GD e sanitizzazione nomi (`uniqid()`). *(Cap. 5)*
- [ ] Inserire il componente `MediaPicker` per il caricamento diretto di audio e immagini. *(Cap. 8)*
- [ ] Usare l'editor "Clean-HTML" con gestione sicura dell'evento "Paste". *(Cap. 8)*
- [ ] Implementare la logica slug con normalizzazione accenti italiani se il contenuto è in italiano. *(Cap. 5)*

## Fase 5: SEO e Syndication
- [ ] Creare `public/index.php` come SEO Engine: query DB → iniezione meta tag nell'HTML di Vite. *(Cap. 11)*
- [ ] Aggiungere il rinomina di `index.html` → `index_react.html` nel build script se index.php è in public/. *(Cap. 2, 11)*
- [ ] Creare `api/rss.php` con feed RSS 2.0 valido (header corretto, date RFC 822, URL assoluti). *(Cap. 12)*
- [ ] Aggiungere tag `<link rel="alternate" type="application/rss+xml">` nell'`<head>` HTML. *(Cap. 12)*

## Fase 6: Ottimizzazione e Deploy
- [ ] Configurare la "Programmazione Reale" tramite query SQL su `published_at`. *(Cap. 9)*
- [ ] Configurare la Cache JSON con TTL 300s per query di listing pesanti. *(Cap. 7)*
- [ ] Impostare `clean-dist.js` nel processo di build per rimuovere i file `.sqlite` dalla cartella `dist/`. *(Cap. 2)*
- [ ] Configurare header `Cache-Control: max-age=31536000` per i file in `uploads/` via `.htaccess`. *(Cap. 7)*

## Fase 7: Specifico per Tipologia di Sito

### Per Siti con Newsletter (SitoRuntime pattern)
- [ ] Creare tabella `subscribers` con `email UNIQUE`, `is_active`, `created_at`. *(Cap. 13)*
- [ ] Implementare `newsletter.php` con gate admin + azioni pubbliche (subscribe, unsubscribe). *(Cap. 13)*
- [ ] Usare il pattern `{EMAIL_PLACEHOLDER}` per il link di disiscrizione personalizzato. *(Cap. 13)*
- [ ] Abilitare rate limiting con `usleep(500000)` ogni 10 email nel ciclo di invio. *(Cap. 13)*

### Per Portfolio/Sito Personale (SimonePizziWebSite pattern)
- [ ] Aggiungere tabella `projects` con `sort_order`, `is_visible`, `button_a`, `button_b`. *(Cap. 15)*
- [ ] Implementare `projects.php` con i 5 metodi HTTP incluso PATCH per toggle visibilità e riordinamento. *(Cap. 15)*
- [ ] Creare componenti `PortfolioGrid.tsx`, `ProjectEditor.tsx`, `ProjectsList.tsx`. *(Cap. 15)*

### Per Festival/Concorso (FDCA / DISINTELLIGENZA pattern)
- [ ] Aggiungere tabelle `participants`, `votes`, `settings` con master switch `registration_active` e `voting_active`. *(Cap. 16, 17)*
- [ ] Implementare `participants.php` con workflow pending → approved/rejected. *(Cap. 16)*
- [ ] Implementare `votes.php` con protezione IP + cookie anti-frode. *(Cap. 17)*

### Per Migrazione SQLite → MySQL (SitoRuntime pattern)
- [ ] Creare `db_credentials.php` separato (aggiungere al `.gitignore`). *(Cap. 14)*
- [ ] Aggiornare `db.php` con connessione PDO MySQL (`utf8mb4`, `EMULATE_PREPARES=false`). *(Cap. 14)*
- [ ] Eseguire `init_mysql.php` per creare lo schema MySQL sul server. *(Cap. 14)*
- [ ] Eseguire `migrate_to_mysql.php` per trasloco dati (ONE-SHOT, eliminare dopo). *(Cap. 14)*

---
*Questa checklist è generata basandosi sui capitoli del Modello Universale miniCMS v2.0. Per i dettagli implementativi fare riferimento ai file `.md` corrispondenti.*
