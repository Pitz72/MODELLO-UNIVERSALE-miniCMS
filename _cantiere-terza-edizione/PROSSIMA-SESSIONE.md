# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟨 **FASE 3 — SCRITTURA in corso.** Riscritture CHIRURGICHE. Target: 20 capitoli + 2 appendici.
> ✅ CAP 10 Security · ✅ CAP 8 Editing (box-ancora "4 emettitori") · ✅ CAP 11 SEO (falla viva) · ✅ CAP 12 RSS (chiude il filo per escape/sottrazione).
> 🟦 Questa sessione: **5ª card di scrittura — CAP 13 — Newsletter & Email System** (CHIUDE definitivamente il filo dei 4 emettitori).

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
`_cantiere-terza-edizione/ROADMAP.md`, `LOG.md`, `sintesi/_INDICE-SINTESI.md` e — per la scrittura —
`sintesi/S2-inventario-contenuti.md` (azioni/correzioni per capitolo) e `sintesi/S3-scaletta-globale.md`
(indice a 20 capitoli, mappa card→capitolo §3, fili trasversali §4, decisioni del gate §8).

STATO: FASE 1 ✅, FASE 2 ✅, FASE 3 in corso — **CAP 10 ✅ · CAP 8 ✅ · CAP 11 ✅ · CAP 12 ✅** (4/9 riscritture).
Decisioni del gate (S3 §8): riscritture **CHIRURGICHE**; ordine FASE 3: (1) CAP 10 ✅ → (2) CAP 8 ✅ →
(3) CAP 11 ✅ → (4) CAP 12 ✅ → **(5) CAP 13 Newsletter ← QUESTA SESSIONE** → (6) CAP 14 Admin →
(7) CAP 6 Bridge → (8) CAP 7 Media → (9) CAP 20 Reactions → (10) correzioni → (11) App. B Fork → (12) FASE 4.

UNITÀ DI QUESTA SESSIONE: **FASE 3 / scrittura del CAP 13 — Newsletter & Email System** (riscrittura chirurgica).
È il **quarto e ultimo capitolo del filo dei 4 emettitori** (aperto in CAP 8, falla viva in CAP 11, feed che chiude
in CAP 12): qui il filo si **chiude del tutto** perché nessuno dei tre siti emette il `content` nella mail. Ma
proprio perché il rischio XSS è chiuso, la lente vera diventa un'altra: **quanto si può semplificare un sistema di
posta** prima che diventi pericoloso.

Metodo (riscrittura CHIRURGICA — NON da zero):
1. Leggi il **CAP 13 attuale** (`CAPITOLO 13 - Newsletter & Email System.md`) e la scheda **S1-C9**
   (`sintesi/S1-C9-newsletter-email.md`) per intero (pattern §1, tabella §2, GOLD §3, mappa+correzioni §4).
   Richiama (NON riscrivere) il **box-ancora "4 emettitori"** di CAP 8 §4: qui si chiude l'ultima casella.
   Per gli stralci di codice reali usa le **card di mappatura** (`mappatura/*/(*-C9).md`) con riferimento `path:linea`.
2. **Preserva** ciò che è corretto; **sostituisci** le parti smentite; **aggiungi** le sezioni mancanti.
   Correzioni note (da S1-C9 §4): il capitolo **omette il double opt-in** e mostra il modello DIS (mail() nuda)
   attribuendolo a SR; §4 **unsubscribe-by-email NON è GDPR-compliant** (chiunque disiscrive chiunque, serve token);
   §6.3 `usleep` è **throttle non rate-limit**; §6.4 query-senza-content è anche una difesa XSS. Aggiungere:
   **mail-bombing** (SR senza rate-limit), **header-injection via name** (DIS), **SMTP/PHPMailer in prod** vs `mail()`,
   i **2 token** (conferma + disiscrizione).
3. **Scala "quanto puoi semplificare la posta" (D5/D2):** double-opt-in pieno + 2 token + rate-limit (SPW) →
   SMTP-PHPMailer ma un-token-riusato + rate-limit ASSENTE = mail-bombing (SR) → `mail()` nuda senza opt-in né token,
   header-injection via name (DIS). Tesi D2 "più ingegnerizzato ≠ più sicuro" (SR ricco ma lascia il buco più grave).
4. **CHIUDE il filo dei 4 emettitori:** nessuno emette il `content` nella mail (SPW manda solo un link/estratto;
   SR/DIS idem) → il buco XSS non si riapre nemmeno qui. Richiamo finale al box-ancora di CAP 8, con la tabella completata.
5. Mantieni tono narrativo + blocchi di codice reali con origine `path:linea` + box
   `[!WARNING]`/`[!NOTE]`/`[!TIP]`/`[!IMPORTANT]` (stile casa) + footer "Prossimo Capitolo" (→ CAP 14 Admin, nuovo).
6. **REVISIONE STILISTICA OBBLIGATORIA (regola fissa, memoria `feedback-revisione-stilistica-capitoli`):**
   a capitolo scritto, passalo per la skill **`prosa-italiana`** (tipografia — caporali «», puntini `…`;
   prosa/narrativa — ritmo, lessico, niente filler) **e** per **`humanizer`** (antipattern LLM — trattini
   lunghi abusati, tricolon, signposting, boldface meccanico). Pass finale «cosa rende ancora LLM?» + correzione.
   Verifica via grep che non restino `—` in prosa (solo nei commenti codice / celle-tabella «non applicabile» è OK) né `...`/`"..."` fuori dal codice.

Criterio di STOP: CAP 13 riscritto (chirurgico) e coerente, con il double-opt-in + la scala di semplificazione +
mail-bombing/header-injection + il filo dei 4 emettitori **chiuso** (richiamo box-ancora); correzioni applicate
(unsubscribe-by-email non-GDPR, usleep=throttle, modello-DIS-non-è-SR); **revisione stilistica eseguita.** NB: CAP resta numerato 13.

Ciclo di chiusura OBBLIGATORIO: aggiorna `ROADMAP.md` (§5: spunta CAP 13, indica CAP 14 come prossimo) +
una riga `LOG.md` + git add/commit/push (verifica sync) + riscrivi QUESTO file (root +
`_cantiere-terza-edizione/`) con la prossima unità: **FASE 3 / CAP 14 — Admin Dashboard & Panels (NUOVO capitolo)**
(da scrivere quasi da zero — è il capitolo nuovo deciso al gate S4: tre-modelli dashboard + tre-architetture di guardia
+ backup-fuori-docroot + tabella write-only + sezione "Misurare senza terze parti"/analytics first-party; CAP 19
festival-dashboard ne diventa la specializzazione. Qui scatta la **rinumerazione Parte V +1** → valutare se applicarla
ora o in FASE 4. Fonti S1-C12 + S1-C11 per analytics).

Nota metodo: un capitolo per sessione (materiale corposo). Scrivere/committare un capitolo alla volta.
