# Mappatura — SitoRuntime — C3: Frontend Bridge & State

> **Stato:** COMPLETATO
> **Sessione:** 14 · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `SitoRuntime/`)
> - `src/api.ts` (client HTTP unico: `API_BASE`, stato modulo `csrfToken`, `csrfHeaders()`, oggetto `api` con ~30 metodi)
> - `src/App.tsx` (router `BrowserRouter`/`Routes`/`Route` a element, code-splitting `lazy`+`Suspense`, `ErrorBoundary` unico)
> - `src/pages/Admin.tsx` (guard a livello di componente: `checkAuth` on mount, `if(!user) → <LoginForm>`; orchestratore stato admin)
> - `src/components/admin/LoginForm.tsx` (form login, gestione errore locale)
> - `src/components/admin/ArticleEditor.tsx:160-246` (upload immagini come bridge: `uploading` booleano, niente progress)
> - `src/components/ErrorBoundary.tsx` (boundary di classe, fallback "Ricarica Pagina")
> - `src/utils/news.ts` (data layer pubblico: `getNews`/`getArticleBySlug` + mapper `RawApiArticle`→`NewsItem`/`Article`)
> - `src/pages/News.tsx` (paginazione load-more lato client su stato locale) · `src/pages/Article.tsx` (lettura singola + sanitize render-time → C6)
> - Letti come consumatori del contratto: `src/components/admin/MediaGallery.tsx`, `PodcastManager.tsx`, `NewsletterComposer.tsx`, `UserManagement.tsx`, `src/pages/Podcasts.tsx`, `About.tsx`, `Home.tsx`, `Contact.tsx`
> - `public/api/admin.php` (contratto risposta `check_auth`/`login`/`list`, letto come consumatore — vedi SR-C2)

## 1. Cosa fa (sintesi narrativa)

C3 è il **ponte client↔server** di SitoRuntime: il punto in cui la SPA React parla con gli endpoint
PHP di C1/C2/C4. Come in SimonePizziWebSite **non c'è libreria di data-fetching** (niente React
Query, Axios, Redux): tutto poggia su `fetch` nativo. Ma rispetto a SPW-C3 il modello **diverge su
tre assi architetturali**, e questa è l'osservazione centrale della card:

1. **Un solo modulo client `src/api.ts`**, oggetto-namespace `api` con un metodo per azione
   (`getNews`, `login`, `saveArticle`, `uploadImage`, `deleteSpeaker`…). Ma a differenza di SPW:
   - la base URL è **fissa e relativa**: `const API_BASE = '/api'` (`api.ts:4`), **senza auto-commutazione
     prod/dev** e senza `localhost:8888` (SPW: `import.meta.env.PROD ? '/api' : 'http://localhost:8888/api'`).
     SitoRuntime sviluppa quindi sempre **same-origin** (proxy Vite o build servita dal PHP);
   - **non esiste una `fetchConfig` condivisa** e — punto cruciale — **non c'è `credentials:'include'`
     da nessuna parte**. Il cookie di sessione viaggia con la policy `fetch` di default (`same-origin`),
     che basta perché tutto è same-origin. È la controparte client esatta dell'osservazione di SR-C2:
     la CORS multi-dominio **non** emette `Access-Control-Allow-Credentials`, quindi l'auth è di fatto
     same-origin → il client non ha bisogno di `credentials:'include'`;
   - **niente gestione errore nel client**: ogni metodo fa `return await res.json()` **senza
     `if(!res.ok) throw`** (SPW invece lancia su ~50 metodi). Il body della risposta — anche d'errore
     `{success:false, error}` — è quindi **sempre preservato** e passato al chiamante, che decide.

2. **La gestione del token CSRF lato client** (la divergenza-chiave da SPW, che non ha CSRF a token).
   SR-C2 ha mostrato che il backend **restituisce `csrf_token` nel body** di `login`/`check_auth` e
   pretende l'header `X-CSRF-Token` sulle mutazioni. Il frontend implementa l'handshake con la
   forma più minimale possibile: **una variabile a livello di modulo** in `api.ts`.
   - `let csrfToken = ''` (`api.ts:6`): NON in `localStorage`, NON in un Context React, NON in stato
     di componente. Vive solo **in memoria del modulo**.
   - viene **catturato** dentro `login` (`api.ts:31`) e `checkAuth` (`api.ts:37`):
     `if (data.csrf_token) csrfToken = data.csrf_token;`
   - viene **iniettato** sulle mutazioni via helper `csrfHeaders()` (`api.ts:8-10`), spread negli
     header di tutte le POST/DELETE: `headers: { 'Content-Type': 'application/json', ...csrfHeaders() }`.
   - viene **azzerato** al logout (`api.ts:42`: `csrfToken = ''`).
   Conseguenza strutturale (vedi §4): essendo in-memory, **al reload della pagina il token è perso**
   finché `checkAuth()` non viene rieseguito — cosa che `Admin.tsx` fa sempre `onMount`, quindi nel
   flusso reale funziona, ma è una dipendenza implicita fragile.

3. **La protezione delle rotte admin è un componente, non un loader.** SitoRuntime usa il **router
   classico a element** (`<BrowserRouter><Routes><Route element=…>`, `App.tsx:54-72`): **niente
   data-loader, niente `adminAuthLoader`/`redirect` di react-router** come in SPW. La rotta
   `/admin` è un semplice `<Route path="/admin" element={<Admin />} />` (`App.tsx:68`) **senza guard
   a livello router**. Il gate vive **dentro** `Admin.tsx`: `checkAuth()` on mount (`Admin.tsx:74-88`),
   `loading` finché risponde, poi `if (!user) return <LoginForm/>` (`Admin.tsx:189`). È un guard
   **render-time imperativo** (stato `user` nel componente), non dichiarativo. La vera difesa resta —
   come in SPW — server-side: `isLoggedIn()`/`validateCsrf()` per-ramo di SR-C2.

Lo stato è quindi **tutto locale ai componenti** (`useState`+`useEffect`): non c'è store globale né
data layer react-router. Il data layer pubblico è fattorizzato in `src/utils/news.ts` (mapper +
fetch), gli altri domini fanno `fetch` diretto via `api` dentro lo `useEffect` della pagina.

## 2. Pattern miniCMS rilevanti

- **Client come oggetto-namespace su `fetch`** (`api.ts:12`): un singolo `export const api` con metodi
  raggruppati per dominio via commenti (`// Public Read`, `// Admin Auth`, `// Speakers`, `// Newsletter`,
  `// Podcast Feeds`). Identico spirito a SPW (niente classi/DI, import diretto), **ma più sottile**:
  niente `fetchConfig`, niente error-handling, ogni metodo è 3-4 righe.
- **CSRF synchronizer token lato client come stato di modulo** (`api.ts:6-10,31,37,42`): è il pattern
  centrale e la divergenza forte da SPW (che non ha CSRF a token: usa Origin/Referer server-side).
  Cattura nel body → memorizzazione in chiusura di modulo → reiniezione via header. Minimalismo
  estremo: nessuna astrazione, nessuna persistenza.
- **Header CSRF condizionale e per-metodo** (`csrfHeaders()`): l'header `X-CSRF-Token` è emesso **solo
  se** il token è presente e **solo sui metodi mutativi** (POST/DELETE). Le letture pubbliche (`getNews`,
  `getSpeakers`, `getPodcasts`) non lo includono — coerente col gate server che chiede `validateCsrf()`
  solo sulle mutazioni.
- **Guard render-time nel componente, non nel router** (`Admin.tsx:74-88,183-189`): `checkAuth` on
  mount + macchina a stati `loading → (!user ? LoginForm : Dashboard)`. È il "Auth::check lato client"
  di SitoRuntime, ma realizzato con `useState`/`useEffect` invece che con un loader dichiarativo.
- **Contratti di payload eterogenei letti "per forma nota"** (NON Double Read): ogni endpoint ha la
  **sua** busta e il client la conosce esplicitamente (vedi §3/§6). Non c'è il `Array.isArray(res) ? res
  : res.data` di SPW sullo *stesso* endpoint; c'è invece un **mosaico di buste diverse** più, su due
  endpoint, una **guardia difensiva `Array.isArray(res)`** (vedi sotto).
- **`Array.isArray` come guardia anti-errore sugli endpoint a "array nudo"** (`Podcasts.tsx:14`,
  `PodcastManager.tsx:26`, `About.tsx:24`, `Home.tsx:59`, `PodcastDetail.tsx:34`): speakers e podcasts
  rispondono con un **array JSON nudo** in caso di successo, ma con `{success:false, error}` in caso
  d'errore. Il client distingue i due con `if (Array.isArray(res)) setX(res)`: se è array è dato buono,
  altrimenti si ignora silenziosamente. È il "cugino" del Double Read di SPW — stessa radice (contratto
  non uniforme), soluzione diversa (guardia di tipo invece di doppia lettura).
- **Data layer pubblico fattorizzato + mapper difensivo** (`utils/news.ts`): `getNews`/`getArticleBySlug`
  isolano il `fetch` e convertono il record grezzo `RawApiArticle` in `NewsItem`/`Article`, assorbendo
  le incoerenze del thin stack (`published_at ?? created_at ?? Date.now()`, `category || 'News'`,
  `cover_image || ''`, `author || 'Redazione'`). È l'equivalente di `mappers.ts` di SPW, ma con dentro
  anche il fetch e la **degradazione graziosa** (catch → `{items:[], meta:{…}}`).
- **Code splitting per rotta** (`App.tsx:12-28`): tutte le pagine — incluso l'intero `Admin` — sono
  `lazy()`+`Suspense` con `PageLoader`, così il bundle pubblico non porta il peso del pannello.

## 3. Codice chiave (stralci con origine)

**Base URL fissa relativa + stato CSRF di modulo + header condizionale** — `src/api.ts:4-10`:

```ts
const API_BASE = '/api';                 // niente switch prod/dev, niente localhost: sempre same-origin

let csrfToken = '';                      // stato in-memory del MODULO (no localStorage, no Context)

function csrfHeaders(): Record<string, string> {
    return csrfToken ? { 'X-CSRF-Token': csrfToken } : {};
}
```

**Cattura del token CSRF dal body (handshake) — niente `credentials:'include'`** — `src/api.ts:24-39`:

```ts
login: async (username, password) => {
    const res = await fetch(`${API_BASE}/admin.php?action=login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },   // <-- nessun credentials:'include'
        body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (data.csrf_token) csrfToken = data.csrf_token;       // cattura nel body (SR-C2)
    return data;                                            // <-- nessun if(!res.ok) throw: body preservato
},
checkAuth: async () => {
    const res = await fetch(`${API_BASE}/admin.php?action=check_auth`);
    const data = await res.json();
    if (data.csrf_token) csrfToken = data.csrf_token;       // ri-cattura: ricostruisce il token al mount
    return data;
},
```

**Reiniezione del token sulle mutazioni** — `src/api.ts:55-70` (stesso schema su tutti i POST/DELETE):

```ts
saveArticle: async (article) => {
    const res = await fetch(`${API_BASE}/admin.php?action=save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...csrfHeaders() },  // X-CSRF-Token qui
        body: JSON.stringify(article)
    });
    return await res.json();
},
deleteSpeaker: async (id) => {
    const res = await fetch(`${API_BASE}/speakers.php?id=${id}`, {
        method: 'DELETE',
        headers: { ...csrfHeaders() }
    });
    return await res.json();
},
```

**Guard render-time nel componente (no loader react-router)** — `src/pages/Admin.tsx:74-88,183-189`:

```tsx
useEffect(() => { checkAuth(); }, []);

const checkAuth = async () => {
    try {
        const res = await api.checkAuth();
        if (res.authenticated) {        // busta {authenticated, user, csrf_token}
            setUser(res.user);          // res.user = { username, role } (oggetto)
            loadData();
        }
    } finally { setLoading(false); }
};
// ...nel render:
if (loading) return <Loader …/>;
if (!user)   return <LoginForm onLogin={handleLogin} />;   // gate: nessun utente → form di login
```

**Buste di payload eterogenee, lette ognuna per la sua forma** (il "non-Double-Read"):

```ts
// news.php (pubblico):  { success, data:[…], meta:{ current_page, total_pages, total_items } }
if (res.success) { items: res.data.map(mapToNewsItem), meta: res.meta || {…} }   // utils/news.ts:31-34
// admin.php?action=list:  { success, articles:[…], total }
setArticles(newsRes.articles); setArticlesTotal(newsRes.total ?? newsRes.articles.length); // Admin.tsx:93-94
// admin.php?action=check_auth/login:  { authenticated|success, user:{username,role}, csrf_token }
// speakers.php / podcasts.php:  ARRAY NUDO (o {success:false,error} su errore)
if (Array.isArray(res)) setPodcasts(res);                                        // Podcasts.tsx:14
// feed_config.php:  { success, feed_url }      media:{ success, files }   newsletter:{ success, subscribers }
```

**Mapper difensivo + degradazione graziosa del data layer pubblico** — `src/utils/news.ts:28-41`:

```ts
export const getNews = async (page = 1, limit = 6) => {
    try {
        const res = await api.getNews(page, limit);
        if (res.success) {
            return { items: res.data.map(mapToNewsItem),
                     meta: res.meta || { current_page: page, total_pages: 1, total_items: 0 } };
        }
    } catch (e) { console.error("Failed to fetch news", e); }
    return { items: [], meta: { current_page: page, total_pages: 1, total_items: 0 } }; // fallback "vuoto ma valido"
};
```

**Upload come bridge: `fetch` FormData + CSRF, ma SENZA progress** — `src/api.ts:71-80`:

```ts
uploadImage: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/upload.php`, {
        method: 'POST',
        headers: { ...csrfHeaders() },   // NB: niente Content-Type → boundary multipart corretto
        body: formData
    });
    return await res.json();
},
```
Il chiamante (`ArticleEditor.tsx:169-181,233-245`, `MediaGallery.tsx:49`) usa solo un booleano
`uploading` (spinner on/off) — **niente barra di avanzamento** (SPW invece ha la variante XHR
`xhr.upload.onprogress`).

## 4. Problemi riscontrati & soluzioni

- **Messaggio d'errore del backend perso nel login — GOLD (parallelo identico a SPW-C3).** SR-C2
  confeziona stati semantici precisi (`429` "Troppi tentativi. Riprova tra 15 minuti.", `401`
  "Invalid credentials"). E qui — a differenza di SPW — il client **preserva** il body: `api.login`
  ritorna `data` intero (`api.ts:30-32`), e `Admin.handleLogin` fa `throw new Error(res.error)`
  propagando il testo del server (`Admin.tsx:119-120`). **Ma il punto di perdita si è solo spostato
  più in alto**: `LoginForm.handleSubmit` (`LoginForm.tsx:18-25`) cattura l'errore e mostra un
  **letterale hardcoded** `setError('Login fallito. Controlla le credenziali.')`, **scartando
  `err.message`**. Risultato finale identico a SPW: l'utente rate-limited vede sempre "Login fallito"
  e mai il `429`. Lezione speculare per il libro: in SPW il body si perde nel *client* (`api.ts`), in
  SR si perde nella *UI* (`LoginForm`) — **due punti diversi della pipeline, stesso esito**.
- **Token CSRF in-memory: perso al reload, dipendenza implicita da `checkAuth` on mount.** `csrfToken`
  vive solo nella chiusura del modulo (`api.ts:6`). Un **hard reload** della pagina admin azzera la
  variabile; le mutazioni successive partirebbero **senza** `X-CSRF-Token` → `403` da `validateCsrf()`.
  Il sistema regge **solo perché** `Admin.tsx` esegue `checkAuth()` `onMount` (`Admin.tsx:74-75`), e
  `check_auth` **ri-restituisce** il token (`admin.php`, SR-C2) che `api.ts:37` ri-cattura. È una
  garanzia **accoppiata e non dichiarata**: se un domani una rotta admin montasse un editor senza
  passare dal `checkAuth` di `Admin`, le POST fallirebbero in modo opaco. → Box "dove vive il token
  CSRF nel client: in-memory vs storage, e il prezzo del reload".
- **Niente gestione `401`/`403` mid-sessione, nessun interceptor centralizzato (come SPW).** Il guard
  (`checkAuth`) scatta **solo al mount** di `Admin`. Se la sessione scade mentre l'admin edita, una
  `saveArticle` riceve `401`/`403`, `ArticleEditor` mostra un `alert('Errore: …')` (`ArticleEditor.tsx:215`)
  **senza** redirigere al login né rifare `checkAuth`. L'utente resta su una pagina "morta". Manca un
  punto unico che riconosca lo status e forzi il re-login. Identico gap a SPW-C3 — qui aggravato dal
  fatto che un `403` da CSRF scaduto è indistinguibile a UI da un errore di salvataggio generico.
- **`subscribeNewsletter` invia il body senza `Content-Type` (bug minore).** `api.ts:151-156`:
  `fetch(..., { method:'POST', body: JSON.stringify({email}) })` **senza** header `Content-Type:
  application/json`. Il browser invia allora `text/plain;charset=UTF-8`; il backend deve leggere
  `php://input` grezzo (non `$_POST`) perché regga — funziona solo se `newsletter.php` fa
  `json_decode(file_get_contents('php://input'))`. Incoerenza rispetto a tutte le altre POST del file
  che impostano l'header. → Nota/verifica in C9.
- **Gestione errore duplicata e "alert-driven" in ogni chiamante.** Non essendoci `throw` nel client,
  **ogni call site** ripete `try { const res = await api.x(); if (res.success) {…} else alert(res.error) }
  catch { alert('Errore di connessione') }` (`ArticleEditor.tsx:201-246`, `Admin.tsx:170-181`, ecc.).
  Funziona ma è verboso e usa `alert()`/`confirm()` nativi (UX grezza). Un helper `request()` unico
  centralizzerebbe CSRF, lettura busta, `401`-handling e messaggistica. → Box "quando il thin stack
  chiede un piccolo strato di astrazione" (gemello del rilievo SPW-C3).
- **`res.user` cambia forma tra check_auth e l'uso UI, ma regge.** `check_auth`/`login` restituiscono
  `user: { username, role }` (oggetto — vedi `admin.php`, SR-C2), e la UI legge `user.username`
  (`Admin.tsx:221`) e `user.role` (`Admin.tsx:522,529`) per il gating delle sezioni admin-only. NB:
  SR-C2 ha annotato che il backend **non** salva `username` in sessione, ma **lo rispedisce** nel body
  di login da `$user['username']` — quindi a video il nome appare; sul DB l'autore articolo resta
  'Admin'. Coerenza solo apparente. → Ponte a SR-C2 §4 e a C4 (campo `author`).

## 5. Estetica / UX (moderna ma funzionale)

- **Error boundary unico di classe, brandizzato** (`ErrorBoundary.tsx`): un solo `ErrorBoundary` avvolge
  tutta l'app in `App.tsx:94`. Fallback con icona `AlertTriangle`, "Qualcosa è andato storto" + bottone
  "Ricarica Pagina" (`window.location.reload()`); stack visibile **solo in `import.meta.env.DEV`**. Più
  semplice della coppia `RootBoundary`/`AdminErrorBoundary` di SPW (niente distinzione 404-vs-errore,
  niente `useRouteError` perché non si usano i loader).
- **Macchina a 3 stati ovunque: loading → empty → contenuto.** Pattern ripetuto in modo coerente:
  `News.tsx:61-69` (spinner → "Nessun articolo trovato. Torna a controllare presto!" → griglia),
  `Article.tsx:74-97` (spinner → "Articolo non trovato" con link di ritorno → articolo),
  `Admin.tsx:183-189` (spinner → LoginForm → dashboard). Gli stati vuoti sono **brandizzati e parlanti**,
  mai schermate bianche.
- **Load-more incrementale su stato locale** (`News.tsx:30-38`): `setNews(prev => [...prev, ...result.items])`
  con `currentPage < totalPages` (`News.tsx:161`) a guidare il bottone "Carica altri articoli". Niente
  dedup esplicito (a differenza dell'hook di SPW) — si fida del backend per non ripetere.
- **Dashboard admin a card-griglia con sezione attiva** (`Admin.tsx:234-299`): 8 `DashboardCard` colorate
  (Utenti/News/Speaker/Newsletter/Podcast/Media/Feed/Impostazioni) che cambiano `section`; le sezioni
  admin-only (`users`/`newsletter`) sono gated client-side su `user.role === 'admin'` (`Admin.tsx:522,529`)
  — coerente coi ruoli di SR-C2, ma è solo UX: la vera difesa è `isAdmin()` server.
- **`ConfirmDialog` custom** (`Admin.tsx:152-161,205`) per le eliminazioni speaker, ma **`alert()`/
  `confirm()` nativi** altrove (`ArticleEditor.tsx:175,225`): UX disomogenea (metà premium, metà grezza).
- **Paginazione admin "range testuale"** (`Admin.tsx:372-392`): "1–20 di 137" con frecce Prec/Succ
  disabilitate ai bordi — pulita e informativa.

## 6. Differenze rispetto agli altri siti

Il confronto con **SPW-C3** è il cuore della card: stessa filosofia (niente librerie di data-fetching,
oggetto `api` su `fetch`, guard client + difesa server reale), **implementazione divergente su quasi
ogni asse del ponte**.

| Aspetto | SimonePizziWebSite (SPW-C3) | SitoRuntime (questa card) |
|---|---|---|
| **Base URL** | auto-commuta `'/api'` (prod) ↔ `'http://localhost:8888/api'` (dev) | **fissa `'/api'`**, nessuno switch dev (sempre same-origin) |
| **`fetchConfig` condivisa** | sì (`credentials`+headers riusati) | **no**: ogni metodo costruisce i propri header |
| **`credentials:'include'`** | **sì, su ogni chiamata** (cookie di sessione esplicito) | **assente** (default `same-origin`; coerente con CORS senza `Allow-Credentials` di SR-C2) |
| **CSRF lato client** | **nessuno** (server usa Origin/Referer) | **token sincronizzato**: `csrfToken` di modulo, catturato nel body, rispedito in `X-CSRF-Token` |
| **Dove vive il token CSRF** | n/a | **variabile in-memory del modulo** (no localStorage/Context) → persa al reload |
| **Error handling nel client** | `if(!res.ok) throw new Error('…')` su ~50 metodi (body spesso scartato nel client) | **nessun throw**: `return res.json()` sempre → body preservato; il chiamante legge `res.success` |
| **Dove si perde il messaggio backend** | nel **client** (`api.login` genera "Login fallito") | nella **UI** (`LoginForm` hardcoda "Login fallito", scarta `err.message`) — **stesso esito** |
| **Data layer / routing** | **loader react-router** (`createBrowserRouter`, render-as-you-fetch) | **`<Routes>`/`<Route element>` classico** + `fetch` in `useEffect`; niente loader |
| **Route guard admin** | **loader dichiarativo** `adminAuthLoader`→`redirect('/admin/login')` sulla rotta padre | **componente imperativo**: `checkAuth` on mount in `Admin.tsx`, `if(!user)→<LoginForm>` |
| **Contratto payload** | **Double Read** sullo stesso endpoint: `Array.isArray(res)?res:res.data` | **buste eterogenee per-endpoint** (`{success,data,meta}` / `{success,articles,total}` / array nudo / `{success,feed_url}`) + **guardia `Array.isArray` anti-errore** su speakers/podcasts |
| **Error boundary** | due (`RootBoundary` 404-aware via `useRouteError` + `AdminErrorBoundary`) | **uno solo** di classe, fallback "Ricarica Pagina" (no 404 dedicato: non ci sono loader) |
| **404 reale** | `throw new Response(404)` intercettato dal boundary | rotta catch-all `<Route path="*" element={<NotFound/>}>` + "non trovato" inline nei componenti |
| **Upload** | `fetch` FormData **+ variante XHR con `onprogress`** (barra) | **solo `fetch` FormData** + booleano `uploading` (spinner, niente progress) + `X-CSRF-Token` |
| **Stato condiviso** | quello del router (per-rotta) + 2 hook (`useFetchArticles`/`useCategories`) | **tutto `useState` locale** ai componenti; data layer pubblico in `utils/news.ts` |
| **Interceptor 401 mid-sessione** | **assente** (gap noto) | **assente** (gap identico, aggravato da `403` CSRF indistinguibile) |

Sintesi: **SPW** è più "react-router-idiomatico" (loader come data layer e come guard, Double Read
esplicito, upload con progress), **SitoRuntime** è più "minimale-imperativo" (router a element, guard
nel componente, stato locale, CSRF a token gestito con una variabile di modulo). La novità di C3 di
SR rispetto a SPW è **interamente la gestione del token CSRF lato client** — un meccanismo che SPW
non ha proprio. Il gap comune più rilevante resta il **mancato interceptor 401/403 mid-sessione**:
presente in entrambi i siti, è candidato a un box trasversale.

Per DISINTELLIGENZA/FDCA (SQLite, festival) il bridge sarà verosimilmente ancora più piccolo
(voto/iscrizione): termine di paragone "minimo" alle rispettive card C3.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **Token CSRF lato client come stato di modulo** (cattura nel body → header `X-CSRF-Token`) | Cap. "CSRF nel thin stack" — **lato CLIENT**, complemento del lato server di SR-C2 (alto valore) |
| **Dove vive il token: in-memory vs storage**, e il prezzo del reload (dipendenza da `checkAuth`) | Box "Il token CSRF e il reload: una garanzia accoppiata" (nuovo) |
| Base URL **fissa same-origin** + **niente `credentials:'include'`** vs SPW prod/dev + include | Cap. "Un client HTTP minimale" / Box "quando NON serve `credentials:'include'`" (ponte CORS SR-C2) |
| **Client senza `throw`**: il body d'errore preservato, la perdita si sposta nella UI | Box "leggere il body anche sugli errori" — **2ª variante** (la perdita in `LoginForm` vs in `api.ts` di SPW) |
| **Guard nel componente** (`checkAuth` on mount) vs **guard come loader** (SPW) | Cap. "Proteggere le rotte admin lato client": due scuole (loader vs componente) |
| **Buste eterogenee per-endpoint** + **guardia `Array.isArray` anti-errore** vs Double Read di SPW | Cap. "Contratti di payload elastici": Double Read (SPW) e guardia di tipo (SR), stessa radice |
| Router classico `<Routes>` vs `createBrowserRouter`+loader | Box "Due modi di fare routing in React: dichiarativo-dati vs element" |
| Data layer fattorizzato + mapper difensivo + degradazione graziosa (`utils/news.ts`) | Cap. "Normalizzare i record del thin stack" (ponte mapper SPW) |
| Upload `fetch` FormData con CSRF **senza** progress vs XHR con barra (SPW) | Cap. "Upload file dal client": versione minimale (ponte C5) |
| **Niente interceptor 401/403 mid-sessione** (comune a SPW e SR) | Box "gestire la scadenza di sessione nel thin stack" (trasversale, alto valore) |
| `subscribeNewsletter` POST senza `Content-Type` | Box "il body JSON che arriva come text/plain" (ponte C9) |

## 8. Note / domande aperte

- **Puntatori ad altri cluster** (annotati qui, NON mappati in questa card):
  - I metodi di `api.ts` toccano endpoint di **C4** (`news.php`/`speakers.php` lato contenuti),
    **C5** (`upload.php`/`media.php`), **C8** (`feed_config.php`, RSS privato Telegram), **C9**
    (`newsletter.php`/`contact.php`), **C12** (admin dashboard/users/podcasts). Qui interessa **solo**
    come il client li chiama (firma, verbo HTTP, forma busta); la *logica server* è dei rispettivi cluster.
  - **`Article.tsx:13-42`**: `sanitizeContent` con DOMPurify + estrazione/ripristino degli iframe
    YouTube prima della sanitizzazione, poi `dangerouslySetInnerHTML` (`Article.tsx:44-46,166-167`).
    È la **difesa XSS-stored a render-time** lato client → **C6** (Editor/sanitizzazione). Qui solo
    notato che il bridge consuma `getArticleBySlug` e passa `content` grezzo al sanitizer.
  - **`ArticleEditor.tsx`** monta Tiptap (vedi import `@tiptap/*` in `package.json`) → **C6**. Qui
    ispezionato **solo** il ramo upload (bridge `uploadImage`), non l'editor.
  - **`useAudioPlayer.ts`** (player radio live) e **`Player.tsx`/`Visualizer.tsx`** → dominio media/streaming,
    fuori dall'ambito C3 (non è il ponte API↔contenuti). Non ispezionati.
  - **`SEO.tsx`** (`News.tsx:6`, `Article.tsx:6`) → **C7** (SEO/meta lato client). Non ispezionato.
- **Da verificare (C9):** `subscribeNewsletter` (`api.ts:151-156`) invia il body **senza** `Content-Type` —
  controllare in `newsletter.php` se legge `php://input` grezzo (altrimenti `$_POST` sarebbe vuoto).
- **Da verificare (C1/build):** non c'è `localhost:8888` né variabile d'ambiente per la base URL; in
  dev il same-origin è garantito da un proxy Vite? Controllare `vite.config.ts` (fuori ambito C3).
- **Conferma di coerenza con SR-C2:** l'assenza di `credentials:'include'` lato client è la controparte
  esatta dell'assenza di `Access-Control-Allow-Credentials` lato server (SR-C2 §4): l'auth è
  **de-facto same-origin** su entrambi i lati. Nessuna credenziale/segreto presente nel client (corretto).
- Versione del sito al momento della mappatura: **2.9.13** (`package.json`, coerente con SR-C1/SR-C2).
