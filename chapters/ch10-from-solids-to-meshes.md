# From Solids to Meshes


This chapter is about the step where exact geometry becomes something
other tools can consume: tessellation into triangles for a printer's
slicer, and finite-element meshing into tetrahedra for the solver
Chapter 11 puts to work. Both are controlled approximations, and both
end in a physical payoff – the chapter closes by completing Chapter
2's clutch brick into a part worth printing and clicking onto a real
brick.

## Why Discretize

Every shape this book has built so far is exact: a face carries the real
mathematical surface it describes, a cylindrical wall is a cylinder, not
an approximation of one. Most of what a shape is handed to next cannot
use that exactness directly. A graphics card draws triangles, not
trimmed NURBS surfaces. A 3D printer's slicer needs a closed skin to
decide inside from outside, not a set of trimmed B-Rep faces. A
structural solver needs the interior broken into small, simple pieces
it can write one equation for and couple to its neighbors – not a
volume bounded by exact surfaces with no interior structure at all.

A **mesh** is what a B-Rep becomes to meet these needs: the exact
geometry, replaced by a finite set of simple pieces – flat triangles on
a surface, tetrahedra filling a volume – each one so simple that
whatever comes next can work with it directly. Turning exact geometry
into a mesh is **tessellation**, and it is always an approximation: a
flat triangle can only ever touch a curved surface, never coincide with
it exactly, so a curved region needs more, smaller triangles to stay
close to the real shape than a flat one does. Every kernel operation
this book has used already performs a tessellation of its own, quietly,
every time a shape is drawn in the viewer – there is no other way to
put an exact B-Rep on a screen built from pixels.

## STL: A Surface, Tessellated

**STL** is the simplest mesh format this book will use, and the most
limited by design: a flat list of triangles, each one three points and
a normal direction, and nothing else. No topology connecting one
triangle to its neighbors, no units, no color, no history of how the
shape was built – just enough to describe a surface's shape, which is
exactly what a 3D printer's slicer needs and nothing more.

```python
from cadquery import func as cf

r_outer, wall, height = 9.0, 2.0, 65.0
outer = cf.cylinder(d=2 * r_outer, h=height)
inner = cf.cylinder(d=2 * (r_outer - wall), h=height)
cell_can = outer - inner

cell_can.exportStl("cell_can.stl", tolerance=0.1, angularTolerance=0.1)
```

Two settings control how closely the triangles follow the real surface.
`angularTolerance` bounds the angle between neighboring triangles along
a curve, in radians; tightening it from `0.8` to `0.02` on a plain
cylinder takes the tessellation from 208 triangles to 2512. `tolerance`
bounds the straight-line distance between a triangle's flat face and
the curved surface it approximates. By default, CadQuery scales that
distance by the size of each edge being meshed (`relative=True`) rather
than treating it as an absolute bound in millimeters; `relative=False`
makes it one. With `relative=False` on `cell_can` above, tolerance
values of `2.0`, `0.5`, `0.1`, `0.01`, `0.001` mm give `412`, `412`,
`412`, `716`, `2248` triangles. Smaller tolerance and smaller angular
tolerance both mean more triangles, and more triangles mean a larger
file.

An STL file only describes a shape a slicer can actually use if the
triangles close up into a watertight skin, with a well-defined inside
and outside and no gaps. A single, valid `Solid` tessellates into a
watertight mesh by construction, so the failure modes STL is known for
in practice – gaps, flipped normals, edges shared by more than two
triangles – trace back to a solid that was already broken before
tessellation. "Broken" here means
specifically what `isValid()` checks: topological consistency, not
whether the shape looks like the one intended. Chapter 7's pinched
sweep is the sharp counterexample – `isValid()` reports `True`,
`exportStl` succeeds without complaint, and the resulting STL is a
technically watertight mesh of a tube that still folds back through
its own wall. `isValid()` and `isinstance(..., Solid)` catch a boolean
that silently produced the wrong topological type; neither one checks
whether the geometry makes physical sense, and a slicer receiving a
self-intersecting but "valid" mesh like that one is on its own.

## Meshing for Simulation

A **finite-element mesh** fills a volume: tetrahedra packed through a
part's interior, not just triangles describing its skin, each
element coupled to its neighbors at a shared face or edge so a solver
can compute a quantity like stress or temperature across the whole
part rather than only its surface. Element size and element shape both
matter here directly – small enough, and regular enough, for the
numbers a solver produces on each element to actually mean something.
A flat face two large triangles describe perfectly well for STL still
needs dozens of small, evenly sized elements for a solver, not because
the shape needs explaining any better, but because the physics
computed across that face does.

:::{figure} ../figures/generated/ch10-stl-vs-fem.png
:width: 95%

The same plate, two meshes. Left: an STL tessellation – a couple of
large triangles on the flat faces, a denser ring only around the
curved hole, tuned purely for surface fidelity. Right: a finite-element
mesh of the same part – triangles and tetrahedra of a controlled,
roughly uniform size throughout, filling the interior a printer's
slicer never needed to see.
:::

Both meshes in that figure come from the same part. The left one is
the kernel's tessellation, the same one `exportStl` writes. The
right one comes from a different tool entirely, built for exactly the
uniform, interior-filling job STL was never meant for.

## Building the Mesh with Gmsh

**Gmsh** is the standard open-source tool for building the kind of mesh
a solver needs: triangles or tetrahedra of a controlled size, filling a
face or a volume rather than only describing its boundary, and it can
mesh a shape in either two or three dimensions from the same geometry.
**cadgmsh** is a thin wrapper that hands a CadQuery shape to Gmsh
directly and returns a `meshio.Mesh` object in Python.

```python
plate = cf.box(60, 40, 6)
hole = cf.cylinder(d=16, h=8).moved(z=-1)  # overshoots both faces
part = plate - hole
```

The hole cylinder is taller than the plate is thick, and shifted so it
overshoots both faces rather than landing exactly flush with either – a
habit worth adopting for cutting booleans in general: a cut that
overshoots cannot leave a zero-thickness sliver behind, and never asks
the kernel to decide the fate of two faces that coincide exactly.

```python
import cadgmsh
import pyvista as pv

surface_mesh = cadgmsh.mesh(part, dim=2, lc=5)
volume_mesh = cadgmsh.mesh(part, dim=3, lc=5)

pv.from_meshio(volume_mesh).plot(show_edges=True)
```

`dim=2` meshes only the part's faces – a flat mesh over each
surface, no interior, the natural choice for a thin plate or a shell.
`dim=3` fills the interior with tetrahedra as well, needed whenever the
solver's own equations act on a volume rather than a surface.
`lc`, characteristic length, is the target element size in millimeters
– the same fidelity-against-cost tradeoff `tolerance` was for STL,
except now the cost is solver time, not file size, and the reader
controls it directly rather than approximating it through a deflection
bound. **PyVista** reads the resulting mesh and renders it with its
element edges visible, whichever kind of mesh it is – the figure above
came from exactly this call, `plot(show_edges=True)` on each side.

## Maker Payoff: Printing the Clutch Brick

A real clutch brick is hollow underneath: the cavity is where the
brick below reaches in, and the cavity's inner walls are what grip
that brick's studs. This section adds the underside to Chapter 2's
`clutch_brick` – body and studs, taken over unchanged – and turns it
into a part a reader can print and click onto a real, physical brick:

```python
from cadquery import Solid


def clutch_brick(
    length: float,
    width: float,
    height: float,
    stud_diameter: float,
    stud_height: float,
    stud_spacing: float,
    wall: float = 1.2,
    roof: float = 1.0,
    grip_clearance: float = 0.0,
    post_diameter: float = 2.5,
) -> Solid:
    body = cf.box(length, width, height)
    stud = cf.cylinder(d=stud_diameter, h=stud_height)
    left_stud = stud.moved(x=-stud_spacing / 2, z=height)
    right_stud = stud.moved(x=stud_spacing / 2, z=height)

    cavity_width = stud_diameter - grip_clearance
    cavity_height = height - roof
    cavity = cf.box(length - 2 * wall, cavity_width, cavity_height + 1)
    cavity = cavity.moved(z=-0.5)
    hollowed = body - cavity

    post_height = cavity_height + 0.5
    post = cf.cylinder(d=post_diameter, h=post_height)

    result = hollowed + post + left_stud + right_stud
    assert isinstance(result, Solid)
    return result
```

A brick this narrow – one stud wide – does not carry the tube wider
bricks use to grip a stud from more than one side; there simply is not
room for one between walls this close together. The grip instead comes
from the two long inner walls of the cavity itself, spaced by
`cavity_width`, squeezing directly against a stud pressed up into them
from below; a center `post`, running the full depth of the cavity
between the two studs, adds the kind of reinforcement rib a real hollow
molded part carries against warping and sink marks, clear of the grip
channel on every side and clear of any real stud, which lands at
`stud_spacing / 2` off-center, not on the axis the post itself occupies.
The post's height overshoots into the roof by the same margin the cavity
already overshoots by – without that overshoot, the post is a
separate, disconnected solid floating inside the cavity rather than
part of the same part, exactly the `assert isinstance(result, Solid)`
two lines above exists to catch. `grip_clearance` states, directly, how
much narrower than
the stud that gap actually is: at `0` the fit is nominally line-to-line
with no interference at all; a real, physical stud probed against the
gap with a boolean intersection confirms it – `0.0` mm³ of overlap. Push
`grip_clearance` to `0.2` and the same probe shows `0.459` mm³ of real,
solid interference; at `0.4` it is `1.29` mm³ – a small number, but the
whole clutch mechanism the reader is about to print depends on it being
positive rather than zero or negative.

:::{figure} ../figures/generated/ch10-clutch-brick-cutaway.png
:width: 45%

The completed `clutch_brick`, rendered semi-transparent: the two studs,
the hollow cavity between the long grip walls, and the center
reinforcement post are all invisible from the outside otherwise.
:::

That number is also precisely what a 3D printer will not reproduce
exactly. FDM printers routinely print internal cavities a little
undersized and external features a little oversized relative to the
model that asked for them, an artifact of the nozzle's width and
the way each layer's outline is traced – printer-specific, and not
something this book can state a universal correction for. `grip_clearance`
is exactly the parameter to iterate against a real, physical result:
print the brick, try clicking it onto a real, commercially available
clutch brick, and adjust the number up if the fit is loose, down if the
printed walls do not flex enough to let the stud in at all. STL export,
from here, is a single call already familiar from earlier in this
chapter:

```python
brick = clutch_brick(15.6, 7.8, 9.6, 4.8, 1.7, 8.0, grip_clearance=0.15)
brick.exportStl("clutch_brick.stl", tolerance=0.05, angularTolerance=0.1, relative=False)
```

A model that clicks onto a real, physical part is a physical unit test
in the fullest sense this book has offered one: not `isValid()`
reporting `True`, not a volume matching an analytic formula, but a
printed part either gripping a real brick's stud or not.

:::{note} Try It
- Print `clutch_brick` at a couple of different `grip_clearance` values
  – `0.0`, `0.15`, `0.3` – and click each onto a real, commercially
  available clutch brick. Record which ones grip, which fall off, and
  which are too tight to press together at all; that range is your
  printer's real tolerance, not a number this book could have told you
  in advance.
- Mesh `clutch_brick` with `cadgmsh.mesh(brick, dim=3, lc=1)`, and view
  it in PyVista with `show_edges=True`. Where does the mesh get visibly
  denser without being asked to – and does that match where the part's
  geometry is most detailed?
- Export the same `cell_can` from this chapter at three tolerances –
  loose, moderate, tight – with `relative=False`, and compare both the
  file sizes and how the curved wall actually looks up close in the
  viewer. At what point does tightening the tolerance further stop
  changing what you can actually see?
:::
