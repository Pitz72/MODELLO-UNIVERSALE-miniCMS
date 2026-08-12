# CANTIERE EN — CHIUSO

> 🏁 **Non c'è una «prossima sessione».** L'edizione inglese di «React + PHP: The Thin Stack» è
> **tradotta, revisionata, impaginata, pubblicata su KDP e in distribuzione** (stato confermato da
> Simone il **12/08/2026**; il listing è online da tempo, data esatta non registrata qui).
> Questo file resta come chiusura del cantiere, non come prompt di lavoro.

## Cosa è stato completato

### 1. Traduzione (chiusa il 28/06/2026)
- `manuale-en/`: **23 file** — `CHAPTER 01…20` + `APPENDIX A/B/C`, un commit per file.
- Paratesti tradotti in `PARATESTI-EN.md` (frontespizio, colophon, dedica, Parti, BIO, metadata EPUB).
- Verifica tipografica US su tutti i file: 0 caporali «», 0 spelling UK, em-dash 0 in prosa-corpo,
  0 residui IT in prosa (restano solo le stringhe-codice IT volute, policy D2).

### 2. Gate linguistico — proofread madrelingua tecnico US (chiuso il 28/06/2026)
Triage applicato su tutti i 23 file: **Plane→Layer**, **treatment→cure without prevention**,
**net→safety net/backstop**, **rung/scale invariato**, più de-calchi nativi puntuali.
Respinte: l'inversione dell'analogia estintore/allarme (CAP 14) e `forged`→`spoofed` per il CSRF.
Dettaglio in `GLOSSARIO-IT-EN.md` §«Decisioni di revisione madrelingua US» e in `LOG-EN.md`.

### 3. Build EN (chiusa il 29/06/2026)
- **Interno cartaceo**: `_cowork-impaginazione/master/Interno_The-Thin-Stack_3ed_7x10_BN_EN.pdf` —
  DeviceGray formale (Ghostscript 9.55.0, prodotto in **Cowork**), **164 pp** multiplo di 4,
  504×720 pt (7×10"), font IBM Plex embedded.
- **EPUB**: `ebook/React-PHP-The-Thin-Stack-EN.epub` (en-US, cover EN).
- **Copertina**: `copertina/cover_finale_en.pdf` (dorso 9,38 mm per 164 pp) + `ebook_cover_16_en.jpg`.
- Script: `produzione/build_book_en.py` + `template_en.typ`; `ebook/build_epub_en.py` + `metadata_en.yaml`.

### 4. Pubblicazione KDP
Listing **EN separato** da quello italiano (ISBN/ASIN proprio). Caricato e **in distribuzione**.

## Se un giorno servisse una correzione all'edizione EN
1. Correggi i `.md` in `manuale-en/` — convenzioni in `ROADMAP-EN.md` §3 (tipografia **US**, non italiana)
   e `GLOSSARIO-IT-EN.md`. Revisione con la skill **`humanizer`**, **non** `prosa-italiana`.
2. Commit + push su `main`, e registra la modifica in `LOG-EN.md`.
3. Rigenera i deliverable seguendo `_cowork-impaginazione/ISTRUZIONI-COWORK-BUILD-EN.md`
   (l'interno DeviceGray va fatto in **Cowork**: `gs` segfaulta su Windows).
4. ⚠️ Se il conteggio pagine cambia (≠ 164 o non multiplo di 4) va **rigenerata anche la copertina**,
   perché cambia il dorso.
5. Ricarica su KDP il listing EN (e ordina una copia di prova se l'interno è cambiato).
