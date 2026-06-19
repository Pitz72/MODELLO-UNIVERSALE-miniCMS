# APPENDICE B: Ciclo di vita di un fork

Il Modello descrive come si costruisce un sito thin stack. Non dice cosa succede quando lo si **forka**, eppure è un evento reale nella vita di questi progetti, e ne abbiamo un esempio mappato dall'interno: FDCA, il «Festival della Canzone Artificiale», nasce come fork di DISINTELLIGENZA, il «Festival della Disintelligenza Naturale». Stesso autore, stesso motore, tema nuovo: dalla comicità dell'errore umano alla musica generativa. Questa appendice racconta quella fase, perché ha rischi tutti suoi, e il primo è il più silenzioso di tutti.

Il Capitolo 2 ha già introdotto il pattern: due festival con la stessa base funzionale partono da una copia di ciò che già funziona. Il vantaggio è l'indipendenza; il rischio è il suo rovescio esatto. Qui lo guardiamo da vicino.

---

## 1. Il backend si congela, il frontend riparte

La prima cosa che si nota di FDCA è dove è andata l'energia del fork. La cartella `public/api/` è copiata da DISINTELLIGENZA **byte per byte**: stessi 28 file, stessa logica di autenticazione, voto, upload, newsletter, festival, zero differenze di contenuto. Tutto il lavoro nuovo è sul *guscio* pubblico: pagine vetrina riscritte (Home, Filosofia, Manifesto, Edizioni Passate, Contatti), un branding diverso, un cursore animato. È il pattern naturale di un re-skin: si cambia ciò che si vede, non ciò che funziona.

La conseguenza è che la logica di server è ereditata intatta. E «intatta» include ogni cosa, anche le falle.

---

## 2. Il fork eredita il debito: copiare un backend insicuro lo moltiplica

Questo è il punto centrale dell'appendice. Nessuna delle vulnerabilità di sicurezza di DISINTELLIGENZA è stata risolta nel fork, perché il backend è copiato riga per riga. Quello che era un problema in un sito diventa lo stesso identico problema in due.

| Vulnerabilità ereditata | Dove è descritta | Stato in FDCA |
| :--- | :--- | :--- |
| Catena **RCE da upload pubblico** (upload no-auth, MIME dal client, nome conservato, niente PHP-off) | CAP 7 | presente, immutata |
| **Auth grado-zero** (niente CSRF, niente rate-limit, niente protezione da fixation) | CAP 10 | presente |
| **Newsletter senza double opt-in né token** + header injection | CAP 13 | presente |
| **Reset distruttivi senza token CSRF** | CAP 10, CAP 14 | presente |
| **`vote_count` denormalizzato** (drift della classifica) | CAP 18 | presente |
| **Render senza DOMPurify** (stored-XSS) | CAP 8 | presente |

C'è un dettaglio che rende la storia ancora più istruttiva. Sul repository di DISINTELLIGENZA esiste un intervento aperto per chiudere la catena RCE dell'upload (CAP 7). Quel fix vive su DISINTELLIGENZA, e **non tocca FDCA**: il fork ha la sua copia del file vulnerabile, scollegata dall'originale. Il giorno in cui il backend di FDCA andrà online, la RCE sarà replicata, identica, su un secondo dominio, mentre tutti credono di averla risolta.

> [!WARNING]
> **Il fix non segue il fork**
> Quando si forka copiando il backend, si ereditano le feature e si ereditano le falle, nello stesso gesto. Da quel momento i due rami sono indipendenti: ogni correzione di sicurezza fatta su uno **non** arriva all'altro per magia, va riapplicata a mano. È facile dimenticarlo, perché il fork sembra «un altro progetto», con un altro nome e un'altra versione. Ma sotto è lo stesso codice, e una falla chiusa in un ramo resta spalancata nell'altro finché qualcuno non la chiude di nuovo, di proposito. Prima di forkare un backend, conviene avere un elenco delle sue vulnerabilità note proprio per non perderlo di vista dopo la copia.

---

## 3. Il guscio scollegato

C'è una seconda sorpresa in FDCA: il frontend nuovo **non parla con il backend ereditato**. Non c'è un `src/api.ts`, non c'è una sola chiamata `fetch` verso `/api/`. Le pagine vetrina sono marketing puro, non connesso al CMS che gira dietro. FDCA, allo stato, è un sito-vetrina con dietro un CMS pieno e funzionante ma irraggiungibile dalla sua stessa applicazione.

Non è un errore: è una fase. Prima la pelle, poi (forse) il ricablaggio. È lo scollamento tipico di un restyle in corso d'opera, e di per sé non fa danni, perché un backend che nessuno chiama non espone nulla. Il rischio è latente e differito: il giorno in cui il frontend verrà connesso, erediterà *anche operativamente* i comportamenti, e i bug, del backend di DISINTELLIGENZA. Lo scollamento di oggi è anche la ragione per cui le falle del §2 non sono ancora sfruttabili end-to-end, e per cui è facile dimenticarsene.

---

## 4. La versione che riparte da zero su codice che non riparte

FDCA si presenta come **v0.0.1**. Il `package.json` dice 0.0.1, il `metadata.json` parla di «Remix», il README è quello generato da Google AI Studio. Tutto comunica un prodotto nuovo, appena nato. Sotto, però, gira un backend a v0.5.x con tutto il suo debito accumulato.

> [!WARNING]
> **La versione racconta una nascita, il codice racconta un'eredità**
> La discontinuità di versione *nasconde* la continuità del debito. È il rovescio del problema delle stringhe di versione divergenti che si vede in DISINTELLIGENZA (sidebar, init e package indicano tre numeri diversi): lì troppe versioni per un solo codice, qui una versione-zero per un codice tutt'altro che zero. In entrambi i casi il numero di versione mente sullo stato reale del software. Quando vedi un `0.0.1`, non dare per scontato che sotto ci sia poco: guarda il codice, non l'etichetta.

---

## 5. Il fork che si scrive la roadmap da solo

FDCA include una cartella `ROADMAP-EVOLUZIONE-miniCMS` con nove capitoli, generati con assistenza AI, che pianificano di ricostruire il miniCMS in modo pulito. I titoli di quei capitoli **ricalcano i cluster** di questa stessa mappatura: Backend, API PHP, Frontend Bridge, Admin & Protected Routes, Festival Engine. È un artefatto prezioso, perché conferma dall'interno la struttura che questo manuale ricostruisce dall'esterno: la spina dorsale del thin stack è riconoscibile anche a chi ci lavora dentro, al punto da volerla riscrivere ordinata. Un progetto che documenta l'intenzione di evolvere il proprio motore è la prova che il pattern esiste ed è leggibile.

---

## 6. Un motore, due festival

C'è anche un lato luminoso del forking, e FDCA lo dimostra. Il modello festival (iscrizione, selezione, voto a turni, master switch di registrazione e voto, classifica derivata dal `vote_count`) è **lo stesso** nei due siti: cambia solo il tema, dall'errore umano alla musica generativa. È la prova positiva che il modulo concorso descritto ai Capitoli 17 e 18 è un componente davvero riusabile: lo stesso engine regge due festival diversi con un semplice re-skin.

Il forking, insomma, non è un male in sé. Riusare un dominio che funziona cambiando la pelle è efficiente e legittimo. Diventa un problema solo quando il re-skin si dimentica del motore: quando si copia il backend e si trascura che dentro quella copia c'erano anche le falle, e che da quel momento è responsabilità del fork tenerle chiuse.

---

## In sintesi

Forkare un progetto thin stack è una fase reale e comune, e ha una sua fisiologia: il backend si congela, il frontend riparte, la versione si azzera, il tema cambia. Il rischio specifico è uno solo, ma è serio: l'eredità silenziosa del debito. Un fork che copia il backend verbatim si porta dietro ogni vulnerabilità, immutata, mentre la versione-zero e il nome nuovo raccontano un prodotto pulito. Il fix non segue il fork: va riapplicato a mano, su un ramo che ormai vive di vita propria. La regola, se si forka, è tenere insieme due liste: quella delle feature da riusare e quella delle falle da non ereditare. La prima è il motivo per cui si forka; la seconda è la ragione per cui un fork va trattato come un progetto da mettere in sicurezza da capo, non come una copia già a posto.
