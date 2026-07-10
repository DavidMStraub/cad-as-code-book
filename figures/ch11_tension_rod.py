"""Figure: the tension rod FEM solution from Chapter 11 ("Checking the
Result Against a Hand Calculation") - the same rod, mesh, and solve shown
in the chapter's own code, rendered as a von Mises stress contour. Plotted
on the undeformed shape deliberately: the real displacement is a fraction
of a millimeter on a 40mm rod and almost entirely axial (the radial,
Poisson-driven component is an order of magnitude smaller still), so even
a large exaggeration factor would not produce a shape visibly different
from a plain cylinder in a cropped, auto-scaled render - warping it would
claim a visual effect the image does not actually deliver.
"""

import cadgmsh
import numpy as np
import pyvista as pv
from cadquery import func as cf
from skfem import Basis, ElementTetP1, ElementVector, condense, solve
from skfem.io.meshio import from_meshio
from skfem.models.elasticity import lame_parameters, linear_elasticity, linear_stress, sym_grad

from _common import GENERATED_DIR, _crop_to_content

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

pvmesh = pv.from_meshio(cadmesh)

tet_mask = np.array([c.type == 10 for c in pvmesh.cell])  # VTK_TETRA
tet_grid = pvmesh.extract_cells(np.where(tet_mask)[0])
tet_grid.cell_data["von Mises (MPa)"] = von_mises_elem

pv.OFF_SCREEN = True
plotter = pv.Plotter(off_screen=True, window_size=(1000, 1000), border=False)
plotter.background_color = "white"
plotter.add_mesh(
    tet_grid,
    scalars="von Mises (MPa)",
    cmap="viridis",
    show_edges=False,
    scalar_bar_args={
        "title": "von Mises (MPa)",
        "vertical": True,
        "position_x": 0.8,
        "position_y": 0.15,
        "height": 0.7,
        "width": 0.15,
        "font_family": "times",
        "title_font_size": 32,
        "label_font_size": 28,
        "color": "black",
    },
)
plotter.camera_position = "iso"
plotter.camera.azimuth += 25
plotter.enable_parallel_projection()
plotter.reset_camera()

out_path = GENERATED_DIR / "ch11-tension-rod.png"
plotter.screenshot(str(out_path), scale=2)
_crop_to_content(out_path)
print(f"wrote {out_path}")
