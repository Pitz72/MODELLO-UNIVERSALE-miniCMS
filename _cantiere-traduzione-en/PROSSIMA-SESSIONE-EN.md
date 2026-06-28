# PROSSIMA SESSIONE — Traduzione EN

> ✅ Pianificazione fatta (`ROADMAP-EN.md` + `GLOSSARIO-IT-EN.md`). ✅ **CAP 1-20 TRADOTTI** in `manuale-en/`.
> 🎉 **IL CORPO DEL LIBRO EN È COMPLETO** (tutti e 20 i capitoli, un commit per capitolo).
> 🟦 **OBIETTIVO DI QUESTA SESSIONE: tradurre le 3 APPENDICI (A, B, C)** — l'ultimo passo prima che l'edizione
> inglese sia integralmente tradotta. Stesso metodo dei capitoli: **atomico, una appendice alla volta, un commit
> per appendice, con tutte le verifiche** — più appendici in fila nella stessa sessione (contesto caldo).

## Prima di tutto
1. Leggi `_cantiere-traduzione-en/ROADMAP-EN.md` (policy, tipografia **US**, ciclo per capitolo) e
   `GLOSSARIO-IT-EN.md` (termini congelati, ormai ricchissimo: §2 copre tutti i CAP 1-20, §3 mappa i titoli,
   §4 gli idiomi). Leggi le ultime righe di `LOG-EN.md` per la voce e le convenzioni già fissate.
2. **GATE pilota SUPERATO (28/06):** voce + tipografia approvate sul CAP 1, riferimento per tutto.
   NB: prima della pubblicazione EN serve comunque un **proofread da madrelingua tecnico**.

## Obiettivo: tradurre le 3 Appendici (una alla volta, un commit per appendice)
**Chiudi la traduzione del libro con le tre appendici, in ordine (mappa titoli in `GLOSSARIO-IT-EN.md` §3):**
- **Appendice A — Boilerplate Checklist** (sorgente: `manuale/BOILERPLATE-CHECKLIST.md` →
  `manuale-en/APPENDIX A - Boilerplate Checklist.md`): la checklist per partire da zero.
- **Appendice B — The Life of a Fork** (sorgente: `manuale/APPENDICE B - Ciclo di vita di un fork.md` →
  `manuale-en/APPENDIX B - The Life of a Fork.md`): FDCA, il guscio scollegato, «il fix non segue il fork»,
  i termini-firma sono già nel glossario §2 (a disconnected shell, the fix doesn't follow the fork, The Fork Pattern).
- **Appendice C — Testing & Deployment** (sorgente: `manuale/APPENDICE C - Testing e Deploy.md` →
  `manuale-en/APPENDIX C - Testing & Deployment.md`): la più snella.

Falle **una alla volta, completando il ciclo per ciascuna prima di passare alla successiva** (NON tutte insieme):
traduci → humanizer → tipografia US → glossario+LOG → grep-clean → **commit della singola appendice** → poi la
prossima. A fine sessione: **push** + verifica sync, aggiorna `PROSSIMA-SESSIONE-EN.md` (a quel punto: traduzione
EN FINITA, resta solo la build Typst/EPUB EN, scope Cowork) + memoria di progetto.

Promemoria di metodo: **stringhe letterali italiane nel codice restano intatte** (policy D2), si traducono solo
i commenti; le stringhe-UI IT citate in prosa che portano il senso prendono una **glossa EN una volta**. H1: se
il sorgente IT accorcia il titolo rispetto al nome-file, rispetta il sorgente; per i titoli con trattino lungo
usa la forma EN con **em-dash** già fissata nel glossario §3. La forma-titolo EN delle appendici è
«Appendix X — Titolo» (em-dash nel titolo: consentito §3).

### Ciclo di lavoro (fisso)
1. Traduci dal sorgente italiano congelato, applicando il glossario.
2. **Commenti dentro il codice:** tradurli in EN; identificatori/keyword/stringhe/`path:linea`/versioni intatti.
3. Pass **rilettura madrelingua** + skill **`humanizer`** (NON `prosa-italiana`) + pass «what still reads as translated/AI?».
4. **Tipografia US:** virgolette curve “ ”/‘ ’ (mai «»), punteggiatura DENTRO le virgolette, em-dash chiuso e
   con parsimonia (0 in prosa-corpo: tienilo a virgola/punto/due-punti; em-dash solo in titoli/footer e nelle
   annotazioni `file:linea` dei commenti-codice), en-dash per intervalli, virgola di Oxford, spelling -ize/-or,
   Title Case nei titoli.
5. Aggiorna il **glossario** con i termini nuovi; aggiorna **LOG-EN.md**.
6. **Grep di verifica:** `grep "«\|»"` = 0; virgolette dritte solo dentro i blocchi codice; niente spelling UK
   (`colour|behaviour|centre|-ise|defence`); nessun residuo italiano fuori dai nomi propri/stringhe-codice volute.
7. **Commit + push + verifica sync.**

## Note
- Mappa titoli completa e termini in `GLOSSARIO-IT-EN.md` §3/§2; idiomi in §4; INVARIATI in §5.
- Build EN (Typst/EPUB) e listing KDP separato = a valle, scope Cowork (non ora): a quel punto serve la variante
  EN dello `STRUCT` (nomi-file, Part titles, BIO, colophon EN) — vedi ROADMAP §7.
- Ordine di questa sessione: Appendice A → B → C. **Dopo le appendici, la traduzione EN del libro è integrale.**
