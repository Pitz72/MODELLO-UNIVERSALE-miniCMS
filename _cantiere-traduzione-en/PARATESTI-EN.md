# Paratexts — EN (US) edition

Tutti i testi di servizio (front matter + back matter) tradotti per l'edizione inglese. Oggi vivono come
**stringhe cablate** nello `STRUCT`/`write_libro()` di `_cowork-impaginazione/produzione/build_book.py` (interno
Typst) e in `_cowork-impaginazione/ebook/metadata.yaml` (EPUB), tutti in **italiano**. Questo file raccoglie le
versioni EN pronte da inserire nella **variante EN dello STRUCT** in fase di build (scope Cowork, ROADMAP §7).
Tipografia US, glossario applicato. La **dedica** è già tradotta dentro `manuale-en/CHAPTER 01 - Manifesto.md`
(il build la estrae dal Manifesto) → non serve ripeterla qui.

---

## 1. Frontispiece (p. 1)

- **Title:** React + PHP: The Thin Stack *(già inglese, invariato)*
- **Subtitle:** The miniCMS protocol for modern web apps
- **Author:** Simone Pizzi
- **Edition:** Third Edition
- **Publisher:** RUNTIME EDIZIONI *(nome proprio del marchio, invariato — §5)*

## 2. Colophon (p. 3)

```
React + PHP: The Thin Stack
The miniCMS protocol for modern web apps
Third Edition — June 2026

© 2026 Simone Pizzi
© 2026 Runtime Edizioni

All rights reserved. No part of this book may be reproduced without the written consent of the
publisher, except for brief quotations in reviews.

The trademarks and product names cited are the property of their respective owners.

www.runtimeradio.com
```

## 3. Dedication (p. 5)

> Già nel `CHAPTER 01 - Manifesto.md` (estratta in fase di build). Per riferimento, testo EN:
>
> *For Valerio Galano: because he’s like Neo, he sees worlds in code, and he taught me to think in a
> different way. I wonder whether I taught him a little something in return.*
>
> *For Giuseppe Pugliese who, even though he sees the world in his own particular way, takes pride in being
> a web developer and keeps at his craft with passion.*

## 4. Table of Contents

- Heading: **Contents** *(IT «Indice»)*

---

## 5. Part titles & descriptions (STRUCT)

| # | Title | Description |
|---|---|---|
| I | **The Vision** | The why. The philosophy that guides every technical decision. |
| II | **The Architecture** | The foundations. Project structure, database, technology stack. |
| III | **The Components** | The bricks. Backend, frontend, media, editor: the building blocks of the system. |
| IV | **The Operational Flow** | How content lives. From the lifecycle to distribution, by way of security and SEO. |
| V | **The Real-World Cases** | Where theory meets production. Patterns extracted from real projects, with their scars. |
| — | **Appendices** | Practical tools and edge cases. |

(Titoli di Parte già fissati nel glossario §1; le descrizioni sono nuove, tradotte qui.)

---

## 6. Author BIO (back matter — “The Author”)

Heading: **The Author** *(IT «L'autore»)*

> Simone Pizzi is an author and publisher. He founded Runtime Edizioni and Runtime Radio, for which he
> curates editorial, audio, and digital projects. He has published the short-story collection *L'Albero dei
> Racconti* (The Tree of Tales) and the science-fiction novella *Frequenza di Servizio* (Service Frequency).
>
> This manual grows out of real work on four production sites — SitoRuntime, DISINTELLIGENZA, FDCA, and
> SimonePizziWebSite — and gathers the “thin stack” protocol he built them with: React and TypeScript for the
> presentation, native PHP and SQLite or MySQL for the data, with no backend framework and no oversized
> infrastructure.

(Titoli dei libri nella BIO: italiano in corsivo + glossa EN, policy D3; glosse fissate nel glossario §2.)

---

## 7. EPUB metadata (`metadata.yaml`) — variante EN

```yaml
title: "React + PHP: The Thin Stack"
subtitle: "The miniCMS protocol for modern web apps"
creator:
  - role: author
    text: Simone Pizzi
publisher: "Runtime Edizioni"
language: en-US
date: "2026-06"
rights: "© 2026 Simone Pizzi / Runtime Edizioni — Third Edition"
```

---

## Note per il build EN (a valle, scope Cowork)
- Lo `STRUCT` di `build_book.py` referenzia i capitoli per **nome-file IT** (`CAPITOLO N - …`): la variante EN
  deve puntare ai file `manuale-en/CHAPTER NN - …` e `APPENDIX A/B/C - …`.
- `extract_dedica()` cerca il blocco `#quote` nel Manifesto: funziona identico sul `CHAPTER 01 - Manifesto.md`
  (la dedica EN è già un blockquote in testa al file).
- Stessa gabbia 7×10", stessi font IBM Plex. Colophon/folio invariati nella forma, solo testo EN.
- «Terza Edizione --- Giugno 2026» → «Third Edition — June 2026» (en/em-dash US, §3).
