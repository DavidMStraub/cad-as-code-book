[-IMPORTS-]

// Colours
#let accent      = rgb("[-options.accent_color-]")
#let bg-note     = rgb("#eff6ff")
#let bg-warn     = rgb("#fff7ed")
#let bg-tip      = rgb("#f0fdf4")
#let bg-aside    = rgb("#f5f0ff")
#let border-note = rgb("#3b82f6")
#let border-warn = rgb("#f97316")
#let border-tip  = rgb("#22c55e")
#let border-aside= rgb("#8b5cf6")
#let code-bg     = rgb("#f5f5f5")
#let code-fg     = rgb("#1e1e2e")

// Fonts
#let body-font = ("Linux Libertine O",)
#let mono-font = ("Fira Code", "IBM Plex Mono")
#let sans-font = ("Source Sans 3", "IBM Plex Sans", "Linux Biolinum O")

// Document metadata
#set document(title: "[-options.book_title-]")

// Page layout
#set page(
  paper: "[-options.paper-]",
  margin: (top: 2.5cm, bottom: 3cm, inside: 2.8cm, outside: 2.2cm),
  binding: left,
  header: context {
    let page-num = counter(page).get().first()
    if page-num > 2 [
      #set text(size: 0.78em, fill: luma(120))
      #if calc.odd(page-num) [
        #h(1fr) #smallcaps[[-options.book_title-]] #h(6pt) #page-num
      ] else [
        #page-num #h(6pt) #smallcaps[[# for author in doc.authors #][# if loop.first #][-author.name-][# endif #][# endfor #]] #h(1fr)
      ]
      #v(-4pt)
      #line(length: 100%, stroke: 0.3pt + luma(180))
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
  pagebreak(weak: true)
  v(2cm)
  if it.numbering != none {
    text(font: sans-font, size: 1em, fill: accent, weight: "bold", {
      "CHAPTER "
      counter(heading).display("1")
    })
    v(4pt)
  }
  text(font: sans-font, size: 2.2em, weight: "bold", it.body)
  v(0.4cm)
  line(length: 100%, stroke: 0.5pt + accent)
  v(0.6cm)
}

#show heading.where(level: 2): it => {
  set par(first-line-indent: 0em)
  v(1.4em)
  text(font: sans-font, size: 1.5em, weight: "semibold", fill: accent, it.body)
  v(0.3em)
}

#show heading.where(level: 3): it => {
  set par(first-line-indent: 0em)
  v(1em)
  text(font: sans-font, size: 1.2em, weight: "regular", it.body)
  v(0.2em)
}

#show heading.where(level: 4): it => {
  set par(first-line-indent: 0em)
  v(0.7em)
  text(font: sans-font, size: 1em, weight: "regular", style: "italic", it.body)
  v(0.15em)
}

// Code blocks
#show raw.where(block: true): it => block(
  width: 100%,
  fill: code-bg,
  stroke: 0.5pt + rgb("#d0d0d8"),
  radius: 6pt,
  inset: 14pt,
  text(font: mono-font, size: 0.82em, fill: code-fg, it),
)
#show raw.where(block: false): it => highlight(
  fill: rgb("#ebebf0"),
  top-edge: 0.7em,
  bottom-edge: -0.2em,
  radius: 2pt,
  text(font: mono-font, size: 0.87em, fill: code-fg, it),
)

// Figure captions
#show figure.caption: it => text(size: 0.87em, style: "italic", it)

// Title page
#page(
  margin: (top: 4cm, bottom: 3cm, left: 3.5cm, right: 3.5cm),
  header: [],
  footer: [],
)[
  #v(2fr)
  #align(center)[
    #text(font: sans-font, size: 3em, weight: "black", fill: accent)[[-options.book_title-]]
    #v(0.4cm)
    [# if options.book_subtitle #]
    #text(font: sans-font, size: 1.5em, fill: luma(60))[[-options.book_subtitle-]]
    #v(1.2cm)
    [# endif #]
    #line(length: 40%, stroke: 1.5pt + accent)
    #v(1.2cm)
    #text(font: sans-font, size: 1.2em)[
      [# for author in doc.authors #][-author.name-][# if not loop.last #], [# endif #][# endfor #]
    ]
    [# if options.edition #]
    #v(0.3cm)
    #text(font: sans-font, size: 0.9em, fill: luma(100))[[-options.edition-]]
    [# endif #]
  ]
  #v(3fr)
  #align(center)[
    #text(size: 0.82em, fill: luma(120))[
      [# if options.publisher #][-options.publisher-] · [# endif #][-options.year-] \
      [# if options.isbn #]ISBN [-options.isbn-] \ [# endif #]
      [# if doc.doi #]DOI [-doc.doi-] \ [# endif #]
      [# if options.urn #]URN [-options.urn-][# endif #]
    ]
  ]
]

// Table of contents
#page(header: [], footer: [])[
  #text(font: sans-font, size: 2em, weight: "bold")[Contents]
  #v(1.5em)
  #show outline.entry.where(level: 1): it => {
    v(1em, weak: true)
    strong(it)
  }
  #outline(
    title: none,
    indent: auto,
    depth: 2,
  )
]

#counter(page).update(1)

= [-doc.title-]

[-CONTENT-]
