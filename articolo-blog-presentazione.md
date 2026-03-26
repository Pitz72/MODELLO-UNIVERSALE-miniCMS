# Ho scritto un manuale. E non avrei dovuto farlo.

*Pubblicato il 26 marzo 2026 — Simone Pizzi*

---

Ci sono cose che si fanno senza sapere che le si sta facendo.

Anni di codice scritto, di siti lanciati, di crash notturni risolti alle tre di mattina con il caffè freddo sul tavolo e un terminale aperto su tre schermi. Anni di pattern riscoperti ogni volta, di soluzioni reinventate, di lezioni imparate e poi dimenticate e imparate di nuovo. E poi, a un certo punto, qualcuno ti chiede: *«Ma come funziona esattamente questo tuo sistema?»* — e ti rendi conto che sai rispondere, ma non sai dove guardare per mostrarglielo.

Ecco come nasce un manuale. Non da una decisione, ma da una lacuna.

---

## Il problema che non sapevo di avere

Ho costruito quattro siti negli ultimi anni. Non quattro esperimenti — quattro cose vere, in produzione, usate da persone reali. **Runtime Radio**, una radio web con streaming, podcast, redazione di notizie. **DISINTELLIGENZA** e il suo fork gemello **FDCA**, due festival musicali con iscrizioni, votazioni e un sistema di gestione concorrenti. E poi il mio sito personale, **SimonePizziWebSite**, che è un po' un portfolio e un po' un blog e un po' un diario tecnico.

Quattro siti diversi. Quattro scopi diversi. E, ho scoperto a un certo punto, *una stessa architettura sottostante* — affinata, corretta, migliorata iterazione dopo iterazione, fino a diventare qualcosa che funziona davvero bene.

Il problema era che esisteva solo nella mia testa.

E nella testa non è documentazione. Nella testa è rumore.

---

## La scelta che cambia tutto: il frontend bello, il backend onesto

Devo fare una confessione che potrebbe disturbare qualcuno: **non uso Node.js lato server**. Non uso framework PHP. Non ho container, non ho pipeline CI/CD, non ho un servizio cloud che mi costa una cifra mensile. I miei siti girano su hosting condivisi da pochi euro al mese.

E sono veloci. Sono sicuri. Sono mantenibili.

Come è possibile? La risposta è una scelta architettonica precisa, che ho chiamato — e che nel manuale chiamo — *il piano della separazione*.

> *Da un lato, il frontend ha raggiunto una maturità estetica e funzionale straordinaria: React, TypeScript, Tailwind. Dall'altro, questa rivoluzione ha portato con sé una complessità infrastrutturale sproporzionata rispetto ai bisogni reali della maggioranza dei siti.*

Il frontend — l'interfaccia, le animazioni, l'esperienza visiva — lo faccio con React 19, TypeScript, Tailwind. È compilato, ottimizzato, servito come bundle statico. È bellissimo da scrivere e performante da usare.

Il backend — i dati, la logica, la sicurezza — lo faccio con PHP nativo e SQLite (o MySQL quando necessario). Nessun framework, nessun ORM, nessuna dipendenza esterna. Solo PHP, PDO, e un database che non richiede configurazione server.

I due parlano attraverso API REST. Il frontend non sa niente del database. Il backend non sa niente di React. La separazione è la fonte di tutta la semplicità.

Ho chiamato questa architettura **The Thin Stack**. Stack sottile. Perché usa solo quello che serve, e niente di più.

---

## Quattro siti, quattro cicatrici

Sarebbe disonesto presentare questo manuale come il risultato di una pianificazione brillante. Non lo è. È il risultato di *errori*, soprattutto.

### La notte in cui il database ha smesso di rispondere

Febbraio 2026. Runtime Radio aveva traffico crescente da mesi. Il database SQLite teneva, teneva, teneva — e poi una notte ha ceduto tutto insieme. Il problema era tecnico: avevo attivato il **WAL mode** di SQLite, teoricamente più performante. In pratica, su un hosting condiviso Apache, il file di lock WAL rimaneva appeso e corrompeva le letture.

In meno di ventiquattr'ore abbiamo migrato l'intero database a MySQL. Senza perdere un dato.

Quella migrazione è documentata parola per parola nel manuale. Non come ricetta teorica — come resoconto di una notte reale, con i problemi reali, le soluzioni reali, e i tre script PHP che hanno reso possibile un trasloco dati senza downtime esteso.

La lezione: *SQLite è la scelta giusta finché il traffico è gestibile. Poi esiste un percorso preciso per uscirne.* Il manuale documenta entrambe le cose.

### I bot che simulavano gli amici

Tre giorni dopo la migrazione, mentre l'infrastruttura era ancora in fase di stabilizzazione, è arrivato l'attacco.

Non era un attacco spettacolare. Era elegante, quasi chirurgico. Migliaia di bot ostili **simulavano i crawler di Telegram, Facebook e X** — quei piccoli programmi che i social media mandano quando qualcuno condivide un link, per generare l'anteprima. Runtime Radio, come tutti i siti costruiti con questa architettura, intercettava quelle richieste per iniettare i meta tag corretti nell'HTML. Una funzionalità utile. Che si è trasformata in un'arma.

Ogni richiesta dei bot forzava una query al database. Mille richieste al secondo. Il database, appena migrato, ha ceduto.

> *I grafici del traffico hanno iniziato a disegnare picchi anomali, simili a pareti verticali.*

La risposta è stata in tre fasi: spegnimento di emergenza con streaming audio preservato (il servizio core non si interrompe mai, nemmeno durante un attacco), poi una cache precompilata che serve i bot da file statici senza interrogare il database, poi un sistema ibrido che distingue esplicitamente tra richieste di bot e richieste umane.

Tutto questo è nel manuale. Con il codice. Con la storia. Con i nomi delle persone che hanno aiutato a ricostruire.

*Carlo Santagostino, Walter Sbano, Peppe Pugliese, Valerio Galano* — la comunità tecnica che era lì quando serviva. La resilienza non è solo nel codice.

---

## Perché un manuale gratuito

Questa è la domanda che mi sono fatto anch'io, onestamente.

Il tempo impiegato per scrivere questo manuale è stato significativo. Non un weekend — settimane di lavoro, di revisione, di scelta di cosa includere e cosa lasciare fuori. Potevo venderlo. Potevo metterlo dietro una newsletter a pagamento. L'ho fatto gratis perché credo in una cosa specifica: **la conoscenza tecnica si moltiplica quando è libera, e si atrofizza quando è chiusa**.

Ogni pattern che ho documentato è stato estratto da codice che gira in produzione da qualcuno che stava cercando di fare una cosa bella con quello che aveva. La maggior parte di quello che so l'ho imparato da blog, da documentazioni open source, da stackoverflow, da gente che ha deciso che valeva la pena scrivere. È giusto restituire.

E poi c'è un secondo motivo, più pratico: **documentare obbliga a capire davvero**. Ci sono pattern che usavo da anni e che ho capito veramente solo quando ho dovuto spiegarli. Scrivere il manuale è stato, in parte, scrivere per me stesso. Per il me futuro che si troverà a riprendere un progetto dopo sei mesi e avrà bisogno di ricordarsi come funziona.

---

## Cosa trovi dentro

Il manuale si chiama ufficialmente *React + PHP: The Thin Stack — Il protocollo miniCMS per Web App moderne*. Prima edizione. Marzo 2026.

È organizzato in **cinque parti e un allegato**, per un totale di diciotto capitoli.

**Parte I — La Visione** è un solo capitolo, il Manifesto. È il perché. La tensione irrisolta tra la potenza di React e la semplicità di PHP, e come questa architettura prova a risolverla senza tradire nessuno dei due lati.

**Parte II — L'Architettura** è dove si decidono le fondamenta: struttura delle cartelle, strategia database (SQLite o MySQL e quando passare dall'uno all'altro), scelta dello stack frontend e perché ogni libreria che aggiungi ha un costo che devi essere disposto a pagare.

**Parte III — I Componenti** è la cucina. Come si scrive un endpoint PHP che non è mai vulnerabile. Come si costruisce il bridge tra frontend e backend in TypeScript. Come si gestiscono media, upload, editor di contenuto ricco.

**Parte IV — Il Flusso Operativo** è dove i contenuti prendono vita: il ciclo di vita editoriale (bozza, programmato, pubblicato), l'autenticazione e la sicurezza, il SEO per i motori di ricerca e i social, il feed RSS, la newsletter. Con il codice dell'incidente DDoS documentato per intero.

**Parte V — I Casi Reali** è forse la parte più onesta. La migrazione vera di Runtime Radio da SQLite a MySQL, con i tre script che l'hanno resa possibile. Il modulo portfolio di SimonePizziWebSite con la logica di riordinamento drag-and-drop. L'intero sistema festival di DISINTELLIGENZA e FDCA, dalle iscrizioni alle votazioni anti-frode alla dashboard di reportistica.

E infine una **Boilerplate Checklist** — una lista pratica, fase per fase, di tutto quello che serve per avviare un nuovo progetto da zero.

Ogni capitolo è autonomo. Si può leggere dall'inizio alla fine come un libro, o si può usare come reference andando direttamente al capitolo che serve. I cross-reference tra capitoli sono espliciti: quando un pattern richiede di conoscere qualcosa documentato altrove, c'è un rimando diretto.

---

## A chi è rivolto, onestamente

Non a tutti.

Non è per chi vuole un sito in un pomeriggio. Per quello esistono WordPress, Squarespace, Webflow — tutti ottimi strumenti per quello che fanno.

Non è per chi gestisce architetture enterprise con milioni di utenti simultanei. Per quello esistono soluzioni molto più sofisticate, e giustamente.

È per una fascia specifica di persone che mi sembra spesso lasciata sola dall'ecosistema tecnico:

Il **developer che conosce React** ma è stufo di dover imparare un backend intero — Node, Express, Prisma, Docker — ogni volta che vuole aggiungere un'API semplice. Che sa già come funziona il frontend e vuole un backend che funzioni senza sorprese.

Il **freelance** che deve consegnare siti belli, veloci, sicuri e mantenibili a clienti che non hanno budget per infrastrutture cloud. Che sa che il cliente tra sei mesi chiamerà con una modifica urgente, e che quel momento deve essere gestibile.

L'**autore, il musicista, il festival, la radio** che vuole una presenza digitale propria, controllata, indipendente dai capricci delle piattaforme. Che vuole sapere esattamente dove vivono i suoi dati e che succede se smette di pagare un abbonamento.

E forse, soprattutto, **chiunque creda che il web possa ancora essere un posto fatto da persone, per persone** — senza intermediari, senza vendor lock-in, senza la sensazione costante di costruire su sabbia.

---

## Una nota sul titolo

*The Thin Stack* non è stata la prima proposta.

Ho considerato titoli più descrittivi, più tecnici, più espliciti. Nessuno funzionava davvero. O erano troppo generici, o erano troppo criptici, o erano semplicemente brutti.

*The Thin Stack* è rimasto perché dice esattamente quello che è. Uno stack sottile. Non minimale nel senso di impoverito — minimale nel senso di *Saint-Exupéry*: **la perfezione si raggiunge non quando non c'è più niente da aggiungere, ma quando non c'è più niente da togliere**.

Questo è l'obiettivo dichiarato di ogni scelta documentata nel manuale. Non la soluzione più elegante in astratto, ma la soluzione più semplice che funziona davvero in produzione.

---

## Dove trovarlo

Il manuale è disponibile gratuitamente nel repository GitHub dedicato. I file sono in Markdown — leggibili direttamente su GitHub, capitolo per capitolo — e viene distribuito anche come **PDF compilato**, formattato come un libro tecnico vero.

Niente paywall, niente email richiesta, niente iscrizione obbligatoria.

Se lo usi, se ci trovi un errore, se hai una domanda su qualcosa che non è chiaro — sai dove trovarmi. Questo sito, i soliti canali. Sono curioso di sapere cosa ci fate.

E se lo trovi utile, *condividilo*. Non per me — per il prossimo developer che è sveglio alle tre di mattina con un crash in produzione e ha bisogno di capire cosa sta succedendo.

Per quello che ero io, qualche anno fa.

---

*— Simone Pizzi, marzo 2026*

*P.S. — Il database di Runtime Radio, quello che ha ceduto a febbraio, adesso gira su MySQL ed è stabile come una roccia. La radio non si è mai fermata. Lo streaming continuava anche durante l'attacco. Alcune cose, quando le progetti bene, resistono davvero.*
