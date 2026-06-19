# Impaginazione KDP — interno del manuale

Composizione tipografica print-ready dell'**interno** di
«React + PHP: The Thin Stack» (3ª edizione) per Amazon KDP. Engine: **Typst**.
Le specifiche di gabbia stanno in `GABBIA_TIPOGRAFICA.md`.

## Struttura della cartella

```
_cowork-impaginazione/
├─ GABBIA_TIPOGRAFICA.md     # specifiche tipografiche (decisioni)
├─ master/                   # >>> MASTER DI PUBBLICAZIONE <<<
│  └─ Interno_The-Thin-Stack_3ed_7x10_BN.pdf
└─ produzione/               # tutto il lavoro (toolchain + intermedi)
   ├─ template.typ           # la gabbia Typst
   ├─ alerts.lua             # filtro pandoc: GitHub alerts -> #admonition
   ├─ build_book.py          # build: .md -> frammenti -> libro.typ -> master PDF
   ├─ libro.typ              # assemblato (generato)
   ├─ capitoli-typ/          # frammenti Typst dei capitoli (generati)
   └─ prototipi/             # prove di impaginazione (scartabili)
```

- **`master/`** contiene SOLO il PDF finale, quello che si carica su KDP.
- **`produzione/`** contiene la toolchain e i file intermedi. Tutto ciò che è
  generato (`libro.typ`, `capitoli-typ/`) si ricrea con un comando.

## Come si ricostruisce il master

I `.md` in `../manuale/` sono la fonte unica; non si toccano qui.

```bash
pip install typst pypandoc_binary fonttools brotli pymupdf pypdf --break-system-packages
cd produzione
python3 build_book.py     # genera frammenti + libro.typ, calcola le bianche
                          # (multiplo di 4) e compila ../master/...pdf
```

Font in `../fonts/IBM_Plex/` (OFL): IBM Plex Serif (corpo) + IBM Plex Mono (codice).

## Da fare prima della pubblicazione
- Conversione finale **DeviceGray** (Grey Gamma 2.2) del master.
- **Copertina** integrale (dorso su 160 pp + carta KDP).
- **eBook**.
- **Copia di prova fisica** (regola assoluta) prima di pubblicare.
