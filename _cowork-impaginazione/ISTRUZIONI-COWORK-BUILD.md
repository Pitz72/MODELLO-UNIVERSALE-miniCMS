# ISTRUZIONI PER COWORK — Build print-ready «The Thin Stack» (ristampa urgente)

> **Documento di handoff autosufficiente.** Lo legge una sessione **Claude Cowork** che non ha memoria
> della sessione Code in cui sono state fatte le correzioni. Qui dentro c'è tutto: dove pescare il
> materiale, come compilare, dove consegnare, come verificare.

## ⏱️ Perché è urgente
Il libro **è già stato mandato in stampa, ma con tre errori tecnici**. Sono stati corretti nel testo.
Serve **rigenerare l'interno PDF print-ready** (DeviceGray) e l'EPUB, e **rimandare in stampa l'interno**.
**Buona notizia:** le correzioni **non cambiano il numero di pagine** (resta **160 pp**, multiplo di 4) →
il **dorso e la copertina NON vanno rifatti**. Si ristampa solo l'interno.

## ✅ Cosa è cambiato (commit `0968314`)
Tre correzioni chirurgiche, già nei sorgenti `.md`:
1. **CAP 16** (`CAPITOLO 16 - Portfolio & Projects Module.md`): aggiunta una nota `[!NOTE]` «Una nota di
   dialetto» dopo lo schema SQL (lo schema è mostrato in dialetto SQLite ma SPW gira su MySQL).
2. **CAP 11 §7** (`CAPITOLO 11 - SEO Pre-rendering…md`): corretta la frase sui crawler social — al bot
   arriva **HTML generato a partire dai file JSON di cache**, non un payload JSON.
3. **CAP 20 §3** (`CAPITOLO 20 - Social Interactions & Reactions.md`): commento inline sul `substr(…,0,40)`.

## 📍 Dove trovare il materiale
**Repo Git (fonte unica):**
- Locale: `C:\Users\Utente\Documents\GitHub\SITI-WEB\MODELLO-UNIVERSALE-miniCMS`
- Remoto: `https://github.com/Pitz72/MODELLO-UNIVERSALE-miniCMS.git` — branch **`main`**
- **PRIMA DI TUTTO:** `git pull` e verifica di essere su `main` con il commit **`fc091bd`** o successivo
  (deve includere `0968314`, le correzioni). Comando di check: `git log --oneline -3`.

Struttura rilevante:
```
manuale/                       ← 23 .md: FONTE UNICA del testo (NON modificare per buildare)
fonts/IBM_Plex/                ← font OFL (IBM Plex Serif + Mono) usati dall'interno
_cowork-impaginazione/
├─ produzione/build_book.py    ← BUILD INTERNO (Typst → 2 passate → DeviceGray via ghostscript)
├─ produzione/template.typ     ← la gabbia Typst (7×10", B/N)
├─ produzione/alerts.lua       ← filtro pandoc per i box [!NOTE]/[!WARNING]/[!TIP]
├─ ebook/build_epub.py         ← BUILD EPUB (pandoc)
├─ copertina/cover_finale.pdf  ← copertina integrale KDP (INVARIATA, non rigenerare)
├─ copertina/ebook_cover_16.jpg← cover per l'EPUB
├─ master/                     ← qui build_book.py scrive l'interno DeviceGray finale
└─ GABBIA_TIPOGRAFICA.md       ← specifiche tipografiche
```

## 🔧 Ambiente e dipendenze
```bash
pip install typst pypandoc fonttools brotli pymupdf pypdf
# serve anche: pandoc (3.x) e ghostscript a PATH
```

> ### ⚠️ NOTA CRITICA — ghostscript / DeviceGray (il vero motivo di questo handoff)
> Lo step finale di `build_book.py` chiama **ghostscript** per convertire l'interno in **DeviceGray**
> (B/N pre-stampa). Su **Windows** (gs `gswin64c` 10.07.1) questo passo **segfaulta** (`0xC0000005`,
> crash a ~40% del file) con qualunque combinazione di flag, e **tronca il PDF** in scrittura. **È per
> questo che la finalizzazione va fatta qui in Cowork**, in un ambiente dove ghostscript gira (Linux).
> - Verifica che gs funzioni: `gs --version` deve rispondere e il comando di conversione (sotto) deve
>   uscire con **codice 0** producendo un PDF leggibile.
> - Se anche qui gs dovesse fallire: l'interno Typst è **già in scala di grigi** (solo `luma()`+nero,
>   zero immagini, zero RGB/CMYK), quindi `produzione/_interno_rgb.pdf` è stampabile B/N come ripiego,
>   ma **l'obiettivo è il DeviceGray formale**.
>
> Comando di conversione usato (per riferimento/diagnostica manuale):
> ```
> gs -q -dBATCH -dNOPAUSE -dSAFER -sDEVICE=pdfwrite \
>    -dProcessColorModel=/DeviceGray -dColorConversionStrategy=/Gray \
>    -dCompatibilityLevel=1.6 -dEmbedAllFonts=true -dSubsetFonts=true \
>    -dAutoRotatePages=/None -dDownsampleGrayImages=false \
>    -o master/Interno_The-Thin-Stack_3ed_7x10_BN.pdf produzione/_interno_rgb.pdf
> ```

## 🏗️ Come buildare
```bash
# 1) INTERNO cartaceo (DeviceGray, 160 pp)
cd _cowork-impaginazione/produzione
python build_book.py
#   → genera frammenti + libro.typ, compila 2 passate (folio + bianche multiplo di 4),
#     converte in DeviceGray e scrive: ../master/Interno_The-Thin-Stack_3ed_7x10_BN.pdf

# 2) EPUB
cd ../ebook
python build_epub.py
#   → scrive: React-PHP-The-Thin-Stack.epub  (con copertina ebook_cover_16.jpg)
```

## ✔️ Verifiche obbligatorie prima della consegna
- Interno: **160 pagine**, conteggio **multiplo di 4**, colorspace **DeviceGray**.
  Lo script stampa già: `Pagine: 160 | multiplo4: True | indice@… | ParteI@…=folio1`.
- Le **3 correzioni** sono presenti: cerca nel testo «nota di dialetto» (Cap 16),
  «generato a partire da file JSON» (Cap 11), il commento sul `substr` (Cap 20).
- **Copertina:** confermare che resta `copertina/cover_finale.pdf` **invariata** (160 pp → dorso uguale).

## 📦 Dove consegnare (cartella archivio pubblicati)
Copiare gli output finali in:
```
C:\Users\Utente\Documents\Claude\Projects\Progetto di Impaginazione Libri\Libri Archiviati\Pubblicati\The Thin Stack\
├─ master\Interno_The-Thin-Stack_3ed_7x10_BN.pdf   ← interno DeviceGray rigenerato (SOVRASCRIVERE)
├─ ebook\React-PHP-The-Thin-Stack.epub             ← EPUB rigenerato (SOVRASCRIVERE)
└─ cover\cover_finale.pdf                          ← INVARIATO (non toccare)
```
> Nota: il 27/06/2026 da Code ho già copiato lì un interno **in scala di grigi (non DeviceGray)** e
> l'EPUB aggiornato, come ripiego. **Sostituisci l'interno con il DeviceGray** appena buildato qui.

## 🚀 Pubblicazione KDP (ristampa)
- Caricare su KDP **solo il nuovo interno** (la copertina è identica: stesso conteggio pagine, stesso dorso).
- Regola d'oro prima di confermare: per una ristampa *con correzioni di testo a parità di impaginazione*
  la copia di prova fisica è raccomandata ma, vista l'urgenza, il check minimo è il **preflight KDP**
  (DeviceGray accettato, 160 pp, margini/gabbia 7×10" invariati).

---
*Materiale e toolchain: commit `fc091bd` del repo MODELLO-UNIVERSALE-miniCMS. Per dubbi sul perché di una
scelta di contenuto, le motivazioni delle 3 correzioni sono nel messaggio di commit `0968314`.*
