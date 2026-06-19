# Scheda di Sintesi — S1-C11 — Engagement & Reactions (superfici di scrittura pubblica)

> **Stato:** COMPLETATO
> **Cluster FASE 2:** S1-C11 · **Data:** 2026-06-19 · **Commit:** _(in corso)_
> **Fonti (card di mappatura, in particolare i §6):** SPW-C11 (unico sito con reazioni) · contrappunti cross-sito: DIS-C9 (`contact.php` write-time `strip_tags`), DIS-C10 (voto festival), S1-C2 (voter_hash, IP grezzo, rate-limit), S1-C6 (sanitizzazione render-time)
> **Capitoli del libro toccati:** CAP 19 (Social Interactions & Reactions) — principale · ponti a CAP 10 (anti-abuso/rate-limit/identità anonima → S1-C2), CAP 8 (le due filosofie di sanitizzazione → S1-C6), CAP 13 (`mail()` fire-and-forget → S1-C9), CAP 18 (engagement leggero vs voto-competitivo → S1-C10) → vedi §4

---

## 0. In una frase
L'engagement anonimo è il **fronte di scrittura pubblica** del CMS — le **uniche due superfici** in cui
un visitatore non autenticato scrive nel DB (reazioni agli articoli e messaggi dal form contatti) — e
proprio perché è il punto più esposto concentra le difese più sofisticate del sito: identità anonima
derivata (`SHA256(IP+UA)`), anti-doppio-voto **a livello DB**, **rate-limit a due strati** e
sanitizzazione **al write-time**. Quest'ultima chiude il "filo dell'input pubblico" con **polarità
inversa** rispetto agli articoli: lì il contenuto admin-trusted è salvato grezzo e ripulito al *render*
(S1-C6); qui l'input pubblico-non-fidato è ripulito **alla scrittura** — due filosofie antitetiche di
sanitizzazione che convivono nello stesso codebase.

## 1. Il pattern comune — la filosofia "thin stack" su questa lente

Cluster sostanzialmente mono-sito (le **reazioni** esistono solo in SimonePizziWebSite), ma la lente —
"come il thin stack gestisce la scrittura pubblica non autenticata" — ha riscontri cross-sito sul lato
*messaggi/contatti* (presente anche in DIS-C9 e SR-C9). La forma canonica:

**1) Endpoint-router su `REQUEST_METHOD` con gate selettivo.** `messages.php` apre i rami privati
(`GET` lista, `PUT` marca-letto, `DELETE`) con `Auth::check()`, lascia il `POST` **pubblico** — speculare
a `subscribers.php` (S1-C9). Le reazioni sono interamente pubbliche (GET conteggi + POST toggle), **senza
alcun ramo admin** (il reset conteggi, se esiste, vive in analytics/C12).

**2) Identità anonima derivata, niente account né cookie.** Il votante è uno pseudonimo
`voter_hash = SHA256(IP + User-Agent)`; i messaggi hashano l'IP (`ip_hash`). Nessun dato personale
persistito in chiaro — *GDPR-by-design* (con i caveat del §3). È lo stesso pattern dell'IP hashato della
newsletter (S1-C9) e il contraltare *virtuoso* del voto festival che salva IP+UA **in chiaro** (DIS-C10,
S1-C2).

**3) L'integrità garantita dal DB, non solo dal codice.** L'anti-doppio-voto è una
`UNIQUE KEY (article_id, voter_hash, reaction)` + `INSERT IGNORE`: il duplicato è rifiutato dal database
anche sotto race condition/doppio click. Il codice applicativo fa il toggle (esiste→DELETE,
altrimenti→INSERT), ma la barriera vera è lo schema.

**4) Difesa dell'input pubblico al WRITE-TIME.** `name`/`subject`/`message` passano da
`strip_tags`+`filter_var` **prima** dell'`INSERT`: ciò che entra nel DB è già privo di tag → lo
stored-XSS è neutralizzato all'origine. È il pattern "neutralizza all'ingresso" — lo stesso `strip_tags`
write-time del `contact.php` di DIS (S1-C9), e l'**opposto** del content articoli (render-time, S1-C6).

**5) Degradazione graziosa + email best-effort.** Le reazioni degradano a conteggi-zero su qualsiasi
errore (la pagina articolo non si rompe mai); la notifica email dei messaggi è `mail()` nativa
*fire-and-forget* (return ignorato) — **il DB è la fonte di verità, l'email è best-effort** (stesso
trasporto e stessa filosofia di S1-C9).

## 2. Le varianti (tabella: SPW reale vs testo idealizzato vs riscontri cross-sito)

Cluster mono-sito: la tabella confronta **SPW (codice reale)**, **il testo del libro (CAP 19)** e i
**riscontri cross-sito** delle tecniche dove esistono altrove.

| Asse | SimonePizziWebSite (reale) | CAP 19 (idealizzato) | Cross-sito |
|---|---|---|---|
| **Reazioni** | 5 tipi toggle, plurime per articolo | descritte (5 tipi, toggle) | **solo SPW** (SR/DIS non le hanno) |
| **Messaggi/contatti** | `messages.php` POST pubblico + admin gated | **assente dal capitolo** | `contact.php` in DIS-C9 e SR-C9 (write-time `strip_tags` DIS) |
| **Identità anonima** | `SHA256(IP+UA)` **non salato** | "Hash SHA256 **salato**" (claim) | IP+UA **in chiaro** nel voto festival (DIS-C10) → contrappunto |
| **Anti-doppio-voto** | `UNIQUE KEY` + `INSERT IGNORE` (DB) | sì (UNIQUE KEY) | barriera IP/24h nel voto festival (DIS, diversa) |
| **Rate-limit** | **DUE strati**: voter_hash 20/min + **solo-IP 30/min** (`login_attempts`, v1.19.0) | **UNO** strato, mislabeled "per IP, 20/min" | riuso `login_attempts` come throttle generico (S1-C2/C9) |
| **Sanitizzazione input** | **write-time** `strip_tags` (messaggi) | non discussa | write-time anche in DIS `contact.php`; render-time per articoli (S1-C6) |
| **Render admin** | text-node React (auto-escape), **no** `dangerouslySetInnerHTML` | non discusso | opposto del render articoli con `dangerouslySetInnerHTML`+DOMPurify (S1-C6) |
| **Sorgente IP** | **raw** `REMOTE_ADDR` (non `getClientIp` di S1-C2) | non discusso | `getClientIp` anti-spoof esiste in S1-C2 ma qui non usato |
| **Consenso GDPR (form)** | doppio checkbox **solo client** (backend non verifica) | non discusso | singolo/implicito altrove (S1-C9/C10) |

**Lettura della tabella.** Il modulo reazioni è **maturo e ben difeso** (anti-doppio-voto a livello DB,
rate-limit a due strati, identità anonima), ma il CAP 19 lo descrive nella versione *semplificata e un
po' edulcorata*: dichiara l'hash "salato" (non lo è), chiama "per IP" un limite che è per `voter_hash`,
**omette il secondo strato** (la vera difesa anti-UA-rotation) e **ignora del tutto i messaggi**, che
sono metà del cluster e portano il GOLD delle "due filosofie di sanitizzazione". La lente cross-sito
utile è che la **scrittura pubblica** è trattata in modo coerente nel Modello: identità hashata + difesa
all'ingresso — con SPW che la realizza nella forma più completa, e gli altri siti che ne hanno solo il
ramo *contatti*.

## 3. GOLD & box problemi-soluzioni

- **Le due filosofie di sanitizzazione, una di fronte all'altra** — *(SPW; salda il filo input-pubblico
  di S1-C6)* — è il GOLD portante. Nello **stesso codebase** convivono due strategie opposte: il
  **content degli articoli** (admin-trusted) è salvato **grezzo** e ripulito **al render** con DOMPurify
  (S1-C6); il **testo dei messaggi** (input pubblico non-fidato) è ripulito **alla scrittura** con
  `strip_tags`, così ciò che arriva al DB è già innocuo. Non è un'incoerenza: è la **scelta giusta per
  ciascun contesto** — l'input pubblico va neutralizzato il prima possibile (write-time), il contenuto
  ricco editoriale va preservato e sanitizzato dove serve la fedeltà (render-time). Doppia difesa sui
  messaggi: anche il pannello admin li rende come **text-node React** (auto-escape) senza
  `dangerouslySetInnerHTML`. → Box "Write-time vs render-time: dove ripulire l'input" (**alto valore**,
  chiude il filo S1-C6; oggi CAP 19 non lo tratta).

- **Il rate-limit a due strati: perché uno solo non basta** — *(SPW)* — il primo limite è su `voter_hash`
  (IP+UA, 20/min), ma lo **User-Agent è controllato dal client**: ruotandolo si genererebbe un hash nuovo
  a ogni richiesta, aggirando il limite. La v1.19.0 aggiunge un **secondo argine ancorato al solo IP**
  (30/min) riusando `login_attempts` con namespace `rea:`. È il caso di studio perfetto:
  *quando la chiave di rate-limit include input del client, serve un secondo strato su una chiave che il
  client non controlla*. → Box "Un solo strato di rate-limit non basta se la chiave include input del
  client" (**alto valore**; corregge CAP 19 §4 che descrive un solo strato).

- **L'identità anonima e i limiti del claim GDPR** — *(SPW; rimando S1-C2)* — `voter_hash =
  SHA256(IP+UA)` non persiste dati personali in chiaro: buono. Ma il CAP 19 lo dice **"salato"** e
  afferma che "non permette di risalire all'IP" — **inesatto**: l'hash **non è salato**, e lo spazio
  degli IP è piccolo abbastanza da rendere `SHA256(IP+UA)` **reversibile per forza bruta**. È
  pseudonimizzazione utile (meglio dell'IP in chiaro del voto festival, DIS-C10), ma il claim
  "anonimo/irreversibile" è sovradichiarato. → Box "Hash non è anonimato: pseudonimizzazione e i suoi
  limiti" (corregge CAP 19 §3; ponte S1-C2 voter_hash).

- **L'integrità che vive nello schema, non nel codice** — *(SPW)* — `UNIQUE KEY (article_id, voter_hash,
  reaction)` + `INSERT IGNORE`: il doppio voto è impossibile **per costruzione del DB**, non per una
  `if` applicativa che una race condition potrebbe scavalcare. È il principio "il database come guardiano
  dell'integrità", lo stesso che manca al `vote_count` denormalizzato del festival (S1-C10, dove l'assenza
  di reconciliation apre il drift). → Box "Lasciare l'integrità al database" (ponte S1-C10, contrasto).

- **L'IP grezzo invece dell'helper anti-spoof** — *(SPW; rimando S1-C2)* — sia `reactions.php` sia
  `messages.php` usano il **raw** `$_SERVER['REMOTE_ADDR']`, non il `getClientIp()` anti-spoof introdotto
  in S1-C2: dietro proxy/CDN può collassare tutti i visitatori su un IP (rate-limit troppo aggressivo) o
  mancare l'IP reale. Da notare che qui — come nel voto festival (S1-C2) — l'IP grezzo ha anche un lato
  *non-spoofabile*; ma l'incoerenza con l'helper esistente resta. → rimando S1-C2.

- **Email fire-and-forget: il DB è la verità** — *(SPW; ponte S1-C9)* — la notifica del messaggio è
  `mail()` nativa col **return ignorato**: se l'invio fallisce il visitatore vede comunque "Messaggio
  inviato!" perché il record è già salvato. Scelta difendibile (il messaggio non si perde), ma da
  raccontare: l'email è un *side-channel* best-effort, non la conferma dell'azione. Stesso trasporto e
  stessa filosofia della newsletter (S1-C9). → confluisce nel box email di S1-C9.

- **Engagement leggero vs voto-competitivo: due mondi della "scrittura pubblica"** — *(SPW vs DIS)* — le
  reazioni di SPW e il voto festival di DIS (S1-C10) sono entrambi "scrittura pubblica anonima" ma con
  intenti opposti: la reazione è **libera e plurima** (puoi dare più reazioni diverse allo stesso
  articolo, il toggle è reversibile, l'anti-abuso è soft), il voto è **singolo e sorvegliato** (una sola
  espressione, barriera IP/24h, master switch). Stesso pattern tecnico (identità hashata, anti-doppio),
  due tarature di rigidità a seconda della posta in gioco. → Box "Reazione vs voto: tarare l'anti-abuso
  sulla posta in gioco" (ponte S1-C10).

## 4. Mappa → capitolo/i del libro

| Materiale della scheda | Capitolo esistente | Azione |
|---|---|---|
| **Rate-limit a due strati** (voter_hash + solo-IP) | **CAP 19 §4** | **riscrivi**: §4 descrive un solo strato e lo mislabella "per IP" (vedi correzioni) |
| **Le due filosofie di sanitizzazione** (write-time messaggi vs render-time articoli) | **CAP 19** (nuovo box) + **CAP 8** | **nuovo box** ad alto valore (chiude il filo S1-C6; oggi assente) |
| **`messages.php`: la seconda superficie pubblica** (POST pubblico + admin gated, write-time, auto-scaffolding) | **CAP 19** (nuova sez.) | **espandi**: il capitolo è solo-reazioni; i messaggi sono metà del cluster |
| **Identità anonima: hash ≠ anonimato** | **CAP 19 §3** | **correggi**: l'hash non è "salato" né irreversibile (ponte CAP 10/S1-C2) |
| **Anti-doppio-voto a livello DB** | **CAP 19 §5-6** | **ok** (già presente); collega al contrasto col drift del festival (S1-C10) |
| **IP grezzo vs `getClientIp`** | **CAP 19** + **CAP 10** | **rimanda a S1-C2** (uniformare la sorgente IP) |
| **Optimistic UI con rollback** (ReactionBar) | **CAP 19** (UX) + **CAP 6** | **aggiungi**: micro-interazione resiliente (oggi non descritta) |
| **Consenso GDPR solo client** | **CAP 19** + privacy | **nota**: il backend non verifica i checkbox |
| **`mail()` fire-and-forget** | **CAP 13** (ponte) | **rimanda a S1-C9** |
| **Engagement leggero vs voto festival** | **CAP 19** + **CAP 18** | **nuovo box**: tarare l'anti-abuso sulla posta in gioco |

**Correzioni al testo attuale (la mappatura smentisce / disallinea il libro):**
- **CAP 19 §4 descrive UN solo strato di rate-limit e lo chiama "per IP, 20/min".** Nel codice il limite
  20/min è su **`voter_hash` (IP+UA)**; il vero limite **per-solo-IP** (30/min, su `login_attempts`) è un
  **secondo strato** aggiunto in v1.19.0 proprio perché il primo è aggirabile ruotando lo User-Agent.
  Da riscrivere documentando entrambi gli strati e il *perché* del secondo (il GOLD del cluster).
- **CAP 19 §3 dichiara l'hash "salato" e "non permette di risalire all'IP".** Il codice reale è
  `SHA256(IP+UA)` **senza salt**, e con lo spazio IP ridotto è **reversibile per forza bruta**: è
  pseudonimizzazione, non anonimato irreversibile. Da correggere il claim (e, se si vuole renderlo vero,
  aggiungere davvero un salt segreto server-side).
- **CAP 19 ignora completamente `messages.php`.** Il cluster engagement ha **due** superfici di scrittura
  pubblica (reazioni *e* messaggi); il capitolo tratta solo le reazioni. Vanno aggiunti i messaggi con il
  loro GOLD: sanitizzazione **write-time**, auto-scaffolding della tabella, rate-limit sulla propria
  tabella, render admin auto-escapato.
- **CAP 19 omette le due filosofie di sanitizzazione** (write-time vs render-time), che è il ponte più
  prezioso verso CAP 8 (S1-C6): da introdurre come box.
- **Versione:** il capitolo dice "ispirato a SimonePizziWebSite (v2.0)"; SPW è a **v1.21.0** e le
  reazioni datano v1.0.0/v1.13.0 (rate-limit secondo strato v1.19.0). Da correggere il riferimento.

## 5. Cosa si scarta / dedup

- **Materiale già consolidato altrove (richiamato, non ri-mappato):**
  - **identità hashata, IP grezzo vs `getClientIp`, rate-limit come meccanica, `login_attempts` come
    tabella-throttle universale** → **S1-C2** (qui solo l'*applicazione* alle reazioni/messaggi e il
    GOLD del doppio strato).
  - **la sanitizzazione render-time del content + DOMPurify + `dangerouslySetInnerHTML`** → **S1-C6**
    (qui solo il *contrasto* write-time/render-time).
  - **`mail()` nativa fire-and-forget, trasporto, il `contact.php` di DIS/SR** → **S1-C9** (qui solo il
    ramo notifica dei messaggi).
  - **il voto festival (barriera IP/24h, master switch, vote_count)** → **S1-C10** (qui solo il
    *contrasto* engagement-leggero/voto-competitivo).
  - **l'aggregazione delle reazioni in `analytics.php` e il reset conteggi** → **S1-C12** (admin); qui
    solo notato che `reactions.php` non ha ramo admin.
- **Dettaglio per-sito che NON entra nel libro:** numeri di riga, i nomi/label esatti delle 5 reazioni e
  le loro icone SVG, i numeri precisi dei rate-limit (20/30/3), il destinatario email hardcoded, il
  versionamento ambiguo del banner (v1.0.0 vs v1.13.0 vs v1.19.0). Restano nella card SPW-C11 come fonte.
- **Perché la scheda è mono-sito ma non isolata:** le reazioni esistono solo in SPW, ma la lente
  "scrittura pubblica anonima difesa all'ingresso" ha agganci reali su tre cluster già scritti (S1-C2
  identità/rate-limit, S1-C6 sanitizzazione, S1-C9 contatti/email, S1-C10 voto) — la scheda vale
  soprattutto come **nodo che li collega** e come correzione del CAP 19, non come nuova mappatura.
