# Scheda di Sintesi — S1-C9 — Newsletter & Email

> **Stato:** COMPLETATO
> **Cluster FASE 2:** S1-C9 · **Data:** 2026-06-19 · **Commit:** _(in corso)_
> **Fonti (card di mappatura, in particolare i §6):** SPW-C9, SR-C9, DIS-C9 (+ FDCA-DIFF: backend = DIS, `mail()` nativa senza opt-in ereditata → fuori scala)
> **Capitoli del libro toccati:** CAP 13 (Newsletter & Email System) — principale · ponti a CAP 8/11/12 (gli altri tre emettitori del `content` → da S1-C6/C7/C8), CAP 10 (rate-limit/header-injection/CSRF, il riciclo di `login_attempts`), CAP 9 (consenso/visibilità), CAP 16-18 (consenso implicito festival DIS), CAP 14 (i tre schemi `subscribers` di SR) → vedi §4

---

## 0. In una frase
La newsletter **chiude definitivamente il "quadro dei quattro emettitori del `content`"** (S1-C6→C7→C8):
è il 4°/ultimo emettitore e **nessuno dei tre siti emette `content`** — quindi il buco XSS non si riapre
nemmeno qui. Ma proprio perché il rischio XSS è chiuso, la lente vera del cluster diventa un'altra: la
**scala "quanto puoi semplificare un sistema di posta"** — double opt-in pieno + rate-limit (SPW) →
SMTP autenticato ma un-token-per-tutto e rate-limit assente (SR) → `mail()` nuda senza opt-in né token
(DIS) — dove ogni semplificazione toglie una difesa, e il sito col **backend più ricco (SR) lascia il
buco più grave** (mail-bombing), confermando la tesi di S1-C2 "più ingegnerizzato ≠ più sicuro".

## 1. Il pattern comune — la filosofia "thin stack" su questa lente

Tutti e tre i siti hanno una newsletter **fatta in casa, senza servizi esterni**, e condividono cinque
tratti.

**1) Endpoint-router su `?action=` con gate pubblico→admin nello stesso file.** Le azioni pubbliche
(`subscribe`, `unsubscribe`) sono servite *prima* di un gate centrale; tutto ciò che segue
(`count`/`list`/`send`/…) è admin. È il pattern endpoint-router di S1-C4 applicato alla posta — SPW lo
spezza in due file (`subscribers.php` + `newsletter_send.php`), SR e DIS lo concentrano in un
`newsletter.php` ALL-IN-ONE con il confine pubblico/admin segnato da un solo `if` a metà file.

**2) Validazione email server-side + iscrizione idempotente "per cattura del duplicato".** Tutti usano
`FILTER_VALIDATE_EMAIL` lato server (non si fidano del form) e gestiscono la ri-iscrizione provando
l'`INSERT` e **catturando la violazione UNIQUE (23000)** come *successo* ("Sei già iscritto!") — niente
pre-check, e anti-enumeration soft (non si rivela chi è già in lista). Stesso pattern reattivo dello
slug in S1-C4.

**3) Disiscrizione morbida via `is_active=0`.** Nessuno cancella il record: l'iscritto è marcato
inattivo, preservando la storia e prevenendo re-iscrizioni accidentali. La disiscrizione risponde
**HTML** (non JSON) perché è un link cliccato dentro una mail.

**4) Newsletter HTML a tabelle + CSS inline + cover assoluta.** L'email è costruita una volta come
stringa HTML con un **placeholder** per il link di disiscrizione, poi `str_replace` per-destinatario;
layout a tabelle e stili inline per i client di posta; le `cover_image` relative sono rese assolute. Il
footer porta sempre informativa GDPR + link disiscrizione.

**5) Il `content` non entra MAI nell'email.** La query di invio seleziona `title`/`summary|excerpt`/
`cover_image`/`slug` — **mai `content`** — e l'email rimanda all'articolo con un "Leggi tutto →". È la
chiusura del filo dei quattro emettitori (§3): la newsletter è "snella" *e* sicura perché non tocca il
campo HTML grezzo difeso solo a render-time (S1-C6).

Sopra questa base condivisa, i tre siti divergono su **quanto del ciclo di vita** implementano (double
opt-in? token? rate-limit? quale trasporto?) — ed è lì che vive il valore della scheda.

## 2. Le varianti per sito (tabella unica, deduplicata)

| Asse | SimonePizziWebSite | SitoRuntime | DISINTELLIGENZA | *(FDCA)* |
|---|---|---|---|---|
| **Geografia** | **due file** (`subscribers.php` + `newsletter_send.php`) | **un file** ALL-IN-ONE `newsletter.php` (gate a metà) | **un file** `newsletter.php` (+ `contact.php`) | = DIS |
| **Trasporto** | `mail()` nativa ovunque | **PHPMailer/SMTP** STARTTLS (newsletter) + `mail()` (contact) → **due trasporti** | `mail()` nativa, **duplicata per file** | = DIS |
| **Double opt-in** | **sì** — `confirm_token` monouso (azzerato) | **sì** — un solo `confirmation_token` | **NO** — iscritto `is_active=1` subito | = DIS |
| **Token disiscrizione** | **`unsubscribe_token`** random stabile, separato | **lo stesso** `confirmation_token` (doppio scopo) | **nessuno** — disiscrizione per sola email | = DIS |
| **Rate-limit subscribe** | **sì** — ricicla `login_attempts` (3/15min, anti-mail-bombing) | **NO** — IP solo memorizzato (XFF grezzo) → **mail-bombing** | **NO** | = DIS |
| **CSRF mutazioni** | `Auth::check` (Origin/Referer) | `validateCsrf` (token) | **assente** (S1-C2) | = DIS |
| **Emette `content`?** | **no** | **no** | **no** | = DIS |
| **Sanitizzazione output** | body `intro` **grezzo** (ZERO sanit.), salvo perché dietro Auth | **tutto `htmlspecialchars`** | **tutto `htmlspecialchars`** | = DIS |
| **Posizione nei "4 emettitori"** | 4° e **MENO** sanitizzato | 4° e **PIÙ** sanitizzato | 4° e sicuro (per escape) | = DIS |
| **Filtro `status` nell'invio** | implicito (`getArticles({admin:false})`) | **esplicito** `status='published'` (unico SR che NON lo dimentica) | (news per id, escapate) | = DIS |
| **Throttle invio** | **nessuno** | `usleep` ogni 10 + `try/catch` per-destinatario | **nessuno** (il più rozzo) | = DIS |
| **Invio** | `foreach mail()` sincrono nella request | `foreach` SMTP sincrono nella request | `foreach mail()` sincrono nudo | = DIS |
| **Schema `subscribers`** | completo (token, stati) via `migrate_newsletter.php` (deploy-and-delete) | **3 verità divergenti** (init_mysql base / fix_ fossile SQLite / `apply_v293` self-healing) | minimale (email/`is_active`) via `update_db_0_1_3` | = DIS |
| **Storicizzazione invii** | `newsletter_sends` | — | `newsletter_campaigns` (subject/count/sent_by) | = DIS |
| **Consenso/GDPR (form)** | **doppio** checkbox (trattamento + 16+) | **singolo** checkbox (variante `minimal` senza) | + iscrizione **implicita** all'approvazione festival (S1-C10) | = DIS |
| **Header injection** | mitigato | mitigato (`From` non da input) | **possibile** via `name` nel Subject di `contact.php` | = DIS |
| **Link-poisoning** | difeso (`SITE_URL` canonico, mai `HTTP_HOST`) | **non si pone** (URL hardcoded `runtimeradio.com`) | non difeso (host nel link) | = DIS |

**Lettura della tabella.** Sull'asse sicurezza-XSS i tre **convergono** (nessuno emette `content` →
quadro chiuso, §3). Su tutto il resto emerge la **scala "quanto puoi togliere a un sistema di posta"**:
**SPW** è il gradino completo (due file, double opt-in con *due* token distinti, rate-limit anti-mail-
bombing, link-poisoning difeso) — paga solo sul body `intro` non sanitizzato (ma è dietro Auth) e
sull'invio sincrono. **SR** aggiunge il trasporto più "serio" (SMTP autenticato) e l'unico throttle, ma
*toglie* il rate-limit (→ mail-bombing) e *fonde* i due token in uno solo riusato e senza TTL. **DIS**
toglie anche il double opt-in e ogni token: iscrizione di terzi e disiscrizione di chiunque diventano
strutturali — ma porta due note d'igiene che SR aveva perso (`FILTER_VALIDATE_EMAIL` ovunque +
`strip_tags` write-time sul contact). Il ribaltamento-chiave (gemello di S1-C2/C5): **il sito col
backend più ricco — SR — lascia il buco operativo più grave** (il form che spara email a nome tuo),
proprio dove SPW, più semplice, lo aveva chiuso.

**FDCA è fuori scala:** backend PHP byte-identico a DIS → eredita `mail()` nuda, niente opt-in, niente
token, header-injection inclusa. Caso fork.

## 3. GOLD & box problemi-soluzioni

- **Il quadro dei QUATTRO emettitori — qui si CHIUDE definitivamente** — *(cross-sito; salda
  S1-C6→C7→C8→C9)* — è il valore trasversale della scheda. Lo stesso campo (`content`, salvato grezzo,
  S1-C6) ha quattro render-path con **quattro policy diverse e nessuna condivisa**; la newsletter è il
  quarto, e in tutti e tre i siti **non emette `content`** → il quadro si chiude senza riaprire il buco:

  | # | Emettitore | Cosa emette del `content` | Sanitizzazione | Esito |
  |---|---|---|---|---|
  | 1 | **Render React** (S1-C6) | `content` pieno | **DOMPurify** (tag+attributi) — *DIS ne è privo* | ✅ sicuro (⚠️ scoperto in DIS) |
  | 2 | **Prerender crawler** (S1-C7) | `content` pieno | `strip_tags` **allowlist** (solo tag) | ⚠️ **buco sugli attributi** (SPW, SR; DIS immune) |
  | 3 | **Feed RSS** (S1-C8) | niente (SPW/DIS) · preview 500c (SR) | — / `strip_tags`+`htmlspecialchars` | ✅ sicuro (sottrazione o escape) |
  | 4 | **Newsletter** (**questa scheda**) | **niente** (tutti e tre: solo `title`/`summary`/`intro`) | grezzo dietro-Auth (SPW) · `htmlspecialchars` (SR/DIS) | ✅ sicuro (la newsletter non tocca `content`) |

  Esito finale del filo: **l'unica falla che resta aperta in tutto il quadro è la riga 2** — il buco
  sugli attributi del prerender (S1-C7), su SPW e SR. Curiosità ulteriore: SPW e SR sono *speculari* sul
  meno-sanitizzato — in SPW la newsletter è il 4° e **meno** sanitizzato (body `intro` grezzo, salvo
  solo perché dietro Auth), in SR è il 4° e **più** sanitizzato (non emette content + escapa tutto). La
  lezione resta quella di S1-C6/C7: *serve una sanitizzazione server-side condivisa da tutti gli
  emettitori del `content`*, invece di N policy ad hoc — il feed e la newsletter dimostrano che "non
  emettere il campo pericoloso" funziona, ma è disciplina umana, non architettura. → Box "Una
  sanitizzazione, quattro render-path: il filo che si chiude" (**altissimo valore**, perno
  S1-C6/C7/C8; chiude il ponte).

- **Il form che spara email a nome tuo: il rate-limit dimenticato** — *(SR, contrasto SPW)* — la
  `subscribe` di SR **non throttla affatto**: l'IP è catturato (`subscribed_ip`) ma **solo memorizzato,
  mai usato come limite**, e preso da `X-Forwarded-For` grezzo (spoofabile). Chiunque può fare POST con
  email arbitrarie e far partire email di conferma **SMTP verso terzi**, senza limiti → bruciamento
  reputazione dominio + consumo quota SMTP. L'infrastruttura `.cache/ratelimit/` (S1-C2) **esiste** e
  non è stata riusata. SPW invece chiude il vettore riciclando la tabella `login_attempts` (prefisso
  `sub:`, IP hashato, 3/15min) con commento esplicito sul mail-bombing. È il difetto-gemello opposto:
  SPW lo aveva chiuso, SR — col backend più ricco — lo lascia aperto. → Box "Il form che spara email a
  nome tuo: rate-limit ≠ throttle" (**alto valore**, ponte CAP 10).

- **Rate-limit vs throttle: due cose diverse spesso confuse** — *(SPW vs SR)* — il `usleep(500000)` ogni
  10 invii di SR (e l'omonimo nel CAP 13) è un **throttle anti-greylisting** (proteggere *il mail server*
  dal sovraccarico in uscita), **non** un **rate-limit anti-abuso** (proteggere *il sistema* da chi
  martella l'iscrizione). SR ha il throttle ma non il rate-limit; SPW ha il rate-limit ma non il
  throttle. Sono difese ortogonali a layer diversi (l'una sull'invio, l'altra sull'ingresso). → Box
  "Throttle in uscita ≠ rate-limit in ingresso" (corregge CAP 13 §6.3, che chiama "Rate Limiting" il
  throttle).

- **Double opt-in a tre gradini, e i due token che diventano uno (e poi zero)** — *(SPW → SR → DIS)* —
  il double opt-in è la garanzia che chi iscrive un'email **possiede quella casella**. SPW lo fa col
  manuale: `confirm_token` monouso (azzerato all'uso) + `unsubscribe_token` random **stabile e separato**.
  SR lo fa ma con **un solo `confirmation_token`** che serve a confermare *e* a disiscrivere, **mai
  azzerato e senza TTL** — con due conseguenze: l'email promette *"il link scade dopo il primo utilizzo"*
  (falso, sopravvive all'uso) e ogni newsletter **espone il confirmation_token** nell'URL di
  disiscrizione (chi inoltra la mail può disiscrivere quell'utente). DIS **non ha opt-in né token**:
  iscrizione attiva subito (chiunque iscrive l'email altrui) e disiscrizione **per sola email**
  (chiunque disiscrive chiunque, e via GET → prefetch-able). → Box "Double opt-in e il segreto del link
  di disiscrizione" (perno; corregge CAP 13 §4 che chiama la versione senza-token "GDPR-Compliant").

- **Sanitizzare per il DB ≠ sanitizzare per gli header email** — *(DIS)* — `contact.php` applica
  `strip_tags($name)`, che rimuove i tag HTML **ma non gli a-capo `\r\n`**; quel `$name` finisce nel
  **Subject** dell'email all'admin → un nome con `\r\n` può **iniettare header** (Cc/Bcc). L'`email`
  (in `Reply-To`) è invece blindata da `FILTER_VALIDATE_EMAIL`: il vettore è il *nome*. SR mitiga
  mettendo nel `From` un valore non derivato dall'input; SPW non espone input pubblico negli header. È
  l'esempio didattico perfetto che *la sanitizzazione ha un contesto*: write-time per il DB non protegge
  il contesto-header. → Box "Email header injection dal campo nome" (alto valore, ponte CAP 10).

- **Invio sincrono nella request: perché serve una coda** — *(tutti e tre, scala di rozzezza)* — l'intero
  invio è un `foreach` bloccante dentro la richiesta HTTP: su liste grandi → `max_execution_time`/timeout
  e consegna parziale invisibile. È lo stesso anti-pattern "lavoro pesante sincrono nella request" della
  conversione WebP (S1-C5). I tre gradini: SR è il meno peggio (`usleep` + `try/catch` per-destinatario,
  conta gli errori), SPW conta solo il booleano di `mail()` (nessun retry/bounce), DIS è il più rozzo
  (nessun throttle, **ignora il valore di ritorno** → `recipients_count` conta i *tentativi*, non i
  successi). Nessuno ha coda/cron. → Box "Inviare a una lista senza coda: i limiti del thin stack"
  (ponte CAP 14/scalabilità).

- **Tre verità per una tabella: lo schema `subscribers` di SR** — *(SR)* — SR ha **tre punti** che
  "creano" `subscribers` con tre schemi diversi: `init_mysql.php` (base, 4 colonne, pre-opt-in);
  `fix_newsletter_table.php` (fossile **SQLite** — `sqlite_master`/`PRAGMA`/`AUTOINCREMENT`, si
  romperebbe su MySQL e comunque ricrea solo le 4 colonne minime); `apply_v293_newsletter` dentro
  `admin.php` (la **vera** migrazione double opt-in, self-healing, con conferma retroattiva degli
  iscritti storici via `HEX(RANDOM_BYTES(32))`). Solo l'ultimo è allineato al runtime, che **presuppone**
  lo schema esteso: su un DB con solo lo schema base ogni query fallisce finché `apply_v293` non gira
  (dipendenza d'ordine non dichiarata). È la "tabella che nessuno crea due volte uguale" già vista in
  S1-C4/C1. → confluisce nel box di **S1-C13** (DB Evolution); qui solo il sintomo lato newsletter.

- **Il trasporto: `mail()` nativa vs SMTP autenticato — e i due trasporti coesistenti** — *(scala +
  SR)* — SPW e DIS usano `mail()` nativa (sendmail di sistema: zero config ma deliverability fragile, no
  SPF/DKIM — DIS ha persino il commento `// Fake domain?` sul `From`). SR usa **PHPMailer/SMTP STARTTLS**
  con segreti da `.env` (primo uso reale di `lib/` vendored) — ma **solo per la newsletter**: `contact.php`
  resta su `mail()` nativa → **due meccaniche di posta nello stesso sito**. SMTP autenticato è il
  gradino "deliverability seria"; il prezzo è la coesistenza incoerente. → Box "Spedire dal thin stack:
  sendmail vs SMTP autenticato" (nuovo).

- **Telegram fossile: il filo si chiude qui** — *(SR; ponte S1-C1/C8)* — il `TELEGRAM_BOT_TOKEN` nei
  segreti di SR (S1-C1) **non è usato da nessun file PHP** (grep negativo su `telegram|sendMessage`).
  L'unico "Telegram" è un microcopy admin: *"Usa questo link nel tuo Bot Telegram per pubblicare le
  news"* — cioè l'admin incolla **a mano** l'URL del feed (S1-C8) in un bot esterno. L'integrazione
  automatica **non esiste**: è coerente col `feed_config.php` security-theater di S1-C8 e col GUID `urn`
  anti-ripubblicazione di S1-C8 (pensato proprio per un consumatore bot mai costruito). Il token è il
  relitto di un'intenzione mai realizzata. → chiude il filo "Telegram fossile" (ponte S1-C1/C8).

- **Consenso come effetto collaterale: l'iscrizione implicita** — *(DIS; ponte S1-C10)* — un'email entra
  in `newsletter_subscribers` o via `subscribe` (con consenso) **o** via `participants.php` (`INSERT OR
  IGNORE` all'approvazione di un partecipante al festival) **senza consenso esplicito** alla newsletter —
  e i commenti nel sorgente mostrano lo sviluppatore in dubbio proprio su questo. Due porte d'iscrizione,
  una sola con consenso chiaro. → Box "Consenso e GDPR: l'iscrizione come effetto collaterale" (ponte
  CAP 16-18 festival).

## 4. Mappa → capitolo/i del libro

| Materiale della scheda | Capitolo esistente | Azione |
|---|---|---|
| **Double opt-in con due token** (confirm monouso + unsubscribe stabile) | **CAP 13** (nuova sez. centrale) | **riscrivi**: oggi CAP 13 **non menziona affatto** il double opt-in (vedi correzioni) |
| **Il quadro dei 4 emettitori, CHIUSO** | **CAP 13** (box) + ponti **CAP 8/11/12** | **nuovo box** ad altissimo valore: la tabella dei 4 emettitori che si chiude sulla newsletter |
| **Il form che spara email a nome tuo** (rate-limit assente SR) | **CAP 13** + **CAP 10** | **nuovo box**: il vettore mail-bombing e il riuso di `login_attempts` (SPW) |
| **Rate-limit (ingresso) ≠ throttle (uscita)** | **CAP 13 §6.3** | **correggi**: §6.3 chiama "Rate Limiting" il `usleep` (è throttle anti-greylisting) |
| **Token disiscrizione: serve un segreto** | **CAP 13 §4** | **correggi**: §4 presenta l'unsubscribe-by-email come "GDPR-Compliant" — è la versione forgeable/prefetch-able |
| **Email header injection dal nome** (DIS) | **CAP 13** + **CAP 10** | **nuovo box**: `strip_tags` non toglie `\r\n` |
| **Trasporto: `mail()` vs PHPMailer/SMTP** (+ due trasporti SR) | **CAP 13 §8** | **amplia**: oggi §8 cita SMTP solo come "scalabilità futura"; SR lo usa già in prod |
| **Invio sincrono senza coda** (3 gradini) | **CAP 13 §8** + scalabilità | **nuovo box**: l'anti-pattern, gemello del WebP (S1-C5) |
| **Tre schemi `subscribers`** (SR) | **CAP 13 §1** + **CAP 14** | **nota** + ponte: lo schema reale di SR ha i token (non quello minimale di §1) |
| **Consenso implicito festival** (DIS) | **CAP 13** + **CAP 16-18** | **nuovo box**: due porte d'iscrizione |
| **Form GDPR doppio/singolo checkbox** | **CAP 13** (UX) | **aggiungi**: la variante `minimal` senza checkbox è un gap |

**Correzioni al testo attuale (la mappatura smentisce / disallinea il libro):**
- **CAP 13 OMETTE interamente il double opt-in**, che è la feature-cardine di **due siti su tre** (SPW e
  SR). Il capitolo mostra una `subscribe` che rende l'email attiva *subito* (`INSERT` → `is_active=1`) e
  una `unsubscribe` *per sola email senza token* — cioè **il modello DIS** (il più debole) — e lo
  attribuisce a **SitoRuntime**, il cui runtime reale ha invece `confirmation_token`, conferma via email
  e schema esteso (`apply_v293_newsletter`). Da riscrivere documentando il double opt-in (token, stati
  `pending/confirmed/unsubscribed`) come pattern principale, con il modello senza-conferma come *gradino
  minimo* (DIS), non come standard.
- **CAP 13 §4 chiama "GDPR-Compliant" la disiscrizione per sola email.** È invece la versione
  **insicura**: senza `unsubscribe_token` chiunque conosca l'email disiscrive l'utente, ed essendo una
  **GET** è prefetch-able (un client di posta può disiscrivere passandoci sopra). La versione conforme è
  quella di SPW (token random stabile + idealmente POST di conferma). Da correggere.
- **CAP 13 §6.3 chiama "Rate Limiting" il `usleep(500000)`.** È un **throttle anti-greylisting** (ritmo
  in uscita), non un rate-limit anti-abuso (limite in ingresso). Il vero rate-limit (SPW che ricicla
  `login_attempts`) **non è nel capitolo**, e la sua assenza in SR è il buco mail-bombing. Da
  distinguere i due concetti e aggiungere il rate-limit in ingresso.
- **CAP 13 §6.4 dà la query senza `content` solo come "ottimizzazione di payload".** È vero ma riduttivo:
  è anche (e soprattutto) la **chiusura del filo XSS dei 4 emettitori** — la newsletter non tocca il
  campo grezzo. Da collegare al box sicurezza (CAP 8/11/12).
- **CAP 13 omette:** il vettore **mail-bombing** (rate-limit assente), l'**header injection** dal nome,
  il trasporto **SMTP/PHPMailer** realmente in uso (relegato a "scalabilità futura" in §8 mentre SR lo
  usa già), i **due trasporti coesistenti** di SR, i **due token distinti** di SPW, la **storicizzazione
  campagne**, il **consenso implicito** festival. Sono dimensioni reali del cluster assenti dal capitolo.

## 5. Cosa si scarta / dedup

- **Ripetizioni fuse:** i §6 di SPW-C9, SR-C9 e DIS-C9 erano la stessa comparazione da tre lati (con
  SPW↔SR come "cuore" sia di SPW-C9 che di SR-C9, e DIS-C9 che la estendeva a tre). Qui la comparazione è
  scritta **una volta sola** nella tabella del §2, sulla scala "quanto puoi semplificare la posta"; il
  quadro dei 4 emettitori — che le tre card riportavano ciascuna a modo suo — è consolidato in **una
  sola tabella** nel §3 (riga 4 finalmente piena per tutti).
- **Dettaglio per-sito che NON entra nel libro:** numeri di riga, i nomi esatti delle 8/11 azioni admin,
  le palette delle email (verde SPW / teal SR / crema-arancio DIS), i microcopy ("Leggi Peggio",
  "Newsletter ufficiale del disastro"), le 3 varianti del `NewsletterForm` di SR, l'endpoint diagnostico
  `test_smtp`, la lunghezza-password esposta. Restano nelle card come fonte.
- **Materiale che appartiene ad altre schede:**
  - **gli altri tre emettitori del `content`** (render/prerender/feed) → **S1-C6/C7/C8** (qui solo la
    riga 4 e la chiusura del quadro).
  - **i tre schemi `subscribers` come storia evolutiva del DB + l'invio sincrono come potenziale
    incidente di timeout** → **S1-C13** (qui solo i sintomi lato newsletter).
  - **CSRF / `Auth::check` / `validateCsrf` / `login_attempts` come *meccanica*, IP grezzo come PII** →
    **S1-C2** (qui solo *usati*: il riuso di `login_attempts` come throttle generico, l'IP in `contacts`).
  - **il festival (approvazione partecipanti, report votazioni, master switch)** → **S1-C10** (qui solo
    il *trigger* dell'iscrizione implicita).
  - **`news`/`status`/`published_at`/slug, `cover_image`/WebP, `SITE_URL` vs `HTTP_HOST`, singleton PDO,
    PHPMailer vendored in `lib/`** → **S1-C1/C4/C5** (già consolidati); qui solo consumati.
  - **i pannelli admin** (Newsletter Studio, compositore, inbox `contacts` write-only, `test_smtp`) →
    **S1-C12** (qui solo il lato server `send`/salvataggio).
