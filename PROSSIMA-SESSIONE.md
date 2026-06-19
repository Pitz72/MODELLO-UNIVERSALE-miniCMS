# PROSSIMA SESSIONE — SESSIONE FINALE DI FINALIZZAZIONE CONTENUTI

> 🟩 **FASE 3 quasi conclusa.** Riscritture 9/9 ✅ · batch correzioni legacy 10/10 ✅ (CAP 1/2/3/4/5/9/16/17/18/19).
> 🟦 **Questa è la sessione finale dei CONTENUTI**: si chiude tutto ciò che resta da *scrivere*, in un colpo solo.

---

## ⚠️ CONFINE DI SCOPE (memoria `scope-claude-code-vs-cowork-kdp`)

Questo progetto in **Claude Code** finalizza i **CONTENUTI** del libro (testo, correttezza tecnica, coerenza,
prosa, tipografia editoriale dei `.md` come caporali «»). La **composizione tipografica / impaginazione per
KDP** (font, margini, gabbia, resa PDF/ebook di stampa, rigenerazione finale di `_master.md` come artefatto)
**NON si fa qui**: è un progetto **Claude Cowork dedicato**. Quando i contenuti saranno finalizzati, Simone
farà domande e darà indicazioni prima del passaggio a Cowork. **Quindi: niente impaginazione, niente build di
stampa. Solo finalizzazione del testo.**

---

Stiamo lavorando alla TERZA EDIZIONE del manuale miniCMS. Leggi prima
`_cantiere-terza-edizione/ROADMAP.md`, `LOG.md`, `sintesi/_INDICE-SINTESI.md`,
`sintesi/S2-inventario-contenuti.md` (azioni) e `sintesi/S3-scaletta-globale.md` (§2 indice 20 cap + 2 appendici, §8 ordine).

STATO: FASE 1 ✅, FASE 2 ✅, FASE 3 — riscritture 9/9 ✅ + correzioni legacy 10/10 ✅. **Manca solo:** 1 capitolo
(CAP 15) + le 2 appendici/allegati + la finalizzazione editoriale di testo (footer/intro/etichetta).

## OBIETTIVO DELLA SESSIONE: chiudere TUTTO il testo. Sei task, in ordine, un commit per task.

### Task 1 — CAP 15 Database Evolution (SQLite → MySQL) · AGGIORNA/CORREGGI · fonte S1-C13
Leggi `CAPITOLO 15 - Database Evolution - Da SQLite a MySQL.md` + `sintesi/S1-C13-db-evolution-incidenti.md`
(la scheda usa la vecchia numerazione: «CAP 14» = questo CAP 15). Correzioni: §1 migrazione motivata da
traffico → è **reazione al crash WAL notturno** (l'incidente È il motivo, salda §1+§2; coerente con CAP 1/3 già
corretti); §6 la checklist **prescrive un backup che SR non ha** (cura-senza-prevenzione, ponte CAP 14);
aggiungi che **DIS gira ANCORA su SQLite in produzione** (non un gradino da abbandonare). Aggiungi (GOLD): i **6
fossili** SQLite in repo, i **3 schemi `subscribers`** divergenti, il **doppio binario** one-shot vs self-healing,
il **bug data-stringa** (separatore T), il debito **schema-as-code senza `schema_version`** (versione nei nomi-file).
Card per gli stralci: `mappatura/SitoRuntime/SR-C13-*.md` + DIS-C1 (`update_db_*`). Footer → CAP 16.

### Task 2 — Appendice B «Ciclo di vita di un fork» (FDCA) · NUOVA · fonte S1-FORK
Crea il file appendice (`APPENDICE B - Ciclo di vita di un fork.md` o nome coerente col README). Materiale S1-FORK:
il fork **eredita tutto il debito** (RCE-upload S1-C5, auth grado-zero, no-opt-in, reset-senza-CSRF, no-DOMPurify) —
**il fix non segue il fork**; **guscio scollegato** (frontend riscritto senza `api.ts`/`fetch`); **v0.0.1 su backend
v0.5.x** (la versione nasconde il debito); **roadmap-AI** che ricalca i cluster; **un-motore-due-festival** (modulo
riusabile). Ponti a CAP 7 (RCE), CAP 10 (sicurezza), CAP 2 §6 (pattern fork già accennato). Registra l'appendice nel README.

### Task 3 — Appendice A / Boilerplate Checklist · AGGIORNA · fonte: tutte le schede
Leggi `BOILERPLATE-CHECKLIST.md`. Riallinea ogni voce ai **20 capitoli rinumerati + 2 appendici** e aggiungi le
checklist-sicurezza emerse: **upload PHP-off** (CAP 7), **CSRF a 3 gradini** (CAP 10), **double opt-in** (CAP 13),
**backup fuori-docroot** (CAP 14), **sanitizzazione server-side condivisa / 4 emettitori** (CAP 8). Verifica i cross-ref `(Cap. N)`.

### Task 4 — E1 · Coerenza editoriale del testo · tutti i 20 capitoli + appendici
Verifica/uniforma: i footer **«Prossimo Capitolo»** seguono l'ordine-libro corretto (1→…→20→App.); aggiungi/ritocca
le **intro di Parte** (I La Visione, II Architettura, III Componenti, IV Flusso Operativo, V Casi Reali) se mancano o
sono incoerenti; tono uniforme. NB: non riscrivere i capitoli, solo cuciture e raccordi.

### Task 5 — E2 · Etichetta «Terza Edizione» ovunque · fonte: incoerenza nota
Oggi l'etichetta è incoerente (README/_master = «Prima Edizione»; build-pdf.sh/articolo-blog = «Seconda Edizione»;
articolo dice «diciotto capitoli» ma sono 20). Uniforma a **«Terza Edizione»** in: `README.md`, `build-pdf.sh`
(manifest/titolo), `articolo-blog-presentazione.md` (20 capitoli + 2 appendici, Terza Edizione). NB: `_master.md`
è artefatto rigenerato → toccarlo solo nell'header testuale se serve, NON impaginarlo (è materia Cowork).

### Task 6 — Verifica finale del libro
`grep` tipografico su TUTTI i capitoli: `—` / `"` / `...` solo dentro blocchi di codice (i capitoli appena scritti
sono già clean; controlla i pochi punti rimasti). README: indice coerente con 20 capitoli + Appendici A/B. Aggiorna
ROADMAP §5/§6/§7 (FASE 3 CONCLUSA; FASE 4-contenuti conclusa; resta solo il passaggio Cowork/KDP) + LOG + commit/push.

## ⚠️ REVISIONE STILISTICA OBBLIGATORIA (regola fissa `feedback-revisione-stilistica-capitoli`)
Per ogni testo NUOVO o riscritto (Task 1, 2, e parti di 3): skill **`prosa-italiana`** + **`humanizer`** + pass
finale «cosa rende ancora LLM?». Checklist (già applicata a CAP 1-20):
- **TIPOGRAFIA:** caporali **«»** (NON `"..."` fuori dal codice); puntini `…` (NON `...`) fuori dal codice; apostrofo
  dritto `'`; accenti corretti; numeri uno-dieci in lettere.
- **ANTIPATTERN:** trattino lungo `—` **NON in prosa** (→ virgola/punto/parentesi; solo in commenti-codice e celle «n/a»);
  niente tricolon meccanici; niente filler («vale la pena», «conviene», «è importante notare», «va detto subito», «in conclusione»);
  niente boldface a raffica; varia il ritmo; preserva la tesi; **niente quarta parete** («versione precedente»/«Seconda Edizione»).
- **VERIFICA GREP prima di ogni commit:** `grep "—"`, `grep '\.\.\.'`, `grep '"'` → solo dentro blocchi di codice.

Criterio di STOP della sessione: CAP 15 scritto, App. A e App. B scritte/allineate, footer/intro/etichetta coerenti,
grep-clean su tutto, README e ROADMAP aggiornati. **A quel punto i CONTENUTI del libro sono FINALIZZATI** e pronti per
la consegna al progetto Cowork di impaginazione KDP. Avvisa Simone: «contenuti finalizzati, pronto per le tue domande
e per il passaggio a Cowork».

Nota metodo: un task per commit (atomico). Dentro la sessione si possono fare tutti e sei, ma committati uno alla volta.
