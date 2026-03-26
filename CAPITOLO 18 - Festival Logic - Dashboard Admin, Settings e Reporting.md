# CAPITOLO 18: Festival Logic - Dashboard Admin, Settings e Reporting (v1.0)

Il controllo del Festival avviene tramite una dashboard centralizzata che permette all'admin di attivare/disattivare intere fasi dell'evento e monitorare i risultati.

## 1. Master Switches (Global Settings)
La tabella `settings` agisce come il "quadro elettrico" del festival:
- **`registration_active`**: Abilita/Disabilita il form di iscrizione pubblico.
- **`voting_active`**: Apre/Chiude la sessione di voto pubblico.
- **`current_round`**: Identifica la fase attuale del concorso.

## 2. Dashboard Gestionale (KPIs)
L'area admin deve mostrare indicatori chiave di prestazione (KPI) in tempo reale:
- **Totale Partecipanti**: Suddivisi per stato (Pending, Approved).
- **Voti Totali**: Volume di voti ricevuti.
- **Votanti Unici**: Stima degli utenti unici basata sull'IP e sul Cookie.

## 3. Workflow di Approvazione e Ranking
- **Approvazione**: L'admin visualizza i partecipanti in una tabella dedicata, ascolta l'audio e decide l'esito. L'approvazione è l'unica azione che scatena l'invio dell'email di conferma ufficiale.
- **Classifica (Ranking)**: Il sistema deve fornire una classifica ordinata per `vote_count`, permettendo all'admin di selezionare i finalisti da spostare nel round successivo.

## 4. Reporting Automatico
Alla chiusura della sessione di voto (quando `voting_active` viene portato a `0`), il backend può innescare l'invio di un'email di report finale allo staff:
- Riepilogo voti totali.
- Top 20 dei partecipanti più votati.
- Statistiche di partecipazione geografica (facoltativo, basato sugli IP).

---
*Fine della Documentazione Avanzata del Modello Universale Festival miniCMS.*
