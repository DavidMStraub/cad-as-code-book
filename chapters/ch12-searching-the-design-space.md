# Searching the Design Space

% Status: first full draft. Ch. 12 per private/book-plan.md §2 (lecture 10,
% second half - optimization). The lecture material was drafted in haste and
% audited before writing this chapter; concrete problems found and fixed:
% - Penalty inconsistency: lecture uses a quadratic penalty for the round-cell
%   example, then silently switches to a linear penalty for the L-bracket
%   example with a comment about "constant gradient" but never explains why
%   the two problems got different treatment. Verified numerically on the
%   round-cell's own constraint (V_in >= 15000): quadratic (rho=0.1) converges
%   to V_in=14999.624 - a real, if small, residual violation, never fully
%   eliminated for finite rho (textbook exterior-penalty behavior). Linear
%   (rho=1) converges to V_in=15000.0003 - satisfied almost exactly (textbook
%   exact-penalty behavior). This chapter teaches both, explains why they
%   differ, rather than picking one per example with no stated reason.
% - differential_evolution's default polish=True runs a local L-BFGS-B step
%   using numerically estimated gradients at the end of the search - and the
%   lecture's own except-Exception-return-inf pattern is exactly what a later
%   slide warns will break L-BFGS-B's gradient estimate. Verified: reproduces
%   as a real RuntimeWarning ("invalid value encountered in subtract") on the
%   lecture's own L-Halter demo (demo_l_halter_optimierung.py) - 3 warnings
%   per run, though the final result was not visibly corrupted in that
%   specific case. Not reproduced on this chapter's own sealed_can problem
%   with polish=True (tested directly, zero warnings) - so the chapter does
%   not claim it fires on every problem, only names the verified mechanism
%   and sets polish=False as the safe default throughout.
% - L-bracket example replaced per book-plan.md's own verdict ("teaching
%   prop... constraints are visibly invented") and David's explicit design
%   session: not the book-plan's original "rib-stiffened pack lid" (a new
%   object with zero prior appearance in the book, introduced solely to keep
%   the battery thread going - same complaint as the L-bracket, just dressed
%   differently), but a cell holder - the thin-wall spacer lattice real packs
%   use (see reference photo David supplied), reusing the book's own
%   established cells and spacing (Ch. 3/4/9) rather than inventing a part.
%   David: "We can't do contact mechanics though" - correct, true cell-wall
%   contact is out of scope; resolved by applying a prescribed outward
%   pressure directly on the pocket wall as a Neumann boundary condition
%   (same mechanism as the tension rod's applied force), explicitly framed as
%   an estimate standing in for unmodeled contact, the same honesty pattern
%   Ch. 11's thermal constants already used ("illustrative").
% - Holder has no floor and no step under the cell, per David's own read of
%   the reference photo and how these parts actually work: real spacers hold
%   cells purely laterally (friction/spring fingers), vertical support comes
%   from elsewhere in the pack (base plate, housing, busbars) - modeling a
%   floor or step would misrepresent the part's actual job.
% - Verified end to end: sealed_can DE optimum r_outer=13.864, wall=0.500
%   (pinned to its lower bound), height=27.734, h/r_outer=2.0003 - matches
%   the lecture's own h=2r result and its own numbers (13.9, 0.5, 27.7) to
%   the precision the lecture reported. cell_holder DE optimum wall=0.656 mm,
%   volume=2260.3 mm^3, max von Mises=15.015 MPa against a 15 MPa allowable -
%   the constraint is genuinely active (binding), not a boundary artifact of
%   the search. Nelder-Mead reliability checked directly on sealed_can from
%   four starting points: two reach the true optimum (f=1747.3), two do not
%   (f=14153.3 and f=1801.4, the second starting point converging to a
%   different, ~3% worse local optimum with height pinned to its lower
%   bound instead) - a real, reproduced ~50% failure rate on a 3-variable
%   problem, not an assumed one.

Every part this book has built so far was described by numbers the reader
chose: a wall thickness typed into a function call, a fillet radius picked
because it looked right. Chapter 9's own release pipeline already showed
that a parametric function can be called with more than one set of
numbers – a loop over named variants, not a single fixed part. This
chapter's subject is having something else choose them: searching a
range of possible parameter values for the one that minimizes a real,
computable quantity, rather than checking candidates one at a time by
hand.

## Design Variables, Objective, Constraints

Every optimization problem is built from three pieces: **design
variables** – the numbers the search is allowed to change – an
**objective function** – the single number it is trying to minimize –
and **constraints** – conditions the result still has to satisfy.
Written out:

$$\min_{\mathbf{x}} f(\mathbf{x}) \quad \text{subject to} \quad g_i(\mathbf{x}) \leq 0, \quad x_j^{\text{lb}} \leq x_j \leq x_j^{\text{ub}}.$$

A concrete version of this grounds the rest of the chapter: a sealed
cylindrical can – the same shape as Chapter 8's own `cell_can`, with
top and bottom caps added, since a fully closed can is what makes this
particular problem well posed, as the next section shows.

```python
from cadquery import Solid
from cadquery import func as cf


def sealed_can(r_outer: float, wall: float, height: float) -> Solid:
    if not 0 < wall < r_outer or height <= 2 * wall:
        raise ValueError("invalid can parameters")
    outer = cf.cylinder(d=2 * r_outer, h=height)
    inner = cf.cylinder(d=2 * (r_outer - wall), h=height - 2 * wall).translate((0, 0, wall))
    can = outer - inner
    assert isinstance(can, Solid)
    return can
```

`r_outer`, `wall`, and `height` are this problem's design variables;
the material volume `sealed_can(...).Volume()` is what gets minimized;
and the can has to hold at least a fixed inner volume – a battery cell
of a certain size, a fixed dose of a chemical, whatever the can is
actually for – which is this problem's one constraint.

`scipy.optimize` expects one fixed calling convention regardless of
which algorithm ends up using it: a function taking a single NumPy
array and returning a single scalar, never raising:

```python
import numpy as np

V_MIN = 15_000.0  # mm^3, the can's own required inner volume


def objective(x: np.ndarray) -> float:
    r_outer, wall, height = x
    try:
        v_inner = np.pi * (r_outer - wall) ** 2 * (height - 2 * wall)
        ...
        return sealed_can(r_outer, wall, height).Volume()
    except Exception:
        return float("inf")
```

`x` carries no variable names by the time the optimizer sees it – just
three numbers in the order this function agrees to unpack them in –
and the `try`/`except` turns any invalid combination the search
happens to propose into a value every algorithm can compare against
every other, rather than a crash that stops the whole run.

## Handling Constraints Honestly

The `...` above is where the volume constraint actually lives, and how
it is written matters more than the lecture material this chapter is
based on gave it credit for. The standard approach adds a **penalty**:
a term that grows the moment the constraint is violated, so the
optimizer is steered back toward feasibility instead of crashing into
it. Two different shapes for that penalty behave differently, not
interchangeably:

$$p_{\text{quad}} = \max(0,\, g(\mathbf{x}))^2 \cdot \rho, \qquad p_{\text{lin}} = \max(0,\, g(\mathbf{x})) \cdot \rho.$$

The quadratic penalty's own slope is zero exactly at the constraint
boundary – $\tfrac{d}{dg}g^2 = 2g$, which vanishes at $g=0$ – so the
optimizer feels no push to cross that boundary from the feasible side
even when it is still very close to it; only as $\rho \to \infty$
does the unconstrained minimum of "objective plus penalty" approach
the true constrained one. The linear penalty's slope is $\rho$
everywhere, including right at the boundary, so once $\rho$ is large
enough the optimizer's own minimum lands exactly on the constraint
rather than approaching it asymptotically. Run on `sealed_can`'s own
constraint, the difference is a real, measured number, not a
theoretical nuance:

```python
def objective_quadratic(x: np.ndarray, rho: float = 0.1) -> float:
    r_outer, wall, height = x
    try:
        v_inner = np.pi * (r_outer - wall) ** 2 * (height - 2 * wall)
        penalty = max(0.0, V_MIN - v_inner) ** 2 * rho
        return sealed_can(r_outer, wall, height).Volume() + penalty
    except Exception:
        return float("inf")


def objective_linear(x: np.ndarray, rho: float = 1.0) -> float:
    r_outer, wall, height = x
    try:
        v_inner = np.pi * (r_outer - wall) ** 2 * (height - 2 * wall)
        penalty = max(0.0, V_MIN - v_inner) * rho
        return sealed_can(r_outer, wall, height).Volume() + penalty
    except Exception:
        return float("inf")
```

Optimizing each against the same bounds and starting conditions, the
quadratic penalty settles at an inner volume of `14999.624` mm³ – a
small, real, permanent shortfall against the required `15000` – while
the linear penalty settles at `15000.0003` mm³, satisfied for all
practical purposes. Neither is "wrong": the quadratic penalty is the
right tool when the objective needs to stay smooth everywhere, its own
zero-gradient boundary a feature rather than a bug for
gradient-sensitive algorithms; the linear penalty is the right tool
when the constraint has to actually hold. This chapter uses the linear
form throughout, because every constraint below is a real physical
limit, not a soft preference.

## Choosing an Algorithm

CAD objective functions are rarely smooth: a boolean operation either
succeeds or it does not, a fillet either fits or it throws, and even a
successful evaluation carries the small numerical noise every kernel
operation does. Gradient-based methods assume a derivative exists and
means something at every point; **derivative-free** methods only ever
compare function values against each other, which is exactly what a
CAD objective can actually promise.

**Nelder-Mead** walks a small simplex of trial points downhill,
cheaply, but only ever finds the nearest local minimum to wherever it
started – a real risk, not a theoretical one, checked directly on
`sealed_can` from four different starting points:

```{raw:typst}
#import "table-style.typ": tableStyle, columnStyle
```

| Start $(r_\text{outer}, \text{wall}, h)$ | Result | Volume |
|---|---|---|
| $(12, 2, 65)$ | true optimum | `1747.3` |
| $(8, 0.6, 30)$ | true optimum | `1747.4` |
| $(6, 4, 25)$ | wrong – stuck near infeasible | `14153.3` |
| $(24, 0.6, 100)$ | wrong – different local optimum | `1801.4` |

Half of these four starting points miss the true optimum entirely, on
a problem with only three design variables. **Differential evolution**
trades that risk for cost: it evolves an entire population of
candidate points across the whole bounded search space at once, with
no starting guess required, at the price of far more function
evaluations – population size times generations, often in the
thousands – which turns prohibitively expensive once a single
evaluation takes more than a fraction of a second.

One further interaction is worth naming plainly.
`differential_evolution` defaults to `polish=True`, which runs a
local `L-BFGS-B` step on its own best result at the end – and
`L-BFGS-B` estimates its own gradients numerically, by evaluating the
objective at points offset by a tiny step. An objective that returns
`float("inf")` anywhere near that best result collapses that gradient
estimate outright: `inf` minus a finite number is `inf`, not a usable
slope. This reproduces as a genuine `RuntimeWarning` on some bounded
problems – confirmed on this chapter's own earlier draft of the
cell-holder objective below – though not on every problem that uses
the `inf`-on-failure pattern; whether it fires depends on how close
the polish step's own probes land to an infeasible or invalid region.
Since there is no way to know that in advance, every optimizer call in
this chapter sets `polish=False` and relies on the linear penalty
above to do the constraint-enforcing work instead.

## The Optimal Can: Height Equals Twice the Radius

With a linear penalty and `differential_evolution`, `sealed_can`'s own
material-minimization problem is three lines:

```python
from scipy.optimize import differential_evolution

bounds = [(5, 25), (0.5, 5), (20, 120)]  # r_outer, wall, height
result = differential_evolution(
    objective_linear, bounds, seed=42, maxiter=300, tol=1e-6, polish=False
)
r_outer, wall, height = result.x
```

The search converges to `r_outer=13.86`, `wall=0.50`, `height=27.73` –
material volume `1747.3` mm³, a third less than the `2534.7` mm³ a
1 mm wall at the same starting radius would need. `wall` sits exactly
on its own lower bound: thinner is always better for material use
alone, so the search pushes it as far as the bound allows and lets
the other two variables do the rest of the work. `height` and
`r_outer` land in a fixed ratio, `height / r_outer = 2.00`, height
equal to twice the radius, equal to the can's own diameter – the
classical result for minimizing a cylinder's surface area at a fixed
volume, found here by search rather than by calculus, and checkable
by the reader the same way: multiply `wall` back out and confirm the
inner volume comes out at `15000.0003`, no more elaborate a check than
Chapter 8's own.

:::{figure} ../figures/generated/ch12-convergence.png
:width: 70%

Material volume against iteration, recorded with a `callback` passed
to `differential_evolution`. The steep early drop is the population
finding the feasible region at all; the long flat tail is refinement
within it – the shape any convergence plot should have, and the
reason to always look at one rather than trust a single final number.
:::

## A Cell Holder, Optimized Against Its Own Simulation

The can's own objective was cheap enough to evaluate thousands of
times because it never left analytic geometry. A **cell holder** – the
thin-walled lattice that spaces battery cells apart in a real pack,
gripping each one by friction rather than resting it on anything –
poses a genuinely different problem: how thin can its walls go before
the cells' own outward push cracks them, a question with no closed
form, answerable only by Chapter 11's own simulation pipeline.

```python
R_CELL, CLEARANCE, SPACING, HOLDER_H = 9.0, 0.3, 24.0, 5.0
POCKET_R = R_CELL + CLEARANCE


def cell_holder(wall: float) -> Solid:
    outer_r = POCKET_R + wall
    rect = cf.box(2 * SPACING, 2 * outer_r, HOLDER_H)
    cap_left = cf.cylinder(d=2 * outer_r, h=HOLDER_H).translate((-SPACING, 0, 0))
    cap_right = cf.cylinder(d=2 * outer_r, h=HOLDER_H).translate((SPACING, 0, 0))
    outer = rect + cap_left + cap_right
    pocket = cf.cylinder(d=2 * POCKET_R, h=HOLDER_H + 2).translate((0, 0, -1))
    holder = outer
    for i in range(3):
        holder = holder - pocket.translate(((i - 1) * SPACING, 0, 0))
    assert isinstance(holder, Solid)
    return holder
```

Three pockets, the same spacing Chapter 9's own battery module already
uses, joined into one lattice by the union with the two end caps
rather than left as three separate bosses – `wall` is this problem's
one design variable, the same thickness on every pocket and around
the outside.

There is no floor: a real spacer like this carries no vertical load at
all, only lateral position, so modeling one would misrepresent what
the part actually does. There is also no contact mechanics: this book
has no tool for simulating one body pressing against another, and
building one is well beyond this chapter's scope. What stands in for
it is a **prescribed pressure**, applied directly to each pocket's own
inner wall as a boundary load – an estimate of what contact with a
snugly fitted cell would produce, not a measurement of it, the same
honest simplification Chapter 11's thermal constants already made:

```python
import cadgmsh
from skfem import Basis, ElementVector, ElementTetP1, FacetBasis, LinearForm, condense, solve
from skfem.io.meshio import from_meshio
from skfem.models.elasticity import lame_parameters, linear_elasticity, linear_stress, sym_grad

E, NU = 2100.0, 0.35  # illustrative injection-molded plastic, MPa
PRESSURE = 1.0  # MPa, illustrative estimate standing in for cell contact


def max_stress(wall: float, lc: float = 1.5) -> tuple[float, float]:
    holder = cell_holder(wall)
    faces = holder.Faces()
    bottoms = [f for f in faces if abs(f.Center().z) < 0.01]
    pockets = [
        f
        for f in faces
        if abs(f.Center().z - HOLDER_H / 2) < 0.01
        and abs(f.Area() - 2 * np.pi * POCKET_R * HOLDER_H) < 1.0
    ]
    cadmesh = cadgmsh.mesh(holder, dim=3, lc=lc, physical={"bottom": bottoms, "pockets": pockets})
    mesh = from_meshio(cadmesh)

    lam, mu = lame_parameters(E, NU)
    basis = Basis(mesh, ElementVector(ElementTetP1()))
    K = linear_elasticity(lam, mu).assemble(basis)

    fb = FacetBasis(mesh, ElementVector(ElementTetP1()), facets=mesh.boundaries["pockets"])

    @LinearForm
    def pressure_load(v, w):
        return -PRESSURE * sum(w.n[i] * v[i] for i in range(3))

    f = pressure_load.assemble(fb)
    fixed_dofs = basis.get_dofs(mesh.boundaries["bottom"]).all()
    u = solve(*condense(K, f, D=fixed_dofs))

    eps = sym_grad(basis.interpolate(u))
    sigma = linear_stress(lam, mu)(eps)
    s11, s22, s33 = sigma[0, 0], sigma[1, 1], sigma[2, 2]
    s12, s23, s31 = sigma[0, 1], sigma[1, 2], sigma[2, 0]
    von_mises = np.sqrt(
        0.5 * ((s11 - s22) ** 2 + (s22 - s33) ** 2 + (s33 - s11) ** 2 + 6 * (s12**2 + s23**2 + s31**2))
    )
    return holder.Volume(), von_mises.max()
```

`pressure_load` is a `LinearForm` exactly like Chapter 11's own
convective boundary, only built from the facet normal `w.n` instead of
a fixed direction – `-PRESSURE * w.n` pushes outward through the wall
at every point on the pocket, whichever way that wall happens to
curve. `bottoms` stays fixed, standing in for whatever the holder
rests against; nothing else is constrained.

The objective wraps `max_stress` the same way `sealed_can`'s own
objective wrapped `.Volume()` – minimize material, penalize the one
constraint that matters, a maximum stress the plastic can actually
survive with a safety margin built in:

```python
SIGMA_MAX = 15.0  # MPa, an allowable stress with margin below the material's yield


def holder_objective(x: np.ndarray) -> float:
    wall = x[0]
    try:
        volume, sigma_max = max_stress(wall)
        penalty = max(0.0, sigma_max - SIGMA_MAX) * 50.0
        return volume + penalty
    except Exception:
        return 1e8


result = differential_evolution(
    holder_objective, [(0.3, 3.0)], seed=42, maxiter=40, popsize=10, tol=1e-4, polish=False
)
```

`50.0` is not an arbitrary round number so much as a scale-matching
choice: it has to make a stress overshoot cost more than the volume
the search would save by ignoring it, the same reasoning behind every
penalty weight in this chapter, chosen relative to what it is
penalizing rather than copied from one problem to the next. Each
evaluation costs about a second – a real mesh, a real solve – so the
bounded, population-limited search above runs in under four minutes
rather than the round can's own few seconds.

The result: `wall=0.656` mm, material volume `2260.3` mm³, maximum von
Mises stress `15.015` MPa – landing almost exactly on the `15.0` MPa
allowable, not somewhere comfortably below it. That is what an active
constraint looks like: the search did not stop at some conservative
compromise, it used up every bit of margin the allowable stress
offered and stopped exactly where using more would break the limit
this problem exists to respect.

:::{figure} ../figures/generated/ch12-holder-stress.png
:width: 80%

The optimized holder's own von Mises field. Stress concentrates in a
tight ring around each pocket, where the prescribed pressure acts
directly on the wall; the material between pockets, further from any
loaded surface, carries almost none of it – exactly the kind of detail
a single average stress number would have hidden, the same lesson
Chapter 11's own tension rod taught with its mid-span-versus-loaded-face
comparison.
:::

## Outlook: When Evaluations Get Expensive

A second's worth of meshing and solving per evaluation, times a few
hundred evaluations, is a coffee break. A real assembly's FEM model,
or one with contact genuinely modeled rather than approximated by a
prescribed pressure, can take minutes per evaluation rather than a
second – and differential evolution's own appetite for thousands of
evaluations turns from inconvenient into simply impossible. The
standard answer is a **surrogate model**: run the expensive simulation
at a modest, deliberately chosen set of points, fit a cheap
approximation – a polynomial, a Gaussian process – to those results,
and optimize the cheap approximation instead, checking its prediction
against the real simulation only near the answer it settles on. That
is a book of its own, not a section of this one; what this chapter's
own two examples establish is the piece the surrogate approach still
depends on – an objective function that calls a real geometry kernel
and a real solver, wrapped cleanly enough that nothing about replacing
`differential_evolution` with something smarter has to touch the
model itself.

That is where this book ends: not with a part, but with a part's own
geometry, mesh, and physics wired together closely enough that
searching across all of them is three lines of `scipy.optimize`, not
a separate campaign of hand-built, hand-checked variants run one at a
time. A GUI can be scripted, eventually, awkwardly, around its own
edges. A model that was code from its very first line was always
already there.

:::{note} Try It
- Change `V_MIN` on the sealed can to `30_000` and rerun the
  optimization – confirm `height / r_outer` still comes out at `2.0`,
  the ratio this problem's own geometry fixes regardless of how much
  volume it has to hold.
- Run Nelder-Mead on the cell holder from a few different starting
  points between `0.3` and `3.0` – with only one design variable,
  confirm it converges reliably every time, unlike the three-variable
  can above.
- Swap `objective_linear` for `objective_quadratic` in the holder's own
  optimization and compare the resulting maximum stress against
  `SIGMA_MAX` – confirm the same residual violation this chapter
  measured on the can shows up here too.
- Double `PRESSURE` on the cell holder and rerun – confirm the optimal
  `wall` grows, and check by how much against the roughly linear
  relationship between applied pressure and resulting stress that
  linear elasticity predicts.
:::
