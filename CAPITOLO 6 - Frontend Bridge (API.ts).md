# CAPITOLO 6: Frontend Bridge (API.ts) (Terza Edizione)

React parla con PHP attraverso un solo punto. Non chiamate `fetch` sparse per i componenti, ma un oggetto `api` che le raccoglie tutte: un metodo per azione (`login`, `getNews`, `uploadImage`, `submitVote`), raggruppati per dominio con qualche commento, importati ovunque con `import { api }`. Niente Axios, niente React Query, niente Redux, nessuno store globale. È la versione thin-stack del data access layer: una facciata piatta sopra `fetch`, coerente con la filosofia del modello (CAP 4), meno dipendenze possibile.

Sotto quella superficie comune c'è un problema condiviso, ed è la vera lente del capitolo: l'API PHP non ha un contratto uniforme. Gli endpoint, cresciuti per accrescimento, rispondono con buste diverse (un array nudo, oppure `{ data, total }`, oppure `{ success, … }`), e a volte con un HTTP 200 anche quando le cose sono andate male. Nessuno dei tre siti versiona quel contratto. Ognuno si limita a leggere in modo difensivo quello che arriva, e il modo in cui se ne fa carico è ciò che li distingue.

Le tre risposte si leggono bene come una scala di *investimento*. SimonePizziWebSite investe nello state layer: i loader di react-router come data layer, e il «Double Read» del payload. SitoRuntime investe nella sicurezza del client: un token CSRF tenuto in una variabile di modulo. DISINTELLIGENZA investe in un codemod, uno script che rattoppa il client a posteriori. Tre modi di tenere insieme React e PHP quando nessuno dei due lati ha un contratto stabile. E come nei capitoli precedenti, l'ordine d'investimento non coincide con la solidità: chi spende di più non è chi sbaglia di meno.

Il quarto sito, FDCA, non entra qui. Il fork ha riscritto e ridotto il frontend a vetrina pubblica, e non ha alcun `api.ts` né `fetch` verso `/api`: dove sul backend era byte-identico a DIS, sul ponte è semplicemente assente. Un guscio scollegato dal CMS, che vive nel capitolo dedicato al forking, non in questo.

---

## 1. Un solo client, sottile su `fetch`

Prima delle differenze, i tratti che i tre siti hanno in comune. Il client è un oggetto-namespace, non una classe: nessuna istanza, nessuna dependency injection, si importa e si chiama. Non c'è libreria di data-fetching: lo stato condiviso o vive nel router (SPW) o è `useState` locale ai componenti (SR, DIS), e il «fetching» è `fetch` nativo. Dove possibile i metodi sono tipizzati (`NewsArticle[]`, `UserRole`), così il chiamante sa cosa aspettarsi, ma il contratto vero lo detta il PHP, e non sempre combacia con i tipi dichiarati.

L'autenticazione, infine, viaggia col cookie di sessione `HttpOnly` (CAP 10): il client non porta token di bearer né stato d'autenticazione persistente. Da qui discende un dettaglio che divide subito i tre siti, la base URL e il cookie.

```ts
// SPW api.ts:1-12 — base URL che commuta prod/dev, config condivisa col cookie
export const API_URL = import.meta.env.PROD ? '/api' : 'http://localhost:8888/api';

const fetchConfig: RequestInit = {
    credentials: 'include',  // propaga il cookie di sessione PHP (in dev attraversa localhost:8888)
    headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' }
};
```

```ts
// SR api.ts:4 — base fissa, nessuno switch: sempre same-origin
const API_BASE = '/api';     // niente localhost:8888, e — punto cruciale — niente credentials:'include'
```

> [!NOTE]
> **`credentials:'include'`: quando serve e quando è rumore**
> SPW mette `credentials:'include'` su ogni chiamata, e deve farlo: in sviluppo il frontend e il backend stanno su due origini diverse (`localhost:8888`), e senza quell'opzione il cookie di sessione non partirebbe. SR e DIS non lo mettono mai, perché sviluppano e pubblicano same-origin, dove il cookie viaggia da solo con la policy di default di `fetch`. C'è una simmetria esatta col lato server (CAP 10): la CORS di SR non emette `Access-Control-Allow-Credentials`, quindi l'autenticazione è di fatto same-origin su entrambi i lati, e lì `credentials:'include'` sarebbe una riga che non fa nulla. La regola: quell'opzione serve quando client e API stanno su origini diverse; same-origin, è rumore.

---

## 2. Il contratto non è uniforme: tre modi di leggere il payload

È il cuore del capitolo. Gli endpoint rispondono con buste diverse, e il client deve sopravvivere a questa incoerenza. Le tre tecniche sono il GOLD del cluster.

SPW vive il caso più ostico: *lo stesso* endpoint a volte risponde con un array nudo, a volte con un oggetto paginato `{ data, total }`. La risposta è leggere il payload in due forme possibili, ed è questo, e soltanto questo, il pattern che il modello chiama «Double Read».

```ts
// SPW loaders.ts:30-31 — lo stesso endpoint a volte è array, a volte { data, total }
const articlesData = Array.isArray(articlesRes) ? articlesRes : articlesRes.data;
const projectsData = Array.isArray(projectsRes) ? projectsRes : projectsRes.data;
```

SR non ha lo stesso endpoint ambiguo, ha un mosaico: ogni endpoint ha la *sua* busta, e il client la conosce a memoria. Su due di essi, però, dove la risposta è un array nudo in caso di successo ma un oggetto `{ success:false, error }` in caso di errore, mette una guardia di tipo.

```ts
// SR — ogni endpoint ha la sua busta, letta per forma nota:
//   news.php → { success, data, meta }      admin?action=list → { success, articles, total }
//   speakers.php / podcasts.php → ARRAY NUDO, oppure { success:false, error } su errore
if (Array.isArray(res)) setPodcasts(res);   // Podcasts.tsx:14 — guardia di tipo anti-errore
```

DIS sceglie la via opposta: non normalizza affatto. Ritorna il JSON così com'è («busta zero») e lascia che sia il chiamante a sapere com'è fatto.

```ts
// DIS api.ts — "busta zero": il client non tocca la forma, la passa grezza al chiamante
return await res.json();
```

> [!TIP]
> **Contratti elastici: Double Read, guardia di tipo, busta zero**
> Stessa radice, tre rimedi. Quando un'API cresce per accrescimento e nessuno versiona la forma delle risposte, il client deve decidere quanto lavoro fare al posto del contratto mancante. SPW legge lo stesso payload in due forme possibili (il «Double Read» vero: array nudo *o* `{ data, total }`). SR conosce la busta di ogni endpoint e, dove la forma è ambigua, mette una guardia `Array.isArray` che distingue il dato buono dall'errore. DIS non normalizza: ritorna il JSON com'è e si fida del chiamante. Nessuna delle tre è sbagliata; sono tre punti sulla scala di quanta incoerenza del server il client accetta di assorbire. Un avvertimento di terminologia: «Double Read» è *questo*, la lettura della forma del payload di successo. Non è il clonaggio della risposta per estrarne un messaggio d'errore, che è un'altra cosa e ha un'altra storia (il prossimo paragrafo).

---

## 3. Quando il backend ha torto: il 200 che mente e il messaggio perso

A volte il backend non collabora in due modi distinti. Il primo: risponde HTTP 200 anche su un fallimento logico, mettendo l'errore nel body. È il caso di alcuni endpoint di DIS (la newsletter), e il client lo rattoppa a mano, metodo per metodo.

```ts
// DIS api.ts:341-343 — alcuni endpoint tornano HTTP 200 anche in errore: rattoppo per-metodo
const data = await res.json();
if (data.status === 'error') throw new Error(data.message);   // non un interceptor unico
```

Attenzione all'attribuzione, perché è facile scambiarlo per una regola generale: questo è il pattern di DIS, non una prescrizione universale del modello. È la conseguenza di un backend che non usa sempre i codici HTTP, e il bridge se ne fa carico caso per caso. Il secondo modo in cui il backend non collabora è l'opposto: risponde con un errore preciso, e il client lo butta via. Per estrarre quel messaggio quando c'è, serve clonare la risposta.

```ts
// il blocco che ESTRAE il messaggio d'errore dal body (response cloning) — NON è il "Double Read"
if (!res.ok) {
    let err = 'Errore imprevisto dal server';
    try { const j = await res.clone().json(); err = j.message || err; } catch (e) {}
    throw new Error(err);
}
return await res.json();
```

In DIS questo blocco compare identico in venticinque metodi. Non perché qualcuno l'abbia scritto venticinque volte, ma perché l'ha iniettato uno script.

```js
// DIS fix_api.cjs:4-23 — regex-replace: trova ogni fetch e appende il blocco, se manca
const regex = /(const res = await fetch\([\s\S]*?\);)/g;
code = code.replace(regex, (match, p1, offset, string) => {
    const nextLine = string.substring(offset + p1.length).trim().split('\n')[0];
    if (nextLine.startsWith('if (!res.ok)')) return match;   // salta chi ce l'ha già → i metodi "sfuggiti"
    const check = `\n  if (!res.ok) { /* … res.clone().json() … */ throw new Error(err); }`;
    return match + check;
});
```

> [!WARNING]
> **Il codemod che rattoppa il client: potenza e tracce**
> DIS non ha scritto a mano la gestione degli errori del suo client: l'ha generata con un codemod. `fix_api.cjs` cerca ogni `const res = await fetch(...)` e, se non c'è già un `if (!res.ok)`, vi appende un blocco che clona la risposta ed estrae `message`. Funziona, e in pochi secondi copre l'intero file. Ma lascia tre impronte. La prima: lo stesso blocco identico, parola per parola, ovunque. La seconda: i metodi «sfuggiti», quelli che avevano già un loro `if (!res.ok)` con un messaggio generico (`login` con «Login failed», `uploadFile` con «Upload failed»), che lo script ha saltato lasciando il bridge disomogeneo. La terza: una riga duplicata, residuo di una seconda passata. È un caso reale di manutenzione del client per trasformazione automatica del sorgente, con i suoi vantaggi e i suoi effetti collaterali. Quel blocco è esattamente ciò che un manuale potrebbe vendere come «lo standard» della gestione errori: qui è il prodotto di una macchina, non di una scelta, ed è bene saperlo riconoscere.

Resta il problema più diffuso, e il più istruttivo perché comune a tutti e tre: il messaggio d'errore del backend che si perde. Il server (CAP 10) si è dato la pena di confezionare stati e testi precisi, un 429 con «Troppi tentativi, riprova tra quindici minuti». Il client lo getta, in tre punti diversi della catena.

```ts
// SPW api.ts:22 — il body d'errore (anche un 429 parlante) viene scartato qui, nel client
if (!res.ok) throw new Error('Login fallito');
```

```tsx
// SR LoginForm.tsx:18-25 — qui il body è preservato da api.login, ma la UI lo butta comunque
catch (err) { setError('Login fallito. Controlla le credenziali.'); }   // err.message ignorato
```

In SPW il messaggio si perde nel client, in SR nella UI, in DIS a macchia di leopardo (i metodi toccati dal codemod lo preservano, quelli sfuggiti no). Tre punti diversi, lo stesso esito: l'utente sotto rate-limit vede sempre «Login fallito» e mai il 429 che gli direbbe quanto aspettare.

> [!WARNING]
> **Leggere il body anche sui rami d'errore**
> `res.ok` dice *se* la richiesta è andata a buon fine, non *perché* è fallita; il perché sta nel body. Buttarlo via, come fanno tutti e tre i siti sul login, vanifica il lavoro fatto sul server per rendere parlanti gli errori, e lascia l'utente davanti a un messaggio inutile. La lezione è semplice e spesso ignorata: il body va letto anche, e soprattutto, quando la risposta non è ok. Dove farlo conta meno del farlo: l'importante è non sostituire un 429 «riprova tra quindici minuti» con un generico «errore».

---

## 4. Il token CSRF lato client

È l'investimento che distingue SitoRuntime, e il meccanismo più sofisticato del cluster. Il backend di SR (CAP 10) restituisce un `csrf_token` nel body di `login` e `check_auth`, e pretende l'header `X-CSRF-Token` su tutte le mutazioni. Il client gestisce l'handshake nel modo più minimale possibile: una variabile a livello di modulo.

```ts
// SR api.ts:6-10 — il token CSRF vive in una variabile di modulo, in memoria
let csrfToken = '';                          // non localStorage, non Context, non stato di componente
function csrfHeaders() { return csrfToken ? { 'X-CSRF-Token': csrfToken } : {}; }
```

```ts
// SR api.ts:31,37 — catturato dal body di login/check_auth, rispedito solo sulle mutazioni
if (data.csrf_token) csrfToken = data.csrf_token;
// ...e su ogni POST/DELETE:  headers: { 'Content-Type': 'application/json', ...csrfHeaders() }
```

Il token viene catturato all'login, reiniettato sulle scritture, azzerato al logout. SPW non ha niente di tutto questo (gli basta il controllo di Origin/Referer lato server), e DIS non ha CSRF affatto: è una soluzione tutta di SR. Ma tenerlo in una variabile di modulo ha un prezzo nascosto.

> [!WARNING]
> **Il token CSRF e il reload: una garanzia accoppiata**
> La variabile vive in memoria: a un ricaricamento della pagina sparisce, e la prima mutazione successiva partirebbe senza `X-CSRF-Token`, prendendo un 403. Il sistema regge solo perché il componente admin rifà `checkAuth()` ogni volta che si monta, e quella chiamata ri-restituisce il token. È una dipendenza reale ma non dichiarata da nessuna parte: se domani una pagina admin montasse un editor senza passare da quel `checkAuth`, le scritture fallirebbero in modo opaco, con un 403 che a video è indistinguibile da un errore di salvataggio. Se un token deve sopravvivere al reload, va messo dove sopravvive davvero (un `sessionStorage`, o un handshake esplicito a ogni avvio), non lasciato a un effetto collaterale del montaggio di un componente.

---

## 5. Proteggere l'area admin: loader o componente

La protezione delle rotte riservate lato client è due scuole per la stessa cosa. SPW usa una guardia dichiarativa: un loader montato sulla rotta padre `/admin`, che verifica la sessione prima che la pagina si monti e redirige se manca.

```ts
// SPW loaders.ts:10-20 — una guardia, N pagine figlie: la sessione è verificata prima del render
export const adminAuthLoader = async () => {
    const session = await api.checkSession();
    if (!session || !session.user) return redirect('/admin/login');
    return session;
};
```

SR e DIS usano invece una guardia imperativa dentro un componente: `checkAuth` al montaggio, una macchina a stati che mostra il login finché non c'è un utente.

```tsx
// SR Admin.tsx:74-189 — guardia dentro il componente, eseguita al montaggio
useEffect(() => { checkAuth(); }, []);
if (loading) return <Loader />;
if (!user)   return <LoginForm onLogin={handleLogin} />;   // nessun utente → form di login
```

Il confronto architetturale completo, con le sue conseguenze (per esempio la guardia di DIS che controlla l'utente ma non il ruolo), è al CAP 14. Qui conta una cosa sola.

> [!NOTE]
> **Loader o componente: due scuole, una sola difesa vera**
> La differenza pratica tra le due è un lampo: col loader non si vede mai contenuto riservato prima del redirect; col componente c'è un istante di «loading» prima del verdetto. Ma è una differenza di esperienza, non di sicurezza. In tutti e tre i siti la difesa reale è il gate server-side (CAP 10), e la guardia client serve solo a non mostrare una porta che il server terrebbe comunque chiusa. Nascondere una pagina è esperienza utente; impedire un'azione è sicurezza, e va fatta sul server.

---

## 6. La sessione che scade mentre lavori

C'è un buco che attraversa tutti e tre i siti, ed è forse il più importante del capitolo perché nessuno lo copre. La guardia dell'area admin scatta una volta sola: quando navighi (SPW) o quando la pagina si monta (SR, DIS). Ma la sessione può morire *dopo*, mentre stai scrivendo un articolo, anche solo perché un cambio password fatto altrove l'ha invalidata via `session_version` (CAP 10).

```ts
// in tutti e tre: la mutazione riceve 401/403, il client mostra un errore generico
// e NON redirige. Manca un punto unico che riconosca lo status e forzi il re-login.
```

> [!WARNING]
> **Gestire la scadenza di sessione nel thin stack**
> A sessione morta, il salvataggio prende un 401, il client mostra «errore nel salvataggio» e ti lascia su una pagina che non funziona più, col lavoro ancora a schermo e nessun invito a rifare il login. Nessuno dei tre siti ha un interceptor che riconosca il 401/403 e forzi il re-login; in SR è perfino peggio, perché un 403 da token CSRF scaduto è identico, a video, a un errore qualsiasi. È il rovescio del fatto che la gestione errori vive sparsa in ogni metodo invece che in un solo strato: un piccolo `request(path, opts)` centralizzato, oltre a togliere la ripetizione del wrapper `fetch`, sarebbe il posto naturale dove gestire la sessione scaduta una volta per tutte, insieme al Double Read e agli header.

---

## 7. Upload e paginazione: le stesse tre mani

Restano due superfici dove le tre filosofie si vedono in piccolo. La prima è l'upload. Il bridge invia un `FormData`, e in tutti e tre c'è lo stesso accorgimento: si toglie l'header `Content-Type`, altrimenti il browser non scrive il boundary multipart e il file non arriva. Cambia il contorno.

```ts
// SPW api.ts:438-509 — per FormData si TOGLIE Content-Type; in alternativa XHR per la barra di avanzamento
const { headers, ...rest } = fetchConfig;
const res = await fetch(`${API_URL}/upload.php`, { ...rest, method: 'POST', body: formData,
    headers: { 'Accept': 'application/json' } });   // variante: XMLHttpRequest + xhr.upload.onprogress
```

SPW offre la barra di avanzamento via `XMLHttpRequest`; SR manda il `FormData` con l'`X-CSRF-Token` ma senza progresso, un semplice spinner; DIS lo manda senza progresso e senza CSRF. Il lato server di tutto questo (la validazione, la conversione WebP, la catena RCE da upload pubblico di DIS) è il CAP 7.

La seconda superficie è la paginazione, ed è legata a doppio filo al Double Read del §2. È proprio il contratto `{ data, total }` a rendere possibile, e necessaria, la lettura in due forme: senza un `total` non si sa quante pagine restano.

```ts
// SPW useFetchArticles.ts:32-49 — il { data, total } del Double Read alimenta il load-more con dedup
const data  = Array.isArray(res) ? res : res.data;
const total = !Array.isArray(res) && res.total !== undefined ? res.total : data.length;
// ...accumula le pagine, deduplica per id, hasMore = (lista unita).length < total
```

SPW accumula le pagine deduplicando per `id` e calcola `hasMore` sulla lunghezza unita. SR fa il load-more senza dedup, fidandosi del backend per non ripetere. DIS non pagina affatto. E c'è una trappola silenziosa: quando l'endpoint torna un array nudo, senza `total`, SPW ripiega su `data.length` come totale, e `hasMore` diventa `false` anche quando ci sarebbero altre pagine. È la conseguenza diretta di leggere un contratto che non è garantito. Il lato server (il `{ data, total }`, il `COUNT` e il `LIMIT/OFFSET`) è al CAP 9.

---

## In sintesi

Il ponte tra React e PHP è in tutti e tre lo stesso oggetto su `fetch`, ma è cresciuto attorno a un'API senza contratto stabile, e ognuno ci ha messo del suo. SPW nello state layer, con i loader e il Double Read del payload. SR nel token CSRF tenuto in una variabile di modulo. DIS in un codemod che ha rattoppato la gestione errori a posteriori, lasciando le sue impronte (la ripetizione, i metodi sfuggiti, la riga duplicata). Tre investimenti diversi, e nessuno che renda il bridge davvero solido: il messaggio d'errore del backend si perde in tutti e tre, e in tutti e tre manca la cosa che servirebbe di più, un punto unico che gestisca la sessione scaduta. La morale non è «scegli il client più ricco». È che un wrapper su `fetch` non è mai solo trasporto: è il posto dove un'API imperfetta diventa, o non diventa, un'esperienza affidabile. Le decisioni che contano (leggere il body anche sugli errori, dove vive il token, cosa fare quando la sessione muore) stanno tutte lì.

---
*Prossimo Capitolo: Media & Optimization. L'upload come superficie d'attacco: validare i file davvero, spegnere PHP nelle cartelle pubbliche, e la catena che da un'immagine porta all'esecuzione di codice.*
