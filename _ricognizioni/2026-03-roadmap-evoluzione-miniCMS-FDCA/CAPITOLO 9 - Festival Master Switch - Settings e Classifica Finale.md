# CAPITOLO 9: Festival Master Switch - Settings e Classifica Finale

FDCA deve dare il controllo totale del festival all'amministratore tramite interruttori globali e monitoraggio dei voti.

## 1. Implementazione Settings (settings.php)
Copiare `settings.php` da `DISINTELLIGENZA`. Questo file gestisce:
- `registration_active`: Apre/Chiude il form Iscriviti.
- `voting_active`: Apre/Chiude il form Vota.
- `current_round`: La fase del festival.

## 2. Dashboard delle Votazioni (VotingManager.tsx)
Implementare `src/pages/admin/VotingManager.tsx` in FDCA:
- Visualizzazione della classifica in tempo reale (`ORDER BY vote_count DESC`).
- Contatore voti totali e votanti unici.
- Possibilità di resettare i voti (per un nuovo turno).

## 3. Reporting Finale
Al termine del festival, l'admin deve poter scaricare (o ricevere via email) il report definitivo della classifica per procedere alla premiazione dei talenti vincitori.

---
*Conclusione: FDCA è ora un sistema completo per la gestione del Festival, speculare a DISINTELLIGENZA.*
