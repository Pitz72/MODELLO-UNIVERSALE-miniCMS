# Mappatura — DISINTELLIGENZA — C12: Admin Dashboard & Panels

> **Stato:** COMPLETATO
> **Sessione:** 27 · **Data:** 2026-06-18 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `DISINTELLIGENZA/`)
> - `src/Routes.tsx` (router: `createBrowserRouter`, area `/admin` con `AdminLayout` + figli)
> - `src/components/admin/AdminLayout.tsx` (guard-componente `checkAuth` on mount + sidebar + chrome)
> - `src/pages/admin/Dashboard.tsx` (cruscotto: metriche reali da `stats.php`)
> - `src/pages/admin/Registrations.tsx` (gestione iscrizioni: approva/rifiuta + audio player)
> - `src/pages/admin/Settings.tsx` (master switch + cambio password + reset turni/edizione)
> - `src/pages/admin/NewsletterManager.tsx` (compositore newsletter)
> - elenco pannelli: `pages/admin/{Dashboard,Login,NewsManager,NewsletterManager,Podcast,Registrations,Settings,TeamManager,UserList,VotingManager,MediaCenter}.tsx`
> - **VERIFICA buco DIS-C9:** grep `contacts` → solo `contact.php` (POST) + `update_db_0_1_3` (schema): **nessun pannello/endpoint legge `contacts`**
> - confronto: `SR-C12-admin.md`, `SPW-C12-admin-dashboard.md`

## 1. Cosa fa (sintesi narrativa)

C12 è il **pannello di amministrazione** di DISINTELLIGENZA. A differenza degli altri cluster, il
**lato server dell'admin è già stato mappato sparso** (stats/settings=DIS-C10, users=DIS-C2,
participants-status/round=DIS-C10, newsletter-send=DIS-C9): questa card è soprattutto il **lato
frontend** — come la SPA React orchestra quegli endpoint in una console.

L'osservazione centrale è che **DIS-C12 è una via di mezzo tra SR-C12 e SPW-C12**, e per certi versi
il pannello **più "finito"** dei tre sul piano UX:

- **Ha un `AdminLayout`** (sidebar a 9 voci + header + `Outlet`) che avvolge **tutte** le rotte figlie
  — come SPW (un layout, N pagine), **non** come il mega-componente unico di SR.
- **Ma il guard è un componente**, non un loader: `AdminLayout` chiama `api.checkAuth()` *on mount* e
  fa `navigate('/admin/login')` se non autenticato (`AdminLayout.tsx:13-22`) — il pattern di **SR**,
  non l'`adminAuthLoader→redirect` di SPW. Curiosità: gira comunque su `createBrowserRouter`
  (l'infrastruttura data-router di SPW), ma **senza usarne i loader**.
- **Soprattutto: la dashboard MISURA.** Dove SR-C12 era "la dashboard che non misura niente" (8 card
  di sola navigazione, zero dati), DIS mostra **metriche reali** prese da `stats.php`: iscritti totali
  (+24h), voti registrati (+stato sessione), storage usato con breakdown per cartella, classifica
  provvisoria/definitiva, ultimi iscritti. Niente grafici Chart.js né analytics/tracking di SPW, ma
  numeri veri — un cruscotto **testuale** che esiste davvero.

I pannelli coprono l'intero festival: News, Newsletter, Media, Iscrizioni (con player audio), Voto,
Podcast, Team, Impostazioni (+ Utenti, raggiungibile per URL ma non in sidebar). Ognuno è una pagina
React che chiama gli endpoint già mappati.

## 2. Pattern miniCMS rilevanti

- **`AdminLayout` + rotte figlie via `Outlet`** (`Routes.tsx:47-64`, `AdminLayout.tsx:84-96`): un
  unico layout con sidebar persistente e area contenuto che cambia. Una guardia copre N pagine (come
  SPW), contro il section-switcher monolitico di SR. La rotta `/admin` index fa
  `Navigate to="/admin/dashboard"` (`Routes.tsx:51`).
- **Guard-componente on-mount** (`AdminLayout.tsx:13-22`): `checkAuth().then(u => !u ? navigate(login)
  : setUser(u))`, con stato `loading` ("VERIFYING BIOMETRICS...") e `if (!user) return null`. È la
  protezione **client-side** dell'intera area: nessun loader, nessun redirect server. Stesso modello
  di SR (`Admin.tsx` checkAuth on mount), ma qui fattorizzato nel layout invece che nel mega-componente.
- **Dashboard a metriche reali** (`Dashboard.tsx:9-15,19-57`): `getStats()` → 3 card contatore +
  2 pannelli (classifica `top_voted`, ultimi iscritti). Degradazione graziosa esplicita (loading,
  `stats.status==='error'`, `participants_count===undefined`). È il consumer di `stats.php` (DIS-C10).
- **Aggiornamento ottimistico dei toggle** (`Settings.tsx:24-29`, `Registrations.tsx:27-31`): i master
  switch (maintenance/registration/voting) aggiornano subito lo stato locale e poi chiamano
  `api.updateSetting(key, value)` → `settings.php` POST (DIS-C10). UX immediata.
- **Re-fetch dopo mutazione** (`Registrations.tsx:33-37`): approva/rifiuta → `updateParticipantStatus`
  → `getParticipants()` di nuovo. Niente update ottimistico qui (lo stato cambia colonna/bordo via
  `data-status`), si ricarica la lista. Semplice e corretto.
- **Compositore newsletter con selezione articoli** (`NewsletterManager.tsx:26-66`): legge le news
  (`getNews(1,50)`, con guardia `Array.isArray` sulla "busta zero" di DIS-C4), permette di
  selezionarle e comporre subject/intro, poi `sendNewsletter({intro,subject,articles})` →
  `newsletter.php?send` (DIS-C9). Mostra il conteggio iscritti da `getNewsletterStats`.
- **Conferme client-side su azioni distruttive** (`Settings.tsx:136-164`): reset voti = un `confirm`;
  reset edizione = **doppio `confirm`** con elenco dettagliato di cosa viene cancellato/preservato. La
  rete di sicurezza è **solo lato client** (`window.confirm`), il backend ha il suo `confirm_reset`
  (DIS-C2). Le `fetch('/api/reset_*.php', {method:'POST'})` partono **senza token CSRF** (conferma
  DIS-C2).
- **Player audio inline per la valutazione** (`Registrations.tsx:39-56,149-170`): l'admin ascolta e
  scarica la traccia del partecipante (`p.audio_file`, l'upload pubblico di DIS-C5) direttamente dalla
  card — UX di giuria.
- **Brand voice nei microcopy admin**: "VERIFYING BIOMETRICS...", "DISCONNECT", "Inviata a {n}
  vittime.", "Nessuna iscrizione ricevuta. Il mondo è salvo, per ora.", "Nessuno. Tristezza." Il tono
  del festival permea anche il backstage.

## 3. Codice chiave (stralci con origine)

**Guard-componente che protegge tutta l'area admin** — `AdminLayout.tsx:13-25`:

```tsx
useEffect(() => {
    api.checkAuth().then(u => {
        if (!u) { navigate('/admin/login'); }     // protezione CLIENT-side (no loader, no redirect server)
        else { setUser(u); }
        setLoading(false);
    });
}, [navigate]);
if (loading) return <div ...>VERIFYING BIOMETRICS...</div>;
if (!user) return null;                            // NB: nessun controllo role==admin (vedi §4)
```

**Router: AdminLayout come parent di tutte le rotte admin (un guard, N pagine)** — `Routes.tsx:47-64`:

```tsx
{ path: '/admin', element: <AdminLayout />, children: [
    { index: true, element: <Navigate to="/admin/dashboard" replace /> },
    { path: 'dashboard', element: <Dashboard /> },
    { path: 'users', element: <UserList /> },          // raggiungibile per URL ma NON in sidebar (§4)
    { path: 'registrations', element: <Registrations /> },
    { path: 'voting', element: <VotingManager /> },
    { path: 'settings', element: <Settings /> },
    // ... news, podcast, media, team, newsletter
]}
```

**Dashboard che MISURA (≠ SR): metriche reali da stats.php** — `Dashboard.tsx:19-37,61-73`:

```tsx
<CardTitle>ISCRITTI TOTALI</CardTitle>
<div className="text-4xl ...">{stats.participants_count}</div>
<p>+{stats.participants_new} nelle ultime 24h</p>          // (bug fuso: stats.php usa date() PHP, DIS-C10)
// ...
<CardTitle>VOTI REGISTRATI</CardTitle>
<div>{stats.votes_count}</div> <p>Sessione: {stats.voting_active ? 'APERTA' : 'CHIUSA'}</p>
// ...classifica dal vote_count denormalizzato (DIS-C10):
{stats.top_voted.map((p,i) => <li>#{i+1} {p.stage_name} — {p.vote_count} voti</li>)}
```

**Azioni distruttive: doppio confirm CLIENT + fetch senza CSRF** — `Settings.tsx:155-163`:

```tsx
onClick={async () => {
    if (confirm('⚠️ ATTENZIONE: RESET EDIZIONE ... cancellerà TUTTI i partecipanti/voti/audio ...')) {
        if (confirm('ULTIMA CONFERMA: I dati ... saranno persi per sempre. Procedere?')) {
            const res = await fetch('/api/reset_system.php', { method: 'POST',
                          body: new URLSearchParams({ action: 'confirm_reset' }) });  // NESSUN CSRF
            alert((await res.json()).message); window.location.reload();
        }
    }
}}
```

**Gestione iscrizioni: approva/rifiuta + audio player di giuria** — `Registrations.tsx:33-37,153`:

```tsx
const handleStatusChange = async (id, status) => {
    await api.updateParticipantStatus(id, status);   // participants.php?update_status (DIS-C10)
    setParticipants(await api.getParticipants());     // re-fetch
};
// ...
<Button onClick={() => togglePlay(p.audio_file, p.id)}>▶</Button>   // ascolta la traccia (DIS-C5)
```

## 4. Problemi riscontrati & soluzioni

- **GOLD — i `contacts` sono raccolti ma MAI letti (tabella write-only).** Verificato (chiude il filo
  DIS-C9): `contact.php` è **solo POST** (salva + email all'admin) e **nessun** pannello admin né
  endpoint legge la tabella `contacts`. Non esiste una `ContactsManager.tsx`, non c'è una `getContacts`
  in `api.ts`. L'unico modo in cui l'admin "vede" un messaggio è la **email di notifica**; la copia in
  DB è **scrivibile e mai consultata** dall'applicazione. → Box "la tabella write-only: dati raccolti e
  mai mostrati" (alto valore — il costo nascosto di salvare senza un consumer).
- **GOLD — guard ROLE-BLIND: l'intera area admin è aperta a qualunque utente loggato.** `AdminLayout`
  verifica solo che `checkAuth` ritorni un utente (`AdminLayout.tsx:15`), **non** che
  `role === 'admin'`. Quindi un **editor** vede tutta la console (iscrizioni, voto, reset, utenti…);
  è il **backend** a respingere, ma in modo **incoerente** (DIS-C2: `settings`/`reset_*`/`users` sono
  admin-only, ma `participants.php?update_status/update_round` accettano qualsiasi loggato). Risultato:
  un editor può **approvare/respingere partecipanti e cambiare i round** dalla UI senza essere admin.
  È la versione DIS del "il gate nasconde il contenuto, non la card" di SR-C12, qui estesa all'**intera
  area**. → Box "una guardia che controlla il login ma non il ruolo" (ponte DIS-C2).
- **GOLD — azioni distruttive via `fetch` diretto senza CSRF.** I reset (`Settings.tsx:138,158`)
  chiamano `/api/reset_votes.php` e `/api/reset_system.php` con `fetch` POST **nudo**, senza token
  (DIS non ha CSRF, DIS-C2). La protezione è il doppio `window.confirm` (solo UX) + il gate admin
  backend + il `confirm_reset`. Manca la difesa CSRF: una pagina malevola potrebbe innescare il reset
  sull'admin loggato. → consolidare con DIS-C2 (catastrofe a un clic).
- **Dashboard eredita i difetti di `stats.php`.** I "nuovi iscritti 24h" usano il confronto sfasato
  PHP-tz↔UTC (DIS-C10), e la classifica legge il **`vote_count` denormalizzato** (DIS-C10): se il
  contatore drifta, la dashboard mostra una classifica sbagliata **con la massima autorevolezza** (è
  "la" classifica definitiva, `Dashboard.tsx:61`). Il pannello eredita i rischi del dato. → nota
  (ponte DIS-C10).
- **`UserList` orfana nella navigazione.** La rotta `/admin/users` esiste (`Routes.tsx:53`) ma **non**
  è tra le 9 voci della sidebar (`AdminLayout.tsx:27-37`): la gestione utenti è raggiungibile solo
  digitando l'URL. Funziona, ma è una pagina "nascosta" non scopribile dalla UI. → nota.
- **Versione hardcoded stantia nel pannello.** `AdminLayout.tsx:45` mostra "v0.3.5" in sidebar, mentre
  `package.json` è 0.5.x (e `init_db.php` dichiarava "v0.3.6", DIS-C1): **terza** stringa di versione
  divergente nel sito. Stringhe di versione sparse e mai allineate. → nota (ricorrente cross-card).
- **Conferme e reset solo client-side per le edizioni/turni.** La distinzione turno/edizione vive
  nella UI (`Settings.tsx:130-170`, "GESTIONE TURNI & EDIZIONI"); il backend (`reset_votes`/
  `reset_system`) non sa nulla di "edizione" — è solo la UI a dare significato narrativo alle due
  operazioni. Coerente, ma la semantica del dominio è **nel frontend**, non nei dati (nessuna tabella
  `editions`/`rounds`, ponte DIS-C10 "round manuali").
- **Nessun backup/export/analytics dal pannello.** A differenza di SPW-C12 (backup ZIP fuori docroot,
  pseudo-cron, analytics tracking, export), DIS non ha nulla di tutto questo in UI; il backup esiste
  ma è **automatico e lato server** prima dei reset (DIS-C2), non un'azione admin esplicita. → §6.

## 5. Estetica / UX (moderna ma funzionale)

- **Console "terminale" coerente** (`AdminLayout`): sidebar nera, accenti verde-`dis-green`,
  font mono, microcopy da sistema ("DIS.ADMIN", "VERIFYING BIOMETRICS...", "DISCONNECT", "VIEW SITE
  ↗"). L'estetica admin è curata e on-brand quanto il sito pubblico.
- **Dashboard leggibile a colpo d'occhio**: tre contatori grandi con bordo colorato per categoria
  (verde/viola/blu), storage breakdown in mono, classifica numerata. Densità informativa giusta senza
  grafici — "misura ma non sovraccarica".
- **Player audio di giuria** (`Registrations.tsx`): ascolto/anteprima e download della traccia
  direttamente nella card del partecipante, con stato play/pause per riga. UX pensata per il compito
  reale (valutare le candidature).
- **Feedback d'invio newsletter** con stati `idle/sending/success/error` e messaggio ("Inviata a {n}
  vittime."), bottone disabilitato durante l'invio (`NewsletterManager.tsx:48-66,109-121`).
- **Reset con narrazione chiara** (`Settings.tsx`): i due `confirm` spiegano in dettaglio cosa viene
  cancellato e cosa preservato — riducono il rischio di errore su azioni irreversibili.
- **Bypass manutenzione documentato in UI** (`Settings.tsx:64`): link `/?preview=true` per vedere il
  sito anche con la manutenzione attiva — piccola cortesia operativa per l'admin.

## 6. Differenze rispetto agli altri siti

Confronto a **TRE**: DIS-C12 vs SR-C12 e SPW-C12.

| Aspetto | SimonePizziWebSite (SPW-C12) | SitoRuntime (SR-C12) | **DISINTELLIGENZA (questa card)** |
|---|---|---|---|
| **Layout admin** | `AdminLayout` + rotte figlie | mega-componente `Admin.tsx` unico | **`AdminLayout` + rotte figlie** (come SPW) |
| **Guard** | `adminAuthLoader` (loader→redirect) | componente `checkAuth` on mount | **componente `checkAuth` on mount** (come SR) su `createBrowserRouter` |
| **Controllo ruolo nel guard** | sì (loader) | parziale | **NO** (solo login; role-blind) |
| **Dashboard** | cruscotto 3 livelli + **Chart.js** + period selector | **zero metriche** (navigazione) | **metriche reali testuali** (no grafici) — via di mezzo |
| **Fonte metriche** | `analytics.php` (tracking views/click) | nessuna | **`stats.php`** (conteggi + storage breakdown) |
| **Analytics/tracking** | sì (motore dedicato) | no | **no** |
| **Backup/export** | ZIP fuori docroot + pseudo-cron | **assente** | **assente in UI** (backup auto pre-reset lato server, DIS-C2) |
| **Settings store** | `app_settings` chiavi arbitrarie | nessuno | **`settings` = master switch festival** (UPSERT) |
| **Pannelli di dominio** | contenuti/media/newsletter | contenuti/speaker/podcast/newsletter | **+ festival**: iscrizioni (audio player), voto, reset turni/edizione |
| **Azioni distruttive** | gated + secret timing-safe | — | doppio `confirm` client + gate admin, **niente CSRF** |
| **Inbox messaggi** | `messages` letti in admin (SPW-C11) | — | **`contacts` MAI letti** (write-only) — GOLD |

**Sintesi.** DIS-C12 si colloca **tra** i due flagship: ha la **struttura** di SPW (AdminLayout +
rotte figlie + sidebar) ma il **guard** di SR (componente on-mount), e una dashboard che — grazie a
`stats.php` — **misura davvero** (cosa che mancava del tutto a SR) pur restando testuale (niente
Chart.js/analytics/backup di SPW). I suoi tratti distintivi sono i **pannelli di dominio del
festival** (valutazione candidature con player audio, gestione turni/edizioni, master switch) che
nessun altro sito ha. I due nei più rilevanti sono di **sicurezza** e li eredita da DIS-C2: il guard
**role-blind** (l'intera console aperta agli editor) e le azioni distruttive **senza CSRF**. Più un
difetto di **prodotto**: la tabella `contacts` raccolta e **mai mostrata**. Con questa card
**DISINTELLIGENZA è COMPLETO** (7 card: C1, C2, C4, C5, C9, C10, C12).

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **Tre modi di fare un admin**: mega-componente (SR) / AdminLayout+loader (SPW) / AdminLayout+guard-componente (DIS) | Cap. "L'area admin di una SPA": la scala completa (alto valore) |
| **La dashboard che misura senza grafici** (stats.php → contatori testuali) | Box "misurare senza Chart.js: il cruscotto minimo utile" (contrappunto a SR-C12) |
| **Guard role-blind**: login sì, ruolo no | Box sicurezza "proteggere l'area non basta: serve il ruolo" (ponte DIS-C2) |
| **La tabella write-only** (`contacts` raccolti e mai letti) | Box "dati senza consumer: raccogliere e dimenticare" (alto valore di prodotto) |
| **Azioni distruttive in UI**: doppio confirm client vs CSRF backend | Box "il confirm non è una difesa di sicurezza" (ponte DIS-C2/SR-C13) |
| **Pannello di giuria** (player audio + approva/rifiuta) | Box "UI pensata per il compito reale" |
| **Master switch come pannello** (toggle ottimistici → settings UPSERT) | Box "feature flag con un interruttore" (ponte DIS-C10) |
| **Stringhe di versione divergenti** (sidebar v0.3.5 / init v0.3.6 / package 0.5.x) | confluisce nel box "la versione che non si allinea mai" |

## 8. Note / domande aperte

- **Puntatori ad altri cluster** (annotati qui, NON mappati in questa card):
  - **Logica festival** (stati, round, classifica, master switch come *meccanica*) → **C10** (già
    mappato): C12 ne è la *presentazione*. Il `vote_count` denormalizzato e il bug fuso di `stats.php`
    si ripercuotono sulla dashboard.
  - **Auth/ruoli/CSRF** → **C2** (già mappato): il guard role-blind e le fetch senza CSRF sono la
    ricaduta UI delle scelte di C2.
  - **Newsletter/email** (compositore, conteggio iscritti) → **C9** (già mappato): `NewsletterManager`
    è il front di `newsletter.php?send`.
  - **News/Media/Podcast/Team manager** (`NewsManager`, `MediaCenter`, `Podcast`, `TeamManager`) →
    contenuti **C4** / media **C5**: pannelli CRUD che consumano quegli endpoint; qui solo elencati
    come parte della console (non ri-mappati nel dettaglio, logica già in C4/C5).
  - **`Login.tsx`** → front di `auth.php?login` (**C2**).
  - **`api.ts`** (metodi `getStats`/`getParticipants`/`updateParticipantStatus`/`updateSetting`/
    `getNewsletterStats`/`sendNewsletter`/`checkAuth`/`logout`) → il bridge client, dominio **C3** (non
    mappato come card a sé per DIS; qui osservato come superficie consumata dai pannelli).
- **Da verificare in FDCA-DIFF:** se il fork cambia i pannelli admin (es. aggiunge la lettura dei
  `contacts`, o un ruolo-check nel guard, o grafici).
- **Conferma cross-card:** la dashboard consuma `stats.php` (DIS-C10) e i toggle scrivono `settings`
  via UPSERT (DIS-C10); i reset chiamano `reset_*.php` (DIS-C2). C12 è il tessuto che lega C2/C9/C10.
- Versione del sito al momento della mappatura: **0.5.x** (`package.json`); sidebar admin dichiara
  ancora "v0.3.5".
