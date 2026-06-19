# Scheda di Sintesi — S1-C12 — Admin Dashboard & Panels

> **Stato:** COMPLETATO
> **Cluster FASE 2:** S1-C12 · **Data:** 2026-06-19 · **Commit:** _(in corso)_
> **Fonti (card di mappatura, in particolare i §6):** SPW-C12, SR-C12, DIS-C12 (+ FDCA-DIFF: frontend riscritto **senza area admin** → fuori scala)
> **Capitoli del libro toccati:** **GAP — manca un capitolo "Admin Dashboard" generale** (CAP 18 è la dashboard *festival*) → proposta di nuovo capitolo in S3 · ponti a CAP 10 (guard/`session_version` → S1-C2/C3), CAP 14 (backup/cron/manutenzione → S1-C13), CAP 18 (dashboard festival → S1-C10), CAP 19 (analytics consumer delle reazioni → S1-C11) → vedi §4

---

## 0. In una frase
La dashboard admin è il **tessuto che lega tutti gli altri cluster** (contenuti, media, newsletter,
reazioni, festival diventano qui numeri e azioni), e i tre siti la realizzano su **due assi ortogonali
e indipendenti**: *quanto misura* (SPW misura con Chart.js / SR **non misura niente** = console CRUD /
DIS misura ma **testuale**) e *come è costruita* (route-guard con loader SPW / mega-componente unico SR /
`AdminLayout` + guard-componente DIS). Il ribaltamento cross-edizione più forte — gemello di S1-C2/C5/C9
— è che **il flagship della scalabilità e degli incidenti (SR) ha l'admin meno attrezzato**: né
metriche né backup, cioè né l'occhio per *vedere* i problemi né la rete per *sopravvivere* ad essi.

## 1. Il pattern comune — la filosofia "thin stack" su questa lente

Sotto le differenze, le tre aree admin condividono quattro tratti.

**1) L'admin è un aggregatore, non un'applicazione a sé.** Nessuno dei tre ha una "app admin" separata:
la console **monta i pannelli degli altri cluster** (editor articoli di C4/C6, media di C5, compositore
newsletter di C9, gestione festival di C10) dentro un telaio comune. C12 è il *telaio* + le poche
superfici proprie (impostazioni, gestione utenti, dashboard).

**2) Una guardia copre l'intera area (non per-pagina come il backend).** Dove ogni endpoint PHP chiama
`Auth::check`/`isLoggedIn` per conto suo, il frontend protegge **tutta** l'area riservata con **un solo**
punto di controllo — loader o componente. È il principio "una guardia, N pagine", già aperto in S1-C3 e
qui portato a compimento (con la divergenza loader-vs-componente del §2).

**3) Degradazione graziosa per-pannello.** Se una fonte dati cade (analytics assente, feed-config in
errore, tabella non migrata), il pannello interessato si nasconde o mostra zero, ma **il resto della
console resta usabile**: `try/catch` con fallback-0 (SPW `stats.php`), `console.error` e prosegui (SR/DIS
`loadData`). La dashboard non è mai una pagina bianca.

**4) Cambio password come voce del pannello "Impostazioni".** Tutti e tre espongono il cambio password
admin dentro le impostazioni (meccanica già in S1-C2); è spesso l'**unica** voce davvero "di
configurazione" presente, perché le impostazioni-sito chiave/valore esistono solo in SPW.

Su questa base condivisa, i due assi — *misurare* e *strutturare* — separano nettamente i tre siti.

## 2. Le varianti per sito (tabella unica, deduplicata)

| Asse | SimonePizziWebSite | SitoRuntime | DISINTELLIGENZA | *(FDCA)* |
|---|---|---|---|---|
| **Geografia backend** | **4 file** (`stats`/`analytics`/`settings`/`backup`) + `optimize_db` | **tutto in `admin.php`** (mega-router 17 `?action=`, quasi tutto altri-cluster) | sparso (stats/settings=C10, users=C2, send=C9) | — (no admin) |
| **Struttura frontend** | `AdminLayout` + sotto-albero di rotte **data-driven** (loader per pagina) | **un solo componente** `Admin.tsx` (596 righe, section-switcher in-memory) | `AdminLayout` + rotte figlie via `Outlet` | — |
| **Guard** | **`adminAuthLoader`** (loader → redirect) | **componente** `checkAuth` on mount → `<LoginForm>` | **componente** `checkAuth` on mount → `navigate(login)` (su `createBrowserRouter`, loader non usati) | — |
| **Controllo ruolo nel guard** | sì | parziale (contenuto sì, card no) | **NO** (role-blind: editor vede tutta la console) | — |
| **La dashboard MISURA?** | **sì** — 7 card + 10 mini-stat + **6 grafici Chart.js** + periodo 7/30/90 | **no** — zero contatori/grafici (card = navigazione) | **sì ma TESTUALE** — contatori + storage breakdown + classifica, no grafici | — |
| **Fonte metriche** | `analytics.php` (tracking view/click first-party) + `stats.php` | nessuna | `stats.php` (conteggi; eredita bug fuso + drift `vote_count` di S1-C10) | — |
| **Impostazioni store** | `app_settings` chiave/valore (mass-write, no whitelist) | **nessuno** (solo cambio password) | `settings` = master switch festival (UPSERT) | — |
| **`session_version` su cambio pw** | **sì** (server, invalida le altre sessioni) + min-len 12 | **no** (logout forzato client `setTimeout`) + nessun min-len | (cambio pw via C2) | — |
| **Backup / export / cron** | **backup auto FUORI docroot** + `random_bytes`+`chmod 0600`+rotazione + pseudo-cron `hash_equals` | **NIENTE** | **niente in UI** (backup auto pre-reset lato server, S1-C2) | — |
| **Gestione utenti** | — (single-owner) | **pannello a ruoli** admin/editor (+ "prevent suicide") | `UserList` (orfana: rotta senza voce in sidebar) | — |
| **Inbox messaggi** | `messages` **letti** in admin (S1-C11) | — | **`contacts` MAI letti** (tabella write-only) | — |
| **Manutenzione** | `optimize_db.php` (ADD INDEX idempotente, gated) | azioni GET in `admin.php` (webp/migrazioni) **senza UI**, gated `isLoggedIn` non `isAdmin` | reset via `fetch` POST senza CSRF (doppio `confirm` UX) | — |

**Lettura della tabella.** I due assi sono **indipendenti**: SPW è alto su entrambi (misura molto +
struttura data-driven), SR è basso su entrambi (non misura + mega-componente), DIS è la **via di mezzo**
(misura testuale + struttura SPW-like ma guard SR-like). Lo spettro del *misurare* va da "cruscotto
analitico con 6 grafici" (SPW) a "menu travestito da dashboard" (SR), con DIS che dimostra il **gradino
utile intermedio**: numeri veri senza l'apparato Chart.js/analytics. Lo spettro dello *strutturare* è la
scala già aperta in S1-C3 (loader dichiarativo → guard imperativo). Il punto cross-sito più forte resta
il **paradosso di SR**: il sito mappato *per* gli incidenti (S1-C13) non ha né le metriche per accorgersi
di un problema né il backup per rimediarvi — ha la *cura* (revert d'emergenza) ma non la *prevenzione*.

**FDCA è fuori scala:** il fork ha riscritto il frontend come **vetrina senza area admin** (nessun
`AdminLayout`, nessuna rotta `/admin`, nessun `api.ts`) → il backend admin di DIS resta nel repo ma
**irraggiungibile**. Caso fork "spento".

## 3. GOLD & box problemi-soluzioni

- **Tre modelli di dashboard sullo stesso problema** — *(SPW vs SR vs DIS)* — il GOLD portante. Stessa
  esigenza ("dare all'admin una vista del sistema"), tre risposte: **cruscotto analitico** (SPW: tracking
  first-party + 6 grafici + periodo selezionabile), **console CRUD** che non misura nulla (SR: 8 card di
  sola navigazione — "menu travestito da dashboard"), **cruscotto testuale** (DIS: contatori e classifica
  reali senza grafici). DIS è la lezione più utile: *si può misurare con valore anche senza Chart.js né un
  motore analytics* — bastano i `COUNT` giusti. → Box "Tre dashboard: analitica, console, testuale —
  quanto cruscotto ti serve davvero" (alto valore; gemello del framing upload di S1-C5).

- **Il flagship degli incidenti senza rete di salvataggio** — *(SR; ponte S1-C13)* — SR non ha
  **nessun** backup, export o cron, e **nessuna** metrica. SPW invece ha il pattern d'oro: backup
  automatico **fuori dalla document root** (`../db_backups_*`), con fallback dentro la docroot protetto da
  un `.htaccess Require all denied` **ricreato a runtime** — perché `clean-dist.js` (postbuild) **strippa
  `.data/` dalla dist**, quindi il deny committato nel repo non arriva mai sul server; più nome con
  `random_bytes`, `chmod 0600`, rotazione 15, pseudo-cron gated admin-OR-secret `hash_equals` (fail-closed).
  Il contrasto dà senso a S1-C13: gli incidenti di SR fanno più male perché manca tutto questo. → Box "Il
  build può tradire la tua difesa statica: difenditi a runtime" + Box "Cura senza prevenzione: il sito che
  non si fa il backup" (entrambi alto valore; ponte S1-C13).

- **La tabella write-only: dati raccolti e mai mostrati** — *(DIS)* — `contact.php` salva i messaggi in
  `contacts`, ma **nessun pannello né endpoint li legge** (nessuna `ContactsManager`, nessuna
  `getContacts`): l'admin li vede solo nell'email di notifica, la copia in DB è **scrivibile e mai
  consultata**. È il costo nascosto del "salva tutto": persistere senza un consumer significa PII
  accumulata senza scopo (e senza un punto dove cancellarla). → Box "Dati senza consumer: raccogliere e
  dimenticare" (alto valore di prodotto + privacy).

- **La guardia che controlla il login ma non il ruolo** — *(DIS; rimando S1-C2)* — `AdminLayout` verifica
  solo che `checkAuth` ritorni un utente, **non** `role==='admin'`: un **editor** vede l'intera console
  (iscrizioni, voto, reset, utenti) e — per il gate backend incoerente di S1-C2 — può davvero approvare
  partecipanti e cambiare round dalla UI. È la versione DIS, estesa all'intera area, del "il gate nasconde
  il contenuto ma non la card" di SR (dove l'editor clicca "Utenti" e ottiene un **pannello vuoto**). →
  Box "Proteggere l'area non basta: serve il ruolo" (ponte S1-C2).

- **Due modi di buttare fuori dopo il cambio password** — *(SPW vs SR; rimando S1-C2)* — stessa esigenza
  ("dopo il cambio password, invalida le sessioni"), due implementazioni: SPW fa `session_version + 1`
  **lato server** (invalida le *altre* sessioni, tiene la corrente) e impone min-len 12; SR non ha la
  colonna e compensa **lato client** con `setTimeout(handleLogout, 1500)` — che slogga solo *questa*
  sessione e non tocca eventuali altre aperte altrove, senza min-len server. → confluisce nel box
  sessioni di S1-C2 (qui il sintomo lato pannello).

- **La console nascosta: azioni potenti senza un bottone** — *(SR)* — `optimize_webp`, `apply_v291_status`
  (un `ALTER TABLE`), `apply_v293_newsletter`, `fix_image_paths` sono azioni **GET** dentro `admin.php`,
  gated `isLoggedIn` ma **non** `isAdmin` e **senza** CSRF (sono GET): si lanciano **digitando l'URL**, e
  **nessun pannello le invoca**. Chi non conosce gli `?action=` non sa che esistono. È manutenzione "a
  mano" senza UI né confine di ruolo — la meccanica DB di queste azioni è S1-C13, qui il punto è che
  vivono nell'hub admin **invisibili**. → Box "La console nascosta: operazioni senza interfaccia"
  (ponte S1-C13).

- **Il `confirm()` non è una difesa di sicurezza** — *(DIS; rimando S1-C2)* — i reset distruttivi partono
  da `fetch('/api/reset_*.php', POST)` **senza token CSRF**; la "protezione" è il doppio `window.confirm`
  (puro UX) + il gate admin backend. Un `confirm` riduce l'errore umano, **non** ferma una richiesta
  cross-site forgiata. → confluisce nel box "reset-a-un-clic" di S1-C2.

- **`app_settings` mass-write + la casa mancante dei settings** — *(SPW; ponte S1-C8)* — il POST di
  `settings.php` fa `foreach($data as $k=>$v) INSERT … ON DUPLICATE KEY UPDATE` **senza whitelist** delle
  chiavi: un admin può scrivere qualunque `setting_key`. Rischio basso (è gated), ma è anche il punto dove
  *dovrebbero* vivere i "TODO settings" del feed RSS (S1-C8, titolo/descrizione hardcoded) — infrastruttura
  pronta, mai usata per contenuto/SEO. → Box "Configurazione runtime nel DB: l'infrastruttura che nessuno
  popola" (ponte S1-C8).

## 4. Mappa → capitolo/i del libro

| Materiale della scheda | Capitolo | Azione |
|---|---|---|
| **L'intera scheda** (i tre modelli + architettura + backup + utenti) | **— (nessun capitolo "Admin Dashboard" generale)** | **PROPONI NUOVO CAPITOLO** in S3 — vedi nota sul gap |
| **Tre modelli di dashboard** (analitica/console/testuale) | nuovo CAP "Admin Dashboard" | **sezione centrale** |
| **Tre architetture** (loader / mega-componente / AdminLayout+guard) | nuovo CAP + **CAP 10/ponte S1-C3** | **sezione**: una guardia, N pagine; loader vs componente |
| **Backup fuori-docroot + `.htaccess` runtime** | nuovo CAP + **CAP 14** | **box GOLD** (ponte S1-C13) |
| **Cura senza prevenzione** (SR senza backup né metriche) | nuovo CAP + **CAP 14** | **box** (ponte S1-C13) |
| **Tabella write-only** (`contacts` DIS) | nuovo CAP | **box** (prodotto + privacy) |
| **Guard role-blind** (DIS) | nuovo CAP + **CAP 10** | **box** (ponte S1-C2) |
| **`session_version` server vs logout client** | **CAP 10** | **rimanda a S1-C2** (qui il sintomo) |
| **Analytics first-party** (view dedup, click rate-limited, consumer reazioni) | nuovo CAP + **CAP 19** | **sezione** "misurare senza terze parti" (ponte S1-C11) |
| **Console nascosta** (manutenzione GET senza UI) | nuovo CAP + **CAP 14** | **box** (ponte S1-C13) |

**Correzioni / note sul testo attuale:**
- **GAP STRUTTURALE: non esiste un capitolo "Admin Dashboard" generale.** Nei 19 capitoli attuali l'unica
  "dashboard" trattata è **CAP 18 (Festival — Dashboard, Settings & Reporting)**, che è specifica del
  modulo concorso (S1-C10) e descrive `settings`/KPI festival, non la dashboard editoriale. Il materiale
  di C12 (i tre modelli, l'architettura del pannello, backup/manutenzione, analytics first-party,
  gestione utenti) **non ha un capitolo dove andare**. → da proporre in **S3** un nuovo capitolo "Admin
  Dashboard & Panels" distinto dal CAP 18 festival, con CAP 18 che ne diventa il caso-festival.
- **CAP 18 va riletto come *istanza* del pattern generale.** Una volta creato il capitolo Admin generale,
  CAP 18 (dashboard festival) ne è la specializzazione: evitare che i due si sovrappongano (il master
  switch e i KPI festival restano in CAP 18, la struttura del pannello/guard/backup va nel nuovo).
- **Materiale già coperto altrove da non duplicare nel nuovo capitolo:** il guard loader-vs-componente
  (S1-C3/CAP 6), `session_version`/CSRF/reset-a-un-clic (S1-C2/CAP 10), backup/cron/migrazioni come
  *meccanica DB* (S1-C13/CAP 14), il consumer reazioni→analytics (S1-C11/CAP 19). Il nuovo capitolo deve
  **citare** questi, non re-spiegarli.

## 5. Cosa si scarta / dedup

- **Ripetizioni fuse:** i §6 di SR-C12 e DIS-C12 erano entrambi un confronto "vs SPW"; SPW-C12 era il
  riferimento. Qui la comparazione è scritta **una volta sola** nella tabella del §2, sui due assi
  (*misurare* / *strutturare*) invece che come tre liste separate.
- **Dettaglio per-sito che NON entra nel libro:** numeri di riga, i nomi esatti delle 8 sezioni di
  `Admin.tsx`, le 9 voci di sidebar di DIS, le ~20 aggregazioni di `analytics.php`, i microcopy del
  backstage ("VERIFYING BIOMETRICS…", "Inviata a {n} vittime"), la `disabled` prop morta della
  `DashboardCard` di SR, le stringhe di versione divergenti di DIS (sidebar v0.3.5 / init v0.3.6 /
  package 0.5.x — confluisce nel filo "versione che non si allinea" di S1-C13). Restano nelle card come fonte.
- **Materiale che appartiene ad altre schede (richiamato, non ri-mappato):**
  - **guard loader-vs-componente, Double Read dei loader** → **S1-C3**.
  - **`session_version`, CSRF, reset-a-un-clic, gate role-blind come *meccanica*, IP grezzo** → **S1-C2**.
  - **backup/cron, `optimize_db`, le migrazioni `apply_v291/v293`, i 3 schemi `subscribers`, `clean-dist.js`** → **S1-C13** (qui solo i sintomi lato pannello + il GOLD backup-placement).
  - **analytics come consumer delle reazioni; il pannello messaggi** → **S1-C11**.
  - **i pannelli di dominio** (ArticleEditor, MediaManager, NewsletterComposer, gestione festival/voto) → **S1-C4/C5/C6/C9/C10** (qui solo come *aggregati nel telaio*).
  - **il box Feed Telegram / `feed_config` security-theater** → **S1-C8** (qui solo l'UX copia-link).
