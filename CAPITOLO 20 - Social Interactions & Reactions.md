# CAPITOLO 20: Social Interactions & Reactions (Terza Edizione)

Quasi tutto, nel CMS, è scrittura riservata: pubblicare un articolo, caricare un file, comporre una newsletter, ognuna di queste azioni vive dietro `Auth::check()`. Ci sono due eccezioni, e questo capitolo parla di loro. Le **reazioni** agli articoli e i **messaggi** del form contatti sono le uniche due superfici in cui un visitatore non autenticato scrive davvero nel database. Sono il fronte più esposto del sito, e proprio per questo concentrano le difese più sofisticate che SimonePizziWebSite abbia costruito.

Una premessa necessaria: le reazioni esistono **solo** in SimonePizziWebSite. SitoRuntime e DISINTELLIGENZA non le hanno; la superficie dei messaggi, invece, ritorna altrove come form contatti. Quindi il capitolo è in larga parte mono-sito, ma la sua lente, *come il thin stack gestisce la scrittura pubblica anonima*, tocca fili che attraversano tutto il libro: l'identità hashata e l'anti-abuso (CAP 10), la sanitizzazione (CAP 8), l'email best-effort (CAP 13), il voto del festival (CAP 18).

E c'è un GOLD che vale la lettura: nello stesso codebase convivono **due filosofie opposte** di sanitizzazione. Il contenuto degli articoli, scritto da un admin di cui ci si fida, è salvato grezzo e ripulito al momento di mostrarlo; il testo dei messaggi, scritto da chiunque passi, è ripulito al momento di salvarlo. Non è una contraddizione: è la scelta giusta per ciascun contesto, e le due si guardano in faccia proprio qui.

---

## 1. Due superfici, un solo principio: difendere all'ingresso

Sotto le differenze, le due superfici condividono cinque tratti.

Entrambe sono endpoint-router su `REQUEST_METHOD` con un **gate selettivo**: in `messages.php` il `POST` è pubblico (chiunque invia un messaggio), mentre `GET`, `PUT` e `DELETE` (lista, marca-letto, elimina) passano da `Auth::check()`; le reazioni sono interamente pubbliche, e non hanno alcun ramo admin. L'identità di chi scrive è uno **pseudonimo derivato**, non un account né un cookie. L'integrità è affidata al **database**, non solo a una `if` applicativa. L'input pubblico è ripulito **al momento della scrittura**. E tutto degrada con grazia: le reazioni cadono a conteggio zero su qualsiasi errore (la pagina articolo non si rompe mai), e la mail di notifica è best-effort, perché la verità sta nel record salvato, non nell'email partita.

I prossimi paragrafi prendono questi cinque tratti uno per uno, partendo da quello che il modulo dichiara di sé con un po' troppa generosità: l'anonimato.

---

## 2. L'identità anonima, e perché un hash non è anonimato

Il votante non ha un account. Viene identificato da uno pseudonimo calcolato al volo dai due dati che il server vede a ogni richiesta: l'indirizzo IP e lo User-Agent.

```php
// SPW reactions.php:25-29 — pseudonimo anonimo, nessun dato personale persistito in chiaro
$voter_hash = hash('sha256',
    ($_SERVER['REMOTE_ADDR'] ?? 'unknown') .
    ($_SERVER['HTTP_USER_AGENT'] ?? 'unknown')
);
```

È una buona idea: nel database non finisce un indirizzo IP in chiaro, ma una stringa che non significa nulla per chi la legge. È meglio di quello che fa il voto del festival, che gli IP li salva in chiaro (CAP 18). Ma qui serve una precisazione onesta, perché è facile raccontarla meglio di com'è. Questo hash **non è salato**, e lo spazio degli indirizzi IPv4 è piccolo: poco più di quattro miliardi di valori, che un computer prova tutti in un tempo ridicolo. Combinato con uno User-Agent plausibile, un `SHA256(IP+UA)` senza salt si **inverte per forza bruta**. Non protegge l'IP, lo offusca soltanto.

> [!WARNING]
> **Un hash non è anonimato: è pseudonimizzazione, e ha dei limiti**
> «Lo hashiamo, quindi è anonimo e a norma» è una frase che si sente spesso, e quasi sempre è falsa. Un hash è una funzione deterministica: lo stesso input dà sempre lo stesso output, e se lo spazio degli input è piccolo (gli IP lo sono) chiunque può costruirsi la tabella inversa. Quello che si ottiene è pseudonimizzazione, utile per non avere l'IP in chiaro nel database, non anonimato irreversibile. Per renderlo davvero difficile da invertire serve un **salt segreto** custodito sul server e mai esposto: senza quello, l'hash è un lucchetto con la chiave appesa accanto. È comunque un passo avanti rispetto a salvare l'IP nudo; il problema è solo dichiararlo più di quello che è.

Un dettaglio minore nella stessa direzione: sia le reazioni sia i messaggi leggono il `REMOTE_ADDR` grezzo, non l'helper anti-spoofing `getClientIp()` usato altrove nel sito (CAP 10). Dietro un proxy o una CDN questo può far collassare molti visitatori su uno stesso indirizzo, e rendere il rate-limit del prossimo paragrafo più severo del dovuto.

---

## 3. Il rate-limit a due strati: perché uno solo non basta

Per impedire a uno script di gonfiare i conteggi, le reazioni hanno un limite di frequenza. Il primo strato conta le azioni recenti per `voter_hash`: oltre venti al minuto, la richiesta viene respinta. Sembra sufficiente, ma c'è una crepa, ed è il cuore di questo capitolo: lo `voter_hash` include lo User-Agent, che è un'intestazione **scelta dal client**. Basta cambiarla a ogni richiesta per ottenere un hash diverso ogni volta, e il primo strato non vede mai due azioni dello «stesso» votante.

La versione 1.19.0 ha tappato la crepa con un secondo argine, ancorato a una chiave che il client non controlla: il **solo IP**.

```php
// SPW reactions.php:92-119 — due strati, perché il primo è aggirabile
// Strato 1: per voter_hash (IP + UA), max 20/min — ma lo UA lo sceglie il client
$stmtRate = $pdo->prepare("SELECT COUNT(*) FROM article_reactions
    WHERE voter_hash = ? AND created_at >= DATE_SUB(NOW(), INTERVAL 1 MINUTE)");   // >= 20 -> 429

// [v1.19.0] Strato 2: per SOLO IP, max 30/min — riusa login_attempts con namespace 'rea:'
$rl_key = 'rea:' . substr(hash('sha256', $ip), 0, 40);
$stmtIpRate = $pdo->prepare("SELECT COUNT(*) FROM login_attempts
    WHERE ip_address = ? AND attempt_time >= DATE_SUB(NOW(), INTERVAL 1 MINUTE)");  // >= 30 -> 429
```

Il secondo strato riusa la tabella `login_attempts`, la stessa che difende il login dalla forza bruta (CAP 10) e la newsletter dal mail-bombing (CAP 13), distinguendo gli usi con un prefisso di namespace (`rea:`). Una tabella, tre lavori.

> [!TIP]
> **Se la chiave del rate-limit include input del client, serve un secondo strato**
> È un errore facile e diffuso: si sceglie una chiave «forte» per il rate-limit (qui IP più User-Agent, più specifica del solo IP) senza accorgersi che una sua parte è sotto il controllo di chi vuoi limitare. Lo User-Agent lo decide il browser, e un attaccante lo cambia a ogni richiesta con una riga di codice: la chiave diventa nuova ogni volta e il limite non scatta mai. La difesa è affiancare un secondo strato su una chiave che il client non può falsificare a piacimento, come l'IP. I due strati lavorano insieme: il primo è preciso sui casi normali, il secondo regge quando il primo viene aggirato.

---

## 4. L'integrità vive nello schema, non nel codice

Una reazione funziona a interruttore: se non l'hai ancora data, un clic la aggiunge; se ce l'hai già, un altro clic la toglie. Questa logica sta nel codice, ma non è lì che vive la garanzia anti-doppione. Quella sta nello schema della tabella.

```sql
-- SPW migrate_reactions.php:19-27 — la UNIQUE KEY è la vera barriera anti-duplicato
CREATE TABLE IF NOT EXISTS article_reactions (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    article_id  INT NOT NULL,
    reaction    VARCHAR(20) NOT NULL,
    voter_hash  VARCHAR(64) NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_vote (article_id, voter_hash, reaction)   -- doppio voto impossibile per costruzione
);
```

```php
// SPW reactions.php:129-145 — il toggle nel codice; l'INSERT IGNORE si appoggia alla UNIQUE KEY
if ($existing) { /* DELETE: rimuovi */ }
else { $pdo->prepare("INSERT IGNORE INTO article_reactions (article_id, reaction, voter_hash)
    VALUES (?, ?, ?)")->execute([$article_id, $reaction, $voter_hash]); }
```

La differenza è sottile ma decisiva. Un controllo applicativo del tipo «leggi se esiste, poi inserisci» può essere scavalcato da una race condition: due richieste quasi simultanee leggono entrambe «non esiste» e inseriscono entrambe. La `UNIQUE KEY` invece rifiuta il duplicato a prescindere da cosa fa il codice, anche sotto doppio clic o richieste in corsa. È il principio del database come guardiano dell'integrità, ed è esattamente ciò che manca al contatore denormalizzato dei voti del festival (CAP 18), dove l'assenza di un vincolo equivalente lascia spazio al disallineamento.

> [!NOTE]
> **Lascia che sia il database a garantire l'integrità**
> Quando una regola dice «questa combinazione può esistere una volta sola», il posto giusto per imporla è un vincolo nello schema, non un `if` nel codice applicativo. Il vincolo regge sotto concorrenza, sopravvive ai bug del codice che gli gira intorno, e vale per ogni via di scrittura presente e futura. Il codice può occuparsi dell'esperienza (il toggle, il messaggio all'utente); l'integrità, lasciala al motore che la sa difendere davvero.

---

## 5. La seconda superficie: i messaggi, e le due filosofie di sanitizzazione

Le reazioni sono metà del cluster. L'altra metà è `messages.php`, il form contatti. La tabella si crea da sola alla prima chiamata (lo schema viaggia col codice, con un `CREATE TABLE IF NOT EXISTS` e un `ALTER` difensivo), il `POST` è pubblico con il suo rate-limit (tre messaggi per IP ogni quindici minuti, contati sulla propria tabella), e la notifica all'amministratore è una `mail()` nativa fire-and-forget: se l'invio fallisce, il visitatore vede comunque «messaggio inviato», perché il record è già salvato e l'email è solo un canale secondario (CAP 13).

Ma il punto che conta è come viene trattato il testo che arriva da fuori. Viene ripulito **prima** di toccare il database.

```php
// SPW messages.php:86-90 — input pubblico ripulito al WRITE-TIME: ciò che entra nel DB è già innocuo
$name    = trim(strip_tags($data['name']    ?? ''));
$email   = trim(filter_var($data['email']   ?? '', FILTER_SANITIZE_EMAIL));
$subject = trim(strip_tags($data['subject'] ?? ''));
$message = trim(strip_tags($data['message'] ?? ''));
```

Qui si chiude il filo dell'input pubblico, e lo fa con una polarità rovesciata rispetto agli articoli. Il contenuto di un articolo (CAP 8) è scritto da un admin di cui ci si fida, viene salvato grezzo per non perderne la formatura ricca, e viene ripulito con DOMPurify solo **al momento di mostrarlo** (render-time). Il testo di un messaggio arriva da uno sconosciuto, e viene ripulito con `strip_tags` **al momento di salvarlo** (write-time): nel database finisce qualcosa di già privo di tag, e lo stored-XSS è neutralizzato all'origine. C'è pure una seconda rete: il pannello admin mostra il messaggio come text-node React, che riscrive da solo i caratteri speciali, e non usa mai `dangerouslySetInnerHTML`.

> [!IMPORTANT]
> **Write-time o render-time: dove ripulire l'input dipende da chi te lo manda**
> Nello stesso codebase convivono due strategie opposte, e nessuna delle due è sbagliata. L'input pubblico e non fidato va neutralizzato il prima possibile, alla scrittura: meno cose pericolose tieni nel database, meglio dormi. Il contenuto ricco e fidato (un articolo formattato) va invece preservato così com'è e ripulito dove serve la fedeltà, alla lettura, perché ripulirlo alla scrittura distruggerebbe la formattazione legittima. La domanda non è «write-time o render-time» in astratto, ma «di chi mi fido per questo dato»: la risposta decide il momento. Sbagliare verso non è elegante: salvare grezzo l'input pubblico apre lo stored-XSS, ripulire alla scrittura il contenuto editoriale lo mutila.

Un paio di note di contorno, per onestà. Il `POST` pubblico non ha protezione CSRF, ed è corretto così: non c'è un'azione privilegiata da forgiare, l'unico argine sensato è il rate-limit. E il doppio checkbox di consenso GDPR del form è verificato **solo lato client**: chi invia direttamente all'endpoint lo salta. È coerente con l'idea che il consenso sia esperienza utente e non barriera tecnica, ma va saputo.

---

## 6. Reazione contro voto: tarare l'anti-abuso sulla posta in gioco

Le reazioni di SimonePizziWebSite e il voto del festival di DISINTELLIGENZA (CAP 18) sono, tecnicamente, lo stesso gesto: scrittura pubblica anonima difesa da un'identità hashata e da una barriera anti-doppione. Ma servono a due cose diverse, e la rigidità è tarata di conseguenza. La reazione è libera e plurima: puoi darne più d'una allo stesso articolo, toglierle, rimetterle, e l'anti-abuso è leggero perché la posta in gioco è bassa. Il voto del festival è singolo e sorvegliato: una sola espressione per partecipante, una barriera per IP a finestra di ventiquattr'ore, un interruttore generale che lo chiude del tutto, perché lì si decide una classifica e l'incentivo a barare è reale.

> [!NOTE]
> **Stessa meccanica, due tarature: pesa l'anti-abuso sulla posta in gioco**
> È inutile sorvegliare un «mi piace» come se fosse un'urna elettorale, e pericoloso trattare un voto che assegna un premio con la leggerezza di un like. La stessa cassetta degli attrezzi (identità derivata, vincolo di unicità, rate-limit) si tara su due livelli di rigidità a seconda di quanto costa l'abuso. Capire dove sta la posta in gioco, prima di scrivere il codice anti-frode, è ciò che evita sia la frizione inutile sia la difesa insufficiente.

---

## 7. La micro-interazione: ottimistica, ma con rete

Lato client la barra delle reazioni aggiorna il conteggio e lo stato del pulsante **prima** che il server risponda: il clic sembra istantaneo. Se la richiesta fallisce, l'aggiornamento viene annullato e la UI torna allo stato reale. È l'optimistic UI dei social, con il rollback che la rende onesta. Insieme alla degradazione a conteggio zero vista al §1 (se le reazioni non caricano, l'articolo si legge lo stesso), è il modo in cui un modulo «di contorno» non diventa mai un punto di rottura della pagina.

---

## In sintesi

La scrittura pubblica anonima è il punto più esposto del CMS, e SimonePizziWebSite lo difende con cura: identità derivata invece dell'IP in chiaro, integrità imposta dallo schema invece che dal codice, rate-limit a due strati invece di uno aggirabile, e input ripulito all'ingresso invece che fidato. La lezione che lega tutto è quella delle due filosofie di sanitizzazione: non esiste un posto giusto in assoluto dove ripulire l'input, esiste la domanda «di chi mi fido», e la risposta cambia il verso della difesa. Resta da ricordare anche cosa il modulo *non* è: l'hash non rende anonimo nessuno, lo offusca; il consenso del form è cortesia, non barriera. Saperlo, e non raccontarsi che il lucchetto è più solido di com'è, è parte della stessa onestà tecnica che attraversa tutto il libro. Qui finisce il giro dentro il CMS: dalle fondamenta del backend fino all'ultimo clic di un visitatore che non sapremo mai chi è.

---
*Fine della Parte V. Le appendici raccolgono i materiali di servizio: la checklist per partire da zero e il caso del fork (FDCA), il progetto che eredita un intero CMS, debiti di sicurezza compresi.*
