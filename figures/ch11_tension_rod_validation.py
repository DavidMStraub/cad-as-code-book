"""Figure: FEM vs. analytic solution along the tension rod's own axis,
from Chapter 11 ("Checking the Result Against a Hand Calculation") - the
same solve shown in the chapter's own code, plotted instead of printed so
the St. Venant spread near the loaded face is visible directly rather
than described in two pairs of numbers.
"""

import cadgmsh
import matplotlib.pyplot as plt
import numpy as np
from cadquery import func as cf
from matplotlib import font_manager
from skfem import Basis, ElementTetP1, ElementVector, condense, solve
from skfem.io.meshio import from_meshio
from skfem.models.elasticity import lame_parameters, linear_elasticity, linear_stress, sym_grad

from _common import EDGE_COLOR, FILL_COLOR, GENERATED_DIR

for path in font_manager.findSystemFonts():
    if "LinLibertine_R." in path:
        font_manager.fontManager.addfont(path)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=path).get_name()
        break

r, length = 10.0, 40.0
rod = cf.cylinder(d=2 * r, h=length)
bottom = rod.faces("<Z")
top = rod.faces(">Z")

cadmesh = cadgmsh.mesh(rod, dim=3, lc=2.5, physical={"top": top, "bottom": bottom})
mesh = from_meshio(cadmesh)

E, nu = 210e3, 0.3
lam, mu = lame_parameters(E, nu)
basis = Basis(mesh, ElementVector(ElementTetP1()))
K = linear_elasticity(lam, mu).assemble(basis)

F = 1000.0
top_dofs = basis.get_dofs(mesh.boundaries["top"]).nodal["u^3"]
f = basis.zeros()
f[top_dofs] = F / len(top_dofs)
fixed_dofs = basis.get_dofs(mesh.boundaries["bottom"]).all()
u = solve(*condense(K, f, D=fixed_dofs))

eps = sym_grad(basis.interpolate(u))
sigma = linear_stress(lam, mu)(eps)
s11, s22, s33 = sigma[0, 0], sigma[1, 1], sigma[2, 2]
s12, s23, s31 = sigma[0, 1], sigma[1, 2], sigma[2, 0]
von_mises = np.sqrt(
    0.5 * ((s11 - s22) ** 2 + (s22 - s33) ** 2 + (s33 - s11) ** 2 + 6 * (s12**2 + s23**2 + s31**2))
)
von_mises_elem = von_mises.mean(axis=1)
elem_z = mesh.p[2, mesh.t].mean(axis=0)

uz_um = u[basis.nodal_dofs[2]] * 1000.0
node_z = mesh.p[2]

A = np.pi * r**2
z_line = np.linspace(0, length, 100)
uz_analytic_um = F * z_line / (E * A) * 1000.0
sigma_analytic = F / A

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4.2))

ax1.scatter(node_z, uz_um, s=6, color=FILL_COLOR, edgecolor=EDGE_COLOR, linewidth=0.3, label="FEM nodes")
ax1.plot(z_line, uz_analytic_um, color=EDGE_COLOR, linewidth=1.5, label="analytic")
ax1.set_xlabel("z (mm)")
ax1.set_ylabel("$u_z$ (µm)")
ax1.set_title("Displacement")
ax1.legend(frameon=False, fontsize=8)

ax2.scatter(
    elem_z, von_mises_elem, s=6, color=FILL_COLOR, edgecolor=EDGE_COLOR, linewidth=0.3, label="FEM elements"
)
ax2.axhline(sigma_analytic, color=EDGE_COLOR, linewidth=1.5, label="analytic")
ax2.set_xlabel("z (mm)")
ax2.set_ylabel("von Mises (MPa)")
ax2.set_title("Stress")
ax2.legend(frameon=False, fontsize=8)

fig.tight_layout()
out_path = GENERATED_DIR / "ch11-tension-rod-validation.png"
fig.savefig(out_path, dpi=200)
print(f"wrote {out_path}")
