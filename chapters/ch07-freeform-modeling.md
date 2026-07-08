# Freeform Modeling

% Status: drafting in progress. See private/book-plan.md §2 (Ch. 7) for
% the agreed structure. Source: CAx-Programmierung lecture 06 (sweep/loft
% mechanics) + the dropped final project (NACA rotor blade, harvested for
% the multisection/fairness example only - no spars, no hollowing, no
% FEM, per book-plan open decision #6).
%
% Explicitly rejected: framing this chapter by contrast against Ch. 3
% ("what extrude and revolve cannot do") - tried once, cut after direct
% feedback that it's the same "arguing against a version the reader
% never saw" tic flagged repeatedly elsewhere in this book, and that
% "X cannot do Y" is empty rhetoric unless Y already matters to the
% reader on its own. Sections open with positive content only - what
% sweep/loft ARE and DO - never a comparison to earlier chapters as the
% justification for a section existing. Same rule for figure captions
% and any "thread"/"this book's own running X" meta-language pointing
% at earlier chapters - be concrete and self-contained instead (e.g.
% name the actual earlier part, like Ch. 4's tray, rather than an
% abstract "thread").
%
% Current sections, per book-plan: Sweep (path frames, transition,
% compact tube example; serpentine channel demoted to Try It) - Loft
% (duct transition as the canonical example, pack lid as a 2-3 sentence
% coda only) - Multisection Loft and Surface Fairness (NACA airfoil +
% curvature-fairness audit, honest craft note) - Try It.
%
% "Periodic Sections and a Fusion Vessel" (W7-X capstone) was drafted,
% corrected repeatedly (physics causality, plasma-boundary-vs-vessel
% conflation, a half-period-mirror bug, a full-period-pattern G0 kink
% measured directly at ~22% relative tangent mismatch, a diagnostic-
% code-in-textbook mistake, and finally figures that still weren't
% usable after several honest attempts) and, after all that, CUT by
% David on 2026-07-08 - not close enough to shippable, not worth further
% iteration right now. Full content preserved in
% private/ch07-w7x-vessel-backup.md for a possible future revival (a
% correct periodic-surface fit is the real fix; `cf` doesn't reach it).
% Consequence: this chapter no longer redeems Ch. 1's "impossible to
% click together" promise - that is an open question again, see
% book-plan.md §8. Do not re-add the W7-X section without a genuinely
% different, more tractable plan than what's in the backup file.
%
% Verification discipline matches Ch. 6: every claim checked against
% cf/OCP before writing, every figure generated from numbers verified
% that way first. Note from the W7-X attempt: verifying a claim before
% writing it and putting the verification CODE in the book are different
% questions - only show code the reader would want to reproduce or learn
% from, never a one-off diagnostic built purely to check a claim.

## Sweep: A Profile Carried Along a Path

A **sweep** carries a profile along a path curve, the path's own
tangent direction deciding how the profile is placed and reoriented the
entire way. A profile at the very start of a path needs exactly that
local frame – which way is "along the path," which way is "up" – built
from the same `positionAt` and `tangentAt` Chapter 6 used to read a
point and a direction off a curve:

```python
from cadquery import func as cf

path = cf.polyline((0, 0, 0), (30, 0, 0), (30, 30, 0), (60, 30, 0))
p0 = path.positionAt(0.0, mode="length")
t0 = path.tangentAt(0.0, mode="length")

plane = cf.Plane(p0, (0, 0, 1), t0)
profile = cf.face(cf.wire(cf.circle(12.0))).located(plane.location)
tube = cf.sweep(profile, path)
```

`tube.isValid()` reports `True`. It is also, visibly, wrong: the path
above bends twice at a right angle, and the swept tube pinches down to
almost nothing at the second bend, the wall folding back through itself
– a real defect `isValid()` does not catch, because it checks
topological consistency, not whether the shape looks like the one asked
for. The default `transition="transformed"` places the profile on the
plane bisecting each pair of incoming and outgoing path directions; at a
gentle bend that plane cuts a clean miter, but sharpen the bend enough
and the same bisector plane slices back through the tube's own incoming
wall before the joint, which is exactly the fold in the render above.

Two other transition modes handle the same sharp bend without pinching:

```python
tube_right = cf.sweep(profile, path, transition="right")
tube_round = cf.sweep(profile, path, transition="round")
print([f.geomType() for f in tube_right.Faces()])
print([f.geomType() for f in tube_round.Faces()])
```

Both keep the three straight segments as plain `CYLINDER` faces, the
same type Chapter 6 already established for any straight extrusion of a
circle; where they differ is the joint itself. `transition="right"`
squares each joint off instead of mitering it – the two neighboring
cylinders meet directly along a sharp seam, no extra face needed.
`transition="round"` fills the same two joints with a genuine curved
patch instead, `REVOLUTION` appearing in the face list exactly twice,
once per bend, where `right` has none. Both build a solid a bent pipe or
duct actually could be; `transformed` remains the right default for
gentle bends, where it is cheaper and the miter is not worth avoiding,
but a sharp enough turn is exactly the kind of thing worth rendering and
looking at before trusting `isValid()` alone.

:::{figure} ../figures/generated/ch07-sweep-transitions.png
:width: 95%

The same profile, the same two-bend path, three transition modes. Left
(`transformed`, the default): the tube pinches shut at the sharp second
bend – a self-intersection `isValid()` does not flag. Middle (`right`):
a clean squared-off elbow. Right (`round`): a clean rounded elbow.
:::

A path with more than one profile along it is a **multisection sweep**
– sweep and loft's own hybrid, the profile changing shape at each
station while still following an explicit path rather than loft's
implicit straight-line interpolation between stations. Placing the
*end* profile is where Chapter 6's two parameter modes stop being an
academic distinction: `path` above is a `Wire` built from three
straight edges, each with its own local parameter range starting back
at $0$, so `path.positionAt(1.0, mode="parameter")` silently lands at
the end of the *first* edge – thirty millimeters along a
ninety-millimeter path – not the end of the path a reader would expect.
`mode="length"`, the one Chapter 6 built by integrating and inverting
arc length precisely so it means the same thing everywhere along a
curve, has no such seam to trip over:

```python
p1 = path.positionAt(1.0, mode="length")
t1 = path.tangentAt(1.0, mode="length")

profile_start = cf.face(cf.wire(cf.circle(12.0))).located(plane.location)
profile_end = cf.face(cf.wire(cf.circle(5.0))).located(cf.Plane(p1, (0, 0, 1), t1).location)
tapered = cf.sweep([profile_start, profile_end], path)
```

A tapered, bent duct in one call – `cf.sweep` accepts a sequence of
profiles exactly where it accepted one, no separate API to learn. The
rest of this chapter leans on the plain single-profile form; a duct
whose shape needs to change while its path also curves is the kind of
part this option exists for.

## Loft: Interpolating Between Profiles

**Loft** drops the path entirely: given a handful of profiles, each
already placed wherever it belongs, the solid connecting them comes from
interpolating a surface through all of them at once. The profiles do
not need to be resized copies of each other – a duct that connects a
round inlet to a rectangular outlet needs exactly two genuinely
different shapes, not two sizes of the same one:

```python
bottom = cf.wire(cf.circle(25.0))
top = cf.wire(cf.rect(60.0, 40.0)).translate((0, 0, 80))

duct = cf.loft([bottom, top], cap=True)
print(duct.isValid(), [f.geomType() for f in duct.Faces()])
```

`True`, and `['BSPLINE', 'BSPLINE', 'BSPLINE', 'BSPLINE', 'BSPLINE',
'PLANE', 'PLANE']` – five lateral patches stitched together to carry
the circle smoothly into the rectangle's four straight sides and
rounded corners, plus the two flat end caps `cap=True` adds. Every
lateral patch comes back `BSPLINE`, ruled or not, for the same reason a
plain circle needed `BSPLINE` the moment Chapter 6 asked it to become a
NURBS surface: nothing about a circular cross-section is expressible in
the straight-line patches a ruled loft would otherwise prefer.

:::{figure} ../figures/generated/ch07-duct-transition.png
:width: 38%

A round-to-rectangular duct transition – `loft` between a circle and a
rectangle, capped at both ends. Neither profile is a resized copy of
the other.
:::

`ruled` and `continuity` are still exactly the arguments Chapter 6's
surface math describes – `ruled=True` for a sheet-metal-formable duct
that can tolerate a visible seam at the transition, the smooth default
for one that cannot – and a loft can end in a single point instead of a
second profile: lofting a circle straight to a `cf.vertex` produces a
`CONE` outright, the same analytic type `cf.cone` itself builds,
confirming a cone really is nothing more than a degenerate loft.

The tray Chapter 4 built for a battery cell could use a lid: loft
between a rounded rectangle at the base and a smaller rounded rectangle
at the top, drafted inward, then one call to `cf.hollow` for wall
thickness – no different in kind from the duct above, just a gentler
taper. Chapter 12 returns to this same lid and makes it structural,
rib-stiffened rather than a plain cover; here it is only worth naming.

