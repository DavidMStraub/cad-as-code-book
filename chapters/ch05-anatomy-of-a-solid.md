# Anatomy of a Solid

This chapter opens the solid up. Chapter 2 counted a plate's faces,
edges, and vertices and promised the full story later; this is that
story: what a boundary representation is made of, how its pieces
connect and share, what makes a shape readable as a solid at all, and
why sub-shapes have no stable names – together with the selector
tools that answer that last problem properly. The chapter closes
where the structure pays off most directly: reading a STEP file
written by software that has never heard of this book's stack.

## Geometry and Topology

Every solid this book has built so far turned out to have a definite
number of faces, edges, and vertices, and those numbers followed real
rules. A plate with one hole always gains exactly one new face. A
cylinder always has exactly two vertices. None of this is coincidence,
and it comes from a distinction worth making precisely, because the rest
of this chapter – and a good deal of what makes CAD software behave the
way it does – rests on it.

A **boundary representation** describes a solid by describing the surface
enclosing it, and it does so in two genuinely separate layers.
**Geometry** is the raw mathematical description of shape: where points
sit in space, what curve a particular edge traces, what surface a
particular face lies on, how curved or how long something is. **Topology**
is the structure connecting those pieces: how many faces a solid has, how
many edges bound each face, which vertices those edges share, which
faces touch which. Geometry answers *where*; topology answers *what
connects to what*. A boundary representation is the two together –
topology supplies the skeleton, geometry fills it in with actual shape.

A cube and an arbitrary rectangular box make the split concrete. Built
the same way – six faces meeting at right angles – they share exactly
the same topology: eight vertices, twelve edges, six faces, each face
bounded by four edges, each edge bounded by two vertices, every one of
those facts identical between the two shapes.

```python
from cadquery import func as cf

cube = cf.box(10, 10, 10)
box = cf.box(30, 20, 10)
for shape in (cube, box):
    print(len(shape.Faces()), len(shape.Edges()), len(shape.Vertices()))
```

Both lines print `6 12 8`. What differs is purely geometric: the cube's
edges are all ten millimeters, the box's are not; the cube's faces are
squares, the box's are rectangles of two different sizes. Same topology,
different geometry, and neither fact was in any way implied by the
other – exactly as a subway map and a geographic map can describe the
same rail network from two independent angles. The map that shows which
stations connect and where to change lines is a topological
description; the map that shows exactly where each station sits and how
many kilometers apart they are is a geometric one. Both are true, both
are useful, and confusing one for the other is a real category of
mistake, one this chapter comes back to more than once.

A cylinder is small enough to take apart completely by hand, which makes
it a good first specimen.

```python
cyl = cf.cylinder(d=10, h=10)
print(len(cyl.Faces()), len(cyl.Edges()), len(cyl.Vertices()))
```

Three faces, three edges, two vertices. The face count is easy to
believe – a lateral wall, a top cap, a bottom cap – but the edge and
vertex counts are worth pausing on: a cylinder has two circular rims,
top and bottom, and a naive guess might expect two edges and no
vertices at all, since a full circle has no natural endpoint. The actual
structure is visible by walking it directly:

```python
def show_topology(shape, indent=""):
    print(indent + shape.ShapeType())
    for child in shape:
        show_topology(child, indent + "  ")


show_topology(cyl)
```

Iterating a shape with a plain `for` loop walks exactly one level down
its topology, so calling `show_topology` recursively prints the whole
nested tree beneath it. Run on the cylinder, it shows one solid, one
shell, three faces – and the lateral face accounts for the missing
structure. A cylindrical surface is a flat strip rolled into a tube,
and the **seam** where the strip's two ends meet back up is a real
edge, used twice by the same face – its boundary runs up one side of
the seam and back down the other. That seam needs a start and an end,
and those two points are the cylinder's two vertices, one where the
seam meets each rim; the rims themselves are each a single closed
circular edge whose start and end are the same vertex. Three edges,
two vertices, nothing left unaccounted for.

The printed tree says the same thing in a way that rewards a careful
look: the lateral face's wire lists *four* edge entries – the two
rims, and the seam twice – where `Edges()` reported three, and each
closed rim lists two vertex entries that are the same vertex in both
roles, start and end. The walk visits every *use* of an element; the
counting methods report each element once. The double appearances are
the first sighting of a fact the rest of this chapter leans on:
sub-shapes are shared, not copied.

:::{figure} ../figures/generated/ch05-cylinder-seam.png
:width: 22%

The cylinder's edges are its real topology: two circular rims, and the
seam running up the lateral face, whose two endpoints are the
cylinder's only vertices.
:::

## The B-Rep Vocabulary

### The Topological Primitives

Chapter 2 used four kinds of shape without formally naming the whole
family: a solid is bounded by faces, faces by edges, edges end at
vertices. Seven kinds exist in total, differing in dimension, in what
bounds them, and – for four of them – in the kind of geometry
attached.

A **vertex** is zero-dimensional: a single point in space, and nothing
more. An **edge** is one-dimensional: a piece of a curve – a line, a
circle, a spline – bounded by (up to) two vertices; a full circle, with
no natural start or end, still needs one vertex to close its loop, which
is exactly what the cylinder's rims showed. A **wire** is also
one-dimensional but carries no geometry of its own: it is an ordered,
connected chain of edges, nothing more – a wire is not required to close
back on itself, and an open chain is exactly as valid a wire as a closed
one. What *does* require closure is a face's boundary: a wire bounding a
face's outer contour, or an inner one where the face has a hole, has to
close into a loop for "the region this face covers" to mean anything,
but that is a requirement on faces, not a property wires carry on their
own. A
**face** is two-dimensional: a piece of a surface – a plane, a cylinder, a
sphere – bounded by one or more wires. A **shell** is a connected set of
faces, joined along shared edges; it may or may not enclose a volume,
and carries no geometry beyond what its faces already have. A **solid**
is a volume bounded by one or more shells – the actual target of most
parametric construction, and the type every primitive this book has
built starts as. A **compound** is simply a collection of shapes with no
particular connectivity promised at all – two unrelated solids in one
container are already a valid compound.

:::{figure} ../figures/static/ch05-brep-primitives.svg
:width: 100%

The seven topological primitives, in increasing dimension: a point, a
curved or straight piece bounded by points, a connected chain of those
pieces (shown closed here, though a wire need not be), a bounded patch
of surface, a connected set of patches (shown here as a box missing its
lid), a volume they enclose, and an unstructured collection of any of
the above.
:::

Four of these seven carry a piece of geometry that is genuinely their
own – a vertex its point, an edge its curve, a face its surface – and
three do not. Wire, shell, and compound introduce no new geometry at
all: they are pure organization, connecting the geometry-bearing
vertices, edges, and faces beneath them into larger structures. This is
worth building directly at least once, since a shell in particular does
not have to be closed the way a solid must:

```python
box = cf.box(10, 10, 10)
open_shell = cf.shell(box.Faces()[:5])
print(open_shell.ShapeType(), open_shell.isValid())
```

Five of the box's six faces, sewn together, are a perfectly valid
shell – an open box missing its lid – because *shell* only promises
connectivity, never closure. Closing the sixth face back in would turn
it into a solid; nothing about being a shell requires that.

### Hierarchy, Connectivity, and Sharing

The seven types form a strict hierarchy – solid, shell, face, wire,
edge, vertex, each level bounded by the one below it – and the single
fact that makes the hierarchy worth understanding, rather than just
memorizing, is that sub-elements are **shared**, not copied. Two faces
that meet along an edge do not each carry their own private copy of that
edge; they refer to the exact same one. That single fact is what
"connected" means in a B-Rep, and it is checkable directly:

```python
plate = cf.box(20, 20, 10)
edge = plate.Edges()[0]
for f in plate.Faces():
    if edge in f.Edges():
        print(f.Center())
```

This prints two different face centers – the two faces that happen to
meet along that particular edge – because `edge in f.Edges()` is asking
exactly the connectivity question: does this face's boundary include
this specific, shared edge. Two edges are connected the same way, through
a shared vertex, and the whole hierarchy can be walked top to bottom this
way: a face's edges, an edge's vertices, without ever needing to know
how many other faces or edges exist elsewhere in the shape.

Sharing is also the direct explanation for why a boolean operation
changes a solid's element counts by more than the number of features
suggests. Chapter 2's plate with one hole came out to seven faces,
fifteen edges, ten vertices, and the reasoning is now available in full:

```python
part = cf.box(80, 50, 10) - cf.cylinder(d=20, h=10)
print(len(part.Faces()), len(part.Edges()), len(part.Vertices()))

appearances = sum(len(f.Edges()) for f in part.Faces())
print(appearances)
```

Seven faces: the plate's original six, plus exactly one new curved face
for the hole's cylindrical wall, the same "one hole, one face" rule that
held for the cylinder alone. The last line prints 29, one short of
thirty – and thirty is what fifteen edges would total if every one of
them were shared by exactly two faces, the ordinary case. The shortfall
is the hole's seam edge, self-shared by its one curved face rather
than shared between two different ones, exactly as it was for the bare
cylinder. Fifteen edges is the plate's original twelve plus the hole's
three (two rims, one seam); ten vertices is the plate's original eight
plus the hole's two seam-ends. Every one of Chapter 2's numbers follows
from the same two rules this chapter has now established: one hole, one
face; edges and vertices are shared, and a seam edge is shared with
itself.

## Correctness and Its Failure Modes

### Orientation

A thought experiment first, no code needed to state it: take six square
faces, sewn together into a shell along shared edges, forming a closed
cube. The topology alone – six faces, twelve edges, eight vertices, all
connected exactly the way a cube's should be – does not settle what the
result actually *is*. It could be a solid cube, material filling the
inside. It could just as easily be the boundary of a cube-shaped cavity
carved out of a much larger block, material filling the *outside*
instead. Nothing in the connectivity distinguishes the two; both are the
identical shell.

The missing piece is **orientation**: which way each face actually
faces. A solid's faces each carry a direction – outward-pointing normal
vectors – and the rule that makes a shell readable as a specific solid
is that every face's normal points away from the material, never into
it. Checking this on a box confirms the mechanism, not just the rule:

```python
box = cf.box(10, 10, 10)
for f in box.Faces():
    print(f.wrapped.Orientation(), f.normalAt())
```

Three of the box's six faces report `FORWARD`, three `REVERSED`, in
pairs. Each face's underlying plane carries a normal direction as part
of its geometry, and for a box the planes of two opposite faces point
the same way – both x-faces' planes along +x, for instance. The face on
the far side can use that direction as its outward normal unchanged:
`FORWARD`. The face on the near side cannot, and `REVERSED` records
precisely that disagreement between the face's material side and the
arbitrary sense of its surface. `normalAt()` already resolves the two
pieces: every printed normal points away from the box's material,
whichever raw flag the face carries underneath. The same idea reaches one level
deeper, into a face's own boundary: when a face has an inner wire – the
rim of a hole, say – walking that inner wire has to trace the opposite
sense from the outer contour, so that "material on this side" stays
consistent all the way around the hole rather than flipping inside out.
Every boolean operation, every export, every validity check depends on
this being consistent everywhere in a shape; an oriented shell is a
solid, a shell with any of this wrong is, at best, a shape that quietly
fails the moment something asks it to behave like one.

### Validity

That last case – geometry that looks complete but is not actually
usable – is common enough to deserve its own check, and it is worth
seeing fail before seeing what catches it:

```python
plate = cf.box(60, 40, 10)
hole = cf.cylinder(d=10, h=10).moved(x=25, y=15)
corners = plate.edges("|Z")

result = (plate - hole).fillet(8, corners)
print(result.isValid(), result.Volume())
```

This prints `False`, and a volume – a number, not an exception. The
library built *something* and handed it back without complaint; only
asking `isValid()` reveals it is broken. The hole here sits close enough
to a corner that rounding the corner needs material the hole has already
removed – the fillet has nothing left to build a rounded surface
from – and the result comes back with faces or edges
that do not actually agree with each other, exactly the kind of
inconsistency Orientation just described in the abstract. `isValid()`
runs OCCT's structural checker over the whole shape and every
sub-shape in it – closed wires, non-self-intersecting faces, correctly
agreeing orientations, and more, documented exhaustively in the
checker's reference rather than repeated here – and a result that
fails it should never be trusted downstream, whatever `Volume()` or
`isValid()`-blind code might otherwise suggest. Filleting the corners
*before* cutting the hole avoids the conflict entirely – the same
dependency question Chapter 4 asked of the tray's features: know what
an operation depends on, because the library will not stop to ask.

### The Topological Naming Problem

A second, quieter failure has nothing to do with whether a shape is
valid. Suppose an edge is picked out once, found correct, and hardcoded:

```python
plate = cf.box(60, 40, 10)
hole = cf.cylinder(d=10, h=10).moved(x=15)
part = plate - hole

hole_rim = part.Edges()[13]
print(hole_rim.geomType())
```

This prints `CIRCLE`, correctly the hole's rim, found once by
printing every edge until the right one turned up. Now the design
changes – a second, smaller clearance hole is added near one corner, an
entirely ordinary revision that has nothing to do with the first hole:

```python
corner_hole = cf.cylinder(d=4, h=10).moved(x=26, y=16)
part = plate - hole - corner_hole

hole_rim = part.Edges()[13]
print(hole_rim.geomType())
```

The identical line now prints `LINE`. Index 13 used to be the hole's
rim; adding an unrelated hole elsewhere shifted the numbering of
everything after it, and that position now belongs to some straight
edge nowhere near the original hole. No error, no warning – a later step
built on `hole_rim`, a fillet say, would silently act on the wrong edge.

This is the **topological naming problem**
{cite:p}`kripac1997mechanism`, and it is not specific to
any one kernel or library. Internally, a B-Rep kernel assigns each
edge, face, and vertex a working identity for the shape it just built –
there is no permanent registry carrying "this is the same edge as
before" automatically across a rebuild, because after a boolean or a
fillet, the kernel has genuinely constructed new topology from scratch,
and matching pieces of it back to what existed a moment ago is, in
general, not something that can be done perfectly. `part.Edges()[13]`
never names an edge; it names a position in a list, and that position is
only as stable as the exact sequence of operations that produced it.
Insert an operation anywhere earlier and every index downstream can
silently point somewhere else.

## The Full Selector Toolkit

The fix is not a smarter index – it is to stop describing a sub-shape by
where it sits in a list and start describing what it actually *is*.
Chapter 2 already did this twice without naming the pattern: `">Z"` for
"furthest along an axis," `"%CIRCLE"` for "shaped like a circle." Both
belong to a small, complete language for describing a sub-shape by a
property rather than a position. Direction strings (`">Z"`, `"<X"`,
`"+Y"`) select extremes along an axis; type filters (`"%CIRCLE"`,
`"%PLANE"`, `"%CYLINDER"`) select by the underlying curve or surface; the
two combine by chaining calls, `faces(">Z").edges("%CIRCLE")`, narrowing
a set of faces down before searching within it for the right edges.

Some descriptions do not reduce to a short string, and `cadquery.selectors`
provides a family of `Selector` objects for exactly that case – an
escape hatch from the string syntax, not a separate system:

```python
import math

from cadquery.selectors import RadiusNthSelector

plate = cf.box(60, 40, 10)
hole = cf.cylinder(d=10, h=10).moved(x=15)
corner_hole = cf.cylinder(d=4, h=10).moved(x=26, y=16)
part = plate - hole - corner_hole

main_hole_rim = part.faces(">Z").edges(RadiusNthSelector(-1))
print(main_hole_rim.Edges()[0].Length() / (2 * math.pi))
```

`RadiusNthSelector(-1)` selects by radius rank – here, the largest
circular edge on the top face, printed back as its radius of `5.0` –
and it is the sharper question Chapter 4 promised when a lead-in
selector captured a mounting hole's rim it never meant to touch. The
description also survives the exact revision that broke
`part.Edges()[13]`: add the corner hole, reorder the cuts, add a third
hole later, and this line still finds the edge with the biggest
radius, because the description was never a claim about where the edge
sits in a list. `NearestToPointSelector`, `BoxSelector`,
`AreaNthSelector`, and a handful of others in the same module cover most
of what a position-independent description needs; for anything left
over, `Selector` is a plain base class with one method to
implement, `filter(objectList)`, which makes writing a custom one – "the
edge closest to this face's centroid," "the widest of the remaining
faces" – a few lines of ordinary Python, not a special kind of code.

## Reading a Foreign STEP File

Nothing in this chapter has been specific to one piece of software.
Vertex, edge, wire, face, shell, solid – the same seven types, the same
hierarchy, the same orientation rule – are how CATIA, SolidWorks, NX,
FreeCAD, and CadQuery all represent a solid, whichever
kernel happens to sit underneath (Dassault's CGM, Siemens's Parasolid,
or the open-source OCCT this book has been using directly). What differs
between them is which curve and surface types each one supports, how
each handles tolerance and precision, and the shape of its own API – not
the concepts themselves. **STEP** (formally ISO 10303) is the file
format that carries this shared structure between systems: a STEP file
exported from any of them stores the same vertices, edges, faces,
shells, and solids a reader would find by walking the model directly
inside the software that made it, with no topology lost in translation.

```python
import cadquery

shape = cadquery.importers.importStep("plate.step").val()
print(shape.ShapeType(), len(shape.Faces()), shape.isValid())
show_topology(shape)
```

`importStep` is the one place in this book where the library's
fluent `Workplane` is unavoidable – it is what the function returns –
and `.val()` immediately drops back out of it to the plain `Shape` the
rest of the book has used throughout. Everything from here on is exactly
the tools already built in this chapter: `Faces()`, `isValid()`,
`show_topology`, selectors, all working identically whether the shape
was built by this script a moment ago or read from a file that came from
a system that has never heard of this library. Importing a foreign part
is not a translation problem, because there is nothing left to
translate – which is the concrete version of the adoption argument
Chapter 1 opened with.

:::{note} Try It
- Build a mounting plate with four bolt holes and run `show_topology` on
  it. Count the faces, edges, and vertices by hand from the rules this
  chapter established, then check the count against `len(...)`.
- Select the plate's top face, then its four cylindrical hole faces, and
  fillet only the top rims of the holes – not the bottom ones. What
  selector isolates "top" without also selecting "bottom"?
- Build a stud on the plate's top face using `Plane(top_face)`, the
  Chapter 3 technique, and fillet the seam where the stud meets the
  plate. Which edge is that, and how do you select it without counting?
- Construct a flange: a ring (a large cylinder minus a smaller one) with
  six bolt holes spaced sixty degrees apart on a bolt circle. How many
  of its faces are cylindrical? Fillet every hole's rim, top and bottom,
  in one selector expression.
- Export any solid from this chapter to STEP, re-import it, and confirm
  `Volume()` agrees with the original to within floating-point
  tolerance.
:::
