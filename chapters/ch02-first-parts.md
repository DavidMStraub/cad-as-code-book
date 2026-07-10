# First Parts

## A First Solid

A short script is enough to see how the pieces fit together. Setting up the
two packages it needs is a one-time matter, covered in Appendix A; nothing
more is assumed here.

```python
from cadquery import func as cf
from ocp_vscode import show

plate = cf.box(80, 50, 10)
hole = cf.cylinder(d=20, h=10)
part = plate - hole

show(part)
```

Two primitives, one operation. `box` takes length, width, and height;
`cylinder` takes a diameter and a height, its axis along the vertical.
Both center themselves on the origin in x and y, but neither centers along
its own height: each sits with its base at z = 0 and extends upward from
there. That detail doesn't matter yet, since the plate and the hole share
the same height and so line up exactly top and bottom – but it matters a
great deal the moment two shapes of *different* heights are stacked, a
case this chapter returns to. The `-` operator subtracts one solid from
another – material is removed wherever the two overlap – so `part` is a
plate with a hole bored straight through its center. Calling `show` sends
the result to the viewer.

% Width compensated (64% declared for an intended ~41%): a typst layout bug
% squares the percentage for a figure this close after a chapter's opening
% heading + first code block (confirmed isolated to this one figure only;
% every other figure in the book renders correctly at its plain declared
% width). Re-check this if the surrounding prose changes enough to move
% the figure's position on the page.
:::{figure} ../figures/generated/ch02-plate-with-hole.png
:width: 64%

The plate with a hole bored through its center.
:::

Before going further, one choice deserves a sentence. CadQuery offers two
ways of writing models: a fluent style, in which operations are chained onto
a running modeling object, and the direct style used above, in which shapes,
faces, and locations are ordinary Python values passed explicitly between
functions and operators. This book uses the direct style throughout. It
keeps the geometry itself – solids, faces, edges – visible in the code, so
that later chapters can inspect, test, and manipulate those objects
directly. Readers who meet the fluent style elsewhere, including most of
CadQuery's own documentation, will recognize the same operations under
different spelling.

A hole through the exact center is a special case; most are not. Moving a
shape before combining it is one call:

```python
hole = cf.cylinder(d=20, h=10).translate((20, 0, 0))
part = plate - hole
```

`translate` returns a new shape shifted by the given offset and leaves the
original untouched – every operation in this book works this way, producing
a result rather than changing something in place. A plain offset is all
this chapter needs; placing a shape at an angle, or flush against a face
that is itself tilted in space, takes a somewhat richer object, a
**Location**, which Chapter 3 introduces alongside the rest of the spatial
vocabulary.

## Selecting What You Mean

Suppose the hole's edge should be rounded, top and bottom, but the plate's
outer edges should stay sharp. The listing methods above return everything,
without distinction; picking the right sub-shapes by counting through a
list would break the moment a dimension changes and the count shifts.
Alongside `Faces()` and `Edges()`, CadQuery has a second, lowercase family –
`faces()`, `edges()` – that takes a **selector**: a short string describing
a sub-shape by what it *is*, not by where it happens to sit in a list.

```python
top_face = part.faces(">Z")
hole_edge = top_face.edges("%CIRCLE")
```

`">Z"` reads as "the face furthest along +Z" – the top of the plate,
whichever position it happens to occupy internally. `"%CIRCLE"` filters for
edges whose underlying curve is a circle, which among the top face's edges
is exactly the rim of the hole; the plate's four straight outer edges are
of a different kind and are excluded automatically. Called with no
argument at all, `faces()` and `edges()` fall back to returning everything,
exactly like their capitalized counterparts – the two families differ only
in whether a selector is available, not in what they cover.

With the right edge in hand, rounding it is one call:

```python
result = part.fillet(2.0, [hole_edge])
show(result)
```

`fillet` takes a radius and a list of edges and returns a new solid with
those edges rounded to that radius. A matching operation, `chamfer`,
produces a flat angled cut instead of a curved one, when that is what a
drawing calls for.

:::{figure} ../figures/generated/ch02-plate-with-hole-filleted.png
:width: 41%

The hole's rim, filleted; the plate's outer edges stay sharp.
:::

## Dimensions as Variables

The plate is now doing something recognizable: a hole is placed, the right
edge is selected, and that edge alone is rounded. The remaining step is to
stop treating the dimensions as one-off numbers typed into a script.

Everything so far has used numbers written directly into the code. The
point of building a part this way is that the numbers do not have to stay
there:

```python
from cadquery import Shape


def plate_with_hole(
    length: float, width: float, thickness: float, hole_diameter: float, hole_offset: float
) -> Shape:
    plate = cf.box(length, width, thickness)
    hole = cf.cylinder(d=hole_diameter, h=thickness).translate((hole_offset, 0, 0))
    part = plate - hole
    hole_edge = part.faces(">Z").edges("%CIRCLE")
    return part.fillet(2.0, [hole_edge])
```

Calling `plate_with_hole(80, 50, 10, 20, 20)` produces exactly the part
built above; calling it with a different length produces a different plate,
correctly, without a single line being touched by hand. The parameters
carry names and types – `length: float`, not just `length` – so the model
states plainly what kind of input it expects and what kind of object it
returns. Type hints have no effect on how the code runs; what they buy, and
why they are worth the extra few characters, is the subject of Chapter 8.

A second habit starts here alongside them: backing a model with a check.

```python
part = plate_with_hole(80, 50, 10, 20, 20)
assert part.isValid()
assert part.Volume() > 0
```

A two-line sanity check will not catch every mistake, but it catches the
common ones – a hole so large it consumes the plate, an offset that pushes
it outside the material entirely – immediately, rather than when the file
is opened by someone else. Later chapters use a small library, `pytest`, to
write checks like this one more conventionally, and Chapter 8 turns the
habit into a working practice; for now, a plain `assert` says everything
that is needed.

## What Did We Just Build?

At this point the plate is no longer just a picture on the screen. It has
been moved, combined, selected from, rounded, parameterized, and checked.
That makes it worth stopping to ask what kind of object `part` actually is.
A shape can list its own sub-shapes:

```python
print(len(part.Faces()), "faces")
print(len(part.Edges()), "edges")
print(len(part.Vertices()), "vertices")
```

For a plate with one hole all the way through, the answer is seven faces,
fifteen edges, ten vertices. Six faces and twelve edges belong to the plate
itself, exactly as many as a plain box has; boring the hole adds one curved
**face** for the hole's wall, and – because that face is closed on itself
and needs a seam – three more **edges** and two more **vertices** than a
hole would seem to need at first glance. None of this has to be memorized.
What matters is the hierarchy: a **solid** is bounded by faces, faces are
bounded by edges, and edges end at vertices. That is why the selector above
could ask for a face and then an edge on it: those things are not metaphors
or screen decorations, but real parts of the model that can be queried
directly.

% Figure: the plate-with-hole solid, faces/edges/vertices called out, next
% to the small hierarchy diagram (Solid -> Face -> Edge -> Vertex).

Chapter 5 returns to this hierarchy in depth – how faces and edges are
shared, what orientation means, why the counts come out exactly this way.
For now, the working vocabulary above is enough to keep building.

## Worked Example: A Clutch Brick

The plate with a hole is enough to establish the mechanics. To end the
chapter with a complete part rather than a minimal example, the same moves –
primitives, placement, a boolean – can be used to build a small
**clutch brick**, the stud-and-tube toy brick familiar from any box of
interlocking building bricks. A real brick's studs sit in a regular grid,
which is exactly the kind of repetition Chapter 4 automates; here, two studs
are placed by hand, which is all that is needed to see how a stud is
attached.

```python
def clutch_brick(
    length: float,
    width: float,
    height: float,
    stud_diameter: float,
    stud_height: float,
    stud_spacing: float,
) -> Shape:
    body = cf.box(length, width, height)
    stud = cf.cylinder(d=stud_diameter, h=stud_height)

    left_stud = stud.translate((-stud_spacing / 2, 0, height))
    right_stud = stud.translate((stud_spacing / 2, 0, height))

    return body + left_stud + right_stud
```

Both primitives sit with their base at z = 0 by default, as the plate and
hole did earlier in this chapter – so the body's top surface is simply at
z = `height`, and moving a stud (itself starting base-first at z = 0) up
by exactly that much places its base flush against the body's top, with
nothing to embed and no gap to leave. Stacking two shapes that both start
from their own base is addition, not an extra correction – it is *not*
centering that makes this simple, but the fact that both primitives already
agree on which end is the bottom.

```python
import math

brick = clutch_brick(
    length=15.6,
    width=7.8,
    height=9.6,
    stud_diameter=4.8,
    stud_height=1.7,
    stud_spacing=8.0,
)

expected = 15.6 * 7.8 * 9.6 + 2 * math.pi * (4.8 / 2) ** 2 * 1.7
assert abs(brick.Volume() - expected) < 0.5
show(brick)
```

Because the studs sit on the surface rather than inside it, their volume
simply adds to the body's, so an independent hand calculation is a direct
check on the result – the same move as the plate's check, now carried out on
a part with more than one added feature.

:::{figure} ../figures/generated/ch02-clutch-brick.png
:width: 35%

The clutch brick, two studs placed by hand.
:::

The brick is also the chapter's first complete, shareable part: not just a
shape in a viewer, but a file a colleague can open without running any of
this code.

```python
from cadquery import exporters

exporters.export(brick, "brick.step")
```

The file this produces holds the same exact boundary representation the
model computed – faces, edges, curved surfaces – not an approximation of
it. **STEP** is the name of that format, and it opens in essentially any CAD
system in use today. Chapter 1 argued that code can produce ordinary CAD
artifacts, not just private scripts; this export is the first concrete proof
of that claim. Chapter 9 returns to STEP in depth, including how to carry
names, colors, and whole assemblies of parts along with the geometry.

:::{note} Try It
- Change `plate_with_hole`'s `hole_offset` until the hole touches the
  plate's edge. What happens to the fillet, and why?
- Fillet the plate's four outer vertical edges instead of the hole. Which
  selector isolates them?
- Give the clutch brick four studs instead of two, still placed by hand. At
  what point does writing each one out individually stop feeling
  reasonable? Keep the answer in mind for Chapter 4.
:::
