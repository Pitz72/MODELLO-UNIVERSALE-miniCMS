# PROSSIMA SESSIONE — Traduzione EN

> ✅ Pianificazione fatta (`ROADMAP-EN.md` + `GLOSSARIO-IT-EN.md`). ✅ **CAP 1 (pilota) e CAP 2 tradotti**
> in `manuale-en/`. 🟦 Si prosegue in ordine-libro.

## Prima di tutto
1. Leggi `_cantiere-traduzione-en/ROADMAP-EN.md` (policy, tipografia **US**, ciclo per capitolo) e
   `GLOSSARIO-IT-EN.md` (termini congelati, in crescita).
2. **GATE pilota SUPERATO (28/06):** Simone ha approvato il CAP 1 (voce + tipografia = riferimento per
   tutto il resto). Si prosegue. NB: prima della pubblicazione EN serve un proofread da madrelingua tecnico.

## Obiettivo: tradurre il prossimo capitolo (un capitolo = una sessione = un commit)
**CAP 3 — Database Strategy** (`manuale/CAPITOLO 3 - Database Strategy.md`
→ `manuale-en/CHAPTER 03 - Database Strategy.md`). Ha blocchi codice (PDO/PRAGMA/SQL) e diversi box.

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
- Ordine: CAP 3 → 4 → … → 20 → App. A/B/C. I capitoli corposi (es. CAP 10) possono prendere una sessione intera.
