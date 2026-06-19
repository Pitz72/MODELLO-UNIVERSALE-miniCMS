# CAPITOLO 19: Festival Logic - Dashboard Admin, Settings e Reporting

Questa dashboard è il quadro di comando del concorso, ma non è una console a sé: è la **specializzazione festival** dell'area admin generale del Capitolo 14. La struttura che la regge (la guardia che protegge l'area, il layout, il backup fuori docroot) appartiene a quel capitolo; qui restano le cose proprie del festival, gli interruttori delle fasi, i KPI del concorso, l'approvazione, la classifica e il report. Leggere questo capitolo come l'istanza-festival di un pattern generale, e non come un pannello isolato, evita di duplicare ciò che il Capitolo 14 ha già spiegato.

E come gli altri due capitoli del modulo, anche questo allinea il testo idealizzato al codice reale, dove due funzioni promesse non sono ciò che sembrano: il report finale e i finalisti.

## 1. I Master Switch

La tabella `settings`, una coppia chiave/valore, è il quadro elettrico del festival: `registration_active` apre o chiude il form di iscrizione, `voting_active` la sessione di voto, `current_round` indica la fase. Un interruttore qui apre o chiude un'intera fase per tutti.

La tabella è leggibile pubblicamente (il frontend la consulta per sapere cosa mostrare) e scrivibile solo dall'admin. Un dettaglio già incontrato al Capitolo 18 torna qui: la lettura dei flag accetta sia `'1'` sia `'true'`, perché la scrittura non ha mai fissato una convenzione unica. È una toppa difensiva che compensa un'incoerenza a monte, non un design.

## 2. I KPI del Concorso

L'area mostra gli indicatori in tempo reale: i partecipanti suddivisi per stato (pending, approved), il volume totale dei voti, una stima dei votanti unici. Su quest'ultima serve un'avvertenza, perché il modulo la calcola «per IP e cookie». Il cookie, però, è una difesa cosmetica (Capitolo 18): si cancella, quindi conta poco come misura di unicità. Il segnale affidabile è uno solo, l'IP nella finestra delle ventiquattr'ore; il «votante unico» va letto come «IP unico», con tutte le imprecisioni del caso (la rete aziendale che collassa molti votanti su un indirizzo solo).

## 3. Approvazione e Classifica

L'admin vede i partecipanti in una tabella, ascolta la traccia e decide l'esito; l'approvazione è l'unica azione che fa partire l'email di conferma ufficiale. Quella stessa azione, però, è concessa a chiunque sia loggato, non solo agli amministratori: il gate role-blind del Capitolo 17 vale anche da qui.

La classifica si ordina per `vote_count`, ed è veloce proprio perché legge un contatore già pronto invece di contare i voti. Ne paga però la fragilità: senza una riconciliazione periodica, quel contatore può divergere in silenzio dai voti reali (il box del Capitolo 18 spiega perché, e cosa aggiungere). C'è poi una promessa del testo che il codice non mantiene.

> [!WARNING]
> **Lo stato `finalist` racconta un piano mai realizzato**
> Il modulo idealizzato parla di «selezionare i finalisti da spostare nel round successivo», come se esistesse uno stato `finalist` che l'admin assegna. Nell'enum dei partecipanti quello stato c'è, ma **nessuna riga di codice lo imposta mai**: le fasi del concorso si gestiscono accendendo il flag booleano `in_current_round` su gruppi di partecipanti, non promuovendoli a uno stato. Quel `finalist` è uno schema che documenta un'intenzione abbandonata, non una funzione. È utile saperlo riconoscere: uno stato che esiste nel database ma che nessuno scrive è un fossile, e descriverlo come attivo confonde il lettore su come gira davvero il concorso.

## 4. Il Reporting che non è mai stato Acceso

Alla chiusura del voto, dice il modulo idealizzato, il backend invia allo staff un'email di report finale: voti totali, Top 20 dei più votati, qualche statistica geografica sugli IP. La funzione esiste, si chiama `sendVotingReport`, ed è scritta per intero. C'è solo un problema.

> [!WARNING]
> **Una feature costruita e disabilitata: «Phase 2»**
> `sendVotingReport` è interamente implementata ma **disabilitata nel codice**, commentata con l'etichetta «Phase 2». È vero che il backend *contiene* il report; è falso che lo *invii*. È il gemello dello stato `finalist` del paragrafo precedente: codice presente, funzione dormiente. Presentare una capacità commentata come operante è uno dei modi più facili in cui una documentazione si disallinea dal software: la regola, per chi scrive documentazione tecnica, è descrivere cosa il codice *fa*, non cosa è *pronto a fare se qualcuno lo riattiva*. Finché «Phase 2» resta commentata, il report finale è una promessa, non una funzione.

## In sintesi

Il pannello del festival è coerente con la filosofia del modulo, gli interruttori semplici e i numeri essenziali, ma porta le crepe del «fatto a interruttori»: una stima di unicità che si fida di un cookie cosmetico, una classifica che può derivare senza accorgersene, uno stato `finalist` mai usato e un report mai acceso. Sono i punti dove il concorso reale diverge dalla sua versione raccontata, e conoscerli è ciò che distingue chi sa governarlo da chi crede di farlo. La struttura che tiene insieme questo pannello (guardia, layout, backup) resta al Capitolo 14, di cui questa è la versione festival.

> [!IMPORTANT]
> **Il Canone**
> - È l'istanza-festival dell'area admin (Capitolo 14): struttura, guardia e backup vivono lì, qui restano gli interruttori e i KPI del concorso.
> - I master switch vanno letti in modo coerente con come sono scritti (niente `'1'` contro `'true'`).
> - Mostra KPI onesti (votanti unici per IP, consapevoli del drift di `vote_count`, Capitolo 18).
> - Non spacciare per attive le feature costruite ma disabilitate, e togli gli stati vestigiali (uno stato `finalist` mai impostato).

---
*Prossimo Capitolo: Social Interactions & Reactions. L'ultima superficie del CMS, dove a scrivere nel database è il pubblico anonimo.*
