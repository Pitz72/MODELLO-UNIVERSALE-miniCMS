# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA unità. Questa volta è una card SINGOLA ad alto
> valore: DIS-C10, il CUORE del sito-festival DISINTELLIGENZA.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.

METODO (ROADMAP §0.1): si accorpano SOLO coppie di cluster già accoppiati. C10 (Festival Logic) è
il cuore del sito e va fatta DA SOLA (alto valore e corposa). Restano poi DIS-C9 (Newsletter/contact,
leggera) e DIS-C12 (Admin), più FDCA-DIFF. Questa sessione = card SINGOLA: DIS-C10.

Stato: i PRIMI DUE siti (flagship) COMPLETI; il 3° in corso.
- SimonePizziWebSite: COMPLETO (11 card). SitoRuntime: COMPLETO (10 card).
- DISINTELLIGENZA (festival, SQLite VIVO): DIS-C1, DIS-C2, DIS-C4, DIS-C5 fatte. 25/~30 card totali.

CONTESTO da card già fatte (leggi DIS-C2 e DIS-C4 prima di iniziare): il festival ha già lasciato
molti fili aperti verso C10. DIS-C2 ha mappato SOLO l'aspetto sicurezza/anti-frode del voto e della
registrazione; C10 deve mappare la LOGICA festival completa. Cosa NON ripetere (già in DIS-C2): la
catena anti-doppio-voto (cookie+IP/24h), il backup pre-reset, i gate. C10 li richiama come puntatori.

Unità di QUESTA sessione: DIS-C10 (Festival Logic) del sito DISINTELLIGENZA
(C:\Users\Utente\Documents\GitHub\SITI-WEB\DISINTELLIGENZA). UNA card.

Ambito DIS-C10 (Festival Logic):
- public/api/participants.php — il CICLO DI VITA del partecipante: submit pubblica (pending) →
  update_status (approved/rejected, con email C9) → update_round (in_current_round). Mappare gli stati
  (pending/approved/rejected/finalist da init_db.php:55) e le transizioni. (La sicurezza della submit
  è DIS-C2; qui la LOGICA di concorso.)
- public/api/votes.php — la MECCANICA del voto come logica festival: 1-3 preferenze, in_current_round,
  vote_count denormalizzato, session_id di raggruppamento. (anti-frode = DIS-C2; qui conteggio/round.)
- public/api/settings.php — i MASTER SWITCH del festival: voting_active, registration_active,
  voting_period/registration_period, maintenance_mode. Come si leggono/scrivono, chi li tocca.
- public/api/stats.php — classifiche/aggregazioni del festival (conteggi voti, partecipanti per stato,
  vincitori?). Verificare se è pubblico o gated, e cosa calcola.
- public/api/reset_votes.php + reset_system.php — dal punto di vista del FLUSSO festival (reset turno
  vs reset totale, cosa preserva/cancella). La sicurezza/backup è DIS-C2; qui il significato nel ciclo.
- Schema: participants (vote_count, in_current_round, status), votes, settings — come si tengono
  coerenti (es. vote_count denormalizzato vs COUNT su votes).
- NON sconfinare: auth/anti-frode/CSRF=C2 (fatto), upload audio=C5 (fatto), news=C4 (fatto),
  email/newsletter=C9, admin dashboard/UI=C12, bootstrap/DB=C1.

Fai così:
1. Ispeziona in modo microscopico i file (cita sempre percorso/file:linea).
2. Compila UNA card seguendo _TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/DISINTELLIGENZA/DIS-C10-festival-logic.md
3. §6: confronto — DIS è l'UNICO sito con festival logic completa (SPW/SR non ce l'hanno; FDCA è un
   fork). Quindi il §6 è soprattutto INTERNO (come il festival modella stati/round/voto) + un cenno a
   come questo "dominio votazioni" non esista negli altri due siti. Anticipa il diff FDCA.
4. Chiudi i fili lasciati aperti da DIS-C2/C4/C5 verso C10 (round, vote_count, stats, ruoli editor).
5. Lascia puntatori per C9 (email approvazione) e C12 (UI admin del festival).

Criterio di STOP: card in stato COMPLETATO.

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (DIS-C10 → ✅)
- aggiungi UNA riga a _cantiere-terza-edizione/LOG.md (più recente IN BASSO)
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta DIS-C10, aggiorna stato globale)
- git add/commit/push (un commit) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: verosimilmente DIS-C9
  (Newsletter & Email + contact) da sola, poi DIS-C12 (Admin), infine FDCA-DIFF.
