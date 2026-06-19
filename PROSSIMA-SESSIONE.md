# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟨 **FASE 3 — SCRITTURA in corso.** Riscritture CHIRURGICHE. Target: 20 capitoli + 2 appendici.
> ✅ CAP 10 Security · ✅ CAP 8 Editing · ✅ CAP 11 SEO · ✅ CAP 12 RSS · ✅ CAP 13 Newsletter
> 🟢 **FILO DEI 4 EMETTITORI COMPLETO** (CAP 8→11→12→13).
> 🟦 Questa sessione: **6ª card — CAP 14 — Admin Dashboard & Panels (CAPITOLO NUOVO + rinumerazione Parte V).**

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
`_cantiere-terza-edizione/ROADMAP.md`, `LOG.md`, `sintesi/_INDICE-SINTESI.md` e — per la scrittura —
`sintesi/S2-inventario-contenuti.md` (sezione B1 = il capitolo Admin nuovo) e `sintesi/S3-scaletta-globale.md`
(indice a 20 capitoli §2 + nota rinumerazione §2 + decisioni gate §8).

STATO: FASE 1 ✅, FASE 2 ✅, FASE 3 in corso — **CAP 10 ✅ · 8 ✅ · 11 ✅ · 12 ✅ · 13 ✅** (5/9).
Ordine (S3 §8): … → (6) **CAP 14 Admin [NUOVO] ← QUESTA SESSIONE** → (7) CAP 6 Bridge → (8) CAP 7 Media →
(9) CAP 20 Reactions → (10) correzioni → (11) App. B Fork → (12) FASE 4.

UNITÀ DI QUESTA SESSIONE: **FASE 3 / CAP 14 — Admin Dashboard & Panels (generale)** — è il **capitolo NUOVO**
deciso al gate S4 (S2/B1): oggi NON esiste, l'unica "dashboard" è il CAP 19 festival. Si scrive **quasi da zero**
(non è una riscrittura chirurgica). **Attenzione:** questa è anche la sessione in cui scatta la **rinumerazione
fisica della Parte V (+1)**.

⚠️ PASSO 0 — RINUMERAZIONE (da fare PRIMA di scrivere, altrimenti due file "CAP 14"):
Inserendo il nuovo CAP 14 Admin in Parte IV, tutta la Parte V scala di +1. Rinominare i file + aggiornare gli
header `# CAPITOLO N` + i cross-reference interni + README + Boilerplate:
- `CAPITOLO 14 - Database Evolution - Da SQLite a MySQL.md` → **CAP 15**
- `CAPITOLO 15 - Portfolio & Projects Module.md` → **CAP 16**
- `CAPITOLO 16 - Festival Logic - Iscrizioni…` → **CAP 17**
- `CAPITOLO 17 - Festival Logic - Votazioni…` → **CAP 18**
- `CAPITOLO 18 - Festival Logic - Dashboard Admin…` → **CAP 19** (diventa la *specializzazione festival* del nuovo CAP 14)
- `CAPITOLO 19 - Social Interactions & Reactions.md` → **CAP 20**
Poi creare il nuovo file `CAPITOLO 14 - Admin Dashboard & Panels.md`. Verificare con grep i cross-ref ("CAP 14".."CAP 19",
"Capitolo 14".."19") nei capitoli e in README/_master/Boilerplate e correggerli. (NB: la memoria di progetto dice che
una rinumerazione è già stata fatta una volta → procedere con cura, un rename alla volta.) Se la sessione si allunga
troppo, si può fare SOLO la rinumerazione in questa sessione e scrivere il capitolo nella successiva — decidere all'inizio.

Metodo (scrittura del NUOVO capitolo Admin):
1. Leggi le schede **S1-C12** (`sintesi/S1-C12-admin-dashboard.md`) — principale — e **S1-C11**
   (`sintesi/S1-C11-engagement-reactions.md`) per la sezione analytics. Per gli stralci di codice reali usa le
   card di mappatura `mappatura/*/(*-C12).md` (+ SPW-C11 per `analytics.php`) con riferimento `path:linea`.
2. Materiale (da S2/B1 + S1-C12): i **tre modelli di dashboard** su DUE assi ortogonali — *quanto misura*
   (Chart.js analitica SPW / non-misura console-CRUD SR / testuale DIS) e *come è costruita* (route-guard-loader
   SPW / mega-componente SR / AdminLayout+guard-componente DIS); **backup fuori-docroot + `.htaccess` runtime**
   (SPW ha la rete, SR NIENTE → "cura senza prevenzione", ponte CAP 15); **tabella write-only** (`contacts` mai
   letti, DIS); **gate role-blind** (rimando CAP 10); **`session_version` server vs logout client** (rimando CAP 10);
   **console nascosta di manutenzione** (GET senza UI, SR); `confirm()` ≠ CSRF; `app_settings` mass-write.
3. **Sezione "Misurare senza terze parti"** (S2/B3, analytics first-party): view dedup per IP-giorno, click
   rate-limited con risposta neutra, niente Google Analytics. Fonti SPW-C11 (`analytics.php`) + S1-C11.
4. Inquadra il CAP 19 (festival dashboard) come **specializzazione** di questo capitolo generale (rimando).
5. Tono narrativo + scala a 3 gradini (D5) + box `[!WARNING]`/`[!NOTE]`/`[!TIP]`/`[!IMPORTANT]` + footer
   "Prossimo Capitolo" (→ CAP 15 Database Evolution, ex-14).
6. **REVISIONE STILISTICA OBBLIGATORIA (regola fissa, memoria `feedback-revisione-stilistica-capitoli`):**
   skill **`prosa-italiana`** (caporali «», puntini `…`, ritmo, niente filler) + **`humanizer`** (trattini lunghi,
   tricolon, signposting, boldface meccanico) + pass finale «cosa rende ancora LLM?». Verifica grep: niente `—`
   in prosa (ok nei commenti codice / celle-tabella), niente `...`/`"..."` fuori dal codice.

Criterio di STOP: rinumerazione Parte V completata e verificata (grep cross-ref puliti) + nuovo CAP 14 Admin
scritto e coerente (tre-modelli + tre-architetture + backup-placement + write-only + role-blind + sezione analytics
+ CAP 19 come specializzazione); **revisione stilistica eseguita.**

Ciclo di chiusura OBBLIGATORIO: aggiorna `ROADMAP.md` (§5: spunta CAP 14, segna la rinumerazione fatta, indica
CAP 6 Bridge come prossimo) + una riga `LOG.md` + git add/commit/push (verifica sync) + riscrivi QUESTO file
(root + `_cantiere-terza-edizione/`) con la prossima unità: **FASE 3 / CAP 6 — Frontend Bridge (API.ts)**
(riscrittura chirurgica: Double Read corretto — il nome "Double Read"≠response-cloning; CSRF lato client; guard
loader-vs-componente; messaggio backend perso. Fonti S1-C3).

Nota metodo: un capitolo per sessione. La rinumerazione + il capitolo nuovo sono parecchio: se serve, spezzare.
