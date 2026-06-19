#set page(width: 371.1mm, height: 260.35mm, margin: 0pt)
#set text(fill: rgb("#eef3f8"))

// sfondo: immagine upscalata, riempie tutta la copertina (crop centrato)
#place(top + left, image("bg_fit.png", width: 371.1mm, height: 260.35mm))

#let TEAL = rgb("#2DD4BF")
#let GRAY = rgb("#9fb3c8")
#let front0 = 190.125mm
#let TRIMW  = 177.8mm

// ---------- FRONTE (destra) ----------
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
  #text(font: "IBM Plex Mono", size: 9.5pt, fill: GRAY)[Il protocollo miniCMS per Web App moderne]
]])
#place(top + left, dx: front0, dy: 233mm, box(width: TRIMW)[#align(center)[
  #text(font: "IBM Plex Serif", size: 17pt, weight: "medium")[Simone Pizzi]
]])
#place(top + left, dx: front0, dy: 244mm, box(width: TRIMW)[#align(center)[
  #text(font: "IBM Plex Mono", size: 8.5pt, fill: GRAY, tracking: 1.5pt)[TERZA EDIZIONE]
]])

// ---------- DORSO (centro pagina) ----------
#place(center + horizon, rotate(90deg)[
  #text(font: "IBM Plex Serif", size: 9pt, weight: "semibold")[Simone Pizzi]
  #h(6pt) #text(font: "IBM Plex Mono", size: 8pt, fill: TEAL)[·] #h(6pt)
  #text(font: "IBM Plex Serif", size: 9pt)[The Thin Stack]
])

// ---------- RETRO (sinistra) ----------
#let bx = 13mm
#place(top + left, dx: bx, dy: 38mm,
  text(font: "IBM Plex Mono", size: 9pt, fill: TEAL, tracking: 2.5pt)[IL PROTOCOLLO MINICMS])
#place(top + left, dx: bx, dy: 50mm, box(width: 150mm)[
  #set par(leading: 0.7em, justify: false)
  #set text(font: "IBM Plex Serif", size: 11pt, fill: rgb("#d4dfea"))
  Il frontend è diventato magnifico. Ma sotto ci mettiamo troppo: Node, container, CMS in abbonamento, servizi cloud, per siti che girerebbero benissimo su un hosting da pochi euro.

  «The Thin Stack» è il protocollo che separa due piani: la presentazione a React e TypeScript, i dati a PHP nativo e SQLite (o MySQL quando serve). Niente framework di backend, niente overhead: uno scheletro minimo ma vero, che scala su tre gradini a seconda di ciò che ti serve.

  Venti capitoli e tre appendici costruiti su quattro siti reali in produzione: sicurezza fatta a mano, SEO che funziona, feed, newsletter, dashboard, e tutte le cicatrici di chi l'ha messo online sul serio.
])
#place(top + left, dx: bx, dy: 243mm,
  text(font: "IBM Plex Mono", size: 9pt, weight: "medium", tracking: 2pt)[RUNTIME EDIZIONI])
#place(top + left, dx: bx, dy: 248mm,
  text(font: "IBM Plex Mono", size: 7.5pt, fill: GRAY)[www.runtimeradio.com])

// area codice a barre KDP (riservata, basso-destra del retro)
#place(top + left, dx: 125mm, dy: 218mm,
  rect(width: 47mm, height: 30mm, radius: 1.5pt, fill: white.transparentize(8%))[
    #align(center + horizon)[#text(font: "IBM Plex Mono", size: 7pt, fill: rgb("#7a8aa0"))[area codice a barre]]
  ])
