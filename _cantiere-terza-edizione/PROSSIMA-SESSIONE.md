# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟨 FASE 2 (SINTESI) in corso. S1-C1 (Backend Core) ✅ e S1-C2 (Security & Auth) ✅ COMPLETATE.
> Questa è la TERZA scheda di sintesi: **S1-C3 Frontend Bridge & State**. Ordine confermato:
> S1 → S2 → S3 → S4 (nessuna deviazione).

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md, _cantiere-terza-edizione/LOG.md e
_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md per il contesto.

STATO: FASE 1 (mappatura) CONCLUSA — 4 siti, 34 card, copertura COMPLETA. FASE 2 (SINTESI) in corso:
**2/14 schede S1 completate** (S1-C1 Backend Core ✅, S1-C2 Security & Auth ✅). Metodo: UNA scheda
tematica cross-sito per sessione, che fonde i 2-3 trattamenti per-sito di un cluster in UNA visione
comparata (pattern comune + varianti per sito in tabella unica + GOLD + mappa→capitoli). Le fonti
sono le card di mappatura (specialmente i loro §6, già a confronto). NON si rilegge il codice
sorgente: si consolida ciò che è già mappato. Il template è
`_cantiere-terza-edizione/sintesi/_TEMPLATE-SCHEDA.md`; i modelli già fatti sono
`S1-C1-backend-core.md` e `S1-C2-security-auth.md` (seguine struttura e livello di dettaglio).

UNITÀ DI QUESTA SESSIONE: **S1-C3 — Scheda tematica cross-sito "Frontend Bridge & State"**.
Fonti primarie: SPW-C3, SR-C3, DIS-C3. Da consolidare (spunti dai §6 già scritti):
- **Forma del client `api.ts`:** oggetto-namespace su `fetch` in tutti e tre (no Axios/React Query/
  Redux), un metodo per azione. Divergenza: SPW base URL auto-commutata prod/dev + `credentials:
  'include'`; SR base FISSA `/api` SENZA `credentials:'include'` (controparte client della
  CORS-senza-Allow-Credentials di SR-C2 → auth de-facto same-origin su entrambi i lati); DIS come SR
  (base fissa, no credentials).
- **CSRF lato client:** SPW non lo gestisce nel client (è Origin/Referer server-side, S1-C2); SR ha
  il **token CSRF in-memory** (`let csrfToken` di MODULO, catturato dal body di login/check_auth,
  reiniettato via `csrfHeaders()`→`X-CSRF-Token` solo sulle mutazioni, azzerato al logout) — perso al
  reload, regge solo grazie al `checkAuth` on-mount (dipendenza accoppiata non dichiarata); DIS NON ha
  CSRF (più scarno di SR).
- **Lettura del payload — il GOLD del cluster:** SPW = pattern **"Double Read"** (`Array.isArray(res)
  ? res : res.data`) perché MESCOLA le due famiglie di buste nei loader; SR = contratti ETEROGENEI
  per-endpoint letti per forma nota + guardia difensiva `Array.isArray`; DIS = "busta zero" passata
  grezza (risposte sempre nude). → la scala "come un client si difende da un'API cresciuta
  incrementalmente".
- **Data layer / routing & guard:** SPW = react-router data-loader (`loaders.ts`, render-as-you-fetch)
  + guard = `adminAuthLoader`→`redirect` (versione client del gate `Auth::check()`); SR = router
  CLASSICO `<Routes>/<Route>` senza loader, guard = il COMPONENTE `Admin.tsx` (checkAuth on mount,
  if(!user)→`<LoginForm>`); DIS = guard-componente `AdminLayout` (come SR) su `createBrowserRouter`
  (data-router senza usarne i loader).
- **GOLD error-handling INIETTATO da codemod (DIS):** `fix_api.cjs/js` = regex-replace che appende il
  blocco `if(!res.ok){res.clone().json()...}` a ogni `fetch` — prove: stesso blocco in ~25 metodi,
  metodi "sfuggiti" con messaggio generico (login/getNewsDetail/uploadFile/submitVote), riga
  DUPLICATA api.ts:370-371; il client rattoppa per-metodo l'HTTP-200-con-body-errore della newsletter
  (DIS-C9). Chiude il puntatore `fix_api` di DIS-C1.
- **`if(!res.ok) throw` e messaggi backend persi:** SPW NON fa throw nel client → body sempre
  preservato MA il messaggio 429 si perde comunque nel login; SR idem 429 perso ma in punto diverso
  (`LoginForm.tsx:21` hardcoda 'Login fallito' scartando `err.message`); niente interceptor 401/403
  mid-sessione (gap comune a tutti, aggravato in SR dal 403 CSRF indistinguibile).
- **Upload:** SPW `fetch`+XHR con `onprogress`; SR/DIS `FormData`+(CSRF in SR) SENZA progress.

Fai così:
1. Scrivi la scheda in `_cantiere-terza-edizione/sintesi/S1-C3-frontend-bridge.md` seguendo
   `_TEMPLATE-SCHEDA.md` (0 una-frase · 1 pattern comune · 2 tabella varianti UNICA e deduplicata · 3
   GOLD/box · 4 mappa→capitoli · 5 scarti/dedup). La tabella comparativa va scritta UNA volta, pulita.
2. Mappa esplicitamente → capitoli esistenti: soprattutto **CAP 6 (Frontend Bridge / API.ts)**, con
   ponti a CAP 10 (Security, per il CSRF in-memory e il guard client), CAP 9 (Content Lifecycle, per
   i loader/contratti di lista) e CAP 4 (Frontend Dependencies, per il "no React Query/Axios").
   Segnala eventuali CORREZIONI al testo attuale (come fatto per CAP 3 in S1-C1 e CAP 10 in S1-C2).
3. Aggiorna `_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md` (S1-C3 → ✅, contatore 3/14).

Criterio di STOP: scheda S1-C3 in stato COMPLETATO (pattern + varianti + GOLD + mappa capitolo).

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna `_cantiere-terza-edizione/sintesi/_INDICE-SINTESI.md` (S1-C3 → ✅)
- aggiorna `_cantiere-terza-edizione/ROADMAP.md` (spunta S1-C3 in §4, aggiorna §7 stato globale)
- aggiungi UNA riga a `_cantiere-terza-edizione/LOG.md` (più recente IN BASSO)
- git add/commit/push (un commit) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md, sia root sia in _cantiere-terza-edizione/) con la
  prossima scheda: **S1-C4 (Content APIs)** — fonti SPW-C4, SR-C4, DIS-C4 (Double Read CHIUSO lato
  server SPW / geografia frammentata 3 buste SR / busta-zero DIS; slug, visibilità published_at,
  tag M:N vs category-stringa-libera).
