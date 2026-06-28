# PROSSIMA SESSIONE — Traduzione EN

> ✅ Pianificazione fatta (`ROADMAP-EN.md` + `GLOSSARIO-IT-EN.md`). ✅ **CAP 1-15 tradotti** in `manuale-en/`.
> 🟦 **OBIETTIVO DI QUESTA SESSIONE: completare gli ULTIMI 5 CAPITOLI (16, 17, 18, 19, 20)** con lo stesso
> metodo con cui sono stati fatti i CAP 11-15: **atomico, un capitolo alla volta, un commit per capitolo, con
> tutte le verifiche del caso** — ma più capitoli in fila nella stessa sessione (il contesto resta caldo, non
> si spreca il ricaricamento della memoria). Le Appendici A/B/C restano a valle, in una sessione successiva.

## Prima di tutto
1. Leggi `_cantiere-traduzione-en/ROADMAP-EN.md` (policy, tipografia **US**, ciclo per capitolo) e
   `GLOSSARIO-IT-EN.md` (termini congelati, in crescita).
2. **GATE pilota SUPERATO (28/06):** Simone ha approvato il CAP 1 (voce + tipografia = riferimento per
   tutto il resto). Si prosegue. NB: prima della pubblicazione EN serve un proofread da madrelingua tecnico.

## Obiettivo: completare i CAP 16→20 (uno alla volta, un commit per capitolo)
**Porta a termine il libro traducendo i 5 capitoli rimasti, in ordine:**
- **CAP 16 — Portfolio & Projects Module** (`manuale-en/CHAPTER 16 - Portfolio & Projects Module.md`): modulo
  universale portfolio/showcase, riordino drag-and-drop, visibilità a interruttore.
- **CAP 17 — Festival Logic — Submissions & Approval Workflow**
- **CAP 18 — Festival Logic — Voting & Anti-Fraud Protection**
- **CAP 19 — Festival Logic — Admin Dashboard, Settings & Reporting** (è l'istanza-festival del CAP 14)
- **CAP 20 — Social Interactions & Reactions** (chiude; le reazioni le consuma l'`analytics.php` del CAP 14)

Falli **uno alla volta, completando il ciclo per ciascuno prima di passare al successivo** (NON tutti insieme):
traduci → humanizer → tipografia US → glossario+LOG → grep-clean → **commit del singolo capitolo** → poi il
prossimo. A fine sessione: **push** + verifica sync, e aggiorna `PROSSIMA-SESSIONE-EN.md` + memoria di progetto
(il libro EN sarà finito tranne le Appendici A/B/C, da fare dopo).

Promemoria di metodo: **stringhe letterali italiane nel codice restano intatte** (policy D2), si traducono solo
i commenti; le stringhe-UI IT citate in prosa che portano il senso prendono una **glossa EN una volta**. H1: se
il sorgente IT accorcia il titolo rispetto al nome-file (come CAP 8), rispetta il sorgente; per i titoli col
trattino lungo (CAP 17/18/19) usa la forma EN con **em-dash** già fissata nel glossario §3.

### Ciclo di lavoro (fisso)
1. Traduci dal sorgente italiano congelato, applicando il glossario.
2. **Commenti dentro il codice:** tradurli in EN; identificatori/keyword/stringhe/`path:linea`/versioni intatti.
3. Pass **rilettura madrelingua** + skill **`humanizer`** (NON `prosa-italiana`) + pass «what still reads as translated/AI?».
4. **Tipografia US:** virgolette curve “ ”/‘ ’ (mai «»), punteggiatura DENTRO le virgolette, em-dash chiuso e
   con parsimonia, en-dash per intervalli, virgola di Oxford, spelling -ize/-or, Title Case nei titoli.
5. Aggiorna il **glossario** con i termini nuovi; aggiorna **LOG-EN.md**.
6. **Grep di verifica:** `grep "«\|»"` = 0; virgolette dritte solo dentro i blocchi codice; niente spelling UK
   (`colour|behaviour|centre|-ise`); nessun residuo italiano fuori dai nomi propri.
7. **Commit + push + verifica sync.**

## Note
- Mappa titoli completa e termini in `GLOSSARIO-IT-EN.md` §3/§2.
- Build EN (Typst/EPUB) e listing KDP separato = a valle, scope Cowork (non ora).
- Ordine di questa sessione: CAP 16 → 17 → 18 → 19 → 20 (poi il corpo del libro EN è completo). Le
  Appendici A/B/C sono il passo successivo, in una sessione a parte.
