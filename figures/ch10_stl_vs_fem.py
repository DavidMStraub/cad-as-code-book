"""Figure: STL tessellation vs. FEM volume mesh on the same part, from
Chapter 10 ("Two Meshes, Two Jobs") - a plain plate with a hole, chosen
deliberately generic rather than tied to the battery thread (an earlier
draft used Chapter 8's cell_can, a concentric-cylinder tube, but nothing
later in this book actually simulates a battery can, so that connection
was never real - see the standalone cadgmsh bug report in
private/ for why that shape also happens to break gmsh's native-pointer
import, independent of this decision).

Left panel: CadQuery's own tessellate(), the same triangulation
exportStl() writes, surface-only, optimized for shape fidelity - few
large triangles on the flat faces, denser rings around the curved hole.
Right panel: cadgmsh.mesh(part, dim=3), a real FEM mesh - surface
triangles plus tetrahedra filling the interior, sized for uniform,
well-shaped elements rather than surface fidelity alone.
"""

import cadgmsh
import numpy as np
import pyvista as pv
from cadquery import func as cf

from _common import EDGE_COLOR, FILL_COLOR, GENERATED_DIR, _crop_to_content

plate = cf.box(60, 40, 6)
hole = cf.cylinder(d=16, h=8).moved(z=-1)
part = plate - hole

# Left: STL tessellation (surface only, tuned for shape fidelity)
verts, tris = part.tessellate(tolerance=0.2, angularTolerance=0.15)
points = np.array([(v.x, v.y, v.z) for v in verts])
faces = np.hstack([[3, *t] for t in tris])
stl_mesh = pv.PolyData(points, faces)

# Right: FEM volume mesh (surface + interior tetrahedra, tuned for uniform elements)
fem_meshio = cadgmsh.mesh(part, dim=3, lc=5)
fem_mesh = pv.from_meshio(fem_meshio)

pv.OFF_SCREEN = True
plotter = pv.Plotter(off_screen=True, shape=(1, 2), window_size=(2000, 1100), border=False)

plotter.subplot(0, 0)
plotter.add_mesh(stl_mesh, color=FILL_COLOR, show_edges=True, edge_color=EDGE_COLOR, line_width=1.5)
plotter.camera_position = "iso"
plotter.enable_parallel_projection()

plotter.subplot(0, 1)
plotter.add_mesh(
    fem_mesh, color=FILL_COLOR, show_edges=True, edge_color=EDGE_COLOR, line_width=1.0, opacity=0.9
)
plotter.camera_position = "iso"
plotter.enable_parallel_projection()

plotter.link_views()
out_path = GENERATED_DIR / "ch10-stl-vs-fem.png"
plotter.screenshot(str(out_path), scale=2)
_crop_to_content(out_path)
print(f"wrote {out_path}")
