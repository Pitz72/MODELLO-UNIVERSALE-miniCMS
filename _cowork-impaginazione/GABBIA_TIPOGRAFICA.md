# GABBIA TIPOGRAFICA — "React + PHP: The Thin Stack" (3ª Edizione)

Specifiche di impaginazione per la stampa POD (Amazon KDP). Engine: **Typst**.
Questo file è il ponte verso Claude Code: le decisioni vivono qui, nel repo.

## Decisioni di gabbia (fissate con Simone, 2026-06-19)
- **Formato (trim):** 7 × 10 pollici = 177,8 × 254 mm. Standard KDP per manuali informatici.
- **Interno:** bianco e nero. Conversione finale in DeviceGray (Grey Gamma 2.2) come passo pre-stampa.
- **Margini speculari (mirror, rilegatura a sinistra):** interno 20 / esterno 16 / top 18 / bottom 20 mm.
  (KDP per 151–300 pp a 7×10 chiede gutter ≥ 0,625" ≈ 15,9 mm e esterno ≥ 6,35 mm: rispettati.)
- **Font corpo:** IBM Plex Serif 10 pt, interlinea ~14 pt (par leading 0.72em). Non Garamond:
  scelta "da manuale informatico" approvata da Simone.
- **Font codice:** IBM Plex Mono 8,5 pt. Blocchi su fondo grigio chiaro (luma 238).
- **Righe di codice lunghe:** a-capo automatico a 76 colonne con marker di continuazione **↪**
  (niente font minuscolo, per l'ipovisione di Simone). Implementato come show-rule in `template.typ`.
- **Admonition** (GitHub alerts → box B/N): barra verticale a sinistra + etichetta IT
  (ATTENZIONE / CAUTELA / IMPORTANTE / NOTA / CONSIGLIO), nessun colore.
- **Numerazione:** paratesto romano (l'indice mostra i,ii,…), corpo arabo da 1; folio centrato in basso.
- **Apertura Parti:** sempre su pagina dispari, con sottotitolo/descrizione (dalle intro di Parte del README).
- **Apertura capitoli:** sempre a pagina nuova, NON per forza dispari (scelta di Simone).
- **Pagine totali = multiplo di 4** (brossura): padding di pagine bianche in coda.

## Ordine del paratesto (indicazione di Simone)
1. p.1 Frontespizio (titolo, sottotitolo, autore, "Terza Edizione", Runtime Edizioni)
2. p.2 bianca
3. p.3 Colophon (© 2026 Simone Pizzi / Runtime Edizioni, Terza Edizione, Giugno 2026)
4. p.4 bianca
5. p.5 Dedica (corsivo, allineata a destra) — testo spostato dall'epigrafe del CAP 1
6. p.6 bianca
7. Indice (subito dopo la dedica, folio romano)
8. Corpo: Parti (pagina dispari) + 20 capitoli + 3 appendici (A Boilerplate, B Fork, C Testing&Deploy)
9. Bio autore ("L'autore") in fondo
10. Pagine bianche fino al multiplo di 4

## Struttura cartella e toolchain
- `master/` — **solo il PDF di pubblicazione** (`Interno_The-Thin-Stack_3ed_7x10_BN.pdf`).
- `produzione/` — tutto il lavoro:
  - `template.typ` — la gabbia (page, font, show-rule wrap codice, admonition, parti, indice, heading).
  - `alerts.lua` — filtro pandoc: GitHub alerts → `#admonition(...)`.
  - `build_book.py` — `.md` → frammenti → `libro.typ` → master PDF; estrae la dedica dal CAP 1,
    calcola da solo le pagine bianche (multiplo di 4) e compila.
  - `capitoli-typ/` — frammenti Typst (generati); `libro.typ` — assemblato (generato); `prototipi/` — prove.
- `../fonts/IBM_Plex/` — i .ttf (OFL), condivisi, usati da Typst via `--font-path`.

### Build (sandbox Cowork)
```
pip install typst pypandoc_binary fonttools brotli pymupdf pypdf --break-system-packages
cd produzione
python3 build_book.py     # rigenera tutto e compila ../master/Interno_...pdf
```

### Gotcha noti
- **FUSE incoerente in Cowork:** i file letti da Typst (es. `template.typ`) vanno scritti **da bash**,
  non con lo strumento Write (la vista FUSE arriva troncata → "unclosed delimiter").
- Gli `#include` di Typst NON ereditano gli import → ogni frammento è prefissato con
  `#import "../template.typ": admonition, horizontalrule`.
- I glifi speciali (checkbox ☐, frecce →, box-drawing dei diagrammi, emoji) non sono in IBM Plex:
  Typst usa il fallback DejaVu, embedded. Corretto e voluto.

## Stato (2026-06-19)
Interno **print-ready**: **160 pp**, multiplo di 4, formato 504×720 pt, font tutti embedded,
**DeviceGray verificato** (0 DeviceRGB, scarto canali ≤1 = solo antialiasing). Numerazione: indice
romano, corpo arabo **da 1 sulla Parte I**, **nessun folio sulle bianche**. Dedica e bio confermate.
`build_book.py` esegue tutto: Typst → intermedio RGB → Ghostscript DeviceGray → `master/`.
✅ **Completati anche copertina** (dorso su 160 pp + carta KDP), **eBook** e copia di prova: l'edizione
italiana è **pubblicata su KDP e in distribuzione**. La stessa gabbia è stata riusata per l'**edizione
inglese** (`template_en.typ`, interno di **164 pp** → dorso 9,38 mm), anch'essa pubblicata.
