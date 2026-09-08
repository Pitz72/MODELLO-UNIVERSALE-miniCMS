# CAPITOLO 7: Festival Engine - Sistema Iscrizioni e Approvazione

FDCA, in quanto sito di festival, deve gestire l'acquisizione dei talenti con un workflow di approvazione sicuro.

## 1. Il Backend delle Iscrizioni (participants.php)
Copiare `participants.php` da `DISINTELLIGENZA`. Questo file gestisce:
- L'inserimento delle candidature nel database (stato `pending`).
- L'invio automatico delle email di conferma (Received, Approved, Rejected).
- L'inserimento automatico nella newsletter degli utenti approvati.

## 2. Il Frontend delle Iscrizioni (Iscriviti.tsx)
Aggiornare la pagina `Iscriviti.tsx`:
- Integrare la chiamata `api.submitParticipant(formData)`.
- Aggiungere il disclaimer obbligatorio sull'iscrizione alla newsletter (come richiesto).
- Gestire il caricamento dell'audio tramite `api.uploadFile(file, 'audio_participant')` prima di inviare il form.

## 3. Gestione Admin (Registrations.tsx)
Implementare la pagina `src/pages/admin/Registrations.tsx`:
- Tabella di riepilogo di tutti gli iscritti.
- Pulsanti di azione rapida: **APPROVA** / **RIFIUTA**.
- Player audio integrato per ascoltare il contributo direttamente dalla riga della tabella.

---
*Obiettivo: Automatizzare il processo di selezione dei partecipanti.*
