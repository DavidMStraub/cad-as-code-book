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
% coda only) - Multisection Loft: A Curved Spine of Profiles (a swept,
% tapered wing with a winglet, built from a cf.spline spine +
% positionAt/tangentAt frames + loft - see below) - Try It.
%
% Multisection/wing section: went through several real corrections,
% worth recording so they aren't repeated. (1) First draft used a flat
% linear taper+washout wing (no spine curve) as the vehicle for a
% curvature-fairness demo extending Ch. 6's curvature comb to a surface
% isoline - killed because (a) it leaned on real aerodynamics domain
% claims (washout rationale, boundary-layer sensitivity, quarter-chord
% "aerodynamic center") neither of us can personally verify, violating
% the book's own evidence rule, and (b) the actual result was a
% non-event (nothing wiggled, gentle taper never gives loft anything to
% struggle with) - a lot of unverifiable setup for no payoff. (2)
% Rebuilt around David's own idea: a spine curve (cf.spline) carrying
% sweep + an upward winglet bend, profiles placed on it via
% positionAt/tangentAt (reusing Sweep's own technique), then loft - a
% real composition of three already-taught pieces, no new aerodynamics
% claims needed. First attempt at this broke visibly (a self-
% intersecting, folded shape) because spine points were written as
% (span, sweep, bend) tuples but cf.spline reads 3-tuples as literal
% (X,Y,Z) - a real coordinate-labeling bug, fixed by writing
% (x_sweep, y_span, z_bend) consistently. (3) The spine's own v=0.0
% endpoint tangent came back pointing in a wrong/misleading direction -
% the same "free ends are untrustworthy" fact Ch. 6 already established
% for interpolating splines, now recurring naturally; fixed by placing
% the root/tip stations at frac=0.001/0.999 rather than exactly 0.0/1.0,
% and this became real, honest content rather than a hidden workaround.
% (4) Wing scale: asked for "A380-scale", corrected to "A350-scale" -
% used approximate, order-of-magnitude dimensions (half-span ~32m, LE
% sweep ~32deg) explicitly labeled as illustrative, not certified
% aircraft data, matching the book's no-fabricated-facts rule. (5) THE
% CURVATURE-FAIRNESS AUDIT ITSELF WAS CUT ENTIRELY, twice-corrected
% first (my own diagnostic/wiggle-counting code had ended up verbatim
% in draft textbook prose - same mistake as the W7-X section, caught
% again) then cut outright on David's explicit instruction ("The same
% check I SAID I DON'T WANT") - replaced with one short, generic,
% honest caveat paragraph that ALSO now defined "fairness" in plain
% language, since the heading used the word but nothing in the body
% explained it once the audit was gone (David: "What is fairness even").
% Section heading changed from "...and Surface Fairness" to "A Curved
% Spine of Profiles" to match what the section actually does now.
%
% (6) Even the standalone caveat paragraph was itself wrong, David caught
% it again: it read as "here's how to build a wing... just kidding, you
% can't really build wings in CAD" - undercutting the section's own
% point instead of scoping it, and not earned by anything the section
% actually demonstrated once the audit was gone. Fixed by cutting the
% whole paragraph and folding one clause into the sentence that was
% already hedging the dimensions ("not copied from a certified
% drawing... neither is the surface itself held to any aerodynamic
% tolerance - the technique carries over regardless"). Section now ends
% on the built wing and the figure, not a disclaimer. General lesson:
% a caveat has to scope the achievement, not retroactively cancel it -
% if a closing paragraph makes the reader feel the preceding section was
% pointless, that is the wrong caveat even if every word in it is true.
% Lesson for future sections: do not add a verification/audit unless it
% is going to survive to the final draft - if in doubt, state the
% concept in one honest sentence rather than build (and then have to
% strip out) a whole demonstration.
%
% Figure (ch07_wing.py): camera framing needed the geometry itself
% rotated to a known orientation (planform angle computed from the
% bounding box, rotated to lie along +X, then tilted to reveal the
% winglet) rather than hunting for a pyvista azimuth/elevation offset by
% trial - repeated trial-and-error on camera angle alone did not
% converge and wasted time; rotating the shape to a deterministic target
% orientation did, on the first try.
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
% 2026-07-11: intro paragraph added; naca4_points was USED but never
% DEFINED in the chapter (reader could not reproduce the wing) - the
% function is now a listing, restructured so Black-92 doesn't shred the
% formula lines, verified point-for-point identical to ch07_wing.py's
% version; the claimed "maximum camber 0.04" was wrong (it is 0.02 -
% the chapter even said "camber 2%" one line later; verified
% numerically, peak at x=0.396 of the cosine-spaced samples, thickness
% 0.12 peak at x=0.297); stale "Chapter 12 returns to this same lid,
% rib-stiffened" sentence cut (Ch. 12's FEM example is the cell holder,
% the rib lid never happened); "X's own" tic swept; new figure
% ch07_airfoil.svg (2D NACA 2412 outline with camber line and thickness
% marked - readers who have never seen an airfoil get the vocabulary
% the wing section uses). Re-verified this session: transformed tube
% isValid()==True despite the pinch; right = 3 CYLINDER + 2 PLANE, no
% REVOLUTION; round = same + exactly 2 REVOLUTION; positionAt(1.0,
% mode="parameter") -> (30,0,0) vs mode="length" -> (60,30,0); duct
% 5 BSPLINE + 2 PLANE; loft circle-to-vertex -> ['CONE'].
% Exercise feasibility checked same day (David asked): the lid exercise
% as previously written was NOT solvable - cf.hollow on the lofted
% rounded-rect lid returns an INVALID shape in every variant tried
% (kind="intersection": silent no-op, volume unchanged; kind="arc":
% plausible volume 7366 but isValid()==False; walls 1.0 and 1.5 alike).
% The working route, now the one the exercise teaches: subtract an
% inner loft of inward-offset rounded rectangles - valid, 7362.9 mm^3,
% 19 faces. The Loft-section coda no longer names cf.hollow as "one
% call" (falsified for exactly this geometry); the exercise hints
% cf.fillet2D (face.vertices() compound, NOT a Python list - a list
% raises AttributeError) and turns the hollow trap into an isValid()
% check. Exercise 1 rewording: ch4's exercise builds hex-packed POCKETS
% in a tray, not a standing cell grid - now says "seat cells in the
% hex-packed tray"; viewer-only overlap check replaced by
% zero-intersection-volume in code.
%
% Verification discipline matches Ch. 6: every claim checked against
% cf/OCP before writing, every figure generated from numbers verified
% that way first. Note from the W7-X attempt: verifying a claim before
% writing it and putting the verification CODE in the book are different
% questions - only show code the reader would want to reproduce or learn
% from, never a one-off diagnostic built purely to check a claim.

Extrude pushed a profile along a straight line; revolve spun one
around a fixed axis. This chapter adds the two operations that free
the profile from both constraints: sweep, which carries it along an
arbitrary path curve, and loft, which fits a surface through a
sequence of profiles placed anywhere in space. The closing section composes
them with Chapter 6's curves into a genuinely freeform part – a
swept, tapered airliner wing that curves up into a winglet.

## Sweep: A Profile Carried Along a Path

A **sweep** carries a profile along a path curve, the path's
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
and the same bisector plane slices back through the tube's incoming
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
– a hybrid of sweep and loft, the profile changing shape at each
station while still following an explicit path. Placing the
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
at the top, then hollow the result out for wall thickness – no
different in kind from the duct above, just a gentler taper. Building
it is one of this chapter's exercises.

## Multisection Loft: A Curved Spine of Profiles

Two sections are enough to connect a circle to a rectangle. A **wing**
needs more, and not only because its cross-section – an aerodynamic
profile, not a circle or a rectangle – changes size from root to tip.
Many wings sweep back and curve upward into a **winglet** near the tip,
a visible feature on most modern airliners: the stations a loft needs
are not spaced along a straight line at all, but along a curve. That
curve is exactly what Chapter 6's interpolating spline already builds,
and placing a profile on it at a chosen point is exactly what this
chapter's Sweep section already did with `positionAt` and
`tangentAt` – a wing is those two pieces composed, not a new technique.

A wing section, or **airfoil**, is not an arbitrary curve. The
**NACA four-digit** family, published by the National Advisory
Committee for Aeronautics in the 1930s and still in everyday use,
defines one from three digits alone: maximum camber, its position
along the **chord** – the straight line from the leading edge to the
trailing edge, against whose length everything else is measured – and
maximum thickness. Both ingredients are short closed-form functions: a
camber line the profile bends along, and a thickness distribution laid
perpendicular to it,

```python
import math


def naca4_points(code, n=60):
    m, p, t = int(code[0]) / 100, int(code[1]) / 10, int(code[2:]) / 100
    xs = [0.5 * (1 - math.cos(math.pi * i / n)) for i in range(n + 1)]

    def thickness(x):
        poly = 0.2969 * math.sqrt(x) - 0.1260 * x - 0.3516 * x**2 + 0.2843 * x**3
        return 5 * t * (poly - 0.1036 * x**4)

    def camber(x):
        if x < p:
            return m / p**2 * (2 * p * x - x**2), 2 * m / p**2 * (p - x)
        k = m / (1 - p) ** 2
        return k * ((1 - 2 * p) + 2 * p * x - x**2), 2 * k * (p - x)

    upper, lower = [], []
    for x in xs:
        yc, dyc = camber(x)
        theta, yt = math.atan(dyc), thickness(x)
        upper.append((x - yt * math.sin(theta), yc + yt * math.cos(theta)))
        lower.append((x + yt * math.sin(theta), yc - yt * math.cos(theta)))
    return list(reversed(lower)) + upper[1:]
```

one outline, on a chord running from $0$ to $1$, traced from the
trailing edge around the leading edge and back. The cosine spacing in
`xs` concentrates sample points near the leading edge, where the
curvature is highest. Evaluating the two ingredient functions at their
peaks is a direct check on the transcription: for `'2412'`, maximum
camber $0.02$ at $x = 0.4$ and maximum thickness $0.12$ near
$x = 0.3$ – camber $2\%$ at $40\%$ chord, thickness $12\%$, exactly
the three digits the name promises.

:::{figure} ../figures/generated/ch07-airfoil.svg
:width: 75%

The NACA 2412 outline `naca4_points` produces, with its two
ingredients drawn in: the camber line (dashed), peaking at $2\%$ of
chord at $x=0.4$, and the thickness distribution, $12\%$ of chord at
its widest, laid perpendicular to the camber line.
:::

The **spine** – the curve the wing bends along – is built the same way
Chapter 6 built any interpolating curve: a handful of points, one
`cf.spline`. Sweep angle and the winglet's upward bend are both just
coordinates in that short list, not separate parameters to compute:

```python
SWEEP_DEG, HALF_SPAN = 32.0, 32000.0
sweep = math.tan(math.radians(SWEEP_DEG))

spine_pts = [
    (0, 0, 0),
    (HALF_SPAN * 0.5 * sweep, HALF_SPAN * 0.5, 0),
    (HALF_SPAN * 0.90 * sweep, HALF_SPAN * 0.90, 100),
    (HALF_SPAN * 0.97 * sweep + 300, HALF_SPAN * 0.97, 900),
    (HALF_SPAN * 0.97 * sweep + 900, HALF_SPAN, 2400),
]
spine = cf.spline(spine_pts)
```

Placing a profile at a point along it needs a frame – which way is
"along the spine," which way is "up" – and `positionAt`/`tangentAt`
already answer that:

```python
pts01 = naca4_points("2412")

def profile_at(frac, chord):
    p = spine.positionAt(frac, mode="length")
    t = spine.tangentAt(frac, mode="length")
    plane = cf.Plane(p, (1, 0, 0), t)
    pts = [(x * chord, y * chord) for x, y in pts01]
    return cf.wire(cf.spline(pts)).located(plane.location)
```

The very first station is worth placing a fraction of a percent inside
the spine's start, not exactly on it: a global interpolating
spline's endpoint tangent is whatever the solver's end condition
produces, the same free-end fact Chapter 6 established, not necessarily
the direction the curve appears to be heading a moment later. Evaluating
`spine.tangentAt(0.0, ...)` directly returns a real but misleading
direction here; `0.001` does not:

```python
stations = [(0.001, 9500), (0.35, 6500), (0.65, 4200),
            (0.85, 2600), (0.95, 1500), (0.999, 700)]
wing = cf.loft([profile_at(f, c) for f, c in stations], cap=True)
print(wing.isValid(), [f.geomType() for f in wing.Faces()])
```

`True`, and `['BSPLINE', 'PLANE', 'PLANE']` – six stations, a chord
tapering from nine and a half meters at the root to well under a meter
at the winglet tip, lofted into one solid. The dimensions are chosen to
match the scale of a real widebody airliner wing, not copied from a
certified drawing, and neither is the surface itself held to any
aerodynamic tolerance – the technique carries over regardless.

:::{figure} ../figures/generated/ch07-wing.png
:width: 95%

A swept, tapered wing curving up into a winglet at the tip, six stations
lofted into one solid – root at the left.
:::

:::{note} Try It
- Seat cells in the hex-packed tray from Chapter 4's exercises and
  thread a coolant channel between them: a `cf.sweep`'d tube along a
  path that bends around the cells rather than through them,
  `transition="round"` at each turn. Check the clearance in code rather
  than by eye: the tube's intersection with every cell should come back
  with zero volume.
- Build the lid this chapter's Loft section described: a rounded
  rectangle at the tray's base (`cf.fillet2D`, applied to a face's
  vertices, rounds the corners), a smaller one at the top, lofted, with
  the wall made by subtracting a second loft of inward-offset profiles.
  If you reach for `cf.hollow` as the shortcut instead, run `isValid()`
  on what it hands back before trusting it. Place the lid over the
  Chapter 4 tray in the viewer and confirm it closes over the pockets
  rather than cutting into them.
- Change the wing's spine: move its last control point to a sharper bend
  or a taller rise and re-loft. At what bend does `cf.loft` stop
  producing a valid solid, and does `isValid()` actually catch the point
  where it stops looking like a wing?
:::

