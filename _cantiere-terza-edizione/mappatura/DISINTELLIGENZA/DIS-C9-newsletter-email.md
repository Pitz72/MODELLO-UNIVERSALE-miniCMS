# Mappatura — DISINTELLIGENZA — C9: Newsletter & Email (+ contact)

> **Stato:** COMPLETATO
> **Sessione:** 26 · **Data:** 2026-06-18 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `DISINTELLIGENZA/`)
> - `public/api/newsletter.php` (subscribe/unsubscribe pubblici + stats/send admin; `mail()` nativa)
> - `public/api/contact.php` (form contatti pubblico: validazione write-time, salvataggio, notifica email)
> - `public/api/update_db_0_1_3.php:9-34` (schema `newsletter_subscribers`/`contacts`/`newsletter_campaigns`, DIS-C1)
> - richiami: `participants.php:10-16,184-189` (sendEmail + INSERT newsletter all'approvazione — DIS-C10) · `stats.php:44-48` (sendVotingReport — DIS-C10)
> - confronto: `SPW-C9-newsletter-email.md`, `SR-C9-newsletter-email.md`

## 1. Cosa fa (sintesi narrativa)

C9 è il **sistema di posta** di DISINTELLIGENZA: la newsletter (iscrizione, disiscrizione, invio
campagne) e il form contatti. Come tutto il resto del sito è **thin stack** e — coerentemente con
DIS-C2 — è la versione **più grezza dei tre siti**: trasporto via **`mail()` nativa** ovunque,
**nessun double opt-in**, **nessun token di disiscrizione**, **nessun rate-limit**. In cambio ha due
buone abitudini di igiene che SR aveva perso: la **validazione dell'email** con `FILTER_VALIDATE_EMAIL`
e la **sanitizzazione write-time** (`strip_tags`) sul form contatti.

Due file:

- **`newsletter.php`** — un endpoint `?action=` con due livelli. **Pubblico**: `subscribe` (valida
  l'email e fa `INSERT` in `newsletter_subscribers`, **attivo da subito**, niente conferma) e
  `unsubscribe` (GET, mette `is_active = 0` **per sola email, senza token**). **Admin** (`role==admin`):
  `stats` (conteggio iscritti) e `send` (compone la newsletter HTML con articoli `news` e la spedisce
  a tutti gli iscritti attivi in un **`foreach mail()` sincrono**, poi salva la campagna).
- **`contact.php`** — form contatti **interamente pubblico** (niente sessione): valida `name`/`email`/
  `message` (con `strip_tags` + `FILTER_VALIDATE_EMAIL`), salva in `contacts` (con IP grezzo) e manda
  una notifica email all'admin via `mail()`.

L'email del sito vive però **anche fuori da C9**: i template comici di concorso e l'iscrizione
automatica alla newsletter all'approvazione di un partecipante stanno in `participants.php` (DIS-C10),
e il report finale votazioni in `stats.php`/`settings.php`. Il **trasporto** (`mail()`) è
**duplicato** in ognuno di questi file, non centralizzato.

## 2. Pattern miniCMS rilevanti

- **Trasporto `mail()` nativo, duplicato per file** (`newsletter.php:121-129`, `contact.php:38-42`,
  `participants.php:10-16`, `stats.php:44-48`): nessuna libreria (no PHPMailer/SMTP come SR), nessun
  helper condiviso. Ogni file costruisce i propri header `MIME-Version`/`Content-type`/`From` e chiama
  `mail()`. Massima semplicità, zero deliverability hardening (no SPF/DKIM, no SMTP autenticato).
- **Iscrizione SENZA double opt-in** (`newsletter.php:21-22` + schema `is_active DEFAULT 1`,
  `update_db_0_1_3.php:13`): `INSERT` diretto e iscritto **subito attivo**. Nessun `confirmation_token`,
  nessuna email di conferma. È l'opposto del double opt-in di SPW-C9 e SR-C9. Conseguenza: chiunque può
  iscrivere un'email altrui (niente prova di possesso della casella).
- **Validazione email con `FILTER_VALIDATE_EMAIL`** (`newsletter.php:13,51`, `contact.php:18`): igiene
  di base presente su tutti gli ingressi email (a differenza di `participants.php` che non la fa,
  DIS-C2). Buona pratica.
- **Sanitizzazione WRITE-TIME sul form contatti** (`contact.php:17,19`): `strip_tags` su `name` e
  `message` prima dell'`INSERT`. È lo stesso pattern "neutralizza all'origine" di SPW-C11 (messages):
  lo stored-XSS è disinnescato in scrittura. Buona pratica (con un buco sugli a-capo, vedi §4).
- **Idempotenza iscrizione via catch del duplicato** (`newsletter.php:24-31`): nessun pre-check, prova
  l'`INSERT` e **cattura la violazione UNIQUE** (codice 23000) restituendo "Sei già iscritto!" come
  *successo*. Stesso pattern reattivo dello slug news di DIS-C4 e anti-enumeration soft.
- **Newsletter HTML con articoli + escape totale dell'output** (`newsletter.php:75-118`): la campagna
  pesca `news` per id, ne stampa `title`/`excerpt`/`cover_image` **tutti via `htmlspecialchars`** e
  l'`intro` via `htmlspecialchars`+`nl2br`. **Non** emette `news.content` (il body grezzo). Quindi,
  come SPW/SR, la newsletter è un emettitore **sicuro per escape** (vedi §4).
- **Link di disiscrizione personalizzato via placeholder** (`newsletter.php:112,128`): il footer
  contiene `...?action=unsubscribe&email={EMAIL}` e per ogni destinatario `{EMAIL}` è sostituito con
  `urlencode($email)`. Personalizzazione per-destinatario senza token (vedi §4).
- **Storicizzazione campagne** (`newsletter.php:134-135`): ogni invio registra una riga in
  `newsletter_campaigns` (`subject`, `content`=intro, `recipients_count`, `sent_by`=user_id). Audit
  trail minimale degli invii.
- **Gate "pubblico-poi-admin" nello stesso file** (`newsletter.php:12-42`): le azioni pubbliche
  (`subscribe`) sono gestite **prima** del gate admin; poi un blocco nega tutto tranne `unsubscribe`;
  poi le azioni admin. Stessa struttura "a strati per posizione" di SR, fragile per ordine (DIS-C2).

## 3. Codice chiave (stralci con origine)

**Iscrizione: valida email, INSERT diretto attivo, idempotenza via 23000** — `newsletter.php:12-32`:

```php
if ($action === 'subscribe') {
    $email = filter_var($input['email'] ?? '', FILTER_VALIDATE_EMAIL);
    if (!$email) { echo json_encode(['status'=>'error','message'=>'Email non valida']); exit; }
    try {
        $stmt = $pdo->prepare("INSERT INTO newsletter_subscribers (email) VALUES (?)");  // is_active DEFAULT 1: attivo subito
        $stmt->execute([$email]);
        echo json_encode(['status'=>'success','message'=>'Iscrizione completata']);     // NESSUN double opt-in
    } catch (PDOException $e) {
        if ($e->getCode() == 23000) { echo json_encode(['status'=>'success','message'=>'Sei già iscritto!']); }
        else { echo json_encode(['status'=>'error','message'=>'Errore database']); }
    }
    exit;
}
```

**Disiscrizione PUBBLICA, GET, per sola email SENZA token** — `newsletter.php:50-58`:

```php
if ($action === 'unsubscribe') {
    $email = filter_var($_GET['email'] ?? '', FILTER_VALIDATE_EMAIL);
    if (!$email) { echo "Email invalida"; exit; }
    $stmt = $pdo->prepare("UPDATE newsletter_subscribers SET is_active = 0 WHERE email = ?");
    $stmt->execute([$email]);                       // chiunque conosca l'email può disiscriverla
    echo "<h1>Disiscrizione confermata</h1>...";
    exit;
}
```

**Invio campagna: foreach `mail()` sincrono senza throttle, newsletter escapata** — `newsletter.php:117-135`:

```php
$stmt = $pdo->query("SELECT email FROM newsletter_subscribers WHERE is_active = 1");
$recipients = $stmt->fetchAll(PDO::FETCH_COLUMN);
$count = 0;
foreach ($recipients as $email) {
    $personalHtml = str_replace('{EMAIL}', urlencode($email), $html);
    mail($email, $subject, $personalHtml, $headers);   // sincrono, niente usleep/throttle, return ignorato
    $count++;
}
$pdo->prepare("INSERT INTO newsletter_campaigns (subject, content, recipients_count, sent_by) VALUES (?, ?, ?, ?)")
    ->execute([$subject, $intro, $count, $_SESSION['user_id']]);
```

**Form contatti pubblico: write-time `strip_tags` + IP grezzo + notifica admin** — `contact.php:14-42`:

```php
$name    = strip_tags($input['name'] ?? '');                       // sanitizzazione in SCRITTURA
$email   = filter_var($input['email'] ?? '', FILTER_VALIDATE_EMAIL);
$message = strip_tags($input['message'] ?? '');
if (!$name || !$email || !$message) { /* 400 */ }
$pdo->prepare("INSERT INTO contacts (name, email, message, ip_address) VALUES (?, ?, ?, ?)")
    ->execute([$name, $email, $message, $_SERVER['REMOTE_ADDR']]);  // IP in chiaro (PII)
$subject = "Nuovo Messaggio da $name - Disintelligenza";           // $name nel Subject (vedi §4: header injection)
$headers = "From: no-reply@disintelligenza.runtimeradio.com\r\nReply-To: $email\r\n...";
mail('runtimeradio@gmail.com', $subject, $body, $headers);
```

## 4. Problemi riscontrati & soluzioni

- **GOLD — newsletter senza double opt-in: iscrizione di terzi.** `subscribe` (`newsletter.php:21`)
  rende l'email **attiva da subito** (`is_active DEFAULT 1`), senza email di conferma né token. Chiunque
  può iscrivere l'indirizzo di un altro: nessuna prova di possesso della casella. SPW-C9 e SR-C9
  risolvono entrambi con un **confirmation_token** (double opt-in). → Box "double opt-in: perché
  l'iscrizione immediata è un problema" (contrappunto a SPW/SR).
- **GOLD — disiscrizione senza token (chiunque può disiscrivere chiunque).** `unsubscribe`
  (`newsletter.php:50-55`) è una **GET pubblica** che imposta `is_active = 0` **per sola email**, senza
  un `unsubscribe_token` segreto. Conoscendo (o indovinando) l'email di un iscritto la si può
  disiscrivere; ed essendo GET è **prefetchabile** (un crawler/anteprima link può disiscrivere
  passandoci sopra). SPW usa un `unsubscribe_token` random stabile proprio per questo. → Box
  "il link di disiscrizione ha bisogno di un segreto" (ponte SPW-C9).
- **GOLD — possibile email header injection via `name` nel form contatti.** `contact.php:17` usa
  `strip_tags($name)`, che rimuove i tag HTML **ma non gli a-capo** `\r\n`. Quel `$name` finisce nel
  **Subject** dell'email all'admin (`:36`). Un `name` contenente `\r\n` potrebbe iniettare header
  aggiuntivi nella mail (Cc/Bcc) verso l'admin. L'`email` (usata in `Reply-To`) è invece filtrata da
  `FILTER_VALIDATE_EMAIL`, quindi sicura; il vettore è il nome. → Box "sanitizzare per il DB ≠
  sanitizzare per gli header email" (alto valore didattico).
- **GOLD — invio sincrono senza throttle né gestione errori.** Il `foreach mail()` (`newsletter.php:
  127-131`) spedisce a tutti gli iscritti **nello stesso request**, **senza `usleep`/coda** (SR aveva
  almeno `usleep` ogni 10) e **ignorando il valore di ritorno** di `mail()` (nessun try/catch per
  destinatario). Su una lista grande → timeout PHP e nessuna traccia di quali invii siano falliti
  (`recipients_count` conta i *tentativi*, non i successi). → Box "inviare a una lista senza coda: i
  limiti del thin stack" (gemello dell'invio sincrono di SPW/SR, qui il più rozzo).
- **Nessun rate-limit su `subscribe`/`contact`.** Coerente con DIS-C2 (zero rate-limit nel sito):
  `subscribe` può essere martellato per riempire `newsletter_subscribers` di email finte (non c'è
  email di conferma, quindi non è mail-bombing di terzi — ma è inquinamento della lista); `contact`
  può essere usato per spam verso la casella admin. SPW riusava `login_attempts` per limitare; DIS no.
  → nota (ponte DIS-C2/C5: il sito è aperto e non limitato su più fronti).
- **Due percorsi d'iscrizione divergenti.** Un'email entra in `newsletter_subscribers` o via
  `newsletter.php?subscribe` (validata, idempotente) **oppure** via `participants.php:188` (`INSERT OR
  IGNORE` all'approvazione di un partecipante, DIS-C10) — quest'ultima **senza consenso esplicito**
  alla newsletter (i commenti di `participants.php:136-143` mostrano lo sviluppatore in dubbio proprio
  su questo). Due porte, una sola con consenso chiaro. → Box "consenso newsletter: l'iscrizione come
  effetto collaterale" (chiude il filo DIS-C10, GDPR).
- **Newsletter è un emettitore SICURO per escape (quadro emettitori).** Diversamente dal `content`
  grezzo salvato in DIS-C4 (difesa a render-time lato client), la newsletter **non** emette
  `news.content`: stampa solo `title`/`excerpt`/`cover_image`/`intro`, tutti via `htmlspecialchars`
  (`newsletter.php:90,103,104`). Quindi anche se un articolo contenesse HTML malevolo nel body, la
  newsletter non lo propaga. Sicuro per **escape** (come il feed di SR-C8, l'opposto-per-sottrazione di
  SPW). → nota cross-cluster (l'analisi completa dei "4 emettitori" di SPW/SR qui è più semplice perché
  l'editor/sanitizzazione di DIS non è stato mappato a fondo — DIS non ha un C6 dedicato).
- **`From` su dominio "fake?" + Reply-To gmail.** `newsletter.php:123` ha il commento esplicito
  "Fake domain?" sul `From: no-reply@disintelligenza.runtimeradio.com`: incertezza sulla reale
  esistenza/configurazione del dominio mittente → rischio deliverability/spam-folder (niente SPF/DKIM
  con `mail()`). Il `Reply-To` punta a `runtimeradio@gmail.com` (casella reale). → nota operativa.
- **IP grezzo salvato in `contacts`.** `contact.php:32` salva `REMOTE_ADDR` in chiaro (PII, come i
  voti di DIS-C2). Nessun hashing. → nota privacy (consolidare con DIS-C2 `votes`).
- **`stats` admin ma `unsubscribe` scavalca il gate.** L'ordine dei rami (`newsletter.php:36-42`) nega
  l'accesso non-admin **tranne** `unsubscribe`; corretto come intento, ma è di nuovo sicurezza "per
  posizione e per eccezione" anziché per gate esplicito per-ramo (DIS-C2).

## 5. Estetica / UX (moderna ma funzionale)

- **Newsletter HTML con forte identità visiva** (`newsletter.php:78-114`): palette
  crema/marrone/arancio, `Courier`, bordi spessi, bottoni "Leggi Peggio", titoli "Newsletter ufficiale
  del disastro" e footer "Non vuoi più ricevere queste email? Ottima scelta." La grafica email **è**
  brand voice (coerente con i template di concorso di DIS-C10).
- **Messaggi d'iscrizione parlanti** ("Iscrizione completata", "Sei già iscritto!"): l'idempotenza è
  presentata come successo, niente errore spaventoso per chi si re-iscrive.
- **Pagina di disiscrizione "umana"** (`newsletter.php:56`): risponde con un HTML "Disiscrizione
  confermata. Non riceverai più email dal Festival." invece di un JSON crudo — è un link cliccato da
  una mail, quindi una pagina ha senso (UX corretta per il contesto).
- **Cover image con fallback a URL assoluto** (`newsletter.php:99-101`): se la `cover_image` è un path
  relativo, viene prefissata col dominio (le immagini in email devono essere assolute). Cura del
  dettaglio che fa la differenza tra immagini rotte e visibili nei client di posta.

## 6. Differenze rispetto agli altri siti

Confronto a **TRE**: DIS-C9 (SQLite vivo) vs SPW-C9 e SR-C9 (MySQL migrati).

| Aspetto | SimonePizziWebSite (SPW-C9) | SitoRuntime (SR-C9) | **DISINTELLIGENZA (questa card)** |
|---|---|---|---|
| **Trasporto** | `mail()` nativa | **PHPMailer/SMTP** STARTTLS | **`mail()` nativa** (duplicata per file) |
| **Double opt-in** | sì (`confirm_token` monouso) | sì (un solo `confirmation_token`) | **NO** (iscritto attivo subito) |
| **Token disiscrizione** | `unsubscribe_token` random stabile | `confirmation_token` riusato | **NESSUNO** (per sola email, forgeable) |
| **Validazione email** | sì | sì | **sì** (`FILTER_VALIDATE_EMAIL`) |
| **Rate-limit** | riusa `login_attempts` per-IP | **assente** (mail-bombing) | **assente** |
| **CSRF** | `Auth::check` Origin/Referer | `validateCsrf` token | **assente** (DIS-C2) |
| **Sanitizzazione** | newsletter body grezzo (dietro admin) | escape `htmlspecialchars` | **escape** newsletter + **strip_tags write-time** su contact |
| **Invio** | `foreach mail()` sincrono | `foreach` + `usleep`/try-catch per dest. | **`foreach mail()` sincrono nudo** (il più rozzo) |
| **Emette `content`?** | no (body separato) | no (SELECT senza content) | **no** (solo title/excerpt/cover/intro escapati) |
| **Schema subscribers** | completo (token, stati) | 3 schemi divergenti | **minimale** (email/subscribed_at/is_active) |
| **Storicizzazione invii** | — | — | **`newsletter_campaigns`** (subject/count/sent_by) |
| **Header injection** | mitigato | mitigato | **possibile via `name` nel Subject contact** |

**Sintesi.** DIS-C9 è il sistema email **più scarno dei tre**: `mail()` nativa, **niente double
opt-in**, **niente token di disiscrizione**, niente rate-limit né CSRF, invio sincrono nudo. Ma —
controcorrente rispetto alla sua stessa filosofia grado-zero — porta **due note d'igiene** che
altrove erano disuguali: `FILTER_VALIDATE_EMAIL` su tutti gli ingressi e `strip_tags` **write-time**
sul form contatti (lo stesso choke-point all'origine di SPW-C11). I due buchi che lo distinguono in
negativo sono **strutturali del modello "senza token"**: iscrizione di terzi e disiscrizione di
chiunque. In più ha un dettaglio suo, l'**header injection via il nome** nel form contatti. Sul piano
positivo, è l'unico ad avere una tabella di **storicizzazione campagne**. Per il libro è il terzo
gradino della scala "quanto puoi semplificare un sistema di posta": SR toglieva il rate-limit, DIS
toglie anche il double opt-in e i token.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **Double opt-in: perché l'iscrizione immediata è un problema** | Cap. "Newsletter nel thin stack": il gradino DIS (senza conferma) vs SPW/SR |
| **Il link di disiscrizione ha bisogno di un segreto** (token) | Box "unsubscribe sicuro: token vs sola email" (ponte SPW-C9) |
| **Sanitizzare per il DB ≠ per gli header email** (`strip_tags` non toglie `\r\n`) | Box sicurezza "email header injection dal campo nome" (alto valore) |
| **Trasporto: `mail()` nativa vs PHPMailer/SMTP** | Box "tre modi di spedire una mail" (mail/mail/SMTP nei tre siti) |
| **Invio sincrono a una lista senza coda** | Box "perché serve una coda" (il più rozzo dei tre, ponte SPW/SR) |
| **Consenso newsletter come effetto collaterale** (iscrizione all'approvazione) | Box "consenso e GDPR: due porte d'iscrizione" (chiude DIS-C10) |
| **Idempotenza iscrizione via catch UNIQUE** | confluisce nel box "reattivo vs preventivo" (con slug DIS-C4) |
| **Storicizzazione campagne** (`newsletter_campaigns`) | Box "tenere traccia degli invii" |
| **Email come brand voice** (template comici, "Leggi Peggio") | Box "la grafica della posta è identità" (ponte DIS-C10) |

## 8. Note / domande aperte

- **Puntatori ad altri cluster** (annotati qui, NON mappati in questa card):
  - **Email di concorso** (template received/approved/rejected, `sendEmail`) e **iscrizione newsletter
    all'approvazione** vivono in `participants.php` → **C10** (già mappato): qui ho mappato il
    **trasporto** e il sistema newsletter; il *trigger* di concorso è C10. Il consenso GDPR di
    quell'`INSERT OR IGNORE` resta una domanda aperta condivisa.
  - **Report finale votazioni** (`sendVotingReport`, `stats.php`/`settings.php`) → **C10** (già
    mappato, disabilitato): stesso trasporto `mail()`.
  - **Compositore newsletter lato admin** (selezione articoli, intro, anteprima) e **inbox contatti**
    (lettura di `contacts`) → **C12** (Admin Dashboard): qui solo il lato server (`send`, salvataggio
    `contacts`); la UI è C12.
  - **`news` come contenuto della newsletter** → **C4** (già mappato): `send` pesca `news` per id;
    qui solo notato che la newsletter li impagina (escapati).
  - **Auth/CSRF/rate-limit/IP in chiaro** → **C2** (già mappato): C9 conferma l'assenza di CSRF e
    rate-limit e l'IP grezzo in `contacts` (gemello dei `votes`).
- **Da verificare in C12:** esiste una UI per leggere/gestire `contacts` e `newsletter_campaigns`? E
  un'anteprima della newsletter prima dell'invio?
- **Conferma schema (DIS-C1):** `newsletter_subscribers`/`contacts`/`newsletter_campaigns` sono create
  da `update_db_0_1_3.php` (non da `init_db.php`) — coerente con lo schema frammentato di DIS-C1.
- Versione del sito al momento della mappatura: **0.5.x** (`package.json`).
