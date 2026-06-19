# PROSSIMA SESSIONE — prompt pronto da incollare

> 🟩 **FASE 3 quasi conclusa.** Riscritture 9/9 ✅ · batch correzioni legacy 10/10 ✅ (CAP 1/2/3/4/5/9/16/17/18/19).
> Restano: **CAP 15 Database Evolution** (non era nel batch) + **App. B Fork (FDCA)**, poi FASE 4.
> 🟦 Questa sessione: **CAP 15 — Database Evolution (SQLite → MySQL).**

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
`_cantiere-terza-edizione/ROADMAP.md`, `LOG.md`, `sintesi/_INDICE-SINTESI.md` e — per il lavoro —
`sintesi/S2-inventario-contenuti.md` (azione per capitolo) e `sintesi/S3-scaletta-globale.md` (§3 mappa card→capitolo, §8 ordine).

STATO: FASE 1 ✅, FASE 2 ✅, FASE 3 — riscritture 9/9 ✅ + correzioni legacy 10/10 ✅. Resta da fare in FASE 3:
**CAP 15 Database Evolution** (AGGIORNA/CORREGGI, S1-C13) e **App. B Fork (FDCA)** (S1-FORK), poi **FASE 4** editoriale.

UNITÀ DI QUESTA SESSIONE: **FASE 3 / CAP 15 — Database Evolution (Da SQLite a MySQL)** (AGGIORNA/CORREGGI).

> NB numerazione: dopo la rinumerazione di Parte V, **CAP 15 = Database Evolution** (ex CAP 14 in S2/S1-C13).
> La scheda S1-C13 usa la vecchia numerazione: «CAP 14» = questo capitolo (CAP 15 attuale).

Metodo (AGGIORNA/CORREGGI — NON da zero):
1. Leggi il **CAP 15 attuale** (`CAPITOLO 15 - Database Evolution - Da SQLite a MySQL.md`) e la scheda **S1-C13**
   (`sintesi/S1-C13-db-evolution-incidenti.md`) per intero (§3 GOLD + §4 mappa/correzioni). Per gli stralci di
   codice reali le card `mappatura/*/(*-C13).md` (SR) / *-C1 (DIS update_db_*) con `path:linea`.
2. Applica AGGIORNA/CORREGGI. Correzioni note (S1-C13 §4):
   - §1 la migrazione è motivata da **soglie di traffico** → il caso reale di SR è la **reazione a un crash WAL
     notturno** (saldare §1+§2: l'incidente È il motivo); coerente con CAP 3 §6 e CAP 1 già corretti.
   - §6 la checklist **prescrive un backup che SR non ha** (il flagship-incidenti è il meno attrezzato:
     cura-senza-prevenzione, ponte CAP 14); allineare.
   - il capitolo è **SR-centrico** e non dice che **DIS gira ANCORA su SQLite in produzione** (SQLite vivo, non
     un gradino da abbandonare) — aggiungere il contrappunto.
   - Aggiungere (GOLD S1-C13): i **6 fossili** SQLite in repo (igiene), i **3 schemi `subscribers`** divergenti
     (init/fossile-rotto/self-healing), il **doppio binario** one-shot vs self-healing, il **bug data-stringa**
     (`debug_time` separatore T), il debito **"schema-as-code" senza `schema_version`** (versione nei nomi-file).
3. Allinea i rimandi alla numerazione attuale (Parte V 15-20) e ai capitoli già fatti (CAP 1/3/9/14 toccano il tema).
4. Tono narrativo + blocchi di codice reali `path:linea` + box `[!WARNING]`/`[!NOTE]`/`[!TIP]`/`[!IMPORTANT]` (stile casa)
   + footer "Prossimo Capitolo" coerente (→ CAP 16 Portfolio in ordine-libro).

5. ⚠️ **REVISIONE STILISTICA OBBLIGATORIA — REGOLA FISSA** (`feedback-revisione-stilistica-capitoli`).
   prosa-italiana + humanizer + pass finale «cosa rende ancora LLM?». Checklist (applicata a CAP 1-9/16-20):
   - **TIPOGRAFIA:** caporali **«»** (NON `"..."` fuori dal codice); puntini `…` (NON `...`) fuori dal codice;
     apostrofo dritto `'`; accenti corretti; numeri uno-dieci in lettere. I capitoli legacy con `"..."` vanno allineati a «».
   - **ANTIPATTERN:** trattino lungo `—` **NON in prosa** (→ virgola/punto/parentesi; solo in commenti-codice e celle «n/a»);
     niente tricolon meccanici; niente filler («vale la pena», «conviene», «è importante notare», «va detto subito», «in conclusione»);
     niente boldface a raffica; varia il ritmo; preserva tesi; **niente quarta parete** («versione precedente»/«Seconda Edizione»).
   - **VERIFICA GREP prima del commit:** `grep "—"`, `grep '\.\.\.'`, `grep '"'` → solo dentro blocchi di codice.

Criterio di STOP: CAP 15 corretto e coerente (migrazione=reazione-a-incidente non traffico; DIS-SQLite-vivo;
6-fossili/3-schemi/doppio-binario/schema-as-code; cura-senza-prevenzione) + **revisione stilistica eseguita**.

Ciclo di chiusura OBBLIGATORIO: aggiorna `ROADMAP.md` (§5/§7) + una riga `LOG.md` + git add/commit/push (verifica sync)
+ riscrivi QUESTO file (root + `_cantiere-terza-edizione/`) con la prossima unità: **App. B Fork (FDCA)** da
`sintesi/S1-FORK-fdca.md` (il fork eredita tutto il debito — RCE inclusa, il fix non segue il fork; guscio
scollegato senza api.ts; v0.0.1 su backend v0.5.x; roadmap-AI; un-motore-due-festival). **Ricorda di rimettere
le REGOLE TIPOGRAFICHE/PROSA/ANTIPATTERN come qui sopra.** Dopo App. B → **FASE 4** (E1 footer/intro, E2 etichetta
"Terza Edizione" ovunque, E3 build PDF).

Nota metodo: un capitolo per sessione. Scrivere/committare un capitolo alla volta.
