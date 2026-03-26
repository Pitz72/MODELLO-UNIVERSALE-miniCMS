# CAPITOLO 16: Festival Logic - Iscrizioni e Workflow Approvazione (v1.0)

Il Modello Universale include un sistema gestionale per concorsi e festival, focalizzato sull'acquisizione di talenti e la gestione del loro ciclo di vita.

## 1. Il Workflow del Partecipante
Ogni iscrizione passa attraverso una pipeline di validazione obbligatoria gestita dal backend.

### 1.1 Stati di Iscrizione
- **pending**: Stato iniziale. Il partecipante ha caricato i dati ma non è visibile sul sito.
- **approved**: Il partecipante è validato, riceve l'email di conferma e viene inserito automaticamente nella newsletter.
- **rejected**: Il partecipante viene scartato e riceve una notifica di cortesia.

## 2. Automazione Email (Transaction Emails)
Il backend deve gestire l'invio di email transazionali in tempo reale per ogni cambio di stato, utilizzando template HTML coerenti con il branding del festival.
- **Email di Ricezione**: Conferma tecnica del caricamento file.
- **Email di Esito**: Comunicazione formale (positiva o negativa).

## 3. Gestione Asset Partecipanti
I file audio o video caricati dagli utenti devono essere isolati (`api/uploads/audio/participants/`) e rinominati in modo univoco. L'admin deve poterli pre-ascoltare nel Media Center prima di procedere all'approvazione.

## 4. Newsletter Sync Strategy
Il sistema garantisce la crescita del database marketing inserendo l'indirizzo email dell'utente nella tabella `newsletter_subscribers` **solo nel momento dell'approvazione**. Questo assicura che il database contenga solo utenti reali e validati.

---
*Prossimo Capitolo: Festival Logic - Votazioni e Protezione Anti-Frode.*
