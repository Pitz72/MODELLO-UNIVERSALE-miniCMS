# CAPITOLO 17: Festival Logic - Iscrizioni e Workflow Approvazione (Terza Edizione)

Una premessa di onestà, prima del modulo. Il «festival» non è parte del core del miniCMS: è un **modulo opzionale**, presente in **un solo sito su quattro** (DISINTELLIGENZA), che FDCA eredita immutato perché ne è un fork con il backend byte-identico. I tre capitoli che seguono (questo, le votazioni, la dashboard) raccontano un concorso a voto pubblico reale, con i suoi pregi e le sue crepe, non un componente standard da dare per scontato.

Questo primo capitolo copre la porta d'ingresso: come un partecipante si iscrive, come l'admin lo valuta, e i due punti in cui il modulo idealizzato diverge dal codice (l'iscrizione alla newsletter e il caricamento pubblico delle tracce).

## 1. Il Workflow del Partecipante

L'iscrizione segue una pipeline a tre stati, gestita non da una macchina a stati ma da una colonna `status` che l'admin fa avanzare.

- **`pending`**: stato iniziale. Il partecipante ha inviato i dati e la traccia, ma non è visibile sul sito.
- **`approved`**: validato. Riceve l'email di conferma, entra nel concorso ed (vedi §4) viene iscritto alla newsletter.
- **`rejected`**: scartato, con una notifica di cortesia.

C'è però un dettaglio di sicurezza che il workflow «pulito» nasconde: l'azione che cambia lo stato (`update_status`) è protetta solo da un controllo di sessione, non di ruolo. Significa che **anche un editor**, non solo un amministratore, può approvare o respingere i partecipanti.

> [!WARNING]
> **Il gate che confonde «loggato» con «admin»**
> Approvare un partecipante è una decisione che pesa: lo fa entrare nel concorso, gli invia un'email a tuo nome, lo iscrive alla newsletter. Eppure il backend la concede a chiunque sia loggato, senza verificare che sia un amministratore. È lo stesso «gate role-blind» che attraversa più punti del sito (Capitolo 10): nascondere una voce di menu a un editor è esperienza utente, ma impedirgli un'azione è sicurezza, e va fatto sul ruolo, lato server. Qui non è fatto.

## 2. Le Email Transazionali

A ogni cambio di stato il backend invia un'email con un template HTML coerente col branding del festival: una conferma tecnica alla ricezione, e una comunicazione formale (positiva o negativa) all'esito. Il trasporto è `mail()` nativa, *fire-and-forget*: il record nel database è la fonte di verità, l'email è un canale best-effort (la meccanica completa, con i suoi limiti, è al Capitolo 13).

## 3. Gli Asset dei Partecipanti: l'Upload Pubblico che Apre una Porta

Le tracce audio caricate dai partecipanti finiscono in una cartella isolata (`uploads/audio/participants/`) con nome univoco, e l'admin le pre-ascolta nel Media Center prima di decidere. Fin qui la versione comoda. La versione vera è che quel caricamento, per abbassare l'attrito dell'iscrizione, **non richiede login**, ed è il fronte da cui parte la catena RCE descritta al Capitolo 7.

> [!WARNING]
> **L'upload pubblico delle tracce cambia tutte le regole**
> Un form di iscrizione che accetta file senza autenticazione è una superficie d'attacco aperta a Internet. In DISINTELLIGENZA quattro debolezze si sommano: il caricamento è pubblico, la validazione si fida del Content-Type dichiarato dal browser, il nome del file conserva l'estensione, e la cartella non spegne PHP. Il risultato, verificato, è l'esecuzione di codice remoto (la catena completa, anello per anello, è al Capitolo 7). La lezione per chi costruisce un'iscrizione senza attrito: l'apertura al pubblico è una scelta di prodotto legittima, ma va pagata con le difese che quell'apertura richiede (validare i byte reali, neutralizzare il nome, spegnere PHP nella cartella), non con la loro assenza. FDCA, essendo un fork, ha ereditato la stessa porta aperta intatta.

## 4. L'Iscrizione alla Newsletter all'Approvazione

All'approvazione, l'indirizzo del partecipante viene inserito nella tabella della newsletter con un `INSERT OR IGNORE`. Il modulo idealizzato lo presenta come una «strategia di crescita» del database marketing, che garantirebbe una lista di soli utenti reali e validati. È il framing da rovesciare.

> [!WARNING]
> **Iscriversi a un concorso non è acconsentire al marketing**
> Chi invia la propria traccia acconsente a partecipare al festival, non a ricevere una newsletter: sono due basi giuridiche diverse (Capitolo 13). Iscrivere d'ufficio i partecipanti approvati alla mailing list, senza un consenso esplicito e separato, è un problema di conformità GDPR, non un pregio di prodotto. I commenti nel sorgente tradiscono il dubbio dello stesso sviluppatore. La soluzione è semplice e va nella direzione opposta a quella «comoda»: un consenso marketing distinto, opt-in, raccolto al momento dell'iscrizione e registrato; l'approvazione al concorso non deve trascinarsi dietro l'iscrizione alla newsletter come effetto collaterale.

> [!IMPORTANT]
> **Il Canone**
> - Workflow `pending → approved/rejected` con master switch `registration_active`.
> - L'upload pubblico delle tracce è il fronte della catena RCE: gatelo e validalo come ogni upload (Capitolo 7).
> - L'approvazione è un'azione admin: gate per **ruolo**, non solo per login (niente gate role-blind).
> - Iscriversi a un concorso non è consenso al marketing: niente sync della newsletter senza opt-in esplicito e separato.

---
*Prossimo Capitolo: Festival Logic, Votazioni e Protezione Anti-Frode. Il voto pubblico, le difese che contano davvero e quelle solo cosmetiche.*
