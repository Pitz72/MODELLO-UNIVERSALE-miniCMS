# Mappatura — SitoRuntime — C9: Newsletter & Email

> **Stato:** COMPLETATO
> **Sessione:** 17 (SR-C9 da sola) · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito `SitoRuntime/`)
> - `public/api/newsletter.php` (**l'endpoint unico ALL-IN-ONE**: subscribe/confirm/unsubscribe pubblici + 8 azioni admin compreso `send`)
> - `public/api/contact.php` (form contatti pubblico, trasporto `mail()` NATIVA — il *secondo* trasporto del sito)
> - `public/api/fix_newsletter_table.php` (micro-migrazione one-shot dello schema `subscribers` — **fossile SQLite**, gated `.htaccess` `^fix_`)
> - `public/api/admin.php:373-396` (`apply_v293_newsletter` — la VERA migrazione double opt-in, self-healing) · `:398-445` (`test_smtp` diagnostica)
> - `public/api/init_mysql.php:47-56` (schema base `subscribers` — solo 4 colonne, pre-double-opt-in)
> - `public/api/lib/phpmailer/*` (PHPMailer vendored — **primo uso reale**, chiude il puntatore di SR-C1)
> - `src/components/NewsletterForm.tsx` (form pubblico 3 varianti) · `src/components/admin/NewsletterComposer.tsx` ("Newsletter Studio" 2 tab)
> - `src/pages/Unsubscribe.tsx` (`src/App.tsx:70` rotta `/unsubscribe`) · `src/api.ts:150-210` (11 metodi client)
> - Mount form: `src/pages/Article.tsx:174`, `Contact.tsx:233`, `Home.tsx:470`, `News.tsx:186`
> - `public/api/db_credentials.php:27-31` (`SMTP_*` dai segreti, `.env`) — controprova `TELEGRAM_BOT_TOKEN:21` **non usato** da nessun file di C9

---

## 1. Cosa fa (sintesi narrativa)

C9 in SitoRuntime è una newsletter **fatta in casa con double opt-in**, come in SPW, ma con tre divergenze
strutturali forti:

1. **Un solo file ALL-IN-ONE.** Dove SPW spezzava in due (`subscribers.php` + `newsletter_send.php`),
   SR concentra TUTTO in `newsletter.php`: i tre flussi pubblici (`?action=subscribe|confirm|unsubscribe`)
   e — dopo un **gate centrale** `isLoggedIn() && role==='admin'` (`newsletter.php:177`) — otto azioni admin
   (`count`, `list_subscribers`, `resend_confirmation`, `confirm_subscriber`, `revoke_subscriber`,
   `reactivate_subscriber`, `delete_subscriber`, `send`). È l'endpoint-router su `?action=` portato
   all'estremo, con il confine pubblico/admin segnato da un singolo `if` a metà file.

2. **Trasporto via PHPMailer/SMTP**, non `mail()` nativa. È il **primo uso reale** della libreria
   PHPMailer vendored in `lib/` (vista dormiente in SR-C1): `createMailer()` (`newsletter.php:47-64`)
   costruisce un client SMTP con STARTTLS leggendo `SMTP_HOST/USER/PASS/PORT/FROM_NAME` da
   `db_credentials.php` (i segreti `.env` di SR-C1). Divergenza netta dalla `mail()` nativa di SPW-C9.

3. **Due trasporti email coesistono nello stesso sito.** `contact.php` (form contatti) NON usa PHPMailer:
   manda con **`mail()` nativa** (`contact.php:37`) verso `runtimeradio@gmail.com` hardcoded. Quindi SR ha
   *due* meccaniche di posta — SMTP autenticato per la newsletter, sendmail di sistema per i contatti — una
   dicotomia che SPW non ha (lì è `mail()` ovunque).

Il ciclo di vita dell'iscritto: il form crea un record `is_active=0` con un `confirmation_token` (64 hex);
l'email di conferma porta a `?action=confirm` che setta `is_active=1, confirmed_at=NOW()`; il link di
disiscrizione in fondo a ogni newsletter chiama `?action=unsubscribe`. La composizione/invio è una tab del
pannello admin "Newsletter Studio".

## 2. Pattern miniCMS rilevanti

- **Endpoint-router ALL-IN-ONE con gate a metà file** (`newsletter.php:69-181`): i rami pubblici precedono
  il gate `if (!isLoggedIn() || role!=='admin') 403`, tutto ciò che segue è admin. Lo stesso file serve due
  audience separate da una sola riga — variante estrema del pattern `?action=` già visto in `admin.php` (C4).
- **Double opt-in con token `random_bytes(32)`→64 hex** (`newsletter.php:80`), come SPW e come i token di
  C2. Ma **un solo token** fa doppio servizio (conferma *e* disiscrizione): non esiste un
  `unsubscribe_token` separato (cfr. §4 e §6).
- **Anti-enumeration**: la `subscribe` ritorna sempre lo stesso messaggio neutro ("Controlla la tua email…")
  sia per un'email nuova sia per una già confermata (`newsletter.php:88-91`), per non rivelare chi è iscritto.
- **CSRF a token sincronizzato (C2) sulle mutazioni admin**: `validateCsrf()` su `resend_confirmation`,
  `confirm_subscriber`, `revoke_subscriber`, `reactivate_subscriber`, `delete_subscriber`, `send`
  (`newsletter.php:211,235,251,265,281,295`). Le letture admin (`count`, `list_subscribers`) sono GET senza
  CSRF. Coerente con la meccanica X-CSRF-Token di SR-C2/C3.
- **Migrazione self-healing idempotente** (`admin.php:373-396`, `apply_v293_newsletter`): `ALTER TABLE … ADD
  COLUMN` per-colonna con skip su `Duplicate column` + UPDATE retroattivo che conferma gli iscritti
  esistenti e genera loro un token (`HEX(RANDOM_BYTES(32))`). Stesso spirito "deploy-and-run" di SPW, ma
  **dentro `admin.php`** (gated admin) anziché in uno script da cancellare.
- **Throttle minimale anti-greylisting nell'invio** (`newsletter.php:364`): `if ($count % 10 === 0)
  usleep(500000)` — mezzo secondo ogni 10 email. SPW non aveva alcun ritmo; SR ne ha uno (rudimentale).
- **Resilienza per-destinatario nell'invio** (`newsletter.php:359-362`): ogni `send()` è in un `try/catch`
  che incrementa `$errors` e prosegue; il loop non si interrompe sul primo bounce (meglio del booleano
  secco di SPW).

## 3. Codice chiave (stralci con origine)

**Trasporto SMTP via PHPMailer (primo uso di `lib/`, segreti da `db_credentials.php`)** — `newsletter.php:47-64`:

```php
function createMailer(): \PHPMailer\PHPMailer\PHPMailer {
    require_once __DIR__ . '/lib/phpmailer/Exception.php'; /* … PHPMailer.php, SMTP.php … */
    $cfg = getSmtpConfig();                       // = require db_credentials.php (.env)
    $mail = new \PHPMailer\PHPMailer\PHPMailer(true);
    $mail->isSMTP();
    $mail->Host = $cfg['SMTP_HOST']; $mail->SMTPAuth = true;
    $mail->Username = $cfg['SMTP_USER']; $mail->Password = $cfg['SMTP_PASS'];
    $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS; $mail->Port = $cfg['SMTP_PORT'];
    $mail->setFrom($cfg['SMTP_USER'], $cfg['SMTP_FROM_NAME']);
    return $mail;
}
```

**Subscribe: nessun rate-limit, IP solo memorizzato (X-Forwarded-For grezzo)** — `newsletter.php:71-103`:

```php
$ip    = trim(explode(',', $_SERVER['HTTP_X_FORWARDED_FOR'] ?? $_SERVER['REMOTE_ADDR'] ?? '')[0]);
$token = bin2hex(random_bytes(32));
// … check anti-enumeration … INSERT/UPDATE con confirmation_token, subscribed_ip = $ip …
sendConfirmationEmail($email, $token);   // ← parte SUBITO, nessun throttle per-IP (cfr. §4 GOLD)
```

**L'invio: SELECT senza `content`, tutto escapato — il PONTE XSS è chiuso** — `newsletter.php:306,330,339-340`:

```php
$stmt = getDB()->prepare("SELECT id, title, slug, summary, cover_image FROM news
                          WHERE id IN ($placeholders) AND status = 'published' ORDER BY published_at DESC");
// ↑ NIENTE content selezionato; e — unico tra gli emettitori — filtra status='published'
// …
if ($intro) $html .= '…' . nl2br(htmlspecialchars($intro)) . '…';                 // intro pubblico-zero (admin) escapato
$html .= '<h2>…' . htmlspecialchars($art['title']) . '…</h2>';                     // title escapato
$html .= '<p>…' . htmlspecialchars($art['summary']) . '…</p>';                     // summary escapato
```

**Un solo token per conferma E disiscrizione (mai azzerato)** — `newsletter.php:139,159,324`:

```php
// confirm: setta is_active+confirmed_at, MA NON azzera confirmation_token
getDB()->prepare("UPDATE subscribers SET is_active = 1, confirmed_at = NOW() WHERE confirmation_token = ?")->execute([$token]);
// unsubscribe: cerca per lo STESSO token
$stmt = getDB()->prepare("SELECT id FROM subscribers WHERE confirmation_token = ? AND is_active = 1");
// send: l'URL di disiscrizione ESPONE il confirmation_token
$unsubUrl = 'https://runtimeradio.com/unsubscribe?token=' . urlencode($sub['confirmation_token']);
```

**La VERA migrazione dello schema double opt-in (self-healing, gated admin)** — `admin.php:378-391`:

```php
$cols = ['confirmation_token' => "ALTER TABLE subscribers ADD COLUMN confirmation_token VARCHAR(64) NULL",
         'confirmed_at' => "…", 'subscribed_at' => "…", 'subscribed_ip' => "…"];
foreach ($cols as $col => $sql) {
    try { $db->exec($sql); } catch (\PDOException $e) {
        if (strpos($e->getMessage(), 'Duplicate column') !== false) {/* skip */} else throw $e; }
}
$db->exec("UPDATE subscribers SET confirmed_at = NOW(), … confirmation_token = HEX(RANDOM_BYTES(32))
           WHERE is_active = 1 AND confirmed_at IS NULL");   // conferma retroattiva degli iscritti storici
```

**Il fossile SQLite che NON produce lo schema reale** — `fix_newsletter_table.php:12,17-22,27`:

```php
$stmt = $pdo->query("SELECT name FROM sqlite_master WHERE type='table' AND name='subscribers'"); // ← SQLite!
$pdo->exec("CREATE TABLE IF NOT EXISTS subscribers (id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1)");                  // ← solo 4 colonne, niente confirmation_token
$pdo->query("PRAGMA table_info(subscribers)");               // ← PRAGMA: rompe su MySQL
```

## 4. Problemi riscontrati & soluzioni

- **🔒 GOLD — CHIUSURA DEFINITIVA DEL PONTE C6/C7/C8: la newsletter NON emette `news.content`, ed è
  l'emettitore PIÙ sicuro dei quattro.** L'invio (`newsletter.php:306`) seleziona `id, title, slug,
  summary, cover_image` — **mai `content`**. Quindi, a differenza del feed C8 (che ne emetteva un preview di
  500c), la newsletter di SR **non tocca affatto** il campo HTML grezzo difeso a render-time da DOMPurify
  (C6). In più, ogni campo dinamico che finisce nell'HTML è **escapato con `htmlspecialchars`**: `title`
  (`:339`), `summary` (`:340`), e l'`intro` admin con `nl2br(htmlspecialchars())` (`:330`). Quadro completo
  dei **QUATTRO emettitori** dello stesso dato, ora CHIUSO:
    | Emettitore | Cosa emette | Sanitizzazione | Esito |
    |---|---|---|---|
    | React `Article.tsx` (C6) | `content` pieno | **DOMPurify** (tag+attributi) | ✅ pieno e sicuro |
    | Prerender `index.php:318` (C7) | `content` pieno | `strip_tags` **allowlist** (solo tag) | ⚠️ buco sugli attributi |
    | Feed `feed_news_rss.php:40` (C8) | **preview 500c** di `content` | `strip_tags` (tutti) + `htmlspecialchars` | ✅ sicuro (testo escapato) |
    | **Newsletter `newsletter.php` (C9)** | **NIENTE `content`** (solo `title`/`summary`/`intro`) | `htmlspecialchars` su tutto | ✅✅ **il più sicuro** (sottrazione + escape) |
  **Morale:** SR è speculare a SPW ma con esito opposto sul *meno* sanitizzato. In SPW la newsletter era il
  **4°/ULTIMO e MENO** sanitizzato (body grezzo `buildNewsletterHtml` ZERO sanitizzazione, salvo solo perché
  dietro Auth). In SR la newsletter è il 4° e **PIÙ** sanitizzato (non emette content + escapa tutto). Il
  ponte XSS-stored è chiuso **per sottrazione E per escape**. Unico input pubblico del cluster (l'`email` di
  conferma) non viene nemmeno stampato in HTML grezzo. **Ponte C6→C7→C8→C9: CHIUSO su tutti i fronti.**

- **🔒 GOLD — Nessun rate-limit sulla `subscribe`: vettore di mail-bombing.** A differenza di SPW (che
  riciclava `login_attempts` con prefisso `sub:`, max 3/15min, commento esplicito sul mail-bombing),
  `newsletter.php` **non throttla affatto** l'iscrizione. L'IP viene catturato (`subscribed_ip`,
  `:79`) ma **solo memorizzato, mai usato come limite**; e viene preso da `HTTP_X_FORWARDED_FOR` grezzo
  (spoofabile — stesso difetto del rate-limit di SR-C2). Conseguenza: chiunque può fare POST con email
  arbitrarie e far partire email di conferma SMTP verso terzi, senza limiti → bruciamento reputazione
  dominio + consumo quota SMTP. Esiste già l'infrastruttura `.cache/ratelimit/` (SR-C2) che NON è stata
  riusata qui. È il difetto-gemello opposto a SPW: SPW lo aveva chiuso, SR lo lascia aperto. **Alto valore
  didattico** (box "il form che spara email a nome tuo").

- **Tre schemi `subscribers` divergenti — cicatrice di evoluzione DB.** (→ C13)
  - `init_mysql.php:49-55`: schema **base** a 4 colonne (`id, email, created_at, is_active`),
    pre-double-opt-in. **Non** contiene `confirmation_token`/`confirmed_at`/`subscribed_at`/`subscribed_ip`.
  - `fix_newsletter_table.php`: micro-migrazione **fossile SQLite** (usa `sqlite_master`, `PRAGMA
    table_info`, `AUTOINCREMENT`) che ricrea le **stesse 4 colonne** minime. Su MySQL si romperebbe; e
    comunque **non** produce le colonne che `newsletter.php` richiede. È un relitto morto come `init_db.php`
    di SR-C1.
  - `admin.php:378-391` (`apply_v293_newsletter`): la **vera** migrazione che aggiunge le 4 colonne del
    double opt-in e conferma retroattivamente gli iscritti storici. → SitoRuntime ha **tre punti** che
    "creano" la stessa tabella con tre verità diverse; solo l'ultimo è allineato al runtime. Il runtime
    `newsletter.php` **presuppone** lo schema esteso: su un DB con solo lo schema base, ogni query fallisce
    finché `apply_v293_newsletter` non è stato eseguito (dipendenza d'ordine non dichiarata).

- **Un solo token per conferma e disiscrizione, mai azzerato, senza TTL.** Non esistono `confirm_token`
  monouso + `unsubscribe_token` stabile (come in SPW): c'è **un unico `confirmation_token`** che (a) conferma
  l'iscrizione e (b) resta valido per sempre come token di disiscrizione (`:139` non lo azzera, `:159`/`:324`
  lo riusano). Implicazioni: l'email di conferma promette *"Il link scadrà dopo il primo utilizzo"*
  (`newsletter.php:39`) — **falso**, il token sopravvive all'uso. E ogni newsletter inviata **espone il
  confirmation_token** nell'URL di disiscrizione (`:324`): chi intercetta/inoltra una mail può disiscrivere
  quell'utente (rischio basso, ma il token non dovrebbe avere doppio scopo).

- **Disiscrizione (e conferma) via GET, prefetch-able.** `Unsubscribe.tsx:16` chiama
  `?action=unsubscribe` con una GET al mount della pagina; e `?action=confirm` è anch'essa una GET che muta
  stato. I client di posta che fanno **prefetch dei link** possono disiscrivere/confermare per errore. Stesso
  difetto di SPW-C9; qui aggravato dal fatto che il token di disiscrizione è il token di conferma.

- **Invio sincrono `foreach` nella request HTTP.** Come SPW, l'intero invio è un loop bloccante dentro la
  richiesta (`:322-365`). Su liste grandi → rischio `max_execution_time`. SR mitiga col `usleep` ogni 10
  (anti-greylisting) e col `try/catch` per-destinatario, ma resta lo stesso anti-pattern "lavoro pesante
  sincrono nella request" già visto in SR-C5 (WebP) e SPW-C9 — nessuna coda/cron. → candidato C13 se è già
  emerso un incidente di timeout.

- **`contact.php`: pubblico, senza CSRF/auth/rate-limit, trasporto `mail()` nativa.** Form contatti che manda
  a `runtimeradio@gmail.com` hardcoded. Mitigazioni presenti: sanitizzazione **write-time**
  (`strip_tags`+`htmlspecialchars(ENT_QUOTES)` su `name`/`message`, `FILTER_VALIDATE_EMAIL` sull'email,
  `:9-11`) e `From: no-reply@$SERVER_NAME` (non da input utente) → **header-injection mitigata** (l'email
  validata non passa CRLF). Ma nessun throttle → spam verso la casella (bersaglio fisso, meno grave del
  mail-bombing della newsletter perché non spara verso terzi). È il secondo trasporto del sito (mail() vs
  SMTP della newsletter): incoerenza operativa.

- **Gate admin su `$_SESSION['role']` grezzo invece di `isAdmin()`** (`newsletter.php:177`): `if
  (!isLoggedIn() || $_SESSION['role'] !== 'admin')`. Funziona, ma bypassa l'helper `isAdmin()` di SR-C2 —
  micro-incoerenza rispetto al resto degli endpoint gated.

- **URL hardcoded `runtimeradio.com` (senza `www`).** Conferma (`:26`), disiscrizione (`:324`) e link news
  (`:333,336`) sono hardcoded su `runtimeradio.com`, mentre il feed C8 hardcodava `www.runtimeradio.com`:
  **incoerenza di dominio** dentro lo stesso sito. Niente `SITE_URL` canonico (assente da SR-C1). Lato
  positivo: hardcoded ⇒ il link-poisoning via `HTTP_HOST` che SPW dovette difendere **non si applica** qui
  (ma a costo di rigidità su staging / dominio `.it`).

## 5. Estetica / UX (moderna ma funzionale)

- **`NewsletterForm` a 3 varianti** (`minimal`/`card`/`inline`) con stati `idle/loading/success/error` e
  micro-feedback. Le varianti `card`/`inline` montano **un solo checkbox** di consenso (Privacy Policy GDPR,
  `:124-133`) — non il **doppio** checkbox di SPW (trattamento + 16+). Montato in 4 punti reali: Article,
  Contact, Home, News. ⚠️ La variante `minimal` (footer) **non** ha checkbox di consenso: gap GDPR se usata
  per iscrivere (qui non risulta montata nei 4 punti, ma esiste).
- **"Newsletter Studio"** (`NewsletterComposer.tsx`): pannello admin a 2 tab (Invia / Gestione Iscritti). Tab
  invio con textarea intro + selezione card-articoli (max 20) + `confirm()` pre-invio col conteggio iscritti.
  Tab iscritti con **ciclo di vita a 3 stati** (`confirmed`/`pending`/`revoked`, badge colorati), filtri +
  ricerca client, e azioni contestuali per stato (Reinvia/Conferma per pending, Revoca per confirmed,
  Riattiva per revoked, Elimina sempre) — un parco-azioni **più ricco** del compositore di SPW.
- **Landing `/unsubscribe`** (`Unsubscribe.tsx`): brandizzata, valida il token a 64 char lato client prima di
  chiamare il backend, stati `loading/success/error/invalid` con CTA di ritorno e mailto di assistenza.
- **Email a tema scuro** coerente col brand (teal `#2dd4bf` su `#0f172a`), layout a tabelle per i client di
  posta, sia conferma che newsletter; card articolo con cover, titolo, summary e CTA "Leggi tutto →".
- **Footer GDPR nell'email di invio** (`:344-348`): nota sul trattamento dati (Reg. UE 2016/679) + link
  Privacy Policy + Disiscriviti — compliance-by-design nel template.

## 6. Differenze rispetto agli altri siti

Il confronto con **SPW-C9** è il cuore della card.

| Aspetto | SimonePizziWebSite (SPW-C9) | SitoRuntime (questa card) |
|---|---|---|
| **Geografia** | **due file** (`subscribers.php` + `newsletter_send.php`) | **un file ALL-IN-ONE** `newsletter.php` (gate pubblico/admin a metà file) |
| **Trasporto** | `mail()` nativa ovunque | **PHPMailer/SMTP** (STARTTLS, segreti `.env`) per la newsletter; `mail()` nativa per `contact.php` (due trasporti) |
| **Token** | `confirm_token` monouso (azzerato) + `unsubscribe_token` stabile separato | **un solo `confirmation_token`** fa conferma E disiscrizione, **mai azzerato** |
| **Rate-limit subscribe** | **SÌ** (ricicla `login_attempts`, 3/15min, anti-mail-bombing) | **NO** (IP solo memorizzato, mai limitato) → **vettore mail-bombing** |
| **Emette `content`?** | **NO** (ma body `intro` grezzo, ZERO sanitizzazione, salvo perché dietro Auth) | **NO** + **tutto `htmlspecialchars`** (l'emettitore PIÙ sicuro dei 4) |
| **Posizione nel "quadro dei 4 emettitori"** | 4°/ultimo e **MENO** sanitizzato | 4°/ultimo e **PIÙ** sanitizzato |
| **Filtro `status` nell'invio** | implicito (`getArticles({admin:false})`) | **esplicito** `status='published'` — l'UNICO emettitore SR che NON dimentica `status` (vs C7/C8) |
| **Throttle invio** | nessuno | `usleep` ogni 10 + `try/catch` per-destinatario |
| **Schema** | introdotto da `migrate_newsletter.php` (deploy-and-delete) | **3 verità divergenti** (init_mysql base / fix_ fossile SQLite / `apply_v293` self-healing in admin.php) |
| **Form GDPR** | **doppio** checkbox obbligatorio | **singolo** checkbox (Privacy Policy); variante minimal senza checkbox |
| **Azioni admin** | lista/approva/elimina/export CSV | + resend / revoke / **reactivate** + ciclo di vita a 3 stati (più ricco) |
| **Diagnostica** | assente | `test_smtp` (admin) che verifica la connessione SMTP |

Sintesi: dove SPW-C9 era *"due file, mail() nativa, doppio token, rate-limit presente, body poco sanitizzato
ma dietro Auth"*, SR-C9 è *"un file, SMTP autenticato, token unico riusato, rate-limit ASSENTE, content non
emesso e tutto escapato"*. SR fa **una scelta migliore** sulla sanitizzazione (l'emettitore più sicuro) e
**una peggiore** sul rate-limit (mail-bombing aperto). Il double opt-in c'è in entrambi, ma SR lo realizza
con un token a doppio scopo e uno schema stratificato in tre migrazioni.

Per **DISINTELLIGENZA/FDCA** (festival, SQLite) la ROADMAP prevede un `DIS-C9`: lì il riuso di
`login_attempts`/`.cache` e PHPMailer andrà verificato — termine di paragone "minimo" ancora da mappare.

## 7. Candidati per il libro

| Contenuto | Capitolo (esistente da aggiornare / nuovo) |
|---|---|
| **Endpoint ALL-IN-ONE** (un file, due audience, gate a metà) vs i due file di SPW | Cap. "Un endpoint, due facce" (contrasto SPW) |
| **PHPMailer/SMTP vs `mail()` nativa** (e i due trasporti coesistenti del sito) | Cap. "Spedire email dal thin stack: sendmail vs SMTP autenticato" (nuovo) |
| **I QUATTRO emettitori, chiusi**: la newsletter come emettitore più sicuro (sottrazione+escape) | Box "una sanitizzazione, quattro render-path" → **CHIUDE il filo C6→C7→C8→C9** |
| **Il form che spara email a nome tuo** (rate-limit assente = mail-bombing) | Box problemi/soluzioni "rate-limit dimenticato" (**alto valore**, contrasto con SPW che lo aveva) |
| **Un token, due scopi** (conferma+disiscrizione, mai azzerato, TTL promesso e assente) | Box "il token che vive troppo a lungo" |
| **Tre schemi per una tabella** (init_mysql / fix_ fossile SQLite / apply_v293 self-healing) | Cap. DB Evolution (ponte C13) "la tabella che nessuno crea due volte uguale" |
| **Invio sincrono nella request** (gemello del WebP di C5) | Cap. Scalabilità/problemi "lavoro pesante nella richiesta" |
| **Migrazione self-healing dentro admin.php** (vs script deploy-and-delete di SPW) | Box "migrazioni che si auto-riparano" |
| **`status='published'` ricordato qui, dimenticato in C7/C8** | (stesso box C4/C7) "due idee di 'pubblico'" — qui l'eccezione virtuosa |

## 8. Note / domande aperte

- **Ponte di sicurezza C6→C7→C8→C9: CHIUSO definitivamente.** La newsletter (l'ultimo possibile emettitore di
  `news.content`) **non emette `content`** e **escapa tutto** con `htmlspecialchars`: non è un vettore
  XSS-stored. Il quadro dei quattro render-path dello stesso dato è completo; serve comunque una
  sanitizzazione server-side condivisa (tesi C6/C7 rafforzata). Nessun emettitore SR riapre il buco; l'unico
  residuo è il **buco sugli attributi del prerender C7** (`strip_tags` allowlist), che resta la falla aperta
  del cluster contenuti.
- **Telegram: confermato fossile, nessun invio.** `TELEGRAM_BOT_TOKEN` esiste nei segreti (SR-C1,
  `db_credentials.php:21`) ma **nessun file di C9** (né di tutto il backend PHP) lo usa: grep negativo su
  `telegram|sendMessage|api.telegram`. L'unico "Telegram" è (a) link social nel frontend e (b)
  `Admin.tsx:553` *"Usa questo link nel tuo Bot Telegram per pubblicare automaticamente le news"* — cioè
  l'admin incolla **a mano** l'URL del feed C8 in un bot esterno. L'integrazione bot automatica **non esiste**
  (coerente con la diagnosi C8 del `feed_config.php` security-theater). Il token è un relitto di
  un'intenzione mai costruita.
- **`test_smtp`** (`admin.php:398-445`): diagnostica admin-gated che invia un'email di test a `SMTP_USER` e
  ritorna host/port/user + lunghezza password (non il valore) + debug SMTP verboso. Strumento operativo, non
  un endpoint di prodotto. → puntatore **C12** (pannelli admin/diagnostica).
- **Puntatori ad altri cluster** (annotati, NON mappati qui):
  - Singleton PDO / `db.php` / `db_credentials.php` (segreti SMTP) / PHPMailer vendored in `lib/` → **C1**
    (qui solo *usati*; SR-C1 li aveva marcati "→C9": **puntatore chiuso**).
  - `isLoggedIn()`/`role`/`validateCsrf()`/`.cache/ratelimit/` (non riusato) → meccanica **C2**.
  - Contratti client `api.ts` / fetch senza credentials / route `/unsubscribe` → **C3**.
  - Schema `news`/`status`/`published_at`/slug → **C4** (qui consumati).
  - `cover_image` come URL + conversione WebP → **C5**.
  - `apply_v293_newsletter`, lo schema base `init_mysql`, il fossile `fix_newsletter_table.php`, l'invio
    sincrono (potenziale incidente timeout) → **C13** (evoluzione DB & incidenti).
  - `test_smtp`, "Newsletter Studio", dashboard iscritti → **C12** (admin UI).
- **Credenziali/segreti:** i valori `SMTP_*` e `TELEGRAM_BOT_TOKEN` provengono da `.env` via
  `db_credentials.php` e **non sono stampati** in questa card (solo i nomi delle chiavi). `test_smtp` espone
  solo la *lunghezza* della password, non il valore.
- **Versione di riferimento:** sito **2.9.13**; la migrazione `apply_v293_newsletter` (= v2.9.3) data
  l'introduzione del double opt-in.
