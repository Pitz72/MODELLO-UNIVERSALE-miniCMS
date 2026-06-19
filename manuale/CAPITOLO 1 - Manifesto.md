# CAPITOLO 1: Manifesto

> *A Valerio Galano, perché lui è come Neo, vede mondi nel codice e mi ha insegnato a ragionare in un modo diverso. Chissà se un po' anche io gli ho insegnato qualcosa.*
>
> *A Giuseppe Pugliese che, anche se vede il mondo in un modo tutto suo, ritiene sia un orgoglio essere uno sviluppatore web e persevera nella sua arte con passione.*

---

## Perché Esiste Questo Protocollo

Esiste una tensione irrisolta al centro dello sviluppo web moderno.

Da un lato, il frontend ha raggiunto una maturità estetica e funzionale straordinaria: React, TypeScript, Tailwind. Animazioni fluide, componenti riutilizzabili, type safety, hot reload. L'esperienza di sviluppo è diventata un piacere, e il prodotto finale, quando fatto bene, è visivamente e funzionalmente superiore a qualsiasi soluzione del passato.

Dall'altro lato, questa rivoluzione ha portato con sé una complessità infrastrutturale sproporzionata rispetto ai bisogni reali della maggioranza dei siti. Node.js, database cloud, container, pipeline CI/CD, micro-servizi, CMS headless con piani in abbonamento. L'overhead tecnico e il costo operativo sono diventati la norma anche per siti che potrebbero girare perfettamente su un hosting da cinque euro al mese.

Questo protocollo nasce da una domanda precisa: **è possibile avere la potenza estetica e tecnica di React senza abbandonare la semplicità, il controllo e l'economicità di un backend PHP con SQLite?**

La risposta, costruita su mesi di lavoro reale su progetti reali, è sì.

---

## Il Principio Fondativo: La Separazione dei Piani

Il Modello Universale non è una tecnologia. È un'architettura mentale.

Separa con nettezza due piani che spesso vengono confusi:

**Il Piano della Presentazione** appartiene a React. È il luogo della forma, dell'interazione, dell'animazione, della tipografia, della palette colori. È dove vive il talento estetico, dove Tailwind traduce l'intenzione visiva in CSS preciso, dove framer-motion aggiunge peso e respiro ai movimenti. Questo piano è compilato, ottimizzato, servito come asset statico.

**Il Piano dei Dati** appartiene a PHP e SQLite (o MySQL quando necessario). È il luogo della persistenza, della logica di business, della sicurezza, del ciclo di vita dei contenuti. Non è «il backend» nel senso pesante del termine: nessun framework, nessun ORM, nessuna dipendenza esterna. Solo PHP nativo, PDO, e un database file-based che non richiede configurazione server.

Questi due piani comunicano attraverso un contratto preciso: le API REST. Il frontend non sa niente del database. Il backend non sa niente di React. La loro separazione è la fonte di tutta la scalabilità e la manutenibilità del sistema.

---

## La Scala, non l'Assenza

«Thin stack» non significa «backend assente». Significa un backend ridotto all'osso ma vero, e significa soprattutto una scala. Lo stesso scheletro (PHP nativo, un singleton PDO per richiesta, un file per endpoint, niente framework) si declina su gradini diversi a seconda di cosa serve. Al grado-zero c'è SQLite, un database che è un singolo file, senza un server da configurare né un segreto da custodire. Un gradino sopra c'è MySQL essenziale, quando i dati o il traffico lo richiedono. Più su ancora c'è MySQL ingegnerizzato, con connessioni rinforzate, prelude condivisi e scaffolding dedicato. Non sono tre architetture diverse: sono lo stesso modello a tre altezze.

Questo manuale è costruito su quattro siti reali che occupano punti diversi di quella scala, e li legge proprio così. Quando un capitolo mostra «tre modi di fare la stessa cosa», non sta elencando opzioni a caso: sta misurando quanto si può togliere, o aggiungere, allo stesso scheletro prima che cambi natura. La scala a tre gradini, dal grado-zero all'ingegnerizzato, è la chiave di lettura del libro intero.

---

## Cosa Non È Questo Protocollo

Non è un framework. Non impone strutture di codice rigide, non richiede dipendenze specifiche, non vincola le scelte stilistiche.

Non è un CMS tradizionale. Non c'è un'interfaccia visual builder, non ci sono temi preconfezionati, non c'è un marketplace di plugin. Ogni sito costruito con questo protocollo è unico, fatto a mano, su misura per il suo scopo.

Non è una soluzione enterprise. Non è progettato per gestire milioni di utenti simultanei, flussi di dati complessi o architetture distribuite. È progettato per siti che devono essere eccellenti, veloci, sicuri e mantenibili da un team piccolo, o anche da una persona sola.

Non è per chi vuole un sito in dieci minuti. È per chi vuole capire cosa sta costruendo.

---

## Quando NON Usare Questo Protocollo

Un manifesto onesto deve dire anche dove finisce. Il Thin Stack scambia la complessità dell'infrastruttura con la disciplina di chi lo scrive: toglie il framework e mette al suo posto la tua attenzione. Quando quel baratto non conviene, conviene un altro stack. Ecco i casi in cui sceglierei altro senza esitare.

**Quando il team è grande.** Le convenzioni qui non sono imposte da un framework, sono tenute insieme dalle persone. Con uno o due sviluppatori funziona; oltre i quattro o cinque, l'assenza di una struttura rigida diventa un costo, non una libertà, e un framework opinionato (Laravel, Next.js con le sue regole) ripaga la curva di apprendimento.

**Quando serve il tempo reale.** Chat dal vivo, notifiche push istantanee, presenza, collaborazione simultanea su uno stesso documento: sono carichi che vogliono WebSocket e processi persistenti, non il modello richiesta-risposta di PHP su hosting condiviso. Si possono forzare, ma è la strada in salita.

**Quando la scala è davvero alta.** Decine di migliaia di richieste al secondo, picchi imprevedibili, necessità di scalare orizzontalmente su più nodi: qui servono code, cache distribuite e database gestiti. Il Capitolo 3 mette dei numeri concreti sotto questa frase, così la soglia non resta un'opinione.

**Quando i dati sono complessi e molto relazionali.** Transazioni distribuite, reportistica analitica pesante, modelli con decine di entità interconnesse: a un certo punto un ORM e un RDBMS ingegnerizzato non sono overhead, sono lo strumento giusto.

**Quando la conformità è un requisito esplicito.** Audit formali, certificazioni, ambienti regolati che pretendono framework e librerie con supporto commerciale e una catena di responsabilità documentata: il fai-da-te disciplinato, qui, è un rischio che non vale la pena correre.

La regola che tiene insieme questi casi è semplice: il Thin Stack è eccellente finché la complessità del problema sta sotto la complessità che un framework imporrebbe. Quando la supera, il framework smette di essere un peso e diventa una rete. Riconoscere quel punto di sorpasso è parte della stessa onestà tecnica che attraversa il resto del libro.

---

## I Valori che Guidano Ogni Decisione

**Controllo totale.** Chi costruisce un sito con questo protocollo possiede ogni riga del suo stack. Nessun vendor lock-in, nessun aggiornamento forzato che rompe la produzione, nessuna dipendenza da un servizio esterno per la sopravvivenza del sito.

**Leggerezza come principio, non come compromesso.** SQLite non è la scelta «economica» rispetto a MySQL: è la scelta giusta per il 90% dei casi d'uso. La semplicità non è una limitazione da superare, è un obiettivo da raggiungere e difendere.

**La sicurezza come architettura, non come patch.** Le decisioni di sicurezza sono integrate nel design del sistema: database fuori dalla root pubblica, uno script di build che non lascia mai il database nel deploy, sessioni PHP con cookie HttpOnly, password mai in chiaro. Non sono misure aggiunte dopo, sono la struttura stessa.

**Più ingegnerizzato non vuol dire più sicuro.** È la lezione più scomoda che questi siti insegnano, e ritorna in quasi ogni capitolo. Il sito tecnicamente più ricco, con le connessioni più blindate e l'infrastruttura più curata, è spesso quello con i fondamentali più fragili: una password di default scritta nel codice, nessun backup automatico, un argine anti-abuso che manca proprio dove servirebbe. Aggiungere complessità non paga interessi di sicurezza da sola, e a volte distrae dalle due righe che contano davvero. Diffidare dell'equazione «più strati uguale più sicuro» è uno dei fili che tengono insieme questo manuale.

**La documentazione come parte del codice.** Un sistema che non si capisce è un sistema che non si può mantenere. Questo protocollo è documentato con la stessa cura con cui è costruito, perché la conoscenza deve rimanere accessibile anche quando il contesto cambia.

**L'esperienza reale come unico validatore.** Ogni pattern documentato in questo manuale è stato estratto da codice che gira in produzione. Le lezioni più importanti vengono da incidenti veri, non da scenari ipotetici: il crash notturno del WAL che ha costretto Runtime Radio a migrare d'urgenza su MySQL, l'ondata di bot che ne ha saturato l'entry-point. La teoria senza la cicatrice non insegna abbastanza.

---

## A Chi È Rivolto

A chiunque voglia costruire un sito web che sia una cosa viva: non un template, non un WordPress personalizzato, non un sito sputato fuori da un builder.

Al developer che conosce React e vuole un backend senza dover imparare un framework intero.

Al freelance che deve consegnare un sito veloce, mantenibile e sicuro a un cliente che non ha budget per infrastrutture cloud.

All'autore, al musicista, al festival, alla radio che vuole una presenza digitale propria, controllata, indipendente dai capricci delle piattaforme.

A chiunque creda che il web possa essere ancora un posto fatto da persone, per persone, senza intermediari.

---

## Due Voci: «Dal vivo» e «Il Canone»

Questo manuale fa una cosa che la maggior parte dei testi tecnici evita: mostra il codice reale com'è, non come dovrebbe essere. È la sua forza, ma può confondere, perché in una stessa pagina convivono due cose diverse, e vanno tenute distinte.

La prima voce è **«dal vivo»**: la fotografia di cosa fanno davvero i quattro siti. Qui ci sono le scelte buone e anche le cicatrici, gli anti-pattern, le falle lasciate aperte. Quando il testo racconta che un sito salva l'HTML grezzo senza sanitizzarlo, o espone uno script di migrazione, non lo sta raccomandando: lo sta documentando. È il corpo di ogni capitolo, ed è scritto senza sconti proprio perché la cicatrice insegna più della teoria.

La seconda voce è **«il Canone»**: la regola da seguire, distillata. Ogni capitolo si chiude con un riquadro intitolato **Il Canone**, che separa nettamente la prescrizione dalla fotografia. Lì trovi cosa fare in un progetto nuovo, ripulito dalle imperfezioni dei casi reali. Se hai dieci secondi e vuoi solo la norma, leggi quel riquadro; se vuoi capire *perché* la norma è quella, leggi il capitolo che lo precede.

> [!NOTE]
> **La regola di lettura, in una riga**
> Il corpo del capitolo dice cosa il codice *fa* («dal vivo»); il riquadro finale dice cosa tu *dovresti* fare («il Canone»). Quando i due divergono, ha sempre ragione il Canone: la divergenza è il punto, non un errore di stampa.

---

## Come Usare Questo Manuale

Il manuale è organizzato in capitoli tematici indipendenti. Non è necessario leggerlo dall'inizio alla fine: ogni capitolo è una reference autonoma.

Per iniziare un nuovo progetto da zero, la **BOILERPLATE-CHECKLIST** è il punto di partenza pratico.

Per migliorare un progetto esistente, i capitoli specifici (Database Strategy, Security & Auth, SEO Pre-rendering) offrono pattern applicabili in modo chirurgico.

Per imparare dalla storia, i capitoli con la voce esperienziale (il crash del WAL, l'attacco dei bot su Runtime Radio, la migrazione a MySQL) sono la lettura più onesta che questo manuale può offrire.

Il codice non mente. Le cicatrici nemmeno.

---

> [!IMPORTANT]
> **Il Canone**
> - Separa i due piani: React compilato per la presentazione, PHP nativo con PDO per i dati, un contratto REST tra loro.
> - Scegli il gradino giusto della scala (SQLite grado-zero → MySQL essenziale → MySQL ingegnerizzato), mai più di quanto serve.
> - Tratta la sicurezza come architettura, non come patch, e diffida dell'equazione «più strati uguale più sicuro».
> - Documenta com'è il codice, non com'è bello: la cicatrice insegna più della teoria.
> - Usa il Thin Stack finché la complessità del problema resta sotto quella che un framework imporrebbe; superato quel punto, scegli il framework.

---

*«La perfezione si raggiunge non quando non c'è più niente da aggiungere, ma quando non c'è più niente da togliere.»*
*Antoine de Saint-Exupéry*

---
*Prossimo Capitolo: Architettura e Struttura Progetto. Dove le idee diventano cartelle.*
