# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟨 **FASE 3 — SCRITTURA in corso.** Riscritture CHIRURGICHE. Target: 20 capitoli + 2 appendici.
> ✅ CAP 10 Security · ✅ CAP 8 Editing · ✅ CAP 11 SEO · ✅ CAP 12 RSS · ✅ CAP 13 Newsletter · ✅ CAP 14 Admin (NUOVO)
> 🟢 Filo 4 emettitori COMPLETO · 🟢 **Rinumerazione Parte V eseguita** (ora 20 capitoli fisici, ex 14-19 → 15-20).
> 🟦 Questa sessione: **7ª card — CAP 6 — Frontend Bridge (API.ts).**

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
`_cantiere-terza-edizione/ROADMAP.md`, `LOG.md`, `sintesi/_INDICE-SINTESI.md` e — per la scrittura —
`sintesi/S2-inventario-contenuti.md` (azioni/correzioni per capitolo) e `sintesi/S3-scaletta-globale.md`
(indice a 20 capitoli §2, mappa card→capitolo §3, decisioni gate §8).

STATO: FASE 1 ✅, FASE 2 ✅, FASE 3 in corso — **CAP 10 ✅ · 8 ✅ · 11 ✅ · 12 ✅ · 13 ✅ · 14 ✅** (6/9).
Ordine (S3 §8): … → **(7) CAP 6 Bridge ← QUESTA SESSIONE** → (8) CAP 7 Media → (9) CAP 20 Reactions →
(10) correzioni CAP 1/2/3/4/5/9/16/17/18/19 → (11) App. B Fork → (12) FASE 4.

UNITÀ DI QUESTA SESSIONE: **FASE 3 / CAP 6 — Frontend Bridge (API.ts)** (riscrittura chirurgica).

Metodo (riscrittura CHIRURGICA — NON da zero):
1. Leggi il **CAP 6 attuale** (`CAPITOLO 6 - Frontend Bridge (API.ts).md`) e la scheda **S1-C3**
   (`sintesi/S1-C3-frontend-bridge.md`) per intero (pattern §1, tabella §2, GOLD §3, mappa+correzioni §4).
   Per gli stralci di codice reali usa le card di mappatura `mappatura/*/(*-C3).md` con riferimento `path:linea`.
2. **Preserva** ciò che è corretto; **sostituisci** le parti smentite; **aggiungi** le sezioni mancanti.
   Correzioni note (da S1-C3 §4): il nome **"Double Read" è sbagliato** (non è response-cloning: è il
   pattern "tre modi di leggere il payload" array-vs-{data,total}); aggiungere **CSRF lato client** (token
   in-memory di SR), la **guard loader-vs-componente**, il **messaggio backend perso** (es. login 429),
   l'assenza di **interceptor 401** mid-sessione. NB: **FDCA non ha api.ts** (frontend scollegato, fuori scala).
3. Scala/varianti: stesso oggetto `api` su `fetch` con tre investimenti attorno a un'API non-uniforme —
   state-layer + Double Read SPW / token CSRF in-memory SR / codemod `fix_api` DIS. Tesi D2 dove pertinente.
4. Tono narrativo + blocchi di codice reali con origine `path:linea` + box `[!WARNING]`/`[!NOTE]`/`[!TIP]`/`[!IMPORTANT]`
   (stile casa) + footer "Prossimo Capitolo" (→ CAP 7 Media/Upload, la prossima riscrittura dell'ordine FASE 3;
   oppure, se preferisci l'ordine-libro, → CAP 7 comunque, dato che 6→7 coincidono).

5. ⚠️ **REVISIONE STILISTICA OBBLIGATORIA — REGOLA FISSA (memoria `feedback-revisione-stilistica-capitoli`).**
   A capitolo scritto, PRIMA del commit, passalo per le skill **`prosa-italiana`** e **`humanizer`**, poi fai
   il pass finale «cosa rende ancora questo testo ovviamente LLM?» e correggi. Il libro è tecnico ma deve
   essere semplice, narrativo, piacevole — senza appiattire la tesi. Checklist concreta (già applicata a CAP 8/10/11/12/13/14):
   - **TIPOGRAFIA ITALIANA:** virgolette **caporali «»** per termini/citazioni/etichette (NON le `"..."` dritte
     fuori dal codice); puntini di sospensione `…` unici (NON `...`) fuori dal codice; apostrofo curvo `'`;
     accenti corretti (è/é, perché, sé, né); i numeri da uno a dieci in lettere.
   - **ANTIPATTERN LLM (humanizer):** il **trattino lungo `—` NON va usato in prosa** (convertilo in virgola,
     punto o parentesi) — è ammesso SOLO nei commenti dei blocchi di codice (etichette d'origine) e come cella
     «non applicabile» nelle tabelle; niente **tricolon** non guadagnati (gruppi di tre meccanici); niente
     **signposting/filler** («vale la pena», «conviene», «è importante notare», «approfondiamo», «in conclusione»)
     ripetuti; niente **boldface meccanico** a raffica; niente conclusioni genericamente positive; varia il ritmo
     delle frasi; preserva voce e posizione (la tesi NON va annacquata).
   - **VERIFICA GREP prima del commit:** `grep "—"` → solo commenti-codice/celle-tabella; `grep '\.\.\.'` e
     `grep '"'` → solo dentro blocchi di codice; conta caporali e filler. (Vedi i comandi usati nei LOG di CAP 11/12/13/14.)

Criterio di STOP: CAP 6 riscritto (chirurgico) e coerente, con "Double Read" corretto + CSRF client + guard
loader-vs-componente + messaggio-backend-perso + no-interceptor-401; correzioni applicate; **revisione stilistica eseguita.**

Ciclo di chiusura OBBLIGATORIO: aggiorna `ROADMAP.md` (§5: spunta CAP 6, indica CAP 7 come prossimo) +
una riga `LOG.md` + git add/commit/push (verifica sync) + riscrivi QUESTO file (root +
`_cantiere-terza-edizione/`) con la prossima unità: **FASE 3 / CAP 7 — Media & Optimization — Upload & Sicurezza**
(riscrittura chirurgica: difesa upload 3/1/0 SPW/SR/DIS, catena RCE pubblica DIS, `$_FILES['type']` non è
validazione, PHP-off `.htaccess`, path-guard realpath/basename, WebP non universale; cache TTL già spostata a
CAP 9, SEO a CAP 11. Fonti S1-C5). **Ricorda di rimettere le REGOLE TIPOGRAFICHE/PROSA/ANTIPATTERN come qui sopra.**

Nota metodo: un capitolo per sessione. Scrivere/committare un capitolo alla volta.
