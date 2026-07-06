# Profiles into Solids

## From Flat to Solid

Every solid built so far has come from a primitive – a box, a cylinder –
already three-dimensional the moment it appeared. Most real parts are not
built that way. A far more common starting point is a flat outline, drawn
once, then given a third dimension by one of two operations: pushed
straight through space, or spun around an axis. The first is called
**extrude**; the second, **revolve**. Between them, these two operations
account for a large share of the solids in any mechanical design – a
bracket is an extruded outline, a bolt or a bottle is a revolved one – and
this chapter builds one part of each kind.

Both operations start from the same kind of object: a flat, closed
outline lying in a plane, called a **profile**. A profile is not a sketch
in the loose sense of a drawing – it is an exact **face**, the same kind of
object that already bounds every solid this book has built, just one that
happens to be flat and not yet part of any solid. Where does a profile
live in space? By default, in the plane that already has a name from
Chapter 1's discussion of coordinate axes: the **XY plane**, spanned by the
x- and y-axes at height zero. CadQuery gives this plane, and two others
used constantly enough to deserve their own names, ready-made constants:

```python
from cadquery import Plane

Plane.XY()   # the ground plane: spanned by x and y, normal along z
Plane.YZ()   # spanned by y and z, normal along x
Plane.ZX()   # spanned by z and x, normal along y
```

A **Plane** is more than a flat surface: it carries an origin, a normal
direction, and an in-plane orientation, which together fix a complete
local coordinate frame in space. A profile drawn "on" a plane inherits that
frame – its own x and y directions are the plane's, and when it is later
extruded or revolved, the direction of that operation is measured against
the plane's normal. For everything up to the last section of this chapter,
`Plane.XY()` is the only plane needed, and it works exactly as global x and
y already do; the richer uses of `Plane` appear once there is a reason for
them.

## Extrude: A Profile Pushed Straight Up

The simplest profile is a rectangle, and the simplest use of extrude
reproduces something already familiar:

```python
from cadquery import func as cf

profile = cf.face(cf.rect(27, 148))
housing = cf.extrude(profile, (0, 0, 91))
```

`rect` builds a rectangular *outline* of the given width and length,
centered on the origin, lying in the XY plane – a closed chain of edges
called a **wire**, not yet a surface. `face` turns that outline into the
flat surface it encloses, which is what actually makes it a profile: a
face, not a wire, is what `extrude` and `revolve` both expect. `extrude` itself takes a profile and a *direction* to push it
in – a vector, not a plain number – so `(0, 0, 91)` pushes the profile 91
millimeters straight up in z; a tilted vector would push it off at an
angle instead, producing a slanted prism rather than a straight one. (A
third, optional argument, `both`, extrudes symmetrically in both
directions from the profile's own plane instead of only forward from it.)

The result is a box, 27 by 148 by 91 millimeters: the dimensions of a real
lithium-ion battery cell of the 100-amp-hour class, in the format called
**prismatic** – built in a flat, rectangular metal or laminate case, rather
than the round metal can most people picture at the word "battery." The
flat shape gives up a little of a cylindrical cell's structural simplicity
in exchange for packing far more tightly against its neighbors, which is
why prismatic cells are common wherever many of them are stacked into a
pack, as in an electric vehicle. This housing is the shape this chapter
builds throughout.

:::{figure} ../figures/generated/ch03-housing.png
:width: 36%

The extruded housing: 27 by 148 by 91 millimeters.
:::

Nothing about this result could not have been written directly as
`cf.box(27, 148, 91)`; extrude and a primitive box agree exactly when the
profile is a plain rectangle and the push runs straight along its normal.
The two stop agreeing the moment the profile is anything else – a shape
with a notch, a chamfered corner, an outline traced point by point – and
that is the case extrude exists for. This chapter's second worked shape,
later in the chapter, is exactly such a case.

% Verify against installed CadQuery 2.8: exact keyword names and default
% centering behavior for cf.rect (extrude's own signature is confirmed:
% extrude(s: Shape, d: VectorLike, both: bool = False, ...) -> Shape).

For an outline with no simple name, a profile can be built point by point
and closed into a face directly:

```python
points = [
    (0, 0), (27, 0), (27, 10), (20, 10),
    (20, 148 - 10), (27, 148 - 10), (27, 148), (0, 148),
    (0, 0),
]
outline = cf.polyline(*points)
notched_profile = cf.face(outline)
```

`polyline` connects a sequence of points with straight segments into a
wire, the same kind of outline `rect` produces; the last point repeats the
first to close the loop, exactly as it must, or the result is an open
outline `face` cannot turn into a surface. Curved segments – arcs, splines
– close into faces the same way, once joined into a single closed outline;
the profile a face is built from need not be straight-edged at all. Passed to `extrude` exactly as the rectangle was,
this notched outline would produce a housing with a notch running its
full height, which no single primitive shape could produce directly. The
housing built for this chapter does not need one, and keeps the plain
rectangular profile; the notched version above exists only to show that
extrude's real domain is broader than a box.

## A Plane Derived from a Face

The housing is only half a battery cell. A real prismatic cell has two
terminals on its top face, and placing them raises a question Chapter 2's
plain offsets could not quite answer: Chapter 2 built a stud on top of a
brick by computing its height by hand – half the body's height plus half
the stud's – and offsetting from the global origin. That works as long as
the body's own height is known and fixed. The moment the housing's
thickness becomes a variable – which, being a real design, it eventually
will – every offset computed against global coordinates has to be
recomputed by hand alongside it. There is a more durable way to say the
same thing: *put the terminal on the housing's top face*, whatever height
that face currently happens to be at.

```python
top_face = housing.faces(">Z")
top_plane = Plane(origin=top_face.Center())
```

`Center` returns the centroid of a face – its geometric middle – as a
point in space; `Plane`, given only an origin, keeps its default normal of
straight up in z, which is exactly right here, because the top of this
housing faces straight up. The plane this produces sits exactly on the
housing's top surface, wherever that surface is, because it was read from
the housing itself rather than computed alongside it. Change the housing's
height, and `top_plane` moves with it automatically; nothing about the
terminals needs to be touched.

Placing something on that plane, offset from its center, combines two
locations – the plane's own placement, and a further offset within it –
with `*`:

```python
from cadquery import Location

terminal = cf.cylinder(d=8, h=5)
left_terminal = terminal.moved(Location(top_plane) * Location((0, -48.5, 0)))
right_terminal = terminal.moved(Location(top_plane) * Location((0, 48.5, 0)))

cell = housing + left_terminal + right_terminal
```

`Location(top_plane)` alone is the plane's own position and orientation –
its origin on the housing's top surface, its "up" along the plane's
normal. Composing it with `Location((0, -48.5, 0))` by multiplication adds
a further offset *measured in that plane's own local coordinates*: 48.5
millimeters along the plane's own y-direction, which, for a flat,
upward-facing plane like this one, is the same as global y, but would
follow the plane's own tilt if the face it came from were tilted instead.
Composing the two locations this way, rather than passing the offset
straight into `Location`'s own constructor alongside the plane, matters:
that single-step form discards the plane's origin entirely and places the
result at the raw offset in global coordinates – exactly the kind of
mistake that is easy to make and easy to miss, since the code still runs
without error. The two terminals land 97 millimeters apart, symmetric
about the housing's center, sitting on top of it rather than embedded in
it or floating above it – and every one of these facts remains true no
matter what the
housing's own dimensions later become. This is **design intent** again,
in a new form: the terminals' construction records *where they belong
relative to the housing*, not a pair of numbers that happened to be
correct once.

:::{figure} ../figures/generated/ch03-cell-with-terminals.png
:width: 36%

The housing with both terminals placed on its top face.
:::

## Revolve: A Profile Spun Around an Axis

A profile can also become a solid by turning, rather than pushing.
**Revolve** sweeps a profile through a full circle – or part of one –
around an axis, and the result is exactly the kind of rotationally
symmetric shape a lathe produces: a bolt, a bottle, a cylindrical battery
cell. The profile revolve needs looks nothing like the ones used for
extrude so far. It is not the shape being built, but a **half** of the
shape's cross-section – the outline traced by a single straight line from
the axis outward to the object's surface and back, at one fixed angle.
Spin that outline through 360 degrees and it sweeps out the full solid;
draw the *whole* cross-section instead of half of it, and revolving it
would try to occupy the same space twice.

Concretely, this section builds a **cylindrical** battery cell – the round
metal can most people already picture at the word "battery," scaled up,
and the format used in laptops, power tools, and many electric vehicles.
Cylindrical cells are sold in standardized sizes named after their own
dimensions: a cell coded **18650** is, by that code alone, eighteen
millimeters across and sixty-five millimeters tall – the "18" and the
"650" are the diameter and the height, in millimeters and tenths of a
millimeter, respectively. This section builds exactly that cell, with a
narrower terminal knob at the top. Its half-profile is a stepped outline
in a single plane containing the axis: out to the cell's radius, up the
full height of the body, in to the terminal's narrower radius, up the
short height of the knob, and back to the axis to close the shape.

```python
r_cell, h_cell = 9.0, 65.0
r_terminal, h_terminal = 2.5, 1.0

points = [
    (0, 0, 0),
    (r_cell, 0, 0),
    (r_cell, 0, h_cell - h_terminal),
    (r_terminal, 0, h_cell - h_terminal),
    (r_terminal, 0, h_cell),
    (0, 0, h_cell),
    (0, 0, 0),
]
half_profile_outline = cf.polyline(*points)
half_profile = cf.face(half_profile_outline)
```

Each point here has three coordinates, not two, and the middle one – y –
is zero throughout: the profile must lie in a plane that *contains* the
axis it will be spun around, not one perpendicular to it, or the sweep
spins the flat profile inside its own plane instead of standing it up into
a solid. The x-coordinate carries the radius, distance out from the axis;
the z-coordinate carries height along it; y stays at zero, placing the
whole profile in the XZ-plane, which does contain the vertical z-axis used
below. Revolving turns that radius coordinate into an actual radius,
sweeping every point on the outline through its own circle around the
axis. A point on the profile at radius $r$ and height $h$
traces out a full circle as the sweep angle $\varphi$ runs from $0°$ to
$360°$:

$$x = r\cos\varphi, \qquad y = r\sin\varphi, \qquad z = h$$

the height staying exactly where it was while the radius becomes the
horizontal distance from the axis at every angle around it – the same
relationship Chapter 6 examines in more general form, for surfaces that
are not simply swept in a circle.

```python
cell = cf.revolve(half_profile, (0, 0, 0), (0, 0, 1))
```

The axis is given as two separate arguments: a point it passes through,
and a direction it points in – here, the origin and straight up in z, so
the profile's radius coordinate sweeps out circles centered on the
vertical axis, exactly as intended. A fourth, optional argument gives the
swept angle; left unspecified, it defaults to a full 360 degrees, and the
same call with an explicit smaller angle would produce a wedge instead of
a full solid, useful for showing an interior cutaway without hiding it
behind more material.

:::{figure} ../figures/generated/ch03-18650-cell.png
:width: 10%

The revolved 18650 cell, with its narrower terminal knob at the top.
:::

## Rotation, and Why Order Matters

Translation, from Chapter 2, moves a shape without turning it. The
remaining kind of movement is rotation, and it introduces something
translation never has to worry about: the order two movements happen in
can change the result.

A shape's own orientation is changed the same way its position was:

```python
rotated = terminal.moved(rz=45)
```

`moved` accepts translation and rotation together, as separate keyword
arguments – `x`, `y`, `z` for position, `rx`, `ry`, `rz` for rotation in
degrees about the x-, y-, and z-axes. A rotation by angle $\theta$ about
the z-axis leaves every point's z-coordinate untouched and turns its x and
y together, counterclockwise when viewed from above:

$$x' = x\cos\theta - y\sin\theta, \qquad y' = x\sin\theta + y\cos\theta, \qquad z' = z$$

`rz` supplies exactly this $\theta$, in degrees; `rx` and `ry` are the same
rotation, written about the other two axes instead. Whether `rx`, `ry`,
and `rz` are given together in a single call or applied through several
chained `moved` calls, each one always turns the shape about the
*original* x-, y-, and z-axes – the ones fixed in space from the start –
never about axes that have already been tilted by an earlier rotation in
the same sequence. This is the same choice a much older piece of
vocabulary names: an **extrinsic** Euler angle is one measured about fixed
axes, as here; an *intrinsic* Euler angle is measured about axes that
rotate along with the object being turned, which is not what `moved` does.
Given together, the three combine as three fixed-axis rotations applied in
a set order – first about x, then y, then z – which as a single matrix
acting on a point is the product

$$R = R_z(rz) \, R_y(ry) \, R_x(rx),$$

read right to left, innermost first: a point is rotated about x, then
about y, then about z, all three axes fixed throughout, never the
shape's own tilting frame.

A second, easy-to-miss fact matters just as much: a rotation turns a shape
about whichever point currently sits *at the origin* – not about the
shape's own center, unless that center already happens to be there.
Passing both a translation and a rotation to one `moved` call applies them
as a single combined step; calling `moved` twice in sequence applies them
as two separate steps, one after the other – and because rotation is
anchored at the origin rather than at the shape itself, the order of those
two steps changes where the shape ends up, not only how it is turned.

```python
a = cf.box(20, 5, 5).moved(rz=90).moved(x=30)   # rotate, then move
b = cf.box(20, 5, 5).moved(x=30).moved(rz=90)   # move, then rotate
```

Both boxes are rotated 90 degrees and moved 30 millimeters from the same
starting shape, using the same two numbers – yet `a` and `b` end up in
different places. The box starts centered on the origin, so rotating it
first only turns it – its center has nowhere to go, since it is already
sitting at the point the rotation pivots around. The translation that
follows then carries this rotated box 30 millimeters along the world's x,
landing its center at $(30, 0, 0)$. Moving first tells a different story:
the box slides 30 millimeters along x while still unrotated, so its center
now sits away from the origin, at $(30, 0, 0)$ – and the rotation that
follows swings the *whole box*, center included, about the origin rather
than about that point, carrying the center to $(0, 30, 0)$ instead. The
box ends up in a different place not because rotation and translation are
arbitrary about order in general, but because rotation is never about the
object – it is always about the origin.

This also explains how to rotate a part about its own center on purpose:
move the center to the origin, rotate, then move it back.

$$T_{p} \circ R \circ T_{-p}$$

translating by $-p$ first, so the point $p$ that should stay fixed sits at
the origin during the rotation, then undoing that translation afterward.
Written as operations more generally, a translation $T$ and a rotation $R$
compose to $T \circ R$ in one order and to $R \circ T$ in the other, and

$$T \circ R \;\neq\; R \circ T$$

in general – exactly the difference between `a` and `b` above. Two
translations, by contrast, always commute – $T_1 \circ T_2 = T_2 \circ
T_1$, whichever is applied first, the final position is the same – which
is why Chapter 2 never had to think about the order of a sequence of
moves. Rotation is the first operation in this book where sequence is
part of the meaning, not just a detail of how the code happens to be
written, and there is no substitute for checking, in the viewer, that a
chain of placements has landed a part where it was meant to go.

:::{note} Try It
- Extrude `notched_profile` instead of the plain rectangle and compare the
  housing's face count to the plain box's from Chapter 2. How many new
  faces did the notch add?
- Change the housing's height and re-run the terminal placement code
  without changing a single number in it. Confirm in the viewer that the
  terminals stay on the top surface.
- Reduce the 18650 half-profile's swept angle from a full circle to 270
  degrees and view the result. Which part of the cell is now visible that
  was hidden before?
- Build the two boxes from the order-of-operations example and measure the
  distance between their centers. Predict the distance before running the
  code, then check.
:::
