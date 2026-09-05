"""Figure: the thermal cell model from Chapter 11 ("A Thermal Model: Heat
Generated Inside a Cell") - the same three-cell geometry, mesh, and solve
shown in the chapter's own code, rendered as a temperature contour.
"""

import cadgmsh
import numpy as np
import pyvista as pv
from cadquery import Solid
from cadquery import func as cf
from skfem import Basis, BilinearForm, ElementTetP1, FacetBasis, LinearForm, condense, solve
from skfem.io.meshio import from_meshio
from skfem.models.poisson import laplace, unit_load

from _common import GENERATED_DIR, _crop_to_content

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

basis = Basis(mesh, ElementTetP1())
k = 1.0e-3
K = k * laplace.assemble(basis)

q = 3.0e-5
f = q * unit_load.assemble(basis)

fb = FacetBasis(mesh, ElementTetP1(), facets=mesh.boundaries["sides"])
h_conv, T_amb = 1.5e-5, 25.0


@BilinearForm
def convective(u, v, w):
    return h_conv * u * v


@LinearForm
def ambient(v, w):
    return h_conv * T_amb * v


K = K + convective.assemble(fb)
f = f + ambient.assemble(fb)

T_plate = 25.0
cold_dofs = basis.get_dofs(mesh.boundaries["bottom"])
T = basis.zeros()
T[cold_dofs] = T_plate

T_solved = solve(*condense(K, f, x=T, D=cold_dofs))
print("min/max/mean:", T_solved.min(), T_solved.max(), T_solved.mean())

# Per-cell extremes, to check whether the three cells actually differ.
p = mesh.p.T
for i in range(3):
    cx = (i - 1) * 24.0
    mask = np.abs(p[:, 0] - cx) < 9.5
    print(f"cell {i}: min={T_solved[mask].min():.2f} max={T_solved[mask].max():.2f}")

pvmesh = pv.from_meshio(cadmesh)
pvmesh.point_data["T"] = T_solved

# The true hottest point sits on each cell's own axis, well inside the
# volume, not on the outer skin - a plain surface render never shows it.
# Clipping away the near half exposes each cell's own interior instead.
clipped = pvmesh.clip(normal=(0, 1, 0), origin=(0, 0, 0))

pv.OFF_SCREEN = True
plotter = pv.Plotter(off_screen=True, window_size=(1600, 900), border=False)
plotter.background_color = "white"
plotter.add_mesh(
    clipped,
    scalars="T",
    cmap="viridis",
    show_edges=False,
    scalar_bar_args={
        "title": "T (degC)",
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
plotter.camera_position = "iso"
plotter.camera.elevation -= 10
plotter.enable_parallel_projection()
plotter.reset_camera()

out_path = GENERATED_DIR / "ch11-thermal-cells.png"
plotter.screenshot(str(out_path), scale=2)
_crop_to_content(out_path)
print(f"wrote {out_path}")
