# CAPITOLO 5: Backend Logic (PHP)

Il backend del miniCMS è il motore che elabora i dati e fa da guardiano. Questo capitolo definisce come è fatto un endpoint, come si avvia, come gestisce gli identificatori, il fuso orario e gli errori. Il filo conduttore è sempre lo stesso: niente framework, un file PHP per responsabilità, e tre modi di declinare lo stesso scheletro a seconda di quanto il sito ha scelto di ingegnerizzare.

## 1. Gestione degli Identificatori (Slug)

Gli URL devono essere parlanti e univoci. Il Modello genera lo slug lato server e ne garantisce l'unicità contro le collisioni.

### 1.1 Algoritmo base
```php
function createSlug($string) {
    // minuscolo, trim e rimozione dei caratteri non alfanumerici (eccetto il trattino)
    return strtolower(trim(preg_replace('/[^A-Za-z0-9-]+/', '-', $string)));
}
```

### 1.2 Algoritmo avanzato (normalizzazione degli accenti italiani)

Il pattern base produce slug malformati con le parole accentate (`caffè` diventa `caff-`). La variante di **SimonePizziWebSite** risolve il problema con una mappa esplicita prima della pulizia:

```php
function generateSlug($title, $pdo) {
    $accents      = ['à','è','é','ì','ò','ù','À','È','É','Ì','Ò','Ù','â','ê','î','ô','û','ä','ë','ï','ö','ü'];
    $replacements = ['a','e','e','i','o','u','a','e','e','i','o','u','a','e','i','o','u','a','e','i','o','u'];
    $title = str_replace($accents, $replacements, $title);
    $slug  = strtolower(trim(preg_replace('/[^A-Za-z0-9-]+/', '-', $title)));

    // anti-collisione: se lo slug esiste, aggiunge un suffisso temporale
    $stmt = $pdo->prepare("SELECT COUNT(*) FROM articles WHERE slug = ?");
    $stmt->execute([$slug]);
    if ($stmt->fetchColumn() > 0) $slug .= '-' . time();
    return $slug;
}
```

Per i siti con contenuto italiano va usato sempre il pattern avanzato. (Le tre filosofie di slug dei vari siti, accenti compresi o elisi, sono dettagliate al Capitolo 9.)

## 2. Gestione del Fuso Orario

Su un hosting internazionale (un server a Los Angeles, per dire) `date()` e `time()` usano il fuso del server, e questo rompe la logica di visibilità `published_at <= NOW`, che per un sito italiano deve ragionare in ora italiana.

```php
// all'inizio di ogni endpoint con logica temporale
date_default_timezone_set('Europe/Rome');
$ita_now_str = date('Y-m-d H:i:s');   // ora italiana per i confronti SQL
```

La regola è semplice, la sua applicazione no. SimonePizziWebSite forza il fuso in **ogni** endpoint; SitoRuntime e DISINTELLIGENZA lo fanno solo in alcuni (`index.php`, `news.php`), e altrove no. Il risultato è una soglia di pubblicazione che si sposta a seconda di quale file la valuta.

> [!WARNING]
> **Il fuso va forzato ovunque, o non serve a niente**
> Forzare il timezone in un solo endpoint dà una falsa sicurezza: un articolo programmato può risultare già pubblicato per un file e ancora futuro per un altro, perché la stessa stringa `published_at` viene confrontata con un `NOW` calcolato in fusi diversi. SitoRuntime porta la cicatrice di questo problema in un `debug_time.php` che documenta un incidente sul separatore della data (lo spazio diventato `T`). La logica del confronto sulle date, e i tre modi di sbagliarla, è al Capitolo 9; qui basta la regola di bootstrap: se forzi il fuso, fallo nel prelude condiviso, non endpoint per endpoint.

## 3. Anatomia di un Endpoint: il Router su `REQUEST_METHOD`

Non c'è un router centrale. Ogni file in `public/api/` è un endpoint autonomo, e smista da sé in base al verbo HTTP della richiesta. È il pattern che rende il thin stack leggibile: l'URL `/api/articles.php` è il file `articles.php`, e dentro quel file c'è tutto ciò che lo riguarda.

```php
$method = $_SERVER['REQUEST_METHOD'];

if      ($method === 'GET')    { /* lettura: page, limit, slug, id, category, admin */ }
elseif  ($method === 'POST')   { Auth::check(); /* creazione */ }
elseif  ($method === 'PUT')    { Auth::check(); /* sostituzione completa */ }
elseif  ($method === 'PATCH')  { Auth::check(); /* aggiornamento parziale: toggle is_visible, sort_order */ }
elseif  ($method === 'DELETE') { Auth::check(); /* eliminazione */ }
```

Il gate non è uniforme sul file ma **selettivo sul ramo**: il `GET` di lettura resta pubblico, i rami che mutano lo stato passano da `Auth::check()`. Nei progetti più vecchi (DISINTELLIGENZA, SitoRuntime prima del refactor) le mutazioni viaggiavano tutte come `POST` con un campo `action` nel body; il pattern con i verbi separati è più leggibile e si sposa meglio con un client TypeScript espressivo.

## 4. I Tre Stili di Bootstrap

Prima di smistare la richiesta, un endpoint deve avviarsi: aprire la connessione, far partire la sessione, mandare gli header, gestire l'eventuale preflight CORS. Qui i tre siti occupano tre gradini, ed è un buon ritratto della scala del Capitolo 1.

**SimonePizziWebSite: prelude inline.** Ogni file include in testa i suoi mattoni (`require 'db.php'`, `require 'auth_helper.php'`, gli header) e apre la connessione subito. L'`auth_helper.php` incapsula `session_start()`, il `Content-Type` e la classe `Auth`:

```php
// auth_helper.php — session, header e Auth in un solo include
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

Concentrare `session_start()` e `header()` in un file solo riduce il rischio di «headers already sent» da spazi o BOM sparsi nei file.

**SitoRuntime: prelude condiviso `cors.php`.** Il sito serve un frontend che in sviluppo arriva da un'altra origine, quindi antepone a tutto un `cors.php` che gestisce header, `Content-Type` e il preflight `OPTIONS`, poi apre la connessione in modo lazy (`getDB()` con uno `static`, copiato in ogni file). La CORS reale **non** è aperta a tutti: è una allowlist di origini note, con riflessione dell'`Origin` ammesso.

```php
// cors.php — prelude condiviso: allowlist, non "*"; risponde al preflight e termina
$allowed = ['https://runtimeradio.com', 'https://www.runtimeradio.com', 'https://runtimeradio.it'];
$origin  = $_SERVER['HTTP_ORIGIN'] ?? '';
if (in_array($origin, $allowed, true)) {
    header("Access-Control-Allow-Origin: $origin");
    header('Vary: Origin');
}
header('Content-Type: application/json');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }
```

**DISINTELLIGENZA: inline minimale, niente CORS.** Sviluppa e pubblica same-origin, quindi non ha bisogno di header CORS: il `.htaccess` garantisce che frontend e API stiano sulla stessa origine, e il cookie di sessione parte da solo. Il bootstrap è ridotto all'osso.

> [!NOTE]
> **`Access-Control-Allow-Origin: *` quasi mai**
> L'asterisco va bene solo per un'API pubblica di sola lettura, senza cookie. Appena c'è una sessione, riflettere una allowlist di origini è la scelta corretta, e va accompagnata da una decisione esplicita su `Access-Control-Allow-Credentials` (SitoRuntime non lo emette, e di conseguenza l'autenticazione resta de-facto same-origin: il dettaglio, col suo riflesso sul client, è ai Capitoli 6 e 10).

### L'errore di connessione: tre risposte

Cosa succede quando il database non risponde è un piccolo test di maturità, e i tre siti lo passano in modo diverso.

```php
// SPW: codice HTTP corretto + JSON + log per la diagnosi
catch (PDOException $e) {
    http_response_code(500);
    error_log('DB: ' . $e->getMessage());                 // resta nei log, non va al client
    echo json_encode(['status' => 'error', 'message' => 'Database non disponibile']);
    exit;
}
```

SimonePizziWebSite risponde `500`, in JSON, e scrive l'eccezione nei log del server. SitoRuntime risponde `503` in JSON ma **non logga**, e così perde la diagnostica proprio quando servirebbe. DISINTELLIGENZA fa la cosa da non fare: `die("Connection failed: " . $e->getMessage())`, che stampa al client il messaggio dell'eccezione (path inclusi), senza un codice HTTP e fuori dal formato JSON.

> [!WARNING]
> **Un errore di connessione non deve mai parlare al client**
> Il messaggio di una `PDOException` può contenere percorsi del filesystem, nomi di database, dettagli che a un attaccante fanno comodo. La regola: codice HTTP corretto (`500` o `503`), un messaggio generico al client, e il dettaglio vero solo nei log del server con `error_log()`. Stampare `$e->getMessage()` in pagina, come fa DISINTELLIGENZA, è information disclosure gratuita.

## 5. Elaborazione Media

Caricare un file non è un semplice `move_uploaded_file`, è una trasformazione. Il `type` dell'upload mappa su cartelle diverse, ognuna con la sua politica: le immagini sono pubbliche e ridimensionate, gli audio dei podcast solo via admin, gli audio dei partecipanti su una cartella isolata e (nel caso del festival) ad accesso aperto. Ogni immagine dell'admin viene normalizzata a una larghezza massima (1920px), preservando il canale alpha di PNG e WebP. La trattazione completa, comprese le insidie di sicurezza dell'upload (la validazione dei byte reali, il naming, la catena RCE dell'upload pubblico), è al Capitolo 7: qui basta sapere che il file passa per GD prima di posarsi su disco.

## 6. Sicurezza dell'Input e dell'Output

- **Nomi dei file**: ogni upload viene rinominato con `uniqid()` e ripulito dai caratteri speciali, per non lasciare all'utente il controllo del nome (e quindi dell'estensione). Il perché è al Capitolo 7.
- **Integrità del JSON**: ogni risposta è preceduta da `header('Content-Type: application/json')`, e in caso di errore porta il codice HTTP giusto (`400`, `401`, `403`, `500`) insieme a un messaggio JSON descrittivo.
- **`FILTER_SANITIZE_STRING` è deprecato** (da PHP 8.1): al suo posto, `strip_tags(trim($var))`.

## 7. Gestione del Buffer

Un `Notice` o un `Warning` di PHP stampato in mezzo a una risposta la rende JSON non valido, e il frontend si rompe. La difesa è duplice: `display_errors = 0` in produzione (gli errori vanno nei log, non in pagina) ed eventualmente `ob_start()` per controllare cosa esce. È lo stesso principio dell'errore di connessione del §4: il client riceve dati puliti, la diagnostica resta sul server.

> [!IMPORTANT]
> **Il Canone**
> - File-per-endpoint con router su `REQUEST_METHOD`; gate selettivo sul ramo (GET pubblico, mutazioni dietro `Auth::check`).
> - CORS via allowlist di origini con `Vary`, mai `*` insieme alle credenziali.
> - L'errore di connessione si scrive nei log e risponde al client in modo generico: mai `getMessage()` in chiaro.
> - Forza il timezone in **ogni** endpoint con logica temporale, e in produzione `display_errors = 0`.

---
*Prossimo Capitolo: Frontend Bridge (API.ts). La connessione tra React e PHP, e i tre modi di leggere un payload che non ha un contratto stabile.*
