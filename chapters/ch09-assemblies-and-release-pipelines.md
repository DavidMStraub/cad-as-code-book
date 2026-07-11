# Assemblies and Release Pipelines

% Status: full rewrite after David's second round of content feedback
% (first draft's issues: jumped straight into code with no concept framing;
% opened §9.1 by describing Ch. 3/4 negatively - "never put anything in
% them"/"never gave it anywhere to sit", flagged as a habit to memorize, see
% private memory cad-book-working-rules.md; §9.4 "Format Landscape" was a
% table with zero-content surrounding prose - merged into a real BREP/STL
% discussion instead, section removed; every code block was a flat top-level
% script with no functions - refactored into tray()/battery_module()/
% release()/fixture_for()/geometric_diff(), matching the book's own
% establish-then-generalize pattern (Ch. 4's tray_hardcoded -> tray_design_intent,
% battery_module() -> battery_module(r_cell, h_cell) here); one inline
% expression (`cell_solid + cf.offset(...)`) was dumped raw into body prose -
% moved into fixture_for()'s own code block; a Ch. 1 backward-reference
% ("the geometric complement Chapter 1 pointed at and this book has not
% built until now") was cut as apologetic meta-commentary.
%
% Facts re-verified against the installed CadQuery package after the
% refactor (all code re-run end to end, not just reasoned about):
% - tray() reliably returns a Solid (isValid True, Volume 15445.60...) -
%   the -> Solid annotation is honest, unlike Ch. 8's deliberately-broken
%   example.
% - `cq.Assembly` and `cq.Color` live under top-level `cadquery`, not
%   `cadquery.func` - confirmed by direct inspection. `cf.Location` and
%   `cf.Shape` ARE the same classes as `cq.Location`/`cq.Shape`.
% - `Assembly.save()` is deprecated (FutureWarning) - `Assembly.export()`
%   used throughout instead, verified for both STEP and STL, no warning.
% - A 'Plane' constraint between two named faces snaps the child to the
%   *parent face's own in-plane origin*, not just the out-of-plane gap -
%   confirmed by testing three cells at three different x offsets, all
%   collapsing to the same x after solving. Constraints stay a single-pair
%   aside for this reason; the multi-cell pattern is a plain loop over
%   Locations.
% - `cf.offset` on a closed Shell does NOT grow the enclosed solid - it
%   builds a thin offset shell ("rind"), consistent with Ch. 7's finding
%   that `cf.offset` builds a standoff surface, not wall thickness.
%   `part + cf.offset(part.Shells()[0], t)` (fusing the rind back onto the
%   original) matches an analytic bigger-cylinder volume to the last
%   printed digit - this is what fixture_for() does.
% - The geometric diff is `(a - b) + (b - a)`, wrapped here as
%   geometric_diff(a, b) - cf has no dedicated symmetric-difference
%   operator. Verified on two plate revisions with a moved mounting hole:
%   isValid True, 2 solids, 141.287... mm^3.
% - The enclosure generator from Ch. 4's exercises was never built in the
%   book text, so the release-pipeline batch example runs over Ch. 4's
%   named CellSpec variants (18650, 21700) instead - real code already on
%   the page.
% 2026-07-11 pass: intro paragraph added; "X's own" tics + two brand
% mentions swept. Three substantive fixes:
% (1) fixture_for had the centered-box bug AGAIN (the exact ch2/ch3
%     lesson): block.translate((0,0,h/2)) put the block at z 35..105
%     while the grown cell spans -0.3..65.3 - the "pocket" was a dent in
%     the block's underside, isValid True and plausible volume (55014),
%     a textbook valid-but-wrong. Fixed: base-up block (30,30,50), grown
%     part raised by floor=5 - verified: pocket opens at the top with
%     opening area exactly the grown body's cross-section (271.7 mm^2),
%     cell rests on the floor and protrudes 20 mm. Two intermediate fix
%     attempts failed and taught the geometry: floor=4 with h=70 left a
%     0.7 mm roof over the body (grown top is 65.3, only the terminal
%     broke through) - a holding fixture must be SHORTER than the part.
% (2) make_cell had been re-defined with loose (r_cell, h_cell) numbers -
%     the exact mismatched-numbers anti-pattern Ch. 4's CellSpec section
%     warns about, under the same function name as Ch. 4's spec-taking
%     version. Now uses Ch. 4's CellSpec/make_cell verbatim;
%     battery_module takes a CellSpec; the variants dict holds CellSpecs
%     built with replace(), echoing Ch. 4's idiom. BOM output strings
%     unchanged (f"cell_{spec.r_cell}" prints the same cell_9.0/cell_10.5).
% (3) tray()/cached_tray/fixture_for now carry the assert-isinstance
%     narrowing Ch. 8 established - ch9 is the first post-Ch.8 chapter
%     and its annotated functions returned bare boolean/import results
%     that mypy would flag one chapter after teaching the fix.
% Also: one sentence at the end of the release section connects the
% pipeline to Ch. 8's CI gate (tests run before export) - the two
% chapters previously never referenced each other.
% Full chapter re-run end to end after these changes; all printed
% outputs re-verified (see below where quoted).

This chapter takes finished parts and turns them into a product:
assembled into a named, colored structure, exchanged through the
formats other tools actually read, and released – bill of materials,
supplier file, and print file from one loop over the named variants.
It closes with two smaller tools of the same trade: a fixture derived
from an imported STEP file, and a geometric diff that shows what a
revision changed in the shape itself.

## Assembling the Battery Module: Names, Colors, Locations

Every solid this book has built is one continuous piece of material – a
boolean union of features, indistinguishable from the outside as
anything but a single part. Most real products are not built that way:
a battery pack is a tray of one material holding cells of an entirely
different one, each with its own supplier and its own line in a bill
of materials. Fusing them with `+`, the way earlier chapters fused
features into one part, would erase exactly the distinctions that
matter – a single fused lump has no way to say "this half is aluminum,
that one is a purchased cell." An **assembly** keeps shapes separate on
purpose: a named tree of individual parts, each with its own placement,
appearance, and identity, positioned relative to one another without
ever merging their geometry. This is not a notion invented for one
library's convenience – product structure, an assembly's parts and their
relative placements, is part of the STEP standard itself, the same
industry-wide exchange format this chapter's STEP section reaches
for; any CAD system reading a STEP assembly back expects to find
exactly this kind of tree, not a single fused shape.

Chapter 4's tray and cell are exactly this kind of pair –
two parts that belong together but should never be fused into one –
and they are what this chapter builds its first assembly out of.
`tray` returns Chapter 4's tray as a single function call rather than a
loose script – with the `assert isinstance` narrowing Chapter 8
established, since its `-> Solid` is a promise about a boolean's
result – and `CellSpec` and `make_cell` are Chapter 4's, unchanged:

```python
from dataclasses import dataclass, replace

from cadquery import Shape, Solid
from cadquery import func as cf
import cadquery as cq

TRAY_THICKNESS = 6.0


def tray() -> Solid:
    width, depth = 100, 30
    mounting_hole = cf.cylinder(d=3.4, h=TRAY_THICKNESS).translate((44, 12, 0))
    mounting_holes = mounting_hole + mounting_hole.mirror("YZ", basePointVector=(0, 0, 0))
    result = cf.box(width, depth, TRAY_THICKNESS) - mounting_holes

    cell_radius, clearance, pocket_depth = 9.0, 0.3, 3.0
    pocket = cf.cylinder(d=2 * (cell_radius + clearance), h=pocket_depth)
    pocket = pocket.translate((0, 0, TRAY_THICKNESS - pocket_depth))
    for i in range(3):
        result = result - pocket.translate(((i - 1) * 24.0, 0, 0))
    assert isinstance(result, Solid)
    return result


@dataclass
class CellSpec:
    r_cell: float
    h_cell: float
    r_terminal: float = 2.5
    h_terminal: float = 1.0


cell_18650 = CellSpec(r_cell=9.0, h_cell=65.0)


def make_cell(spec: CellSpec):
    points = [
        (0, 0, 0),
        (spec.r_cell, 0, 0),
        (spec.r_cell, 0, spec.h_cell - spec.h_terminal),
        (spec.r_terminal, 0, spec.h_cell - spec.h_terminal),
        (spec.r_terminal, 0, spec.h_cell),
        (0, 0, spec.h_cell),
        (0, 0, 0),
    ]
    return cf.revolve(cf.face(cf.polyline(*points)), (0, 0, 0), (0, 0, 1))
```

`cq.Assembly` is the structure that keeps calls to these two functions
separate instead of combining their results into one shape:

```python
def battery_module() -> cq.Assembly:
    assy = cq.Assembly(name="battery_module")
    assy.add(tray(), name="tray", color=cq.Color("gray"))
    cell = make_cell(cell_18650)
    for i in range(3):
        x = (i - 1) * 24.0
        loc = cq.Location((x, 0, TRAY_THICKNESS))
        assy.add(cell, name=f"cell_{i}", color=cq.Color("steelblue"), loc=loc)
    return assy
```

`Assembly` and `Color` live under the top-level `cadquery` package
rather than `cadquery.func` – a structuring layer above individual
shapes, not another geometry operation – so this is the first chapter
to import both. The pattern for placing the three cells is a plain loop
over `Location`s, the same idiom `tray()` itself used for its three
pockets; `cq.Assembly` adds a name, a color, and a place in a tree on
top of geometry this book already knows how to build, not a new way of
building it.

:::{figure} ../figures/generated/ch09-battery-module.png
:width: 55%

The battery module: Chapter 4's tray in gray, three of Chapter 3's cells
in blue, placed by the loop above.
:::

## Constraints: Solving for a Placement Instead of Computing It

`battery_module` computes each cell's `z` by hand: `TRAY_THICKNESS`,
read off and typed in. `Assembly` also supports stating the
relationship instead and letting a solver work the number out:

```python
pair = cq.Assembly(name="pair")
pair.add(tray(), name="tray")
pair.add(make_cell(cell_18650), name="cell", loc=cq.Location((0, 0, 50)))  # placeholder z

pair.constrain("tray@faces@>Z", "cell@faces@<Z", "Plane")
pair.solve()
print(pair.children[1].loc.toTuple())
```

`"tray@faces@>Z"` selects the tray's topmost face with the same string
selectors Chapter 5 already taught; `"Plane"` asks the solver to bring
the cell's bottom face into that plane, whatever `z` it takes to
get there. The placeholder `50` above is gone after `solve()` – the
printed location's `z` comes back `6.0`, `TRAY_THICKNESS` itself,
without that number appearing anywhere in this snippet. A `Plane`
constraint positions the whole face-to-face relationship, not only the
gap along one axis, so it fits a single, deliberate pairing like this
one cleanly; `battery_module`'s three cells stay a plain loop over
`Location`s instead, the same reason `tray()` preferred a loop to a
more elaborate pattern tool for its three pockets.

## STEP: Exchanging Geometry with Metadata

An assembly built in a script is gone the moment the script ends.
**STEP** is the file format that carries a shape – or a whole assembly
– to another CAD system, and it carries more than raw geometry: names
and colors survive the round trip along with the exact B-Rep.

```python
assy = battery_module()
assy.export("battery_module.step")

reloaded = cq.Assembly.load("battery_module.step")
for child in reloaded.children:
    print(child.name, child.obj.Volume())
```

```
tray 15445.6
cell_0 16305.7
cell_1 16305.7
cell_2 16305.7
```

Every name given to `add` inside `battery_module` comes back unchanged,
and every solid's volume matches what it was before export – STEP is
exact geometry, not an approximation, the same distinction Chapter 10
will draw sharply against mesh formats. A colleague opening this file
in FreeCAD or Fusion 360 sees a module with three cells and a tray,
correctly named and colored, not one anonymous lump.

## Choosing a Format: BREP and STL

STEP is the right tool once geometry needs to leave this book's
scripts – for a supplier, a colleague, another CAD system entirely.
Two more formats earn a place in this book for jobs STEP is not suited
to.

**BREP** is the kernel's native serialization: the exact data
structure the kernel already holds in memory, written to disk without
translating it into anything else first. That skipped translation is
what makes BREP both faster to write and read than STEP and, unlike
STEP, unreadable by anything outside this one kernel – there is no
standardized structure to translate into, no colors or names encoded
in a way another program would know how to find. That trade only makes
sense for a job that never leaves the machine that wrote it: caching a
shape that took real time to build, so a second run does not pay to
rebuild it.

```python
from pathlib import Path


def cached_tray(cache_path: Path) -> Solid:
    if cache_path.exists():
        cached = cf.Shape.importBrep(str(cache_path))
        assert isinstance(cached, Solid)
        return cached
    result = tray()
    result.exportBrep(str(cache_path))
    return result
```

The second call with the same `cache_path` returns immediately – the
geometry is read back exactly as it was written, not recomputed.

**STL** gives up exactness on purpose: a shape reduced to a mesh of flat
triangles, an approximation rather than the same curves and surfaces
STEP and BREP both preserve exactly. Chapter 10 covers meshing in full;
what matters here is that STL is the format 3D printers and slicers
actually consume, so it earns its place in this chapter's release
pipeline even though it is the one format here that cannot round-trip
back into an exact shape.

```{raw:typst}
#import "table-style.typ": tableStyle, columnStyle
```

| Format | Geometry | Names / colors | Typical use |
|---|---|---|---|
| STEP | exact B-Rep | yes | exchange with another CAD system |
| BREP | exact B-Rep, kernel-native | no | caching intermediate results locally |
| STL | triangle mesh, lossy | no | 3D printing, Chapter 10 |

Two-dimensional drawings – dimensioned views, tolerances, title blocks
– are the one exchange format this book will not cover: the library's
drawing support is thin compared to a dedicated drafting tool, and a
half-built treatment would cost pages without leaving the reader able
to produce a drawing a machine shop would actually accept.

## The Release Pipeline: One Script, Three Outputs

A design is not finished when it looks right in the viewer; it is
finished when a supplier can manufacture it, a print farm can print a
prototype, and whoever ordered the parts knows what is actually in the
box. `battery_module` already builds one named variant; generalizing
it to take a `CellSpec`, rather than assuming the 18650's numbers,
turns "build another variant" from copying a script into calling a
function with a different spec – the bundled-numbers argument Chapter 4
made for `make_cell`, now paying off one level up:

```python
def battery_module(spec: CellSpec) -> cq.Assembly:
    assy = cq.Assembly(name="battery_module")
    assy.add(tray(), name="tray", metadata={"part": "tray"})
    cell = make_cell(spec)
    for i in range(3):
        x = (i - 1) * 24.0
        loc = cq.Location((x, 0, TRAY_THICKNESS))
        assy.add(cell, name=f"cell_{i}", metadata={"part": f"cell_{spec.r_cell}"}, loc=loc)
    return assy
```

A second function turns one assembly into the three things a release
actually needs – a **bill of materials** (a part list with quantities),
a STEP file for a supplier, an STL for a printed prototype – reading
the part list straight from the assembly's tree via `traverse()`
and the `metadata` given to each `add`, rather than keeping it as a
separate document that can drift out of sync with the model:

```python
from collections import Counter


def release(assy: cq.Assembly, name: str) -> None:
    assy.export(f"battery_module_{name}.step")
    assy.export(f"battery_module_{name}.stl")
    counts = Counter()
    for _, sub in assy.traverse():
        if sub.obj is not None:
            counts[sub.metadata["part"]] += 1
    print(name, dict(counts))
```

Driving both across Chapter 4's named cell variants is now a
two-line loop, not a script that has to be copied and edited per
variant:

```python
variants = {"18650": cell_18650, "21700": replace(cell_18650, r_cell=10.5, h_cell=70.0)}
for name, spec in variants.items():
    release(battery_module(spec), name)
```

```
18650 {'tray': 1, 'cell_9.0': 3}
21700 {'tray': 1, 'cell_10.5': 3}
```

Nothing here is specific to two cell formats; the same loop over any
number of named variants is Chapter 4's "three-format tray" exercise,
run all the way to shippable files. In a real repository this loop is
the *last* step of a release, behind the gate Chapter 8 built: the
same CI job that runs the tests on every change runs them once more
here, and a variant whose geometry fails its checks never reaches the
`export` calls at all.

## A Fixture from an Imported STEP

Not every part this book generates started life as generated code.
Chapter 1's adoption argument – automate around the CAD a shop already
has, rather than insisting everything be modeled from scratch – has a
concrete, small, and extremely common form: a **fixture**, a block
machined to hold one specific part still, built as that part's
shape subtracted from a block with a little clearance added.

```python
def fixture_for(part: Solid, clearance: float, block=(30, 30, 50), floor=5.0) -> Solid:
    grown = part + cf.offset(part.Shells()[0], clearance)
    w, d, h = block
    result = cf.box(w, d, h) - grown.translate((0, 0, floor))
    assert isinstance(result, Solid)
    return result
```

Growing `part` uniformly by a clearance is not `cf.offset` applied
directly to the solid: offsetting a *closed shell* by itself builds a
thin shell between the original surface and its offset copy – a rind,
not a bigger solid, the same distinction Chapter 7 drew between
`cf.offset`'s standoff surfaces and `cf.hollow`'s wall thickness.
Fusing that rind back onto the original solid is what actually grows
it, the line `grown = part + cf.offset(...)` above – the result's
volume matches a cylinder with radius and height both grown by
`clearance`, to the digit, whether or not `part` was ever a cylinder as
far as this function knows:

```python
reloaded = cq.Assembly.load("battery_module.step")
cell_solid = reloaded.children[1].obj  # one imported cell, opaque geometry

fixture = fixture_for(cell_solid, clearance=0.3)
print(fixture.isValid(), fixture.Volume())
```

`cell_solid` here came from a STEP file, not from `make_cell` – as far
as `fixture_for` is concerned, it could be a supplier's part with no
parametric description behind it at all, exactly the situation the
adoption thread is about. Raising the grown copy by `floor` before
subtracting leaves material under the part, and a block shorter than
the part leaves the pocket open at the top: the real, physical cell
drops in from above, rests on the 5 mm floor with `0.3` mm of
clearance on every held surface, and stands proud of the block where a
gripper or a probe needs to reach it.

## The Geometric Diff

A part revised in place – a hole moved, a wall thickened – leaves no
record of *what* changed unless something is built to show it. `cf` has
no dedicated symmetric-difference operator, but one is two ordinary
booleans away: the material only the old version had, plus the material
only the new one has.

```python
def geometric_diff(a: Shape, b: Shape) -> Shape:
    return (a - b) + (b - a)


plate = cf.box(60, 30, 6)
hole_v1 = cf.cylinder(d=6, h=8).translate((-15, 0, 0))
hole_v2 = cf.cylinder(d=6, h=8).translate((-13, 0, 0))
v1 = plate - hole_v1
v2 = plate - hole_v2

changed = geometric_diff(v1, v2)
print(changed.isValid(), len(changed.Solids()), changed.Volume())
```

```
True 2 141.3
```

Two solids come back inside a single `Compound`, not a `Solid` –
`geometric_diff` is typed to return `Shape` rather than promise a
narrower type it cannot always deliver, the same reasoning Chapter 8
gave for checking a boolean's result instead of assuming it. Those two
solids are a thin crescent of material the new revision restored where
the old hole used to be, and a matching crescent it removed at the new
hole's position – both real, both nonzero, both exactly where the two
revisions actually disagree, and both far smaller than either hole
itself because the two positions mostly overlap. Moving `hole_v2`
further away – to `-10` rather than `-13` –
makes each circle disagree with the other over most of its area
instead of a thin sliver at the edge; the diff is still exactly right,
just no longer a good advertisement for how little actually changed.
`git diff` shows this for the *script*; `geometric_diff` shows it for
the *shape* the script produces – the same comparison, one level lower,
run on rendered geometry instead of source text.

:::{figure} ../figures/generated/ch09-geometric-diff.png
:width: 55%

The geometric diff between two plate revisions: the two crescents where
`v1` and `v2` actually disagree, everything unchanged left out entirely.
:::

:::{note} Try It
- Extend the release pipeline to Chapter 4's third named format, the
  4680 cell from that chapter's exercises, and confirm the printed BOM
  picks it up as a new part without any other line in the loop
  changing.
- Add a fourth constraint to the single-pair example: keep the cell's
  `Plane` constraint to the tray's top face, and add an `Axis`
  constraint aligning the cell's axis to the tray's normal. Does
  `solve()` still place the cell the same way, and what changes if the
  cell starts out tipped over on its side?
- Run `geometric_diff` between two revisions of Chapter 8's `cell_can`
  – one with a rim fillet, one without. Is the diff one solid or
  several, and does its volume match the difference in `Volume()`
  between the two directly?
:::
