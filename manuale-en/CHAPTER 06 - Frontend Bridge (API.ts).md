# CHAPTER 6: Frontend Bridge (API.ts)

React talks to PHP through a single point. Not `fetch` calls scattered across the components, but an `api` object that gathers them all: one method per action (`login`, `getNews`, `uploadImage`, `submitVote`), grouped by domain with a few comments, imported everywhere with `import { api }`. No Axios, no React Query, no Redux, no global store. It’s the thin-stack version of the data access layer: a flat facade over `fetch`, consistent with the model’s philosophy (Ch. 4), as few dependencies as possible.

Under that shared surface there’s a shared problem, and it’s the real lens of the chapter: the PHP API has no uniform contract. The endpoints, grown by accretion, answer with different envelopes (a bare array, or `{ data, total }`, or `{ success, … }`), and sometimes with an HTTP 200 even when things went wrong. None of the three sites version that contract. Each one just reads defensively whatever arrives, and the way it shoulders that is what tells them apart.

The three responses read well as a scale of *investment*. SimonePizziWebSite invests in the state layer: React Router’s loaders as a data layer, and the “Double Read” of the payload. SitoRuntime invests in client-side security: a CSRF token kept in a module variable. DISINTELLIGENZA invests in a codemod, a script that patches the client after the fact. Three ways of holding React and PHP together when neither side has a stable contract. And as in the earlier chapters, the order of investment doesn’t line up with solidity: the one who spends the most isn’t the one who gets it least wrong.

The fourth site, FDCA, doesn’t enter here. The fork rewrote and shrank the frontend into a public storefront, and it has no `api.ts` and no `fetch` to `/api`: where on the backend it was byte-identical to DIS, on the bridge it’s simply absent. A shell disconnected from the CMS, which lives in the chapter on forking, not this one.

---

## 1. One Client, Thin Over `fetch`

Before the differences, the traits the three sites share. The client is a namespace object, not a class: no instance, no dependency injection, you import it and call it. There’s no data-fetching library: shared state either lives in the router (SPW) or is component-local `useState` (SR, DIS), and the “fetching” is native `fetch`. Where possible the methods are typed (`NewsArticle[]`, `UserRole`), so the caller knows what to expect, but the real contract is dictated by the PHP, and it doesn’t always match the declared types.

Authentication, finally, travels on the `HttpOnly` session cookie (Ch. 10): the client carries no bearer token and no persistent auth state. From this follows a detail that immediately splits the three sites, the base URL and the cookie.

```ts
// SPW api.ts:1-12 — base URL that switches prod/dev, shared config carrying the cookie
export const API_URL = import.meta.env.PROD ? '/api' : 'http://localhost:8888/api';

const fetchConfig: RequestInit = {
    credentials: 'include',  // propagates the PHP session cookie (in dev it crosses localhost:8888)
    headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' }
};
```

```ts
// SR api.ts:4 — fixed base, no switch: always same-origin
const API_BASE = '/api';     // no localhost:8888, and—crucially—no credentials:'include'
```

> [!NOTE]
> **`credentials:'include'`: when it matters and when it’s noise**
> SPW puts `credentials:'include'` on every call, and it has to: in development the frontend and the backend sit on two different origins (`localhost:8888`), and without that option the session cookie wouldn’t go out. SR and DIS never set it, because they develop and ship same-origin, where the cookie travels on its own under `fetch`’s default policy. There’s an exact symmetry with the server side (Ch. 10): SR’s CORS doesn’t emit `Access-Control-Allow-Credentials`, so authentication is de facto same-origin on both sides, and there `credentials:'include'` would be a line that does nothing. The rule: that option matters when the client and the API sit on different origins; same-origin, it’s noise.

---

## 2. The Contract Isn’t Uniform: Three Ways to Read the Payload

This is the heart of the chapter. The endpoints answer with different envelopes, and the client has to survive that inconsistency. The three techniques are the standout of the cluster.

SPW lives the hardest case: *the same* endpoint sometimes answers with a bare array, sometimes with a paginated object `{ data, total }`. The answer is to read the payload in two possible shapes, and this, and only this, is the pattern the model calls the “Double Read.”

```ts
// SPW loaders.ts:30-31 — the same endpoint is sometimes an array, sometimes { data, total }
const articlesData = Array.isArray(articlesRes) ? articlesRes : articlesRes.data;
const projectsData = Array.isArray(projectsRes) ? projectsRes : projectsRes.data;
```

SR doesn’t have the same ambiguous endpoint, it has a mosaic: each endpoint has *its own* envelope, and the client knows it by heart. On two of them, though, where the response is a bare array on success but a `{ success:false, error }` object on failure, it puts in a type guard.

```ts
// SR — each endpoint has its own envelope, read by known shape:
//   news.php → { success, data, meta }      admin?action=list → { success, articles, total }
//   speakers.php / podcasts.php → BARE ARRAY, or { success:false, error } on error
if (Array.isArray(res)) setPodcasts(res);   // Podcasts.tsx:14 — type guard against the error case
```

DIS takes the opposite road: it doesn’t normalize at all. It returns the JSON as-is (“zero envelope”) and leaves it to the caller to know its shape.

```ts
// DIS api.ts — "zero envelope": the client doesn't touch the shape, it passes it raw to the caller
return await res.json();
```

> [!TIP]
> **Elastic contracts: Double Read, type guard, zero envelope**
> Same root, three remedies. When an API grows by accretion and no one versions the shape of the responses, the client has to decide how much work to do in place of the missing contract. SPW reads the same payload in two possible shapes (the true “Double Read”: bare array *or* `{ data, total }`). SR knows the envelope of each endpoint and, where the shape is ambiguous, puts in an `Array.isArray` guard that tells the good data from the error. DIS doesn’t normalize: it returns the JSON as-is and trusts the caller. None of the three is wrong; they’re three points on the scale of how much server inconsistency the client agrees to absorb. A note on terminology: the “Double Read” is *this*, reading the shape of the success payload. It’s not cloning the response to pull out an error message, which is a different thing with a different story (the next section).

---

## 3. When the Backend Is Wrong: the Lying 200 and the Lost Message

Sometimes the backend doesn’t cooperate, in two distinct ways. The first: it answers HTTP 200 even on a logical failure, putting the error in the body. That’s the case with some of DIS’s endpoints (the newsletter), and the client patches it by hand, method by method.

```ts
// DIS api.ts:341-343 — some endpoints return HTTP 200 even on error: a per-method patch
const data = await res.json();
if (data.status === 'error') throw new Error(data.message);   // not a single interceptor
```

Mind the attribution, because it’s easy to mistake this for a general rule: this is DIS’s pattern, not a universal prescription of the model. It’s the consequence of a backend that doesn’t always use the HTTP codes, and the bridge handles it case by case. The second way the backend fails to cooperate is the opposite: it answers with a precise error, and the client throws it away. To pull out that message when it’s there, you have to clone the response.

```ts
// the block that EXTRACTS the error message from the body (response cloning) — NOT the "Double Read"
if (!res.ok) {
    let err = 'Errore imprevisto dal server';
    try { const j = await res.clone().json(); err = j.message || err; } catch (e) {}
    throw new Error(err);
}
return await res.json();
```

In DIS this block appears, identical, in twenty-five methods. Not because someone wrote it twenty-five times, but because a script injected it.

```js
// DIS fix_api.cjs:4-23 — regex-replace: find every fetch and append the block, if it's missing
const regex = /(const res = await fetch\([\s\S]*?\);)/g;
code = code.replace(regex, (match, p1, offset, string) => {
    const nextLine = string.substring(offset + p1.length).trim().split('\n')[0];
    if (nextLine.startsWith('if (!res.ok)')) return match;   // skip the ones that already have it → the "slipped-through" methods
    const check = `\n  if (!res.ok) { /* … res.clone().json() … */ throw new Error(err); }`;
    return match + check;
});
```

> [!WARNING]
> **The codemod that patches the client: power and traces**
> DIS didn’t hand-write its client’s error handling: it generated it with a codemod. `fix_api.cjs` looks for every `const res = await fetch(...)` and, if there isn’t already an `if (!res.ok)`, appends a block that clones the response and pulls out `message`. It works, and in a few seconds it covers the whole file. But it leaves three fingerprints. The first: the same identical block, word for word, everywhere. The second: the “slipped-through” methods, the ones that already had their own `if (!res.ok)` with a generic message (`login` with “Login failed,” `uploadFile` with “Upload failed”), which the script skipped, leaving the bridge uneven. The third: a duplicated line, the residue of a second pass. It’s a real case of client maintenance by automatic source transformation, with its upsides and its side effects. That block is exactly what a manual might sell as “the standard” for error handling: here it’s the product of a machine, not a choice, and it’s worth being able to recognize that.

What’s left is the most widespread problem, and the most instructive because it’s common to all three: the backend’s error message that gets lost. The server (Ch. 10) went to the trouble of crafting precise statuses and texts, a 429 with “Troppi tentativi, riprova tra quindici minuti” (too many attempts, try again in fifteen minutes). The client throws it away, at three different points in the chain.

```ts
// SPW api.ts:22 — the error body (even a talkative 429) is discarded here, in the client
if (!res.ok) throw new Error('Login fallito');
```

```tsx
// SR LoginForm.tsx:18-25 — here the body is preserved by api.login, but the UI throws it away anyway
catch (err) { setError('Login fallito. Controlla le credenziali.'); }   // err.message ignored
```

In SPW the message is lost in the client, in SR in the UI, in DIS in patches (the methods the codemod touched preserve it, the slipped-through ones don’t). Three different points, the same outcome: the rate-limited user always sees “Login fallito” and never the 429 that would tell them how long to wait.

> [!WARNING]
> **Read the body on the error branches too**
> `res.ok` tells you *whether* the request succeeded, not *why* it failed; the why is in the body. Throwing it away, as all three sites do on login, wastes the work done on the server to make errors talkative, and leaves the user facing a useless message. The lesson is simple and often ignored: the body has to be read also, and especially, when the response isn’t ok. Where you do it matters less than doing it: the point is not to replace a 429 “try again in fifteen minutes” with a generic “error.”

---

## 4. The CSRF Token on the Client

This is the investment that sets SitoRuntime apart, and the most sophisticated mechanism in the cluster. SR’s backend (Ch. 10) returns a `csrf_token` in the body of `login` and `check_auth`, and demands the `X-CSRF-Token` header on all mutations. The client handles the handshake in the most minimal way possible: a module-level variable.

```ts
// SR api.ts:6-10 — the CSRF token lives in a module-level variable, in memory
let csrfToken = '';                          // not localStorage, not Context, not component state
function csrfHeaders() { return csrfToken ? { 'X-CSRF-Token': csrfToken } : {}; }
```

```ts
// SR api.ts:31,37 — captured from the login/check_auth body, sent back only on mutations
if (data.csrf_token) csrfToken = data.csrf_token;
// ...and on every POST/DELETE:  headers: { 'Content-Type': 'application/json', ...csrfHeaders() }
```

The token is captured at login, reinjected on writes, and cleared at logout. SPW has none of this (the server-side Origin/Referer check is enough for it), and DIS has no CSRF at all: it’s entirely SR’s solution. But keeping it in a module variable has a hidden price.

> [!WARNING]
> **The CSRF token and the reload: a coupled guarantee**
> The variable lives in memory: on a page reload it vanishes, and the first mutation afterward would go out without `X-CSRF-Token`, taking a 403. The system holds only because the admin component reruns `checkAuth()` every time it mounts, and that call re-returns the token. It’s a real dependency, but one declared nowhere: if tomorrow an admin page mounted an editor without going through that `checkAuth`, the writes would fail opaquely, with a 403 that on screen is indistinguishable from a save error. If a token has to survive a reload, put it where it actually survives (a `sessionStorage`, or an explicit handshake on every startup), not at the mercy of a side effect of a component mounting.

---

## 5. Protecting the Admin Area: Loader or Component

Protecting the restricted routes on the client is two schools doing the same thing. SPW uses a declarative guard: a loader mounted on the parent `/admin` route, which checks the session before the page mounts and redirects if it’s missing.

```ts
// SPW loaders.ts:10-20 — one guard, N child pages: the session is checked before render
export const adminAuthLoader = async () => {
    const session = await api.checkSession();
    if (!session || !session.user) return redirect('/admin/login');
    return session;
};
```

SR and DIS use an imperative guard inside a component instead: `checkAuth` on mount, a state machine that shows the login until there’s a user.

```tsx
// SR Admin.tsx:74-189 — guard inside the component, run on mount
useEffect(() => { checkAuth(); }, []);
if (loading) return <Loader />;
if (!user)   return <LoginForm onLogin={handleLogin} />;   // no user → login form
```

The full architectural comparison, with its consequences (for example DIS’s guard that checks the user but not the role), is in Ch. 14. Here only one thing matters.

> [!NOTE]
> **Loader or component: two schools, one real defense**
> The practical difference between the two is a flash: with the loader you never see restricted content before the redirect; with the component there’s an instant of “loading” before the verdict. But it’s a difference of experience, not of security. In all three sites the real defense is the server-side gate (Ch. 10), and the client guard only serves to avoid showing a door the server would keep shut anyway. Hiding a page is user experience; preventing an action is security, and that has to be done on the server.

---

## 6. The Session That Expires While You Work

There’s a hole that runs through all three sites, and it may be the most important one in the chapter because no one covers it. The admin-area guard fires once: when you navigate (SPW) or when the page mounts (SR, DIS). But the session can die *afterward*, while you’re writing an article, even just because a password change made elsewhere invalidated it via `session_version` (Ch. 10).

```ts
// in all three: the mutation gets a 401/403, the client shows a generic error
// and does NOT redirect. There's no single place to recognize the status and force a re-login.
```

> [!WARNING]
> **Handling session expiry in the thin stack**
> With a dead session, the save takes a 401, the client shows “error while saving” and leaves you on a page that no longer works, with your work still on screen and no prompt to log back in. None of the three sites has an interceptor that recognizes the 401/403 and forces a re-login; in SR it’s even worse, because a 403 from an expired CSRF token is identical, on screen, to any other error. It’s the flip side of error handling living scattered across every method instead of in a single layer: a small centralized `request(path, opts)`, on top of removing the repeated `fetch` wrapper, would be the natural place to handle the expired session once and for all, along with the Double Read and the headers.

---

## 7. Upload and Pagination: the Same Three Hands

Two surfaces remain where the three philosophies show in miniature. The first is the upload. The bridge sends a `FormData`, and in all three there’s the same trick: you remove the `Content-Type` header, otherwise the browser doesn’t write the multipart boundary and the file never arrives. The trimmings change.

```ts
// SPW api.ts:438-509 — for FormData you REMOVE Content-Type; alternatively XHR for the progress bar
const { headers, ...rest } = fetchConfig;
const res = await fetch(`${API_URL}/upload.php`, { ...rest, method: 'POST', body: formData,
    headers: { 'Accept': 'application/json' } });   // variant: XMLHttpRequest + xhr.upload.onprogress
```

SPW offers the progress bar via `XMLHttpRequest`; SR sends the `FormData` with the `X-CSRF-Token` but no progress, a simple spinner; DIS sends it with no progress and no CSRF. The server side of all this (the validation, the WebP conversion, DIS’s public-upload RCE chain) is in Ch. 7.

The second surface is pagination, and it’s tied tightly to the Double Read of §2. It’s precisely the `{ data, total }` contract that makes reading in two shapes possible, and necessary: without a `total` you don’t know how many pages are left.

```ts
// SPW useFetchArticles.ts:32-49 — the Double Read's { data, total } feeds the load-more, with dedup
const data  = Array.isArray(res) ? res : res.data;
const total = !Array.isArray(res) && res.total !== undefined ? res.total : data.length;
// ...accumulate the pages, dedupe by id, hasMore = (merged list).length < total
```

SPW accumulates the pages deduping by `id` and computes `hasMore` on the merged length. SR does the load-more without dedup, trusting the backend not to repeat. DIS doesn’t paginate at all. And there’s a silent trap: when the endpoint returns a bare array, with no `total`, SPW falls back on `data.length` as the total, and `hasMore` becomes `false` even when there would be more pages. It’s the direct consequence of reading a contract that isn’t guaranteed. The server side (the `{ data, total }`, the `COUNT` and the `LIMIT/OFFSET`) is in Ch. 9.

---

## In Summary

The bridge between React and PHP is, in all three, the same object over `fetch`, but it grew around an API with no stable contract, and each one added its own touch. SPW in the state layer, with the loaders and the Double Read of the payload. SR in the CSRF token kept in a module variable. DIS in a codemod that patched the error handling after the fact, leaving its fingerprints (the repetition, the slipped-through methods, the duplicated line). Three different investments, and not one that makes the bridge truly solid: the backend’s error message is lost in all three, and in all three the thing that would help most is missing, a single place to handle the expired session. The moral isn’t “pick the richest client.” It’s that a wrapper over `fetch` is never just transport: it’s where an imperfect API becomes, or fails to become, a reliable experience. The decisions that matter (reading the body on errors too, where the token lives, what to do when the session dies) all live there.

> [!IMPORTANT]
> **The Canon**
> - A single `api` object over `fetch`, auth via the session cookie; for multipart uploads, remove the `Content-Type` header and let the browser set it.
> - Define a stable payload shape and read it in one place: a uniform contract beats the “Double Read.”
> - Handle the CSRF token on mutations and centralize the reaction to 401/403 (an interceptor) for expired sessions.
> - Read the response body on the error branches too: don’t lose the backend’s message (e.g. the 429).

---
*Next Chapter: Media & Optimization. The upload as an attack surface: validating files for real, turning PHP off in public folders, and the chain that leads from an image to code execution.*
