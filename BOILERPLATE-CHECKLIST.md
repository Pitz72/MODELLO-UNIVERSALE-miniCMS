# APPENDICE A - Boilerplate Checklist: Avvio Nuovo Progetto miniCMS

Questa checklist riassume i passi pratici per inizializzare un nuovo progetto Web (Sito o Web App) basato sugli standard del «Modello Universale miniCMS». Per i dettagli implementativi, fare riferimento ai capitoli indicati. I rimandi `(Cap. N)` seguono la numerazione della Terza Edizione (20 capitoli + Appendici A e B).

---

## Fase 1: Setup Ambiente e Sicurezza Iniziale
- [ ] Creare la struttura base delle cartelle (`public/api/`, `src/`, `scripts/`). *(Cap. 2)*
- [ ] Creare il file `public/.htaccess` per il routing della SPA (React Router). *(Cap. 2)*
- [ ] Eseguire lo scaffolding del database: cartella `public/api/.data/` con `.htaccess` → `Deny from all`. *(Cap. 2, 3)*
- [ ] Creare la cartella media (`public/api/uploads/`) e la cache (`public/api/.cache/`).
- [ ] Configurare `vite.config.ts` con il proxy corretto per evitare CORS in locale. *(Cap. 6)*
- [ ] Creare `.env.local` con le variabili di sviluppo (`VITE_API_URL=http://localhost/...`).
- [ ] Aggiungere `db_credentials.php` e `.env.local` al `.gitignore` (mai committare credenziali). *(Cap. 15)*

## Fase 2: Configurazione Backend Core (PHP)
- [ ] Implementare `db.php` con connessione lazy a SQLite (`PRAGMA journal_mode=DELETE`, `busy_timeout=5000`, `PRAGMA foreign_keys=ON`). **Non** usare il WAL su hosting condiviso. *(Cap. 3, 15)*
- [ ] Includere l'auto-scaffolding in `db.php`: creazione della cartella `.data/` e dell'`.htaccess` di deny se non esistono. *(Cap. 3)*
- [ ] Creare `init_db.php` per generare le tabelle e l'utente admin di default con `password_hash()` (e cambiarne subito la password). *(Cap. 3, 10)*
- [ ] Creare `auth_helper.php` o `auth.php` con la classe `Auth::check()` che gestisce `session_start()` e gli header JSON. *(Cap. 5)*
- [ ] Configurare i cookie di sessione sicuri (`httponly`, `samesite=Strict`, `secure` se HTTPS). *(Cap. 10)*
- [ ] Applicare `date_default_timezone_set('Europe/Rome')` in **tutti** gli endpoint con logica temporale (l'incoerenza del fuso fa sparire i contenuti programmati). *(Cap. 5, 12, 15)*
- [ ] Nascondere gli errori in produzione (`display_errors = 0` o `try-catch` globale): un `die($e->getMessage())` sul fallimento connessione è un leak. *(Cap. 10)*

## Fase 3: Configurazione Frontend Core (React)
- [ ] Implementare `src/api.ts` con la lettura della forma del payload (il pattern «Double Read» = leggere la busta di successo, non clonare la response) per intercettare gli errori del server. *(Cap. 6)*
- [ ] Configurare `AdminLayout.tsx` con la guardia di auth (route-guard loader o controllo al montaggio) e l'«Hard Logout» (`window.location.reload()`). *(Cap. 14)*
- [ ] Abilitare la «Role-Based UI» per mostrare solo le voci consentite al ruolo connesso (Admin vs Editor): nascondere la pagina è UX, **bloccare l'azione è sicurezza e va fatto sul server**. *(Cap. 10, 14)*
- [ ] Usare `key={item.id}` nel componente editor per forzare il reset del rich text editor al cambio articolo. *(Cap. 8)*

## Fase 4: Integrazione Media e Contenuti
- [ ] Implementare `upload.php` con ridimensionamento automatico GD e sanitizzazione dei nomi (`uniqid()`, estensione ricostruita, non quella del client). *(Cap. 7)*
- [ ] Inserire il componente `MediaPicker` per il caricamento diretto di audio e immagini. *(Cap. 8)*
- [ ] Usare l'editor (Tiptap) con HTML come fonte di verità salvato grezzo; la protezione contro l'XSS è la sanitizzazione **al render** (DOMPurify), non la pulizia all'incolla, che è solo cosmetica. *(Cap. 8)*
- [ ] Implementare la logica slug con normalizzazione degli accenti italiani se il contenuto è in italiano. *(Cap. 5)*

## Fase 5: SEO e Syndication
- [ ] Creare `public/index.php` come SEO Engine: query DB → iniezione dei meta tag nell'HTML di Vite (Dynamic Rendering con UA-sniff). *(Cap. 11)*
- [ ] Aggiungere il rinomina di `index.html` → `index_react.html` nel build script se `index.php` è in `public/`. *(Cap. 2, 11)*
- [ ] Creare `api/rss.php` con un feed RSS 2.0 valido (header corretto, date RFC 822, URL assoluti, content escapato). *(Cap. 12)*
- [ ] Aggiungere il tag `<link rel="alternate" type="application/rss+xml">` nell'`<head>` HTML. *(Cap. 12)*

## Fase 6: Ottimizzazione e Deploy
- [ ] Configurare la «Programmazione Reale» tramite query SQL su `published_at` (confronto **nello stesso formato/fuso**, o delegato a `NOW()`). *(Cap. 9)*
- [ ] Configurare la cache JSON con TTL 300s per le query di listing pesanti. *(Cap. 9)*
- [ ] Impostare `clean-dist.js` nel processo di build per rimuovere i file `.sqlite` dalla cartella `dist/` (e ricreare a runtime le difese statiche che il build strippa). *(Cap. 2, 14)*
- [ ] Configurare l'header `Cache-Control: max-age=31536000` per i file in `uploads/` via `.htaccess`. *(Cap. 7)*

## Fase 7: Sicurezza (le reti emerse dai casi reali)
*Le voci di questa fase sono le difese che, mancando in almeno uno dei siti mappati, hanno prodotto le falle raccontate nel libro.*
- [ ] **Upload con PHP-off**: nella cartella degli upload, un `.htaccess` che disabilita l'esecuzione PHP (prima barriera anti-RCE), più la validazione per magic-bytes (`finfo`), non per il MIME dichiarato dal client. *(Cap. 7)*
- [ ] **CSRF a 3 gradini**: token generato server-side, inviato al client e validato su ogni richiesta che muta stato (POST/PUT/DELETE/azioni admin). Un `confirm()` non è una difesa CSRF. *(Cap. 10, 14)*
- [ ] **Double opt-in newsletter**: due token distinti (conferma e disiscrizione); il link di disiscrizione ha bisogno di un segreto, non basta l'email in chiaro (non è GDPR-compliant). *(Cap. 13)*
- [ ] **Backup automatico fuori dalla document root**, con rotazione e nome non indovinabile; un cron protetto da segreto timing-safe e fail-closed. Avere lo script d'emergenza non sostituisce il backup. *(Cap. 14, 15)*
- [ ] **Sanitizzazione server-side condivisa**: i quattro emettitori del `content` (render, prerender SEO, feed RSS, newsletter) devono passare per la stessa pulizia; uno solo che dimentica riapre il buco XSS. *(Cap. 8, 11, 12, 13)*
- [ ] **Gate per ruolo, non solo per login**: gli endpoint admin verificano `isAdmin`, non solo `isLoggedIn`; le azioni potenti non sono GET senza token. *(Cap. 10, 14)*

## Fase 8: Specifico per Tipologia di Sito

### Per Siti con Newsletter (SitoRuntime pattern)
- [ ] Creare la tabella `subscribers` con lo schema **completo** del double opt-in (`email UNIQUE`, `is_active`, `confirmation_token`, `confirmed_at`, `subscribed_at`, `subscribed_ip`, `created_at`): una tabella, un solo `CREATE`. *(Cap. 13, 15)*
- [ ] Implementare `newsletter.php` con gate admin + azioni pubbliche (subscribe, confirm, unsubscribe). *(Cap. 13)*
- [ ] Usare il pattern `{EMAIL_PLACEHOLDER}` per il link di disiscrizione personalizzato con token. *(Cap. 13)*
- [ ] Distinguere il **throttle** dal **rate-limit**: `usleep(500000)` ogni 10 email regola la cadenza dell'invio (throttle), ma **non** protegge dal mail-bombing; per quello serve un vero rate-limit sull'azione di iscrizione. *(Cap. 13)*

### Per Portfolio/Sito Personale (SimonePizziWebSite pattern)
- [ ] Aggiungere la tabella `projects` con `sort_order`, `is_visible`, `button_a`, `button_b`. *(Cap. 16)*
- [ ] Implementare `projects.php` con i 5 metodi HTTP, incluso PATCH per il toggle di visibilità e il riordinamento. *(Cap. 16)*
- [ ] Creare i componenti `PortfolioGrid.tsx`, `ProjectEditor.tsx`, `ProjectsList.tsx`. *(Cap. 16)*

### Per Festival/Concorso (DISINTELLIGENZA / FDCA pattern)
- [ ] Aggiungere le tabelle `participants`, `votes`, `settings` con i master switch `registration_active` e `voting_active`. *(Cap. 17, 18)*
- [ ] Implementare `participants.php` con il workflow pending → approved/rejected. *(Cap. 17)*
- [ ] Implementare `votes.php` con l'anti-frode reale: la barriera è il vincolo **IP + finestra di 24h** (il cookie è solo cosmetico). *(Cap. 18)*
- [ ] Se il festival nasce come **fork**, mettere in sicurezza il backend da capo: il fork eredita ogni falla, e il fix non lo segue. *(Appendice B)*

### Per Migrazione SQLite → MySQL (SitoRuntime pattern)
- [ ] Fare un backup del `.sqlite` **prima** di toccare il motore, e archiviarlo fuori dal repo. *(Cap. 15)*
- [ ] Creare `db_credentials.php` separato (aggiungere al `.gitignore`). *(Cap. 15)*
- [ ] Aggiornare `db.php` con la connessione PDO MySQL (`utf8mb4`, `EMULATE_PREPARES=false`, `ATTR_TIMEOUT`). *(Cap. 15)*
- [ ] Eseguire `init_mysql.php` per creare lo schema MySQL sul server, poi rimuoverlo. *(Cap. 15)*
- [ ] Eseguire `migrate_to_mysql.php` per il trasloco dati (ONE-SHOT con verifica conteggi, eliminare dopo). *(Cap. 15)*
- [ ] A migrazione conclusa, **rimuovere i fossili del vecchio motore** dal repo (`init_db.php` SQLite, `fix_*`, `optimize_db.php`, `emergency_revert_wal.php`). *(Cap. 15)*

---
*Questa checklist accompagna la Terza Edizione del Modello Universale miniCMS. Per i dettagli implementativi, fare riferimento ai file `.md` dei capitoli e delle appendici corrispondenti.*
