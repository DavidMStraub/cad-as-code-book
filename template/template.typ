[-IMPORTS-]

// Colours
#let accent      = rgb("[-options.accent_color-]")
#let bg-note     = rgb("#eff6ff")
#let bg-warn     = rgb("#fff7ed")
#let bg-tip      = rgb("#eff6ff")
#let bg-aside    = rgb("#f5f0ff")
#let border-note = rgb("#3b82f6")
#let border-warn = rgb("#f97316")
#let border-tip  = rgb("#3b82f6")
#let border-aside= rgb("#8b5cf6")
#let code-bg     = rgb("#fafafa")
#let code-fg     = rgb("#1e1e2e")

// Fonts
#let body-font = ("Linux Libertine O",)
#let mono-font = ("Fira Code", "IBM Plex Mono")
#let sans-font = ("IBM Plex Sans")

// Parts
// A part divider is a level-1 heading carrying the label <part>. The heading
// show rule renders it as a divider page; the running header and the chapter
// counter ignore it (numbering: none does not step the heading counter).
// Chapter files invoke this via a raw-typst block: #part[Title]
#let part-counter = counter("part")
#let part(title) = {
  part-counter.step()
  // Part headings are marked via their supplement field (attaching a label
  // would need bracket-hash markup, which jtex misparses as a template tag).
  heading(level: 1, numbering: none, outlined: true, supplement: [part], title)
}
// NB: chapter files are typst #include-s and cannot see template definitions.
// Raw-typst blocks in markdown must therefore use built-ins only; see
// chapters/part-1.md and chapters/preface.md for the patterns.

// Document metadata
#set document(title: "[-options.book_title-]")

// Page layout
#set page(
  paper: "[-options.paper-]",
  margin: (top: 2.5cm, bottom: 3cm, inside: 2.5cm, outside: 2.5cm),
  binding: left,
  header: context {
    let page-num = counter(page).get().first()
    [
      #set text(font: sans-font, size: 0.85em, fill: luma(60))
      #if calc.odd(page-num) [
        #h(1fr) #smallcaps[[-options.book_title-]] #h(6pt) #page-num
      ] else {
        let chapters = query(heading.where(level: 1).before(here()))
          .filter(h => h.at("supplement", default: auto) != [part])
        let chapter-title = if chapters.len() > 0 { chapters.last().body } else []
        counter(page).display()
        h(6pt)
        smallcaps(chapter-title)
        h(1fr)
      }
      #v(-4pt)
      #line(length: 100%, stroke: 0.3pt + luma(100))
    ]
  },
  footer: [],
)

// Typography
#set text(font: body-font, size: [-options.font_size-], lang: "en")
#set par(justify: true, leading: 0.75em, first-line-indent: 0em)
#set heading(numbering: "1.1.1.")

// Callout base
#let callout(icon: "ℹ", bg: bg-note, border: border-note, title: none, body) = block(
  width: 100%,
  fill: bg,
  stroke: (left: 3pt + border),
  inset: (left: 12pt, right: 10pt, top: 8pt, bottom: 8pt),
  radius: (right: 4pt),
  {
    if title != none {
      text(weight: "bold", fill: border, size: 0.9em, { icon; " "; title })
      v(4pt)
    }
    body
  },
)

// Admonition functions — named {kind}Block to match mystmd's Typst emitter
#let noteBlock(body, heading: [Note])         = callout(icon: "ℹ", bg: bg-note,  border: border-note, title: heading, body)
#let tipBlock(body, heading: [Tip])           = callout(icon: "✓", bg: bg-tip,   border: border-tip,  title: heading, body)
#let warningBlock(body, heading: [Warning])   = callout(icon: "⚠", bg: bg-warn,  border: border-warn, title: heading, body)
#let cautionBlock(body, heading: [Caution])   = callout(icon: "⚠", bg: bg-warn,  border: border-warn, title: heading, body)
#let dangerBlock(body, heading: [Danger])     = callout(icon: "🛑", bg: bg-warn,  border: rgb("#ef4444"), title: heading, body)
#let importantBlock(body, heading: [Important]) = callout(icon: "★", bg: bg-note, border: border-note, title: heading, body)
#let hintBlock(body, heading: [Hint])         = callout(icon: "✓", bg: bg-tip,   border: border-tip,  title: heading, body)
#let attentionBlock(body, heading: [Attention]) = callout(icon: "⚠", bg: bg-warn, border: border-warn, title: heading, body)
#let errorBlock(body, heading: [Error])       = callout(icon: "✗", bg: bg-warn,  border: rgb("#ef4444"), title: heading, body)
#let seealsoBlock(body, heading: [See Also])  = callout(icon: "→", bg: bg-note,  border: border-note, title: heading, body)

// Aside (margin note rendered inline for print)
#let aside(title, body) = callout(icon: "→", bg: bg-aside, border: border-aside, title: title, body)

// Heading hierarchy
#show heading: it => { set par(first-line-indent: 0em); it }

#show heading.where(level: 1): it => {
  if it.at("supplement", default: auto) == [part] {
    // Part divider page
    pagebreak(weak: true, to: "odd")
    page(header: none, footer: none)[
      #v(2fr)
      #text(font: sans-font, size: 1.2em, fill: accent, weight: 450, tracking: 3pt)[
        PART #part-counter.display("I")
      ]
      #v(0.5cm)
      #text(font: sans-font, size: 2.6em, weight: "bold", fill: luma(30), it.body)
      #v(0.5cm)
      #line(length: 30%, stroke: 1.5pt + accent)
      #v(3fr)
    ]
  } else {
    pagebreak(weak: true)
    v(2cm)
    if it.numbering != none {
      text(font: sans-font, size: 1em, fill: accent, weight: 450, {
        "CHAPTER "
        counter(heading).display("1")
      })
      v(4pt)
    }
    text(font: sans-font, size: 2.0em, weight: "semibold", fill: accent, it.body)
    v(0.4cm)
    line(length: 100%, stroke: 0.5pt + accent)
    v(0.6cm)
  }
}

#show heading.where(level: 2): it => {
  set par(first-line-indent: 0em)
  v(1.4em)
  text(font: sans-font, size: 1.5em, weight: "semibold", fill: accent, {
    counter(heading).display("1.1")
    h(0.5em)
    it.body
  })
  v(0.3em)
}

#show heading.where(level: 3): it => {
  set par(first-line-indent: 0em)
  v(1em)
  text(font: sans-font, size: 1.2em, weight: "medium", fill: accent, it.body)
  v(0.2em)
}

#show heading.where(level: 4): it => {
  set par(first-line-indent: 0em)
  v(0.7em)
  text(font: sans-font, size: 1em, weight: "regular", style: "italic", it.body)
  v(0.15em)
}

// Code blocks
// Ligatures off: Fira Code fuses "->", "!=", etc. into single glyphs via
// contextual alternates, which misrepresents the actual characters in
// printed code — readers transcribing code should see literal "->".
#show raw.where(block: true): it => block(
  width: 100%,
  fill: code-bg,
  stroke: 0.5pt + rgb("#d0d0d8"),
  radius: 6pt,
  inset: 14pt,
  text(font: mono-font, size: 0.82em, fill: code-fg, ligatures: false,
    features: ("calt": 0, "liga": 0), it),
)
#show raw.where(block: false): it => box(
  fill: rgb("#ebebf0"),
  inset: (x: 1pt, y: 2pt),
  radius: 2pt,
  text(font: mono-font, size: 0.87em, fill: code-fg, ligatures: false,
    features: ("calt": 0, "liga": 0), it),
)

// Figure captions
#show figure.caption: it => text(size: 0.87em, style: "italic", it)

// Title page
#page(
  margin: (top: 3cm, bottom: 3cm, left: 3.5cm, right: 3.5cm),
  header: [],
  footer: [],
)[
  #v(3fr)
  #text(font: sans-font, size: 3em, weight: "bold", fill: accent)[[-options.book_title-]]
  #v(0.5cm)
  [# if options.book_subtitle #]
  #text(font: sans-font, size: 1.4em, fill: luma(60))[[-options.book_subtitle-]]
  #v(0.8cm)
  [# endif #]
  #line(length: 100%, stroke: 1pt + accent)
  #v(0.8cm)
  #text(font: sans-font, size: 1.1em)[
    [# for author in doc.authors #][-author.name-][# if not loop.last #] · [# endif #][# endfor #]
  ]
  [# if options.edition #]
  #v(0.4cm)
  #text(font: sans-font, size: 0.9em, fill: luma(120))[[-options.edition-]]
  [# endif #]
  #v(1fr)
]

// Copyright / imprint page
#page(
  margin: (top: 3cm, bottom: 3cm, left: 3.5cm, right: 3.5cm),
  header: [],
  footer: [],
)[
  #v(1fr)
  #set text(size: 0.85em, fill: luma(50))
  Copyright © [-options.year-] [# for author in doc.authors #][# if loop.first #][-author.name-][# endif #][# endfor #]

  #v(0.8em)
  #image("cc-by.svg", height: 2.5em)
  #v(0.4em)
  [-options.book_license-]

  #v(1.5em)
  [# if options.publisher #]
  Published by [-options.publisher-] \
  [# endif #]
  [# if options.edition #]
  [-options.edition-] edition \
  [# endif #]
  [# if options.isbn #]
  ISBN [-options.isbn-] \
  [# endif #]
  [# if doc.doi #]
  DOI #link("https://doi.org/[-doc.doi-]")[https://doi.org/[-doc.doi-]] \
  [# endif #]
  [# if options.urn #]
  URN #link("https://nbn-resolving.org/[-options.urn-]")[[-options.urn-]]
  [# endif #]
]

// Table of contents
#page(header: [], footer: [])[
  #text(font: sans-font, size: 2em, weight: "bold")[Contents]
  #v(1.5em)
  #show outline.entry.where(level: 1): it => {
    if it.element.at("supplement", default: auto) == [part] {
      v(1.6em, weak: true)
      text(font: sans-font, weight: "bold", fill: accent, size: 1.05em,
        smallcaps(it.element.body))
      v(0.4em, weak: true)
    } else {
      v(1em, weak: true)
      strong(it)
    }
  }
  #outline(
    title: none,
    indent: auto,
    depth: 2,
  )
]

#counter(page).update(1)

[-CONTENT-]
