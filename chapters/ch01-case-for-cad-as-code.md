# The Case for CAD as Code

% Status: skeleton + content bullets. See private/book-plan.md §1–§3.

% Opening hook: two revisions of the same part — a binary CAD file pair vs. a
% two-line diff. What changed? One of them can tell you.

## A Paradigm Mismatch

- Mechanical products resemble *software* products, not creative one-shot
  deliverables: thousands of interacting parts, a single flawed one can sink
  the design; long-lived; improved through iteration.
- Yet mechanical teams work with tools built on the creative-team paradigm:
  GUI-first, opaque proprietary formats, optimized for short-term productivity
  on products that ship once and only need to "look right."
- Thesis: the tools aren't bad — they're the wrong paradigm for this product
  class. (Cite: Frazelle, *Mechanical CAD: Yesterday, Today, and Tomorrow*;
  KittyCAD code-first post — further reading, argument made in our own voice.)

## What Software Teams Figured Out

- Four practices, each transplantable to mechanical design:
  - **Semantic description** — the product is human-readable text; it explains
    itself, diffs line by line, survives its authors.
  - **Version control** — history with *rationale*, branches for variants,
    review before merge. Contrast: `housing_v2_final_REALLY_final.sldprt`.
  - **Verification on every change** — automated tests catch regressions the
    moment they appear, not at the prototype.
  - **Pipelines** — the release artifacts (files, reports, documentation) are
    *generated*, not manually re-exported after every change.
- Preview: Part III of this book is these four practices, working, on real
  geometry. A teaser figure of the *geometric diff* (two revisions XOR-ed,
  the change highlighted in 3D) belongs here.

## What Code Buys You, Concretely

- **Reproducibility and variants**: a model is a function; a product family is
  a loop. Catalog parts are downloadable — *your* parts are not, and those are
  what you generate. (One sentence on standard parts; the real example — an
  enclosure family generated from a component table — is built in Chapter 4.)
- **Automation of the onerous**: re-meshing after a small change, re-exporting
  deliverables, re-running renders — pipeline work, not engineer work.
- **Algorithmic design**: hundreds of candidate geometries evaluated against
  simulation, optimization finding designs no one would click together
  (Chapter 12).
- Honest costs: ramp-up time, thinking-in-code, a smaller ecosystem than the
  incumbents. The adoption path below is the mitigation.

## How CAD Systems Represent Geometry

% B-Rep pass 1 of 3: concept level only (pass 2 in Ch. 2, deep dive in Ch. 5).

- Three representations: **CSG** (booleans over primitives, compact but
  limited), **B-Rep** (topology + exact surface geometry — the professional
  standard), **mesh** (triangles: an approximation, right for printing and
  simulation, wrong for design).
- Why this book is a B-Rep book; where meshes re-enter (Part III).

## A Short History of Code-First CAD

- OpenSCAD (2010): first popular code-CAD, but CSG-only, no STEP.
- Open CASCADE Technology (1999): the open-source B-Rep kernel under
  everything that follows.
- FreeCAD (2002): OCCT + GUI + Python API.
- CadQuery (2012 / 2020): code-first parametric CAD on OCCT — this book's
  tool. build123d (2022) as the sibling project (Appendix B phrasebook).
- Framing: the kernel is 25 years old and battle-tested; what's new is the
  ergonomics.

## The Stack Used in This Book

- Python + CadQuery 2.8 + OCCT underneath; jupyter-cadquery / OCP CAD Viewer
  for visualization; everything open source, everything scriptable.
- What is deliberately *not* covered: GUI CAD interop beyond STEP, 2D drawings.

## Adopting Code-First Without Betting the Farm

- No hard swap: begin by interrogating the CAD you already have (import STEP,
  measure, check, report — Chapter 5), automate one onerous task (fixtures,
  Chapter 9), grow from there.
- The productivity dip of a hard swap vs. incremental wins on existing files.

## The Plan of This Book, and How to Read It

- The three parts (build → understand → engineer); the running threads
  (battery pack, enclosure generator, fixture, LEGO brick, W7-X) with a
  roadmap figure.
- Reading modes: cover-to-cover vs. reference (canonical-home table, Appendix
  R); note for instructors.
- Every example in this book ends with a check, and every function is typed —
  starting in the next chapter, explained in Chapter 8.
