# Scheda di Sintesi — S1-C3 — Frontend Bridge & State

> **Stato:** COMPLETATO
> **Cluster FASE 2:** S1-C3 · **Data:** 2026-06-19 · **Commit:** _(in corso)_
> **Fonti (card di mappatura, in particolare i §6):** SPW-C3, SR-C3, DIS-C3 (+ FDCA-DIFF: frontend riscritto/scollegato, **nessun `api.ts`** → fuori scala)
> **Capitoli del libro toccati:** CAP 6 (Frontend Bridge / API.ts) — principale · ponti a CAP 10 (Security, CSRF-client + guard), CAP 9 (Content Lifecycle, loader/contratti lista), CAP 4 (Frontend Dependencies) → vedi §4

---

## 0. In una frase
Tutti e tre i siti parlano col backend PHP attraverso **un solo oggetto `api` di wrapper su `fetch`**
— niente Axios, niente React Query, niente Redux — ma il ponte è cresciuto in modo disuguale attorno
a un problema comune: **un'API il cui contratto non è uniforme**. La lezione del capitolo è leggere
le tre risposte a quel problema come una scala di *investimento*: SPW investe nello **state layer**
(loader react-router + "Double Read"), SR nel **token CSRF lato client** (una variabile di modulo),
DIS in un **codemod** che rattoppa il client a posteriori. Tre modi di tenere insieme React e PHP
quando nessuno dei due lati ha un contratto stabile.

## 1. Il pattern comune — la filosofia "thin stack" su questa lente

Sotto le tre implementazioni, il ponte client↔server è **lo stesso oggetto**, e cinque tratti lo
definiscono.

**1) Un solo modulo client, oggetto-namespace su `fetch`.** Ogni sito esporta un singolo
`export const api = { … }` con un metodo per azione (`login`, `getNews`, `uploadImage`,
`submitVote`…), raggruppati per dominio con dei commenti. Niente classi, niente dependency injection,
niente istanze: si fa `import { api }` e si chiama. È la versione thin-stack del "data access layer":
una facciata piatta sopra `fetch`.

**2) Nessuna libreria di data-fetching.** Non c'è React Query, non c'è SWR, non c'è Axios, non c'è
uno store globale (Redux/Zustand). Lo stato condiviso o vive nel router (SPW) o è `useState` locale ai
componenti (SR, DIS). Il "fetching" è `fetch` nativo e basta — coerente con la filosofia del modello
(CAP 4): meno dipendenze possibile.

**3) L'auth viaggia col cookie di sessione, gestita lato server.** Il client non porta token di
bearer né stato d'autenticazione persistente: si appoggia al cookie `HttpOnly` di sessione (S1-C2).
Di conseguenza la "protezione" delle rotte admin lato client è **solo UX** — un guard che redirige o
mostra il login — mentre la difesa reale resta il gate server-side (`Auth::check`/`isLoggedIn`/
`isset($_SESSION)`). Questo doppio livello (UX immediata + sicurezza vera dietro) è esplicito in tutti
e tre.

**4) Il contratto di payload non è uniforme — e il client se ne fa carico.** È il tratto più
caratteristico del cluster. Gli endpoint PHP, cresciuti in modo incrementale, rispondono con buste
diverse (array nudo *oppure* `{data,total}` *oppure* `{success,…}`), e a volte con `HTTP 200` anche
sugli errori. Nessuno dei tre siti versiona il contratto: tutti e tre **leggono in modo difensivo**
ciò che arriva, ognuno con la propria tecnica (§2/§3).

**5) Nessun interceptor centralizzato per la sessione scaduta.** In tutti e tre il guard scatta una
volta sola (alla navigazione o al mount); se la sessione muore *mentre* l'admin edita, la mutazione
riceve `401`/`403` e il client mostra un errore generico **senza** redirigere al login. È un gap
cross-confermato sui tre siti, e uno dei box trasversali più forti.

A questi si aggiunge un tratto UX condiviso: il **mapper difensivo** DB→UI (assorbe le incoerenze di
tipo del thin stack: `is_featured === 1 || === true`, `tags` array-o-stringa-o-assente) e la
**degradazione graziosa** sulle letture non critiche (un default invece di un'eccezione).

## 2. Le varianti per sito (tabella unica, deduplicata)

| Asse | SimonePizziWebSite | SitoRuntime | DISINTELLIGENZA | *(FDCA)* |
|---|---|---|---|---|
| **Struttura client** | oggetto `api` + **`fetchConfig` condivisa** (~60 metodi) | oggetto `api`, header **per-metodo** (~30) | oggetto `api`, header per-metodo (~30) | — (nessun `api.ts`) |
| **Base URL** | **auto-commuta** `'/api'` (prod) ↔ `localhost:8888/api` (dev) | **fissa** `'/api'` (sempre same-origin) | **fissa** `'/api'` | — |
| **`credentials:'include'`** | **sì, su ogni chiamata** | **assente** (default `same-origin`) | **assente** (default `same-origin`) | — |
| **CSRF lato client** | nessuno (server usa Origin/Referer) | **token sincronizzato**: `let csrfToken` di modulo → `X-CSRF-Token` sulle mutazioni | **nessuno** | — |
| **Lettura del payload** | **"Double Read"** `Array.isArray(res) ? res : res.data` sullo stesso endpoint | **buste eterogenee per-endpoint** + guardia `Array.isArray` su speakers/podcasts | **"busta zero"** passata grezza (`return res.json()`) | — |
| **Error-handling nel client** | `if(!res.ok) throw` su ~50 metodi | **nessun throw**: body preservato, il chiamante legge `res.success` | **iniettato da CODEMOD** (`fix_api`): blocco ripetuto, metodi sfuggiti, riga duplicata | — |
| **Dove si perde il messaggio backend** | nel **client** (`api.login` → "Login fallito") | nella **UI** (`LoginForm` hardcoda "Login fallito") | **solo sui metodi sfuggiti** al codemod | — |
| **Data layer / routing** | **loader react-router** (`createBrowserRouter`, render-as-you-fetch) | `<Routes>`/`<Route element>` **classico** + `fetch` in `useEffect` | `createBrowserRouter` **senza usarne i loader** + `fetch` in `useEffect` | — |
| **Route guard admin** | **loader dichiarativo** `adminAuthLoader` → `redirect` | **componente imperativo** `Admin.tsx` (checkAuth on mount → `<LoginForm>`) | **componente** `AdminLayout` (checkAuth on mount → `navigate(login)`) | — |
| **Error boundary** | due (`RootBoundary` 404-aware via `useRouteError` + `AdminErrorBoundary`) | **uno** di classe ("Ricarica Pagina") | minimale (guard-componente, no boundary dedicato) | — |
| **Stato condiviso** | router per-rotta + 2 hook (`useFetchArticles`/`useCategories`) | **`useState` locale** + data layer `utils/news.ts` | **`useState` locale** nei componenti | — |
| **Upload** | `fetch` FormData **+ XHR `onprogress`** (barra) | `fetch` FormData + CSRF, **no progress** | `fetch` FormData, **no progress, no CSRF** | — |
| **`HTTP 200` con body d'errore** | n/a | n/a | **rattoppato per-metodo** (newsletter, DIS-C9) | — |
| **Interceptor 401/403 mid-sessione** | **assente** | **assente** (aggravato: `403` CSRF indistinguibile) | **assente** | — |

**Lettura della tabella.** Lo spettro va dal **più idiomatico-react-router** (SPW: loader come data
layer *e* come guard, Double Read esplicito, upload con progress, due boundary) al **più
minimale-imperativo** (SR e DIS: router a element/senza loader, guard nel componente, stato locale).
La novità di **SR** rispetto a SPW è interamente lato sicurezza-client: il **token CSRF in-memory**,
un meccanismo che SPW non ha proprio (gli basta Origin/Referer server-side, S1-C2). La novità di
**DIS** è di segno opposto: non aggiunge un meccanismo, ne sottrae (zero CSRF) e poi **rattoppa** la
gestione errori con un codemod. Come in S1-C1/C2, l'ordine d'investimento non coincide con la
robustezza: SPW spende nello state layer ma perde il messaggio d'errore nel client esattamente come
SR lo perde nella UI; il gap dell'interceptor 401 è **identico in tutti e tre**.

**FDCA è fuori scala (in modo diverso da S1-C1/C2).** Qui il fork **non** eredita il backend: il
frontend è stato **riscritto e ridotto** (vetrina pubblica generata via Google AI Studio) e
**non ha alcun `api.ts`** né `fetch` verso `/api` (grep negativo, FDCA-DIFF §2). Dove sul backend
FDCA era byte-identico a DIS, sul *bridge* è semplicemente **assente**: un guscio scollegato dal CMS.
Non aggiunge una variante al pattern; è il caso "frontend spento" che vive nella scheda del fork.

## 3. GOLD & box problemi-soluzioni

- **Tre modi di leggere un payload non uniforme** — *(SPW vs SR vs DIS)* — il GOLD portante del
  cluster. Stessa radice (un'API cresciuta in modo incrementale, con buste diverse e nessun
  versionamento del contratto), tre risposte lato client: **"Double Read"** `Array.isArray(res) ? res
  : res.data` sullo *stesso* endpoint che a volte è array e a volte `{data,total}` (SPW); **buste
  eterogenee lette per forma nota**, una per endpoint, con una guardia difensiva `Array.isArray`
  sui due endpoint a "array nudo o `{error}`" (SR); **"busta zero"** — il client non normalizza
  affatto, ritorna il JSON grezzo e il chiamante conosce la forma (DIS). → Box "Contratti di payload
  elastici: Double Read, guardia di tipo, busta zero".

- **Il codemod che rattoppa il client** — *(solo DIS, unico tra i siti)* — `fix_api.cjs`/`fix_api.js`
  sono due script Node che fanno una **regex-replace** su `src/api.ts`: trovano ogni
  `const res = await fetch(...)` e, se non c'è già, vi **appendono** un blocco `if(!res.ok){ …
  res.clone().json() … }`. Le tracce nel codice lo tradiscono: lo **stesso blocco verbatim in ~25
  metodi**; **metodi "sfuggiti"** che avevano già un loro `if(!res.ok)` con messaggio generico
  (`login` "Login failed", `uploadFile`, `submitVote` con stile proprio) → saltati dallo strumento,
  lasciando il bridge disomogeneo; una **riga duplicata** (artefatto di una seconda passata). È un
  caso reale di *manutenzione del client via trasformazione automatica del sorgente*, con i suoi
  effetti collaterali. **Ironia da segnalare:** il blocco iniettato è *esattamente* quello che CAP 6
  §1.1 presenta come "lo standard del Modello" (vedi correzioni §4). → Box "Il codemod che rattoppa
  il client: potenza e tracce" (alto valore, unico).

- **Il messaggio d'errore del backend che si perde** — *(SPW vs SR vs DIS — cross-confermato)* — S1-C2
  ha mostrato che il backend confeziona stati e testi precisi (`429` "Troppi tentativi…"). Il client
  li **butta via**, in tre punti diversi della pipeline: SPW nel **client** (`api.login` fa
  `throw new Error('Login fallito')` scartando il body); SR nella **UI** (`api` preserva il body ma
  `LoginForm` hardcoda "Login fallito" e scarta `err.message`); DIS in modo **frammentato** (i metodi
  coperti dal codemod preservano `j.message`, quelli sfuggiti no). Esito identico ovunque: l'utente
  rate-limited vede sempre "Login fallito" e mai il `429`. → Box "Leggere il body anche sui rami
  d'errore" (alto valore; la lezione è una, i punti di perdita sono tre).

- **Dove vive il token CSRF lato client** — *(SR, complemento di S1-C2)* — il meccanismo più
  sofisticato del cluster e la divergenza forte da SPW. Il backend SR restituisce `csrf_token` nel
  body di `login`/`check_auth` e pretende `X-CSRF-Token` sulle mutazioni; il client lo gestisce con la
  forma più minimale possibile: **una variabile a livello di modulo** (`let csrfToken = ''`), non
  `localStorage`, non Context, non stato di componente. Catturata nel body → reiniettata via
  `csrfHeaders()` solo sui POST/DELETE → azzerata al logout. Conseguenza strutturale: a un **hard
  reload** il token sparisce e le mutazioni successive andrebbero in `403` — regge **solo** perché
  `Admin.tsx` rifà `checkAuth()` on mount, che ri-restituisce il token. È una **garanzia accoppiata e
  non dichiarata**. → Box "Il token CSRF e il reload: in-memory vs storage" (è il lato *client* del
  box CSRF di S1-C2).

- **Guard come loader vs guard come componente** — *(SPW vs SR/DIS)* — due scuole per la stessa cosa.
  SPW usa un **loader dichiarativo** (`adminAuthLoader` → `redirect('/admin/login')`) montato sulla
  rotta padre `/admin`: una guardia, N pagine figlie. SR e DIS usano un **componente imperativo**
  (`checkAuth` on mount, macchina a stati `loading → (!user ? LoginForm : Dashboard)`). In tutti e tre
  la difesa *reale* resta server-side (S1-C2): il guard client è UX immediata, non sicurezza. → Box
  "Proteggere l'area admin di una SPA: loader o componente" (ponte a S1-C12 per l'orchestrazione).

- **Quando NON serve `credentials:'include'`** — *(SPW vs SR/DIS)* — SPW mette `credentials:'include'`
  su ogni chiamata (deve, perché in dev attraversa `localhost:8888`); SR e DIS non lo mettono mai,
  perché sviluppano e deployano **same-origin** e il cookie parte da solo (default `same-origin` di
  `fetch`). È la **controparte client esatta** dell'osservazione di S1-C2: la CORS di SR non emette
  `Access-Control-Allow-Credentials`, quindi l'auth è de-facto same-origin su *entrambi* i lati →
  il client non ha bisogno di `include`. → Box "`credentials:'include'`: quando serve e quando è
  rumore" (ponte CORS S1-C2).

- **Niente interceptor 401/403 mid-sessione** — *(tutti e tre)* — il gap trasversale. Il guard scatta
  solo alla navigazione (SPW) o al mount (SR/DIS); se la sessione scade *durante* l'editing (es. dopo
  un reset password che invalida `session_version`, S1-C2), la `save` riceve `401`/`403`, il client
  mostra un errore generico e **non** redirige: l'utente resta su una pagina "morta". Manca un punto
  unico che riconosca lo status e forzi il re-login. In SR è aggravato dal fatto che un `403` da CSRF
  scaduto è indistinguibile a UI da un errore di salvataggio. → Box "Gestire la scadenza di sessione
  nel thin stack" (ponte a `session_version` di S1-C2, alto valore perché comune ai tre).

- **Quando il `200` nasconde un errore** — *(DIS, = CAP 6 §4)* — alcuni endpoint DIS (newsletter
  `subscribe`/`send`) tornano `HTTP 200` anche in errore, con `{status:'error'}`; il client aggiunge a
  mano `if (data.status === 'error') throw` **per-metodo**, invece che con un interceptor unico. È la
  conseguenza di un backend che non usa sempre i codici HTTP (DIS-C9): il bridge se ne fa carico caso
  per caso. → Box "Validazione incrociata HTTP vs logica" (esiste già come CAP 6 §4, va attribuito a
  DIS e non spacciato per standard universale — vedi correzioni).

## 4. Mappa → capitolo/i del libro

| Materiale della scheda | Capitolo esistente | Azione |
|---|---|---|
| Oggetto `api` su `fetch`, niente React Query/Axios/Redux | **CAP 6 §1** + **CAP 4 (Frontend Dependencies)** | **aggiorna**: il "niente librerie di fetching" è una scelta da esplicitare (ponte CAP 4) |
| **Tre modi di leggere il payload** (Double Read / guardia di tipo / busta zero) | **CAP 6 §1.1** | **riscrivi**: oggi §1.1 chiama "Double Read" la cosa sbagliata (vedi correzioni) |
| **Token CSRF lato client** (variabile di modulo, reload, handshake) | **CAP 6** (nuovo §) + **CAP 10** (ponte) | **nuovo §**: oggi CAP 6 non lo menziona affatto — è il lato client del CSRF di CAP 10 |
| Guard admin: **loader vs componente** | **CAP 6 §3** + **CAP 10 §2** | **nuovo box**: oggi CAP 10 §2 dà solo il "Layout Wrapper"; manca il confronto loader/componente |
| `credentials:'include'` sì/no + same-origin | **CAP 6 §1** | **nuovo box**: quando serve e quando è rumore (ponte CORS CAP 10) |
| **Messaggio backend perso nel login** (client / UI / codemod) | **CAP 6** | **nuovo box problemi-soluzioni** (alto valore, cross-sito) |
| **Niente interceptor 401/403 mid-sessione** | **CAP 6 §3** + **CAP 10** (ponte `session_version`) | **nuovo box** trasversale |
| **Il codemod `fix_api`** che inietta l'error-handling | **CAP 6 §1.1** | **nuovo box** (e spiega da dove viene il blocco oggi presentato come standard) |
| Validazione incrociata HTTP 200 vs logica (DIS) | **CAP 6 §4** | **aggiorna attribuzione**: è il pattern di DIS, non "il Modello" |
| `checkAuth` silenzioso → `null` + hard logout reload | **CAP 6 §3.1–3.2** | **aggiorna attribuzione**: prescrizione DIS-flavored, vedi correzioni |
| Loader come orchestratore + Double Read sulle liste paginas | **CAP 9 (Content Lifecycle)** + **CAP 6 §6** | **ponte**: il contratto `{data,total}` letto "due volte" è la radice della paginazione |
| Upload `fetch` FormData (± progress, ± CSRF) | **CAP 6 §2** + **CAP 7 (Media)** | **aggiorna**: le tre varianti (XHR-progress / no-progress / no-progress-no-CSRF) |

**Correzioni al testo attuale (la mappatura smentisce / disallinea il libro):**
- **CAP 6 §1.1 — il nome "Double Read" è attribuito al pattern SBAGLIATO.** §1.1 chiama "Pattern
  Double Read (Response Cloning)" il blocco `res.clone().json()` che estrae il *messaggio d'errore*
  dalla risposta. Nelle fonti reali **"Double Read" è tutt'altro**: è `Array.isArray(res) ? res :
  res.data`, cioè leggere il *payload di successo* in due **forme** possibili (array nudo vs
  `{data,total}`), ed è un pattern di **SPW**. Il blocco con `res.clone()` è l'**estrazione del body
  d'errore** — e, fatto notevole, è *esattamente* il blocco che il **codemod di DIS** (`fix_api`) ha
  iniettato in ~25 metodi. Da separare in due concetti distinti con due nomi distinti: «Double Read =
  lettura della forma del payload» e «Response cloning = estrazione del messaggio d'errore».
- **CAP 6 §§1.1/3.1/3.2/4 sono "il Modello" ma descrivono il sito più minimale (DIS).** Il
  clone-errori (§1.1), il `checkAuth → null` silenzioso (§3.1), l'hard logout con `reload()` (§3.2) e
  la validazione incrociata `200`-con-errore (§4) sono presentati come prescrizioni universali, ma
  nella realtà sono i pattern di **DISINTELLIGENZA** (e il §1.1 è perfino frutto di un codemod). La
  realtà dei tre siti è uno **spettro**: SPW investe in loader+Double Read, SR nel token CSRF, DIS nel
  codemod. Da riallineare: separare "ciò che il Modello *raccomanda*" da "ciò che un *singolo* sito
  fa".
- **CAP 6 non parla del token CSRF lato client né del guard admin.** Sono due assi centrali del
  cluster (il token in-memory di SR è il meccanismo più sofisticato; loader-vs-componente è una scelta
  architetturale vera) e oggi mancano. Da aggiungere, con ponte a CAP 10.
- **CAP 6 §6 (paginazione) è SPW-centrico.** L'esempio `useFetchArticles`/`hasMore` è di SPW; SR fa
  load-more *senza* dedup (si fida del backend) e DIS non pagina affatto. Da segnalare come variante,
  e da legare al Double Read (il contratto `{data,total}` è ciò che rende possibile — e necessaria —
  la doppia lettura).

## 5. Cosa si scarta / dedup

- **Ripetizioni fuse:** i §6 delle tre card raccontavano lo stesso ponte da tre punti di vista (SPW
  "io vs SR" ipotetico, SR "io vs SPW" con tabella a 14 righe, DIS "io vs entrambi" con tabella a 10
  righe). Qui la tabella comparativa è scritta **una volta sola**, deduplicata.
- **Dettaglio per-sito che NON entra nel libro:** numeri di riga esatti, il bug `#/` residuo da
  HashRouter di SPW, il `subscribeNewsletter` di SR che invia senza `Content-Type`, i commenti
  "ragionamento ad alta voce" di DIS (`api.ts` submitParticipant), la firma esatta del regex del
  codemod (resta nelle card come fonte; nel libro basta il *pattern* + le tre tracce).
- **Materiale che appartiene ad altre schede (per evitare doppioni a valle):**
  - le **buste lato server** (chi ritorna array nudo, chi `{data,total}`, chi `{success,…}`), la
    regola di visibilità, gli slug → **S1-C4 (Content APIs)**; qui solo come il client *legge* quelle
    buste, non come il server le *produce*.
  - il **gate server-side** (`Auth::check`/`isLoggedIn`/CSRF a token nel body), `session_version`,
    CORS/`Allow-Credentials` → **S1-C2 (Security & Auth)**; qui solo la *controparte client* (guard,
    `credentials`, `X-CSRF-Token`).
  - la **sanitizzazione render-time** (DOMPurify + iframe YouTube prima di `dangerouslySetInnerHTML`)
    e Tiptap → **S1-C6 (Editor)**; qui solo notato che il bridge passa `content` grezzo al sanitizer.
  - l'**orchestrazione admin** (`AdminLayout`, RBAC della sidebar, pannelli che consumano `api`) →
    **S1-C12 (Admin Dashboard)**; qui solo il guard come superficie.
  - l'**upload server** (validazione, WebP, catena RCE di DIS-C5) → **S1-C5 (Media)**; qui solo la
    chiamata client `FormData` (± progress, ± CSRF).
  - il **frontend riscritto/scollegato di FDCA** (nessun `api.ts`) → **scheda fork**; qui solo la nota
    "bridge assente".
