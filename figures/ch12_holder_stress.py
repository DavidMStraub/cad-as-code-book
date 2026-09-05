"""Figure: the optimized cell holder from Chapter 12 ("A Cell Holder,
Optimized Against Its Own Simulation") - the same geometry, mesh, and
pressure-loaded elasticity solve shown in the chapter's own code, at the
optimizer's own result (t = 0.656 mm), rendered as a von Mises contour.
"""

import cadgmsh
import numpy as np
import pyvista as pv
from cadquery import Solid
from cadquery import func as cf
from skfem import Basis, ElementVector, ElementTetP1, FacetBasis, LinearForm, condense, solve
from skfem.io.meshio import from_meshio
from skfem.models.elasticity import lame_parameters, linear_elasticity, linear_stress, sym_grad

from _common import GENERATED_DIR, _crop_to_content

R_CELL, CLEARANCE, SPACING, HOLDER_H = 9.0, 0.3, 24.0, 5.0
POCKET_R = R_CELL + CLEARANCE
E, NU = 2100.0, 0.35
PRESSURE = 1.0


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


wall = 0.656
holder = cell_holder(wall)

faces = holder.Faces()
bottoms = [f for f in faces if abs(f.Center().z) < 0.01]
pockets = [
    f
    for f in faces
    if abs(f.Center().z - HOLDER_H / 2) < 0.01 and abs(f.Area() - 2 * np.pi * POCKET_R * HOLDER_H) < 1.0
]

cadmesh = cadgmsh.mesh(holder, dim=3, lc=1.5, physical={"bottom": bottoms, "pockets": pockets})
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
von_mises_elem = von_mises.mean(axis=1)

pvmesh = pv.from_meshio(cadmesh)
tet_mask = np.array([c.type == 10 for c in pvmesh.cell])
tet_grid = pvmesh.extract_cells(np.where(tet_mask)[0])
tet_grid.cell_data["von Mises (MPa)"] = von_mises_elem

pv.OFF_SCREEN = True
plotter = pv.Plotter(off_screen=True, window_size=(1600, 900), border=False)
plotter.background_color = "white"
plotter.add_mesh(
    tet_grid,
    scalars="von Mises (MPa)",
    cmap="viridis",
    show_edges=False,
    scalar_bar_args={
        "title": "von Mises (MPa)",
        "vertical": True,
        "position_x": 0.85,
        "position_y": 0.15,
        "height": 0.7,
        "width": 0.12,
        "font_family": "times",
        "title_font_size": 28,
        "label_font_size": 24,
        "color": "black",
    },
)
plotter.camera_position = "xy"
plotter.enable_parallel_projection()
plotter.reset_camera()

out_path = GENERATED_DIR / "ch12-holder-stress.png"
plotter.screenshot(str(out_path), scale=2)
_crop_to_content(out_path)
print(f"wrote {out_path}")
