# Mappatura — SimonePizziWebSite — C11: Engagement & Social (reactions/messages)

> **Stato:** COMPLETATO
> **Sessione:** 10 · **Data:** 2026-06-15 · **Commit:** _(in corso)_
> **File sorgente ispezionati:** (percorso relativo al sito SimonePizziWebSite)
> - `public/api/reactions.php` (API reazioni, v1.0.0 nel banner / v1.13.0 nel changelog)
> - `public/api/messages.php` (API messaggi di contatto, v1.7.8)
> - `scripts/server-tools/migrate_reactions.php` (creazione tabella `article_reactions`)
> - `src/components/ReactionBar.tsx` (UI reazioni client)
> - `src/components/SingleArticle.tsx:11,48,160-163` (mount ReactionBar)
> - `src/loaders.ts:84-90` (loader articolo: pre-fetch reazioni)
> - `src/pages/ContactPage.tsx:36-61` (form contatti pubblico)
> - `src/pages/admin/MessagesList.tsx` (pannello admin messaggi)
> - `src/api.ts:409-435` (client messaggi admin) · `src/api.ts:511-529` (client reazioni)
> - *(pointer C12)* `public/api/analytics.php:131-259` legge `article_reactions` per le statistiche

---

## 1. Cosa fa (sintesi narrativa)

Il cluster C11 copre i due punti in cui il **visitatore anonimo** può interagire col sito senza autenticarsi: le **reazioni** agli articoli (5 emoji-like con toggle) e i **messaggi** dal form contatti. Sono le uniche due superfici di **scrittura pubblica** del CMS — tutto il resto di C4/C5/C6/C9 è gated dietro `Auth::check`. Per questo C11 è il fronte più esposto del sito e concentra logica anti-spam/anti-abuso.

- **Reactions** (`reactions.php`): per articolo, un visitatore può attivare/disattivare 5 reazioni (`thumb/heart/fire/think/game`). L'identità è uno **pseudonimo anonimo** `voter_hash = SHA256(IP + User-Agent)` — nessun dato personale persistito (claim GDPR-compliant nel banner). Il GET pubblico restituisce i conteggi + le reazioni già date da quel visitatore; il POST fa il toggle e ritorna i conteggi aggiornati. **Nessun ramo admin** dentro reactions.php (niente reset conteggi qui — semmai vive in C12/analytics).
- **Messages** (`messages.php`): endpoint-router classico miniCMS su `REQUEST_METHOD`. `POST` è **pubblico** (chiunque invia un messaggio → salvataggio DB + email di notifica al proprietario); `GET`/`PUT`/`DELETE` sono **admin** (lista, marca-letto, elimina) gated da `Auth::check()`. La tabella `messages` viene **auto-creata** in modo idempotente alla prima chiamata (`ensureMessagesTable`).

---

## 2. Pattern miniCMS rilevanti

- **Endpoint-router su `REQUEST_METHOD` con gate selettivo** (identico a C4/C9): in `messages.php` i rami mutativi/lettura-privata (`GET` lista, `PUT`, `DELETE`) aprono con `Auth::check()`, il ramo `POST` pubblico no. Pattern speculare a `subscribers.php` di C9.
- **Auto-scaffolding della tabella** (`CREATE TABLE IF NOT EXISTS` + `ALTER` difensivo in `try/catch`): `messages.php:19-39` crea `messages` e migra la colonna `ip_hash` sulle installazioni vecchie senza migration esterna. Stessa filosofia "il codice porta con sé il proprio schema" già vista altrove.
- **Riuso di `login_attempts` come rate-limiter universale** (il filo C2 → C9): `reactions.php:107-119` ricicla la tabella `login_attempts` per il limite per-IP, esattamente come `subscribers.php` (C9). `messages.php` invece **NON** la riusa: conta sulla propria tabella `messages` via `ip_hash` (variante del pattern).
- **Pseudonimo anonimo derivato** (`SHA256(IP+UA)`): identità del votante senza account né cookie, GDPR-by-design. Parallelo all'`ip_hash` dei messaggi e all'IP hashato della newsletter (C9).
- **Difesa input pubblico al WRITE-TIME** (`strip_tags`/`filter_var`): `messages.php:87-90`. È l'**opposto** della strategia articoli (C6/C7: contenuto salvato grezzo, sanitizzato al render). Vedi §4 e §8.
- **Client unico `api.ts` + Double-Read graceful**: `getReactions` (api.ts:512) **degrada silenziosamente** a conteggi a zero su qualsiasi errore (try/catch → oggetto di default), così la pagina articolo non si rompe mai per colpa delle reazioni.

---

## 3. Codice chiave (stralci con origine)

### 3.1 Reazioni — pseudonimo anonimo + toggle idempotente

```php
// reactions.php:25-29 — identità anonima, nessun dato personale persistito
$voter_hash = hash('sha256',
    ($_SERVER['REMOTE_ADDR'] ?? 'unknown') .
    ($_SERVER['HTTP_USER_AGENT'] ?? 'unknown')
);
```

```php
// reactions.php:129-145 — toggle: se esiste rimuovi, altrimenti inserisci (INSERT IGNORE)
if ($existing) {
    $stmtDel = $pdo->prepare("DELETE FROM article_reactions
        WHERE article_id = ? AND voter_hash = ? AND reaction = ?");
    $stmtDel->execute([$article_id, $voter_hash, $reaction]);
    $action = 'removed';
} else {
    $stmtIns = $pdo->prepare("INSERT IGNORE INTO article_reactions (article_id, reaction, voter_hash)
        VALUES (?, ?, ?)");
    $stmtIns->execute([$article_id, $reaction, $voter_hash]);
    $action = 'added';
}
```

L'anti-doppio-voto è garantito a **livello DB** dalla chiave unica, non solo dal codice:

```php
// migrate_reactions.php:19-27 — UNIQUE KEY = vera barriera anti-duplicato
CREATE TABLE IF NOT EXISTS article_reactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    article_id INT NOT NULL,
    reaction VARCHAR(20) NOT NULL,
    voter_hash VARCHAR(64) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_vote (article_id, voter_hash, reaction),
    INDEX idx_article (article_id)
) ENGINE=InnoDB ...
```

### 3.2 Reazioni — rate limit a DUE strati (la gemma della card)

```php
// reactions.php:92-119
// Strato 1: per voter_hash (IP+UA) — max 20 azioni/min sulla tabella reactions
$stmtRate = $pdo->prepare("SELECT COUNT(*) FROM article_reactions
    WHERE voter_hash = ? AND created_at >= DATE_SUB(NOW(), INTERVAL 1 MINUTE)");
// ... >= 20 → 429

// [v1.19.0] Strato 2: per SOLO IP — perché voter_hash include lo User-Agent,
// controllato dal client: ruotando l'UA si aggirerebbe lo strato 1.
$rl_key = 'rea:' . substr(hash('sha256', $ip), 0, 40);
$pdo->exec("DELETE FROM login_attempts WHERE attempt_time < DATE_SUB(NOW(), INTERVAL 15 MINUTE)");
$stmtIpRate = $pdo->prepare("SELECT COUNT(*) FROM login_attempts
    WHERE ip_address = ? AND attempt_time >= DATE_SUB(NOW(), INTERVAL 1 MINUTE)");
// ... >= 30 → 429
$pdo->prepare("INSERT INTO login_attempts (ip_address) VALUES (?)")->execute([$rl_key]);
```

Questo è il pattern d'oro: lo sviluppatore ha capito che `voter_hash` da solo è bypassabile (lo UA è input del client) e ha aggiunto un secondo argine ancorato al **solo IP**, riusando la tabella `login_attempts` con un prefisso di namespace (`rea:`) — esattamente la tecnica di `subscribers.php` in C9.

### 3.3 Messaggi — sanitizzazione al WRITE-TIME + validazione

```php
// messages.php:86-107 — input pubblico ripulito PRIMA del salvataggio
$name    = trim(strip_tags($data['name']    ?? ''));
$email   = trim(filter_var($data['email']   ?? '', FILTER_SANITIZE_EMAIL));
$subject = trim(strip_tags($data['subject'] ?? ''));
$message = trim(strip_tags($data['message'] ?? ''));
// + min length name>=2, FILTER_VALIDATE_EMAIL, message>=10; subject default 'Nessun oggetto'
```

### 3.4 Messaggi — rate limit anti-spam (variante: conta sulla PROPRIA tabella)

```php
// messages.php:114-124 — max 3 messaggi per IP-hash in 15 minuti, contati su `messages`
$ip_hash = hash('sha256', $_SERVER['REMOTE_ADDR'] ?? 'unknown');
$stmt_limit = $pdo->prepare("SELECT COUNT(*) FROM messages
    WHERE ip_hash = ? AND created_at > DATE_SUB(NOW(), INTERVAL 15 MINUTE)");
// ... >= 3 → 429
```

### 3.5 Messaggi — notifica email (intreccio con C9: `mail()` nativa + escaping completo)

```php
// messages.php:201-258 — sendNotificationEmail()
$to = 'simonepizzi.1972@proton.me';                  // destinatario HARDCODED
$safeMsg = nl2br(htmlspecialchars($messageBody, ENT_QUOTES, 'UTF-8'));
// ...interpolazioni nel template HTML tutte via htmlspecialchars($senderName/$senderEmail/$subject)...
$headers .= "From: Simone Pizzi <{$from}>\r\n";       // $from = 'noreply@' . HTTP_HOST
$headers .= "Reply-To: {$senderEmail}\r\n";           // risposta diretta al mittente
mail($to, $subjectEncoded, $html, $headers);          // come C9: mail() nativa, no SMTP/PHPMailer
```

### 3.6 Admin render — doppia difesa (escaping React) + nessun `dangerouslySetInnerHTML`

```tsx
// MessagesList.tsx:186-188 — il corpo del messaggio è un text-node JSX → React auto-escapa
<p className="... whitespace-pre-wrap">
    {detail.message}
</p>
// anteprima riga: MessagesList.tsx:167 → {m.preview}  (anch'esso text-node)
```

---

## 4. Problemi riscontrati & soluzioni

- **[GOLD — chiusura del filo "input pubblico"]** Il testo pubblico dei messaggi è sanitizzato **al write-time** con `strip_tags` (`messages.php:87-90`). Questo neutralizza lo **stored-XSS all'origine**: ciò che entra nel DB è già privo di tag. È la strategia **opposta** a quella degli articoli (C6/C7: `articles.content` salvato grezzo, sanitizzato solo al render con DOMPurify / strip_tags-allowlist). Convivono quindi **due filosofie antitetiche** nello stesso codebase. Per i messaggi la scelta è corretta e robusta: anche il pannello admin (`MessagesList.tsx`) renderizza il testo come **text-node JSX** (React auto-escapa) e **non** usa `dangerouslySetInnerHTML` → **doppia difesa**, nessun XSS-stored riproducibile nel pannello admin.
- **Anti-doppio-voto a livello DB, non solo applicativo:** la `UNIQUE KEY unique_vote (article_id, voter_hash, reaction)` + `INSERT IGNORE` rendono il toggle robusto anche in caso di race condition/doppio click — il DB rifiuta il duplicato a prescindere dal codice.
- **Bypass del rate-limit via rotazione User-Agent → risolto in v1.19.0:** il primo limite è su `voter_hash` (IP+UA), ma lo UA è controllato dal client. Aggiunto il secondo argine sul **solo IP** (riuso `login_attempts`). Caso di studio perfetto su "perché un solo strato di rate-limit non basta quando la chiave include input del client".
- **Incoerenza nella sorgente dell'IP rispetto a C2:** sia `reactions.php` sia `messages.php` usano il **raw** `$_SERVER['REMOTE_ADDR']`, **non** l'helper anti-spoof `getClientIp()` introdotto in C2/C9. Dietro proxy/CDN questo può collassare tutti i visitatori su un unico IP (rate-limit troppo aggressivo) oppure, al contrario, non riconoscere l'IP reale. Divergenza da segnalare per uniformare.
- **Banner di `reactions.php` leggermente stale:** il commento d'intestazione (`reactions.php:11`) dice "max 20 azioni per IP al minuto", ma il limite a 20 è in realtà per `voter_hash` (IP+UA); il vero limite per-solo-IP (30/min) è il secondo strato aggiunto dopo. Documentazione da allineare al codice.
- **POST messaggi senza CSRF e senza `getClientIp`:** è un form **pubblico**, quindi l'assenza di token CSRF è di per sé accettabile (non c'è azione privilegiata da forgiare), ma significa che qualunque origin può postare; l'unico argine è 3 msg/15 min per IP. Possibile `From:`-header basato su `HTTP_HOST` (attacker-controllable) → solo cosmetico (non c'è iniezione di header perché va in un campo `From` costruito, non in input grezzo dell'utente), ma da tenere d'occhio.
- **`mail()` nativa "fire-and-forget":** come in C9, il valore di ritorno di `mail()` è ignorato (`messages.php:258`): se l'invio fallisce, il visitatore vede comunque "Messaggio inviato!" perché il messaggio è già salvato nel DB. Il DB è la fonte di verità, l'email è best-effort — scelta difendibile, ma da raccontare.
- **`getReactions` degrada a zero, mai errore:** `api.ts:512-519` ingoia ogni errore restituendo conteggi a zero → la pagina articolo non si rompe mai per le reazioni (graceful degradation, coerente col filo C3).

---

## 5. Estetica / UX (moderna ma funzionale)

- **ReactionBar** (`ReactionBar.tsx`): 5 icone SVG inline (thumb/heart/fire/think/game) con label IT ("Utile/Bello/Interessante/Fa pensare/Game-related"), tooltip animati (framer-motion), `whileTap` scale, micro-rotazione all'attivazione, contatore con transizione `AnimatePresence`. **Optimistic UI**: aggiorna conteggio e stato locale *prima* della risposta server, con **rollback** su errore (`ReactionBar.tsx:64-82`). Accessibilità curata: `min-w/h 44px` (target touch), `aria-pressed`, `aria-label` con conteggio.
- **Palette engagement**: verde brand `#22c55e`/`dis-green` come accento attivo, su fondo scuro — coerente con l'identità del sito.
- **ContactPage**: form con **doppio consenso GDPR** (trattamento dati + età 16+) che gate il submit lato client (`canSubmit`), stato feedback `idle/loading/success/error`, schermata di conferma "Ricevuto!" con reset. NB: il consenso GDPR è verificato **solo lato client** — il backend non lo richiede.
- **MessagesList** (admin): inbox stile email-client con badge "non letti", riga collassabile, dettaglio espanso, **marca-letto automatico** all'apertura (`PUT`), pulsanti "Rispondi" (mailto precompilato `Re:`) ed "Elimina" (con `confirm()`). Empty state e loading curati.

---

## 6. Differenze rispetto agli altri siti

- *(Da completare nella fase di sintesi cross-sito.)* SimonePizziWebSite è il **flagship contenuti**: le reazioni-articolo sono qui un meccanismo editoriale leggero (5 like tipizzati, anonimi). Da confrontare con DISINTELLIGENZA/FDCA (C10) dove invece il "voto" è il cuore festival con anti-frode forte — **engagement leggero (C11) vs voto-competitivo (C10)** sono due mondi diversi: qui il toggle è libero e plurimo (puoi dare più reazioni diverse allo stesso articolo), là il voto è singolo e sorvegliato.
- Da verificare in SitoRuntime (SR-C*) se esiste un equivalente di reazioni/messaggi o se l'engagement è gestito diversamente.

---

## 7. Candidati per il libro

| Cosa | Capitolo (esistente da aggiornare / nuovo) |
|------|--------------------------------------------|
| **Rate-limit a due strati** (voter_hash bypassabile via UA → secondo argine su solo-IP) | Cap. Sicurezza / "anti-abuso degli endpoint pubblici" — box GOLD |
| **`login_attempts` come rate-limiter universale namespaced** (`rea:`, riuso da C2/C9) | Stesso capitolo — pattern trasversale, sezione "una tabella, tre usi" |
| **Anti-doppio-voto a livello DB** (UNIQUE KEY + INSERT IGNORE vs solo logica app) | Cap. "Il database come guardiano dell'integrità" |
| **Due filosofie di sanitizzazione**: write-time (messaggi, strip_tags) vs render-time (articoli, DOMPurify) | Cap. XSS / "dove ripulire l'input" — confronto diretto, chiude il filo C6/C7 |
| **Pseudonimo anonimo `SHA256(IP+UA)`** GDPR-by-design | Cap. Privacy/GDPR — identità senza account né cookie |
| **Optimistic UI con rollback** (ReactionBar) | Cap. UX/Frontend — micro-interazioni resilienti |
| **Auto-scaffolding tabella** (`ensureMessagesTable` + ALTER difensivo) | Cap. "Schema che viaggia col codice" |
| **`mail()` fire-and-forget, DB come fonte di verità** | Cap. Email (intreccio con C9) |

---

## 8. Note / domande aperte

- **Follow-up sicurezza (risposta alla domanda del prompt):** il testo pubblico dei messaggi **viene sanitizzato lato SERVER al write-time** (`strip_tags` su name/subject/message, `messages.php:87-90`). Quindi **NON** è un XSS-stored: ciò che arriva al pannello admin è già privo di tag, e in più il render admin è un text-node React auto-escapato. Filo **CHIUSO** a rischio basso. È il complemento del filo "emettitori" di C9 ma con polarità inversa: lì la fonte era admin (gated), qui è input pubblico — ed è proprio l'input pubblico a essere ripulito più aggressivamente (write-time), mentre il contenuto admin-trusted (articoli) resta grezzo fino al render.
- **Pointer C2 (auth/anti-spoof):** uniformare `reactions.php`/`messages.php` all'helper `getClientIp()` di C2 invece del raw `REMOTE_ADDR`. → annotato qui, non approfondito (è C2).
- **Pointer C12 (admin/analytics):** `analytics.php:131-259` aggrega `article_reactions` (totale, per tipo, top-articoli-per-reazioni). Il "reset/azzeramento conteggi" reazioni, se esiste, vive lì o in `optimize_db.php`/`backup.php` — **non** in `reactions.php`. → da mappare in SPW-C12.
- **Pointer C12 (admin UX):** `Dashboard.tsx` e `AdminLayout.tsx` referenziano "messages"/conteggi non letti per la navigazione admin → SPW-C12.
- **Falso positivo verificato:** `CommunityHub.tsx` compariva nella grep iniziale ma **non** usa reazioni/messaggi/contatti (nessun match sui termini specifici) — coerente col metodo di smentita falsi positivi di C8/C9.
- **Versionamento ambiguo di reactions:** banner file dice `v1.0.0`, il changelog di repo (`docs/changelogs/v1.13.0.md`) e il commento `api.ts:511` attribuiscono la feature a `v1.13.0`; il secondo rate-limit è `v1.19.0`. Da riconciliare in fase di scrittura se si cita la timeline.
- **Consenso GDPR solo client-side:** il backend `messages.php` non verifica i due checkbox — chi posta direttamente all'endpoint salta il gate. Coerente con l'architettura (il consenso è UX, non barriera tecnica), ma da menzionare nel capitolo privacy.
