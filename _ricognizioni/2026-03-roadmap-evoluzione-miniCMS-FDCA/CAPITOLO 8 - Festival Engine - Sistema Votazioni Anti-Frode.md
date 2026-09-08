# CAPITOLO 8: Festival Engine - Sistema Votazioni Anti-Frode

FDCA deve garantire l'equità del voto tramite protezioni incrociate.

## 1. Il Backend del Voto (votes.php)
Copiare `votes.php` da `DISINTELLIGENZA`. Questo file implementa la protezione:
- **IP Protection**: Un solo voto ogni 24 ore per IP.
- **Cookie Protection**: Scadenza a 30 giorni dal voto.
- **Validazione Round**: Voti validi solo per i partecipanti del round attivo.

## 2. Il Frontend del Voto (Vota.tsx)
Implementare `Vota.tsx` nel frontend:
- Caricamento dei soli partecipanti approvati e in gara (`status=approved&round=active`).
- Logica di selezione **Multi-Preferenza**: l'utente può selezionare da 1 a 3 preferenze prima di inviare il voto.
- Messaggio di conferma "Hai già votato" se il cookie è presente.

## 3. Gestione Round (Admin)
FDCA deve poter cambiare il "palinsesto" di voto. In `Registrations.tsx` (admin), aggiungere la possibilità di impostare `in_current_round` tramite un interruttore (toggle).

---
*Obiettivo: Permettere al pubblico di votare i talenti preferiti in modo sicuro e controllato.*
