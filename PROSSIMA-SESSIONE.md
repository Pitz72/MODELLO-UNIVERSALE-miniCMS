# STATO DEL PROGETTO — entrambe le edizioni pubblicate e in distribuzione

> 🏁 **Il lavoro è chiuso.** «React + PHP: The Thin Stack» (Terza Edizione) è pubblicato su Amazon KDP
> in **due listing separati** (italiano e inglese US, ISBN/ASIN propri) ed è **in distribuzione da
> tempo**. Stato confermato da Simone il **12/08/2026**; la data di messa in vendita non è registrata
> in repo. Non c'è lavoro pendente: questo file descrive dove sta cosa, per quando servirà.

---

## Edizione italiana
- **Sorgenti:** `manuale/` — 20 capitoli + 3 appendici (A Boilerplate, B Fork, C Testing & Deploy).
  Contenuti finalizzati il 19/06/2026; ultime correzioni tecniche del revisore il 27/06 (commit `0968314`):
  CAP 16 nota di dialetto sullo schema `projects`, CAP 11 §7 HTML-dai-JSON-di-cache, CAP 20 §3 commento `substr`.
- **Deliverable:** `_cowork-impaginazione/master/Interno_The-Thin-Stack_3ed_7x10_BN.pdf` (**160 pp**),
  `ebook/React-PHP-The-Thin-Stack.epub`, `copertina/cover_finale.pdf` + `ebook_cover_16.jpg`.
- **Cantiere:** `_cantiere-terza-edizione/` (ROADMAP, LOG, mappatura dei 4 siti, schede di sintesi).

## Edizione inglese (US)
- **Sorgenti:** `manuale-en/` — 23 file, `CHAPTER 01…20` + `APPENDIX A/B/C`. Traduzione integrale
  (28/06/2026) + proofread madrelingua tecnico US applicato su tutti i file.
- **Deliverable:** `master/Interno_The-Thin-Stack_3ed_7x10_BN_EN.pdf` (**164 pp**, DeviceGray formale,
  prodotto in Cowork), `ebook/React-PHP-The-Thin-Stack-EN.epub` (en-US),
  `copertina/cover_finale_en.pdf` (dorso 9,38 mm) + `ebook_cover_16_en.jpg`.
- **Cantiere:** `_cantiere-traduzione-en/` (ROADMAP-EN con le convenzioni, GLOSSARIO-IT-EN, LOG-EN,
  PARATESTI-EN).

## Archivio dei pubblicati
`C:\Users\Utente\Documents\Claude\Projects\Progetto di Impaginazione Libri\Libri Archiviati\Pubblicati\The Thin Stack`

---

## Se in futuro servisse una correzione (ristampa)

1. **Correggi i sorgenti `.md`** nella cartella giusta:
   - `manuale/` (IT) → revisione con le skill **`prosa-italiana` + `humanizer`**, tipografia **italiana**
     (caporali «», niente em-dash in prosa);
   - `manuale-en/` (EN) → revisione con la sola skill **`humanizer`**, tipografia **statunitense**
     (virgolette curve, punteggiatura dentro, em-dash ammesso con parsimonia). Convenzioni in
     `_cantiere-traduzione-en/ROADMAP-EN.md` §3 e nel glossario.
2. **Commit + push su `main`**, e registra la modifica nel LOG del cantiere corrispondente.
3. **Rigenera i deliverable** seguendo l'handoff: `_cowork-impaginazione/ISTRUZIONI-COWORK-BUILD.md` (IT)
   o `ISTRUZIONI-COWORK-BUILD-EN.md` (EN). L'EPUB si builda in locale; l'**interno cartaceo DeviceGray va
   fatto in Cowork**, perché su questo Windows `gs` segfaulta a metà conversione (e tronca il PDF in
   scrittura: se corrompe un master tracciato, `git checkout -- <file>`).
4. ⚠️ **Se cambia il numero di pagine** (IT ≠ 160, EN ≠ 164, o non multiplo di 4) va **rigenerata anche
   la copertina**: cambia il dorso.
5. Ricarica sul listing KDP corretto e valuta una copia di prova fisica.
