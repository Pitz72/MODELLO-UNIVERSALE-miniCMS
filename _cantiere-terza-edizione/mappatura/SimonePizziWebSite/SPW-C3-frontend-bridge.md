# Mappatura — SimonePizziWebSite — C3: Frontend Bridge & State

> **Stato:** COMPLETATO
> **Sessione:** 3 · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `SimonePizziWebSite/`)
> - `src/api.ts` (client HTTP unico: `API_URL`, `fetchConfig`, oggetto `api` con ~60 metodi)
> - `src/loaders.ts` (data layer react-router: loader pubblici + admin + route guard `adminAuthLoader`)
> - `src/App.tsx` (router, code-splitting, error boundary, layout, Suspense/HydrateFallback)
> - `src/index.tsx` (mount `createRoot` + `StrictMode`)
> - `src/hooks/useFetchArticles.ts` (stato locale: paginazione, load-more, dedup)
> - `src/hooks/useCategories.ts` (stato locale: fallback ottimistico navigazione)
> - `src/utils/mappers.ts` (normalizzazione record DB → `PortfolioItem`)
> - `src/pages/admin/Login.tsx` (form login, redirect post-auth)
> - `src/pages/admin/AdminLayout.tsx` (logout, shell admin)
> - `src/components/admin/NavigationBlocker.tsx` (guardia "modifiche non salvate")
> - `public/api/auth.php:41-47` (contratto risposta `action=check`, letto come consumatore)

## 1. Cosa fa (sintesi narrativa)

C3 è il **ponte client↔server**: il punto in cui la SPA React parla con gli endpoint PHP mappati in
C1/C2/C4. Non c'è libreria di data-fetching (niente React Query, niente Axios, niente Redux): tutto
poggia su tre pilastri nativi/react-router.

1. **Un solo modulo client** — `src/api.ts` esporta un oggetto `api` con un metodo per ogni azione
   (login, getArticles, createCategory, uploadMedia, toggleReaction…). Ogni metodo è un wrapper
   sottile attorno a `fetch`, con una `fetchConfig` condivisa che porta `credentials: 'include'`
   (per propagare il cookie di sessione PHP) e gli header JSON. La base URL si auto-commuta:
   `/api` in produzione (same-origin), `http://localhost:8888/api` in sviluppo (`api.ts:2`).

2. **Il data layer è react-router, non lo stato globale** — `src/loaders.ts` contiene i `loader`
   che la `createBrowserRouter` di `App.tsx` associa a ogni rotta. I dati arrivano alla pagina
   *prima* del render (pattern "render-as-you-fetch"); le pagine leggono con `useLoaderData()`.
   Non esiste store globale: lo stato condiviso è quello che il router tiene per rotta.

3. **La protezione delle rotte admin è un loader** — `adminAuthLoader` (`loaders.ts:10-20`) chiama
   `api.checkSession()` e, se la sessione manca o l'API risponde `401`, fa `redirect('/admin/login')`.
   È la versione client del gate `Auth::check()` di C2: una guardia dichiarativa, montata una volta
   sulla rotta padre `/admin` e quindi valida per tutte le figlie.

Lo stato locale residuo vive in due hook (`useFetchArticles`, `useCategories`) per i casi in cui il
loader non basta: paginazione incrementale lato client e navigazione con fallback ottimistico.

## 2. Pattern miniCMS rilevanti

- **Pattern "Double Read" del payload** (`loaders.ts:30-31,69`, `useFetchArticles.ts:32-33`,
  `adminNewsletterLoader` `loaders.ts:166`): gli endpoint PHP rispondono **a volte con un array nudo,
  a volte con un oggetto paginato** `{ data: [...], total: N }`. Il client si difende leggendo
  entrambe le forme con `const data = Array.isArray(res) ? res : res.data;`. È il punto di sutura tra
  un'API che è cresciuta in modo incrementale e un frontend che non vuole rompersi: invece di
  versionare il contratto, lo si "legge due volte". Lente fondamentale per il libro.
- **Client come oggetto-namespace, non come classe** (`api.ts:14`): un singolo `export const api`
  con metodi raggruppati per dominio via commenti (`// --- ARTICLES ---`, `// --- MEDIA ---`). Niente
  istanze, niente DI: import diretto ovunque (`import { api } from './api'`).
- **Cookie di sessione propagato per default** (`api.ts:5-12`): `credentials: 'include'` su *ogni*
  chiamata è la controparte client del modello session-based di C2 (`HttpOnly`/`SameSite=Strict`).
  Same-origin in prod → niente CORS; in dev serve `Access-Control-Allow-Credentials` (commento esplicito
  `api.ts:6`). Ponte diretto a C2 (same-origin, CSP `connect-src 'self'`).
- **Loader come "controller" del thin stack lato client** (`loaders.ts`): la logica di orchestrazione
  (fetch in parallelo con `Promise.all`, filtri, ordinamenti, slice "ultimi 4") sta nei loader, non nei
  componenti. Es. `portfolioLoader:24-43` carica articoli+progetti insieme e pre-elabora.
- **Route guard dichiarativa = `Auth::check()` lato client** (`loaders.ts:10-20`): un loader che
  redirige. Doppio gate (client per UX immediata + server per sicurezza reale): il redirect è UX, la
  vera difesa resta `Auth::check()` di C2 sugli endpoint.
- **Fallback ottimistico per il first paint** (`useCategories.ts:7-17`): la navigazione parte con
  `DEFAULT_CATEGORIES` hardcoded e si aggiorna quando `getNavigation()` risponde; su errore resta il
  default. Le rotte categoria sono renderizzabili a freddo, senza attesa.
- **Mapper DB→UI centralizzato e difensivo** (`utils/mappers.ts`): converte il record grezzo PHP in
  `PortfolioItem`, assorbendo le incoerenze di tipo del thin stack (es. `is_featured === 1 || === true`,
  `tags` che può essere array *o* stringa CSV *o* assente → `parseTags`).
- **Degradazione graziosa vs errore propagato** (due strategie esplicite in `api.ts`): le letture
  "non critiche" tornano un default invece di lanciare (`getReactions:512-520`,
  `getArticleAnalytics:333-341`); le scritture e le letture critiche **lanciano** `Error` con messaggio
  parlante (`if (!res.ok) throw new Error(...)`). Gli analytics sono **fire-and-forget**: `trackView`/
  `trackClick` (`api.ts:311-327`) inghiottono ogni errore per non bloccare l'UI.
- **Code splitting per rotta** (`App.tsx:18-37`): tutto l'admin e le pagine secondarie sono
  `React.lazy` + `Suspense`, così il bundle pubblico non porta il peso del pannello.

## 3. Codice chiave (stralci con origine)

**Base URL auto-commutante + config condivisa col cookie** — `src/api.ts:1-12`:

```ts
export const API_URL = import.meta.env.PROD ? '/api' : 'http://localhost:8888/api';

const fetchConfig: RequestInit = {
    credentials: 'include',  // propaga il cookie di sessione PHP (same-origin in prod)
    headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' }
};
```

**Il pattern "Double Read" del payload** — `src/loaders.ts:30-31` (identico in `useFetchArticles.ts:32`):

```ts
// l'endpoint può rispondere con array nudo OPPURE { data, total }
const articlesData = Array.isArray(articlesRes) ? articlesRes : articlesRes.data;
const projectsData = Array.isArray(projectsRes) ? projectsRes : projectsRes.data;
```

**Route guard come loader (gate client di C2)** — `src/loaders.ts:10-20`:

```ts
export const adminAuthLoader = async () => {
    try {
        const session = await api.checkSession();
        if (!session || !session.user) {
            return redirect('/admin/login');
        }
        return session;
    } catch {
        return redirect('/admin/login');
    }
};
```

> **Nota di contratto (consumatore di C2):** `auth.php:41-47` per `action=check` risponde
> `{ status:'success', user: <username> }` (una **stringa**, non un oggetto utente) se loggato, o
> `401 {status:'error'}` altrimenti. Il loader testa `!session.user`: regge perché lo username è
> truthy. Asimmetria minore di naming (`user` = stringa) da tenere a mente.

**Loader come orchestratore: fetch parallelo + pre-elaborazione** — `src/loaders.ts:24-43`:

```ts
export const portfolioLoader = async () => {
    const [articlesRes, projectsRes] = await Promise.all([
        api.getArticles({ limit: 10 }), api.getProjects()
    ]);
    const projectsData = Array.isArray(projectsRes) ? projectsRes : projectsRes.data;
    const recentProjects = projectsData
        .filter((p: any) => p.is_visible === 1 || p.is_visible === true)
        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        .slice(0, 4);
    return { articles: articlesData.map(mapArticleToPortfolioItem),
             projects: recentProjects.map(mapProjectToPortfolioItem) };
};
```

**Router a due alberi (`/admin` protetto, `/` pubblico) con guard + boundary** — `src/App.tsx:230-278`:

```tsx
{ path: '/admin', errorElement: <AdminErrorBoundary />, children: [
    { path: 'login', element: <Login /> },                 // pubbliche: niente loader
    { path: 'recovery', element: <RecoveryRequest /> },
    { path: 'reset-password/:token', element: <ResetPassword /> },
    { path: '', element: <AdminLayout />, loader: adminAuthLoader,  // GUARD qui
      HydrateFallback: Loader, children: [ /* dashboard, articles, media... */ ] }
] },
{ path: '/', element: <PublicLayout />, errorElement: <RootBoundary />, children: [ ... ] }
```

**404 "vero" sollevato dal loader → intercettato dal boundary** — `src/loaders.ts:65-67` +
`src/App.tsx:101-109`:

```ts
if (!category) throw new Response("Categoria non trovata", { status: 404 });
```
```tsx
const RootBoundary = () => {
  const error = useRouteError();
  if (isRouteErrorResponse(error) && error.status === 404) { /* pagina 404 brandizzata */ }
  // ...altrimenti "Errore di Sistema" con bottone "Riavvia Moduli" (reload)
};
```

**Upload: due strategie (fetch FormData + XHR con progress)** — `src/api.ts:438-509`:

```ts
// FormData: si RIMUOVE Content-Type da fetchConfig, altrimenti si rompe il boundary multipart
const { headers, ...restConfig } = fetchConfig;
const res = await fetch(`${API_URL}/upload.php`, { ...restConfig, method: 'POST',
    body: formData, headers: { 'Accept': 'application/json' } });
// ...e in alternativa XMLHttpRequest con xhr.upload.onprogress per la barra di avanzamento
```

**Hook di paginazione incrementale con dedup** — `src/hooks/useFetchArticles.ts:32-49`:

```ts
const data = Array.isArray(res) ? res : res.data;
const total = !Array.isArray(res) && res.total !== undefined ? res.total : data.length;
const mappedItems = data.map(mapArticleToPortfolioItem);
if (isLoadMore) {
    setItems(prev => {
        const existingIds = new Set(prev.map(p => p.id));
        const newUnique = mappedItems.filter(i => !existingIds.has(i.id)); // dedup
        const merged = [...prev, ...newUnique];
        setHasMore(merged.length < total);                                  // calcolo non-stale
        return merged;
    });
}
```

## 4. Problemi riscontrati & soluzioni

- **Messaggi d'errore semantici del backend persi nel login (GOLD).** C2 confeziona stati e testi
  precisi (`429` "Too many failed login attempts. Try again in 15 minutes.", `401` "Credenziali non
  valide"). Ma `api.login` (`api.ts:22`) fa `if (!res.ok) throw new Error('Login fallito')`:
  **scarta** il corpo della risposta e sovrascrive con un messaggio generico. `Login.tsx:22-24`
  mostra `err.message` → l'utente vede sempre "Login fallito" anche quando è rate-limited. Per
  contro `requestRecovery`/`resetPassword` (`api.ts:48-49,59`) leggono `result.message` **prima** di
  lanciare e preservano il testo del server. → Incoerenza di propagazione errori: il lavoro di UX
  fatto in C2 (§5 "stati HTTP semanticamente corretti") è vanificato lato client per il login.
  Lezione per il libro: **il client deve leggere il body anche sui rami d'errore**, non solo `res.ok`.
- **Niente gestione `401` mid-sessione sulle mutazioni.** Il guard (`adminAuthLoader`) scatta solo
  alla *navigazione* tra rotte. Se la sessione scade mentre l'admin sta editando (es. dopo un reset
  password → `session_version` invalidata da C2), un salvataggio chiama `updateArticle`, l'endpoint
  risponde `401`, e il client lancia il messaggio generico "Errore aggiornamento articolo" senza
  redirigere al login. L'utente resta su una pagina "morta". → Manca un interceptor centralizzato che
  riconosca `res.status === 401` e forzi il redirect. Candidato a box "gestire la scadenza sessione
  nel thin stack" (ponte a `session_version` di C2).
- **Gestione errori per-chiamata duplicata (~50 volte).** Ogni metodo di `api.ts` ripete
  `if (!res.ok) throw new Error('...')`. Funziona ed è leggibile, ma è un wrapper `fetch` copiato:
  un helper unico (`request(path, opts)`) centralizzerebbe Double Read, header, e la gestione `401`
  del punto sopra. → Box "quando il thin stack chiede un piccolo strato di astrazione".
- **`#/` residuo in un'app BrowserRouter.** `Login.tsx:97` usa `<a href="#/">` per "Torna al sito
  pubblico": eredità di una vecchia configurazione HashRouter, oggi sotto `createBrowserRouter` non
  naviga (imposta solo l'hash). `AdminLayout.tsx:68` usa invece `/` correttamente. Bug cosmetico minore.
- **`total` assente → `hasMore` può sbagliare.** Se l'endpoint torna un array nudo (niente `total`),
  `useFetchArticles.ts:33` usa `data.length` come totale: `hasMore` diventa `false` anche quando
  esisterebbero altre pagine. È una conseguenza diretta del Double Read su un contratto non garantito.

## 5. Estetica / UX (moderna ma funzionale)

- **Error boundary brandizzati, non schermate bianche** (`App.tsx:98-143`): `RootBoundary` distingue
  `404` ("La pagina… è svanita nel vuoto digitale", CTA "Torna in superficie") da errore generico
  ("Errore di Sistema", bottone "Riavvia Moduli" = `window.location.reload()`), con palette coerente
  (`#05080a`, `dis-green`). `AdminErrorBoundary` è la variante pannello.
- **Transizioni di rotta con `framer-motion`** (`App.tsx:202-213`, `AdminLayout.tsx:76-88`): fade+slide
  su `AnimatePresence` keyed sul pathname; `Suspense` con `<Loader />` come fallback durante il lazy load.
- **`HydrateFallback: Loader`** sulle rotte con loader (`App.tsx:242,266`): niente flash di contenuto
  vuoto durante l'idratazione dei dati.
- **Guardia "modifiche non salvate"** (`NavigationBlocker.tsx` + `useBlocker`): modale che intercetta
  l'abbandono di un editor con dati `isDirty`, con scelte "Rimani Qui"/"Esci". UX premium per evitare
  perdite di lavoro.
- **Fallback ottimistico** (`useCategories`): la UI non "lampeggia" in attesa della navigazione perché
  parte già popolata.
- **Comando-K per la ricerca** (`App.tsx:148-157`): scorciatoia globale `Ctrl/Cmd+K` apre `SearchModal`.

## 6. Differenze rispetto agli altri siti

(Da consolidare in FASE 2. Ipotesi/puntatori:)
- **SitoRuntime (SR-C3)**: la ROADMAP segna per SR un C2 "Security **+ CORS**". Probabile che lì
  `fetchConfig`/`API_URL` debbano gestire una **CORS reale cross-dominio** (più origini), mentre qui
  resta tutto same-origin con `credentials:'include'` innocuo. Da confrontare il client HTTP.
- Verificare se gli altri siti adottano lo stesso **Double Read** (array vs `{data,total}`): è
  l'indizio di una stessa storia evolutiva delle API (paginazione aggiunta dopo).
- Verificare se altrove esiste un **interceptor 401 centralizzato** (qui assente) o lo stesso pattern
  "un metodo per endpoint" in un unico oggetto `api`.
- DISINTELLIGENZA/FDCA (SQLite, festival) avranno verosimilmente un bridge più piccolo (meno endpoint,
  focus su voto/iscrizione): buon termine di paragone "minimo" del pattern.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **Pattern "Double Read"** (`Array.isArray(res) ? res : res.data`) | Cap. "Il ponte React↔PHP / contratti di payload elastici" (nuovo, alto valore) |
| Client come oggetto-namespace su `fetch` (niente Axios/React Query) | Cap. "Un client HTTP minimale nel thin stack" |
| `credentials:'include'` + base URL prod/dev: cookie di sessione lato client | Box "propagare la sessione PHP da React" (ponte C2) |
| Loader react-router come data layer / "controller" client | Cap. "Render-as-you-fetch senza librerie di stato" |
| **Route guard come loader** (`adminAuthLoader` redirect) = `Auth::check()` client | Cap. "Proteggere le rotte admin lato client" (ponte C2) |
| 404 reale via `throw new Response(404)` + `errorElement` brandizzati | Box "errori ed empty-state come parte della UX" |
| Degradazione graziosa vs errore propagato (reactions/analytics vs scritture) | Box "due strategie d'errore nello stesso client" |
| Upload: fetch FormData (no Content-Type) + XHR con progress | Cap. "Upload file dal client" (ponte C5) |
| **Messaggi d'errore del backend persi nel login** | Box problemi/soluzioni "leggere il body anche sugli errori" (alto valore) |
| **Niente interceptor 401 mid-sessione** | Box "gestire la scadenza di sessione" (ponte C2 `session_version`) |
| Fallback ottimistico (`useCategories`) per il first paint | Box "UI che parte popolata" |
| `NavigationBlocker`/`useBlocker`: guardia modifiche non salvate | Box "non perdere il lavoro dell'editor" (ponte C6/C12) |

## 8. Note / domande aperte

- **Puntatori ad altri cluster** (annotati qui, NON mappati in questa card):
  - I metodi di `api.ts` toccano endpoint di **C4** (articles/projects/categories/tags/navigation/
    search via param `q`), **C5** (upload/media), **C9** (subscribers/newsletter_send), **C11**
    (reactions/messages), **C12** (settings/backup/stats/analytics). Qui interessa **solo** come il
    client li chiama (firma, verbi HTTP, forma payload); la *logica server* è dei rispettivi cluster.
  - `RichTextEditor.tsx`/`MediaSelectorModal.tsx`/`SeoScorePanel.tsx`/`InternalLinkSelector.tsx` →
    **C6** (Editor). Qui non ispezionati: usano `api` ma sono UI di editing.
  - `SEO.tsx` + `react-helmet-async` (`App.tsx:5,282`) e `prerender*.js` → **C7** (SEO/Prerendering).
  - `mappers.ts` normalizza i record: la *forma* dei record (schema) è C1/C4; qui solo la conversione UI.
- **Da verificare (C4):** quali endpoint restituiscono array nudo e quali `{data,total}`? La mappa
  esatta del Double Read va completata leggendo `articles.php`/`projects.php`/`subscribers.php` lato
  server (lì si decide il contratto che il client legge "due volte").
- **Da verificare:** esiste un punto unico di logout-on-401? Oggi no (vedi §4). Possibile follow-up
  trasversale quando si mapperà SR-C3 per confronto.
- Nessuna credenziale/segreto presente lato client (corretto: `.env.local` contiene solo config di
  build; le chiamate vanno same-origin a `/api`).
- Versione del sito al momento della mappatura: **1.21.0** (coerente con SPW-C1/C2).
