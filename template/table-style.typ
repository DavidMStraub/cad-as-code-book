// Table styling, imported per-chapter (see chapters/ch09-... for the
// one-line raw:typst pattern to copy). Can't live in template.typ: each
// chapter compiles as its own #include, which re-imports myst-imports.typ's
// plain tableStyle = (:) default fresh, shadowing anything set there.
//
// Thin horizontal rules only, no vertical lines, a slightly heavier rule
// under the header row - a plain "booktabs" look instead of tablex's
// boxed-grid default.
#let tableStyle = (
  auto-vlines: false,
  stroke: 0.5pt + luma(150),
  inset: (x: 8pt, y: 6pt),
  map-hlines: hline => if hline.y <= 1 { hline + (stroke: 0.8pt + luma(70)) } else { hline },
)
#let columnStyle = (:)
