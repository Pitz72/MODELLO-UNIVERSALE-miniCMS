# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟨 **FASE 3 — SCRITTURA in corso.** Riscritture CHIRURGICHE. Target: 20 capitoli + 2 appendici.
> ✅ CAP 10 Security · ✅ CAP 8 Editing (box-ancora "4 emettitori") · ✅ CAP 11 SEO (la falla viva del filo).
> 🟦 Questa sessione: **4ª card di scrittura — CAP 12 — RSS Feed & Syndication** (chiude il filo dei 4 emettitori).

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
`_cantiere-terza-edizione/ROADMAP.md`, `LOG.md`, `sintesi/_INDICE-SINTESI.md` e — per la scrittura —
`sintesi/S2-inventario-contenuti.md` (azioni/correzioni per capitolo) e `sintesi/S3-scaletta-globale.md`
(indice a 20 capitoli, mappa card→capitolo §3, fili trasversali §4, decisioni del gate §8).

STATO: FASE 1 ✅, FASE 2 ✅, FASE 3 in corso — **CAP 10 ✅ · CAP 8 ✅ · CAP 11 ✅** (3/9 riscritture).
Decisioni del gate (S3 §8): riscritture **CHIRURGICHE**; ordine FASE 3: (1) CAP 10 ✅ → (2) CAP 8 ✅ →
(3) CAP 11 ✅ → **(4) CAP 12 RSS ← QUESTA SESSIONE** → (5) CAP 13 Newsletter → (6) CAP 14 Admin →
(7) CAP 6 Bridge → (8) CAP 7 Media → (9) CAP 20 Reactions → (10) correzioni → (11) App. B Fork → (12) FASE 4.

UNITÀ DI QUESTA SESSIONE: **FASE 3 / scrittura del CAP 12 — RSS Feed & Syndication** (riscrittura chirurgica).
È il **terzo capitolo del filo dei 4 emettitori** (aperto in CAP 8, falla viva in CAP 11): qui il feed
**chiude il buco** perché o non emette il `content` o lo escapa del tutto. Il filo si completerà poi col CAP 13.

Metodo (riscrittura CHIRURGICA — NON da zero):
1. Leggi il **CAP 12 attuale** (`CAPITOLO 12 - RSS Feed & Syndication.md`) e la scheda **S1-C8**
   (`sintesi/S1-C8-rss-feed.md`) per intero (pattern §1, tabella §2, GOLD §3, mappa+correzioni §4).
   Richiama (NON riscrivere) il **box-ancora "4 emettitori"** di CAP 8 §4 e la sua tabella: qui il feed è
   la colonna che chiude per escape/sottrazione. Per gli stralci di codice reali usa le **card di mappatura**
   (`mappatura/*/(*-C8).md`) con riferimento `path:linea`.
2. **Preserva** ciò che è corretto; **sostituisci** le parti smentite; **aggiungi** le sezioni mancanti.
   Correzioni note (da S1-C8 §4): il **feed podcast è di DIS, non di SR** (SR *proxa* feed esterni, non
   genera un feed podcast); il **catch-vuoto è insegnato come pattern** ma è un **anti-pattern** (feed
   troncato servito con HTTP 200); `feed.php` **non è un "alias"**. Aggiungere: il **quadro dei 4 emettitori**
   (richiamo, con la riga feed), il **proxy CORS inbound** di SR (allowlist + stale, anti-open-proxy/SSRF),
   il **`feed_config` security-theater**, la regola `status` dimenticata (bozze nel feed SR), il MIME WebP.
   Ampliare §2.5 GUID/URN: SPW usa un URN stabile, SR e DIS NON lo seguono (regressione urn→permalink→audio_url).
3. **Geografia a 3 (D5):** un file unico SPW (excerpt, niente content) / trittico SR (feed + proxy-inbound +
   feed_config; escapa il content con strip_tags+htmlspecialchars) / feed podcast iTunes DIS (non tocca le news).
   Tesi: il feed è l'emettitore **più sicuro** del content (o non lo emette o lo escapa → il buco XSS non si riapre).
4. Mantieni tono narrativo + blocchi di codice reali con origine `path:linea` + box
   `[!WARNING]`/`[!NOTE]`/`[!TIP]`/`[!IMPORTANT]` (stile casa) + footer "Prossimo Capitolo" (→ CAP 13).
5. **REVISIONE STILISTICA OBBLIGATORIA (regola fissa, memoria `feedback-revisione-stilistica-capitoli`):**
   a capitolo scritto, passalo per la skill **`prosa-italiana`** (tipografia — caporali «», puntini `…`;
   prosa/narrativa — ritmo, lessico, niente filler) **e** per **`humanizer`** (antipattern LLM — trattini
   lunghi abusati, tricolon, signposting, boldface meccanico). Pass finale «cosa rende ancora LLM?» + correzione.
   Verifica via grep che non restino `—` in prosa (solo nei commenti codice è OK) né `...`/`"..."` fuori dal codice.

Criterio di STOP: CAP 12 riscritto (chirurgico) e coerente, con il feed che **chiude il filo dei 4 emettitori**
(richiamo al box-ancora) + correzioni applicate (feed-podcast=DIS, catch-vuoto=anti-pattern, feed.php non-alias,
proxy CORS, feed_config security-theater, GUID URN ampliato); **revisione stilistica eseguita.** NB: CAP resta numerato 12.

Ciclo di chiusura OBBLIGATORIO: aggiorna `ROADMAP.md` (§5: spunta CAP 12, indica CAP 13 come prossimo) +
una riga `LOG.md` + git add/commit/push (verifica sync) + riscrivi QUESTO file (root +
`_cantiere-terza-edizione/`) con la prossima unità: **FASE 3 / CAP 13 — Newsletter & Email System** (riscrittura
chirurgica: **chiude DEFINITIVAMENTE il filo dei 4 emettitori** — nessuno emette content; double opt-in 3 gradini;
rate-limit≠throttle + mail-bombing SR; SMTP/PHPMailer; header-injection via name DIS; unsubscribe-by-email non
GDPR-compliant. Fonti S1-C9).

Nota metodo: un capitolo per sessione (materiale corposo). Scrivere/committare un capitolo alla volta.
