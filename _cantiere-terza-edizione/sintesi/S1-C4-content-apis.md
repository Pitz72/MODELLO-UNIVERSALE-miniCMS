# Scheda di Sintesi — S1-C4 — Content APIs

> **Stato:** COMPLETATO
> **Cluster FASE 2:** S1-C4 · **Data:** 2026-06-19 · **Commit:** _(in corso)_
> **Fonti (card di mappatura, in particolare i §6):** SPW-C4, SR-C4, DIS-C4 (+ FDCA-DIFF: backend byte-identico a DIS → eredita la "busta zero" immutata)
> **Capitoli del libro toccati:** CAP 9 (Content Lifecycle) — principale · ponti a CAP 6 (Frontend Bridge, qui si CHIUDE il contratto del Double Read), CAP 3 (visibilità/fusi/schema), CAP 15 (Portfolio & Projects), CAP 10 (404-non-403) → vedi §4

---

## 0. In una frase
Il lato server dei contenuti è, in tutti e tre i siti, lo **stesso endpoint-router su
`REQUEST_METHOD`** — un file per risorsa, un `if/elseif` sul verbo HTTP, il gate solo sui rami
mutativi — ma è il punto in cui si **chiude il Double Read** di S1-C3 (il contratto di payload non è
uniforme *lato server*) e in cui emerge il secondo grande tema del cluster: **come tre CMS gestiscono
"adesso"** — e i tre modi diversi di sbagliare il fuso sui post programmati. La scala va dal **CMS
editoriale ricco** (SPW: tassonomie, ricerca, paginazione robusta) al **grado-zero** (DIS: busta
nuda, niente meta, niente autore, niente tassonomie), con SR nel mezzo ma **frammentato** e con due
tratti propri (cache-su-file, colonne JSON).

## 1. Il pattern comune — la filosofia "thin stack" su questa lente

Sotto le differenze, gli endpoint di contenuto dei tre siti condividono cinque tratti.

**1) L'endpoint-router su verbo HTTP.** Ogni risorsa è un singolo file `.php` che fa da router su
`$_SERVER['REQUEST_METHOD']`: un `if ($method === 'GET') … elseif ('POST') …` dentro un unico
`try/catch`, con `Database::connect()` (il singleton di S1-C1) e il gate (S1-C2) **solo sui rami
mutativi**. Niente router framework, niente controller: la logica di una risorsa vive tutta in un
file. È il pattern strutturale del thin stack allo stato puro.

**2) Un endpoint, due audience.** La stessa risorsa serve il pubblico e la dashboard: la differenza è
una condizione di visibilità (`status` + `published_at`) **aggiunta solo se non sei admin**. La
sessione di S1-C2 decide quale delle due viste ottieni. Non esiste un endpoint "admin" separato per
la lettura: è lo stesso, con un `WHERE` in più o in meno.

**3) La pubblicazione programmata senza cron.** In tutti e tre `published_at` nel futuro significa
"pubblicato ma non ancora visibile": un post appare da solo quando la data arriva, perché la query di
visibilità confronta `published_at <= adesso`. Nessun job schedulato, solo un confronto nel `WHERE`.
È una delle idee più eleganti del modello — e anche la più insidiosa (vedi §3, il fuso).

**4) Lo slug generato dal titolo, con unicità garantita.** Ogni sito deriva uno slug leggibile dal
titolo e ne garantisce l'unicità (a monte con un pre-check, o a valle intercettando il vincolo
`UNIQUE`). È l'URL parlante del thin stack, calcolato in PHP senza librerie.

**5) Il contratto di risposta NON è uniforme — ed è cresciuto in-place.** È il tratto che chiude il
filo di S1-C3: la forma della busta (array nudo vs oggetto con meta) varia per endpoint e per sito,
perché l'API è stata **estesa quando è servito** (paginazione, wrapper `success`) invece di essere
versionata. Il client (S1-C3) si è adattato leggendo in modo difensivo. Qui, lato server, si vede da
dove nasce quella difesa.

A questi si aggiunge un tratto comune di sicurezza-contenuto: il `content` è salvato **grezzo**
(nessuna sanitizzazione write-time), e la difesa XSS-stored è demandata al render-time lato client
(→ S1-C6). E un tratto di onestà: la ricerca, dove esiste, è `LIKE '%q%'`, non full-text reale.

## 2. Le varianti per sito (tabella unica, deduplicata)

| Asse | SimonePizziWebSite | SitoRuntime | DISINTELLIGENZA | *(FDCA)* |
|---|---|---|---|---|
| **Struttura endpoint** | endpoint-router CRUD **per dominio** (`articles.php` GET+POST+PUT+DELETE+PATCH) | **frammentata**: lettura in `news.php` (GET), scrittura in `admin.php?action=…`; speakers/podcasts a parte | endpoint-router **in un file** (GET pubblico + POST `?action`) — come SPW | = DIS |
| **Busta lista** (chiude il Double Read) | **solo `articles`** lista = `{data,total,page,limit}`; tutto il resto **array nudo** | **tre buste**: `{success,data,meta}` (news) / `{success,articles,total}` (admin) / array nudo (speakers/podcasts) | **sempre nuda** ("busta zero": array/oggetto diretto) | = DIS |
| **Wrapper `success`** | assente | presente su news/admin, assente su speakers/podcasts | **assente ovunque** | = DIS |
| **Paginazione** | `COUNT` separato + `total` grezzo + **`PARAM_INT`** esplicito | **`total_pages` pre-calcolato** server in `meta`; niente `PARAM_INT` | **nessun metadato** (`LIMIT/OFFSET` con cast `(int)`, array nudo) | = DIS |
| **Cache di contenuto** | nessuna | **file `.cache/news_*.json` TTL 300s** + invalidazione su save/delete, header `X-Cache HIT/MISS` | nessuna | = DIS |
| **"Adesso" per la visibilità** | PHP `date()` + **`Europe/Rome` forzato** | PHP `date('Y-m-d H:i:s')` (separatore **spazio**); incidente `'T'` in `debug_time.php` (S1-C1) | **`CURRENT_TIMESTAMP` SQLite (UTC)** vs `published_at` nel fuso server | = DIS |
| **Regola `status`** | `status='published' AND published_at<=now` | `status='published' OR status IS NULL` (**cicatrice** migrazione v2.9.1) | interroga **ancora `status='scheduled'`** (residuo v0.5.4 non ripulito) | = DIS |
| **Pubblico vs admin** | `AND` condizionale nello **stesso** endpoint + **404-non-403** sul singolo | **due query in due file** (news.php vs admin.php) | `if(!$isAdmin)` aggiunge il `WHERE` (stesso endpoint) | = DIS |
| **Categorie** | gerarchia `parent_id` + filtro "contenitore" (`IN` sottocategorie) + `navigation.php` ad albero | **N/A**: `category` stringa libera | **N/A**: `category` stringa libera (default `'generale'`) | = DIS |
| **Tag** | M:N `article_tags` **+ cache CSV legacy** (doppia scrittura) | speaker `tags` **JSON** denormalizzato; articoli N/A | campo `TEXT` semplice | = DIS |
| **Ricerca** | `search.php` `LIKE` **unificata** articoli+progetti, campo `type` | **N/A** (filtro al client) | **N/A** | = DIS |
| **Slug** | tabella accenti→sostituti coerente; unicità pre-check + suffisso `-timestamp` | **tre filosofie** (news no-accenti / podcast `iconv` / speaker id-client); unicità reattiva vs preventiva | senza accenti; unicità **preventiva** (`count+'-'.time()`) | = DIS |
| **`author`** | salvato reale | **sempre `'Admin'`** (username non in sessione, S1-C2) | **inesistente** (nessuna colonna) | = DIS |
| **Schema fonte di verità** | `migrate_to_mysql.php` | `init_mysql.php` + micro-migrazioni | **solo il `.sqlite` vivo** (`category`/`status` non sono in nessun file del repo) | = DIS |

**Lettura della tabella.** Lo spettro è netto sull'asse *ricchezza CMS*: **SPW** è il CMS editoriale
completo (categorie gerarchiche "contenitore", tag M:N, ricerca unificata, paginazione con `COUNT`+
`PARAM_INT`); **DIS** è il grado-zero (busta nuda, niente meta, niente tassonomie, niente autore,
niente cache); **SR** sta nel mezzo ma con una geografia **frammentata** (lettura e scrittura news in
file diversi) compensata da due tratti che gli altri non hanno: la **cache di contenuto su file** e le
**colonne JSON native**. Ma il secondo asse — *come si gestisce "adesso"* — non scala con la
ricchezza: i tre siti hanno **tre modi diversi di calcolare e tre modi diversi di sbagliare** la
visibilità temporale (Europe/Rome forzato in PHP / separatore stringa con incidente `'T'` /
`CURRENT_TIMESTAMP` UTC contro fuso locale). E DIS rende **tangibile** il "lo schema mente" di S1-C1:
`category` e `status` sono SELECTati e INSERTati ma non esistono in nessuno scaffolding — vivono solo
nel file `.sqlite`.

**FDCA** ha il backend di contenuti **byte-identico** a DIS (FDCA-DIFF §3): stessa "busta zero",
stesso `CURRENT_TIMESTAMP`, stesso `status='scheduled'` residuo. Non aggiunge varianti; eredita anche
il debito dello schema-solo-nel-file. Caso forking → scheda dedicata.

## 3. GOLD & box problemi-soluzioni

- **Tre buste di lista: la chiusura del Double Read** — *(SPW vs SR vs DIS, chiude S1-C3)* — il GOLD
  che salda la scheda precedente. Lato server la forma della risposta è questa: in **SPW** *un solo*
  endpoint (la lista articoli) ritorna `{data,total,page,limit}`, **tutto il resto** è array nudo → il
  client fa "Double Read" non perché un endpoint cambi forma, ma perché **mescola le due famiglie** nei
  loader (articoli paginati + progetti/categorie/tag nudi). In **SR** ci sono *tre* buste diverse
  (`{success,data,meta}` / `{success,articles,total}` / array nudo) = un mosaico per-endpoint. In
  **DIS** la busta è sempre nuda ("busta zero"). Il contratto non è mai stato versionato: è stato
  **esteso in-place** quando è arrivata la paginazione, e il costo è la fragilità (il `hasMore`
  sbagliato di S1-C3 nasce qui). → Box "Quando estendere un contratto invece di versionarlo, e cosa
  costa" (ponte CAP 6, alto valore).

- **Chi calcola la paginazione: server o client** — *(SPW vs SR vs DIS)* — tre divisioni del lavoro:
  SPW ritorna il `total` grezzo e lascia al client il calcolo di `hasMore` (con il `COUNT(*)`
  separato sulle stesse condizioni e — dettaglio MySQL/PDO obbligatorio — i `LIMIT/OFFSET` bindati
  con `PARAM_INT`, altrimenti vengono quotati come stringhe); SR **pre-calcola `total_pages`** lato
  server e lo mette in `meta`, così il load-more del client è banale (`current_page < total_pages`);
  DIS non dà **nessun** metadato — il client chiede la pagina successiva "alla cieca" finché torna
  vuota. → Box "Paginare senza librerie: dove vive il conteggio".

- **Tre siti, tre modi di sbagliare il fuso sui post programmati** — *(SPW vs SR vs DIS)* — il GOLD
  sul tempo, e una correzione importante al libro. La pubblicazione differita è la stessa idea
  ovunque (`published_at <= adesso`, niente cron), ma "adesso" è calcolato in tre modi: **SPW** forza
  `date_default_timezone_set('Europe/Rome')` e confronta in PHP (corretto, ma dipende dal forcing in
  *ogni* endpoint); **SR** confronta `date('Y-m-d H:i:s')` con separatore spazio — la query è giusta,
  ma esiste l'incidente documentato del separatore `'T'` (`debug_time.php`, S1-C1) latente se il
  client invia un ISO; **DIS** delega a `CURRENT_TIMESTAMP` di SQLite, che è **UTC**, mentre
  `published_at` è salvato nel fuso server (timezone forzato solo in `index.php`) → un post compare/
  sparisce con uno scarto di 1-2 ore. Tre approcci, tre modi di sbagliare. → Box "Chi calcola il
  presente: PHP o il database?" (ponte CAP 3; corregge CAP 9 §2.2, vedi §4).

- **Lo schema che non vive in nessun file** — *(DIS, rende tangibile S1-C1)* — `news.php` SELECTa e
  INSERTa `category` e `status`, ma `init_db.php` non le ha e nessun `update_db_*` le crea: quelle
  colonne esistono **solo nel `.sqlite` vivo**. Lo schema reale non è ricostruibile dal repo. È la
  prova pratica del tema "l'init mente / la verità è nel file" di S1-C1, vista dal lato contenuti. →
  Box "Quando lo scaffolding mente: la verità è nel file DB" (ponte S1-C1).

- **Residui di migrazione nel codice vivo** — *(DIS + SR)* — due query che portano i segni di una
  migrazione mai ripulita: in **DIS** `update_db_v0.5.4` ha normalizzato tutti gli `scheduled` in
  `published` dichiarando "ora la gestisce la data", ma `news.php` **continua** a interrogare
  `status='scheduled'` (codice morto che mente sulla logica); in **SR** la lista pubblica filtra
  `status='published' OR status IS NULL`, dove l'`IS NULL` è la **cicatrice** del fatto che `status` è
  stato aggiunto fuori dallo schema base (migrazione v2.9.1). → Box "La query che porta i segni di una
  migrazione" (ponte S1-C13).

- **Tag a doppia scrittura: migrare un modello senza downtime** — *(SPW)* — `syncArticleTags` scrive
  la relazione normalizzata in `article_tags` (M:N) **e in parallelo** aggiorna il campo storico
  `articles.tags` (CSV) come "cache sicura per retrocompatibilità". In lettura, la lista ricostruisce i
  tag con `GROUP_CONCAT` dalla tabella relazionale sovrascrivendo il legacy. È la convivenza del
  modello vecchio e nuovo durante una migrazione mai conclusa — e smentisce il "passaggio esclusivo"
  raccontato dal libro (§4). → Box "Migrare un modello senza downtime: il doppio binario".

- **Tre filosofie di slug nello stesso sito + lo slug accentato** — *(SR, con eco SPW/DIS)* — SR
  genera lo slug in **tre modi diversi** nello stesso codebase (news senza accenti, podcast con
  `iconv ASCII//TRANSLIT`, speaker che non ha slug e usa l'id dal client), e garantisce l'unicità in
  due modi (reattivo: `catch` del vincolo `UNIQUE 23000` / preventivo: `count + '-'.time()`). SPW ha
  una sola tabella accenti→sostituti coerente (per non produrre `caff-` da `caffè`); DIS fa senza
  accenti, unicità preventiva. → Box "Lo slug accentato e l'unicità: i modi nello stesso modello".

- **Un endpoint, due audience — e il 404 che finge** — *(SPW pattern, realizzato 3 modi)* — la stessa
  query serve pubblico e admin con un `AND status/published_at` condizionale (SPW), due query in due
  file (SR), o un `if(!$isAdmin)` che aggiunge il `WHERE` (DIS). Il dettaglio di sicurezza è di SPW:
  sul singolo articolo non pubblicato si risponde **404, non 403**, per non confermare l'esistenza di
  una bozza a un non autenticato. → Box "Un endpoint, due audience: il 404 deliberato" (ponte S1-C2).

## 4. Mappa → capitolo/i del libro

| Materiale della scheda | Capitolo esistente | Azione |
|---|---|---|
| L'endpoint-router su `REQUEST_METHOD` (un file = una risorsa) | **CAP 5 (Backend Logic)** + **CAP 9** | **aggiorna**: l'anatomia dell'endpoint è la base, qui declinata sui contenuti |
| **Chiusura del Double Read** (solo `articles` = `{data,total}`; mosaico SR; busta zero DIS) | **CAP 6 §1.1** (ponte) + **CAP 9** | **chiude il ponte** aperto in S1-C3: il contratto che il client legge "due volte" nasce qui |
| Paginazione: `total` grezzo / `total_pages` server / niente + `PARAM_INT` | **CAP 9 §2** (nuovo box) | **nuovo box**: "dove vive il conteggio" |
| **Visibilità & fuso**: Europe/Rome / separatore 'T' / CURRENT_TIMESTAMP UTC | **CAP 9 §2.2** + **CAP 3** | **riscrivi**: oggi §2.2 dà una sola strategia come "lo standard" (vedi correzioni) |
| Matrice stati (draft/published/scheduled) | **CAP 9 §1.1** | **aggiorna**: la matrice è SPW; SR ha `status IS NULL`, DIS ha `scheduled` residuo |
| Pubblico vs admin + **404-non-403** | **CAP 9 §5** + **CAP 10** (ponte) | **aggiorna**: §5 è accurato per SPW; aggiungere le 3 realizzazioni (SPW/SR/DIS) |
| **Tag a doppia scrittura** (M:N + CSV legacy) | **CAP 9 §4** | **correggi**: il "passaggio esclusivo a M:N" è SPW-only e mantiene il legacy (vedi correzioni) |
| `category` stringa libera vs tassonomia gerarchica | **CAP 9 §4** | **nuovo box**: "quando NON ti serve una tabella categorie" |
| Ricerca `LIKE` unificata articoli+progetti, campo `type` | **CAP 15 (Portfolio & Projects)** + **CAP 9** | **ponte**: la ricerca unificata vive tra contenuti e portfolio |
| Cache di contenuto su file + invalidazione (SR) | **CAP 9** + **CAP 11 (SEO/cache)** | **nuovo box** (rimando): "cache senza Redis: file JSON" |
| `author` reale / sempre 'Admin' / inesistente | **CAP 9 §3** | **nuovo box** (ponte S1-C2/C3): "quando la sessione non contiene ciò che credi" |
| Schema vivo non ricostruibile (DIS) | **CAP 3** + **CAP 14** | **ponte**: prova pratica di "l'init mente" (S1-C1) |

**Correzioni al testo attuale (la mappatura smentisce / disallinea il libro):**
- **CAP 9 §2.2 — la conversione `T`↔spazio è data come "lo standard", ma è una sola delle tre
  strategie.** Il libro impone la conversione bidirezionale `datetime-local` (`T`) ↔ DB (spazio) come
  regola universale. In realtà è l'approccio (e il punto dolente) di **SR** — il cui incidente è
  documentato in `debug_time.php`. **SPW** risolve diversamente (forza `Europe/Rome` e confronta in
  PHP), **DIS** ancora diversamente (`CURRENT_TIMESTAMP` SQLite in UTC, che evita il problema-stringa
  ma ne introduce uno UTC-vs-locale). Da riscrivere come "tre strategie del presente", ciascuna col
  suo modo di sbagliare, invece di una prescrizione unica.
- **CAP 9 §4 — il "passaggio esclusivo all'architettura RDBMS Multi-Tagging" non è universale.** È
  vero **solo per SPW**, e perfino lì non è "esclusivo": `syncArticleTags` mantiene **in parallelo** il
  campo CSV legacy `articles.tags` come cache di retrocompatibilità (doppia scrittura). **SR** e **DIS**
  non hanno affatto tag relazionali: `category` è una stringa libera e i "tag" sono un campo
  TEXT/JSON. Da correggere: il multi-tagging è un'opzione del modello (quando il sito è un blog
  tassonomico), non lo standard di tutti; e va documentato il doppio binario.
- **CAP 9 §1.1 — la matrice degli stati è il modello SPW.** `draft`/`published+future`/`published+past`
  è preciso per SPW, ma **SR** porta `status IS NULL` (status aggiunto fuori schema base → la lista
  pubblica fa `OR status IS NULL`) e **DIS** interroga ancora `status='scheduled'` (residuo di
  migrazione). Da annotare che la matrice "pulita" è un caso, e che gli altri due mostrano le cicatrici
  delle rispettive migrazioni.
- **CAP 9 §5 — il bypass è accurato per SPW, ma non è l'unica forma.** Il 404-non-403 e il doppio
  controllo `sessione + ?admin=true` sono di SPW (ottimi, da tenere). Aggiungere che SR realizza
  "pubblico vs admin" con **due query in due file** e DIS con un `if(!$isAdmin)` nello stesso endpoint:
  stessa idea, tre strutture.

## 5. Cosa si scarta / dedup

- **Ripetizioni fuse:** i §6 delle tre card confrontavano lo stesso dominio (SPW tabella 13 righe vs
  SR, SR tabella 14 righe vs SPW, DIS tabella a TRE 13 righe). Qui la comparazione è scritta **una
  volta sola**, deduplicata, dal punto di vista della scala ricco→grado-zero.
- **Dettaglio per-sito che NON entra nel libro:** numeri di riga, il PATCH "un solo pin per categoria"
  di SPW (resta come micro-box opzionale), l'`X-Cache: HIT/MISS` come header diagnostico esatto, la
  lista speaker "alleggerita" senza `long_bio`, i nomi delle singole migrazioni (`v2.9.1`/`v0.5.4`).
  Restano nelle card come fonte.
- **Materiale che appartiene ad altre schede (per evitare doppioni a valle):**
  - **il lato client** del contratto (Double Read, guardia `Array.isArray`, buste lette per forma) →
    **S1-C3 (Frontend Bridge)**; qui solo il lato *server* che lo produce.
  - **gate, ruoli, 404-non-403 come misura di sicurezza, asimmetria editor/admin** sui domini →
    **S1-C2 (Security & Auth)**; qui solo *dove* il gate è applicato e quali audience serve.
  - **`cover_image`/`content` come stringa-percorso**, WebP, sottocartelle → **S1-C5 (Media)**; qui i
    contenuti salvano solo il path.
  - **`content` grezzo + sanitizzazione render-time** (DOMPurify, Tiptap) → **S1-C6 (Editor)**.
  - **cache `seo_*` generata su save, prerender, SEO** → **S1-C7 (SEO)**; qui solo la cache di
    *contenuto* (`news_*.json`) come tratto dell'endpoint.
  - **storia delle migrazioni** (`v2.9.1` status, `v0.5.4` scheduled→published, schema-solo-nel-file)
    → **S1-C13 (DB Evolution)**; qui solo il *sintomo* nel codice vivo (cicatrici, residui).
  - **`participants`/`votes` come "contenuto" del festival** → **S1-C10 (Festival Logic)**: non sono
    contenuto editoriale.
