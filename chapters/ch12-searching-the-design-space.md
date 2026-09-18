# Searching the Design Space


Every part this book has built so far was described by numbers the
reader chose: a wall thickness typed into a function call, a fillet
radius picked because it looked right. Chapter 9's release pipeline
turned one such function into a whole family of parts by looping it
over named variants. Choosing the numbers well by hand works for two
or three of them at a time; it breaks down as soon as they start
pulling against each other – in the buoy this chapter sizes, every
millimeter of ballast that makes the hull float more upright also
makes it float deeper – and which variable actually decides the
outcome is rarely obvious until it is checked. That tension is why
optimization is a standing part of the mechanical design toolchain:
a gram removed from an aircraft or a satellite is fuel or payload
gained for the vehicle's entire service life, and the same trade
governs a battery pack, where every gram of supporting structure
competes directly against a gram of cells that could have occupied
its place. This chapter's subject is having a program navigate such
trades: searching a range of possible parameter values for the one
that minimizes a single computable quantity – mass, for both parts
this chapter optimizes – while respecting the constraints a working
part has to meet.

## Design Variables, Objective, Constraints

Every optimization problem is built from three pieces: **design
variables** – the numbers the search is allowed to change – an
**objective function** – the single number it is trying to minimize –
and **constraints** – conditions the result still has to satisfy.
Written out:

$$\min_{\mathbf{x}} f(\mathbf{x}) \quad \text{subject to} \quad g_i(\mathbf{x}) \leq 0, \quad x_j^{\text{lb}} \leq x_j \leq x_j^{\text{ub}}.$$

A concrete version of this grounds the rest of the chapter: an
**instrument buoy** – a floating housing that keeps a sensor package
and its antenna above open water. The shape is a **spar buoy**, a
hull much longer than it is wide that floats upright: a hemispherical
dome at the bottom, a cylindrical body, and a conical neck at the top
that carries the antenna. The electronics – `3` kg of them – sit just
below the hatch at the top of the body, where they stay dry and
reachable for service; a steel ballast disk rests in the dome at the
bottom. A buoy like this has two requirements it either meets or does
not. It has to float high enough – the hatch seal must clear the
waterline with margin, or the first wave washes over it. And it has
to float *upright* – a hull whose mass sits too high simply lies down
flat on the water, antenna and all.

```python
from cadquery import Shape, Solid
from cadquery import func as cf

R_HULL, R_NECK, H_NECK = 60.0, 20.0, 80.0  # mm


def hull(body: float) -> Solid:
    bottom = cf.sphere(2 * R_HULL).moved(z=R_HULL)
    middle = cf.cylinder(d=2 * R_HULL, h=body).moved(z=R_HULL)
    neck = cf.cone(d1=2 * R_HULL, d2=2 * R_NECK, h=H_NECK).moved(z=R_HULL + body)
    shape = bottom + middle + neck
    assert isinstance(shape, Solid)
    return shape
```

`body`, the length of the cylindrical section, is the first design
variable; the thickness of the ballast disk, `t_ballast`, is the
second. The hull diameter is fixed by the instrument rack and the
mooring hardware, the payload by what the buoy exists to carry. The
objective is total mass: this buoy is deployed and recovered by hand
over the side of a small boat, and every kilogram of shell and
ballast makes that job harder.

Both requirements come down to two classical facts about floating
bodies. A body floats at the **draft** – the depth to which its hull
sits in the water – where the displaced water weighs as much as the
body does:

$$\rho_w \, V_{\text{sub}}(d) = m_{\text{total}},$$

and it floats upright if its center of mass lies below its **center
of buoyancy**, the centroid of the submerged volume: tilt the hull,
and weight pulling down at the one and buoyancy pushing up at the
other form a couple that rights it. (Ship designers work with a
weaker criterion, the metacenter, which tolerates a center of mass
above the center of buoyancy; for a hull as slender as this one the
metacenter sits about a millimeter above the center of buoyancy, so
the strict condition is the honest one.) The constraints, then: a
**freeboard** – the height of the hatch above the waterline – of at
least `60` mm, and a center of buoyancy at least `10` mm above the
center of mass, margin for waves and for everything the model leaves
out. With $z_B$ and $z_G$ for the two centers:

$$(R_{\text{hull}} + \text{body}) - d \geq 60 \text{ mm}, \qquad z_B - z_G \geq 10 \text{ mm}.$$

Every quantity in those two conditions is a property of the shape,
and the kernel can be asked for each one directly. The submerged
volume is a boolean intersection – the hull cut by a box that reaches
up to the candidate waterline – and $V_{\text{sub}}$ is its
`.Volume()`; the center of buoyancy is the same intersection's
`.Center()`; the shell's mass and center of mass come from `.Area()`
and the area-weighted centroids of the faces. For this hull – a dome,
a cylinder, and a cone fused together, sliced at an arbitrary height –
those method calls are the only practical route to any of these
numbers, and each costs milliseconds. Lengths are in millimeters and
masses in kilograms throughout, so the densities below carry units of
kg/mm³:

```python
import numpy as np
from scipy.optimize import brentq

RHO_WATER, RHO_STEEL = 1.0e-6, 7.85e-6  # kg/mm^3, fresh water and steel
SHELL_AREAL = 4.0e-6  # kg/mm^2, molded plastic shell
M_PAYLOAD = 3.0  # kg, electronics mounted 40 mm below the hatch
R_BALLAST, Z_BALLAST = 45.0, 25.0  # mm, steel disk resting in the dome
FREEBOARD_MIN, STABILITY_MIN = 60.0, 10.0  # mm


def submerged(shape: Solid, draft: float) -> Shape:
    below = cf.box(6 * R_HULL, 6 * R_HULL, draft)
    return shape * below


def evaluate(body: float, t_ballast: float) -> tuple[float, float, float]:
    shape = hull(body)
    hatch = R_HULL + body
    m_shell = shape.Area() * SHELL_AREAL
    z_shell = sum(f.Area() * f.Center().z for f in shape.Faces()) / shape.Area()
    m_ballast = RHO_STEEL * np.pi * R_BALLAST**2 * t_ballast
    m_total = m_shell + m_ballast + M_PAYLOAD
    z_com = (
        m_shell * z_shell
        + m_ballast * (Z_BALLAST + t_ballast / 2)
        + M_PAYLOAD * (hatch - 40)
    ) / m_total

    def net_lift(draft: float) -> float:
        return RHO_WATER * submerged(shape, draft).Volume() - m_total

    if net_lift(hatch + H_NECK - 1) < 0:
        raise ValueError("heavier than any displacement it can generate: it sinks")
    draft = brentq(net_lift, 1.0, hatch + H_NECK - 1, xtol=0.01)
    z_cob = submerged(shape, draft).Center().z
    return m_total, hatch - draft, z_cob - z_com
```

`submerged` is the entire hydrostatics engine: one intersection.
`evaluate` does the bookkeeping around it. The shell's center of mass
is the area-weighted average of the face centroids – honest for a
shell of uniform thickness – and the ballast and payload enter as
masses at known heights. Then `brentq`, a classic bracketing
**root-finder** {cite:p}`brent1973algorithms`, finds the equilibrium:
`net_lift` is positive when
the buoy displaces more than its weight and negative when it
displaces less, and the draft where it crosses zero is where the buoy
actually floats. A candidate heavier than the displacement of its
entire hull never floats at all, and `evaluate` refuses it with an
exception rather than returning numbers that mean nothing.

`scipy.optimize` {cite:p}`virtanen2020scipy` expects one fixed calling
convention regardless of
which algorithm ends up using it: a function taking a single NumPy
array and returning a single scalar, never raising. Turning
`evaluate`'s two margins into something that convention can search
against needs one more idea: a **penalty** – a term added to the
objective that grows the moment a constraint is violated, since the
optimizer has no other way to compare a design that fails against
one that does not.

The obvious first attempt squares the violation, $p(\mathbf{x}) =
\max(0, g(\mathbf{x}))^2 \cdot \rho$, and for a soft preference that
would be fine. For a real physical margin it is not: the derivative
of $g^2$ is $2g$, which is exactly zero at $g=0$, so right at the
constraint boundary the penalty pushes back with no force at all,
and the optimizer, feeling nothing stopping it there, settles just
inside the infeasible side rather than exactly on the feasible one.
Run on the buoy with a penalty weight that looks entirely reasonable
on paper, that failure is far worse than a rounding error: the search
converges to a design whose center of mass sits `5.2` mm *above* its
center of buoyancy – an "optimized" buoy that capsizes – with
`52.1` mm of freeboard against the required `60`. Making the same
weight ten thousand times larger shrinks the stability shortfall to
two thousandths of a millimeter – smaller, never gone, exactly the
asymptotic behavior that vanishing derivative predicts.

The fix is a penalty whose slope never vanishes:

$$p(\mathbf{x}) = \max(0,\, g(\mathbf{x})) \cdot \rho.$$

Linear rather than quadratic, with a constant slope of $\rho$
everywhere, including right at the boundary, so once $\rho$ is large
enough the minimum lands exactly on the constraint instead of
drifting inside it. The same search, with the same kind of eyeballed
weight, converges to `60.00` mm of freeboard and a `10.00` mm
stability margin – both limits met exactly. Every constraint in this
chapter is a real physical limit a deployed part either meets or does
not, so every objective below uses the linear form:

```python
def objective(x: np.ndarray, rho: float = 1.0) -> float:
    body, t_ballast = x
    try:
        m_total, freeboard, stability = evaluate(body, t_ballast)
    except Exception:
        return float("inf")
    penalty = max(0.0, FREEBOARD_MIN - freeboard) * rho
    penalty += max(0.0, STABILITY_MIN - stability) * rho
    return m_total + penalty
```

`x` carries no variable names by the time the optimizer sees it –
just two numbers in the order this function agrees to unpack them in.
And the `try`/`except` catches everything: a candidate that sinks, a
boolean that fails, a root-finder that loses its bracket – each
becomes `float("inf")`, a value that loses every comparison against a
design that works.

## Choosing an Algorithm

CAD objective functions are rarely smooth: a boolean operation either
succeeds or it does not, a fillet either fits or it throws, and even
a successful evaluation carries the small numerical noise every
kernel operation does. This chapter's objective goes further: across
the entire region of the bounds where a candidate sinks, it returns
`inf` – a plateau with no slope at all. Gradient-based methods assume
a derivative exists and means something at every point;
**derivative-free** methods only ever compare function values against
each other, which is exactly what a CAD objective can actually
promise.

**Nelder-Mead** {cite:p}`nelder1965simplex` keeps a small **simplex** of
trial points – three
points for this two-variable problem, one more than the number of
design variables – and repeatedly replaces the worst of them: reflect
it through the center of the others, and if that reflected point is
better still, push further out in the same direction; if not, pull
back toward the center instead. That is cheap, a handful of
evaluations per step, but it only ever moves toward whatever is
better *nearby* – nothing in the mechanism ever looks somewhere else
in the search space entirely, so what surrounds the starting simplex
decides everything.

Checked directly on the buoy, from ten starting points spread across
the bounds, that risk takes a concrete form:

```{raw:typst}
#import "table-style.typ": tableStyle, columnStyle
```

| Start $(\text{body}, t_\text{ballast})$ | Converges to |
|---|---|
| $(500, 20)$, $(650, 5)$, $(750, 30)$ | the optimum, $8.42$ kg |
| $(200, 10)$, $(250, 120)$, $(300, 50)$, $(400, 100)$, $(450, 60)$, $(700, 140)$ | its starting point, `success=False` |
| $(600, 80)$ | the optimum, after a lucky escape |

The three starts that describe a floating buoy converge to the same
optimum every time – with a smooth feasible region and two variables,
the simplex is reliable once it has a foothold. But seven of the ten
starts describe a buoy that sinks, and there the simplex is born on
the `inf` plateau: three trial points, all infinite, every comparison
a tie. Six of those seven burn their entire evaluation budget
shuffling in place and hand back their starting point with
`success=False`; the seventh happens to stumble onto a floating
design mid-shuffle and recovers. A local search cannot cross a region
that gives it nothing to compare – and for this buoy, sinking
candidates cover most of the bounded search space a designer would
reasonably write down.

**Differential evolution** {cite:p}`storn1997differential` trades that
risk for cost. Instead of one
simplex, it keeps an entire *population* of candidate points
scattered across the whole bounded search space from the start; each
generation, it builds new candidates by combining existing ones –
take two population members, scale their difference, add it to a
third – and keeps whichever version, old or new, scores better.
Because the starting population already covers the space, some of
its members float from generation zero, and the plateau that strands
a lone simplex is just territory the population's survivors quickly
abandon. That coverage costs evaluations – population size times
generations, often in the thousands – prohibitively expensive once a
single evaluation takes more than a fraction of a second.

One further interaction is worth naming plainly.
`differential_evolution` defaults to `polish=True`, which runs a
local `L-BFGS-B` step on the best result at the end – and `L-BFGS-B`
estimates its gradients numerically, by evaluating the objective at
points offset by a tiny step. An objective that returns
`float("inf")` anywhere near that best result collapses the gradient
estimate outright: `inf` minus a finite number is `inf`, not a
usable slope. Whether a given run actually trips over this depends
on how close the polish step's probes land to an infeasible or
invalid region, and there is no way to know that in advance. Every
optimizer call in this chapter sets `polish=False` and relies on the
linear penalty above to do the constraint-enforcing work instead.

With that fixed, the buoy's optimization is a few lines:

```python
from scipy.optimize import differential_evolution

bounds = [(150, 800), (1, 150)]  # body, t_ballast
result = differential_evolution(
    objective, bounds, seed=42, maxiter=60, popsize=12, tol=1e-8, polish=False
)
body, t_ballast = result.x
```

Each evaluation – a fused hull, a boolean intersection for every step
of the root-find – costs about `0.04` s, and the full search of
`1464` evaluations runs in under a minute. It converges to
`body=764.2` mm and `t_ballast=81.7` mm: a buoy of `8.42` kg all told
– `4.08` kg of steel ballast, `1.34` kg of shell, `3` kg of payload –
floating with `764` mm of its `904` mm height under water. Checking
the result the way Chapter 8 would: the freeboard comes out at
`60.00` mm and the stability margin at `10.00` mm – both constraints
exactly binding, with neither design variable resting on a bound. The
search traded hull length against ballast until the two physical
limits bit at the same time, and where that point lies was computed,
fourteen hundred times over, by the same kernel that will eventually
export this hull for manufacture.

:::{figure} ../figures/generated/ch12-buoy.png
:width: 60%

The optimized buoy, split at the waterline the root-finder settled
on: `764` mm of the `904` mm hull sits below the surface, and the
hatch at the top of the cylindrical body clears it by exactly the
required `60` mm.
:::

:::{figure} ../figures/generated/ch12-convergence.png
:width: 70%

Total mass against iteration, recorded with a `callback` passed to
`differential_evolution`; the right panel zooms the vertical axis.
The steep early drop is the population finding designs that float
and clear both margins at all. The tail, flat at full scale, keeps
stepping down by tens of grams for another thirty generations before
it truly settles – the reason to always look at a convergence plot
rather than trust a single final number.
:::

## A Cell Holder, Optimized Against Its Own Simulation

The buoy's objective never took longer than a few hundredths of a
second, because volumes, areas, and centroids are cheap for any
kernel. A **cell holder** – the thin-walled lattice that spaces
battery cells apart in a real pack, gripping each one by friction
rather than resting it on anything – poses a genuinely different
problem: how thin can its walls go before the cells' outward push
cracks them, a question with no closed form, answerable only by
Chapter 11's simulation pipeline.

```python
R_CELL, CLEARANCE, SPACING, HOLDER_H = 9.0, 0.3, 24.0, 5.0
POCKET_R = R_CELL + CLEARANCE


def cell_holder(wall: float) -> Solid:
    outer_r = POCKET_R + wall
    rect = cf.box(2 * SPACING, 2 * outer_r, HOLDER_H)
    cap_left = cf.cylinder(d=2 * outer_r, h=HOLDER_H).moved(x=-SPACING)
    cap_right = cf.cylinder(d=2 * outer_r, h=HOLDER_H).moved(x=SPACING)
    outer = rect + cap_left + cap_right
    pocket = cf.cylinder(d=2 * POCKET_R, h=HOLDER_H + 2).moved(z=-1)
    holder = outer
    for i in range(3):
        holder = holder - pocket.moved(x=(i - 1) * SPACING)
    assert isinstance(holder, Solid)
    return holder
```

Three pockets, the same spacing as Chapter 9's battery module, joined
into one lattice by the union with the two end caps rather than left
as three separate bosses – `wall` is this problem's one design
variable, the same thickness on every pocket and around the outside.

There is no floor: a real spacer like this carries no vertical load
at all, only lateral position, so modeling one would misrepresent
what the part actually does. There is also no contact mechanics: this
book has no tool for simulating one body pressing against another,
and building one is well beyond this chapter's scope. What stands in
for it is a **prescribed pressure**, applied directly to each
pocket's inner wall as a boundary load – an estimate of what contact
with a snugly fitted cell would produce, not a measurement of it, the
same honest simplification Chapter 11's thermal constants already
made:

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
    normal = (s11 - s22) ** 2 + (s22 - s33) ** 2 + (s33 - s11) ** 2
    shear = s12**2 + s23**2 + s31**2
    von_mises = np.sqrt(0.5 * (normal + 6 * shear))
    return holder.Volume(), von_mises.max()
```

`pressure_load` is a `LinearForm` exactly like the `ambient` term of
Chapter 11's convective boundary, only built from the facet normal
`w.n` instead of a fixed direction – `-PRESSURE * w.n` pushes outward through the
wall at every point on the pocket, whichever way that wall happens to
curve. `bottoms` stays fixed, standing in for whatever the holder
rests against; nothing else is constrained.

The objective wraps `max_stress` the same way the buoy's objective
wrapped `evaluate` – minimize material, penalize the one constraint
that matters, a maximum stress the plastic can actually survive with
a safety margin built in, and fall back on the same `inf` for
anything the mesher or solver cannot handle:

```python
SIGMA_MAX = 15.0  # MPa, an allowable stress with margin below the material's yield


def holder_objective(x: np.ndarray) -> float:
    wall = x[0]
    try:
        volume, sigma_max = max_stress(wall)
        penalty = max(0.0, sigma_max - SIGMA_MAX) * 50.0
        return volume + penalty
    except Exception:
        return float("inf")


result = differential_evolution(
    holder_objective, [(0.3, 3.0)], seed=42, maxiter=40, popsize=10, tol=1e-4, polish=False
)
```

`50.0` is a scale-matching choice: it has to make a stress overshoot
cost more than the volume the search would save by ignoring it – the
same reasoning behind every penalty weight in this chapter, chosen
relative to what it is penalizing rather than copied from one problem
to the next. Each evaluation costs about a second – a real mesh, a
real solve – so the bounded, population-limited search above runs in
under four minutes.

The result: `wall=0.656` mm, material volume `2260.3` mm³, maximum
von Mises stress `15.015` MPa – landing almost exactly on the
`15.0` MPa allowable, not somewhere comfortably below it. That is
what an active constraint looks like: the search did not stop at some
conservative compromise, it used up every bit of margin the allowable
stress offered and stopped exactly where using more would break the
limit this problem exists to respect.

:::{figure} ../figures/generated/ch12-holder-stress.png
:width: 80%

The optimized holder's von Mises field. Stress concentrates in a
tight ring around each pocket, where the prescribed pressure acts
directly on the wall; the material between pockets, further from any
loaded surface, carries almost none of it – exactly the kind of
detail a single average stress number would have hidden, the same
lesson Chapter 11's tension rod taught with its
mid-span-versus-loaded-face comparison.
:::

## Outlook: When Evaluations Get Expensive

A second's worth of meshing and solving per evaluation, times a few
hundred evaluations, is a coffee break. A real assembly's FEM model,
or one with contact genuinely modeled rather than approximated by a
prescribed pressure, can take minutes per evaluation rather than a
second – and differential evolution's appetite for thousands of
evaluations turns from inconvenient into simply impossible. The
standard answer is a **surrogate model**: run the expensive
simulation at a modest, deliberately chosen set of points, fit a
cheap approximation – a polynomial, a Gaussian process – to those
results, and optimize the cheap approximation instead, checking its
prediction against the real simulation only near the answer it
settles on. That is a book of its own, not a section of this one;
what the buoy and the cell holder establish is the piece the
surrogate approach still depends on – an objective function that
calls a real geometry kernel and a real solver, wrapped cleanly
enough that nothing about replacing `differential_evolution` with
something smarter has to touch the model itself.

That is where this book ends: not with a part, but with a part's
geometry, mesh, and physics wired together closely enough that
searching across all of them is three lines of `scipy.optimize`, not
a separate campaign of hand-built, hand-checked variants run one at a
time. A GUI can be scripted, eventually, awkwardly, around its edges.
A model that was code from its very first line was always already
there.

:::{note} Try It
- Mount the electronics at mid-hull (`hatch / 2` instead of
  `hatch - 40`) and rerun – confirm the optimum collapses to a
  `428` mm body and `4.6` kg total, both constraints again exactly
  binding. Nearly half the buoy existed to carry `3` kg at the top
  of the hull; the payload's height, and the ballast spent canceling
  it, is what actually sized the design.
- Run Nelder-Mead on the cell holder from a few different starting
  points between `0.3` and `3.0` – with only one design variable and
  every candidate in the bounds buildable, confirm it converges
  reliably every time, unlike the buoy above.
- Rewrite the holder's penalty as a quadratic one and rerun – confirm
  the same silent shortfall this chapter measured on the buoy's
  stability margin shows up here too, now against a real stress limit
  instead of a capsize.
- Double `PRESSURE` on the cell holder and rerun – confirm the
  optimal `wall` grows, and check by how much against the roughly
  linear relationship between applied pressure and resulting stress
  that linear elasticity predicts.
:::
