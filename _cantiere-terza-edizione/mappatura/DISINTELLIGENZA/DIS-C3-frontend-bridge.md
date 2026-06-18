# Mappatura — DISINTELLIGENZA — C3: Frontend Bridge & State

> **Stato:** COMPLETATO · **(card aggiunta in FASE 1-bis: colmatura gap di copertura, 2026-06-18)**
> **Sessione:** 29 · **Data:** 2026-06-18 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `DISINTELLIGENZA/`)
> - `src/api.ts` (client unico oggetto-namespace su `fetch`, 386 righe)
> - `fix_api.cjs` / `fix_api.js` (root — **codemod** che ha INIETTATO l'error-handling in `api.ts`)
> - richiami: `AdminLayout.tsx:13-22` (guard-componente `checkAuth`, DIS-C12), `Dashboard.tsx`/`Registrations.tsx` (consumer in `useEffect`, DIS-C12)
> - confronto: `SPW-C3-frontend-bridge.md`, `SR-C3-frontend-bridge.md`

## 1. Cosa fa (sintesi narrativa)

C3 è il **ponte client↔server** di DISINTELLIGENZA: l'oggetto `api` in `src/api.ts` che la SPA usa per
parlare con gli endpoint PHP. Come SitoRuntime (SR-C3) è un **oggetto-namespace** (`export const api =
{ login, getNews, submitVote, … }`) di wrapper su `fetch`, non le funzioni per-risorsa di SPW. Ma ha
due tratti che lo rendono il bridge più "grezzo" e più interessante dei tre:

1. **Nessun CSRF, nessun `credentials:'include'`, base URL fissa `/api`** — la versione minima del
   bridge (più scarna ancora di SR, che almeno gestiva un token CSRF in memoria). L'auth è de-facto
   **same-origin** su entrambi i lati (il cookie di sessione parte perché stessa origine; DIS-C2).
2. **L'error-handling è stato INIETTATO da un codemod** (`fix_api.cjs`/`fix_api.js`): lo stesso blocco
   `if (!res.ok) { … res.clone().json() … }` è **copia-incollato in ~25 metodi**, con metodi
   "sfuggiti" allo strumento e perfino una riga duplicata. È la firma meccanica di una trasformazione
   automatica del codice — un caso di studio raro e prezioso (vedi §4, GOLD).

Non c'è "state layer": niente data-loader (≠ SPW), niente store globale, niente react-query. Lo stato
vive nei singoli componenti (`useState`+`useEffect`, come si vede in DIS-C12) e la guardia admin è il
**componente** `AdminLayout` che chiama `api.checkAuth()` al mount (DIS-C12) — il pattern di SR, non
il loader di SPW.

## 2. Pattern miniCMS rilevanti

- **Client oggetto-namespace su `fetch`** (`api.ts:3`): un unico `export const api` con ~30 metodi.
  Stessa forma di SR; diversa dalle funzioni separate di SPW. Ogni metodo: `fetch` → `if(!res.ok)` →
  `res.json()`.
- **Base URL FISSA `/api`, niente switch prod/dev** (`api.ts:1`, `const API_BASE = '/api'`): come SR,
  diverso da SPW (che commuta tra dominio di produzione e dev). Implica deploy same-origin.
- **Nessun `credentials:'include'`** in nessuna chiamata: l'autenticazione regge perché il cookie di
  sessione è same-origin (default `same-origin` di `fetch`). È la controparte client del "niente CORS"
  di DIS-C2 — auth same-origin su entrambi i lati. Identico a SR.
- **Nessun token CSRF** (≠ SR che aveva `let csrfToken` di modulo, ≠ SPW Origin/Referer): il client
  non invia alcun header di sicurezza sulle mutazioni. Conferma diretta di DIS-C2 (CSRF assente). È il
  bridge **più semplice** dei tre.
- **Contratto di risposta "busta zero" passato così com'è** (`return await res.json()`): il client
  **non normalizza** la forma (≠ Double Read di SPW, ≠ guardie `Array.isArray` di SR). Coerente con
  DIS-C4: gli endpoint ritornano array/oggetti nudi e il chiamante conosce la forma.
- **Compensazione "HTTP 200 con body d'errore" per-metodo** (`api.ts:341-343,369-372`): alcune azioni
  (newsletter `subscribe`/`send`) tornano `200` anche in errore con `{status:'error'}`; il client
  aggiunge a mano `if (data.status === 'error') throw new Error(data.message)`. Il client **rattoppa**
  l'incoerenza del backend (che non usa sempre i codici HTTP) caso per caso.
- **Upload via `FormData` senza progress** (`api.ts:248-259`, `uploadFile`): `fetch` con `FormData`,
  nessun `XHR`/`onprogress` (come SR, ≠ la barra di avanzamento XHR di SPW). Il parametro `type`
  (image/audio/audio_participant/audio_podcast) pilota lo smistamento server di DIS-C5.
- **`checkAuth` che ingoia gli errori → `null`** (`api.ts:17-26`): `try/catch` che ritorna `null` su
  qualunque fallimento. È la dipendenza su cui si regge il guard-componente di DIS-C12 (`if(!u)
  navigate(login)`).
- **`logout` con reload totale** (`api.ts:13-16`): `fetch(logout)` poi `window.location.reload()` —
  reset di stato brutale ma efficace (niente gestione fine dello stato di sessione client).

## 3. Codice chiave (stralci con origine)

**Il bridge minimo: base fissa, niente credentials/CSRF** — `api.ts:1-22`:

```ts
const API_BASE = '/api';                                 // fisso, no prod/dev (come SR)
export const api = {
    login: async (username, password) => {
        const res = await fetch(`${API_BASE}/auth.php?action=login`, {
            method: 'POST', body: JSON.stringify({ username, password })   // niente credentials:'include', niente X-CSRF
        });
        if (!res.ok) throw new Error('Login failed');     // ← metodo "sfuggito" al codemod: messaggio generico (perde il backend)
        return await res.json();
    },
    checkAuth: async () => {
        try { const res = await fetch(`${API_BASE}/auth.php?action=check_auth`);
              if (!res.ok) return null; return (await res.json()).user; }
        catch { return null; }                            // su cui si regge il guard-componente (DIS-C12)
    },
```

**Il blocco INIETTATO dal codemod, copia-incollato in ~25 metodi** — es. `api.ts:78-86` (gemello identico in getUsers, createNews, getStats, getSettings, …):

```ts
if (!res.ok) {
    let err = 'Errore imprevisto dal server';
    try { const j = await res.clone().json(); err = j.message || err; } catch(e) {}
    throw new Error(err);
}
return await res.json();
```

**La firma del codemod: una riga DUPLICATA + uno stile d'errore divergente "sfuggito"** — `api.ts:303-313,369-372`:

```ts
// submitVote: error-handling SCRITTO A MANO, diverso dal blocco del codemod
submitVote: async (votes) => {
    const res = await fetch(`${API_BASE}/votes.php`, { method:'POST', body: JSON.stringify({ votes }) });
    if (!res.ok) { const err = await res.json(); throw new Error(err.message || 'Errore durante il voto'); }
    return await res.json();
},
// sendNewsletter: riga duplicata (artefatto di copia-incolla)
if (json.status === 'error') throw new Error(json.message);
if (json.status === 'error') throw new Error(json.message);   // ← duplicata
```

**Il codemod che ha prodotto tutto questo** — `fix_api.cjs:4-23` (regex su `const res = await fetch(...)` + append del blocco):

```js
const regex = /(const res = await fetch\([\s\S]*?\);)/g;
code = code.replace(regex, (match, p1, offset, string) => {
    const nextLine = string.substring(offset + p1.length).trim().split('\n')[0];
    if (nextLine.startsWith('if (!res.ok)')) return match;   // salta chi ce l'ha già → spiega i metodi "sfuggiti"
    const check = `\n        if (!res.ok) { let err = 'Errore imprevisto dal server'; try { const j = await res.clone().json(); err = j.message || err; } catch(e) {} throw new Error(err); }`;
    return match + check;
});
```

## 4. Problemi riscontrati & soluzioni

- **GOLD — l'error-handling è frutto di un CODEMOD, e si vede.** `fix_api.cjs`/`fix_api.js` (root)
  sono due script Node quasi identici che fanno una **regex-replace** su `src/api.ts`: trovano ogni
  `const res = await fetch(...)` e, se non c'è già un `if(!res.ok)`, vi **appendono** il blocco di
  gestione errore. Le prove nel codice: (1) lo **stesso identico blocco** ripetuto verbatim in ~25
  metodi; (2) **metodi "sfuggiti"** che avevano già un `if(!res.ok)` con messaggio generico (`login`
  "Login failed", `getNewsDetail` "Not found", `uploadFile` "Upload failed", `submitVote` con stile
  proprio) → il codemod li ha saltati, lasciando il bridge **disomogeneo**; (3) una **riga duplicata**
  (`api.ts:370-371`) = artefatto di una seconda passata. È un caso reale e didattico di
  "trasformazione automatica del codice sorgente" nel thin stack — e dei suoi effetti collaterali
  (incoerenza, duplicazioni). → Box "il codemod che rattoppa il client: pro e tracce" (alto valore,
  unico tra i siti).
- **GOLD — "messaggio backend perso" anche qui, ma sui metodi sfuggiti.** Come SPW (nel client) e SR
  (nella UI del login), DIS perde il messaggio d'errore del server — ma in modo **frammentato**: i
  metodi coperti dal codemod lo preservano (`res.clone().json().message`), quelli sfuggiti no
  (`'Login failed'`, `'Not found'`, `'Upload failed'`). Quindi la qualità degli errori dipende da
  **quali metodi il codemod ha toccato**. → confluisce nel box cross-sito "il messaggio d'errore che
  si perde nel client".
- **GOLD — il client rattoppa l'incoerenza HTTP del backend.** Newsletter `subscribe`/`send`
  ritornano `200` anche in errore con `{status:'error'}` (DIS-C9); il client aggiunge a mano il check
  `data.status === 'error' → throw` (`api.ts:341-343,369-372`). È la conseguenza di un backend che non
  usa sempre i codici HTTP: il bridge se ne fa carico **per-metodo**, non con un interceptor unico. →
  Box "quando il 200 nasconde un errore: rattoppare lato client".
- **Niente interceptor 401/403, niente refresh.** Come SPW/SR, nessuna gestione centralizzata della
  sessione scaduta a metà uso: ogni chiamata gestisce da sé. Il guard-componente (DIS-C12) copre solo
  il primo accesso all'area admin, non la scadenza in corso. → nota (gap comune ai tre).
- **Commenti "ragionamento ad alta voce" nel codice** (`api.ts:154-164`, `submitParticipant`): un
  blocco di commenti dove l'autore discute con sé stesso FormData vs JSON ("Wait, if we use
  FormData…", "My backend participants.php handles $_POST directly"). Stesso tell di codice
  AI-assistito già visto in `init_db.php` ("in repl", DIS-C1) e `participants.php`. → nota.
- **Upload senza feedback di progresso** (`api.ts:248-259`): `fetch`+`FormData`, nessun `XHR
  onprogress`. Su un audio di partecipante grande l'utente non vede avanzamento (≠ barra XHR di SPW).
  Limite UX noto (gemello SR). → nota.

## 5. Estetica / UX (moderna ma funzionale)

- **Bridge prevedibile**: ogni metodo è una funzione `async` che ritorna `res.json()` o lancia un
  `Error` con messaggio — i componenti (DIS-C12) li usano in `try/catch`/`useEffect` e mostrano
  `alert`/stato locale. Contratto semplice da consumare.
- **`logout` reload-and-forget** (`api.ts:15`): nessuno stato di sessione client da ripulire — la
  pagina si ricarica e riparte pulita. UX brutale ma senza bug di stato residuo.
- **Errori "umani" dove il codemod arriva**: `j.message || 'Errore imprevisto dal server'` mostra il
  messaggio italiano del backend (es. "Hai già votato da questo IP oggi.", DIS-C2) quando disponibile.

## 6. Differenze rispetto agli altri siti

Confronto a **TRE** sul bridge client.

| Aspetto | SimonePizziWebSite (SPW-C3) | SitoRuntime (SR-C3) | **DISINTELLIGENZA (questa card)** |
|---|---|---|---|
| **Forma client** | funzioni per-risorsa | oggetto-namespace | **oggetto-namespace** (come SR) |
| **Base URL** | switch prod/dev | fissa `/api` | **fissa `/api`** (come SR) |
| **`credentials:'include'`** | sì | no (same-origin) | **no** (same-origin) |
| **CSRF lato client** | Origin/Referer (server) | **token in-memory** `X-CSRF-Token` | **nessuno** |
| **Contratto risposte** | Double Read (`{data,total}` vs array) | per-endpoint + `Array.isArray` | **"busta zero" passata grezza** |
| **Error handling** | boundary scritti | `if(!res.ok)` + body preservato | **iniettato da CODEMOD** (uneven, duplicati, sfuggiti) |
| **Messaggio backend** | perso nel client (429) | perso nella UI (LoginForm) | **perso solo sui metodi sfuggiti** al codemod |
| **State layer** | `loaders.ts` (data-router) | guard-componente | **guard-componente** (AdminLayout, DIS-C12) |
| **Upload progress** | XHR onprogress | FormData, no progress | **FormData, no progress** (come SR) |
| **200-con-errore** | n/a | n/a | **rattoppato per-metodo** (newsletter) |

**Sintesi.** DIS-C3 è il **gemello scarnificato di SR-C3** (oggetto-namespace, base fissa, no
credentials, guard-componente, upload senza progress) ma **ancora più minimale** (zero CSRF) e con un
tratto unico: l'error-handling **generato da un codemod** (`fix_api`), che lascia tracce visibili —
ripetizione, metodi sfuggiti, una riga duplicata. Dove SPW investe nello state layer (loaders) e SR
nel token CSRF, DIS investe… in uno script che rattoppa il client a posteriori. È il caso di studio
del bridge "thin" portato al limite, e della **manutenzione del client via trasformazione automatica**.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **Il codemod che rattoppa il client** (`fix_api`): regex-replace su `api.ts`, pro e tracce | Box problemi/soluzioni "trasformare il sorgente in massa" (alto valore, unico) |
| **Bridge oggetto-namespace minimo** (no credentials, no CSRF, base fissa) | confluisce nel cap. "Il client API nel thin stack": il gradino DIS |
| **"Busta zero" lato client**: ritornare il json grezzo | Box "quando il client NON normalizza" (ponte DIS-C4, contrasto Double Read SPW) |
| **200 con body d'errore rattoppato per-metodo** | Box "quando il codice HTTP non basta" |
| **Il messaggio d'errore che si perde** (qui in modo frammentato) | confluisce nel box cross-sito sugli errori |
| **Guard-componente vs data-loader** | confluisce nel box "proteggere l'area admin di una SPA" (ponte DIS-C12) |

## 8. Note / domande aperte

- **Puntatori ad altri cluster:**
  - Il **guard-componente** `AdminLayout` (checkAuth on mount) e i pannelli che consumano `api` →
    **C12** (già mappato): C3 è la superficie, C12 l'orchestrazione.
  - `uploadFile` (type image/audio/...) → **C5** (già mappato): la catena upload pubblico passa di qui.
  - Assenza di CSRF/credentials → **C2** (già mappato): C3 ne è la controparte client.
  - Forma "busta zero" delle risposte → **C4** (già mappato): C3 la passa senza toccarla.
  - `submitVote`/`getSettings`/`getStats`/`updateParticipant*` → **C10** (già mappato): C3 è il loro
    canale.
- **Conferma (chiude il puntatore DIS-C1):** `fix_api.cjs`/`fix_api.js` sono **build-tooling che
  modifica `api.ts`** (codemod error-handling), non bootstrap — come anticipato in DIS-C1. Qui ne è
  documentato l'effetto reale sul client.
- **Da valutare (qualità):** la duplicazione del codemod e i metodi sfuggiti sono **debito tecnico
  reale** del sito sorgente (non un difetto della mappatura). Citabile come esempio, non da correggere
  (sola lettura).
- Versione del sito: **0.5.x** (`package.json`).
