# Mappatura — SitoRuntime — C12: Admin Dashboard & Panels

> **Stato:** COMPLETATO
> **Sessione:** 18 (SR-C12 da sola) · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `SitoRuntime/`)
> - `public/api/admin.php` (**il MEGA-ROUTER del sito**: 17 `?action=` in un solo file — login/logout/check_auth/change_password [C2], CRUD news [C4], user management [C12], WebP/fix_image_paths [C5], migrazioni v291/v293 [C13], test_smtp [C9/diagnostica])
> - `public/api/admin.php:174-227` (`list_users`/`create_user`/`delete_user` — l'UNICO pannello *proprio* di C12 lato backend)
> - `public/api/admin.php:151-172` (`change_password` — meccanica C2, qui come UX del pannello "Impostazioni")
> - `src/pages/Admin.tsx` (**il guard-COMPONENTE monolitico** di SR-C3 + l'INTERA area admin in un solo file: 8 sezioni a card, 596 righe)
> - `src/components/admin/UserManagement.tsx` (pannello utenti: crea/lista/elimina con badge ruolo)
> - `src/App.tsx:25,68` (`<Route path="/admin" element={<Admin/>}>` — UNA rotta, NESSUN loader, NESSUN AdminLayout)
> - `public/api/init_mysql.php` (controprova: NESSUNA tabella `app_settings`/`analytics`/`views`/`backup`)
> - **Controprova negativa (grep su tutto `public/api/*.php`):** nessun `app_settings`, `backup`, `analytics`, `track`, `view_count` — solo `COUNT(*)` sparsi (news in `list`, subscribers in `newsletter.php count`)

---

## 1. Cosa fa (sintesi narrativa)

C12 in SitoRuntime è la risposta-per-sottrazione a SPW-C12. Dove SimonePizziWebSite aveva **quattro file
backend dedicati** (`stats.php`, `analytics.php`, `settings.php`, `backup.php`) e una dashboard a tre livelli
di densità con sei grafici Chart.js, SitoRuntime **non ha quasi nulla di tutto questo**. Il "cruscotto" admin
di SR è due cose:

1. **Lato backend, `admin.php` è il MEGA-ROUTER** già incontrato in C2/C4/C5/C9: un solo file con 17 azioni
   `?action=`. Ma — letto con la lente di C12 — quasi tutte quelle azioni *appartengono ad altri cluster*. Le
   azioni **proprie di C12** sono pochissime: la **gestione utenti** (`list_users`/`create_user`/`delete_user`,
   `:174-227`) e il **cambio password come voce di un pannello "Impostazioni"** (`change_password`,
   `:151-172`, meccanica C2). **Non esiste alcun endpoint di statistiche, analytics, tracking, backup,
   export, impostazioni chiave/valore o cron.** La controprova è netta: `grep` su tutto `public/api/` per
   `app_settings|backup|analytics|track` torna **a vuoto**.

2. **Lato frontend, `Admin.tsx` È l'intera area riservata in un solo componente** (596 righe). È il
   **guard-COMPONENTE** di SR-C3 (`checkAuth()` on mount → `<LoginForm>` se `!user`, `:74-88`), e subito sotto
   monta un "Dashboard" che in realtà è un **selettore di sezioni a schede**: otto `DashboardCard` che NON
   contengono dati — sono bottoni di navigazione che cambiano lo stato `section` e fanno apparire, nella stessa
   pagina, il pannello corrispondente. Le otto sezioni (`news`, `speakers`, `settings`, `users`, `newsletter`,
   `feeds`, `media`, `podcasts`) montano i sotto-componenti degli altri cluster. **`Admin.tsx` è quindi
   l'AGGREGATORE di tutte le UI admin del sito**, non un cruscotto analitico.

Il risultato è una dashboard che **non misura niente**: zero contatori, zero grafici, zero trend, nessun
`system_status`. È una console CRUD pura. Il sito-flagship della *scalabilità e degli incidenti* ha l'area
admin **più povera di strumenti** dei due flagship — un paradosso che vale da solo un box nel libro.

## 2. Pattern miniCMS rilevanti

- **Guard-COMPONENTE vs route-guard (la divergenza-madre con SPW).** SPW protegge tutta l'area admin con un
  **unico `loader: adminAuthLoader`** sulla rotta che monta `AdminLayout` (una guardia, N pagine figlie
  data-driven). SR ha **una sola rotta** `/admin` → un solo `<Admin/>` (`App.tsx:68`), **senza loader**: la
  guardia è il `useEffect(checkAuth)` dentro il componente (`Admin.tsx:74-88`), che è esattamente il pattern
  diagnosticato in SR-C3. Non c'è `AdminLayout`, non c'è sotto-albero di rotte, non c'è redirect: se non sei
  loggato vedi `<LoginForm>` *dentro* la stessa pagina.
- **"Dashboard" = section-switcher in-component.** Le otto `DashboardCard` (`Admin.tsx:234-299`) sono bottoni
  che fanno `onClick={() => setSection('...')}`; il contenuto è renderizzato in linea sotto da una catena di
  `{section === '...' && (...)}` (`:306-588`). Niente router, niente `<Outlet/>`, niente lazy per-sezione:
  tutto è in memoria nello stesso componente. È il pattern "SPA dentro la SPA", l'opposto del data-router di
  SPW.
- **`Admin.tsx` come aggregatore dei cluster.** Ogni sezione monta il pannello di un altro cluster:
  `ArticleEditor` (C4/C6), `SpeakerEditor`/`PodcastManager`/`MediaGallery` (C4/C5), `NewsletterComposer` (C9),
  `UserManagement` (C12/C2), il box Feed Telegram (C8). C12 qui è soprattutto **il telaio** che li tiene
  insieme + i due pannelli propri (utenti, password).
- **Mega-router `admin.php` con gate stratificato.** Le azioni pubbliche/auth stanno in cima (login/check/
  logout/change_password, C2); poi un blocco **admin-only** sugli utenti (`$_SESSION['role'] !== 'admin'`,
  `:177,189,216`); poi un **gate unico** `if (!isLoggedIn()) sendError('Unauthorized',401)` (`:231`) dopo il
  quale vivono CRUD news (C4) e tutte le azioni di manutenzione/migrazione (C5/C9/C13). Un solo file, tre
  livelli di accesso, con il confine segnato da poche righe — variante del pattern "gate a metà file" già
  visto in `newsletter.php` (C9).
- **Operazioni di manutenzione URL-triggered senza UI.** `optimize_webp`, `fix_image_paths`,
  `apply_v291_status`, `apply_v293_newsletter`, `test_smtp` sono azioni **GET** che si lanciano **digitando
  l'URL nel browser** (gated `isLoggedIn`): non esiste alcun bottone nella dashboard che le invochi. È la
  "console nascosta" del sito — manutenzione a mano, senza pannello (cfr. §4).

## 3. Codice chiave (stralci con origine)

### 3.1 La guardia è il componente, non un loader (SR-C3 portato in C12)

```tsx
// Admin.tsx:74-88 — checkAuth on mount; nessun adminAuthLoader, nessun redirect
useEffect(() => { checkAuth(); }, []);
const checkAuth = async () => {
    try {
        const res = await api.checkAuth();
        if (res.authenticated) { setUser(res.user); loadData(); }
    } finally { setLoading(false); }
};
// …
if (loading) return <Loader … />;
if (!user)  return <LoginForm onLogin={handleLogin} />;   // ← la "guardia": rende il login NELLA stessa pagina
```

```tsx
// App.tsx:68 — UNA rotta, nessun loader, nessun AdminLayout (vs il sotto-albero di SPW)
<Route path="/admin" element={<Admin />} />
```

### 3.2 La "Dashboard" è un selettore di sezioni: le card non portano dati

```tsx
// Admin.tsx:234-299 — 8 DashboardCard = TAB di navigazione (icona+titolo+descrizione, ZERO numeri)
<DashboardCard icon={Newspaper} title="Gestisci News" description="Scrivi, modifica o elimina…"
    onClick={() => setSection('news')} isActive={section === 'news'} />
// …Utenti, Speaker, Newsletter, Podcast, Media, Feed Telegram, Impostazioni…
// Nessuna card mostra contatori/trend: a differenza delle "stat card" di SPW, qui è puro menu.
```

### 3.3 Il pannello PROPRIO di C12 lato backend: gestione utenti a ruoli

```php
// admin.php:176-213 — list/create con gate admin-only (role grezzo, non isAdmin())
if ($action === 'list_users') {
    if ($_SESSION['role'] !== 'admin') sendError('Forbidden: Admins only', 403);
    $stmt = getDB()->query("SELECT id, username, role, created_at FROM users ORDER BY created_at DESC");
    sendSuccess(['users' => $stmt->fetchAll(PDO::FETCH_ASSOC)]);
}
// create_user: validateCsrf + check duplicato + password_hash, ruolo default 'editor'
// delete_user: validateCsrf + "Prevent suicide" if ($targetId == $_SESSION['user_id']) (:222)
```

### 3.4 Settings = SOLO cambio password (niente app_settings, niente session_version)

```php
// admin.php:151-172 — nessun min-length server, nessun session_version++ (SR non ha la colonna)
if ($user && password_verify($oldPass, $user['password_hash'])) {
    $newHash = password_hash($newPass, PASSWORD_DEFAULT);
    getDB()->prepare("UPDATE users SET password_hash = ? WHERE id = ?")->execute([$newHash, $userId]);
    sendSuccess(['message' => 'Password updated successfully']);
}
```

```tsx
// Admin.tsx:170-180 — il "logout forzato" client-side SOSTITUISCE l'invalidazione sessioni di SPW
const res = await api.changePassword(oldPass, newPass);
if (res.success) {
    setSettingsMsg({ text: 'Password aggiornata. Reindirizzamento al login...', ok: true });
    setTimeout(handleLogout, 1500);     // ← SPW lo fa col server (session_version++), SR col client
}
```

### 3.5 Le operazioni di manutenzione: GET dietro `isLoggedIn`, ma senza bottone e senza isAdmin

```php
// admin.php:231 — gate unico; tutto ciò che segue richiede login (ma NON ruolo admin, NON CSRF perché GET)
if (!isLoggedIn()) { sendError('Unauthorized', 401); }
// …poi: optimize_webp (:348), apply_v293_newsletter (:374), test_smtp (:399),
//        apply_v291_status (:459), fix_image_paths (:473) — si lanciano digitando l'URL, nessuna UI.
```

## 4. Problemi riscontrati & soluzioni

- **🔒 GOLD — "La dashboard che non misura niente": l'intero strato analytics/stats è ASSENTE.** Risposta
  diretta al prompt: in SR **non esiste** `stats.php`, `analytics.php`, `settings.php` né `backup.php`; non
  esiste tracking `view`/`click`, non esiste tabella `app_settings` o `analytics`/`views` (`init_mysql.php` non
  le crea; `grep app_settings|backup|analytics|track` → **zero**), non c'è Chart.js, non c'è alcun contatore in
  dashboard. L'admin è una **console CRUD pura**. Dove SPW-C12 era il "cervello analitico" del sito (≈20
  aggregazioni, 6 grafici, dedup view per IP-giorno, CTR, top-articoli-per-reazioni), SR-C12 è un **menu di
  pannelli di editing**. Box ad alto valore: *"quanto puoi togliere a una dashboard prima che resti solo un
  menu"* — gemello del framing di SR-C5 sull'upload. È anche la prova che i due flagship hanno fatto scelte
  opposte: SPW investe nell'osservabilità first-party, SR la salta del tutto.

- **🔒 GOLD — Nessun backup, nessun export, nessun cron: il flagship "incidenti" non si protegge.** Sempre come
  risposta al prompt: SR **non ha alcun backup del DB**, nessun export ZIP, nessuno pseudo-cron. La gemma di
  SPW-C12 (backup automatico FUORI dalla docroot, nome `random_bytes`, `chmod 0600`, rotazione, pseudo-cron
  `hash_equals` admin-OR-secret, il tutto perché `clean-dist.js` strippa `.data/`) **non ha contropartita
  qui**. Paradosso forte da raccontare: SitoRuntime è il sito mappato proprio per *scalabilità e incidenti*
  (WAL corruption, `emergency_revert_wal.php`, migrazioni di emergenza → C13), eppure è privo di qualunque
  **backup preventivo**. Ha la *cura* (revert d'emergenza) ma non la *prevenzione* (snapshot schedulati). È il
  contrasto che dà senso a C13: gli incidenti fanno più male perché non c'è una rete di salvataggio.

- **🔒 GOLD — `change_password` senza `session_version`: invalidazione sessioni fatta dal client.** SPW alla
  modifica password fa `session_version + 1` lato DB (invalida le ALTRE sessioni, fail-closed di C2). SR **non
  ha** la colonna `session_version` (assente fin da SR-C2): `change_password` (`:166`) aggiorna solo
  `password_hash`. La compensazione è **client-side**: `Admin.tsx:174` fa `setTimeout(handleLogout, 1500)`,
  cioè sloggа l'utente *corrente* dopo il cambio. Differenza didattica netta: stessa esigenza ("dopo il cambio
  password, fuori le sessioni"), risolta sul **server** in SPW e sul **client** in SR — e la versione SR non
  invalida affatto eventuali altre sessioni aperte altrove (mitigato dal fatto che la sessione è de-facto
  same-origin e dura 1h, SR-C2). Inoltre **manca il minimo lunghezza server-side** (SPW imponeva ≥12): SR
  accetta qualunque nuova password lato backend.

- **Gate ruolo che nasconde il contenuto ma NON la card.** Nel frontend le sezioni `users` e `newsletter` sono
  guardate da `&& user?.role === 'admin'` sul **contenuto** (`Admin.tsx:522,529`), ma le rispettive
  `DashboardCard` sono **sempre renderizzate** (`:235,259`). Conseguenza: un utente con ruolo `editor` vede le
  schede "Gestisci Utenti" e "Newsletter", ci clicca sopra e ottiene un **pannello vuoto** (il blocco `&&` non
  rende nulla). Il backend è coerente (403 su `list_users`/`create_user`/`delete_user`), quindi non è un buco
  di sicurezza, ma è un **gap di UX**: la card promette una pagina che per l'editor non esiste. SPW lo evita
  perché la nav è generata e le rotte hanno il loro gate.

- **Manutenzione/migrazioni dietro `isLoggedIn` ma non `isAdmin`, e senza UI.** `optimize_webp`,
  `apply_v291_status`, `apply_v293_newsletter`, `fix_image_paths`, `test_smtp` stanno dopo il gate `isLoggedIn`
  (`:231`) → richiedono login (bene), ma **non** controllano il ruolo admin e — essendo GET — **non** passano
  da `validateCsrf`. Quindi un qualunque `editor` loggato può lanciare una **migrazione di schema**
  (`apply_v291_status` fa `ALTER TABLE news`) o una conversione WebP di massa digitando l'URL. Rischio
  contenuto (serve comunque una sessione valida), ma è il classico "operazioni potenti senza confine di
  ruolo". E il fatto che non esista **alcun bottone** che le invochi le rende una "console nascosta": chi non
  conosce gli `?action=` non sa che esistono. → la meccanica DB di queste azioni è **C13**; qui si annota solo
  che vivono nell'hub admin senza pannello.

- **`role` grezzo invece di `isAdmin()`.** Il gate utenti usa `$_SESSION['role'] !== 'admin'` (`:177,189,216`)
  invece dell'helper `isAdmin()` di SR-C2 — stessa micro-incoerenza già notata in `newsletter.php` (C9). E
  `check_auth` (`:135-139`) prova a leggere `$_SESSION['username']`, che però **non viene mai scritto** al
  login (`:123-124` salva solo `user_id` e `role`) → `username` in `check_auth` è sempre `null` (in pratica il
  client usa `username` solo dalla risposta di `login`, non da `check_auth`). Filo C2/C3.

- **`disabled` prop morta nella `DashboardCard`.** L'interfaccia (`Admin.tsx:24`) e il rendering (`:31,36,37`)
  gestiscono uno stato `disabled`, ma **nessuna** delle otto card lo passa: codice predisposto per pannelli da
  abilitare/disabilitare (es. per ruolo) mai cablato. Coerente col gap-UX sopra: la disabilitazione per ruolo
  era *prevista* ma non collegata.

## 5. Estetica / UX (moderna ma funzionale)

- **Header "CMS · Dashboard"** con badge mono-spaziato `CMS`, saluto `Welcome, <username>` e bottone logout
  (`Admin.tsx:209-232`). Il titolo dice "Dashboard" ma — come da §4 — non c'è alcun dato: è una **promessa
  lessicale** non mantenuta (nessun `system_status: Online` come in SPW).
- **Griglia di 8 card** responsive (`grid-cols-1 md:2 lg:4`, `:234`) con icona colorata (`lucide-react`),
  titolo, descrizione, stato attivo evidenziato dal bordo teal + barra inferiore (`:44-46`), hover sul bordo.
  Estetica curata e coerente (variabili CSS `--c-teal`/`--c-card`/`--c-elevated`), ma la card è **navigazione**,
  non informazione.
- **Area contenuti unica** (`:302-589`) con `min-h-[400px]` e classe d'ingresso `page-enter` per ogni sezione
  (micro-transizione CSS, non framer-motion come SPW). Dentro: liste news (con badge **Bozza**/**Programmato**
  calcolati client da `status`/`published_at`, `:337-352`, eco di C4) e speaker (avatar tondo, badge
  **Founder**), con paginazione news client-side (`:372-392`).
- **Sezione "Impostazioni"** (`:477-519`): un singolo form "Cambia Password" (vecchia/nuova) con messaggio
  inline `settingsMsg` colorato per esito. **È tutta qui** la sezione settings — nessun toggle backup,
  frequenza, export, o chiavi di configurazione. Minimalismo estremo vs le 3 sezioni di SPW (password + backup
  + export ZIP con overlay shimmer).
- **Sezione "Feed Telegram"** (`:535-573`): box che mostra l'URL del feed news privato (da `getFeedConfig`,
  C8) con bottone "Copia Link" e l'avvertenza *"Usa questo link nel tuo Bot Telegram… NON condividere"* — è il
  punto frontend del `feed_config.php` security-theater diagnosticato in SR-C8 (l'URL è in realtà pubblico). →
  puntatore C8.
- **`UserManagement`** (`UserManagement.tsx`): form crea-utente (username/password/select ruolo
  editor·admin) + tabella utenti con badge ruolo colorato (admin viola, editor blu), data creazione, elimina
  con `ConfirmDialog`. È l'unico pannello *nato* in C12. Pulito, tabellare, senza fronzoli.
- **Degradazione:** `loadData` (`:90-111`) avvolge speaker e feed-config in `try/catch` con `console.error` →
  se un caricamento fallisce gli altri pannelli restano usabili (resilienza per-pannello, simile nello spirito
  al fallback-graceful di SPW ma senza i contatori da proteggere).

## 6. Differenze rispetto agli altri siti

Il confronto con **SPW-C12** è il cuore della card e va letto come *"tutto ciò che SPW ha in più"*.

| Aspetto | SimonePizziWebSite (SPW-C12) | SitoRuntime (questa card) |
|---|---|---|
| **Geografia backend** | **4 file dedicati** (`stats`/`analytics`/`settings`/`backup`.php) + `optimize_db` | **tutto in `admin.php`** (mega-router), ma la maggior parte degli `?action=` è di ALTRI cluster |
| **Route guard** | **`adminAuthLoader` UNICO** su `AdminLayout` (una guardia, N rotte figlie) | **guard-COMPONENTE** `Admin.tsx` (`checkAuth` on mount, `if(!user)→<LoginForm>`), 1 rotta `/admin` |
| **Struttura frontend** | `AdminLayout` + sotto-albero di rotte data-driven con loader per-pagina | **un solo componente 596 righe** con `section`-switcher in-memory (no router, no `<Outlet/>`) |
| **Statistiche/contatori** | `stats.php` (7 card "cifre tonde", fallback-0) | **ASSENTI** (nessun endpoint, nessun numero in dashboard) |
| **Analytics/tracking** | `analytics.php` doppia-personalità (POST tracking pubblico / GET ~20 aggregazioni) | **ASSENTI** (niente view/click, niente report) |
| **Grafici** | 6 pannelli Chart.js + selettore periodo 7/30/90 + degradazione graziosa | **NESSUN grafico** |
| **Impostazioni** | `app_settings` chiave/valore auto-scaffolded + cambio password | **SOLO cambio password** (nessuna tabella settings) |
| **`session_version` su cambio pw** | **SÌ** (invalida le altre sessioni, server-side) | **NO** (nessuna colonna; logout forzato lato client) + nessun min-length server |
| **Backup / export / cron** | backup auto FUORI docroot + `random_bytes`+`chmod 0600`+rotazione + pseudo-cron `hash_equals` | **NIENTE** (nessun backup, export o cron) |
| **Gestione utenti** | (utente singolo proprietario) | **pannello utenti a ruoli** admin/editor (create/list/delete, "prevent suicide") — più ricco qui |
| **Manutenzione DB** | `optimize_db.php` (ADD INDEX idempotente, gated) | azioni GET in `admin.php` (webp/migrazioni/fix paths) senza UI, gated `isLoggedIn` ma non `isAdmin` |
| **Aggregazione UI** | sidebar + rotte separate | `Admin.tsx` **aggrega** tutti i pannelli dei cluster in 8 sezioni-card |

Sintesi: dove SPW-C12 è *"quattro file, dashboard analitica a 3 densità, 6 grafici, backup fuori-docroot,
settings chiave/valore"*, SR-C12 è *"un mega-router che è quasi tutto altri-cluster, un componente-aggregatore
senza dati, zero analytics, zero backup"*. **SR fa la scelta opposta a SPW su quasi ogni asse di C12**: meno
osservabilità, meno automazione, meno superfici — ma con un **pannello utenti** che SPW non ha (SPW è
single-owner). Il paradosso da incorniciare: il flagship della scalabilità/incidenti ha l'admin **meno
attrezzato** a osservare e a proteggere il sistema.

Per **DISINTELLIGENZA/FDCA** (festival) la ROADMAP prevede `DIS-C12`: lì la dashboard sarà centrata su
voti/partecipanti (`reset_votes`, `stats` master-switch) — un terzo modello ancora diverso da mappare.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **La dashboard che non misura niente** (SR senza analytics/stats/charts vs il cruscotto di SPW) | Box "quanto puoi togliere a una dashboard" — **gemello** del framing upload di SR-C5 |
| **Guard-COMPONENTE vs route-guard** (`Admin.tsx checkAuth` vs `adminAuthLoader` su `AdminLayout`) | Cap. Auth/Frontend "dove vive la guardia: nel componente o nella rotta" — confronto diretto |
| **Un componente, otto pannelli** (`Admin.tsx` aggregatore, section-switcher in-memory) | Cap. Frontend "la SPA dentro la SPA: quando NON usare il router" |
| **Il mega-router `admin.php`** (17 `?action=`, tre livelli di gate, quasi tutto di altri cluster) | Cap. "Un file, molte facce" — il caso estremo dell'endpoint-router |
| **Nessun backup nel sito degli incidenti** (cura senza prevenzione) | Box problemi/soluzioni → **ponte C13** "il flagship che non si fa il backup" |
| **`session_version` lato server vs logout forzato lato client** (cambio password) | Cap. Auth/sessioni — intreccio C2, due modi di "buttare fuori dopo il cambio" |
| **Gate ruolo che nasconde il contenuto ma non la card** (editor → pannello vuoto) | Box UX "guardare il contenuto e dimenticare il bottone" |
| **Operazioni potenti senza confine di ruolo né UI** (migrazioni GET dietro `isLoggedIn`) | Cap. Manutenzione "la console nascosta: azioni che non hanno un bottone" |
| **Pannello utenti a ruoli con "prevent suicide"** (admin/editor, no auto-eliminazione) | Cap. "Gestione utenti minima" (SR ce l'ha, SPW no) |

## 8. Note / domande aperte

- **Risposte puntuali al prompt:**
  1. *Esiste `stats`/`analytics`/`settings`/`backup` SEPARATO come in SPW, o tutto in `admin.php?action=`?*
     **Né l'uno né l'altro per gli analytics/backup: NON ESISTONO affatto.** I file separati non ci sono, e
     nemmeno le azioni equivalenti dentro `admin.php`. L'unico C12-proper backend è user-management +
     change-password.
  2. *C'è tracking analytics (view/click)?* **No.** Nessun endpoint, nessuna tabella, nessun client.
  3. *Backup del DB? Export?* **No.** Assenti del tutto (vs il backup fuori-docroot di SPW).
  4. *Impostazioni sito chiave/valore?* **No `app_settings`.** Le "Impostazioni" sono solo il cambio password.
  5. *Cambio password admin?* **Sì** (`admin.php:151`), meccanica C2; qui mappata come UX del pannello +
     logout forzato client (`Admin.tsx:174`). Senza `session_version`, senza min-length server.
  6. *Pseudo-cron / manutenzione schedulata?* **No cron.** Solo azioni GET di manutenzione lanciate a mano
     (webp/migrazioni/fix), senza scheduling e senza UI.
- **Quali `?action=` di `admin.php` sono PROPRI di C12 vs puntatori:**
  - **C12 (propri):** `list_users`/`create_user`/`delete_user` (pannello utenti) + `change_password` come UX
    del pannello "Impostazioni".
  - **Puntatori:** `login`/`logout`/`check_auth` + meccanica password/CSRF/rate-limit → **C2**;
    `list`/`get`/`save`/`delete` news → **C4**; `optimize_webp`/`fix_image_paths` + helper `adminImageToWebP`
    → **C5**; `apply_v291_status`/`apply_v293_newsletter` → **C13**; `test_smtp` → **C9/diagnostica** (qui
    confermo: vive nell'hub admin, è uno strumento operativo, non un endpoint di prodotto).
- **`Admin.tsx` come aggregatore:** monta `ArticleEditor`(C4/C6), `SpeakerEditor`/`PodcastManager`/
  `MediaGallery`(C4/C5), `NewsletterComposer`(C9), `UserManagement`(C12/C2) e il box Feed Telegram(C8). La
  card descrive il **telaio** e i due pannelli propri; i pannelli figli sono mappati nei rispettivi cluster.
- **Feed Telegram (sezione `feeds`):** chiude il filo frontend del `feed_config.php` di SR-C8 (URL "privato"
  che è in realtà pubblico). Qui solo UX (copia-link + avviso); la diagnosi di sicurezza è in SR-C8.
- **Versione di riferimento:** sito **2.9.13**. Nessuna versione specifica sulle superfici C12 (non ci sono
  banner `[v…]` come in SPW, dove `analytics.php`/`backup.php` erano datati v1.19.0).
- **Resta da mappare (ultima card SitoRuntime):** **SR-C13 — DB Evolution & Incidenti** (MySQL/WAL,
  `emergency_revert_wal.php`, `migrate_to_mysql.php`, `migrate_status.php`, le migrazioni `apply_v291`/
  `apply_v293`, i tre schemi `subscribers` divergenti di C9, l'assenza di backup qui emersa). Alto valore.
