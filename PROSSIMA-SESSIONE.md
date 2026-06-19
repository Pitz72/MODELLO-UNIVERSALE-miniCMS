# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟩 **FASE 2 — SINTESI CONCLUSA** (S1 14/14 · S2 · S3 · S4 gate superato il 2026-06-19).
> 🟨 **FASE 3 — SCRITTURA avviata.** Target: 20 capitoli + 2 appendici, **riscritture CHIRURGICHE**.
> Questa è la PRIMA card di scrittura: **CAP 10 — Security & Auth**.

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
`_cantiere-terza-edizione/ROADMAP.md`, `LOG.md`, `sintesi/_INDICE-SINTESI.md` e — per la scrittura —
`sintesi/S2-inventario-contenuti.md` (azioni/correzioni per capitolo) e `sintesi/S3-scaletta-globale.md`
(indice a 20 capitoli, mappa card→capitolo §3, decisioni del gate §8).

STATO: FASE 1 (mappatura) ✅, FASE 2 (sintesi) ✅. Decisioni del gate (S3 §8): nuovo CAP 14 "Admin
Dashboard generale" + rinumerazione Parte V; appendice B "Fork"; analytics come sezione; CAP 7
ribilanciato; etichetta "Terza Edizione"; **riscritture CHIRURGICHE**; ordine FASE 3:
**(1) CAP 10 Security → (2) CAP 8 Editing → (3) CAP 11 SEO → (4) CAP 12 RSS → (5) CAP 13 Newsletter →
(6) CAP 14 Admin → (7) CAP 6 Bridge → (8) CAP 7 Media → (9) CAP 20 Reactions → (10) correzioni →
(11) App. B Fork → (12) FASE 4.**

UNITÀ DI QUESTA SESSIONE: **FASE 3 / scrittura del CAP 10 — Security & Auth** (riscrittura chirurgica).
Motivo della priorità: oggi il capitolo **non parla affatto di CSRF, recovery/reset password,
`session_version`** — è il più lacunoso e le sue nozioni sono referenziate da molti altri capitoli.

Metodo (riscrittura CHIRURGICA — NON da zero):
1. Leggi il **CAP 10 attuale** (`CAPITOLO 10 - Security & Auth.md`) e la scheda **S1-C2**
   (`sintesi/S1-C2-security-auth.md`) per intero (pattern §1, tabella §2, GOLD §3, mappa+correzioni §4).
   Attingi anche a S1-C3 (guard/`session_version` lato client), S1-C5 (delete senza CSRF, upload come
   superficie), S1-C11 (rate-limit a 2 strati, `voter_hash`), S1-C12 (gate role-blind). Per gli stralci
   di codice reali usa le **card di mappatura** (`mappatura/*/(*-C2).md`) con riferimento `path:linea`.
2. **Preserva** ciò che nel CAP 10 è corretto; **sostituisci** le parti smentite; **aggiungi** le sezioni
   mancanti. Correzioni note (da S1-C2 §4): §1.1 SameSite reale = **Strict** non Lax + solo SPW ha tutti
   e 3 i flag (SR senza Secure, DIS nessuno); §1.2 `username` assente in sessione in SR; §3 brute-force
   non è solo `sleep(1)` (è lockout a 3 sedi: DB `login_attempts` SPW / file `.cache` SR / **niente** DIS)
   + **da quale IP** lo conti (box anti-spoof); §6 il caso DDoS-da-bot va spostato a CAP 11 (lasciare qui
   solo la lezione "l'UA non è un gatekeeper").
3. **Aggiungi le sezioni assenti oggi:** CSRF a 3 gradini (Origin/Referer SPW / token sincronizzato SR /
   niente DIS); recovery/reset password (token, scadenza, email da `SITE_URL`, enumeration-safe — solo
   SPW); `session_version` (invalidazione sessioni, fail-closed); credenziali di default
   (random/hardcoded/omessa); gate unico-vs-componibile-vs-inline + **role-blind**; protezione DB-a-file
   (`.data/` + `.htaccess` runtime, DIS) e script `update_db_*` non protetti.
4. **Box-ancora da ospitare qui:** D7 "Fidarsi dell'IP: buco o pregio secondo il modello d'abuso"
   (richiamato da CAP 18 voto e CAP 20 reazioni). Rimando (NON ripetere) al box "4 emettitori" che vive
   in CAP 8.
5. Mantieni il **tono narrativo** del libro ("la teoria senza la cicatrice non insegna") + blocchi di
   codice reali con origine + box problemi/soluzioni. Tesi-filo da innestare: D2 "più ingegnerizzato ≠
   più sicuro" (SR ricco ma fragile su cookie/rate-limit).

Criterio di STOP: CAP 10 riscritto (chirurgico) e coerente, con CSRF/recovery/`session_version`/IP-box
presenti; correzioni applicate. **NB:** la rinumerazione fisica (CAP 10 resta 10 in questa fase — il
nuovo CAP 14 Admin e la rinumerazione Parte V si applicano quando si scrive il CAP 14 / in FASE 4).

Ciclo di chiusura OBBLIGATORIO: aggiorna `ROADMAP.md` (§5: spunta CAP 10, indica CAP 8 come prossimo) +
una riga `LOG.md` + git add/commit/push (verifica sync) + riscrivi QUESTO file (root +
`_cantiere-terza-edizione/`) con la prossima unità: **FASE 3 / CAP 8 — Advanced Content Editing**
(riscrittura chirurgica: Tiptap come scala a 3 gradini, DOMPurify render-time come choke-point, paste
cosmetica ≠ sicurezza; **ospita il box-ancora "I quattro emettitori del content"** che apre il filo
CAP 8→11→12→13; fonti S1-C6 + S1-C7/C8/C9 per il box).

Nota metodo: un capitolo per sessione (è materiale corposo). Se resta margine di contesto, si può iniziare
il CAP 8, ma scrivere/committare un capitolo alla volta.
