# LOG — Traduzione EN

Registro cronologico della traduzione inglese (US). Una riga per step.

## 2026-06-28
- **Pilota CAP 1 (Manifesto) tradotto.** Creata cartella `manuale-en/` + `CHAPTER 01 - Manifesto.md`
  (~1.000 parole EN). Applicate le policy della ROADMAP-EN e il glossario. Pass `humanizer` eseguito:
  corretti alcuni calchi dall'italiano («la strada in salita» → *an uphill fight*; «mette numeri sotto la
  frase» → *puts hard numbers to this*; «economicità» → *affordability*; «com'è bello» → *as it looks*).
  Fissati nel glossario i termini-firma del capitolo (The Universal Model, Presentation/Data Plane, base
  rung, essential/engineered MySQL, *In the Wild ↔ The Canon*).
- **Verifiche tipografiche US (clean):** 0 caporali «», 0 virgolette dritte in prosa, 3 em-dash (parsimonia),
  0 spelling UK, 0 residui italiani, virgolette curve presenti.
- Citazione Saint-Exupéry resa con la traduzione inglese canonica.
- **GATE SUPERATO (28/06):** Simone ha approvato il pilota (voce + tipografia). Si prosegue con CAP 2.
  NB: Simone ha dichiarato di non avere competenza per giudicare l'inglese nel merito → prima della
  pubblicazione EN va messo in conto un **proofread da madrelingua tecnico** (come la revisione che ha
  trovato i refusi nell'edizione italiana). La skill `humanizer` + il glossario riducono il rischio, non lo azzerano.
- **CAP 2 (Architecture & Project Structure) tradotto.** Commenti dentro i blocchi codice tradotti in EN;
  identificatori, percorsi, `define()`, script npm e output letterale del log (`🚨 SECURITY:`) intatti.
  Verifiche clean: 0 caporali, 0 spelling UK, 0 residui IT, em-dash solo in 3 commenti-codice (0 in prosa),
  virgolette dritte solo dentro i blocchi codice. Glossario esteso (file-based database, one file per
  endpoint, second net, The Fork Pattern, outside the docroot). **Prossimo: CAP 3 — Database Strategy.**
