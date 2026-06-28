# PROSSIMA SESSIONE — Traduzione EN

> 🎉🎉 **TRADUZIONE EN INTEGRALE COMPLETA.** Tutti e 20 i capitoli + le 3 Appendici (A Boilerplate, B Fork,
> C Testing & Deployment) sono tradotti in `manuale-en/` (un commit per file). Anche i **paratesti**
> (frontespizio, colophon, dedica, Parti, BIO, metadata EPUB) sono tradotti: vedi `PARATESTI-EN.md`.
> La dedica è già dentro `CHAPTER 01 - Manifesto.md`. **Non resta nulla da tradurre.**

## Stato del cantiere (28/06/2026)
- `manuale-en/`: **23 file** — `CHAPTER 01…20` + `APPENDIX A/B/C`. ✅
- Verifica tipografica US su TUTTI i file: **0 caporali «», 0 spelling UK**, em-dash 0 in prosa-corpo
  (solo titoli/footer e annotazioni `file:linea` nei commenti-codice), virgolette dritte solo dentro il codice,
  0 residui IT in prosa (solo stringhe-codice IT volute, policy D2). ✅
- `GLOSSARIO-IT-EN.md`: congelato e ricco (§2 copre CAP 1-20 + App. A/B/C; §3 mappa titoli; §4 idiomi; §5 invariati).
- `LOG-EN.md`: una voce per ogni file, con le decisioni prese.
- `PARATESTI-EN.md`: tutti i testi di servizio EN pronti per la build.

## L'UNICO passo rimasto: BUILD EN (scope Cowork/impaginazione — NON traduzione)
La traduzione è finita. Quel che resta è **produrre i deliverable inglesi**, ed è lavoro di build, non di testo:
1. **Variante EN dello `STRUCT`** in `_cowork-impaginazione/produzione/build_book.py`:
   - puntare ai file `manuale-en/CHAPTER NN - …` e `APPENDIX A/B/C - …` (oggi punta ai nomi IT `CAPITOLO N`);
   - sostituire i paratesti cablati (frontespizio, colophon, Part titles+descrizioni, BIO, «Indice»→«Contents»,
     «L'autore»→«The Author») con le versioni EN di `PARATESTI-EN.md`;
   - `extract_dedica()` funziona identico sul `CHAPTER 01 - Manifesto.md` (la dedica EN è già un blockquote in testa).
2. **Variante EN di `metadata.yaml`** (EPUB): blocco già pronto in `PARATESTI-EN.md` §7 (`language: en-US`, subtitle/
   rights EN).
3. Stessa gabbia 7×10", stessi font IBM Plex. Limite noto: ghostscript DeviceGray segfaulta su Windows
   (l'interno è già grayscale → stampabile lo stesso). Vedi `_cowork-impaginazione/ISTRUZIONI-COWORK-BUILD.md`.
4. **Copertina EN** (quarta/retro + metadati) e **listing KDP separato** (ISBN/ASIN proprio).

## Promemoria finale
- Prima della **pubblicazione** EN: mettere in conto un **proofread da madrelingua tecnico** (la skill `humanizer`
  + il glossario riducono il rischio di traduttese, non lo azzerano; Simone non giudica l'inglese nel merito).
- Convenzioni di traduzione (per eventuali ritocchi): `ROADMAP-EN.md` + `GLOSSARIO-IT-EN.md`. Tipografia US in §3.
