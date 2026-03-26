# CAPITOLO 17: Festival Logic - Votazioni e Protezione Anti-Frode (v1.0)

Il Modello Universale implementa un sistema di votazione pubblica robusto, progettato per prevenire manipolazioni e garantire l'equità del concorso.

## 1. La Sessione di Voto
L'utente può esprimere una o più preferenze (es. da 1 a 3) in una singola chiamata API.
- **Validazione Server-Side**: Il backend verifica che i partecipanti votati siano effettivamente approvati e nel round attivo (`in_current_round = 1`).
- **Transazione Atomica**: L'inserimento del voto e l'aggiornamento del contatore (`vote_count`) nel partecipante devono avvenire all'interno di una transazione SQL (`beginTransaction`).

## 2. Meccanismi di Protezione (Anti-Abuso)
Per impedire voti multipli dallo stesso utente o da bot:
- **Client-Side Protection**: Impostazione di un cookie (`dis_voted`) con scadenza a 30 giorni dopo il voto.
- **Server-Side Protection (IP Tracking)**: Il backend registra l'indirizzo IP del votante e impedisce nuovi voti dallo stesso IP per le successive 24 ore.
- **User Agent Check**: Ogni voto memorizza lo `User Agent` per permettere l'analisi post-voto in caso di comportamenti sospetti.

## 3. Gestione dei Round (Il "Palcoscenico" del Voto)
I partecipanti sono visibili nella pagina pubblica di voto solo se soddisfano due condizioni:
1. `status = 'approved'`
2. `in_current_round = 1`

Questo permette all'admin di attivare/disattivare interi gruppi di partecipanti (eliminatorie, semifinali, finale) semplicemente cambiando un interruttore booleano nella dashboard.

## 4. Master Switch di Votazione
La possibilità di votare è regolata da un interruttore globale (`voting_active`) nella tabella `settings`. Se disattivato, il backend deve restituire un errore `403 Forbidden` a chiunque tenti di inviare un voto.

---
*Prossimo Capitolo: Festival Logic - Dashboard Admin, Settings e Reporting.*
