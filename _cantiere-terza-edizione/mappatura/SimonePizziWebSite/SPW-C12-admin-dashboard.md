# Mappatura — SimonePizziWebSite — C12: Admin Dashboard & Panels

> **Stato:** COMPLETATO
> **Sessione:** 11 · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito SimonePizziWebSite)
> - `public/api/stats.php` (statistiche "cifre tonde" per la dashboard, v1.7.4)
> - `public/api/analytics.php` (motore analytics: tracking pubblico + aggregazioni admin, v1.19.0)
> - `public/api/settings.php` (app_settings + cambio password admin)
> - `public/api/backup.php` (dump SQL, export ZIP, pseudo-cron backup automatico, v1.19.0)
> - `public/api/optimize_db.php` (manutenzione DB: ADD INDEX idempotente, v1.9.3)
> - `src/pages/admin/AdminLayout.tsx` (shell + sidebar nav dell'area riservata)
> - `src/pages/admin/Dashboard.tsx` (widget, mini-stat, 6 grafici Chart.js, selettore periodo)
> - `src/pages/admin/Settings.tsx` (cambio password, backup auto/manuale, export ZIP modulare)
> - `src/loaders.ts:10-20` (adminAuthLoader), `:94-100` (adminDashboardLoader), `:169-171` (adminSettingsLoader)
> - `src/App.tsx:232-258` (route tree admin: gate UNICO su AdminLayout)
> - `src/api.ts:63-125` (client settings/backup/stats), `:328-341` (client analytics)

---

## 1. Cosa fa (sintesi narrativa)

C12 è il **cervello lato admin** del flagship contenuti: il cruscotto che il proprietario vede dopo il login e gli strumenti di manutenzione del sito. È il punto in cui convergono i fili di tutti gli altri cluster — i contenuti di C4, i media di C5, le reazioni di C11, gli iscritti di C9, i messaggi di C11 diventano qui **numeri, grafici e azioni**.

Quattro superfici backend + tre superfici frontend:

- **`stats.php`** — i "contatori grandi": totali articoli/pubblicati/media/iscritti/views/click + `system_status: 'Online'`. Risposta piatta a oggetto, una sola query `COUNT` per metrica, fallback a 0 con `try/catch` per le tabelle non ancora migrate. È la fonte delle 7 card grandi della dashboard.
- **`analytics.php`** — il **motore di analisi vero**, a doppia personalità: il ramo `POST` è **pubblico** (tracking `view`/`click` chiamato dal sito live, nessun `Auth`), il ramo `GET` è **admin** (`Auth::check`) e produce ~20 aggregazioni: top articoli per views/reazioni, click per bottone, reazioni per tipo, serie giornaliera su periodo 7/30/90, views oggi/ieri, confronto 7gg vs 7gg precedenti, visitatori unici, conteggi contenuti/newsletter/messaggi, CTR, top categorie. È il **consumer delle reazioni di C11** (`total_reactions`, `reactions_by_type`, `top_articles_by_reactions`).
- **`settings.php`** — due funzioni in un file gated al top: la tabella chiave/valore **`app_settings`** (GET legge tutto, POST upserta) e il **cambio password admin** (PUT, con verifica vecchia password + `session_version++`).
- **`backup.php`** — manutenzione DB router su `?action=`: `download` (dump SQL completo), `export` (ZIP modulare DB+immagini+documenti), `status` (legge `backup_*` da `app_settings`), `cron` (backup automatico schedulabile, gated da admin **o** secret).
- **`optimize_db.php`** — script "fossile" di ottimizzazione: aggiunge indici (`ADD INDEX`) in modo idempotente. **Non distruttivo**.

Lato client: **`AdminLayout.tsx`** è la shell (sidebar + `<Outlet/>`), **`Dashboard.tsx`** il cruscotto con 6 grafici Chart.js, **`Settings.tsx`** il pannello di manutenzione.

---

## 2. Pattern miniCMS rilevanti

- **Gate UNICO sull'intera area admin (route guard, non per-pagina).** A differenza degli endpoint PHP (ognuno chiama `Auth::check` per conto suo), il **frontend** protegge tutta l'area con un solo `loader: adminAuthLoader` sulla rotta che monta `AdminLayout` (`App.tsx:240-241`). Tutte le rotte figlie (dashboard, settings, articles, …) ereditano il redirect a `/admin/login`. `AdminLayout.tsx:9-10` lo documenta esplicitamente in commento. È il pattern di C3 portato a compimento: **una guardia, N pagine**.
- **Endpoint a doppia personalità pubblico/admin nello stesso file** (`analytics.php`): `POST` pubblico per il tracking, `GET` gated. Stessa filosofia "router su `REQUEST_METHOD` con gate selettivo" di C4/C9/C11, ma qui il discrimine non è mutazione-vs-lettura: è **tracking-anonimo (write pubblico) vs reportistica (read privata)**.
- **Gate-per-branch vs gate-al-top** — due stili convivono: `settings.php:5` mette `Auth::check()` **in cima** (robusto: copre ogni metodo presente e futuro); `backup.php` invece lo ripete **dentro ogni ramo** (`:47, :56, :150`) più una logica custom nel ramo `cron`. Vedi §4: il secondo stile è più fragile.
- **Tabella chiave/valore `app_settings` auto-scaffolded** (`settings.php:13-27`): `CREATE TABLE IF NOT EXISTS` + seed dei default (`backup_auto/frequency/last_run`) se vuota. Stesso "schema che viaggia col codice" di `ensureMessagesTable` (C11). È anche il **luogo dei "TODO settings"**: i candidati naturali per i `title/description` hardcoded del feed RSS (C8) sarebbero proprio qui — ma oggi `app_settings` ospita **solo** chiavi di backup.
- **Fallback graceful a 0 per tabelle non migrate** (`try { COUNT } catch (PDOException) { /* tabella non ancora migrata */ }`): ripetuto in `stats.php:28-38` e `analytics.php:213-233` per projects/subscribers/messages. Il pannello non si rompe mai su un'installazione a schema parziale.
- **Loader admin che fanno `Promise.all`** (`adminDashboardLoader:95-98`): stats + analytics in parallelo, oggetti consumati direttamente (niente Double-Read: entrambi tornano `{...}`, non array — coerente con la chiusura del filo Double-Read in C4).
- **Risposta neutra per non rivelare i blocchi** (`analytics.php:62`): superato il rate-limit dei click, ritorna `{status:'ok'}` invece di 429 — il client non distingue "registrato" da "scartato".

---

## 3. Codice chiave (stralci con origine)

### 3.1 La guardia unica dell'area admin (frontend)

```tsx
// App.tsx:239-258 — un solo loader protegge tutto il sotto-albero admin
{
  path: '',
  element: <AdminLayout />,
  loader: adminAuthLoader,          // ← gate UNICO
  children: [
    { index: true,        element: <Dashboard />, loader: adminDashboardLoader },
    { path: 'settings',   element: <Settings />,  loader: adminSettingsLoader },
    { path: 'messages',   element: <MessagesList /> },   // NB: nessun loader → fetch client-side
    // …articles, projects, media, categories, tags, newsletter…
  ],
}
```

```ts
// loaders.ts:10-20 — la guardia: sessione assente → redirect, mai dato admin servito
export const adminAuthLoader = async () => {
    try {
        const session = await api.checkSession();
        if (!session || !session.user) return redirect('/admin/login');
        return session;
    } catch { return redirect('/admin/login'); }
};
```

### 3.2 analytics.php — doppia personalità: tracking pubblico vs report admin

```php
// analytics.php:16-77 — POST pubblico (nessun Auth), GET gated
if ($method === 'POST') {
    // tracking 'view'/'click' — chiamato dal sito live, anonimo
    // [v1.19.0] l'articolo DEVE esistere: niente ID inventati che gonfiano il DB
    $existsStmt = $pdo->prepare("SELECT COUNT(*) FROM articles WHERE id = ?");
    // …'view': dedup IP-hash+articolo+giorno; 'click': rate-limit 10/min con risposta neutra…
}
elseif ($method === 'GET') {
    Auth::check();                       // ← solo la reportistica è privata
    // …~20 aggregazioni per la dashboard…
}
```

### 3.3 analytics.php — il consumer delle reazioni di C11

```php
// analytics.php:131,143-158 — le reazioni mappate in C11 diventano statistiche qui
$total_reactions = (int)$pdo->query("SELECT COUNT(*) FROM article_reactions")->fetchColumn();

$reactions_by_type = $pdo->query("
    SELECT reaction, COUNT(*) AS count FROM article_reactions
    GROUP BY reaction ORDER BY count DESC")->fetchAll();

$top_articles_by_reactions = $pdo->query("
    SELECT a.id, a.title, a.slug, COUNT(ar.id) AS reaction_count
    FROM articles a JOIN article_reactions ar ON a.id = ar.article_id
    GROUP BY a.id ORDER BY reaction_count DESC LIMIT 10")->fetchAll();
```

### 3.4 settings.php — cambio password con invalidazione delle altre sessioni

```php
// settings.php:74-92 — enforcement server-side + session_version (intreccio con C2)
if (strlen($newPassword) < 12) { http_response_code(400); /* … */ exit; }
if ($user && password_verify($currentPassword, $user['password_hash'])) {
    $newHash = password_hash($newPassword, PASSWORD_DEFAULT);
    // session_version++ invalida le ALTRE sessioni (fail-closed di C2);
    // la sessione corrente resta valida aggiornando $_SESSION
    $updateStmt = $pdo->prepare("UPDATE users SET password_hash = ?,
        session_version = session_version + 1 WHERE id = ?");
    $updateStmt->execute([$newHash, $userId]);
    $_SESSION['session_version'] = (int)($_SESSION['session_version'] ?? 0) + 1;
}
```

### 3.5 backup.php — backup automatico FUORI dalla document root (la gemma della card)

```php
// backup.php:192-213 — incident-aware: il deny del repo non arriva mai sul server
// [v1.19.0] I backup vanno FUORI dalla document root quando possibile.
$docroot = realpath(__DIR__ . '/..');
$outside = dirname($docroot) . '/db_backups_simonepizzi';
if (!is_dir($outside)) @mkdir($outside, 0700, true);

if (is_dir($outside) && is_writable($outside)) {
    $backup_dir = $outside;
} else {
    // Fallback dentro la docroot: ma clean-dist.js elimina .data/ dalla dist,
    // quindi il .htaccess di deny del repo NON arriva sul server → ricrealo a runtime
    $backup_dir = __DIR__ . '/.data/backups';
    if (!is_dir($backup_dir)) mkdir($backup_dir, 0700, true);
    foreach ([__DIR__ . '/.data/.htaccess', $backup_dir . '/.htaccess'] as $ht) {
        if (!file_exists($ht)) @file_put_contents($ht, "Require all denied\n");
    }
}
// Nome file non indovinabile dal timestamp + permessi restrittivi
$filename = "auto_backup_" . date('Y-m-d_H-i-s') . '_' . bin2hex(random_bytes(8)) . ".sql";
file_put_contents($backup_dir . '/' . $filename, $sql);
@chmod($backup_dir . '/' . $filename, 0600);
```

### 3.6 backup.php — pseudo-cron gated admin OR secret (timing-safe)

```php
// backup.php:156-166 — schedulabile da cron esterno senza login, ma protetto
$is_admin = isset($_SESSION['user_id']);
$secret = $_GET['secret'] ?? '';
$configured_secret = defined('BACKUP_CRON_SECRET') ? BACKUP_CRON_SECRET : '';
if (!$is_admin && (empty($configured_secret) || !hash_equals($configured_secret, $secret))) {
    http_response_code(403); die("Accesso negato.");   // fail-closed se secret non definito
}
```

### 3.7 optimize_db.php — manutenzione NON distruttiva, idempotente

```php
// optimize_db.php:11-38 — gated, solo ADD INDEX, "indice già esistente" non è errore
Auth::check();
$queries = [
    "ALTER TABLE articles ADD INDEX idx_status (status)",
    "ALTER TABLE article_views ADD INDEX idx_lookup (article_id, ip_hash, view_date)",
    // …nessun TRUNCATE / DROP / OPTIMIZE: solo aggiunta indici…
];
foreach ($queries as $sql) {
    try { $pdo->exec($sql); /* Successo */ }
    catch (PDOException $e) {
        if (strpos($e->getMessage(), '1061') !== false) { /* "Saltato: indice già esistente" */ }
        else { error_log('optimize_db.php: ' . $e->getMessage()); /* msg PDO mai in risposta HTTP */ }
    }
}
```

---

## 4. Problemi riscontrati & soluzioni

- **[GOLD — incident-aware backup placement]** `backup.php:192-213` racconta un incidente reale e la sua soluzione: i backup automatici vanno **fuori dalla document root** (`../db_backups_simonepizzi`); il fallback dentro la docroot (`.data/backups`) è protetto da `.htaccess Require all denied` **ricreato a runtime** — perché `clean-dist.js` (postbuild, già visto in C5/C7) **rimuove `.data/` dalla dist**, quindi il deny committato nel repo non raggiunge mai il server. In più: nome file con suffisso `random_bytes(8)` (non indovinabile dal timestamp), `chmod 0600`, rotazione a 15 copie. È il pattern d'oro "il build può tradire la tua sicurezza statica → difenditi a runtime".
- **[Follow-up sicurezza del prompt — RISOLTO]** Tutti e cinque gli endpoint admin sono gated:
  - `stats.php:12` `Auth::check()` in cima al `try`. ✓
  - `analytics.php:77` `Auth::check()` sul ramo `GET` (il `POST` è tracking pubblico **by design**). ✓
  - `settings.php:5` `Auth::check()` **al top del file** (copre GET/POST/PUT). ✓ (il più robusto)
  - `optimize_db.php:12` `Auth::check()`. ✓
  - `backup.php`: gate **dentro ogni ramo** (`download:47`, `export:56`, `status:150`); `cron:163` gated admin-OR-secret-timing-safe. Nessun ramo raggiungibile senza autenticazione.
- **`backup.php` non espone download path-traversabili.** Non c'è alcun parametro "file" o "path": `download` rigenera il dump dell'intero DB al volo (`generateSQLDump`), `export` zippa cartelle **fisse** risolte via `realpath` (`uploads/immagini|documenti|file`). Nessun input utente entra in un percorso filesystem → **niente path traversal**. (Da raccontare in contrasto col `download.php` di C5, che invece accetta un nome file ed è perciò path-guarded con `realpath`.)
- **`optimize_db.php` NON è distruttivo.** Nonostante l'intestazione lo chiami "script da caricare→eseguire→cancellare" (eco del fossile `init_db` di C1), in realtà esegue **solo `ADD INDEX`** idempotenti (l'errore 1061 "indice già esistente" è trattato come "Saltato", non fatale) ed è **gated** da `Auth::check`. Quindi è sicuro anche se dimenticato sul server. Divergenza tra il commento ("protocollo usa-e-getta") e la realtà (endpoint gated e innocuo) da segnalare.
- **[Fragilità di pattern] gate-per-branch in `backup.php`.** Mettere `Auth::check()` dentro ogni `elseif` (invece che in cima come `settings.php`) funziona oggi ma è **fragile**: aggiungere un nuovo `?action=` e dimenticare la riga del gate aprirebbe un buco. Oggi è coperto (anche perché un `action` sconosciuto cade fuori da tutti i rami e non produce output), ma è il classico anti-pattern "sicurezza ripetuta a mano" vs "sicurezza in un punto solo".
- **`settings.php` POST accetta chiavi arbitrarie (mass-write).** Il salvataggio fa `foreach ($data as $key => $val) { INSERT … ON DUPLICATE KEY UPDATE }` (`settings.php:52-55`): **nessuna whitelist** delle chiavi ammesse. Un admin (gated) potrebbe scrivere qualunque `setting_key`. Rischio basso perché dietro `Auth::check`, ma manca la validazione "solo chiavi note". Da menzionare se in futuro `app_settings` ospiterà flag di sicurezza.
- **IP raw invece di `getClientIp()` (eco di C11/C2).** `analytics.php:40,55` usa `$_SERVER['REMOTE_ADDR']` grezzo per `ip_hash` (dedup view e rate-limit click), **non** l'helper anti-spoof di C2. Stessa divergenza già annotata in C11: dietro proxy/CDN la dedup può collassare. Da uniformare.
- **`secret` del cron in querystring.** `backup.php?action=cron&secret=…` (`:160`) passa il segreto nell'URL → finisce nei log d'accesso del server. Mitigato da `hash_equals` (timing-safe) e fail-closed se non definito, ma il trasporto via GET è subottimale. Annotato.
- **Rotta `messages` senza loader (`App.tsx:257`).** Unica rotta admin che **non** ha un loader react-router: `MessagesList` fa fetch client-side. Funziona (è comunque dietro la guardia `adminAuthLoader` del layout padre), ma è un'incoerenza rispetto alle altre 8 rotte data-driven. Coerente con quanto già osservato in C11 sul pannello messaggi.

---

## 5. Estetica / UX (moderna ma funzionale)

- **Shell `AdminLayout`**: sidebar fissa 64 (`w-64`) con brand "Console**SP**", 9 link nav con icone `lucide-react`, stato attivo evidenziato (`location.pathname.startsWith`), pulsante logout in rosso e link "Vedi Sito Live ↗". Contenuto in `<Outlet/>` dentro `AnimatePresence` framer-motion (transizione pagina `opacity + x:-10`), `React.Suspense` con `<Loader/>` per le rotte lazy.
- **Dashboard ricca, 3 livelli di densità**: (1) **7 stat card grandi** (totali da `stats.php`), (2) **10 mini-stat card** [v1.19.0] con trend %, sub-label e — per "Messaggi Non Letti" — un `<Link to="/admin/messages">` (è **qui che si chiude il pointer di C11**: il badge non-letti citato in C11 vive in questa card), (3) **6 pannelli grafici** Chart.js via `react-chartjs-2` (`utils/chartConfig`): Line area per l'andamento views + 2 Doughnut (click CTA, reazioni per tipo) + 3 liste/barre (top articoli, top articoli per reazioni, top categorie con barre proporzionali).
- **Selettore periodo 7/30/90 gg** (`Dashboard.tsx:41-50, 268-283`): refetch client `api.getAnalytics(p)` senza ricaricare la pagina, con stato `periodLoading` e fallback "mantiene i dati correnti" su errore. Graceful degradation totale: `analyticsError = !analytics` nasconde mini-stat e grafici ma **lascia le 7 card grandi** (alimentate da `rawStats`) → la dashboard non è mai vuota.
- **Settings, 3 sezioni**: (1) cambio password con avviso "password predefinita", validazione client doppia (match + min 12) speculare a quella server; (2) manutenzione DB con backup manuale (download diretto via `window.location.href`) + backup automatico (toggle + frequenza + "ultimo eseguito"); (3) **export modulare** con 3 toggle-card (DB/Immagini/Documenti) e **overlay di caricamento full-screen** con barra shimmer animata durante la compressione ZIP (operazione lunga, `set_time_limit(600)` lato server). Download via Blob + link temporaneo.
- **Palette coerente** col resto del sito: fondo `zinc-950/900`, accento `dis-green`, icone tipizzate per colore semantico (cyan=views, orange=click, rose=reazioni, purple=visitatori).

---

## 6. Differenze rispetto agli altri siti

- *(Da completare nella fase di sintesi cross-sito.)* SimonePizziWebSite porta la dashboard "editoriale" al massimo: analytics first-party fatte in casa (view/click/reazioni tracciate dal proprio `analytics.php`, niente Google Analytics), 6 grafici Chart.js, export modulare. Da confrontare con **SitoRuntime (SR-C12)** — flagship scalabilità — dove il cruscotto potrebbe avere metriche diverse (podcast/speaker) e con la doc incidenti di SR-C13 che potrebbe intrecciarsi col backup automatico qui mappato.
- Il pattern **backup fuori-docroot + .htaccess ricreato a runtime** è da verificare se esiste anche su SitoRuntime (probabile, stessa famiglia di script `clean-dist.js`); se sì, è un pattern trasversale da promuovere a scheda tematica.
- Festival (DIS/FDCA, C10) avranno invece dashboard centrate su voti/partecipanti (`reset_votes`, `stats` master-switch) — un mondo diverso dall'analytics editoriale.

---

## 7. Candidati per il libro

| Cosa | Capitolo (esistente da aggiornare / nuovo) |
|------|--------------------------------------------|
| **Backup fuori-docroot + .htaccess ricreato a runtime** (il build `clean-dist.js` strippa `.data/` → la sicurezza statica non arriva sul server) | Cap. Sicurezza / "quando il build tradisce la tua difesa statica" — box GOLD |
| **Una guardia, N pagine**: route guard unico su `AdminLayout` (frontend) vs `Auth::check` ripetuto per-endpoint (backend) | Cap. Auth / "dove mettere il gate: in un punto solo o in ogni stanza" — confronto frontend/backend |
| **gate-al-top vs gate-per-branch** (`settings.php` vs `backup.php`) | Stesso capitolo — anti-pattern "sicurezza ripetuta a mano" |
| **Endpoint a doppia personalità** (`analytics.php`: POST tracking pubblico / GET report gated) | Cap. API / "un file, due pubblici" |
| **Analytics first-party fatte in casa** (view dedup per IP-giorno, click rate-limited con risposta neutra, niente GA) | Cap. nuovo "Misurare senza terze parti" — privacy + anti-inflazione |
| **Cambio password con `session_version++`** (invalida le altre sessioni, tiene la corrente) | Cap. Auth / sessioni — intreccio con C2 |
| **`app_settings` chiave/valore auto-scaffolded** + il "dove mettere i settings runtime" (i TODO RSS di C8) | Cap. "Configurazione runtime nel DB" |
| **Pseudo-cron gated admin-OR-secret timing-safe** (`hash_equals`, fail-closed) | Cap. "Automazione schedulata senza login" |
| **Manutenzione DB idempotente** (`ADD INDEX`, errore 1061 = "saltato" non fatale) | Cap. "Script di manutenzione che puoi rieseguire all'infinito" |
| **Dashboard a degradazione graziosa** (analytics assente → si nasconde, le card base restano) + Chart.js | Cap. UX/Frontend — cruscotti resilienti |

---

## 8. Note / domande aperte

- **Follow-up sicurezza (risposta puntuale al prompt):**
  1. *Ogni endpoint admin è gated da `Auth::check`?* **Sì.** `stats.php`, `analytics.php` (ramo GET), `settings.php` (top), `optimize_db.php` tutti gated; `backup.php` gated per-ramo (`download/export/status`) e admin-OR-secret per `cron`. Il `POST` di `analytics.php` è pubblico **by design** (tracking anonimo del sito live).
  2. *`backup.php` espone file scaricabili senza gate o con path traversal?* **No.** Download e export sono dietro `Auth::check`; non esiste parametro file/path (dump rigenerato al volo, export su cartelle fisse via `realpath`) → niente traversal.
  3. *`optimize_db.php` fa operazioni distruttive raggiungibili pubblicamente?* **No.** Solo `ADD INDEX` idempotenti, ed è gated. L'intestazione "usa-e-getta" è fuorviante: l'endpoint è innocuo anche se lasciato sul server.
- **Pointer C8 (RSS settings):** i `title/description` hardcoded del feed RSS (i "TODO settings" di C8) avrebbero in `app_settings` la loro casa naturale, ma **oggi quella tabella ospita solo chiavi `backup_*`**. Nessun settaggio "contenuto/SEO/RSS" è ancora persistito lì → il TODO di C8 resta aperto, qui solo confermo che l'infrastruttura (`settings.php` GET/POST) esisterebbe già per ospitarlo.
- **Pointer C2 (auth/anti-spoof):** `analytics.php` usa `REMOTE_ADDR` grezzo invece di `getClientIp()` (come C11). Da uniformare → è C2.
- **Pointer C5/C7 (build pipeline):** `clean-dist.js` (postbuild) torna protagonista — già citato in C5 (`optimize_uploads`) e C7 (dead code prerender); qui è la causa per cui `backup.php` deve ricreare il `.htaccess` a runtime. Candidato a scheda trasversale "la pipeline di build e i suoi effetti collaterali".
- **`BACKUP_CRON_SECRET`:** costante opzionale (`defined(...)`) — verosimilmente in `config.php` (C1). **Non riportato il valore** (segreto). Se non definita, il ramo cron è raggiungibile **solo** da admin loggato (fail-closed corretto).
- **Incoerenza minore:** la rotta `messages` (`App.tsx:257`) è l'unica admin senza loader react-router (fetch client-side), già notato in C11.
- **CHIUSURA SimonePizziWebSite:** con C12 il flagship contenuti è mappato per intero (C1–C9, C11, C12). Prossimo sito: **SitoRuntime** (SR-C1).
