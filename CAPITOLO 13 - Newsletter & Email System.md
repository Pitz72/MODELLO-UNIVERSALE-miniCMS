# CAPITOLO 13: Newsletter & Email System (v1.0)

La newsletter è uno degli strumenti di fidelizzazione più diretti e indipendenti dalle piattaforme. A differenza dei social media, una lista email è un asset *posseduto* — non soggetta a algoritmi, shadowban o chiusure di account. Questo capitolo documenta il pattern completo implementato in SitoRuntime (Runtime Radio).

## 1. Schema del Database

La tabella `subscribers` è volutamente minimale. L'iscrizione richiede solo un'email valida — niente nome, niente dati aggiuntivi — in linea con il principio del minimo dato necessario per la conformità GDPR.

```sql
-- SQLite
CREATE TABLE IF NOT EXISTS subscribers (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    email     TEXT UNIQUE NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

-- MySQL (equivalente)
CREATE TABLE IF NOT EXISTS subscribers (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    email      VARCHAR(255) UNIQUE NOT NULL,
    is_active  TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

Il campo `is_active` permette la **disiscrizione morbida**: l'utente viene marcato come inattivo senza cancellare il record, preservando la storia dell'iscrizione e prevenendo re-iscrizioni accidentali.

## 2. Architettura degli Endpoint

Il file `newsletter.php` gestisce più azioni via query string `?action=`. La struttura ha un gate chiaro: le azioni pubbliche vengono servite immediatamente, quelle admin richiedono autenticazione.

```
GET/POST ?action=subscribe  → pubblico
GET      ?action=unsubscribe → pubblico (via link email)
GET      ?action=count       → admin only
POST     ?action=send        → admin only
```

```php
<?php
require_once 'cors.php';
require_once 'auth_utils.php';
session_start();

// Lazy DB Connection — caricata solo se necessario
function getDB() {
    static $pdo = null;
    if ($pdo === null) {
        require_once 'db.php';
        $pdo = Database::connect();
    }
    return $pdo;
}

$input = json_decode(file_get_contents('php://input'), true);
$action = $_GET['action'] ?? '';

// --- AZIONI PUBBLICHE (prima del gate admin) ---
// ...

// --- GATE ADMIN ---
if (!isLoggedIn() || $_SESSION['role'] !== 'admin') {
    http_response_code(403);
    echo json_encode(['success' => false, 'error' => 'Forbidden']);
    exit;
}

// --- AZIONI ADMIN ---
// ...
```

## 3. Iscrizione Pubblica

```php
if ($action === 'subscribe') {
    $email = filter_var($input['email'] ?? '', FILTER_VALIDATE_EMAIL);

    if (!$email) {
        echo json_encode(['success' => false, 'error' => 'Email non valida']);
        exit;
    }

    try {
        $stmt = getDB()->prepare("INSERT INTO subscribers (email) VALUES (?)");
        $stmt->execute([$email]);
        echo json_encode(['success' => true, 'message' => 'Iscrizione completata']);
    } catch (PDOException $e) {
        if ($e->getCode() == 23000) { // UNIQUE constraint violation
            echo json_encode(['success' => true, 'message' => 'Sei già iscritto!']);
        } else {
            echo json_encode(['success' => false, 'error' => 'Errore database']);
        }
    }
    exit;
}
```

**Note implementative:**
- `FILTER_VALIDATE_EMAIL` è la validazione lato server — obbligatoria anche se il form frontend valida già.
- Il codice di errore `23000` (UNIQUE constraint violation) viene gestito silenziosamente restituendo un successo: l'utente già iscritto non deve sapere che il suo indirizzo è già nel database (misura anti-enumeration minima).
- La risposta è sempre JSON — questo endpoint è chiamato da React via `fetch()`.

## 4. Disiscrizione GDPR-Compliant

La disiscrizione avviene via link personalizzato nell'email. A differenza della subscribe (che riceve JSON da React), questa action restituisce HTML diretto — perché viene visitata dal browser dell'utente che clicca il link nell'email.

```php
if ($action === 'unsubscribe') {
    $email = filter_var($_GET['email'] ?? '', FILTER_VALIDATE_EMAIL);

    if (!$email) {
        echo "Email non valida.";
        exit;
    }

    try {
        $stmt = getDB()->prepare("UPDATE subscribers SET is_active = 0 WHERE email = ?");
        $stmt->execute([$email]);
        echo "<h1>Disiscrizione completata</h1>
              <p>Ti abbiamo rimosso dalla newsletter. Ci dispiace vederti andare!</p>";
    } catch (PDOException $e) {
        echo "Errore durante la disiscrizione.";
    }
    exit;
}
```

La URL di disiscrizione nell'email ha questa forma:
```
https://runtimeradio.com/api/newsletter.php?action=unsubscribe&email=mario%40example.com
```

L'email è `urlencode()`-ata al momento della generazione dell'email (vedi Sezione 6).

## 5. Conteggio Iscritti (Admin)

```php
if ($action === 'count') {
    try {
        $stmt = getDB()->query("SELECT COUNT(*) FROM subscribers WHERE is_active = 1");
        echo json_encode(['success' => true, 'count' => $stmt->fetchColumn()]);
    } catch (PDOException $e) {
        echo json_encode(['success' => false, 'error' => 'Database error']);
    }
    exit;
}
```

Questo endpoint viene tipicamente chiamato al caricamento della dashboard admin per mostrare la dimensione della lista. Solo iscritti attivi (`is_active = 1`).

## 6. Invio Newsletter (Admin)

L'azione più complessa: genera l'HTML dell'email, personalizza il link di disiscrizione per ogni destinatario, e invia con rate limiting.

### 6.1 Generazione HTML con Placeholder

L'email viene costruita una volta sola come stringa HTML con un placeholder `{EMAIL_PLACEHOLDER}` nel link di disiscrizione. Il placeholder viene poi sostituito per ogni destinatario al momento dell'invio:

```php
// Costruzione HTML con placeholder
$html .= '<a href="https://runtimeradio.com/api/newsletter.php?action=unsubscribe&email={EMAIL_PLACEHOLDER}">
              DISISCRIVITI QUI
          </a>';

// Al momento dell'invio, per ogni destinatario:
foreach ($subscribers as $to) {
    $personalHtml = str_replace('{EMAIL_PLACEHOLDER}', urlencode($to), $html);
    mail($to, $subject, $personalHtml, $headers);
}
```

Questo pattern evita di rigenerare l'intero HTML per ogni email — solo la sostituzione del placeholder è per-destinatario.

### 6.2 Headers Email

```php
$headers  = "MIME-Version: 1.0\r\n";
$headers .= "Content-type:text/html;charset=UTF-8\r\n";
$headers .= "From: Runtime Radio <no-reply@runtimeradio.com>\r\n";
$headers .= "Reply-To: runtimeradio@gmail.com\r\n";
$headers .= "Return-Path: no-reply@runtimeradio.com\r\n";
$headers .= "X-Mailer: PHP/" . phpversion() . "\r\n";
```

- `From` diverso da `Reply-To`: le risposte vanno all'indirizzo reale, non al no-reply.
- `Return-Path`: gestisce i bounce (email non consegnate) — usato dai server di posta.

### 6.3 Rate Limiting

```php
$count = 0;
foreach ($subscribers as $to) {
    $personalHtml = str_replace('{EMAIL_PLACEHOLDER}', urlencode($to), $html);
    mail($to, $subject, $personalHtml, $headers);
    $count++;

    // Pausa ogni 10 email per non sovraccaricare il mail server
    if ($count % 10 === 0) {
        usleep(500000); // 0.5 secondi
    }
}

echo json_encode(['success' => true, 'message' => "Newsletter inviata a $count iscritti"]);
```

Il rate limiting con `usleep()` è fondamentale per hosting condivisi, che spesso impongono limiti di invio per-secondo. Senza questa pausa, il server SMTP rifiuta le email dopo un certo threshold, causando una consegna parziale invisibile.

### 6.4 Query degli Articoli (Ottimizzazione)

L'endpoint di invio riceve un array di ID articoli dal frontend. La query che li recupera è deliberatamente priva del campo `content`:

```php
$placeholders = str_repeat('?,', count($articleIds) - 1) . '?';
$stmt = getDB()->prepare(
    "SELECT id, title, slug, summary, cover_image, published_at
     FROM news WHERE id IN ($placeholders) ORDER BY published_at DESC"
);
$stmt->execute($articleIds);
```

Il campo `content` (HTML completo dell'articolo) non viene mai caricato nelle email: l'email include solo titolo, excerpt/summary e link "Leggi tutto". Questo riduce la dimensione del payload e mantiene le email snelle.

## 7. Struttura Email HTML (Pattern)

Le email HTML devono usare **CSS inline** — i client email (Outlook, Gmail app) non supportano fogli di stile esterni né `<style>` in `<head>`. Il pattern segue questa struttura:

```
[Header con logo/nome]
[Testo intro opzionale]
[Loop articoli: immagine + titolo + excerpt + link]
[Footer: informativa GDPR + link disiscrizione + copyright]
```

```php
$html  = '<!DOCTYPE html><html><body style="font-family: sans-serif; background: #0f172a;">';
$html .= '<div style="max-width: 600px; margin: 0 auto; background: #1e293b; padding: 20px;">';

// Header
$html .= '<h1 style="color: #2dd4bf; text-align: center;">Runtime Radio News</h1>';

// Intro (opzionale, inserito dall'admin)
if ($intro) {
    $html .= '<div style="background: #334155; padding: 15px; border-radius: 6px;">';
    $html .= nl2br(htmlspecialchars($intro)); // Preserva a-capo, escapa HTML
    $html .= '</div>';
}

// Loop articoli
foreach ($articles as $art) {
    $link = "https://runtimeradio.com/news/" . $art['slug'];
    $html .= '<h2><a href="' . $link . '" style="color: #fff;">'
           . htmlspecialchars($art['title']) . '</a></h2>';
    $html .= '<p>' . htmlspecialchars($art['summary']) . '</p>';
    $html .= '<a href="' . $link . '">Leggi tutto &rarr;</a>';
}

// Footer GDPR
$html .= '<p>I tuoi dati sono trattati in conformità al GDPR (UE 2016/679).
          <a href="https://runtimeradio.com/privacy-policy">Privacy Policy</a></p>';
$html .= '<a href="...?action=unsubscribe&email={EMAIL_PLACEHOLDER}">DISISCRIVITI</a>';
$html .= '</div></body></html>';
```

## 8. Considerazioni per la Scalabilità

Il pattern con `mail()` nativo di PHP funziona per liste fino a qualche migliaio di iscritti. Per volumi maggiori o per migliorare la deliverability (evitare lo spam folder), il passaggio a un servizio SMTP esterno richiede solo la sostituzione del blocco di invio:

- **Brevo** (ex Sendinblue) — API gratuita fino a 300 email/giorno
- **Mailgun** — API REST, ottima deliverability
- **Amazon SES** — costo bassissimo a volume alto

La struttura del codice rimane invariata: solo il metodo di consegna cambia.

---
*Capitolo correlato: Cap 10 (Security & Auth) per la gestione della sessione admin che protegge gli endpoint di invio.*

---
*Prossimo Capitolo: Database Evolution - La migrazione da SQLite a MySQL, documentata ora per ora dalla notte reale di febbraio 2026.*
