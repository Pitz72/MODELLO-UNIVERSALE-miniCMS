# ISTRUZIONI PER COWORK — Build print-ready EN «React + PHP: The Thin Stack»

> ✅ **HANDOFF GIÀ ESEGUITO (29/06/2026).** Cowork ha prodotto l'interno DeviceGray EN
> (`master/Interno_The-Thin-Stack_3ed_7x10_BN_EN.pdf`, 164 pp) e l'edizione inglese è poi stata
> **pubblicata su KDP ed è in distribuzione**. Questo documento resta come **procedura di rebuild**
> per un'eventuale ristampa futura, non come lavoro da fare.

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
1. **Interno cartaceo EN** (DeviceGray, print-ready) — l'UNICA cosa che richiede gs/Linux.
2. **Preflight KDP** della copertina print EN già renderizzata (`copertina/cover_finale_en.pdf`) e **conferma
   del conteggio pagine** dell'interno (atteso 164): se ≠ 164, ricalcolare il dorso e ri-renderizzare la cover.

> **Già fatto in Claude Code (non serve rifarlo):** EPUB EN con copertina EN; copertina print EN
> (`cover_finale_en.pdf`, dorso 164 pp) renderizzata da `cover_final_en.typ` (Typst, NIENTE gs);
> immagine ebook EN (`ebook_cover_16_en.jpg`, sottotitolo EN + THIRD EDITION).

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

## 2) Copertina EN — GIÀ RENDERIZZATA (solo preflight + conferma dorso)
- **Print integrale:** `copertina/cover_finale_en.pdf` (renderizzata da `copertina/sorgenti/cover_final_en.typ`
  con Typst, nessun ghostscript). Testo tradotto (sottotitolo **The miniCMS protocol for modern web apps**,
  **THIRD EDITION**, retro **THE MINICMS PROTOCOL** + blurb EN; glossario: two **layers**, three **rungs**, **scars**).
- **Dorso ricalcolato per 164 pp**: `spine = 164 × 0,0572 = 9,38 mm` (IT 9,15), `W = 371,33 mm`, `front0 = 190,355 mm`.
  → **Cowork:** conferma che build_book_en.py riporta **164 pp**; se diverso, aggiorna `spine`/`W`/`front0` in
  `cover_final_en.typ` e ri-renderizza. Poi **preflight KDP** (bleed, dorso, area codice a barre).
- **Immagine ebook EN:** `copertina/ebook_cover_16_en.jpg` (ritaglio del pannello fronte, 1611×2301, ratio 1.428).
  Se vuoi parità col listing IT (ratio 1.6) puoi ricomporla, ma è già valida.

## 3) EPUB EN — GIÀ BUILDATO con cover EN
- `ebook/React-PHP-The-Thin-Stack-EN.epub` usa già `ebook_cover_16_en.jpg`. Per ri-buildare:
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
