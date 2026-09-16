# Simulation


A parametric model that regenerates a part on demand can regenerate
the questions about the part too: how far does it bend under this
load, how hot does it run at that duty cycle? This chapter takes the
volume mesh Chapter 10 built and puts numbers to questions of exactly
that kind, using the finite element method. It works through two
complete problems end to end – a steel rod under tension, validated
against the pen-and-paper answer, and a battery cell heating itself
from the inside – and both run through the same few steps: mesh the
geometry, state the physics and the boundary conditions, solve one
linear system. Two examples do not make anyone a simulation engineer.
What they demonstrate is narrower and more useful: the path from a
parametric model to a checkable physical result is code, short enough
to read in one sitting and cheap enough to rerun the moment a
dimension changes.

## The Finite Element Method

Many of the physical quantities engineers need – how far a loaded part
deflects, how hot a component gets, how a voltage distributes through
a conductor – are governed by a **differential equation**: a
relationship between the quantity itself, how it varies from point to
point, and whatever is driving it, a force, a heat source, a boundary
held at a known value. For a handful of simple shapes, that equation
can be solved exactly with pen and paper – a uniform rod stretched by
a known force, a flat slab conducting heat between two parallel faces.
A real part, with pockets and fillets and holes, essentially never
has an exact solution, not because the physics is different, but
because the geometry is.

The **finite element method (FEM)** is a general strategy for finding
an approximate solution anyway, and it does not care which physics
produced the differential equation in the first place. Break the
domain into small, simple elements – Chapter 10's mesh – and
approximate the unknown quantity by a simple function, usually linear,
within each one. Stitching those local approximations together across
every node they share turns one differential equation with no general
solution into one large system of ordinary linear algebraic equations,
which does. Structural mechanics, heat conduction, electric and
magnetic fields, fluid flow: mathematically, all of them are the same
*kind* of problem – a field quantity, its spatial variation, and
something driving it – which is exactly why one method, and often one
piece of software, solves all of them. What changes from one physics
to the next is not the method; it is which quantity the unknowns
stand for, and which material property builds the matrix that couples
them together.

For a problem that is **linear** – stress proportional to strain, heat
flux proportional to temperature gradient, no dependence of the
material behavior on the solution itself – and **static** – a load
applied and held, with no inertia or time dependence in play – that
system of equations takes one fixed shape, whatever the physics behind
it:

$$K \mathbf{u} = \mathbf{f},$$

where $\mathbf{u}$ collects every **degree of freedom** the mesh
carries – a temperature at every node, say, or a displacement in each
of three directions at every node – and $\mathbf{f}$ collects whatever
is driving the problem, a load or a source. $K$ is assembled the same
way regardless of the physics, one small contribution per element
built from that element's shape, size, and governing material
property, but the name it carries depends on what it represents: in a
structural problem, where it relates a force to a displacement, it is
the **stiffness matrix** – the name this chapter uses for it in the
next section, on exactly that kind of problem. The same role in a
thermal problem, relating a heat source to a temperature, has no
comparably familiar name; this chapter keeps calling it $K$ throughout,
since the mathematics assembling it does not change even where the
everyday name for it would stop making sense.

Both worked examples in this chapter are linear and static, and both
assumptions are worth stating plainly, because a solver never checks
either one automatically. Linearity is what makes a single matrix
equation solvable in one pass at all; the moment stress stops being
proportional to strain, or displacements grow large enough that the
geometry $K$ was built from changes under load, $K$ itself would have
to depend on $\mathbf{u}$, and the single linear solve below becomes an
iterative one. Staticness drops inertia entirely; a part that has to
survive being dropped or shaken, rather than just loaded and held,
needs a mass term and a time axis that nothing in this chapter builds.
A bolted bracket carrying a steady load sits comfortably inside both
assumptions; a part being crash-tested sits outside both. Knowing which
side of that line a real problem falls on matters more than any
setting inside the solver itself.

Several open-source libraries assemble and solve $K \mathbf{u} =
\mathbf{f}$ for a mesh – FEniCS is the best known, built for large,
custom, research-grade problems. This book uses scikit-fem instead,
because a handful of lines are enough to install it, build a basis on
a mesh, and assemble a standard operator like `linear_elasticity` or
`laplace` – exactly the scale of problem this chapter works through.
scikit-fem takes the mesh Chapter 10 already knows how to build, asks
the reader to state which physics the elements should represent and
which degrees of freedom are already known, and returns $\mathbf{u}$ –
a displacement field, a temperature field, whatever the problem asked
for.

## A Tension Rod: Setting Up an Elasticity Problem

A cylindrical rod, pulled along its axis, is the simplest three
dimensional structural problem with a known, closed-form answer to
check a solver against – exactly why it is the worked example here
rather than something more elaborate.

```python
from cadquery import func as cf

r, length = 10.0, 40.0
rod = cf.cylinder(d=2 * r, h=length)

bottom = rod.faces("<Z")
top = rod.faces(">Z")
```

`bottom` and `top` are the rod's two flat end faces, picked out with
the same directional selectors Chapter 5 already taught, applied here
to hand specific faces to the mesher rather than to a boolean.
**cadgmsh** accepts them directly as named regions:

```python
import cadgmsh
from skfem.io.meshio import from_meshio

cadmesh = cadgmsh.mesh(rod, dim=3, lc=2.5, physical={"top": top, "bottom": bottom})
mesh = from_meshio(cadmesh)
```

`mesh.boundaries` now holds two named groups of mesh facets, `"top"`
and `"bottom"`, each one exactly the set of triangles Gmsh generated on
the corresponding face – the bridge between a CAD face and the
degrees of freedom a solver actually works with.

```python
from skfem import Basis, ElementVector, ElementTetP1, condense, solve
from skfem.models.elasticity import linear_elasticity, lame_parameters

E, nu = 210e3, 0.3  # steel, MPa
lam, mu = lame_parameters(E, nu)

basis = Basis(mesh, ElementVector(ElementTetP1()))
K = linear_elasticity(lam, mu).assemble(basis)
```

`ElementVector(ElementTetP1())` states that this problem has three
unknowns per node – a displacement vector, not a single number – and
`linear_elasticity` builds exactly the stiffness matrix $K$ from
before, using the two **Lamé parameters** `lam` and `mu` in place of
the more familiar $E$ and $\nu$ they are computed from:

$$\lambda = \frac{E \nu}{(1 + \nu)(1 - 2\nu)}, \qquad \mu = \frac{E}{2(1 + \nu)}.$$

$\mu$ is also the material's shear modulus; $\lambda$ has no everyday
name of its own. Together they are just another way of writing
Hooke's law for a three-dimensional, not merely one-dimensional,
stress state – the physics is still ordinary Hookean elasticity, only
the two numbers the assembly step actually consumes have different
names than $E$ and $\nu$.

```python
import numpy as np

F = 1000.0  # N
top_dofs = basis.get_dofs(mesh.boundaries["top"]).nodal["u^3"]
f = basis.zeros()
f[top_dofs] = F / len(top_dofs)

fixed_dofs = basis.get_dofs(mesh.boundaries["bottom"]).all()
u = solve(*condense(K, f, D=fixed_dofs))
```

`fixed_dofs` pins every displacement component at the bottom face to
zero – a rigid clamp – and `f` spreads the total axial force `F`
evenly across the nodal degrees of freedom on the top face, `u^3`
naming the third (z) displacement component specifically. `condense`
removes the fixed degrees of freedom from the system before solving it
and puts them back afterward, and `solve` is the linear solve
underneath everything else in this section – the same one-line step
regardless of how many thousand degrees of freedom the mesh happens to
carry.

## Checking the Result Against a Hand Calculation

A rod under a known axial force has a closed-form answer:

$$\Delta l = \frac{F l}{E A}, \qquad \sigma = \frac{F}{A}$$

where $A = \pi r^2$ is the cross-section. Comparing the solver's
displacement field against $\Delta l$ directly is not quite fair to
either number – $\Delta l$ assumes a uniform bar far from any load
application, while the solver's nodes right at the loaded face carry a
real, local stress concentration from spreading a smooth force across
a finite number of discrete points. Away from that face, the two agree
closely:

```python
uz = u[basis.nodal_dofs[2]]
node_z = mesh.p[2]
```

**Von Mises stress**, the standard scalar measure of how close a
three-dimensional stress state is to causing yield, combines all six
independent components of the stress tensor $\sigma$ into one number:

$$
\sigma_{\mathrm{vM}} = \Big[ \tfrac{1}{2}
  \big( (\sigma_{11} - \sigma_{22})^2 + (\sigma_{22} - \sigma_{33})^2 + (\sigma_{33} - \sigma_{11})^2 \\
  {} + 6(\sigma_{12}^2 + \sigma_{23}^2 + \sigma_{31}^2) \big)
\Big]^{1/2}
$$

where $\sigma_{11}, \sigma_{22}, \sigma_{33}$ are the normal stresses
along the three axes and $\sigma_{12}, \sigma_{23}, \sigma_{31}$ the
shear stresses between them. It is not a value `scikit-fem` computes
automatically; it comes from the stress tensor the displacement field
implies:

```python
from skfem.models.elasticity import linear_stress, sym_grad

eps = sym_grad(basis.interpolate(u))
sigma = linear_stress(lam, mu)(eps)

s11, s22, s33 = sigma[0, 0], sigma[1, 1], sigma[2, 2]
s12, s23, s31 = sigma[0, 1], sigma[1, 2], sigma[2, 0]

normal = (s11 - s22) ** 2 + (s22 - s33) ** 2 + (s33 - s11) ** 2
shear = s12**2 + s23**2 + s31**2
von_mises = np.sqrt(0.5 * (normal + 6 * shear))
```

Plotting both fields against axial position, next to the two analytic
formulas above:

:::{figure} ../figures/generated/ch11-tension-rod-validation.png
:width: 95%

FEM against the closed-form solution, along the rod's axis. Left:
nodal $u_z$ against the analytic straight line. Right: per-element von
Mises stress against the analytic $F/A$. Both agree closely over most
of the rod's length; both spread out near the fixed and loaded ends,
where a rigid clamp and a force applied at discrete nodes are real
local disturbances the uniform-bar formula never accounted for, not
solver error.
:::

The mean von Mises stress across every element comes out `3.155` MPa
against the analytic `3.183` – under one percent.

:::{figure} ../figures/generated/ch11-tension-rod.png
:width: 40%

The tension rod's von Mises stress field. The ring of concentrated
stress at the loaded top face is the same effect the plot above
captures numerically – real, and expected, not a solver artifact.
:::

## A Thermal Model: Heat Generated Inside a Cell

Heat conduction is governed by a different equation than elasticity,
but the same $K \mathbf{u} = \mathbf{f}$ machinery assembles it: one
unknown per node instead of three, a **conductivity** in place of a
stiffness, a temperature in place of a displacement – and, new here, a
genuine source term, since a cell generates the heat this problem
moves rather than only receiving it at a boundary the way the tension
rod's force did. The differential equation behind it, before any mesh
or matrix enters the picture, is the **Poisson equation**:

$$-k \nabla^2 T = q,$$

where $T$ is temperature, $k$ the material's thermal conductivity, and
$q$ the volumetric heat generation rate per unit volume. $\nabla^2 T$
is the divergence of the temperature gradient – how sharply the
gradient itself is changing from point to point – and multiplying it
by $-k$ turns that into the net rate heat flows into a point, which
the equation sets equal to whatever is generated there. Assembling
this into $K \mathbf{u} = \mathbf{f}$ the same way the rest of this
chapter assembles every other physics is exactly what
`skfem.models.poisson` does: the $\nabla^2$ operator becomes the
`laplace` bilinear form that builds $K$, and a volumetric source $q$
becomes `unit_load` scaled by $q$, building $f$. The module is named
after the general equation; `laplace` names the specific operator
inside it, and is also the name of the source-free case $q = 0$ – the
**Laplace equation** – that this equation reduces to whenever nothing
is being generated, which is why the same operator building $K$ here
would be the entire equation on its own in a model with no heat
source.

Three cells, each resting on a cooling plate that holds its base at a
fixed temperature, are the domain – no tray, no shared structure
between them, each cell warmed from the inside and cooled through its
base and outer surface:

```python
from cadquery import Solid

r, h = 9.0, 65.0
r_terminal, h_terminal = 2.5, 1.0

body = cf.cylinder(d=2 * r, h=h)
terminal = cf.cylinder(d=2 * r_terminal, h=h_terminal).moved(z=h)
cell = body + terminal
assert isinstance(cell, Solid)

cells = [cell.moved(x=(i - 1) * 24.0) for i in range(3)]

bottoms, sides = [], []
for c in cells:
    faces = c.Faces()
    bottom = min(faces, key=lambda f: f.Center().z)
    bottoms.append(bottom)
    sides.extend(f for f in faces if f is not bottom)

cadmesh = cadgmsh.mesh(cells, dim=3, lc=3, physical={"bottom": bottoms, "sides": sides})
mesh = from_meshio(cadmesh)
```

The same narrow terminal knob Chapter 3's 18650 cell used, unioned
onto the body – `sides` picks up every face the union creates, the
terminal's lateral and top faces included, with no change to how
it is collected: everything but the bottom.

`cadgmsh.mesh` accepts a list of shapes as readily as one – three
separate cells, meshed together in a single call, each keeping its own
identity in the physical groups the mesh comes back with.

A **volumetric heat source** – energy generated throughout the cell's
material, which is how a battery under load actually heats – needs a
different kind of term than a boundary condition supplies:

```python
from skfem.models.poisson import laplace, unit_load

basis = Basis(mesh, ElementTetP1())
k = 1.0e-3  # W/(mm K), an illustrative effective conductivity
K = k * laplace.assemble(basis)

q = 3.0e-5  # W/mm^3, an illustrative uniform generation rate
f = q * unit_load.assemble(basis)
```

`unit_load` integrates a test function over the whole domain rather
than over one boundary; scaled by `q`, it is exactly the right-hand
side a uniform volumetric source produces – the same role `f` played
for the tension rod's point load, built here from different physics.

The cooling plate fixes each cell's base at a known temperature; the
exposed sides and top lose heat to the surrounding air by
**convection** instead, a boundary condition of a different shape:

$$-k \, (\nabla T \cdot \mathbf{n}) = h_{\mathrm{conv}} (T - T_{\mathrm{amb}}),$$

where $\mathbf{n}$ is the outward surface normal, so $\nabla T
\cdot \mathbf{n}$ is how fast temperature rises moving out through it.
The equation reads as a balance at the surface – heat conducted up to it from
inside the cell, the left side, equals heat carried away by the air,
the right side, proportional to how much warmer the surface is than
the air around it, $T_{\mathrm{amb}}$. Unlike the fixed-temperature
plate, $T$ itself appears on both sides of $K \mathbf{u} = \mathbf{f}$
here: it drives the loss, but the loss also depends on the very
temperature the solve is looking for.

Nothing in `skfem.models` builds this particular boundary term, so it
is written out directly as two small forms, one for each side of the
equation:

```python
from skfem import FacetBasis, BilinearForm, LinearForm

fb = FacetBasis(mesh, ElementTetP1(), facets=mesh.boundaries["sides"])
h_conv, T_amb = 1.5e-5, 25.0  # W/(mm^2 K), an illustrative natural-convection value


@BilinearForm
def convective(u, v, w):
    return h_conv * u * v


@LinearForm
def ambient(v, w):
    return h_conv * T_amb * v


K = K + convective.assemble(fb)
f = f + ambient.assemble(fb)
```

`@BilinearForm` and `@LinearForm` are how `laplace` and `unit_load`
themselves are built inside scikit-fem – a plain Python function of a
trial function `u` and test function `v` (`@BilinearForm`) or of `v`
alone (`@LinearForm`), returning the integrand at one quadrature point;
`.assemble` handles the quadrature and the sum over every element or
facet the basis covers, turning that one-point formula into a full
matrix or vector. Writing them out directly here, instead of importing
a ready-made operator, is only necessary because no built-in one
happens to exist for this particular boundary term – the mechanism
underneath is the same either way.

A convective boundary contributes to both sides of $K \mathbf{u} =
\mathbf{f}$ at once: `convective` adds to $K$ because the heat a
surface loses depends on its unknown temperature; `ambient` adds
to $f$ because that loss is driven by a known quantity, the air
temperature – the same split between "depends on the unknown" and
"already known" this chapter has used throughout, applied now to a
boundary integral instead of a volume one.

```python
T_plate = 25.0
cold_dofs = basis.get_dofs(mesh.boundaries["bottom"])
T = basis.zeros()
T[cold_dofs] = T_plate

T_solved = solve(*condense(K, f, x=T, D=cold_dofs))
```

:::{figure} ../figures/generated/ch11-thermal-cells.png
:width: 70%

The solved temperature field across all three cells, identical on each
since nothing in this model couples one cell to another. Cut open to
show the interior, where the hottest point sits, on each cell's
central axis roughly 70% of the way up – warmed from every side
at once and furthest from the fixed-temperature base.
:::

The result stays in a range worth trusting on sight: 25 degrees at the
cooling plate itself, exactly the fixed temperature it was given, up to
`33.1` degrees at that interior point – a modest rise consistent with a
small cell generating a fraction of a watt into air that is free to
carry most of it away. Nothing in this
model connects one cell's mesh to its neighbors – each cell solves as
an independent thermal problem, sharing nothing but the same
cooling-plate temperature and the same surrounding air, an honest fit
for cells spaced apart with nothing but air between them, not a
statement that no real pack ever needs more.

## Toward a Design Space

The same $K \mathbf{u} = \mathbf{f}$ machinery just solved two
genuinely different kinds of physics – a structural load and a
thermal one – from the same handful of building blocks: a mesh, a
material property, a boundary condition, a solve. That repeatability is
the actual payoff of building simulation this way rather than by hand
or inside a separate GUI tool. The geometry a parametric model already
builds becomes the mesh a solver consumes directly; the same script
that generates a part regenerates its simulation the moment a
dimension changes, with no export step, no manual re-meshing, no
reapplying boundary conditions to faces that moved since the last run.
A model that carries its own check, the argument Chapter 8 opened the
book's final part with, now extends all the way to a structural or
thermal one.

Structural and thermal analysis is a discipline in its own right well
beyond these two examples – contact between parts, plasticity and
fatigue, vibration and impact, multiphysics coupling, mesh convergence
studied properly rather than checked once by hand.
This chapter's contribution is narrower: showing that the pipeline
connecting a parametric model to a real, checkable physics result is
code, the same as everything else in this book – which is exactly what
lets
Chapter 12 search a whole design space against a real simulated
result, rather than checking candidates one at a time by hand.

:::{note} Try It
- Rerun the tension rod at half the element size (`lc=1.25` instead of
  `2.5`) and average the von Mises stress over the middle of the rod
  only – elements whose centroid sits between $z = 10$ and $z = 30$ –
  and confirm it moves closer to the analytic value, the same
  convergence argument Chapter 10 raised for mesh quality in general.
  Then average over the whole mesh instead, and notice it moves the
  other way: the finer mesh resolves the concentrations at the clamp
  and the loaded nodes more sharply, and those are real features of
  these boundary conditions, not of the uniform bar the formula
  describes. Converging toward the formula everywhere would require
  boundary conditions the formula actually assumes.
- Halve `F` on the tension rod and confirm both the displacement and
  the von Mises stress halve with it – the definition of linearity,
  checked directly rather than assumed.
- Double `h_conv` on the cell model, standing in for a fan replacing
  still air, and confirm the hottest point drops. Then remove the
  convective boundary entirely and solve with the sides left bare – an
  insulated model has nowhere for most of the heat to go but the small
  cooling-plate contact area alone, and the hottest point should rise
  sharply. How much of a difference does moving air actually make here?
:::
