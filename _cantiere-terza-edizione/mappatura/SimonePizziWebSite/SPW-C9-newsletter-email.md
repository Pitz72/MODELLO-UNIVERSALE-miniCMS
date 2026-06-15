# Mappatura — SimonePizziWebSite — C9: Newsletter & Email

> **Stato:** COMPLETATO
> **Sessione:** 9 · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:**
> - `public/api/subscribers.php` (iscrizione, conferma, disiscrizione, lista/approva/elimina)
> - `public/api/newsletter_send.php` (invio + storico, template HTML)
> - `scripts/migrate_newsletter.php` (migrazione v1.7.4 schema)
> - `src/components/NewsletterSignup.tsx` (form pubblico double opt-in + GDPR)
> - `src/pages/admin/NewsletterAdmin.tsx` (pannello iscritti + compositore invio)
> - `src/pages/NewsletterConfirm.tsx` · `src/pages/NewsletterUnsubscribe.tsx` (landing token)
> - `src/api.ts:343-407` (8 metodi client) · `src/loaders.ts:160-167` (`adminNewsletterLoader`)
> - `src/App.tsx:36-37,256,271-272` (lazy + rotte) · `public/api/db.php:8-9` (`SITE_URL`)
> - Mount form: `src/pages/ContactPage.tsx:200`, `src/components/SingleArticle.tsx:277`, `src/components/CommunityHub.tsx:30`

---

## 1. Cosa fa (sintesi narrativa)

C9 è il sistema di newsletter **fatto in casa**, senza librerie esterne (niente PHPMailer/SMTP): trasporto via `mail()` nativa di PHP. Copre l'intero ciclo di vita dell'iscritto:

1. **Iscrizione pubblica con double opt-in.** Il visitatore compila il form (`NewsletterSignup`), il server crea un record `pending` con un `confirm_token` casuale e invia un'email con link di conferma. Solo dopo il click lo stato passa a `confirmed`. Nulla viene inviato prima della conferma.
2. **Gestione admin.** Pannello con statistiche (totali/confermati/pending/disiscritti), lista, aggiunta manuale (con `force_confirm` che salta l'opt-in), approvazione manuale dei `pending`, eliminazione, export CSV.
3. **Composizione e invio.** L'admin scrive un messaggio introduttivo e può allegare *card* di articoli selezionati; il corpo finale HTML viene assemblato **lato client** e spedito a tutti i `confirmed` in un loop `mail()` per-destinatario. Ogni email ha link di disiscrizione personale.
4. **Disiscrizione.** Link con `unsubscribe_token` in fondo a ogni email → landing `/newsletter/disiscritto` → stato `unsubscribed`.

Due endpoint-router (`subscribers.php`, `newsletter_send.php`) che smistano su `REQUEST_METHOD` — stesso pattern di C4. Schema introdotto dalla migrazione one-shot `migrate_newsletter.php` (deploy → esegui da browser → **cancella subito**, come gli script di C5).

## 2. Pattern miniCMS rilevanti

- **Endpoint-router su `REQUEST_METHOD`** (come C4): `subscribers.php` gestisce GET/POST/PATCH/DELETE in un solo file; i rami pubblici (confirm/unsubscribe/subscribe) sono distinti da quelli admin via `Auth::check()` o sotto-azione `?action=`.
- **Gating selettivo riusato da C2.** `Auth::check()` (CSRF Origin/Referer + session_version) protegge: lista iscritti, PATCH approva, DELETE, e **entrambi** i rami di `newsletter_send.php`. Restano pubblici per design solo i flussi token-based (confirm/unsubscribe) e la POST di iscrizione.
- **Rate limiting che ricicla la tabella `login_attempts` di C2** come throttle generico (non solo per il login): `subscribers.php:146-157`, max 3 iscrizioni / 15 min per IP, con IP **hashato** (`sha256`, prefisso `sub:`) per non riusare lo stesso namespace dei tentativi di login. Commento esplicito: senza, il form è un vettore di **mail-bombing** verso terzi (l'email di conferma parte verso indirizzi arbitrari) che brucia la reputazione del dominio.
- **Token come random_bytes(32) → 64 hex** (`bin2hex`), come i token di reset password di C2. `confirm_token` monouso (azzerato dopo l'uso), `unsubscribe_token` **stabile e riusabile** (mai azzerato) — parallelo al GUID stabile del feed C8.
- **Difesa "link poisoning" v1.19.0:** URL canonico sempre da `SITE_URL` (`db.php:8-9`), **mai** da `HTTP_HOST`, sia nelle email di conferma che nei link di disiscrizione (`newsletter_send.php:67-70`, `subscribers.php:286-288`).
- **Migrazione idempotente "deploy-and-delete"** (`migrate_newsletter.php`): `ALTER TABLE` per-colonna con `[SKIP]` su "Duplicate column", `CREATE TABLE IF NOT EXISTS`; istruzioni a inizio file impongono la cancellazione post-uso.
- **Double Read lato client (C3):** il loader e il compositore normalizzano sempre `Array.isArray(res) ? res : res.data` sugli articoli (`loaders.ts:166`, `NewsletterAdmin.tsx:113`).

## 3. Codice chiave (stralci con origine)

**Double opt-in: creazione token e invio conferma** — `subscribers.php:185-209`
```php
$confirmToken     = $forceConfirm ? null : bin2hex(random_bytes(32));
$unsubscribeToken = bin2hex(random_bytes(32));
$status           = $forceConfirm ? 'confirmed' : 'pending';
// ... INSERT ...
if (!$forceConfirm) {
    sendConfirmEmail($email, $name ?: 'Amico', $confirmToken);
    echo json_encode(['status'=>'success','message'=>'Quasi fatto! Controlla la tua email...']);
}
```

**Rate-limit per-IP riusando `login_attempts`** — `subscribers.php:146-157`
```php
if (!$isAdmin) {
    $rl_key = 'sub:' . substr(hash('sha256', $_SERVER['REMOTE_ADDR'] ?? 'unknown'), 0, 40);
    $pdo->exec("DELETE FROM login_attempts WHERE attempt_time < DATE_SUB(NOW(), INTERVAL 15 MINUTE)");
    $stmtRl = $pdo->prepare("SELECT COUNT(*) FROM login_attempts WHERE ip_address = ?");
    $stmtRl->execute([$rl_key]);
    if ((int)$stmtRl->fetchColumn() >= 3) { http_response_code(429); /* ... */ exit; }
    $pdo->prepare("INSERT INTO login_attempts (ip_address) VALUES (?)")->execute([$rl_key]);
}
```

**Invio: loop `mail()` sincrono per-destinatario** — `newsletter_send.php:73-92`
```php
$sent = 0;
foreach ($recipients as $r) {
    $html = buildNewsletterHtml($subject, $body, $r['name'] ?: 'Amico',
                                $r['unsubscribe_token'], $protocol, $host);
    // ... headers From/Reply-To/MIME ...
    if (mail($r['email'], $encodedSubject, $html, $headers)) { $sent++; }
}
$pdo->prepare("INSERT INTO newsletter_sends (subject, body, recipient_count)
               VALUES (:subject,:body,:count)")->execute([...]);
```

**⚠️ CHIOSA C6/C7/C8 — il body è emesso GREZZO se contiene HTML** — `newsletter_send.php:122-124`
```php
$isHtml   = preg_match('/<[a-zA-Z][\s\S]*>/', $body);
$bodyHtml = $isHtml ? $body : nl2br(htmlspecialchars($body));
// ↑ se $body contiene un tag, NESSUNA sanitizzazione: né htmlspecialchars, né strip_tags, né DOMPurify
```

**Composizione card articolo lato client, anch'essa non escapata** — `NewsletterAdmin.tsx:47-62`
```tsx
function buildArticleHtml(article: Article, siteBase: string): string {
  // article.title / article.excerpt / article.cover_image interpolati RAW nei template literal
  return `... <h3 ...>${article.title}</h3>
          ${article.excerpt ? `<p ...>${article.excerpt}</p>` : ''} ...`;
}
```

**Email di conferma: il nome (input pubblico) È escapato** — `subscribers.php:302,308`
```php
<h1 ...>Ciao, ' . htmlspecialchars($name) . '!</h1>
<a href="' . htmlspecialchars($confirmLink) . '" ...>Conferma Iscrizione</a>
```

## 4. Problemi riscontrati & soluzioni

- **🔒 CHIUSURA DEFINITIVA DEL PONTE C6/C7/C8 — la newsletter è il 4° e ULTIMO emettitore del contenuto.**
  Risultato: **la newsletter NON emette mai `articles.content`** (il campo HTML grezzo difeso solo a render-time da DOMPurify in C6). Quando l'admin allega articoli, vengono inseriti solo `title`, `excerpt`, `cover_image`, `category`, `slug` — *mai* `content`. La regola di visibilità C4 è rispettata indirettamente: il compositore carica `getArticles({admin:false})` (`NewsletterAdmin.tsx:112`), quindi solo `published`.
  Tuttavia l'email è, in assoluto, **l'emettitore meno sanitizzato dei quattro**:
  - C6 render web: DOMPurify (allowlist robusta).
  - C7 prerender: `strip_tags` allowlist (più debole → buco attributi).
  - C8 RSS: `excerpt` + `htmlspecialchars` (il più sicuro, "sicurezza per sottrazione").
  - **C9 email: ZERO sanitizzazione** — `buildNewsletterHtml` emette `$body` grezzo (`:123`) e `buildArticleHtml` interpola `excerpt`/`title` senza escaping (`NewsletterAdmin.tsx:47`).
  **Perché il ponte si chiude comunque (rischio basso):** entrambi i punti di iniezione stanno **dietro il confine di fiducia admin**. `newsletter_send.php` POST è `Auth::check()`-gated, e l'`excerpt` proviene da articoli che solo l'admin può creare (C4/C6). Non esiste un vettore di **stored-XSS da input pubblico** che raggiunga l'email. Il residuo è "self-XSS nel proprio client di posta" o admin compromesso — non l'attacco esterno che minacciava prerender/RSS. Per contro, l'unico input *pubblico* del cluster (il `name` nell'email di conferma) **è** escapato con `htmlspecialchars` (`subscribers.php:302`). **Ponte sicurezza C6→C9: CHIUSO.**

- **Invio sincrono senza coda/throttle** (`newsletter_send.php:74-87`): un solo `foreach` con `mail()` bloccante per ogni iscritto, dentro una request HTTP. Su liste grandi → rischio `max_execution_time`/timeout e nessun ritmo anti-greylisting. Stesso anti-pattern "lavoro pesante sincrono nella request" già visto in C5 (conversione WebP). Nessun retry, nessuna gestione bounce: si conta solo il booleano di ritorno di `mail()`.

- **Disiscrizione via GET senza conferma** (`subscribers.php:64-85`): il link `?action=unsubscribe&token=` agisce su una semplice GET. I client di posta che fanno **prefetch dei link** possono disiscrivere l'utente per sbaglio. Manca uno step di conferma (es. POST esplicita dalla landing).

- **`confirm_token` senza scadenza**, nonostante l'email dichiari "Il link scade se non viene utilizzato" (`subscribers.php:316`): il token non ha TTL, resta valido finché non viene usato o sovrascritto da una nuova richiesta. Claim dell'email tecnicamente falso.

- **`force_confirm` valutato sul raw session check, non su `Auth::check()`** (`subscribers.php:131`): `$isAdmin = isset($_SESSION['user_id'])`. Il ramo admin della POST si fida della sola sessione, bypassando il gate CSRF Origin/Referer di `auth_helper`. Impatto basso (aggiunge solo un iscritto `confirmed`), ma è un'incoerenza rispetto al resto del cluster che usa `Auth::check()`.

- **Copie stantie in `dist/`** (`dist/api/subscribers.php`, `dist/api/newsletter_send.php`): artefatti di build, non fonte di verità. Da ignorare (come l'archeologia `dist/` di C7).

## 5. Estetica / UX (moderna ma funzionale)

- **Form GDPR-by-design** (`NewsletterSignup.tsx`): doppio checkbox obbligatorio (consenso trattamento + dichiarazione 16+), informativa privacy inline (titolare/finalità/base giuridica/diritti artt. 15-21), `canSubmit` gate; stati `idle/loading/success/already/error` con micro-feedback. Montato in **3 punti** reali: ContactPage, in coda a ogni SingleArticle, e nel CommunityHub (non falsi positivi).
- **Compositore admin** (`NewsletterAdmin.tsx`): due tab (Iscritti / Invia), card statistiche colorate per stato, selettore articoli collassabile con badge contatore, anteprima del numero di destinatari sul bottone d'invio, `confirm()` di sicurezza pre-invio, storico invii con conteggio destinatari. Export CSV generato client-side (Blob).
- **Email a tema scuro** coerente col brand (verde `#22c55e` su `#0a0a0a`), layout a tabelle per compatibilità con i client di posta, sia per la conferma sia per la newsletter; card articolo con cover, categoria, excerpt e CTA "Leggi l'articolo →".
- **Landing token brandizzate** (`NewsletterConfirm`/`NewsletterUnsubscribe`): icone di stato, messaggi rassicuranti, CTA di ritorno alla home.

## 6. Differenze rispetto agli altri siti

Da compilare quando saranno mappati **SR-C9** e **DIS-C9**. Ipotesi da verificare: SitoRuntime potrebbe avere volumi maggiori → la coda/throttle assente qui potrebbe essere il punto di divergenza più interessante; DISINTELLIGENZA (SQLite) non potrebbe riusare `login_attempts` allo stesso modo. *(pointer, non in-scope ora)*

## 7. Candidati per il libro

| Contenuto | Capitolo |
|---|---|
| Double opt-in fatto a mano (token, stati pending/confirmed/unsubscribed, ciclo di vita) | **Nuovo**: "Newsletter senza dipendenze" |
| Riuso della tabella `login_attempts` come throttle generico (rate-limit anti-mail-bombing) | Aggiorna cap. Security/C2 (pattern trasversale) |
| **Il filo dei "4 emettitori" del contenuto** (render/prerender/RSS/email) e la sua chiusura | Aggiorna box sicurezza C6/C7/C8 → **sezione di sintesi cross-cluster** |
| Difesa link-poisoning: `SITE_URL` canonico vs `HTTP_HOST` | Aggiorna cap. Security |
| Loop `mail()` sincrono come anti-pattern di scalabilità (gemello del WebP sincrono di C5) | Cap. Scalabilità/problemi-soluzioni |
| Form GDPR-by-design + migrazione "deploy-and-delete" | Cap. UX / Operatività |

## 8. Note / domande aperte

- **Trasporto:** `mail()` nativa PHP, nessun SMTP/PHPMailer/servizio esterno. Mittente `newsletter@<host-da-SITE_URL>`, `Reply-To` di conferma = stesso mittente, `Reply-To` di invio = indirizzo Proton hardcoded (`newsletter_send.php:71`). Nessuna credenziale/segreto presente nel codice (niente da redarre).
- **Schema `subscribers`** (da `migrate_newsletter.php` + uso runtime): `id, email, name, status('pending'|'confirmed'|'unsubscribed'), confirm_token, confirmed_at, unsubscribe_token, created_at`. `newsletter_sends`: `id, subject, body(HTML grezzo), sent_at, recipient_count`.
- **Da verificare in sintesi:** introdurre una coda/cron per l'invio (oggi sincrono) — possibile candidato C13 (DB Evolution/incidenti) se in SR è già emerso un incidente di timeout invio.
- **Pointer fuori-scope incontrati:** `messages.php` (contatti) e `analytics.php`/`stats.php` toccano stringhe "mail"/"contact" ma appartengono a **C11 (Engagement)** e **C12 (Admin)** — solo annotati qui, non mappati.
- **Falsi positivi confermati:** le occorrenze "mail/contact" in `node_modules/lucide-react` (icone) e `.git/hooks` sono rumore; gli unici file C9 reali sono i 7 sorgente elencati in testa.
