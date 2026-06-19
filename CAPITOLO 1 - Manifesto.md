# CAPITOLO 1: Manifesto (Terza Edizione)

## Perché Esiste Questo Protocollo

Esiste una tensione irrisolta al centro dello sviluppo web moderno.

Da un lato, il frontend ha raggiunto una maturità estetica e funzionale straordinaria: React, TypeScript, Tailwind. Animazioni fluide, componenti riutilizzabili, type safety, hot reload. L'esperienza di sviluppo è diventata un piacere, e il prodotto finale, quando fatto bene, è visivamente e funzionalmente superiore a qualsiasi soluzione del passato.

Dall'altro lato, questa rivoluzione ha portato con sé una complessità infrastrutturale sproporzionata rispetto ai bisogni reali della maggioranza dei siti. Node.js, database cloud, container, pipeline CI/CD, micro-servizi, CMS headless con piani in abbonamento. L'overhead tecnico e il costo operativo sono diventati la norma anche per siti che potrebbero girare perfettamente su un hosting da cinque euro al mese.

Questo protocollo nasce da una domanda precisa: **è possibile avere la potenza estetica e tecnica di React senza abbandonare la semplicità, il controllo e l'economicità di un backend PHP con SQLite?**

La risposta, costruita su anni di lavoro reale su progetti reali, è sì.

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

## Come Usare Questo Manuale

Il manuale è organizzato in capitoli tematici indipendenti. Non è necessario leggerlo dall'inizio alla fine: ogni capitolo è una reference autonoma.

Per iniziare un nuovo progetto da zero, la **BOILERPLATE-CHECKLIST** è il punto di partenza pratico.

Per migliorare un progetto esistente, i capitoli specifici (Database Strategy, Security & Auth, SEO Pre-rendering) offrono pattern applicabili in modo chirurgico.

Per imparare dalla storia, i capitoli con la voce esperienziale (il crash del WAL, l'attacco dei bot su Runtime Radio, la migrazione a MySQL) sono la lettura più onesta che questo manuale può offrire.

Il codice non mente. Le cicatrici nemmeno.

---

*«La perfezione si raggiunge non quando non c'è più niente da aggiungere, ma quando non c'è più niente da togliere.»*
*Antoine de Saint-Exupéry*

---
*Prossimo Capitolo: Architettura e Struttura Progetto. Dove le idee diventano cartelle.*
