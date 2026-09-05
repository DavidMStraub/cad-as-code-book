# Designing with Parameters

% Status: full draft, all sections. See private/book-plan.md §2 (Ch. 4).
% Narrative: instead of five independent topics each with its own
% standalone example, the chapter follows one continuous build - a tray
% for Chapter 3's cell - where each concept (feature order, design
% intent, patterns, parameter sets) is the next real decision that comes
% up while building it, not a separate demonstration bolted on. The three
% ambitious artifacts (hex-packed cells, the 18650/21700/4680 variant
% generator, the data-driven enclosure) stay reserved as reader-built
% exercises, scaling up the same tray rather than repeating what the
% chapter already solved.
% 2026-07-11: intro paragraph added; §4 now closes the loop back to the tray
% (tray_design_intent(make_cell(...)) - verified working). Empirical
% claims re-verified in this environment: BoundingBox().xlen exactly
% 18.0 / 21.0 (no tolerance slack) for the revolved cells;
% mirror("YZ", basePointVector=...) signature current.
% §1 reworked same day, on David's judgment that the original locating-
% boss/corner-fillet example was contrived (a material collision requires
% a placement that is already a bug, and the boss never reappeared on the
% tray). New anchor: selector re-evaluation - the code-CAD-specific order
% dependence (a GUI tree pins persistent references; code re-runs the
% query), demonstrated on the tray's real features (pocket lead-in fillet
% vs. mounting hole). Verified: "%CIRCLE" on the top face captures 1 edge
% before the hole exists, 2 after; both orders isValid()==True; volume
% difference 2.593 mm^3. Note fillet() needs real Edge objects - pass
% selection.Edges(), not the compound in a list (a multi-edge compound
% raises TypeError; ch2's [hole_edge] only works because a single match
% returns a bare Edge).

A model whose dimensions are parameters is a model built to be
rebuilt: every value might be different tomorrow, and the construction
has to stay correct when it is. This chapter builds a tray for
Chapter 3's cell and, along the way, meets the four disciplines that
make rebuilding safe: putting features in an order whose dependencies
survive change, deriving dimensions from the geometry they have to
match instead of retyping them, multiplying one feature into a pattern
instead of copying it, and bundling a variant's numbers into a single
object that travels together. The chapter ends where the reader takes
over: three exercises that scale the same tray to a real pack.

## Building the Tray: Feature Order in Practice

A cell needs somewhere to sit: a **tray**, a plate with a pocket to seat
the cell and a mounting hole to bolt it down. It is the natural next part
to build after Chapter 3's cell, small enough to work through directly,
and building it raises immediately a question every part with more than
one feature raises: what order do the features go in?

A base shape is laid down first, almost always, and a part's finishing
touches – fillets, chamfers – almost always go last, with material added
and removed in between in whatever order the design calls for. Chapter 1
called the program the recipe; a recipe's steps have an order, and most
of the time that order can follow the shape of the part itself –
envelope, then features, then finish. This is not a rule enforced by the library;
it is a convention that survives because it usually matches how one
feature's construction depends on another's – a mounting hole needs
material to remove, a fillet needs an intact edge to round, ideally the
last edge that will exist rather than one a later cut is about to
consume.

In code, one dependency reaches further than material: **selection**.
Chapter 2 introduced selectors as the durable way to pick a face or an
edge – durable against dimension change, so that `">Z"` keeps meaning the
top face however thick the plate becomes. But a selector is a question,
and it is answered by the geometry as it stands on the line where it is
asked. Every feature built before that line changes what the question is
asked about.

The tray shows this directly. Its pocket gets a **lead-in** – a small
round on the rim that guides the cell in during assembly – and its
mounting hole is bored straight through the plate. Here are both, in two
orders:

```python
from cadquery import func as cf

width, depth, thickness = 40, 30, 6
plate = cf.box(width, depth, thickness)
pocket = cf.cylinder(d=18.6, h=3).moved(z=thickness - 3)
hole = cf.cylinder(d=3.4, h=thickness).moved(x=16, y=11)

base = plate - pocket
lead_in = base.faces(">Z").edges("%CIRCLE")
round_then_hole = base.fillet(1.0, lead_in.Edges()) - hole

base = plate - pocket - hole
lead_in = base.faces(">Z").edges("%CIRCLE")
hole_then_round = base.fillet(1.0, lead_in.Edges())

print(round_then_hole.Volume() - hole_then_round.Volume())
```

The two versions differ in one respect only: whether the hole already
exists when the selector runs. In the first, `"%CIRCLE"` on the top face
finds one circular edge – the pocket's rim – and the lead-in lands
exactly there. In the second, the same two lines find *two* circular
edges, and the mounting hole's rim is quietly rounded along with the
pocket's – a rim that a screw head is supposed to seat flat against.
Both scripts run without complaint, both produce valid solids, and the
printed volume difference of `2.6` cubic millimeters is how the mistake
announces itself, because nothing else will.

:::{figure} ../figures/generated/ch04-tray-feature-order.png
:width: 41%

`hole_then_round`: the selector, asked after the hole exists, finds two
circular rims, and the mounting hole's rim is rounded along with the
pocket's.
:::

The lesson is not "always finish last" – that would just be a different
rule to follow blindly. The lesson is to ask what each operation actually
depends on. A selector depends on every feature built before the line it
sits on; a fillet, in the same quiet way, depends on intact material near
the edge it rounds, and will consume a small feature placed in its path
without asking. Base, add, subtract, finish remains a good default
reading order because it usually keeps those dependencies pointing one
way – but that is a property of the geometry, not of the convention, and
worth checking whenever a finishing touch and a feature land close
together. There are two honest fixes here: do the rounding while the
pocket's rim is the only circular edge there is – order as the tool – or
ask a more precise question, one that selects the rim by its radius
rather than by circularity alone, so it cannot capture strangers. That
second fix – constructions that say what they mean, instead of what
happens to be true when the line runs – is exactly what Design Intent,
next, is about.

## Design Intent: Deriving the Pocket from the Cell

The tray's pocket has to match the cell it holds – wide enough to seat
it, with a little clearance so the cell is not wedged in. The obvious way
to write that is to look up the cell's radius and type it in:

```python
width, depth, thickness = 40, 30, 6  # the same tray as Feature Order


def tray_hardcoded():
    plate = cf.box(width, depth, thickness)
    pocket_radius = 9.0 + 0.3  # the 18650's radius, plus clearance
    pocket = cf.cylinder(d=2 * pocket_radius, h=3).moved(z=thickness - 3)
    return plate - pocket
```

This works, for exactly as long as the cell stays a 9-millimeter-radius
18650. The moment the design moves to a different cell – a fatter one in
the 21700 format, say: 21 millimeters across, 70 tall, by Chapter 3's
naming code – the `9.0` above does not update itself; it just sits
there, quietly wrong. The alternative is to read the radius from the
cell itself, rather than retype a number that has to match it by
coincidence:

```python
def tray_design_intent(cell):
    plate = cf.box(width, depth, thickness)
    cell_radius = cell.BoundingBox().xlen / 2
    pocket = cf.cylinder(d=2 * (cell_radius + 0.3), h=3).moved(z=thickness - 3)
    return plate - pocket
```

Swap in a 21700-class cell (radius 10.5 millimeters instead of 9.0) and
the difference is immediate: `tray_hardcoded`'s pocket radius is still
`9.3`, smaller than the cell it is supposed to seat – the cell does not
fit, it rests on top of the tray instead of into it. `tray_design_intent`
reads `cell.BoundingBox().xlen / 2` fresh from the actual cell passed in,
so its pocket radius becomes `10.8` automatically, still exactly 0.3
millimeters of clearance, without the tray's code changing at all.

This is the sharper version of the same lesson Chapter 2 stated more
mildly: a fixed number written into a construction is a claim about a
shape it does not itself compute, true only for as long as that other
shape happens not to change. Reading the answer from the model itself –
a face, a bounding box, a selector – makes the claim automatically, every
time, instead of asking whoever changes the cell to remember which other
numbers quietly depended on it.

## Multiplying Geometry: Symmetry and Patterns

A pack holds several cells, not one, so the tray grows to match: wider,
with a mounting hole on each side, a pocket for every cell instead of
one. Both of these are the same underlying idea in two different
guises – build one feature, then place it again without writing its
construction out a second time.

The two mounting holes on a wider tray are mirror images of each other,
not two independent decisions:

```python
from cadquery import func as cf

width, depth, thickness = 100, 30, 6
mounting_hole = cf.cylinder(d=3.4, h=thickness).moved(x=44, y=12)
mounting_holes = mounting_hole + mounting_hole.mirror("YZ", basePointVector=(0, 0, 0))

plate = cf.box(width, depth, thickness)
plate_with_holes = plate - mounting_holes
```

`mirror` takes a plane to reflect across – `"YZ"` here, the plane through
the tray's center – and returns the reflected copy on its own; adding
it to the original gives both holes from one placement decision instead
of two. Move the hole and its mirror image follows automatically, the
same durability argument as Design Intent, applied to a second copy
instead of a derived number.

Repetition that is not a simple reflection – several cell pockets in a
row, say – is a plain Python loop over positions, nothing about the
looping itself specific to the library:

```python
cell_radius, clearance, pocket_depth = 9.0, 0.3, 3.0
pocket = cf.cylinder(d=2 * (cell_radius + clearance), h=pocket_depth)
pocket = pocket.moved(z=thickness - pocket_depth)

tray = plate_with_holes
for i in range(3):
    tray = tray - pocket.moved(x=(i - 1) * 24.0)

print(tray.isValid(), tray.Volume())
```

:::{figure} ../figures/generated/ch04-tray-patterns.png
:width: 41%

The widened tray: mirrored mounting holes, three cell pockets from one
loop.
:::

Three pockets, one `pocket` shape, one loop – the count and the spacing
are both just numbers now, changeable without touching how a single
pocket is built. A **pattern**, in this sense, is nothing more than a
loop over locations, the same idea whether the locations sit in a line,
a circle, or – as the tray will need eventually, to pack cells as
tightly as their own geometry allows – a hexagonal grid.

## Parameter Sets as Data: Dataclasses and Variants

A design that keeps track of several cell *variants* at once – not just
one cell's numbers – benefits from bundling those numbers together
rather than passing them separately. A pack built around an 18650 cell
and a version built around a 21700 cell are the same tray logic applied
to two different, complete sets of dimensions, and passing four or five
separate numbers around invites exactly the mismatch Design Intent just
warned about: nothing stops a radius from one cell pairing up with a
height from another.

Python's `@dataclass` bundles a set of related values into a single
named, typed object:

```python
from dataclasses import dataclass, replace


@dataclass
class CellSpec:
    r_cell: float
    h_cell: float
    r_terminal: float = 2.5
    h_terminal: float = 1.0


cell_18650 = CellSpec(r_cell=9.0, h_cell=65.0)
cell_21700 = replace(cell_18650, r_cell=10.5, h_cell=70.0)
```

`CellSpec` is a small, ordinary Python class – `@dataclass` only saves
writing `__init__` by hand – but grouping the numbers this way means a
function that needs a cell's dimensions can take one `CellSpec` argument
instead of four separate ones, with no way to pass a radius that belongs
to a different cell than the height beside it. `replace` builds a
second, independent `CellSpec` by copying the first and overriding only
the fields that actually differ, which is the point: a 21700 cell is
stated as *what changes relative to an 18650*, not retyped from nothing.

```python
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


cell_a = make_cell(cell_18650)
cell_b = make_cell(cell_21700)
```

:::{figure} ../figures/generated/ch04-cell-variants.png
:width: 27%

The 18650 (left) and 21700 (right) cells, both from `make_cell`, differing
only in the `CellSpec` passed in.
:::

`make_cell` does not know or care how many named variants exist; it
reads whatever `CellSpec` it is given. Chapter 3 built exactly `cell_a`'s
geometry with the numbers written directly into the profile; here they
arrive as one object's fields instead, which is what makes a second,
third, or eventual 4680-format cell a matter of stating a new
`CellSpec`, not rewriting `make_cell`. And the pieces compose:
`tray_design_intent` reads its pocket radius from whatever cell it is
handed, so `tray_design_intent(make_cell(cell_21700))` already produces
a tray that fits the new cell – one variant declaration flowing through
the whole construction. The exercises below scale exactly this up.

## Exercises: Scaling the Tray Up

Everything so far is ready to be pushed further, by the reader rather
than the page: three exercises, each one exactly the pattern just built,
at a scale or a generality this chapter has not itself gone to.

**Hex-packed cells.** A row of pockets wastes space a real pack cannot
afford; circles pack more tightly on a hexagonal grid than in rows and
columns. Extend the patterns loop above from a single row to a hex grid
holding at least a dozen cells, still built from one `pocket` shape and
one loop over computed positions. A packing is correctly hexagonal if
every pocket's six nearest neighbors sit at the same distance from it –
check that directly, on the actual computed centers, rather than trusting
the arrangement by eye.

**A three-format tray.** `CellSpec` above covers the 18650 and the
21700; add the 4680 format's numbers as a third named variant, and write
one function that builds a correctly-sized tray – pocket radius,
mounting hole positions, everything – from a `CellSpec` alone. `assert`
that the pocket radius the function produces for each of the three
variants matches that variant's own cell radius plus clearance, exactly,
the same check Design Intent used to catch the mismatch.

**The enclosure.** A tray is a slice of the real problem: a full
enclosure adds an outer case, standoffs to mount a circuit board, and
cutouts for whatever connectors the board carries – a small **component
table**, one row per feature, in place of the tray's few named numbers.
Build a function that takes such a table (a list of `dataclass` rows is
enough: a kind, a position, a size) and produces one case from it; the
test that matters is not that it looks right in the viewer, but that
changing one row's numbers and rerunning the function changes exactly
the feature that row describes, and nothing else – the same durability
Design Intent asked of the tray, now asked of a whole assembly of
features at once.
