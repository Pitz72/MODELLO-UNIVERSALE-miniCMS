# CAPITOLO 5: Backend Logic (PHP) (v2.0 - ADVANCED)

Il backend del miniCMS funge da motore di elaborazione dati e guardiano della sicurezza. Questa sezione definisce gli standard per la manipolazione delle stringhe, l'elaborazione dei file e la gestione delle risposte.

## 1. Gestione degli Identificatori (Slug Logic)
Gli URL devono essere parlanti (SEO-friendly) e univoci. Il Modello Universale impone una strategia di generazione e collisione lato server.

### 1.1 Algoritmo Base
```php
function createSlug($string) {
    // Minuscolo, trim e rimozione caratteri non alfanumerici (eccetto trattino)
    $slug = strtolower(trim(preg_replace('/[^A-Za-z0-9-]+/', '-', $string)));
    return $slug;
}
```

### 1.2 Algoritmo Avanzato (con Normalizzazione Accenti Italiani)
Il pattern base produce slug malformati con parole italiane che contengono accenti (es. `"caffÃ¨"` â†’ `"caff-"`). Il pattern avanzato, implementato in **SimonePizziWebSite**, risolve il problema con una mappa esplicita:

```php
function generateSlug($title, $pdo) {
    // Mappa esplicita accenti italiani e francesi comuni
    $accents      = ['Ã ','Ã¨','Ã©','Ã¬','Ã²','Ã¹','Ã€','Ãˆ','Ã‰','ÃŒ','Ã’','Ã™',
                     'Ã¢','Ãª','Ã®','Ã´','Ã»','Ã¤','Ã«','Ã¯','Ã¶','Ã¼'];
    $replacements = ['a','e','e','i','o','u','a','e','e','i','o','u',
                     'a','e','i','o','u','a','e','i','o','u'];

    $title = str_replace($accents, $replacements, $title);
    $slug  = strtolower(trim(preg_replace('/[^A-Za-z0-9-]+/', '-', $title)));

    // Anti-collisione
    $stmt = $pdo->prepare("SELECT COUNT(*) FROM articles WHERE slug = ?");
    $stmt->execute([$slug]);
    if ($stmt->fetchColumn() > 0) {
        $slug .= '-' . time();
    }
    return $slug;
}
```
Usare sempre il pattern avanzato per siti con contenuto italiano.

### 1.3 Strategia Anti-Collisione
In fase di creazione, il backend deve verificare l'esistenza dello slug. Se presente, viene aggiunto un suffisso temporale per garantire l'unicitÃ  senza errori di database.
```php
$stmt = $pdo->prepare("SELECT count(*) FROM news WHERE slug = ?");
$stmt->execute([$slug]);
if ($stmt->fetchColumn() > 0) {
    $slug .= '-' . time(); // Aggiunge timestamp per unicitÃ  assoluta
}
```

## 2. Gestione del Fuso Orario (Timezone Forcing)
Su hosting internazionali (es. server a Los Angeles), `date()` e `time()` usano il timezone del server. Questo causa problemi nella logica `published_at <= NOW()` per siti italiani.

**Soluzione standard** (implementata in SimonePizziWebSite e SitoRuntime):
```php
// All'inizio di ogni endpoint con logica temporale
date_default_timezone_set('Europe/Rome');
$ita_now_str  = date('Y-m-d H:i:s'); // Ora italiana per confronti SQL
$ita_now_time = time();               // Timestamp Unix italiano
```
Questa istruzione va inserita in ogni endpoint che filtra per `published_at` o che genera timestamp di creazione.

## 3. Gestione dei Metodi HTTP (RESTful Completo)
Il Modello Universale supporta tutti i metodi HTTP standard per API RESTful:

- **GET**: Lettura. Supporta `page`, `limit`, `slug`, `id`, `category`, `admin=true`.
- **POST**: Creazione di nuove risorse.
- **PUT**: Sostituzione completa di una risorsa esistente (tutti i campi).
- **PATCH**: Aggiornamento parziale (singolo campo: es. toggle `is_visible`, aggiornamento `sort_order`).
- **DELETE**: Eliminazione di una risorsa.

```php
$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') { /* ... */ }
elseif ($method === 'POST') { Auth::check(); /* ... */ }
elseif ($method === 'PUT') { Auth::check(); /* ... */ }
elseif ($method === 'PATCH') { Auth::check(); /* ... */ }
elseif ($method === 'DELETE') { Auth::check(); /* ... */ }
```

**Nota**: In progetti piÃ¹ vecchi (DISINTELLIGENZA, SitoRuntime prima del refactor), tutte le operazioni di modifica usavano POST con un campo `action` nel body. Il pattern RESTful con metodi separati Ã¨ piÃ¹ leggibile e permette al frontend TypeScript di essere piÃ¹ espressivo.

## 4. Il Pattern auth_helper.php (v2.0) (Autenticazione Inline)
SimonePizziWebSite introduce un pattern piÃ¹ snello per la gestione dell'autenticazione: un file `auth_helper.php` che incapsula `session_start()`, l'header `Content-Type` e la classe `Auth` in un unico include:

```php
<?php
// auth_helper.php
require_once 'db.php';
session_start();
header('Content-Type: application/json');

class Auth {
    public static function check() {
        if (!isset($_SESSION['user_id'])) {
            http_response_code(401);
            echo json_encode(['status' => 'error', 'message' => 'Non autorizzato']);
            exit;
        }
    }
}
```

**Utilizzo in ogni endpoint**:
```php
require_once 'auth_helper.php'; // Gestisce session_start() e Content-Type per tutti

// Nelle route protette:
Auth::check();
```

**Vantaggio**: `session_start()` e `header()` vengono chiamati una volta sola nel file helper â€” meno rischi di "headers already sent" dovuti a spazi o BOM nel file PHP.

## 5. Elaborazione Media e Ottimizzazione Immagini
Il caricamento di un file non Ã¨ un semplice spostamento (`move_uploaded_file`), ma un processo di trasformazione.

### 5.1 Polimorfismo dei Percorsi
Il sistema deve mappare il `type` di upload a percorsi fisici e pubblici differenti, applicando logiche di sicurezza specifiche per ogni categoria:
- **images/**: Accessibili pubblicamente, ridimensionamento automatico.
- **audio/podcasts/**: Solo caricamento via Admin.
- **audio/participants/**: Caricamento aperto (se abilitato), cartella isolata.

### 5.2 Auto-Resize & Trasparenza
Ogni immagine caricata dall'admin deve essere normalizzata (es. max 1920px) per preservare lo spazio su disco e la velocitÃ  di caricamento del frontend.
- **PNG/WebP**: Il backend deve preservare il canale Alpha (`imagealphablending`, `imagesavealpha`).
- **QualitÃ **: Standard fissato a 85% per JPEG/WebP per un bilanciamento ottimale peso/qualitÃ .

## 6. Sicurezza dell'Input e Output
- **Sanitizzazione Nomi**: Ogni file caricato deve essere rinominato usando `uniqid()` e pulito da caratteri speciali per evitare vulnerabilitÃ  di esecuzione script.
- **JSON Integrity**: Ogni risposta deve essere preceduta da `header('Content-Type: application/json')`. In caso di errore, deve essere inviato il codice HTTP corretto (`400`, `401`, `403`, `500`) unito a un messaggio JSON descrittivo.
- **FILTER_SANITIZE_STRING deprecato** (PHP 8.1+): Usare `strip_tags(trim($var))` in alternativa.

## 7. CORS Management
SitoRuntime include un file dedicato `cors.php` per la gestione degli header CORS, utile quando il frontend Ã¨ servito da un dominio diverso dall'API (es. sviluppo locale con Vite proxy):

```php
<?php
// cors.php â€” da includere prima di qualsiasi output nelle API pubbliche
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With");
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit(0); // Risponde al preflight e termina
}
```

**Nota**: In produzione con frontend e API sullo stesso dominio, questo file non Ã¨ necessario. Limitare `Access-Control-Allow-Origin: *` all'ambiente di sviluppo; in produzione specificare il dominio esatto.

## 8. Buffer Management
Per evitare che errori PHP (Notice/Warning) sporchino l'output JSON rendendolo invalido per il frontend, il Modello Universale suggerisce l'uso di `ob_start()` o la disattivazione dei log a schermo in produzione (`display_errors = 0`).

---
*Prossimo Capitolo: Frontend Bridge (API.ts) - La connessione tipizzata tra React e PHP, il pattern Double Read.*

