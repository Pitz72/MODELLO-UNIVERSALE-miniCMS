# ISTRUZIONI PER COWORK — Build print-ready EN «React + PHP: The Thin Stack»

> **Documento di handoff autosufficiente.** Lo legge una sessione **Claude Cowork** senza memoria della
> sessione Code. Riguarda l'**edizione inglese (US)**, un listing KDP separato da quello italiano.

## Stato (cosa è già fatto in Claude Code)
- **Traduzione EN integrale + proofread madrelingua US**: 23 file in `manuale-en/` (CHAPTER 01-20 + APPENDIX
  A/B/C). Gate linguistico CHIUSO. Vedi `_cantiere-traduzione-en/LOG-EN.md` e `GLOSSARIO-IT-EN.md`.
- **EPUB EN**: già buildato qui (`ebook/React-PHP-The-Thin-Stack-EN.epub`, en-US) **MA con la copertina
  ebook ITALIANA come placeholder** (vedi §Copertina): va rifatto con la cover EN.
- **Interno EN**: NON finalizzato qui di proposito. L'interno cartaceo si fa in Cowork (ghostscript/DeviceGray
  segfauta su Windows). Gli **script EN sono pronti** (vedi sotto).

## Cosa deve fare Cowork
1. **Interno cartaceo EN** (DeviceGray, print-ready).
2. **Copertina EN** (sia print integrale sia immagine ebook), perché il testo è IT e il **dorso cambia**
   (l'interno EN è **164 pp**, non 160 → dorso diverso → copertina da rigenerare per forza).
3. **Rebuild EPUB EN** con la copertina ebook EN.

## File EN già predisposti (commit su `main`)
```
manuale-en/                                  ← 23 .md EN: FONTE UNICA del testo
_cowork-impaginazione/
├─ produzione/build_book_en.py   ← BUILD INTERNO EN (Typst → 2 passate → DeviceGray via gs)
├─ produzione/template_en.typ    ← gabbia EN (label box EN, "PART", lang "en"); 7×10" B/N
├─ produzione/alerts.lua         ← invariato (filtro box pandoc)
├─ ebook/build_epub_en.py        ← BUILD EPUB EN (pandoc)
├─ ebook/metadata_en.yaml        ← metadata EPUB EN (language: en-US)
├─ copertina/sorgenti/cover_final_en.typ  ← copertina integrale EN (testo tradotto, dorso 164 pp)
└─ master/                       ← qui build_book_en.py scrive l'interno EN
```

## Ambiente
```bash
pip install typst pypandoc fonttools brotli pymupdf pypdf   # + pandoc 3.x e ghostscript a PATH
```

## 1) Interno cartaceo EN
```bash
cd _cowork-impaginazione/produzione
python build_book_en.py
#   → frammenti in capitoli-typ-en/, libro_en.typ, 2 passate (folio + bianche multiplo di 4),
#     DeviceGray via gs, output: ../master/Interno_The-Thin-Stack_3ed_7x10_BN_EN.pdf
```
- Lo script stampa: `Pages: N | multiple-of-4: True | Contents@.. | PartI@..=folio1`.
  In Claude Code (preview, gs in fallback) **N = 164, multiplo di 4 = True, Contents@7, Part I@9**.
- ⚠️ **ghostscript**: build_book_en.py prova il DeviceGray e, se gs fallisce, ripiega sull'interno Typst
  (già grayscale). **In Cowork gs deve girare**: l'obiettivo è il **DeviceGray formale**. Comando manuale di
  riferimento identico a quello IT (vedi `ISTRUZIONI-COWORK-BUILD.md` §gs, ma su `_interno_rgb_en.pdf`).
- Verifica colorspace **DeviceGray**, conteggio pagine **multiplo di 4**.

## 2) Copertina EN  ⚠️ il dorso cambia (164 pp ≠ 160 pp)
- **Copia tradotta** già pronta in `copertina/sorgenti/cover_final_en.typ`:
  - sottotitolo fronte → **The miniCMS protocol for modern web apps**
  - **THIRD EDITION**; retro header **THE MINICMS PROTOCOL**; blurb retro tradotto (3 paragrafi);
  - glossario applicato (thin stack, two **layers**, three **rungs**, **scars**).
- **Geometria ricalcolata per 164 pp** (KDP B/W carta bianca = 0,0572 mm/pagina):
  `spine = 164 × 0,0572 = 9,38 mm` (IT era 9,15 mm). `W = 371,33 mm`, `front0 = 190,355 mm`.
  → **Riconferma il conteggio pagine** stampato da build_book_en.py e, se ≠ 164, ricalcola lo `spine`
  e di conseguenza `W` e `front0` in `cover_final_en.typ` (e in `gen_cover.py` se usi la variante SVG).
- Render copertina print: `typst compile cover_final_en.typ cover_finale_en.pdf` dalla cartella `sorgenti/`
  (font path `../../fonts/IBM_Plex`), poi QA visivo e **preflight KDP** (bleed, dorso, area codice a barre).
- **Immagine ebook EN**: la `copertina/ebook_cover_16.jpg` attuale ha sottotitolo IT
  («Il protocollo miniCMS per Web App moderne») e «TERZA EDIZIONE». Va rifatta in EN
  (sottotitolo **The miniCMS protocol for modern web apps**, **THIRD EDITION**) e salvata come
  `copertina/ebook_cover_16_en.jpg`.

## 3) Rebuild EPUB EN (con cover EN)
- In `ebook/build_epub_en.py` aggiorna `--epub-cover-image` a `copertina/ebook_cover_16_en.jpg`, poi:
```bash
cd _cowork-impaginazione/ebook && python build_epub_en.py   # → React-PHP-The-Thin-Stack-EN.epub
```

## Verifiche prima della consegna
- Interno EN: pagine = quelle riportate dallo script (atteso 164), **multiplo di 4**, **DeviceGray**.
- Nessun residuo IT nei paratesti: deve leggersi **Contents** (non «Indice»), **PART** (non «PARTE»),
  **The Author** (non «L'autore»), **WARNING/NOTE/TIP/IMPORTANT** nei box (non ATTENZIONE/NOTA/…).
- EPUB EN: `dc:language` = **en-US**, copertina **EN**.
- Copertina: dorso coerente col conteggio pagine EN.

## Consegna (archivio pubblicati — sottocartella EN)
```
…\Libri Archiviati\Pubblicati\The Thin Stack\EN\
├─ master\Interno_The-Thin-Stack_3ed_7x10_BN_EN.pdf
├─ ebook\React-PHP-The-Thin-Stack-EN.epub
└─ cover\cover_finale_en.pdf  (+ ebook_cover_16_en.jpg)
```

## KDP
Edizione inglese = **listing KDP separato** (ISBN/ASIN proprio). Il fronte «React + PHP: The Thin Stack»
è già inglese; cambiano sottotitolo, retro e dorso. Preflight KDP su interno DeviceGray + copertina EN.
