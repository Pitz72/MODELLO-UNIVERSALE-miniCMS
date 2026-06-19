# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟩 **FASE 3 — riscritture dei capitoli COMPLETE (9/9).** Restano: correzioni capitoli legacy + App. B Fork.
> ✅ CAP 10 · ✅ CAP 8 · ✅ CAP 11 · ✅ CAP 12 · ✅ CAP 13 · ✅ CAP 14 (NUOVO) · ✅ CAP 6 · ✅ CAP 7 · ✅ CAP 20
> 🟢 Filo 4 emettitori COMPLETO · 🟢 Rinumerazione Parte V eseguita (20 capitoli fisici).
> 🟦 Questa sessione: **10ª card — batch correzioni capitoli legacy (iniziare da CAP 9 Content Lifecycle).**

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
`_cantiere-terza-edizione/ROADMAP.md`, `LOG.md`, `sintesi/_INDICE-SINTESI.md` e — per il lavoro —
`sintesi/S2-inventario-contenuti.md` (azione per capitolo: CONFERMA/AGGIORNA/RISCRIVI/CORREGGI) e
`sintesi/S3-scaletta-globale.md` (indice a 20 capitoli §2, mappa card→capitolo §3, decisioni gate §8).

STATO: FASE 1 ✅, FASE 2 ✅, FASE 3 — **riscritture dei 9 capitoli COMPLETE**
(**CAP 10 ✅ · 8 ✅ · 11 ✅ · 12 ✅ · 13 ✅ · 14 ✅ · 6 ✅ · 7 ✅ · 20 ✅**).
Ordine (S3 §8): … → **(10) correzioni CAP 1/2/3/4/5/9/16/17/18/19 ← QUESTA FASE** → (11) App. B Fork → (12) FASE 4.

UNITÀ DI QUESTA SESSIONE: **FASE 3 / correzioni capitolo legacy — proposta: CAP 9 Content Lifecycle**
(è il capitolo legacy più impattato: ha ASSORBITO la cache TTL spostata da CAP 7, e va allineato a S1-C4).

> ⚠️ SCELTA INIZIO: il batch tocca CAP 1/2/3/4/5/9/16/17/18/19. **CAP 9** è il candidato migliore per primo,
> perché: (a) il CAP 7 appena riscritto ha esplicitamente spostato lì la **cache TTL delle liste** (`.cache/`
> JSON, X-Cache HIT/MISS, invalidazione su POST) → CAP 9 deve ora ACCOGLIERLA; (b) S1-C4 ha correzioni
> pronte (§2.2/§4/§1.1/§5: Double Read CHIUSO lato server = solo `articles` lista ritorna `{data,total}`,
> mosaico 3-buste SR, busta-zero DIS, paginazione chi-conta, "tre modi di sbagliare il fuso" sui post
> programmati, schema-solo-nel-.sqlite DIS, residui-di-migrazione, tag-doppia-scrittura SPW, tre-slug SR,
> 404-non-403). Se preferisci, puoi invece partire da un capitolo più leggero (CAP 1/2/3) o dall'**App. B Fork**.
> **Conferma con Simone da quale capitolo iniziare se hai dubbi.**

Metodo (CORREZIONE / riscrittura mirata — NON da zero):
1. Leggi il **capitolo legacy scelto** e la **scheda di sintesi** corrispondente per intero
   (per CAP 9 → `sintesi/S1-C4-content-apis.md`, §3 GOLD + §4 mappa/correzioni; per gli stralci di codice
   reali le card `mappatura/*/(*-C4).md` con `path:linea`). Per gli altri capitoli vedi la mappa card→capitolo
   in `S3-scaletta-globale.md` §3 e l'azione in `S2-inventario-contenuti.md`.
2. Applica l'azione prevista da S2 (CONFERMA / AGGIORNA / CORREGGI / RISCRIVI): **preserva** il corretto,
   **sostituisci** le parti smentite dalle fonti, **aggiungi** le sezioni mancanti, **integra** lo scope
   spostato (per CAP 9: accogli la cache TTL da CAP 7).
3. Allinea i **rimandi incrociati** alla numerazione attuale (Parte V = 15-20) e ai capitoli già riscritti.
4. Tono narrativo + blocchi di codice reali con origine `path:linea` + box `[!WARNING]`/`[!NOTE]`/`[!TIP]`/`[!IMPORTANT]`
   (stile casa) + footer "Prossimo Capitolo" coerente con l'ordine-libro.

5. ⚠️ **REVISIONE STILISTICA OBBLIGATORIA — REGOLA FISSA (memoria `feedback-revisione-stilistica-capitoli`).**
   A capitolo completato, PRIMA del commit, passalo per le skill **`prosa-italiana`** e **`humanizer`**, poi il
   pass finale «cosa rende ancora questo testo ovviamente LLM?» e correggi. Libro tecnico ma narrativo e piacevole.
   Checklist (già applicata a CAP 6/7/8/10/11/12/13/14/20):
   - **TIPOGRAFIA ITALIANA:** caporali **«»** per termini/citazioni/etichette (NON `"..."` dritte fuori dal codice);
     puntini `…` (NON `...`) fuori dal codice; apostrofo dritto `'` (coerenza col libro); accenti corretti
     (è/é, perché, sé, né); i numeri da uno a dieci in lettere. **NB legacy:** i capitoli vecchi usano `"..."`
     dritte → vanno allineati a «» proprio in questa fase di correzione.
   - **ANTIPATTERN LLM (humanizer):** **trattino lungo `—` NON in prosa** (→ virgola/punto/parentesi; ammesso solo
     nei commenti dei blocchi di codice e come cella «non applicabile» in tabella); niente **tricolon** non guadagnati;
     niente **filler/signposting** («vale la pena», «conviene», «è importante notare», «va detto subito», «in conclusione»);
     niente **boldface meccanico** a raffica; varia il ritmo; preserva voce e tesi; **non rompere la quarta parete**
     (niente «versione precedente del capitolo» né «Seconda Edizione»).
   - **VERIFICA GREP prima del commit:** `grep "—"` → solo commenti-codice/celle-tabella; `grep '\.\.\.'` e
     `grep '"'` → solo dentro blocchi di codice; conta caporali e filler. (Comandi nei LOG di CAP 6/7/20.)

Criterio di STOP: capitolo legacy corretto e coerente con le fonti + scope spostato integrato + rimandi allineati
+ **revisione stilistica eseguita** (incluso allineamento tipografico «» se è un capitolo legacy con `"..."`).

Ciclo di chiusura OBBLIGATORIO: aggiorna `ROADMAP.md` (§5: segna il capitolo corretto; §7 stato) + una riga `LOG.md`
+ git add/commit/push (verifica sync) + riscrivi QUESTO file (root + `_cantiere-terza-edizione/`) con la prossima
unità del batch correzioni (prossimo capitolo legacy o App. B Fork). **Ricorda di rimettere le REGOLE
TIPOGRAFICHE/PROSA/ANTIPATTERN come qui sopra.**

Nota metodo: un capitolo per sessione. Scrivere/committare un capitolo alla volta.
