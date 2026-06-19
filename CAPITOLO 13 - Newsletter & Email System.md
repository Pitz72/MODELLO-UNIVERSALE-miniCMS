# CAPITOLO 13: Newsletter & Email System

Una lista email è uno dei pochi asset che un sito possiede davvero: non passa da un algoritmo, non rischia lo shadowban, non sparisce se una piattaforma chiude. I tre siti del Modello hanno tutti una newsletter fatta in casa, senza servizi esterni, e tutti la costruiscono sullo stesso scheletro thin-stack: un endpoint PHP che gestisce iscrizione e invio, e l'email composta come stringa HTML al volo.

Questo capitolo chiude un filo iniziato cinque capitoli fa. La newsletter è il **quarto e ultimo emettitore** del `content`: dopo il render (CAP 8), il prerender (CAP 11) e il feed (CAP 12), è l'ultimo posto da cui lo stesso HTML salvato grezzo potrebbe uscire verso un browser, quello del client di posta. La buona notizia, che vedremo alla fine, è che nessuno dei tre siti emette il `content` nell'email: il filo si chiude senza riaprire il buco XSS.

E proprio perché sul rischio XSS i tre convergono, la lente vera del capitolo diventa un'altra: **quanto si può semplificare un sistema di posta** prima che la semplificazione diventi pericolosa. Si va da un sistema completo, con double opt-in e protezione anti-abuso, fino a una `mail()` nuda che chiunque può usare per iscrivere o disiscrivere chiunque. E, come già al CAP 10, il sito col backend più ricco non è il più sicuro.

> [!NOTE]
> **Tre punti su cui è facile sbagliare.** Tre aspetti di questo sistema vengono spesso fraintesi. Il primo è il **double opt-in**, la feature-cardine di due siti su tre: ometterlo, e mostrare al suo posto un'iscrizione attiva da subito con disiscrizione per sola email, significa adottare il modello di DIS, il più debole. Quella disiscrizione per sola email **non è «GDPR-Compliant»**: è la versione insicura (chiunque disiscrive chiunque). E un `usleep` **non è «Rate Limiting»**: è un'altra cosa (§4).

---

## 1. Il ciclo di vita di un iscritto

Sotto le differenze, l'anatomia è condivisa. L'endpoint smista per `?action=`, con le azioni pubbliche servite prima di un gate centrale e quelle admin dopo. L'email viene sempre validata lato server, senza fidarsi del form, e la ri-iscrizione si gestisce in modo reattivo: si prova l'`INSERT` e si cattura la violazione del vincolo UNIQUE, restituendo un successo neutro che non rivela chi è già in lista.

```php
// public/api/newsletter.php (DIS) — validazione server-side + idempotenza per cattura del duplicato
$email = filter_var($input['email'] ?? '', FILTER_VALIDATE_EMAIL);
if (!$email) { echo json_encode(['status'=>'error','message'=>'Email non valida']); exit; }
try {
    getDB()->prepare("INSERT INTO subscribers (email) VALUES (?)")->execute([$email]);
    echo json_encode(['status'=>'success','message'=>'Iscrizione completata']);
} catch (PDOException $e) {
    if ($e->getCode() == 23000) {   // violazione UNIQUE → già iscritto, ma non lo riveliamo come errore
        echo json_encode(['status'=>'success','message'=>'Sei già iscritto!']);
    } else { echo json_encode(['status'=>'error','message'=>'Errore database']); }
}
```

La disiscrizione è «morbida»: nessuno cancella il record, l'iscritto viene marcato `is_active = 0`, così si preserva la storia e si evitano re-iscrizioni accidentali. E l'email finale, qualunque sia il sito, è costruita come stringa HTML con layout a tabelle e CSS inline (i client di posta non leggono fogli di stile esterni), con le immagini rese assolute e un placeholder nel link di disiscrizione, sostituito per ogni destinatario.

> [!NOTE]
> **Lo schema minimale non è quello reale.** La tabella `subscribers` a quattro colonne (`id`, `email`, `is_active`, `created_at`) è il modello di DIS. Lo schema reale di SPW e SR ha invece i campi del double opt-in: lo stato (`pending`/`confirmed`/`unsubscribed`), uno o più token, la data di conferma. In SR quello schema esteso convive con due versioni più vecchie create da altri script, una delle quali è un fossile SQLite che su MySQL si romperebbe: il runtime presuppone lo schema esteso e una query fallisce finché la migrazione giusta non è stata eseguita. È la stessa storia di «una tabella, più verità» del CAP 15.

---

## 2. Il double opt-in e il segreto del link di disiscrizione

Il double opt-in è la garanzia che chi iscrive un'email **possiede** quella casella: invece di attivare subito l'indirizzo, si crea un record in attesa e si manda un'email con un link di conferma; solo dopo il click l'iscrizione diventa attiva. È la feature più importante dell'intero sistema, e i tre siti la implementano su tre gradini.

SPW la fa nel modo da manuale, con **due token distinti**: uno di conferma, monouso, azzerato dopo l'uso; uno di disiscrizione, casuale e stabile, separato dal primo.

```php
// public/api/subscribers.php (SPW) — due token con scopi diversi
$confirmToken     = $forceConfirm ? null : bin2hex(random_bytes(32));   // monouso
$unsubscribeToken = bin2hex(random_bytes(32));                          // stabile, separato
$status           = $forceConfirm ? 'confirmed' : 'pending';
if (!$forceConfirm) { sendConfirmEmail($email, $name ?: 'Amico', $confirmToken); }
```

SR la fa con **un solo token** che serve a entrambi gli scopi, conferma e disiscrizione, e che non viene mai azzerato né scade. Ne derivano due piccole conseguenze. L'email di conferma promette che «il link scade dopo il primo utilizzo», ma è falso: il token sopravvive all'uso. E poiché lo stesso token finisce nell'URL di disiscrizione di *ogni* newsletter, chi inoltra una mail consegna a un altro il potere di disiscrivere quell'utente.

```php
// public/api/newsletter.php (SR) — un token, due scopi
// confirm: attiva l'iscrizione MA non azzera il token
"UPDATE subscribers SET is_active = 1, confirmed_at = NOW() WHERE confirmation_token = ?"
// send: l'URL di disiscrizione espone lo stesso confirmation_token
$unsubUrl = 'https://runtimeradio.com/unsubscribe?token=' . urlencode($sub['confirmation_token']);
```

DIS non ha né l'uno né l'altro. L'iscrizione è attiva subito, e la disiscrizione avviene per sola email, senza alcun token:

```php
// public/api/newsletter.php (DIS) — disiscrizione per sola email, via GET, senza token
if ($action === 'unsubscribe') {
    $email = filter_var($_GET['email'] ?? '', FILTER_VALIDATE_EMAIL);
    getDB()->prepare("UPDATE subscribers SET is_active = 0 WHERE email = ?")->execute([$email]);
    echo "<h1>Disiscrizione completata</h1>";   // chiunque conosca l'email può disiscriverla
}
```

> [!WARNING]
> **Il link di disiscrizione ha bisogno di un segreto**
> Questa disiscrizione per sola email viene spesso spacciata per «GDPR-compliant». È l'opposto: senza un token segreto, chiunque conosca o indovini l'indirizzo di un iscritto può disiscriverlo. E poiché è una `GET`, è anche *prefetch-able*: un client di posta che precarica i link può disiscrivere l'utente solo passandoci sopra. La versione corretta è quella di SPW, con un `unsubscribe_token` casuale e stabile (e, idealmente, una conferma con `POST` dalla pagina di atterraggio). Il double opt-in protegge l'ingresso; un token di disiscrizione protegge l'uscita. Servono entrambi.

---

## 3. Spedire: `mail()` nativa o SMTP autenticato

Il trasporto è il punto in cui SR si stacca dagli altri due. SPW e DIS usano la `mail()` nativa di PHP, che si appoggia al sendmail di sistema: zero configurazione, ma deliverability fragile, perché senza SPF e DKIM le email finiscono facilmente nello spam (DIS ha persino un commento «Fake domain?» accanto al mittente). SR usa invece PHPMailer con SMTP autenticato e STARTTLS, leggendo le credenziali dai segreti d'ambiente.

```php
// public/api/newsletter.php (SR) — SMTP autenticato via PHPMailer
$mail = new \PHPMailer\PHPMailer\PHPMailer(true);
$mail->isSMTP();
$mail->Host = $cfg['SMTP_HOST']; $mail->SMTPAuth = true;
$mail->Username = $cfg['SMTP_USER']; $mail->Password = $cfg['SMTP_PASS'];
$mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS; $mail->Port = $cfg['SMTP_PORT'];
$mail->setFrom($cfg['SMTP_USER'], $cfg['SMTP_FROM_NAME']);
```

C'è però una contraddizione interna: SR usa l'SMTP autenticato solo per la newsletter. Il form contatti, `contact.php`, è rimasto sulla `mail()` nativa. Lo stesso sito ha così due meccaniche di posta diverse: è facile pensare all'SMTP come a una scelta «per il futuro, a volumi maggiori», quando in realtà in SR è già in produzione, accanto alla `mail()` che non ha mai dismesso.

---

## 4. Il form che spara email a nome tuo

Arriva qui il difetto più istruttivo del capitolo, e nasce da una confusione comune tra due difese che sembrano simili e non lo sono.

Un **throttle** rallenta l'invio in uscita, per non sovraccaricare il mail server e non farsi mettere in greylisting: è una pausa ogni tot email. Un **rate-limit** limita le richieste in ingresso, per impedire a un estraneo di abusare di un endpoint: è un tetto di tentativi per IP. Sono difese ortogonali, su lati opposti del sistema. Quello che spesso viene chiamato «Rate Limiting» è in realtà un throttle:

```php
// public/api/newsletter.php (SR) — questo è un THROTTLE in uscita, non un rate-limit in ingresso
if ($count % 10 === 0) { usleep(500000); }   // mezzo secondo ogni 10 email: protegge il mail server
```

Il throttle protegge il *tuo* server di posta. Non protegge da chi martella il form di iscrizione. E qui sta il buco di SR: la sua `subscribe` non ha alcun rate-limit. L'IP del richiedente viene perfino registrato, ma solo memorizzato, mai usato come limite, e per giunta letto da `X-Forwarded-For` grezzo (falsificabile, come al CAP 10). Chiunque può quindi mandare richieste di iscrizione con email arbitrarie, e a ognuna parte una vera email di conferma via SMTP verso un terzo che non ha chiesto nulla. È un vettore di mail-bombing che brucia la reputazione del dominio e consuma la quota SMTP.

SPW invece il vettore lo chiude, riusando per la newsletter la stessa tabella `login_attempts` del login (con un prefisso diverso sulla chiave, per non mischiare i contatori):

```php
// public/api/subscribers.php (SPW) — rate-limit anti-mail-bombing che ricicla login_attempts
$rl_key = 'sub:' . substr(hash('sha256', $_SERVER['REMOTE_ADDR'] ?? 'unknown'), 0, 40);
$stmtRl = $pdo->prepare("SELECT COUNT(*) FROM login_attempts WHERE ip_address = ?");
$stmtRl->execute([$rl_key]);
if ((int)$stmtRl->fetchColumn() >= 3) { http_response_code(429); exit; }   // max 3 iscrizioni / 15 min
```

> [!WARNING]
> **Rate-limit in ingresso ≠ throttle in uscita**
> SR ha il throttle ma non il rate-limit; SPW ha il rate-limit ma non il throttle. Hanno difese opposte, e quella che manca a SR è quella che conta di più sulla sicurezza: senza un tetto in ingresso, il form di iscrizione diventa un'arma che spara email a nome tuo verso chiunque. È il ribaltamento già visto al CAP 10: SR, il sito più ingegnerizzato, lascia aperto proprio il buco che SPW, più semplice, aveva chiuso. E la beffa è che l'infrastruttura per limitare (la stessa `.cache/ratelimit/` del login) in SR esiste già: semplicemente non è stata riusata qui.

C'è poi un problema che accomuna tutti e tre, su una scala di rozzezza decrescente: l'invio è un `foreach` bloccante dentro la richiesta HTTP. Su una lista grande, la richiesta va in `max_execution_time` e la consegna si interrompe a metà, senza che nessuno lo sappia. SR è il meno peggio (ha il throttle e un `try/catch` per destinatario che conta gli errori); SPW conta solo il valore di ritorno di `mail()`; DIS lo ignora del tutto, e il contatore delle campagne registra i *tentativi*, non i successi. Nessuno dei tre ha una coda o un cron: è lo stesso anti-pattern del «lavoro pesante dentro la richiesta» visto con la conversione delle immagini al CAP 7.

---

## 5. Header injection dal campo nome

Un'ultima trappola, ed è in DIS, nel form contatti. Il nome inserito dall'utente viene ripulito con `strip_tags` prima di finire nel database, e questo va bene per il database. Ma quello stesso nome viene anche messo nell'oggetto dell'email di notifica all'admin, e lì `strip_tags` non basta:

```php
// public/api/contact.php (DIS) — strip_tags toglie i tag, NON gli a-capo
$name    = strip_tags($input['name'] ?? '');                       // sanitizzazione per il DB
$subject = "Nuovo Messaggio da $name - Disintelligenza";           // ...ma $name finisce nell'header Subject
$headers = "From: no-reply@...\r\nReply-To: $email\r\n";
mail('runtimeradio@gmail.com', $subject, $body, $headers);
```

`strip_tags` rimuove i tag HTML, ma non i caratteri di a-capo `\r\n`. Un nome che li contenga può iniettare header aggiuntivi nell'email, per esempio un `Cc` o un `Bcc` verso indirizzi scelti dall'attaccante. L'email del mittente, che finisce nel `Reply-To`, è invece al sicuro perché passata da `FILTER_VALIDATE_EMAIL`: il vettore è il nome, l'unico campo testuale libero che entra in un header.

> [!WARNING]
> **Sanitizzare per il database non è sanitizzare per gli header email**
> La sanitizzazione ha sempre un contesto. `strip_tags` neutralizza l'HTML, che è il pericolo quando il dato verrà mostrato in una pagina; ma quando lo stesso dato entra in un'intestazione di posta, il pericolo cambia forma, sono i `\r\n` a contare. La regola: per un header email, rimuovi o rifiuta i caratteri di controllo, e non mettere mai input dell'utente nelle intestazioni se puoi evitarlo. SR, non a caso, costruisce il `From` da un valore fisso, non dall'input.

---

## 6. Il filo dei quattro emettitori si chiude

Torniamo un'ultima volta alla tabella del CAP 8. La newsletter è la quarta casella, e in tutti e tre i siti la query d'invio seleziona titolo, riassunto, immagine e link, **mai il `content`**. L'email rimanda all'articolo con un «Leggi tutto», e il campo HTML grezzo difeso solo a render-time non viene mai toccato.

| # | Emettitore | Cosa emette del `content` | Difesa | Esito |
|---|---|---|---|---|
| 1 | **Render React** (CAP 8) | `content` pieno | DOMPurify (SPW, SR) / niente (DIS) | choke-point reale; DIS scoperto |
| 2 | **Prerender SEO** (CAP 11) | `content` pieno | `strip_tags` allowlist (solo tag) | **buco sugli attributi** (SPW, SR) |
| 3 | **Feed RSS** (CAP 12) | niente / preview escapata | `htmlspecialchars` / `strip_tags`+escape | sicuro |
| 4 | **Newsletter** (questo capitolo) | **niente** (solo titolo, riassunto, intro) | `htmlspecialchars` (SR, DIS) / grezzo dietro Auth (SPW) | **sicuro** |

Si potrebbe leggere la query senza `content` come una semplice «ottimizzazione di payload», per tenere le email leggere. È vero, ma è soprattutto la chiusura del filo: non emettere il campo grezzo è ciò che impedisce all'email di diventare un quinto vettore XSS.

C'è una simmetria curiosa tra i due flagship. In SR la newsletter è l'emettitore *più* sicuro dei quattro: non tocca il `content` e per giunta escapa ogni altro campo. In SPW è invece il *meno* sanitizzato, perché il testo introduttivo scritto dall'admin viene emesso grezzo, senza alcun `htmlspecialchars`: è sicuro solo perché chi lo scrive è autenticato, non perché ci sia una difesa. Due posizioni opposte sulla stessa scala.

> [!IMPORTANT]
> **Il quadro completo: una sanitizzazione, quattro render-path**
> Con la newsletter il filo dei quattro emettitori si chiude. Feed e newsletter non riaprono il buco, perché o non emettono il `content` o lo escapano. L'unica falla che resta viva in tutto il quadro è il prerender del CAP 11, con il suo `strip_tags` ad allowlist che lascia passare gli attributi. La conclusione, ripetuta da cinque capitoli, è sempre la stessa: la sanitizzazione del contenuto dovrebbe vivere una volta sola, lato server, condivisa da tutti gli emettitori, invece di essere reinventata (o dimenticata) da ognuno. Il fatto che il buco sia rimasto aperto in un solo punto su quattro non è merito dell'architettura: è fortuna, più la disciplina di chi ha scritto gli altri tre.

---

## 7. Il consenso, e dove sparisce

Resta il lato GDPR dell'iscrizione, che non è solo una questione di token ma di consenso. Sul form, SPW chiede il doppio assenso esplicito (trattamento dei dati e dichiarazione di maggiore età); SR ne chiede uno solo, e ha una variante «minimal» del form, pensata per il footer, che non ha alcun checkbox. DIS, sul form, valida e basta.

Ma il caso più interessante è in DIS, e non passa nemmeno dal form. Un'email può entrare nella lista anche da una seconda porta: quando un partecipante al festival viene approvato, il suo indirizzo viene aggiunto agli iscritti con un `INSERT OR IGNORE`, **senza un consenso esplicito alla newsletter**. I commenti nel codice mostrano lo stesso sviluppatore in dubbio se sia corretto.

> [!WARNING]
> **Il consenso come effetto collaterale**
> Iscrivere qualcuno a una lista perché ha fatto *un'altra* cosa (candidarsi a un festival) è una raccolta di consenso che il GDPR non considera valida: il consenso deve essere specifico per quella finalità. È una trappola facile, perché il codice che lo fa sembra innocuo: una riga di `INSERT` in coda all'approvazione. La regola: ogni porta d'ingresso a una lista email deve avere il suo consenso, esplicito e separato. Il trattamento completo del workflow del festival è ai capitoli che lo riguardano; qui basta la lezione.

---

## In sintesi

La newsletter mostra una scala di semplificazione che è anche una scala di rischio. SPW è il gradino completo: double opt-in con due token distinti, rate-limit contro il mail-bombing, link di disiscrizione con segreto, consenso doppio. SR aggiunge il trasporto più serio, l'SMTP autenticato, ma toglie il rate-limit (e apre il vettore mail-bombing) e fonde i due token in uno solo. DIS toglie anche il double opt-in e ogni token, e lascia un'iniezione di header nel nome del form contatti, pur conservando due buone abitudini d'igiene (la validazione dell'email ovunque e la pulizia in scrittura). Sul `content`, però, tutti e tre fanno la cosa giusta: non lo emettono, e il filo dei quattro emettitori si chiude. La difesa che manca più spesso non è quella contro l'XSS, che qui è risolta per disciplina: è quella contro l'abuso del proprio stesso form.

> [!IMPORTANT]
> **Il Canone**
> - Double opt-in con due token distinti (conferma monouso + disiscrizione stabile): il link di disiscrizione ha bisogno di un segreto, non basta l'email in chiaro.
> - Rate-limit (tetto per IP) sull'iscrizione contro il mail-bombing; non confonderlo col throttle, che regola solo la cadenza d'invio.
> - Sanitizza per gli header email (i `\r\n`), non solo per il DB: il nome è un vettore di header injection.
> - Consenso GDPR esplicito; l'invio di massa, meglio se asincrono o in coda.

---
*Prossimo Capitolo: Admin Dashboard & Panels. Il pannello di controllo che lega insieme i sistemi visti finora, e i tre modi molto diversi in cui i siti decidono cosa un amministratore può vedere e fare.*
