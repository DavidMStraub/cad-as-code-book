# Searching the Design Space

% Status: second full draft. Ch. 12 per private/book-plan.md §2 (lecture 10,
% second half - optimization). First draft used the source lecture's own
% round-cell material-minimization example (h=2r) as the anchor for design
% variables/objective/constraints, penalties, and algorithm choice - four
% sections built around it. David, on reading that draft: the lecture's own
% round-cell example is "shit," "used only due to last minute preparation,"
% and should never have been reached for - correcting book-plan.md's own
% audit table, which still listed it "Keep - textbook-grade" and is what led
% me there. That verdict is now stale; book-plan.md needs updating to match.
% Also flagged in the same pass: a stray "than the lecture material this
% chapter is based on gave it credit for" sentence, a meta-reference to the
% book's own source material that has no business in reader-facing prose
% regardless of the point it was attached to; a vacuous transition sentence
% ("two different shapes... behave differently, not interchangeably"); the
% penalty section presented two penalty types side by side with no real
% stake attached, reading as confusing rather than motivating; the algorithm
% section restated lecture facts about Nelder-Mead/DE without explaining the
% actual mechanism either one uses; the reliability table felt bolted onto
% the exercise. All rewritten below, anchored on a genuinely different
% example instead of a fix to the same one.
%
% New anchor: a compression strut sized against Euler buckling, David's own
% suggestion after rejecting a packing-density alternative as "too trivial...
% and discrete." Verified end to end, exact (not thin-wall-approximated)
% tube cross-section and moment of inertia, aluminum (E=70e3 MPa),
% sigma_allow=150 MPa, P=5000 N, L=1200 mm, K=1.0 (pinned-pinned):
% - DE optimum: r_outer=22.428 mm, wall=0.300 mm (pinned to its own lower
%   manufacturing bound), area=41.994 mm^2, P_cr=5000.00 N (buckling exactly
%   binding), stress=119.07 MPa against a 150 MPa allowable (yield has real
%   margin, ~1.26x) - mass 136.1 g for the 1200 mm strut. Confirms the
%   classical result this chapter states in prose: a slender strut fails by
%   buckling well before the material itself would yield.
% - Quadratic-vs-linear penalty, run on the strut's own buckling constraint
%   (not an abstract aside): quadratic penalty at a reasonable-looking
%   rho=2e-6 converges to P_cr=4215.8 N against the required 5000 N - a
%   15.7% shortfall, i.e. an "optimized" strut that is not actually safe to
%   build. Increasing rho by 1000x (to 2e-3) only shrinks the shortfall to
%   0.01% - smaller, never gone, the textbook asymptotic behavior of an
%   exterior penalty. Linear penalty at rho=20 converges to P_cr=5000.00 N
%   exactly (shortfall 0.0000). Real, safety-relevant stakes replace the
%   round-cell's own ~0.0025%-shortfall version of the same point.
% - Nelder-Mead reliability, checked from ten starting points spread across
%   the bounds: six reach the true optimum (f=41.99-42.00); the other four
%   all converge to the exact same second local optimum, r_outer=3.26 mm,
%   wall=3.10-3.19 mm, f=132.48 - not four different failures, one specific
%   wrong basin wide enough to catch two-fifths of a reasonable spread of
%   guesses. More interesting and more honest than the round-cell's own
%   scattered-failure table.
% - Short-strut check (Try It material): the same problem at L=300 mm
%   instead of 1200 mm converges to a *smaller* cross-section, 33.33 mm^2,
%   with yield exactly binding (stress=150.00 MPa) and buckling comfortably
%   satisfied (P_cr=23105 N against 5000 required) - the short-column /
%   long-column transition every mechanics-of-materials course covers,
%   reproduced by the search itself rather than asserted.
% - polish=True + inf interaction: same verified finding as the first draft
%   (reproduces on the lecture's own L-Halter demo, not reproduced on this
%   chapter's own strut objective directly) - kept, not specific to which
%   worked example carries it.
% Cell holder section (second worked example, FEM-in-the-loop) untouched by
% this revision - not part of David's complaint, only its own opening
% transition sentence updated to reference the strut instead of the can.

Every part this book has built so far was described by numbers the
reader chose: a wall thickness typed into a function call, a fillet
radius picked because it looked right. Chapter 9's own release
pipeline already showed that a parametric function can be called with
more than one set of numbers – a loop over named variants, not a
single fixed part. Choosing well by hand works for two or three
numbers at a time; it stops working long before a real part's own
count of free dimensions, each pulling the design a different
direction at once – a thinner wall saves mass but risks failure, a
shorter part saves material but changes how the whole thing fails, and
which variable actually decides the outcome is rarely obvious until it
is checked. That tension is why optimization is a standing part of the
mechanical design toolchain rather than a novelty: a gram removed from
an aircraft or a satellite is fuel or payload gained for the vehicle's
entire service life, and the same trade governs a battery pack, where
every gram of supporting structure competes directly against a gram of
cells that could have occupied its place instead. This chapter's
subject is having a program navigate that trade for a real part –
searching a range of possible parameter values for the one that
minimizes a real, computable quantity, rather than checking candidates
one at a time by hand.

## Design Variables, Objective, Constraints

Every optimization problem is built from three pieces: **design
variables** – the numbers the search is allowed to change – an
**objective function** – the single number it is trying to minimize –
and **constraints** – conditions the result still has to satisfy.
Written out:

$$\min_{\mathbf{x}} f(\mathbf{x}) \quad \text{subject to} \quad g_i(\mathbf{x}) \leq 0, \quad x_j^{\text{lb}} \leq x_j \leq x_j^{\text{ub}}.$$

A concrete version of this grounds the rest of the chapter: a
**strut** – a slender tube loaded in compression, the kind of support
post that holds a housing or an instrument off whatever it mounts to.
A strut can fail two different ways, not one: the material itself can
yield under direct compressive stress, or, well before that stress is
reached, the whole tube can suddenly bow sideways and **buckle** – the
governing failure mode of anything long and thin loaded along its own
axis, and the reason sizing a strut is never just a stress
calculation.

```python
from cadquery import Solid
from cadquery import func as cf


def strut(r_outer: float, wall: float, length: float) -> Solid:
    if not 0 < wall < r_outer:
        raise ValueError(f"wall must be between 0 and {r_outer}, got {wall}")
    outer = cf.cylinder(d=2 * r_outer, h=length)
    inner = cf.cylinder(d=2 * (r_outer - wall), h=length + 2).translate((0, 0, -1))
    tube = outer - inner
    assert isinstance(tube, Solid)
    return tube
```

`r_outer` and `wall` are this problem's design variables; `length` is
fixed by wherever the strut has to reach, not something the optimizer
gets to change. The two failure modes above translate directly into
this problem's constraints, both closed-form – no mesh or solver
needed yet:

$$P_{\text{cr}} = \frac{\pi^2 E I}{(KL)^2} \geq P, \qquad \sigma = \frac{P}{A} \leq \sigma_{\text{allow}},$$

where $I = \tfrac{\pi}{4}\left(r_\text{outer}^4 - r_\text{inner}^4\right)$
and $A = \pi\left(r_\text{outer}^2 - r_\text{inner}^2\right)$ are the
tube's own cross-sectional moment of inertia and area, $P$ the applied
compressive load, $E$ the material's stiffness, and $K$ a factor set
by how the strut's own two ends are held – $K=1$ for a strut free to
rotate at both ends, the case this chapter uses throughout. The
objective is the cross-section $A$ itself: minimizing it minimizes the
strut's own mass for a fixed length, since mass is just $A$ times
length times density.

`scipy.optimize` expects one fixed calling convention regardless of
which algorithm ends up using it: a function taking a single NumPy
array and returning a single scalar, never raising. Turning the two
constraints above into something that convention can actually search
against needs one more idea: a **penalty** – a term added to the
objective that grows the moment a constraint is violated, since the
optimizer has no other way to compare a design that fails against one
that does not.

The obvious first attempt squares the violation, $p(\mathbf{x}) =
\max(0, g(\mathbf{x}))^2 \cdot \rho$, and for a soft preference that
would be fine. For a real safety margin it is not: the derivative of
$g^2$ is $2g$, which is exactly zero at $g=0$, so right at the
constraint boundary the penalty pushes back with no force at all, and
the optimizer, feeling nothing stopping it there, settles just inside
the infeasible side rather than exactly on the feasible one. Run on
the strut's own buckling constraint, with a penalty weight that looks
entirely reasonable on paper, that is not a rounding error: the search
converges to a strut good for `4215.8` N of buckling resistance
against a required `5000` N – a `15.7`% shortfall, an "optimized"
strut that is not actually safe to build. Making the same penalty
weight a thousand times larger only shrinks the shortfall to `0.01`% –
smaller, never gone, exactly the asymptotic behavior that vanishing
derivative predicts.

The fix is a penalty whose slope never vanishes:

$$p(\mathbf{x}) = \max(0,\, g(\mathbf{x})) \cdot \rho.$$

Linear rather than quadratic, with a constant slope of $\rho$
everywhere, including right at the boundary, so once $\rho$ is large
enough the optimizer's own minimum lands exactly on the constraint
instead of drifting inside it. The same search, the same weight scale,
now converges to a strut good for exactly `5000.0` N – no shortfall at
all. Every constraint in this chapter is a real physical limit a built
part either meets or does not, so every objective below uses this
linear form:

```python
import numpy as np

E, SIGMA_ALLOW = 70e3, 150.0  # MPa, aluminum with margin below yield
P, LENGTH, K = 5000.0, 1200.0, 1.0  # N, mm, pinned-pinned


def section(r_outer: float, wall: float) -> tuple[float, float]:
    r_inner = r_outer - wall
    area = np.pi * (r_outer**2 - r_inner**2)
    moment = np.pi / 4 * (r_outer**4 - r_inner**4)
    return area, moment


def objective(x: np.ndarray, rho: float = 20.0) -> float:
    r_outer, wall = x
    try:
        area, moment = section(r_outer, wall)
        p_crit = np.pi**2 * E * moment / (K * LENGTH) ** 2
        stress = P / area
        penalty = max(0.0, P - p_crit) * rho / 1000 + max(0.0, stress - SIGMA_ALLOW) * rho
        return strut(r_outer, wall, LENGTH).Volume() / LENGTH + penalty
    except Exception:
        return float("inf")
```

`x` carries no variable names by the time the optimizer sees it – just
two numbers in the order this function agrees to unpack them in – and
`strut(...).Volume() / LENGTH` recovers the same cross-sectional area
`section` already computed analytically, this time from the real solid
rather than a formula, the same cross-check in miniature Chapter 8
built into every one of its own functions.

## Choosing an Algorithm

CAD objective functions are rarely smooth: a boolean operation either
succeeds or it does not, a fillet either fits or it throws, and even a
successful evaluation carries the small numerical noise every kernel
operation does. Gradient-based methods assume a derivative exists and
means something at every point; **derivative-free** methods only ever
compare function values against each other, which is exactly what a
CAD objective can actually promise.

**Nelder-Mead** keeps a small **simplex** of trial points – three
points for this two-variable problem, one more than the number of
design variables – and repeatedly replaces the worst of them: reflect
it through the center of the others, and if that reflected point is
better still, push further out in the same direction; if not, pull
back toward the center instead. That is cheap, a handful of
evaluations per step, but it only ever moves toward whatever is better
*nearby* – nothing in the mechanism ever looks somewhere else in the
search space entirely, so wherever the simplex first starts descending
decides which valley it can ever find, right or wrong.

Checked directly on the strut, from ten different starting points
spread across its own bounds, that risk is not theoretical: six reach
the true optimum, area `41.99`–`42.00` mm². The other four all
converge to the exact same wrong point instead – `r_outer=3.26` mm,
`wall=3.10`–`3.19` mm, area `132.5` mm² – not four different mistakes,
one specific second valley wide enough to catch two-fifths of a
reasonable spread of starting guesses:

```{raw:typst}
#import "table-style.typ": tableStyle, columnStyle
```

| Start $(r_\text{outer}, \text{wall})$ | Converges to |
|---|---|
| $(10, 2)$, $(5, 0.5)$, $(35, 1)$ | true optimum, area $\approx 42.0$ |
| $(30, 4)$, $(15, 4.5)$, $(25, 3.5)$ | same wrong valley, area $\approx 132.5$ |

**Differential evolution** trades that risk for cost. Instead of one
simplex, it keeps an entire *population* of candidate points scattered
across the whole bounded search space from the start; each generation,
it builds new candidates by combining existing ones – take two
population members, scale their difference, add it to a third – and
keeps whichever version, old or new, scores better. Because the
starting population already covers the space rather than sitting in
one place, a better valley elsewhere is something the population can
simply already have a foothold in, not something the search has to
stumble into. That coverage costs evaluations – population size times
generations, often in the thousands – prohibitively expensive once a
single evaluation takes more than a fraction of a second.

One further interaction is worth naming plainly.
`differential_evolution` defaults to `polish=True`, which runs a
local `L-BFGS-B` step on its own best result at the end – and
`L-BFGS-B` estimates its own gradients numerically, by evaluating the
objective at points offset by a tiny step. An objective that returns
`float("inf")` anywhere near that best result collapses that gradient
estimate outright: `inf` minus a finite number is `inf`, not a usable
slope. This reproduces as a genuine `RuntimeWarning` on some bounded
problems – confirmed on a lecture-style objective built the same way –
though not on every problem that uses the `inf`-on-failure pattern;
whether it fires depends on how close the polish step's own probes
land to an infeasible or invalid region. Since there is no way to know
that in advance, every optimizer call in this chapter sets
`polish=False` and relies on the linear penalty above to do the
constraint-enforcing work instead.

With that fixed, the strut's own optimization is a few lines:

```python
from scipy.optimize import differential_evolution

bounds = [(3, 40), (0.3, 5)]  # r_outer, wall
result = differential_evolution(
    objective, bounds, seed=42, maxiter=1000, tol=1e-10, popsize=25, polish=False
)
r_outer, wall = result.x
```

The search converges to `r_outer=22.43` mm, `wall=0.30` mm – a
cross-section of `41.99` mm², a strut of about `136` g over its
`1200` mm length. `wall` sits exactly on its own lower manufacturing
bound: thinner is always better once the buckling constraint is
satisfied, so the search pushes it as far as that bound allows and
lets `r_outer` do the rest of the work. Checking the result the same
way Chapter 8 would: buckling resistance comes out at `5000.0` N,
exactly the required load, while the resulting stress is `119.1` MPa
against a `150` MPa allowable – real margin, not zero. Buckling, not
material strength, is what actually decided this strut's own
thickness – the classical result for a slender column, confirmed here
by search rather than assumed.

:::{figure} ../figures/generated/ch12-convergence.png
:width: 70%

Cross-sectional area against iteration, recorded with a `callback`
passed to `differential_evolution`. The steep early drop is the
population finding the feasible region at all; the long flat tail is
refinement within it – the shape any convergence plot should have, and
the reason to always look at one rather than trust a single final
number.
:::

## A Cell Holder, Optimized Against Its Own Simulation

The strut's own objective was cheap enough to evaluate thousands of
times because it never left closed-form formulas. A **cell holder** –
the thin-walled lattice that spaces battery cells apart in a real
pack, gripping each one by friction rather than resting it on anything
– poses a genuinely different problem: how thin can its walls go
before the cells' own outward push cracks them, a question with no
closed form, answerable only by Chapter 11's own simulation pipeline.

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

E_HOLDER, NU = 2100.0, 0.35  # illustrative injection-molded plastic, MPa
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

    lam, mu = lame_parameters(E_HOLDER, NU)
    basis = Basis(mesh, ElementVector(ElementTetP1()))
    K_mat = linear_elasticity(lam, mu).assemble(basis)

    fb = FacetBasis(mesh, ElementVector(ElementTetP1()), facets=mesh.boundaries["pockets"])

    @LinearForm
    def pressure_load(v, w):
        return -PRESSURE * sum(w.n[i] * v[i] for i in range(3))

    f = pressure_load.assemble(fb)
    fixed_dofs = basis.get_dofs(mesh.boundaries["bottom"]).all()
    u = solve(*condense(K_mat, f, D=fixed_dofs))

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

The objective wraps `max_stress` the same way the strut's own
objective wrapped `section` – minimize material, penalize the one
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
rather than the strut's own few seconds.

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
- Rerun the strut at `LENGTH=300` instead of `1200` – confirm the
  optimizer now settles on a *smaller* cross-section with the yield
  constraint exactly binding and real margin left on buckling, the
  opposite of the 1200 mm case: a short, stubby strut fails by
  crushing, a long, slender one by buckling, and which regime a given
  design sits in is not always obvious in advance.
- Run Nelder-Mead on the cell holder from a few different starting
  points between `0.3` and `3.0` – with only one design variable,
  confirm it converges reliably every time, unlike the strut above.
- Rewrite the holder's own penalty as a quadratic one and rerun –
  confirm the same silent shortfall this chapter measured on the
  strut's buckling constraint shows up here too, now against a real
  stress limit instead of a load.
- Double `PRESSURE` on the cell holder and rerun – confirm the optimal
  `wall` grows, and check by how much against the roughly linear
  relationship between applied pressure and resulting stress that
  linear elasticity predicts.
:::
