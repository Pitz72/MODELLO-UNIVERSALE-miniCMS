# CAPITOLO 18: Festival Logic - Votazioni e Protezione Anti-Frode

Il voto è il cuore del concorso, ed è anche il punto in cui un modulo apparentemente robusto rivela quali delle sue difese contano davvero e quali sono solo decorazione. Questo capitolo distingue le une dalle altre, e mette in chiaro due fragilità che il testo idealizzato taceva: la classifica può derivare in silenzio, e il reset non è protetto.

## 1. La Sessione di Voto

Un visitatore può esprimere da una a tre preferenze in una sola chiamata. Il backend valida che ogni partecipante votato sia davvero in gara (`status = 'approved'` e `in_current_round = 1`), poi registra il voto in una transazione che fa due cose insieme: inserisce la riga in `votes` e incrementa il contatore sul partecipante.

```php
// ogni voto è una transazione: INSERT + incremento del contatore denormalizzato
$pdo->beginTransaction();
$pdo->prepare("INSERT INTO votes (participant_id, ip, user_agent) VALUES (?, ?, ?)")
    ->execute([$pid, $ip, $ua]);
$pdo->prepare("UPDATE participants SET vote_count = vote_count + 1 WHERE id = ?")->execute([$pid]);
$pdo->commit();
```

Quel `vote_count` non è una comodità: è la **fonte di verità della classifica**. L'ordinamento dei partecipanti si fa per `vote_count`, non contando le righe di `votes`. È una scelta di performance ragionevole (la classifica diventa una `SELECT ... ORDER BY vote_count`), ma ha un prezzo che il §5 mette a fuoco.

## 2. Le Difese Anti-Abuso, in Ordine di Efficacia Reale

Il modulo presenta tre difese contro il voto multiplo. Il punto, però, è che non sono affatto equivalenti: una regge, una è cosmetica, una non difende nulla. Distinguerle conta, perché confonderle dà una falsa sicurezza.

- **La barriera reale: IP per ventiquattr'ore.** Il backend registra l'indirizzo IP del votante e rifiuta nuovi voti dallo stesso IP per le ventiquattr'ore successive. È l'unica difesa server-side che un attaccante non aggira dal proprio browser.
- **La difesa cosmetica: il cookie.** Dopo il voto viene impostato un cookie (`dis_voted`) con scadenza a trenta giorni. Vive sul client, quindi chiunque lo cancella, apre una finestra anonima o cambia browser e rivota. Migliora l'esperienza dell'utente onesto (gli ricorda che ha già votato), non ferma chi vuole barare.
- **Nessuna difesa, solo registro: lo User-Agent.** Ogni voto memorizza lo `User-Agent`, ma non viene usato per bloccare niente: serve solo a un'eventuale analisi a posteriori.

> [!WARNING]
> **Tre difese, una sola conta**
> Elencare cookie, IP e User-Agent come se fossero tre lucchetti equivalenti è un errore comune e pericoloso, perché chi legge crede di avere una difesa a tre strati quando ne ha una sola. Il cookie e lo User-Agent sono sotto il controllo del client: il primo si cancella, il secondo si falsifica. La sola barriera che vive sul server, e che quindi può davvero limitare l'abuso, è quella basata sull'IP. Conoscere quale difesa regge davvero è ciò che evita di lasciare un concorso indifeso credendolo blindato.

Sull'IP c'è un'osservazione controintuitiva (Capitolo 10): il modulo usa il `REMOTE_ADDR` grezzo, non un helper che legge gli header di forwarding. Per un'autenticazione dietro proxy sarebbe un difetto, ma per un voto pubblico è un **pregio**: l'header `X-Forwarded-For` lo scrive il client e si falsifica, mentre il `REMOTE_ADDR` no. Il rovescio è la collisione NAT: dietro una stessa rete aziendale o universitaria, molti votanti legittimi condividono un IP e si bloccano a vicenda.

> [!NOTE]
> **Il contrappunto privacy: l'identità hashata delle reazioni**
> Il voto del festival salva IP e User-Agent **in chiaro** nella tabella `votes`: dati personali persistiti senza offuscamento. Le reazioni agli articoli (Capitolo 20) affrontano lo stesso problema in modo più attento, derivando uno pseudonimo `SHA256(IP+UA)` invece di salvare l'IP nudo. Nessuno dei due è anonimato perfetto (quell'hash è reversibile, vedi Capitolo 20), ma è la differenza tra «ho offuscato il dato» e «ho conservato l'indirizzo di tutti i votanti in chiaro». Per un modulo che raccoglie voti dal pubblico, salvare l'IP grezzo è una scelta da pesare anche sul piano GDPR, non solo dell'anti-frode.

## 3. I Round a Interruttore

Un partecipante compare nella pagina di voto solo se è `approved` **e** `in_current_round = 1`. Le fasi del concorso (eliminatorie, semifinali, finale) non sono entità con una storia: sono questo flag, acceso o spento dall'admin su gruppi di partecipanti. È la semplicità del modulo, e anche il suo limite.

> [!WARNING]
> **`reset_votes` cancella la storia del turno**
> Far avanzare il concorso significa azzerare i voti del turno e riaccendere il flag sul gruppo successivo. Ma `reset_votes` **cancella** i voti del turno precedente e riporta a zero il contatore: non esiste una storicizzazione per-turno, quindi i risultati delle eliminatorie spariscono, salvo la copia `.bak` che il sistema fa prima delle operazioni distruttive (Capitolo 10). Gestire le fasi con un solo flag booleano è comodo, ma se vuoi conservare i risultati di ogni turno devi archiviarli prima del reset: il modulo, da solo, non lo fa.

## 4. Il Master Switch del Voto

La possibilità di votare è regolata da un interruttore globale (`voting_active`) nella tabella `settings`: se è spento, il backend rifiuta ogni voto con un `403`. La tabella `settings` è leggibile pubblicamente (il frontend la consulta per mostrare o nascondere il form) e scrivibile solo dall'admin.

Un dettaglio rivela una piccola incoerenza interna: la lettura del flag accetta sia `'1'` sia `'true'`, perché un punto del codice salva i booleani come `'1'` e un altro come la stringa `'true'`. La lettura difensiva (`=== '1' || === 'true'`) compensa il fatto che la scrittura non ha mai fissato una convenzione. Funziona, ma è il sintomo da riconoscere: quando il lettore deve indovinare come ha scritto lo scrittore, manca un accordo a monte.

## 5. La Classifica che può Derivare

Resta la fragilità più sottile, e la più importante per l'equità del concorso. Siccome la classifica si ordina per `vote_count` (il contatore denormalizzato del §1) e non per il conteggio reale delle righe di `votes`, i due valori possono divergere. La transazione li tiene allineati nel funzionamento normale, e il reset li riazzera insieme, ma non esiste una **reconciliation**: nessun controllo periodico verifica che `vote_count` corrisponda davvero al numero di voti registrati.

> [!WARNING]
> **Denormalizzare un contatore: velocità contro verità**
> Tenere il totale dei voti in una colonna rende la classifica istantanea, ma la rende anche fragile: basta una transazione interrotta a metà, un import manuale, una correzione fatta a mano sul database, e il contatore non corrisponde più ai voti reali. Il guaio è che la divergenza è **silenziosa**: la classifica mostra un ordine che sembra giusto, e nessuno si accorge che è sbagliato finché qualcuno non conta i voti a mano. Quando un numero denormalizzato decide un esito (una classifica, un premio), serve una query di riconciliazione che periodicamente confronti il contatore con `COUNT(votes)` e segnali gli scostamenti. Il modulo non ce l'ha, ed è la prima cosa da aggiungere prima di affidargli un concorso vero.

C'è infine il reset stesso: le azioni che azzerano voti e contatori (`reset_votes`, `reset_system`) sono potenti e distruttive, ma **non hanno protezione CSRF** (Capitolo 10). Le circonda solo una conferma nel browser, che ferma il clic distratto ma non una richiesta forgiata da un altro sito mentre l'admin è loggato. La copia `.bak` pre-distruttiva è la rete che attenua il danno; la difesa che manca è il token.

> [!IMPORTANT]
> **Il Canone**
> - L'anti-frode reale è il vincolo IP + finestra temporale (24h); il cookie è cosmetico, lo User-Agent solo un indizio.
> - Per il voto pubblico l'IP grezzo è un pregio anti-spoof (a differenza dell'auth dietro proxy, Capitolo 10).
> - Se denormalizzi un contatore (`vote_count`), prevedi una riconciliazione periodica con `COUNT(votes)`, oppure accetti il drift silenzioso.
> - I reset distruttivi passano per un token CSRF più la copia `.bak`; la conferma nel browser non basta.

---
*Prossimo Capitolo: Festival Logic, Dashboard Admin, Settings e Reporting. Il pannello di controllo del concorso, e il report finale che non è mai stato acceso.*
