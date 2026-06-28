# PROSSIMA SESSIONE — Traduzione EN

> ✅ Pianificazione fatta (`ROADMAP-EN.md` + `GLOSSARIO-IT-EN.md`). ✅ **CAP 1-8 tradotti** in `manuale-en/`.
> 🟦 Si prosegue in ordine-libro. **NB: si fanno PIÙ capitoli per sessione** (uno per sessione spreca il
> ricaricamento della memoria — decisione di Simone, 28/06).

## Prima di tutto
1. Leggi `_cantiere-traduzione-en/ROADMAP-EN.md` (policy, tipografia **US**, ciclo per capitolo) e
   `GLOSSARIO-IT-EN.md` (termini congelati, in crescita).
2. **GATE pilota SUPERATO (28/06):** Simone ha approvato il CAP 1 (voce + tipografia = riferimento per
   tutto il resto). Si prosegue. NB: prima della pubblicazione EN serve un proofread da madrelingua tecnico.

## Obiettivo: tradurre i prossimi capitoli (più capitoli a sessione, un commit cumulativo)
**Riparti dal CAP 9 — Content Lifecycle** (`manuale/CAPITOLO 9 - Content Lifecycle.md`
→ `manuale-en/CHAPTER 09 - Content Lifecycle.md`), poi CAP 10 (Security & Auth, corposo), 11, … in ordine.
Valutare quanti farne in base alla lunghezza. Promemoria: **stringhe letterali italiane nel codice restano
intatte** (policy D2); traduci solo i commenti. H1: se il sorgente IT accorcia il titolo rispetto al
nome-file (come CAP 8), rispetta il sorgente.

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
