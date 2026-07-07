# The Mathematics of Shape

% Status: sections 1-2 drafted in full; remaining sections are headings
% only. See private/book-plan.md §2 (Ch. 6) and §8.1 for the open
% depth-control decision, and private/CAx-Programmierung - 03 Geometrie
% I.md for the source lecture §1 draws its formulas and worked examples
% from directly (explicit/implicit/parametric comparison, tangent/arc
% length/curvature derivations, the circle and ellipse curvature
% formulas, the offset formula). This is a math chapter: formulas carry
% the argument, code verifies specific claims after each one rather than
% doing the explaining itself - keep that ratio in any further drafting.
% Merges lectures 03+04 into one continuous argument rather than the
% course's two-week split. Section 2's ellipse
% offset is deliberately undersold on first appearance - the new curve
% type (OFFSET) is a thin, cheap wrapper, not a complicated object, and
% the section says so plainly rather than pretending otherwise. The real
% escalation (degree 2 to degree 12, one edge to four, once expressed as
% NURBS) is a payoff reserved for later in the chapter, once NURBS exist
% to measure it in - see the forward pointer at the end of §2. Canonical
% home (per the book-plan's lookup table) for curve/surface math, NURBS,
% and continuity; must be self-contained enough for a reader who jumps in
% here directly. Cox-de Boor recursion and knot-multiplicity mechanics are
% compressed into a starred subsection - book readers need the
% consequences (local control, continuity classes, why NURBS), not the
% recursion derivation. Closes with a curvature-comb or similar
% visualization of a continuity defect, filling the theory-practice gap
% the lecture material never closed (see book-plan §3, "surface-quality
% inspection"). Sets up sweep/loft in Chapter 7, which cannot be taught
% without this chapter's vocabulary.

## Curves as Parametric Functions

### Explicit, Implicit, and Parametric Curves

Chapter 3 built every profile from straight segments, and mentioned in
passing that curved ones – arcs, splines – close into faces exactly the
same way, without saying what a curved edge actually *is*. It is worth
asking properly, because there is more than one honest way to write a
curve down, and CAD kernels settled on one of them for a specific,
checkable reason.

Take the simplest curved shape there is – a circle of radius $R$ centered
on the origin – and ask how to write it down. The everyday answer from
school algebra is **explicit**: $y$ as a function of $x$,

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
here?" without extra machinery bolted on afterward. Every curve this book
builds from here on – lines, circles, ellipses now, splines and NURBS
later – is exactly this idea, a function from a single number to a point
in space,

$$\mathbf{C}(u) = \begin{pmatrix} x(u) \\ y(u) \\ z(u) \end{pmatrix}, \qquad u \in [u_{\min}, u_{\max}],$$

boldface marking a three-component vector throughout this chapter, as it
does for $\mathbf{C}$ here and for the tangent, normal, and curvature
vectors that follow it. Every `Edge` in a B-Rep, Chapter 5's vocabulary
filled in properly now, carries exactly this: a curve, plus the parameter
interval that trims it to a finite piece.

A parametrization earns its keep by what it makes cheap to ask: what point
sits at a given $u$, and which direction the curve is heading there; how
far apart, along the curve, two parameter values actually are; how
sharply the curve is bending at a point. Each of those questions has a
direct answer in terms of $\mathbf{C}(u)$ and its derivatives, worked out
over the rest of this section.

### Tangent and Arc Length

The **tangent vector** is the parametrization's own derivative,

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
all. Arc length, in general, is not something a curve's own formula hands
over for free; it has to be found numerically, for the whole curve, every
time it is needed. That simplicity the circle enjoys belongs to the
circle alone, not to curves in general.

### Curvature

**Curvature**, $\kappa$, measures how fast the tangent direction turns per
unit distance traveled – how sharply the curve bends, independent of how
it happens to be parametrized. In arc-length terms it is a second
derivative,

$$\kappa = \left|\frac{d^2\mathbf{C}}{ds^2}\right|,$$

and for an arbitrary parametrization, the chain rule together with
Lagrange's identity turns this into a formula that needs no
reparametrization to use:

$$\kappa(u) = \frac{\left\lvert \mathbf{C}'(u) \times \mathbf{C}''(u) \right\rvert}{\left\lvert \mathbf{C}'(u) \right\rvert^{3}}.$$

A straight line has $\kappa = 0$ everywhere – it never turns. A circle of
radius $R$ has $\kappa = 1/R$ everywhere, the reciprocal relationship
behind curvature's usual companion, the **radius of curvature**
$R_\kappa = 1/\kappa$: the radius of the one circle that best hugs the
curve at that single point, tangent to it and matching its bend exactly –
the curve's **osculating circle** there.

% Figure: osculating circles at two points on an ellipse, one near the
% pointed end and one near the round end, each drawn tangent to the curve
% with its own radius of curvature labeled.

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

### Curves in CadQuery

Every formula above is independent of any particular software. In
CadQuery, `cf.ellipse` and its relatives return an `Edge` – Chapter 5's
topological element, a curve wrapped with the parameter interval that
trims it – and `positionAt`, `tangentAt`, and `curvatureAt` read
$\mathbf{C}(u)$, $\mathbf{T}(u)$, and $\kappa(u)$ off it. Two distinct
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
paid again on every call.

```python
assert abs(circle.curvatureAt(0.0) - 1 / 10) < 1e-9
assert abs((p2 - p1).Length - (p4 - p3).Length) < 0.01
```

## The Limits of Analytic Curves

Lines, circles, and ellipses belong to a small, closed family: the
**conics**, curves that appear as a plane's intersection with a cone,
sharing enough structure that CadQuery represents each as an exact
analytic edge – a formula, not an approximation of one. It is tempting to
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
always points straight through its own center, turning at the same
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
conic. The curve is not broken: `ellipse_offset.isValid()` is `True`, and
it is exact and fully usable, evaluable at any parameter to full
precision, curvature and all. What is broken is the assumption from the
start of this section. Lines, circles, and ellipses are the entire
vocabulary this book has for a curve so far, three names covering every
analytic edge built through Chapter 5 – and offsetting the plainest of
the three by a plain 3 millimeters already produces a curve none of the
three names, or any combination of them, can describe. A family this
small was never going to survive contact with the operations a real
design needs; conics are closed under trimming and, one special case
aside, nothing else. Building a curve representation general enough to
hold whatever an operation like this actually produces – not just
offset, but sweep, loft, and every construction still ahead in this book
– is what the rest of this chapter does.

## Building Curves from Control Points

### The Power Basis and Bezier Curves

### B-Splines: Knots and Local Control

## NURBS: Rational Curves and Exact Shape

% A polynomial B-spline cannot trace an exact circle (a fresh, small,
% verifiable demonstration here - interpolate points on a circle, show
% the result bulges off it); a rational one (NURBS) can - weights as the
% mechanism. Close the section with a callback to §2's ellipse and its
% 3mm offset (same numbers, same objects, not pre-promised there -
% just recalled here): convert both to NURBS via .toNURBS() and report
% degree and edge count. Verified in a throwaway script: the plain
% ellipse is 1 edge, degree 2; the offset is 4 edges, degree 12 each.
% That is the real cost of §2's OFFSET curve, invisible from the type
% label alone and only visible once expressed in the same currency
% (NURBS degree) as everything else in this family.

### Cox-de Boor Recursion (starred)

% Compressed; consequences over derivation. Candidate to cut further if
% the chapter runs long.

## Continuity, and From Curves to Surfaces

### Continuity Classes: C0, C1, G1, C2, G2

### Surfaces: Analytic, Swept, and NURBS

% Close with a curvature-visualization worked example (curvature comb or
% equivalent) showing a real continuity defect, not just naming the
% classes - the theory-practice closer the audit flagged as missing.
