// =====================================================================
// GABBIA TIPOGRAFICA — "React + PHP: The Thin Stack" (3a ed.)
// Manuale tecnico, KDP 7x10", B/N. Engine: Typst. v0.2
//   liv.1 = Parte (heading nascosto, solo indice)
//   liv.2 = Capitolo   liv.3 = sezione   liv.4 = sottosezione
// =====================================================================

#let horizontalrule = align(center)[#v(0.2em) #text(fill: luma(150))[\u{2042}] #v(0.2em)]

#let admonition(kind, body) = {
  let labels = (
    warning: "ATTENZIONE", caution: "CAUTELA", important: "IMPORTANTE",
    note: "NOTA", tip: "CONSIGLIO",
  )
  let lab = labels.at(kind, default: upper(kind))
  block(
    width: 100%, fill: luma(243),
    stroke: (left: 2.5pt + luma(110)),
    inset: (left: 10pt, rest: 8pt), radius: (top-right: 2pt, bottom-right: 2pt),
    above: 1em, below: 1em, breakable: true,
  )[
    #text(font: "IBM Plex Mono", weight: "bold", size: 8pt, tracking: 0.6pt)[#lab]
    #v(0.25em, weak: true)
    #body
  ]
}

#let part(num, title, desc) = {
  pagebreak(to: "odd")
  place(top, hide[#heading(level: 1, outlined: true, numbering: none)[#title]])
  align(center + horizon)[
    #if num != none [#text(size: 12pt, tracking: 3pt, fill: luma(90))[PARTE #num] #v(0.8em)]
    #text(size: 26pt, weight: "semibold")[#title]
    #v(1.2em)
    #line(length: 30%, stroke: 0.6pt + luma(160))
    #v(1.2em)
    #block(width: 72%)[#text(size: 11pt, style: "italic", fill: luma(60))[#desc]]
  ]
}

#let conf(doc) = {
  set page(
    width: 177.8mm, height: 254mm,
    margin: (inside: 20mm, outside: 16mm, top: 18mm, bottom: 20mm),
    binding: left,
  )
  set text(font: "IBM Plex Serif", size: 10pt, lang: "it", hyphenate: true)
  set par(justify: true, leading: 0.72em, spacing: 1.05em)

  show raw.where(block: false): it => text(font: "IBM Plex Mono", size: 0.9em, fill: luma(20))[#it]

  show raw.where(block: true): it => {
    let cols = 76
    let out = ()
    for line in it.text.split("\n") {
      let chars = line.clusters()
      if chars.len() <= cols {
        out.push(line)
      } else {
        let i = 0
        let first = true
        while i < chars.len() {
          let chunk = chars.slice(i, calc.min(i + cols, chars.len())).join()
          if first { out.push(chunk); first = false } else { out.push("\u{21AA} " + chunk) }
          i += cols
        }
      }
    }
    block(
      width: 100%, fill: luma(238), inset: (x: 7pt, y: 6pt), radius: 2pt,
      breakable: true, above: 1em, below: 1em,
    )[#text(font: "IBM Plex Mono", size: 8.5pt)[#raw(out.join("\n"))]]
  }

  set table(stroke: 0.5pt + luma(170), inset: 5pt)
  show table.cell.where(y: 0): set text(weight: "bold", size: 9pt)
  show table: set text(size: 9pt)

  show heading.where(level: 2): it => {
    pagebreak(weak: true)
    v(2.0cm)
    block(below: 1.1em)[#text(weight: "semibold", size: 21pt)[#it.body]]
    line(length: 100%, stroke: 0.6pt + luma(160))
    v(0.6em)
  }
  show heading.where(level: 3): it => {
    v(1.0em)
    block(below: 0.45em)[#text(weight: "semibold", size: 13.5pt)[#it.body]]
  }
  show heading.where(level: 4): it => {
    v(0.6em)
    block(below: 0.25em)[#text(weight: "bold", size: 11pt)[#it.body]]
  }

  doc
}
