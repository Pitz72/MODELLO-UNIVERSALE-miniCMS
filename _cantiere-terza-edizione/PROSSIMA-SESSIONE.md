# PROSSIMA SESSIONE — prompt pronto da incollare

> Aggiornato a fine di ogni sessione. Contiene UNA unità. Questa volta è una card SINGOLA leggera:
> DIS-C9 (Newsletter & Email + contact) di DISINTELLIGENZA.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
_cantiere-terza-edizione/ROADMAP.md e _cantiere-terza-edizione/LOG.md per il contesto.

METODO (ROADMAP §0.1): accorpamento solo di coppie già accoppiate. DIS-C9 è leggera ma non ha una
coppia naturale (C12 è admin, meglio da sola; C4/C5 già fatte) → si fa DA SOLA. Questa sessione =
card SINGOLA: DIS-C9.

Stato: i PRIMI DUE siti (flagship) COMPLETI; il 3° quasi completo.
- SimonePizziWebSite: COMPLETO (11). SitoRuntime: COMPLETO (10).
- DISINTELLIGENZA (festival, SQLite VIVO): DIS-C1, C2, C4, C5, C10 fatte. 26/~30 card totali.
- Restano: DIS-C9 (questa), DIS-C12 (admin), poi FDCA-DIFF (chiude la mappatura).

CONTESTO da card già fatte: l'email in DISINTELLIGENZA è già emersa più volte come PUNTATORE a C9 e va
ora mappata a fondo. DIS-C10 ha mostrato che `participants.php` invia email comico-dissacranti
(received/approved/rejected) via `mail()` nativa e fa `INSERT OR IGNORE INTO newsletter_subscribers`
all'approvazione (consenso implicito da chiarire). DIS-C1 ha mostrato che le tabelle
`newsletter_subscribers`/`contacts`/`newsletter_campaigns` sono create da `update_db_0_1_3.php`.

Unità di QUESTA sessione: DIS-C9 (Newsletter & Email + contact) del sito DISINTELLIGENZA
(C:\Users\Utente\Documents\GitHub\SITI-WEB\DISINTELLIGENZA). UNA card.

Ambito DIS-C9 (Newsletter & Email + contact):
- public/api/newsletter.php — iscrizione/disiscrizione newsletter, eventuale invio campagne
  (newsletter_campaigns), gate admin sull'invio, double opt-in? token? trasporto (mail() nativa vs
  PHPMailer)? rate-limit? confronto con SPW-C9 (double opt-in completo) e SR-C9 (PHPMailer/SMTP).
- public/api/contact.php — form contatti pubblico: validazione, salvataggio in `contacts`, invio
  email di notifica, anti-spam/rate-limit.
- Trasporto email: la funzione `sendEmail`/`mail()` (già vista in participants.php:10-16 e stats.php
  sendVotingReport) — è centralizzata o duplicata? Headers, From, charset.
- Tabelle: newsletter_subscribers (is_active), contacts, newsletter_campaigns (subject/content/
  recipients_count/sent_by) — come vengono usate.
- Consenso/GDPR: l'INSERT newsletter all'approvazione partecipante (DIS-C10) + eventuale checkbox nel
  form. Confronto con il double opt-in di SPW/SR.
- NON sconfinare: festival/email di concorso=C10 (fatto, qui solo il TRASPORTO email), auth=C2,
  admin UI=C12, content=C4.

Fai così:
1. Ispeziona in modo microscopico i file (cita sempre percorso/file:linea).
2. Compila UNA card seguendo _TEMPLATE.md e salvala in
   _cantiere-terza-edizione/mappatura/DISINTELLIGENZA/DIS-C9-newsletter-email.md
3. §6: confronto a TRE — DIS-C9 vs SPW-C9 (double opt-in, token, rate-limit riusa login_attempts) e
   SR-C9 (PHPMailer/SMTP, all-in-one, double opt-in). Asse: quanto è "grezzo" il sistema email di DIS
   (mail() nativa? niente double opt-in? niente token di disiscrizione?).
4. Chiudi i fili lasciati aperti da DIS-C10 (consenso newsletter all'approvazione) e DIS-C2 (rate-limit
   assente: vale anche per newsletter/contact? mail-bombing?).
5. Lascia puntatori per C12 (UI compositore newsletter, se esiste).

Criterio di STOP: card in stato COMPLETATO.

Ciclo di chiusura OBBLIGATORIO a fine sessione:
- aggiorna _cantiere-terza-edizione/mappatura/_INDICE-MAPPATURA.md (DIS-C9 → ✅)
- aggiungi UNA riga a _cantiere-terza-edizione/LOG.md (più recente IN BASSO)
- aggiorna _cantiere-terza-edizione/ROADMAP.md (spunta DIS-C9, aggiorna stato globale)
- git add/commit/push (un commit) e verifica che locale = origin/main
- riscrivi QUESTO file (PROSSIMA-SESSIONE.md) con la prossima unità: DIS-C12 (Admin Dashboard &
  Panels) da sola, poi FDCA-DIFF (ultima unità, chiude FASE 1).
