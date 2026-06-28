// FULL KDP COVER — "React + PHP: The Thin Stack" (EN, US edition)
// EN variant of cover_final.typ. Translated copy + geometry recomputed for the EN page count.
//
// ⚠️ SPINE / GEOMETRY: the EN interior is 164 pp (vs IT 160). KDP B/W white paper = 0.0572 mm/page.
//    spine = 164 * 0.0572 = 9.38 mm  (IT was 9.15 mm for 160 pp)
//    page width W = bleed(3.175) + trim(177.8) + spine(9.38) + trim(177.8) + bleed(3.175) = 371.33 mm
//    front0 = bleed(3.175) + back(177.8) + spine(9.38) = 190.355 mm
//    → Cowork: re-confirm the page count printed by build_book_en.py and adjust SPINE if it differs.
#set page(width: 371.33mm, height: 260.35mm, margin: 0pt)
#set text(fill: rgb("#eef3f8"))

// background: upscaled image, fills the whole cover (centered crop)
#place(top + left, image("bg_fit.png", width: 371.33mm, height: 260.35mm))

#let TEAL = rgb("#2DD4BF")
#let GRAY = rgb("#9fb3c8")
#let front0 = 190.355mm
#let TRIMW  = 177.8mm

// ---------- FRONT (right) ----------
#place(top + left, dx: front0, dy: 36mm, box(width: TRIMW)[#align(center)[
  #text(font: "IBM Plex Mono", size: 9pt, fill: TEAL, tracking: 3pt)[RUNTIME EDIZIONI]
]])
#place(top + left, dx: front0, dy: 50mm, box(width: TRIMW)[#align(center)[
  #text(font: "IBM Plex Serif", size: 23pt, weight: "semibold")[React + PHP:]
]])
#place(top + left, dx: front0, dy: 62mm, box(width: TRIMW)[#align(center)[
  #text(font: "IBM Plex Serif", size: 36pt, weight: "semibold")[The Thin Stack]
]])
#place(top + left, dx: front0, dy: 86mm, box(width: TRIMW)[#align(center)[
  #text(font: "IBM Plex Mono", size: 9.5pt, fill: GRAY)[The miniCMS protocol for modern web apps]
]])
#place(top + left, dx: front0, dy: 233mm, box(width: TRIMW)[#align(center)[
  #text(font: "IBM Plex Serif", size: 17pt, weight: "medium")[Simone Pizzi]
]])
#place(top + left, dx: front0, dy: 244mm, box(width: TRIMW)[#align(center)[
  #text(font: "IBM Plex Mono", size: 8.5pt, fill: GRAY, tracking: 1.5pt)[THIRD EDITION]
]])

// ---------- SPINE (page center) ----------
#place(center + horizon, rotate(90deg)[
  #text(font: "IBM Plex Serif", size: 9pt, weight: "semibold")[Simone Pizzi]
  #h(6pt) #text(font: "IBM Plex Mono", size: 8pt, fill: TEAL)[·] #h(6pt)
  #text(font: "IBM Plex Serif", size: 9pt)[The Thin Stack]
])

// ---------- BACK (left) ----------
#let bx = 13mm
#place(top + left, dx: bx, dy: 38mm,
  text(font: "IBM Plex Mono", size: 9pt, fill: TEAL, tracking: 2.5pt)[THE MINICMS PROTOCOL])
#place(top + left, dx: bx, dy: 50mm, box(width: 150mm)[
  #set par(leading: 0.7em, justify: false)
  #set text(font: "IBM Plex Serif", size: 11pt, fill: rgb("#d4dfea"))
  The frontend has become magnificent. But underneath we pile on too much: Node, containers, subscription CMSs, cloud services, for sites that would run perfectly well on a few-euros-a-month host.

  "The Thin Stack" is the protocol that separates two layers: presentation in React and TypeScript, data in native PHP and SQLite (or MySQL when needed). No backend framework, no overhead: a minimal but real skeleton that scales across three rungs depending on what you need.

  Twenty chapters and three appendices built on four real production sites: hand-rolled security, SEO that works, feeds, newsletters, dashboards, and all the scars of someone who actually put it online.
])
#place(top + left, dx: bx, dy: 243mm,
  text(font: "IBM Plex Mono", size: 9pt, weight: "medium", tracking: 2pt)[RUNTIME EDIZIONI])
#place(top + left, dx: bx, dy: 248mm,
  text(font: "IBM Plex Mono", size: 7.5pt, fill: GRAY)[www.runtimeradio.com])

// KDP barcode area (reserved, bottom-right of the back)
#place(top + left, dx: 125mm, dy: 218mm,
  rect(width: 47mm, height: 30mm, radius: 1.5pt, fill: white.transparentize(8%))[
    #align(center + horizon)[#text(font: "IBM Plex Mono", size: 7pt, fill: rgb("#7a8aa0"))[barcode area]]
  ])
