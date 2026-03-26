#!/bin/bash
# Build script: React + PHP: The Thin Stack — Prima Edizione

PANDOC="/c/Users/Utente/AppData/Local/Microsoft/WinGet/Packages/JohnMacFarlane.Pandoc_Microsoft.Winget.Source_8wekyb3d8bbwe/pandoc-3.9.0.1/pandoc.exe"
XELATEX="/c/Users/Utente/AppData/Local/Programs/MiKTeX/miktex/bin/x64/xelatex.exe"
DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT="$DIR/React-PHP-The-Thin-Stack.pdf"
MASTER="$DIR/_master.md"

# Helper: aggiunge un capitolo sostituendo --- con \newpage per evitare parse YAML
append_chapter() {
  local file="$1"
  sed 's/^---$/\\newpage/' "$file" >> "$MASTER"
  printf '\n\n' >> "$MASTER"
}

# Crea il file master con frontmatter YAML
cat > "$MASTER" << 'YAML'
---
title: "React + PHP: The Thin Stack"
subtitle: "Il protocollo miniCMS per Web App moderne"
author: "Simone Pizzi"
date: "Marzo 2026 — Prima Edizione"
lang: it
book: true
classoption: [oneside]
toc: true
toc-own-page: true
toc-depth: 2
colorlinks: true
linkcolor: teal
titlepage: true
titlepage-color: "1E293B"
titlepage-text-color: "FFFFFF"
titlepage-rule-color: "2DD4BF"
titlepage-rule-height: 4
footnotes-pretty: true
code-block-font-size: \footnotesize
...

YAML

# ---- PARTE I ----
printf '\n\\part{La Visione}\n\n' >> "$MASTER"
append_chapter "$DIR/CAPITOLO 1 - Manifesto.md"

# ---- PARTE II ----
printf '\n\\part{L'"'"'Architettura}\n\n' >> "$MASTER"
append_chapter "$DIR/CAPITOLO 2 - Architettura e Struttura Progetto.md"
append_chapter "$DIR/CAPITOLO 3 - Database Strategy.md"
append_chapter "$DIR/CAPITOLO 4 - Frontend Dependencies.md"

# ---- PARTE III ----
printf '\n\\part{I Componenti}\n\n' >> "$MASTER"
append_chapter "$DIR/CAPITOLO 5 - Backend Logic (PHP).md"
append_chapter "$DIR/CAPITOLO 6 - Frontend Bridge (API.ts).md"
append_chapter "$DIR/CAPITOLO 7 - Media & Optimization.md"
append_chapter "$DIR/CAPITOLO 8 - Advanced Content Editing & Media Integration.md"

# ---- PARTE IV ----
printf '\n\\part{Il Flusso Operativo}\n\n' >> "$MASTER"
append_chapter "$DIR/CAPITOLO 9 - Content Lifecycle.md"
append_chapter "$DIR/CAPITOLO 10 - Security & Auth.md"
append_chapter "$DIR/CAPITOLO 11 - SEO Pre-rendering con PHP Entry-Point.md"
append_chapter "$DIR/CAPITOLO 12 - RSS Feed & Syndication.md"
append_chapter "$DIR/CAPITOLO 13 - Newsletter & Email System.md"

# ---- PARTE V ----
printf '\n\\part{I Casi Reali}\n\n' >> "$MASTER"
append_chapter "$DIR/CAPITOLO 14 - Database Evolution - Da SQLite a MySQL.md"
append_chapter "$DIR/CAPITOLO 15 - Portfolio & Projects Module.md"
append_chapter "$DIR/CAPITOLO 16 - Festival Logic - Iscrizioni e Workflow Approvazione.md"
append_chapter "$DIR/CAPITOLO 17 - Festival Logic - Votazioni e Protezione Anti-Frode.md"
append_chapter "$DIR/CAPITOLO 18 - Festival Logic - Dashboard Admin, Settings e Reporting.md"

# ---- ALLEGATI ----
printf '\n\\part{Allegati}\n\n' >> "$MASTER"
append_chapter "$DIR/BOILERPLATE-CHECKLIST.md"

echo "File master creato: $MASTER"

# Compila il PDF con Pandoc + xelatex
echo "Compilazione PDF in corso (la prima volta MiKTeX scarica i pacchetti, potrebbe richiedere alcuni minuti)..."
"$PANDOC" "$MASTER" \
  --output="$OUTPUT" \
  --from=markdown \
  --template=eisvogel \
  --pdf-engine="$XELATEX" \
  --top-level-division=chapter \
  --syntax-highlighting=tango \
  -V geometry:margin=2.5cm \
  2>&1

if [ -f "$OUTPUT" ]; then
  echo "PDF generato con successo: $OUTPUT"
  wc -c < "$OUTPUT" | awk '{printf "Dimensione: %.1f MB\n", $1/1048576}'
else
  echo "Compilazione fallita"
fi
