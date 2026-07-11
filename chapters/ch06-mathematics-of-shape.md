# The Mathematics of Shape

% Status: chapter drafted in full, Curves as Parametric Functions
% through Surfaces. See private/book-plan.md §2 (Ch. 6) and §8.1 for
% the open depth-control decision, and
% private/CAx-Programmierung - 03/04 Geometrie I/II.md for the source
% lectures this chapter draws its formulas and worked examples from
% directly. This is a math chapter: formulas carry the argument, code
% verifies specific claims after each one rather than doing the
% explaining itself - keep that ratio in any further drafting.
% Every figure in the chapter is generated (figures/ch06_*.py) from
% numbers independently verified against the real kernel (OCP/OCCT
% directly where the func API doesn't reach, e.g. the NURBS weights
% example) before being drawn - keep that discipline for Surfaces too.
% Merges lectures 03+04 into one continuous argument rather than the
% course's two-week split. Section 2's ellipse offset is deliberately
% undersold on first appearance - the new curve type (OFFSET) is a thin,
% cheap wrapper, not a complicated object, and the section says so
% plainly rather than pretending otherwise. The real escalation (degree
% 2 to degree 12, one edge to four, once expressed as NURBS) is the
% payoff at the end of the NURBS section, cashing in the forward
% pointer left at the end of §2. Canonical home (per the book-plan's
% lookup table) for curve/surface math, NURBS, and continuity; must be
% self-contained enough for a reader who jumps in here directly.
% 2026-07-11: intro paragraph added; two stale "Fourier series" capstone
% references fixed to the NACA wing Ch. 7 actually builds (the Fourier
% cross-sections belonged to the cut W7-X vessel); the two
% \begin{cases} formulas rewritten in side-condition form - the
% tex-to-typst bug noted below is STILL live (verified in the built PDF:
% both formulas rendered as "N =" with nothing after), and the rewrite
% renders correctly everywhere rather than waiting on upstream;
% Cox-de Boor subsection moved from the NURBS section into Building
% Curves (it defines B-spline machinery; NURBS's opening no longer
% leans on a "previous subsection" that had drifted anyway); "Curve
% Properties in CadQuery" heading and two in-prose "CadQuery"s
% reworded per the keep-the-brand-out-of-prose rule; "X's own" tic
% swept. Spot-re-verified this session: ellipse length 97.01 /
% curvatures 0.2, 0.025; offset edges all OFFSET; cylinder face
% uvBounds (0, 2pi, 0, 30), positionAt (5,0,15), normalAt (1,0,0);
% loft CONE,CONE vs BSPLINE; cf.fillet(box, edges, r) -> PLANE,
% CYLINDER, SPHERE.
% Same day, per David: Surfaces opening expanded - u,v explained as
% coordinates ON the surface (plane -> in-plane x,y; sphere ->
% longitude/latitude; cylinder -> angle/height), isolines named, and
% the trimming asymmetry stated plainly (an edge trims with an interval;
% a face's boundary curves live in the (u,v) domain and are isolines
% only in special cases - plate-with-hole top face as the worked
% contrast). New figure ch06_surface_uv.py: the smooth loft with its
% isoline grid overlaid (sampled via Face.positionAt, near-white lines
% like the ch05 seam figure; u/v arrows + labels drawn in image space
% with PIL - in-scene VTK labels were unreadable and screenshot(scale=2)
% drops 2D text actors).
% Parameter-range claim verified three levels deep (David asked, since
% build123d always shows [0,1]): Geom_CylindricalSurface.Value(pi, 15)
% = (-5, 0, 15), BRepTools.UVBounds = (0, 2pi, 0, 30), and cq
% Face.positionAt(pi, 15) matches - cq passes OCCT's native parameters
% through unchanged; the loft face's [0,1]x[0,1] is the B-spline knot
% range, also native. build123d's position_at normalizes to [0,1] as a
% wrapper convention - Appendix B phrasebook material, not for this
% chapter's prose.
% Try It box added 2026-07-11 (the chapter had no exercises - the only
% content chapter without them). All three verified solvable in this
% environment first: sphere uvBounds (0, 2pi, -pi/2, pi/2), torus
% (0, 2pi, 0, 2pi); single 5-pt spline curvature varies smoothly
% around the middle data point (0.199 -> 0.207 across +-0.5% of
% length) while two splines joined there disagree (0.0143 vs 0.0089,
% and tangents mismatch - G0 joint); closed-profile offset2D returns
% CIRCLE + OFFSET edges (10 total), the CIRCLEs being arc joins at the
% closure corner. A fourth candidate (read the fillet patch's NURBS
% degree/rational flags, "a fillet is the exact-circle machinery") was
% DROPPED: BRep_Tool on the fillet's toNURBS gives UDegree 2 /
% VDegree 1 but IsURational False / IsVRational True - a muddled
% orientation story that would confuse rather than teach; don't re-add
% without understanding why the rational flag lands on the linear
% direction. The old "direct analogue of what an Edge
% carries" sentence was overclaiming exactly this point and is gone;
% also fixed a backward-looking tic in the normalAt sentence.
%
% Surfaces is a standalone "## Surfaces" heading, not a Continuity
% subsection, written with comparable rigor to the curve sections
% (parametric surfaces + the analytic family, sweep/loft as the surface
% analogue of control-point curves - forward-referencing Chapter 7's
% actual operations rather than teaching them here, NURBS surfaces via
% the cylinder-as-tensor-product example, surface continuity via
% fillet), self-contained enough that lifting it into its own chapter
% later, if book-plan §8.9 resolves that way, is a mechanical cut rather
% than a rewrite. Every claim checked directly against cf/OCP before
% writing, same discipline as the rest of the chapter (e.g. cf.cylinder
% takes diameter not radius, verified by positionAt; ruled vs. smooth
% loft geomTypes; toNURBS degree/pole counts on a cylinder).

Chapter 5 said what an edge and a face carry – a curve, a surface, and
the parameter ranges that trim them – and left the mathematics of those
curves and surfaces open. This chapter fills it in: what a parametric
curve is, and what tangent, arc length, and curvature mean on one; why
the analytic curves run out the moment a real operation touches them;
how control points, B-splines, and NURBS build the representation the
rest of CAD stands on; and what continuity between the pieces means,
with the places it genuinely matters. The same story restated one
dimension up – surfaces – closes the chapter.

## Curves as Parametric Functions

### Explicit, Implicit, and Parametric Curves

Chapter 3 built every profile from straight segments. Curved edges –
arcs, splines – close into faces exactly the same way, and this chapter
is about what a curve actually is: there is more than one honest way to
write one down, and CAD kernels settled on one of them for a specific,
checkable reason.

Take the simplest curved shape there is – a circle of radius $R$, lying
flat in a plane and centered on the plane's origin – and ask how to
write it down. The everyday answer from school algebra is **explicit**:
$y$ as a function of $x$,

$$y = \pm\sqrt{R^2 - x^2}.$$

It already needs the $\pm$ to cover both halves of the circle, and it
breaks down entirely at $x = \pm R$, where the tangent is vertical and $y$
stops being a function of $x$ at all in the neighborhood. An **implicit**
equation avoids that particular failure,

$$x^2 + y^2 - R^2 = 0,$$

covering the whole circle at once, no sign ambiguity anywhere – but it
states a relation a point either satisfies or does not, not a rule for
producing points. There is no natural place to start walking around the
circle, no built-in notion of "the next point," and finding even one point
that satisfies it is its own small problem. A third option sidesteps both
difficulties by introducing a parameter:

$$x = R\cos u, \qquad y = R\sin u, \qquad u \in [0, 2\pi).$$

Every value of $u$ gives exactly one point; every point on the circle
comes from exactly one $u$; and walking $u$ steadily from $0$ to $2\pi$
traces the whole circle in order, tangent included, nothing breaking down
anywhere. This is the **parametric** form, and it is the only one of the
three a CAD kernel actually stores – not because the other two are wrong,
but because a parametrization is the only form that answers "what point is
a third of the way around?" or "which direction is the curve heading
here?" without extra machinery bolted on afterward. The circle above sat
in a single plane, $z$ fixed at whatever height that plane happened to
be, but nothing about the parametric idea depends on that – $x(u)$ and
$y(u)$ simply carry a third companion, $z(u)$, free to vary or not.
Every curve this book builds from here on – lines, circles, ellipses now,
splines and NURBS later – is exactly this idea, a function from a single
number to a point in space,

$$\mathbf{C}(u) = \begin{pmatrix} x(u) \\ y(u) \\ z(u) \end{pmatrix}, \qquad u \in [u_{\min}, u_{\max}],$$

boldface marking a three-component vector throughout this chapter, as it
does for $\mathbf{C}$ here and for the tangent, normal, and curvature
vectors that follow it. Every `Edge` in a B-Rep, Chapter 5's vocabulary
filled in properly now, carries exactly this: a curve, plus the parameter
interval that trims it to a finite piece.

A parametrization makes several questions cheap to answer: what point
sits at a given $u$, and which direction the curve is heading there; how
far apart, along the curve, two parameter values actually are; how
sharply the curve is bending at a point. Each has a direct answer in
terms of $\mathbf{C}(u)$ and its derivatives, worked out over the rest of
this section.

### Tangent and Arc Length

The **tangent vector** is the derivative of the parametrization,

$$\mathbf{T}(u) = \mathbf{C}'(u) = \frac{d\mathbf{C}}{du},$$

pointing in the curve's instantaneous direction of travel at $u$. Its
*length* is a "speed" in parameter space, not a physical one, and depends
entirely on how the curve happens to be parametrized – a fact the rest of
this section makes precise.

The **arc length** between two parameter values is the actual distance
traveled along the curve, found by integrating that speed:

$$s(u) = \int_{u_0}^{u} \bigl|\mathbf{C}'(\tilde u)\bigr|\, d\tilde u, \qquad \frac{ds}{du} = |\mathbf{C}'(u)|.$$

A curve is **arc-length parametrized** when $s$ itself is used as the
parameter, which forces $|d\mathbf{C}/ds| = 1$ – unit speed, everywhere, by
construction. This is the geometrically "natural" way to walk a curve,
equal parameter steps always covering equal distance – but it is
expensive to obtain: $s(u)$ is an integral with no guarantee of a closed
form, and inverting it back into a usable parameter is a second, separate
difficulty.

A circle sidesteps both problems. Its speed, worked out in full in the
next subsection, is the constant $|\mathbf{C}'(u)| = R$, so the integral
collapses to the elementary $s(u) = Ru$ – arc length is just the radius
times the angle swept, no integration needed in practice. An ellipse
offers no such shortcut: with $\mathbf{C}(u) = (a\cos u,\, b\sin u)$,

$$|\mathbf{C}'(u)| = \sqrt{a^2\sin^2 u + b^2\cos^2 u},$$

and

$$s(u) = \int_0^{u} \sqrt{a^2\sin^2 \tilde u + b^2\cos^2 \tilde u}\; d\tilde u$$

is an *elliptic integral* – historically the very problem that gave that
whole family of functions its name – with no elementary closed form at
all. Arc length, in general, is not something a curve's formula hands
over for free; it has to be found numerically, for the whole curve, every
time it is needed.

### Curvature

**Curvature**, $\kappa$, measures how fast the tangent direction turns per
unit distance traveled – how sharply the curve bends, independent of how
it happens to be parametrized. In arc-length terms it is a second
derivative,

$$\kappa = \Bigl|\frac{d^2\mathbf{C}}{ds^2}\Bigr|,$$

and for an arbitrary parametrization, the chain rule together with
Lagrange's identity turns this into a formula that needs no
reparametrization to use:

$$\kappa(u) = \frac{\bigl|\, \mathbf{C}'(u) \times \mathbf{C}''(u) \,\bigr|}{\bigl|\, \mathbf{C}'(u) \,\bigr|^{3}}.$$

A straight line has $\kappa = 0$ everywhere – it never turns. A circle of
radius $R$ has $\kappa = 1/R$ everywhere, the reciprocal relationship
behind curvature's usual companion, the **radius of curvature**
$R_\kappa = 1/\kappa$: the radius of the one circle that best hugs the
curve at that single point, tangent to it and matching its bend exactly –
the curve's **osculating circle** there.

:::{figure} ../figures/static/curvature.svg
:width: 50%

A curve $\mathbf{C}$, a point $\mathbf{P}$ on it, and its osculating
circle there: tangent to the curve, perpendicular to the radius vector,
and matching the curve's bend exactly – radius $R_\kappa$, the radius of
curvature at $\mathbf{P}$.
:::

The circle confirms the formula for free. With
$\mathbf{C}(u) = \mathbf{M} + R(\cos u,\, \sin u)$,

$$\mathbf{C}'(u) = R(-\sin u,\, \cos u), \qquad \mathbf{C}''(u) = -R(\cos u,\, \sin u),$$

so $|\mathbf{C}'(u)| = R$ for every $u$ – already the constant speed used
above – and the cross product's magnitude works out to $R^2$, also
constant, giving

$$\kappa(u) = \frac{R^2}{R^3} = \frac{1}{R}$$

at every point, exactly what curvature ought to mean for the one curve
whose bend never changes.

An ellipse is where curvature stops being constant, and the same
derivation, run on $\mathbf{C}(u) = (a\cos u,\, b\sin u)$, shows exactly
why:

$$\kappa(u) = \frac{ab}{\bigl(a^2\sin^2 u + b^2\cos^2 u\bigr)^{3/2}}.$$

At the two ends of the major axis ($u = 0, \pi$), $\sin u = 0$ and the
formula collapses to $\kappa = a/b^2$ – the *sharpest* the ellipse ever
turns. At the two ends of the minor axis ($u = \pi/2, 3\pi/2$), it
collapses instead to $\kappa = b/a^2$ – the *flattest*. With $a = 20$ and
$b = 10$, that is $\kappa = 0.2$ at the pointed ends, a tight
$5$-millimeter radius of curvature, against $\kappa = 0.025$ at the round
ends, a slack $40$ millimeters – an eightfold difference on a single,
ordinary curve.

### Reading Curve Properties in Code

Every formula above is independent of any particular software. This
section asks one narrow, practical question: once a curve exists,
wrapped in an `Edge` as Chapter 5 described (a curve plus the parameter
interval that trims it), how does code actually read $\mathbf{C}(u)$,
$\mathbf{T}(u)$, and $\kappa(u)$ back off it? The library answers through
the edge's `positionAt`, `tangentAt`, and `curvatureAt`. Two distinct
parameters are on offer for the $u$ these methods take, and they are not
interchangeable. `mode="parameter"` is the curve's own formula parameter,
the plain $u$ used throughout this section and the one thing the kernel
actually stores and evaluates the curve in terms of – cheap, exact, no
different from plugging a number into $\cos u$ and $\sin u$ by hand. The
default, `mode="length"`, is not a second native representation but a
convenience built on top of the first: a fraction, from $0$ to $1$, of
the curve's total arc length – found by integrating $s(u)$ over the whole
curve and then numerically inverting that integral to locate the matching
$u$, redone from scratch on every call, since the kernel never stored the
curve this way to begin with.

```python
from cadquery import func as cf

ellipse = cf.ellipse(20.0, 10.0)
circle = cf.circle(10.0)

print(ellipse.geomType(), ellipse.Length())
print(circle.curvatureAt(0.0), circle.curvatureAt(0.3), circle.curvatureAt(0.7))
print(ellipse.curvatureAt(0.0), ellipse.curvatureAt(0.25))
```

`ELLIPSE`, and a length of `97.01` millimeters, the elliptic integral
paid in full since it has no closed form to shortcut. The circle's
curvature is `0.1` at all three points regardless of which parameter is
meant, since a circle's speed never varies and the two modes coincide.
The ellipse's is `0.2` and `0.025`, matching the derived formula exactly
– though `0.25` here means a quarter of the curve's length, not a quarter
turn of $u$; it lands near the minor-axis end only because, for this
particular ellipse, the two happen to be close.

The gap between the two parameters is easy to underestimate. At points
near the pointed end and near the round one, in both modes:

```python
import math

p1, p2 = ellipse.positionAt(0.10), ellipse.positionAt(0.11)
p3, p4 = ellipse.positionAt(0.50), ellipse.positionAt(0.51)
q1, q2 = ellipse.positionAt(0.0, mode="parameter"), ellipse.positionAt(0.05, mode="parameter")
q3 = ellipse.positionAt(math.pi / 2, mode="parameter")
q4 = ellipse.positionAt(math.pi / 2 + 0.05, mode="parameter")

print((p2 - p1).Length, (p4 - p3).Length)
print((q2 - q1).Length, (q4 - q3).Length)
```

In length mode, a $0.01$ step covers close to `0.97` millimeters both
times – one percent of the curve, wherever it is taken, the uniform-speed
guarantee that mode is built to pay for. In parameter mode, the same
$0.05$-radian step covers `0.50` millimeters near the pointed end and
`1.00` near the round one – twice as far for the same nominal step,
exactly $ds/du = |\mathbf{C}'(u)|$ failing to be constant. Neither mode is
wrong; `mode="parameter"` is cheap and silent about distance,
`mode="length"` is what a toolpath or a hand tracing the curve actually
experiences, and its cost is the arc-length machinery this section built,
paid again on every call. Both facts are worth pinning down as the kind
of check Chapter 2 introduced, so a future edit that breaks either
assumption announces itself:

```python
assert abs(circle.curvatureAt(0.0) - 1 / 10) < 1e-9
assert abs((p2 - p1).Length - (p4 - p3).Length) < 0.01
```

## The Limits of Analytic Curves

Lines, circles, and ellipses belong to a small, closed family: the
**conics**, curves that appear as a plane's intersection with a cone,
sharing enough structure that a kernel can represent each exactly – a
formula, not an approximation of one. It is tempting to
assume that family is closed under the operations a model actually needs,
the way it is closed under trimming: cutting a curve down to a sub-range
of its own parameter keeps it exactly the curve it always was, just
shorter. **Offset** is a different story. An offset curve is built by
pushing every point of $\mathbf{C}(u)$ a constant distance $d$ outward
along its own local unit normal $\hat{\mathbf{n}}(u)$ – the curve
counterpart of Chapter 2's `translate`:

$$\mathbf{C}_{\text{offset}}(u) = \mathbf{C}(u) + d\,\hat{\mathbf{n}}(u).$$

Whether that formula reduces to something nameable depends entirely on how
$\hat{\mathbf{n}}(u)$ behaves – and the previous section already
worked out exactly that, for both curves in play here. A circle's normal
always points straight through its center, turning at the same
constant rate curvature promised; an ellipse's normal does not, since its
curvature – the earlier $0.2$ against $0.025$ – is not constant either.

A circle offsets the way that constancy predicts:

```python
circle_offset = cf.offset2D(cf.wire(circle), 3.0)
edge = circle_offset.Edges()[0]
print(edge.geomType(), edge.radius())
```

`CIRCLE`, radius `13.0` – exactly the original 10 millimeters plus the
3-millimeter push, because a circle pushed outward everywhere really is
just a bigger circle, concentric with the first. Run the identical
operation on the ellipse from the previous section:

```python
ellipse_offset = cf.offset2D(cf.wire(ellipse), 3.0)
print([e.geomType() for e in ellipse_offset.Edges()])
```

Every edge in the result prints `OFFSET` – not `ELLIPSE`, not any other
conic – though, as the figure below shows, nothing about the result
looks obviously wrong.

:::{figure} ../figures/generated/ch06-curve-offsets.png
:width: 90%

A circle and an ellipse (dark blue), each offset outward by the same 3
millimeters (orange). The circle's offset stays exactly concentric and
circular; the ellipse's does not stay an ellipse, even though the two
curves look almost alike at a glance.
:::

`ellipse_offset.isValid()` is `True`, and the curve is exact and
fully usable, evaluable at any parameter to full precision, curvature and
all – it is simply not, by any choice of the two radii, an ellipse.
Lines, circles, and ellipses are the entire vocabulary this book has for
a curve so far, three names covering every analytic edge built through
Chapter 5, and offsetting the plainest of the three by a plain 3
millimeters already produces a curve none of the three names, or any
combination of them, can describe. Conics are closed under trimming and,
one special case aside, nothing else; a family this small was never
going to survive contact with the operations a real design needs.
Building a curve representation general enough to hold whatever an
operation like this actually produces – not just offset, but sweep,
loft, and every construction still ahead in this book – is what the rest
of this chapter does.

## Building Curves from Control Points

A wing section traced point by point from the NACA airfoil formula – the
kind Chapter 7's capstone actually builds – has no hope of matching any
curve this book has named so far, not even after the family from the
previous section is stretched to include every offset and every trim of
every conic. What is needed is not one more named formula to add to the list,
but a way of writing curves that was never a short list to begin with:
shapes described directly by the points that should pull them into place,
with no fixed equation deciding in advance what kind of bend is possible.

### The Power Basis and Bezier Curves

The most direct way to let a curve's coefficients be freely chosen is
the **power basis** – writing each coordinate as an ordinary polynomial in
$u$:

$$\mathbf{C}(u) = \sum_{i=0}^n \mathbf{a}_i\, u^i = \mathbf{a}_0 + \mathbf{a}_1 u + \mathbf{a}_2 u^2 + \cdots + \mathbf{a}_n u^n.$$

Given enough terms it can be bent through almost any smooth shape a
designer might want to draw, approximately rather than exactly. Even
granting it that shape, the power basis is unusable in practice, for
three separate reasons. The coefficients $\mathbf{a}_i$ carry no
geometric meaning of
their own; nothing about $\mathbf{a}_3$, read in isolation, says where on
the curve its effect actually shows up. At high degree the curve's shape
grows acutely sensitive to small changes in any one coefficient, the same
numerical fragility behind the Runge phenomenon, where a high-degree
polynomial forced through many data points oscillates wildly between them
rather than following them smoothly. And reshaping the curve on purpose
means solving a linear system for a new set of coefficients, not an
operation anyone can do by eye. What is needed is a basis whose parameters
are themselves points in space.

Pierre Bézier, working at Renault on computer-aided automobile body
design, published exactly that in 1962, and it shipped in Renault's
UNISURF system by 1968. A **Bézier curve** is written directly in terms of
$n+1$ **control points** $\mathbf{P}_0, \ldots, \mathbf{P}_n$:

$$\mathbf{C}(u) = \sum_{i=0}^n B_{i,n}(u)\, \mathbf{P}_i, \qquad B_{i,n}(u) = \begin{pmatrix} n \\ i \end{pmatrix}\, u^i (1-u)^{n-i}, \quad u \in [0, 1],$$

the $B_{i,n}(u)$ the **Bernstein basis polynomials** of degree $n$. They
are never negative on $[0,1]$, since each factor $u^i$, $(1-u)^{n-i}$, and
$\begin{pmatrix} n \\ i \end{pmatrix}$ is, and they sum to exactly $1$ at every $u$ – the binomial
theorem applied to $(u + (1-u))^n$ reads

$$\sum_{i=0}^n B_{i,n}(u) = \sum_{i=0}^n \begin{pmatrix} n \\ i \end{pmatrix} u^i (1-u)^{n-i} = \bigl(u + (1-u)\bigr)^n = 1,$$

which is exactly what "the weights of a weighted average" requires. That
makes $\mathbf{C}(u)$, at every parameter value, a **convex combination**
of the control points, and confines the whole curve to the convex hull of
its control polygon, never overshooting past the outermost points no
matter how the interior ones are placed. At $u=0$, $B_{0,n}(0)=1$ and
every other basis function vanishes, so the curve starts exactly at
$\mathbf{P}_0$; by the same argument at $u=1$ it ends exactly at
$\mathbf{P}_n$. Degree $n=1$ gives a straight segment between two points;
$n=2$ a parabola pulled toward one interior point; $n=3$ the cubic curve
most CAD systems reach for by default, four control points each pulling
the curve toward themselves, none of them – other than the first and last
– ever actually touched by it. The three side by side, squares marking
the two points the curve actually reaches and circles marking the ones
that only pull on it:

:::{figure} ../figures/generated/ch06-bezier-degrees.svg
:width: 90%

Degree 1, 2, and 3 Bézier curves and their control polygons. A cubic can
do something a parabola never can, no matter where its one interior
point is placed – bend one way, then the other, an inflection – because
it has two interior control points pulling in different directions
instead of one.
:::

In practice, $\mathbf{C}(u)$ is rarely evaluated by summing Bernstein
weights directly – at high degree that is exactly the numerically
fragile arithmetic the power basis was already rejected for. CAD systems
instead use **de Casteljau's algorithm**, repeated linear interpolation
between neighboring control points, reaching the same point through
nothing worse conditioned than averaging two points at a time.

The tangent direction at $\mathbf{P}_0$, asserted without proof above,
is a special case of a general fact: differentiating $\mathbf{C}(u)$
term by term shows that the derivative of a degree-$n$ Bézier curve is
itself a degree-$(n{-}1)$ Bézier curve, built from the *differences*
between consecutive control points,

$$\mathbf{C}'(u) = n \sum_{i=0}^{n-1} B_{i,n-1}(u)\, \bigl(\mathbf{P}_{i+1} - \mathbf{P}_i\bigr).$$

At $u=0$ only $B_{0,n-1}(0)=1$ survives, leaving
$\mathbf{C}'(0) = n(\mathbf{P}_1 - \mathbf{P}_0)$ – the scalar $n$ changes
only how fast the curve leaves $\mathbf{P}_0$, not which way, so the
tangent direction there is exactly $\mathbf{P}_1 - \mathbf{P}_0$, now a
consequence of the formula rather than a claim about it.

### Piecewise Bezier Curves

A Bézier curve fixes every one of the power basis's problems – each of
its parameters is a point a designer can see and drag – but a single
curve does not scale to an arbitrary free-form shape. The polynomial
degree is tied directly to the point count: a curve wanting twenty
control points is a degree-nineteen polynomial, back in exactly the
numerically fragile territory the control-point idea was meant to
escape. And every control point, however far from a given stretch of
curve, still influences the entire thing – the Bernstein basis functions
are nonzero across the whole interval $[0,1]$, so moving one point near
the start can visibly move the curve near the end.

The obvious fix is a **piecewise Bézier curve**: cut the shape into
several low-degree segments, each its own small Bézier curve, joined end
to end. Two cubic segments, $\mathbf{a}(u)$ with control points
$\mathbf{a}_0,\ldots,\mathbf{a}_3$ and $\mathbf{b}(u)$ with control
points $\mathbf{b}_0,\ldots,\mathbf{b}_3$, meeting where $\mathbf{a}(1)$
becomes $\mathbf{b}(0)$, show what joining segments smoothly actually
requires. Matching position alone pins one point,

$$\mathbf{a}_3 = \mathbf{b}_0;$$

matching tangent direction too – using the derivative formula above at
each segment's end, $\mathbf{a}'(1)=3(\mathbf{a}_3-\mathbf{a}_2)$ and
$\mathbf{b}'(0)=3(\mathbf{b}_1-\mathbf{b}_0)$ – forces a second,

$$\mathbf{b}_1 = 2\mathbf{b}_0 - \mathbf{a}_2,$$

$\mathbf{b}_1$ now the mirror image of $\mathbf{a}_2$ through the shared
joint rather than a free choice; and matching curvature as well forces a
third,

$$\mathbf{b}_2 = 4\mathbf{b}_0 - 4\mathbf{a}_2 + \mathbf{a}_1,$$

leaving $\mathbf{b}_3$ as the only one of the second segment's four
control points still actually free. Three of four points at every
interior joint, spent the moment real smoothness is required – and that
requirement is not arbitrary: optics and toolpaths both follow curvature,
not just tangent direction, so a jump in it shows just as plainly as a
kink would.

That is a fair trade for a curve with a handful of segments, tuned by a
person one at a time – which is exactly why piecewise Bézier curves,
nothing more elaborate, are still what SVG paths, PostScript and
TrueType font outlines, and every vector illustration tool use for
two-dimensional artwork; the figure below traces one such outline,
control handles and all, directly from the font this page is set in.
The kernel underneath this book's tools
keeps the curve as a first-class citizen too: `BEZIER` is a real
`geomType` in its own right, distinct from `BSPLINE` – the shape a
reader would meet importing a STEP file authored directly in Bézier
form, Chapter 5's foreign-file promise made concrete for a curve type
this book has had no reason to build by hand.

:::{figure} ../figures/static/bezier-handles.svg
:width: 45%

The lowercase "c" of this book's body font, Linux Libertine, traced
as twelve cubic Bézier segments. Every anchor (square or diamond) is
itself a control point – the shared $\mathbf{a}_3=\mathbf{b}_0$ of two
neighboring segments – and the handles extending from it are those
segments' remaining control points, $\mathbf{a}_2$ and
$\mathbf{b}_1$. At the square anchors the two handles are exactly
collinear through the point, the mirrored $\mathbf{b}_1 = 2\mathbf{b}_0 -
\mathbf{a}_2$ derived above, tangent-continuous by construction; at the
diamond anchors they point in unrelated directions, tangent continuity
deliberately not enforced there.
:::

The trade stops being fair at scale. A CAD surface wants not a handful
of segments but potentially thousands of control points, generated and
edited by software as much as by a person, every interior joint paying
the same three-of-four cost a font's dozen anchor points barely notice.
A B-spline is what removes that cost at scale: continuity built into the
basis functions themselves, needing no equations solved by hand at all.

### B-Splines: Knots and Local Control

Everything in this subsection generalizes the last one rather than
replacing it – a Bézier curve turns out to be one particular B-spline,
not a different kind of object, a fact the end of this subsection makes
precise. It sits at a specific point between the two extremes the
previous subsection already built. A piecewise Bézier curve gives every
span a private set of control points – four, for cubic segments –
touching no other span's. A single Bézier curve is the opposite extreme:
one span, every control point governing it at once. A B-spline curve is
what a real overlap between those two looks like: each span is still
governed by exactly as many control points as a Bézier segment of the
same degree would need, but neighboring spans' windows of control points
overlap, sharing all but one – the next span drops the oldest point in
the window and picks up one new one, a slide of exactly one control
point at a time rather than a clean break. That shared, sliding overlap
is where the automatic continuity later in this subsection actually
comes from, not a looser blend of the two extremes. A **B-spline curve**
replaces the single, whole-interval Bernstein basis with a set of basis
functions that are each nonzero over only a small stretch of $u$:

$$\mathbf{C}(u) = \sum_{i=0}^n \mathbf{P}_i\, N_{i,k}(u),$$

$n+1$ control points as before, paired now with an **order** $k$ – one
more than the polynomial degree, so $k=4$ for the cubic curves CAD
systems favor – and a **knot vector** $T = (t_0, \ldots, t_{n+k})$, a
non-decreasing sequence of parameter values that cuts $[t_0, t_{n+k}]$
into the polynomial pieces the curve is actually built from, one $u$-span
at a time. The basis functions $N_{i,k}(u)$ are defined by a recursion
over degree; the general recursive step is worth having on hand once,
in its own subsection later in this chapter, but its first two rungs
are simple enough to see directly. Degree $0$ (order $k=1$) is a bare
step function, equal to $1$ on exactly one knot span and $0$ everywhere
else,

% Formulas deliberately written in side-condition form, not
% \begin{cases}: mystmd's typst math export (via the bundled
% tex-to-typst) drops cases content entirely - both formulas rendered
% as "N = " with nothing after the equals sign in the built PDF, still
% reproducible 2026-07-11 - and \left\{...\right. crashes the typst
% compile. If the upstream bug is ever fixed, these could be folded
% back into cases form, but the side-condition form is correct and
% renders in every target.

$$N_{i,0}(u) = 1 \ \text{ for } t_i \le u < t_{i+1}, \qquad N_{i,0}(u) = 0 \ \text{ otherwise},$$

and degree $1$ (order $k=2$), reached by combining two neighboring steps,
is a triangular "hat", zero outside its two spans, rising linearly
across the first and falling linearly across the second:

$$N_{i,1}(u) = \frac{u - t_i}{t_{i+1}-t_i} \ \text{ for } t_i \le u < t_{i+1}, \qquad N_{i,1}(u) = \frac{t_{i+2}-u}{t_{i+2}-t_{i+1}} \ \text{ for } t_{i+1} \le u < t_{i+2}.$$

Three control points $\mathbf{P}_0, \mathbf{P}_1, \mathbf{P}_2$ and the
clamped knot vector $T=(0,0,1,2,2)$ – the endpoints repeated to order
$k=2$ – make this concrete. $N_{0,1}(u)=1-u$ on $[0,1)$, $N_{1,1}(u)$
rises as $u$ on $[0,1)$ and falls as $2-u$ on $[1,2)$, and
$N_{2,1}(u)=u-1$ on $[1,2)$; at $u=0.5$, only $N_{0,1}$ and $N_{1,1}$ are
nonzero, giving $\mathbf{C}(0.5) = 0.5\,\mathbf{P}_0 + 0.5\,\mathbf{P}_1$
– the plain midpoint of the first control-polygon edge – and at $u=1.5$,
symmetrically, the midpoint of the second. An order-$2$ B-spline is
nothing more exotic than its own control polygon, traced segment by
segment; the recursion only starts to do real work once $k$ grows past
this.

Two facts that matter for using a B-spline of any order follow from the
same construction. First, each $N_{i,k}$ is nonzero over only $k$
consecutive spans of the knot vector, so a single control point
$\mathbf{P}_i$ can only ever move
the curve within that stretch – moving a point near the start leaves the
far end of the curve completely untouched, the **local control** a Bézier
curve cannot offer at any degree. Second, continuity at each knot comes
automatically from the choice of $k$: an order-$k$ B-spline is
$C^{k-2}$ continuous everywhere its knots are simple, which is exactly
why cubic B-splines ($k=4$, so $C^2$) are the default in CAD software –
curvature continuity for free, without a single joint equation written by
hand.

:::{figure} ../figures/generated/ch06-basis-functions.svg
:width: 100%

The same-degree pair, drawn to the same scale: Bernstein basis functions
(left), every one of them nonzero across the entire curve, against a
cubic B-spline basis (right), each function confined to four knot spans.
Global support is why one Bézier control point moves the whole curve;
local support is why one B-spline control point does not.
:::

That difference on the curve itself, not just in the basis functions
behind it: the same seven points as above, moved the same way, once as
a single degree-6 Bézier curve and once as the cubic B-spline just
described.

:::{figure} ../figures/generated/ch06-control-comparison.svg
:width: 100%

The same seven control points, the same one point moved by the same
amount. Left: a single Bézier curve of degree 6 – every point on the
curve shifts, since $\mathbf{P}_1$'s Bernstein weight is nonzero
everywhere. Right: a cubic B-spline on the knot vector above – the curve
changes only up to the marked point, then is not merely similar but
identical, coordinate for coordinate, to the original.
:::

Repeating a knot in the vector is the deliberate way to spend some of
that free continuity back. A knot of multiplicity $m$ reduces continuity
there to $C^{k-1-m}$: multiplicity $1$ (a simple knot) leaves the standard
$C^{k-2}$; multiplicity $k-2$ drops the curve to merely tangent-continuous
there; multiplicity $k-1$ produces a genuine kink, exactly what an
ordinary Bézier joint would have shown at that point; and multiplicity
$k$ forces the curve through that exact control point, no longer just
attracted toward it. Repeating the very first and last knots $k$ times –
a **clamped** B-spline – is the standard way to make a curve actually
pass through its first and last control points, the way a Bézier
curve already does everywhere; without that repetition, a B-spline's
endpoints, like its interior, are only ever attracted toward the nearby
control points, never pinned to them.

Two extremes of that same knob resolve the promise made at the start of
this subsection. With no interior knots at all – $k$ control points, the
knot vector $(0,\ldots,0,1,\ldots,1)$, clamped at both ends and nowhere
else – there is only one span, one polynomial piece, and $N_{i,k}(u)$
turns out to equal $B_{i,k-1}(u)$ exactly: a single Bézier curve is a
B-spline with the plainest knot vector it is possible to write down, not
a different kind of object. Pushed to the opposite extreme – every
interior knot repeated $k-1$ times, dropping continuity to a bare $C^0$
at each one – a B-spline collapses instead into the piecewise-Bézier
curve the previous subsection gave up on. The two curves this chapter
has built by hand turn out to be the same one representation, evaluated
at its two opposite settings.

### Interpolating Curves Through Points

Every control point in this chapter so far has been a lever, not a
destination – even a clamped B-spline, the previous subsection's own
closing case, only pins its *first* and *last* control point onto the
curve; every point in between stays merely attractive, never actually
touched. That is fine when a designer is placing control points
directly, shaping a curve by feel. It is the wrong tool for a different,
equally common problem: a fixed set of points already exists – measured
off a physical part, read off a table, sampled from a formula like the
airfoil sections Chapter 7 builds – and what is needed is a curve that
passes through every one of them, exactly, not a curve merely herded
near them.

This is **interpolation**, and it is a different problem from everything
built so far in this chapter: given data points
$\mathbf{Q}_0, \ldots, \mathbf{Q}_n$, find control points
$\mathbf{P}_0, \ldots, \mathbf{P}_n$ and parameter values
$u_0 < \cdots < u_n$ such that $\mathbf{C}(u_i) = \mathbf{Q}_i$ for every
$i$. Fixing a degree, a knot vector, and the $u_i$ turns this into
$n+1$ linear equations in the $n+1$ unknown control points – each
equation just the basis-function sum from the very first formula of the
previous subsection, evaluated at one $u_i$ – solved once for every
control point together, not derived span by span the way the
piecewise-Bézier joint conditions were. The $u_i$ are not free:
the standard choice is **chord length**, $u_0 = 0$ and
$u_i = u_{i-1} + |\mathbf{Q}_i - \mathbf{Q}_{i-1}|$, so that two data
points far apart get proportionally more of the parameter range than two
points close together – a curve whose speed roughly tracks how far
apart its data actually is, rather than treating every gap as equally
wide.

`cf.spline` builds exactly this, and its numbers confirm it directly
rather than by name alone:

```python
import math
points = [(0, 0, 0), (10, 15, 0), (25, 5, 0), (40, 20, 0), (50, 0, 0)]
curve = cf.spline(points)

chord = [0.0]
for a, b in zip(points, points[1:]):
    chord.append(chord[-1] + math.dist(a, b))
print(chord)
```

Reading the curve's knot vector back off it needs the same direct
kernel access the exact-circle NURBS example later in this chapter
needs, and it matches this hand-computed list exactly:
`[0.0, 18.03, 36.06, 57.27, 79.63]` – chord length, not equal spacing,
with the first and last knots at multiplicity $4$, the clamped case from
the previous subsection, so the curve actually starts and ends at
$\mathbf{Q}_0$ and $\mathbf{Q}_4$. Evaluating the curve at each of those
four knot values returns each $\mathbf{Q}_i$ back exactly, to the full
precision the kernel computes with – the interpolation condition holding
in practice, not just in the equations that defined it. The control
points solved for to make that happen, read the same way, are not the
data points at all except at the two clamped ends: the interior poles
sit at points like $(1.76, 13.98, 0)$ and $(9.08, 20.53, 0)$, nowhere
near the $(10, 15, 0)$ and $(25, 5, 0)$ the curve is nonetheless forced
to pass through. Interpolation and control-point placement solve
opposite problems with the same machinery: one is given the curve's
shape and lets the points fall where the basis functions put them, the
other is given the points and solves backward for whichever control
polygon makes the curve hit them anyway.

:::{figure} ../figures/generated/ch06-spline-interpolation.svg
:width: 65%

The same five points as the code above, and the seven control points
`cf.spline` actually solves for. The curve (black) passes through every
data point $\mathbf{Q}_i$; the control polygon (blue) does not – only
$\mathbf{P}_0$ and $\mathbf{P}_6$, the clamped ends, coincide with a data
point at all.
:::

### Cox-de Boor Recursion

The step from $N_{i,0}$ and $N_{i,1}$, both given explicitly earlier, to
the cubic basis functions this chapter has been plotting and using ever
since is one formula, applied repeatedly:

$$N_{i,k}(u) = \frac{u - t_i}{t_{i+k-1} - t_i}\, N_{i,k-1}(u) \;+\; \frac{t_{i+k} - u}{t_{i+k} - t_{i+1}}\, N_{i+1,k-1}(u).$$

Each order-$k$ basis function is a weighted blend of two order-$(k-1)$
neighbors, the weights sliding linearly from $0$ to $1$ across the
interval each half spans – a direct generalization of the $N_{i,1}$
hat, which is exactly this blend applied to two order-$0$ steps. Every
property this chapter has used – the local support confined to $k$
spans, the automatic $C^{k-2}$ continuity, the knot-multiplicity table –
follows from this recursion, but reproducing that derivation adds
machinery without adding a usable fact: this book's basis-function
figures, and every claim resting on them, were computed with exactly
this formula, applied by code rather than by hand.

## NURBS: Rational Curves and Exact Shape

A B-spline contains Bézier as a special case – the no-interior-knots
extreme worked out above – but it still cannot do one perfectly
ordinary thing: trace an exact circle. The reason is not a shortcoming of any particular
construction – it is algebraic, and it holds for every polynomial
B-spline no matter how many control points or how high the degree.
Suppose $\mathbf{C}(t) = (x(t), y(t))$ is a polynomial curve of degree
$p$ in $t$, and suppose it traces a circle of radius $R$ exactly, so
that $x(t)^2 + y(t)^2 = R^2$ for every $t$, not just at a few sample
points. The left side is itself a polynomial in $t$, of degree at most
$2p$, and for it to equal the constant $R^2$ identically, every
coefficient above the constant term must vanish. But the leading
coefficient of $x(t)^2$ is the square of the leading coefficient of
$x(t)$ – never negative, and zero only if that coefficient already
was. The same holds for $y(t)^2$, and two non-negative numbers sum to
zero only if both do. Working down from the top degree, every
non-constant coefficient of both $x(t)$ and $y(t)$ is forced to zero in
turn, leaving $\mathbf{C}(t)$ a single fixed point, not a circle at all.
A polynomial curve can approximate a circle as closely as its degree and
control points allow; it cannot equal one.

**Rational** curves escape this by dividing one polynomial by another
rather than insisting on a single one. A **NURBS** curve – Non-Uniform
Rational B-Spline – attaches a **weight** $h_i > 0$ to each control
point:

$$\mathbf{C}(u) = \frac{\sum_{i=0}^{n} h_i\, \mathbf{P}_i\, N_{i,k}(u)}{\sum_{i=0}^{n} h_i\, N_{i,k}(u)}.$$

Setting every $h_i$ to the same value leaves the denominator equal to
$\sum_i N_{i,k}(u) = 1$ – partition of unity again – and the whole
expression collapses back to the ordinary B-spline from the previous
subsection: a NURBS curve generalizes a B-spline exactly the way a
B-spline generalizes a Bézier curve, one more link in the same chain.
The weights only do something new when they differ from each other, and
what they can do is trace a circle exactly. Three control points,
$\mathbf{P}_0=(1,0)$, $\mathbf{P}_1=(1,1)$, $\mathbf{P}_2=(0,1)$, and
weights $1$, $\sqrt2/2$, $1$, on a quadratic ($k=3$) NURBS curve, give a
quarter circle of radius $1$ – not approximately. Evaluated at every
parameter value, that curve sits at distance exactly $1.0000000000$ from
the origin, to the full precision the kernel underneath this book
computes with; the identical three control points and knot vector, every
weight set to $1$ instead, trace an ordinary polynomial B-spline that
bulges to radius $1.0607$ at its midpoint – six percent off, and no
placement of the control points fixes it, since the impossibility proof
above applies regardless. The weight on the middle point alone is what
pulls the curve back from that bulge to the exact arc.

:::{figure} ../figures/generated/ch06-nurbs-circle.svg
:width: 38%

The same three control points, the same knot vector, one number
different. The ordinary B-spline bulges visibly outside the true
quarter circle; the NURBS curve, weight $\sqrt2/2$ on $\mathbf{P}_1$
alone, sits exactly on it – not a closer approximation, the curve
itself.
:::

The free-function API has no direct constructor for a weighted
control-point curve like this one – `cf` builds circles and ellipses as
analytic edges outright, never needing NURBS to get them exactly right
in the first place – so this example is the one piece of geometry in the
chapter this book verifies against the kernel directly rather than
building through the API it otherwise teaches throughout.

This is what the offset ellipse from earlier in this chapter was
actually costing, invisibly, the whole time. Converting it to NURBS –
the same currency as every curve in this family, so degree and pole
count mean the same thing for all of them – reads the cost off directly:

```python
ellipse = cf.ellipse(20.0, 10.0)
ellipse_nurbs = ellipse.toNURBS()
print(len(ellipse_nurbs.Edges()))

offset = cf.offset2D(cf.wire(ellipse), 3.0)
offset_nurbs = offset.toNURBS()
print(len(offset_nurbs.Edges()))
```

One edge for the ellipse, four for the offset – `toNURBS` is as far as
the public API goes; the degree behind each of those edges takes the
same direct look at the kernel the quarter-circle above already needed.
Read that way, the ellipse costs degree $2$ – exactly what a conic
should cost, matching the exact quarter-circle above – and the offset,
the curve that looked back when it was first computed like nothing more
than a cheap wrapper around the original, costs degree $12$ on every one
of its four edges. Nothing about that number was visible from the
`OFFSET` type label alone; it only shows up once the curve is forced
into the one representation general enough to measure every curve in
this chapter on the same scale.

## Continuity

### Continuity Classes: C0, C1, G1, C2, G2

The piecewise-Bézier algebra earlier in this chapter already built three
of these classes by hand, one constraint at a time; naming them properly
now just makes precise what was already done. Two curve segments
$\mathbf{a}(u)$ and $\mathbf{b}(u)$ meeting where $\mathbf{a}(1)$ becomes
$\mathbf{b}(0)$ are:

- **$C^0$**: positions agree, $\mathbf{a}(1) = \mathbf{b}(0)$, and
  nothing else – a join with no gap, but a visible kink is completely
  allowed. Every solid this book has built is $C^0$ at every edge it
  has; a sharp corner is not a defect, it is what $C^0$ *is*.
- **$C^1$**: derivatives agree as vectors, $\mathbf{a}'(1) = \mathbf{b}'(0)$
  – matching not just tangent direction but the exact speed each segment
  reaches the joint with, which is exactly the condition
  $\mathbf{b}_1 = 2\mathbf{b}_0 - \mathbf{a}_2$ enforced earlier.
- **$G^1$**: only the tangent *direction* agrees,
  $\mathbf{a}'(1) = c\,\mathbf{b}'(0)$ for some $c > 0$ – strictly weaker
  than $C^1$, since the two speeds are free to differ, but it is the
  condition that actually matters visually: a curve looks smooth the
  moment direction matches, whatever the parametrization is doing
  underneath. A **fillet** is a $G^1$ construction by definition, not a
  $C^1$ one – nothing about rounding a corner cares what speed an
  arbitrary parametrization assigns it.
- **$C^2$ / $G^2$**: second derivatives, or just curvature and its
  osculating plane, agree the same way – exact vector match for $C^2$,
  direction-and-magnitude-of-bend only for $G^2$. This is the join
  matched curvature earlier in this chapter,
  $\mathbf{b}_2 = 4\mathbf{b}_0 - 4\mathbf{a}_2 + \mathbf{a}_1$, now named.

### Where Continuity Actually Matters

Which of these a join actually needs depends on what happens to it
afterward, not on some abstract standard of smoothness. A boolean
operation neither knows nor cares whether an edge is $C^0$ or $G^2$ – a
box's sharp corners are exactly as valid an input as a rounded one, and
demanding curvature continuity there would be solving a problem nobody
has. Four places where it stops being academic, for four different
reasons:

- **Manufacturing.** A milling toolpath is generated by offsetting the
  design surface by the cutting tool's radius – exactly the offset
  construction from earlier in this chapter, run in three dimensions
  instead of two – and a curvature discontinuity in the design surface
  is a discontinuity in the tool's required contact point and
  orientation at that instant. The result is not an aesthetic flaw but
  a real dimensional one: a visible witness mark, or a toolpath that
  has to retract and re-approach exactly where the surface's curvature
  broke.
- **Optical inspection.** Class-A automotive surfacing checks curvature
  continuity by painting reflection lines – straight stripes of light,
  or "zebra stripes" – across the panel and looking at how they bend in
  the reflection. A $G^1$-only join leaves the stripe direction
  matched, so the surface looks smooth to a bare eye, but the stripe's
  curvature kinks visibly at the join – the inspection exists
  precisely because the naked eye, without the stripes, cannot see the
  defect this chapter's curvature comb just made visible directly.
- **Aerodynamics.** A boundary layer's pressure gradient responds to
  how fast the surface curves, not just which way it curves, so a
  curvature discontinuity is a local kink in that pressure gradient –
  small geometrically, but often enough to trigger early boundary-layer
  transition or separation that a truly curvature-continuous surface
  would not. This is why aerodynamic and hydrodynamic surfaces are
  specified to $G^2$ well beyond where a human eye or hand would ever
  notice the difference.
- **Mechanical contact.** Stress under load concentrates exactly where
  curvature changes abruptly – a standard fact of contact mechanics,
  the reason a sharp internal corner is a stress riser and a filleted
  one is not. A load-bearing medical implant with a curvature
  discontinuity on its surface has, in effect, built in a stress riser
  at that exact point, which is why implant surfaces are held to the
  same $G^2$ standard for structural reasons that automotive panels are
  held to for optical ones.

A curve or surface can look perfectly smooth to the eye and still fail
every one of these – the defect is in the curvature, not the tangent,
and curvature is exactly the thing a glance does not check.

A straight line meeting a circular arc, tangent to it at the join, makes
the gap concrete. The line's curvature is $\kappa=0$ everywhere; the
arc's is the constant $\kappa=1/R$ from earlier in this chapter. Both
curves agree in position and tangent direction at the join – it is
genuinely $G^1$, no kink anywhere to see – but curvature jumps from $0$
to $1/R$ the instant the join is crossed, discontinuously, with nothing
in between.

:::{figure} ../figures/generated/ch06-curvature-comb.svg
:width: 85%

A line meeting a circular arc tangentially – no visible kink anywhere –
with a **curvature comb**: short teeth perpendicular to the curve, one
per sample point, scaled to the local curvature. Zero length the entire
length of the line, a sudden jump to constant length the instant the arc
begins. The curve looks $G^1$; the comb shows it is not $G^2$.
:::

## Surfaces

Every curve in this chapter has been a function of one parameter,
$\mathbf{C}(u)$. A surface adds a second:

$$\mathbf{S}(u, v) = \begin{pmatrix} x(u,v) \\ y(u,v) \\ z(u,v) \end{pmatrix}, \qquad u \in [u_0, u_1],\ v \in [v_0, v_1].$$

The two parameters are coordinates *on* the surface, the way $u$ alone
was a coordinate along a curve. For a plane they can literally be the
in-plane $x$ and $y$; for a sphere they are longitude and latitude, the
same two numbers that locate a point on the Earth; for a cylinder, the
angle around and the height up. Freezing one parameter and letting the
other run traces a curve that lies in the surface – an **isoline** –
and the $u$- and $v$-isolines together form a coordinate grid drawn
over the whole surface, the same grid CAD viewers and this book's
figures use to make a curved face legible.

:::{figure} ../figures/generated/ch06-surface-uv.png
:width: 35%

A surface curved in both parameter directions – the smooth loft this
section builds below – with its coordinate grid drawn on: holding $u$
fixed traces the curves running the surface's length, holding $v$
fixed the rings around it, and the arrows mark the two directions of
increase. Every point on the patch is named by its two parameters,
exactly as $u$ alone named every point on a curve; what range the
numbers run over is each surface's private convention – $0$ to $2\pi$
around a cylinder, $0$ to $1$ in both directions on this lofted
B-spline patch.
:::

Every `Face` in a B-Rep, Chapter 5's vocabulary again, carries a
surface plus a trimmed region of its $(u,v)$ domain – but here the
analogy with edges genuinely bends. An edge trims its curve with two
numbers, an interval in $u$. A region of the $(u,v)$ plane is only
that simple when its boundary happens to run along isolines – true for
a cylinder's lateral face, bounded by the two rims and the seam, and
for little else. Bore Chapter 2's hole through a plate and look at the
top face: its outer boundary still follows the plane's isolines, four
straight segments, but its inner boundary is a *circle drawn in the
$(u,v)$ plane*, a curve no pair of parameter intervals can express.
A face's trim is therefore not a rectangle of parameters but a set of
boundary curves living in the parameter domain – which is why
Chapter 5's hierarchy hangs whole wires on a face where an edge made
do with two parameter values. Everything this chapter has proved
about curves – polynomials
failing to reach a circle, control points buying stability, weights
buying exactness, continuity classes controlling how pieces join –
restates one dimension up, faces instead of edges, without needing new
mathematics. What the second parameter changes is the derivative
picture: a curve has one
tangent direction and one normal; a surface's tangent plane is spanned
by two independent directions, $\mathbf{S}_u$ and $\mathbf{S}_v$, and its
normal is their cross product, normalized to unit length – this
cross product is what Chapter 5's `normalAt()` computes.

### Parametric Surfaces and the Analytic Family

A parametric surface is only useful if $\mathbf{S}(u,v)$ and its normal
are cheap to evaluate – exactly the property that picked parametric
curves over the implicit and explicit alternatives in this chapter's
first section. A short list of surfaces gets that for free, a closed
formula standing in for the whole two-parameter family, the direct
surface counterpart of the conics from earlier: a plane, constant normal
everywhere,

$$\mathbf{S}(u,v) = \mathbf{P}_0 + u\,\mathbf{e}_1 + v\,\mathbf{e}_2;$$

a cylinder of radius $R$, its normal always perpendicular to the axis,

$$\mathbf{S}(u,v) = \mathbf{C} + R\cos u\,\mathbf{e}_1 + R\sin u\,\mathbf{e}_2 + v\,\mathbf{e}_3;$$

a sphere of radius $R$, latitude and longitude,

$$\mathbf{S}(u,v) = R\bigl(\cos u\cos v,\ \sin u\cos v,\ \sin v\bigr);$$

and a torus, major radius $R$ and minor radius $r$, a circle of radius
$r$ swept around an axis at distance $R$,

$$\mathbf{S}(u,v) = \bigl((R + r\cos v)\cos u,\ (R + r\cos v)\sin u,\ r\sin v\bigr).$$

A cone belongs on the same list – a circular cross-section shrinking
linearly to a point – though it already shows this family is less
uniform than the conics were: a cylinder's own $v$ turns out to be
literally its height, checked directly below, but nothing forces every
analytic surface's second parameter to mean the same thing twice; a
cone's, in the kernel underneath this book, is arc length along the
slant instead.

```python
from cadquery import func as cf

cyl = cf.cylinder(10.0, 30.0)
side = cyl.Faces()[0]
print(side.geomType(), side.uvBounds())

p = side.positionAt(0.0, 15.0)
print(p, side.normalAt(p))
```

`CYLINDER`, and bounds `(0.0, 6.283, 0.0, 30.0)` – $u$ over a full turn,
$v$ from $0$ to $30$, the cylinder's height, matching the formula
above with nothing hidden. `positionAt(0.0, 15.0)` lands at
`(5.0, 0.0, 15.0)`: radius $5$, half of the $10$-millimeter *diameter*
`cf.cylinder` actually takes as its first argument, at half the
$30$-millimeter height. `normalAt` there returns `(1.0, 0.0, 0.0)`,
pointing straight out along the radius, away from the solid's
material – the same rule Chapter 5's orientation section fixed for flat
faces, confirmed here on a curved one.

### Surfaces from Curves: Sweep and Loft

Chapter 3's `extrude` and `revolve` already build surfaces, one profile
curve at a time; this chapter can finally say what kind. Extrude a
circular profile, and the swept surface inherits the profile's
analytic name; extrude the interpolating spline from earlier in this
chapter instead, and it inherits that curve's name just as directly:

```python
circle_profile = cf.face(cf.wire(cf.circle(10.0)))
extruded = cf.extrude(circle_profile, (0, 0, 30))
print([f.geomType() for f in extruded.Faces()])

points = [(0, 0, 0), (10, 15, 0), (25, 5, 0), (40, 20, 0), (50, 0, 0), (0, 0, 0)]
spline_profile = cf.face(cf.wire(cf.spline(points)))
extruded_spline = cf.extrude(spline_profile, (0, 0, 10))
print([f.geomType() for f in extruded_spline.Faces()])
```

`['CYLINDER', 'PLANE', 'PLANE']` for the circle – a straight extrusion
of a circle really is just a cylinder, no different in kind from
`cf.cylinder` itself. `['EXTRUSION', 'PLANE', 'PLANE']` for the spline
profile: still a single ruled surface, straight lines connecting the
same curve at every height, but no longer a name this chapter's
analytic family covers – `EXTRUSION` is its own distinct type in OCCT,
not a stand-in for `BSPLINE`. Sweep a profile along a curved path
instead of a straight direction, and even that name runs out: a circle
swept along a bent spline path comes back `BSPLINE`, the same fallback
every high-degree curve in this chapter has landed on already. **Sweep**
and **loft**, the operations that build surfaces like these, are
Chapter 7's; what belongs here is only what their output *is*.

Loft carries a choice `extrude` and `revolve` never have to make: what
happens *between* the given sections. `ruled=True` connects consecutive
sections with straight lines, degree $1$ between each pair, no matter
how many sections there are – the surface analogue of piecewise Bézier
earlier in this chapter, each interval its own patch, joined only
$C^0$. The default, `ruled=False`, blends every section into a single
smooth surface, continuity controlled by the `continuity` argument
($C^2$ by default) – the surface analogue of a B-spline, one formula
covering every span at once.

```python
sections = [cf.wire(cf.circle(10.0)),
            cf.wire(cf.circle(16.0)).translate((0, 0, 25)),
            cf.wire(cf.circle(10.0)).translate((0, 0, 50))]
print([f.geomType() for f in cf.loft(sections, ruled=True).Faces()])
print([f.geomType() for f in cf.loft(sections, ruled=False).Faces()])
```

`['CONE', 'CONE']` for the ruled version: two straight-sided cones,
meeting at the middle circle with no attempt at a smooth transition.
`['BSPLINE']` for the default: one face, the bulge between the sections
blended in rather than creased.

:::{figure} ../figures/generated/ch06-loft-continuity.png
:width: 70%

The same three circles – radius 10, 16, 10 – lofted two ways. Ruled
(left): two straight-sided cones meeting at a visible crease at the
middle circle, $C^0$ only. Smooth (right, the default): one B-spline
surface blending the bulge in, no crease anywhere.
:::

### NURBS Surfaces

The weights that turned a B-spline curve into an exact circle
generalize to two parameters exactly the way the surfaces above
generalized curves – one weight $h_{ij}$ per point on a two-dimensional
**control net** $\mathbf{P}_{ij}$ instead of one per point on a control
polygon:

$$\mathbf{S}(u,v) = \frac{\sum_i \sum_j h_{ij}\, \mathbf{P}_{ij}\, N_{i,p}(u)\, N_{j,q}(v)}{\sum_i \sum_j h_{ij}\, N_{i,p}(u)\, N_{j,q}(v)}.$$

Setting every $h_{ij}=1$ collapses the denominator to $1$ the same way
it did for curves, since $\sum_i N_{i,p}(u) = \sum_j N_{j,q}(v) = 1$
separately – the ordinary B-spline surface is the $h_{ij}=1$ special
case of NURBS, one link further down the same chain this chapter has
been building since Bézier. OCCT does not even keep the two cases as
separate classes: `geomType() == 'BSPLINE'` covers both a rational and a
non-rational surface alike, the weights hidden inside the object rather
than switching its type.

The cylinder from earlier in this section makes the tensor product
concrete, because a cylinder is exactly the shape the exact-circle
NURBS curve earlier in this chapter was built to trace, extruded:

```python
from OCP.BRep import BRep_Tool

nurbs = side.toNURBS()
surf = BRep_Tool.Surface_s(nurbs.wrapped)
print(surf.UDegree(), surf.VDegree())
print(surf.NbUPoles(), surf.NbVPoles())
print(surf.IsURational(), surf.IsVRational())
```

`toNURBS` is the public API; reading degree and pole counts back off the
result needs the same direct look at OCCT's `Geom_BSplineSurface`
the exact-circle example used earlier, since neither number is exposed
through `cf`. Degree $2$ in $u$, degree $1$ in $v$: the circular
direction needs the same quadratic degree the exact quarter-circle curve
did, the straight extrusion direction needs nothing more than a line.
`IsURational()` is `True`, `IsVRational()` is `False` – the weights that
bend the circular direction into an exact circle vary with $i$ only,
$h_{ij} = h_i$ for every $j$, uniform along the length of the cylinder.
A rational NURBS curve, in effect, extruded degree $1$ into a surface –
the tensor product formula above doing nothing more exotic than that for
this particular shape.

### Continuity at Surface Boundaries

$G^0$, $G^1$, $G^2$ restate exactly as before – position, tangent plane,
and curvature agreeing across a shared edge in place of a shared point –
the same three classes, one dimension up, with the same practical
stakes: manufacturing, optical inspection, aerodynamics, and mechanical
contact do not stop caring about curvature just because the join is now
a curve instead of a point. A **fillet**, already used without this
vocabulary since Chapter 2, is the clearest worked example, because it
is built to hit exactly one of these classes and no better:

```python
box = cf.box(50, 30, 20)
filleted = cf.fillet(box, box.edges(), 3.0)
print(set(f.geomType() for f in filleted.Faces()))
```

`{'PLANE', 'CYLINDER', 'SPHERE'}` – a cylindrical patch along each
rounded edge, a spherical patch at each rounded corner where three edges
meet, both tangent to the flat faces they join, $G^1$ by construction.
Nothing about that tangency touches curvature: the flat faces carry
curvature $0$ everywhere, the fillet's cylindrical patches carry the
constant curvature $1/R$ their $3\,\text{mm}$ radius fixes, and the join between them
jumps from one to the other exactly the way the curvature comb earlier
in this chapter already made visible for a line meeting an arc – the
identical defect, a surface instead of a curve. Loft's `continuity`
argument, `C1`, `C2`, or `C3`, seen above, is Chapter 7's dial for the
same question at a lofted seam rather than a fillet's – the same
curvature classes from this chapter's Continuity section, now decided
per construction rather than derived from a control-point identity by
hand.

:::{note} Try It
- Print `uvBounds()` for a sphere's face and a torus's face. Which of
  the sphere's two parameters is longitude and which latitude – and
  what do the torus's two $0$-to-$2\pi$ parameters each mean? Confirm
  your reading by evaluating `positionAt` at a few chosen values.
- The interpolating spline passes through its data points – how
  smoothly? Sample `curvatureAt` at closely spaced parameters across
  the middle data point of this chapter's five-point spline and watch
  it change continuously, the $C^2$ promise made concrete. Then build
  the same shape as *two* splines sharing that point and compare
  `tangentAt` and `curvatureAt` on either side of the joint.
- Offset the closed spline profile from the Surfaces section outward
  by 3 mm and print the `geomType()` of every edge in the result.
  `OFFSET` was to be expected – where do the `CIRCLE` edges come from?
  (Look at how the profile closes.)
:::
