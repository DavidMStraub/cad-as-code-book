"""Figure: two cell variants from Chapter 4 ("Parameter Sets as Data") -
the same make_cell function, two CellSpec instances.

Front-on orthographic view rather than the book's usual isometric angle:
the point here is a direct size comparison, and a straight-on view removes
any left/right ambiguity an isometric rotation would introduce.
"""

from dataclasses import dataclass, replace

import pyvista as pv
import pyvista_cad as pc
from cadquery import func as cf

from _common import EDGE_COLOR, FILL_COLOR, GENERATED_DIR, LINE_WIDTH, _crop_to_content


@dataclass
class CellSpec:
    r_cell: float
    h_cell: float
    r_terminal: float = 2.5
    h_terminal: float = 1.0


cell_18650 = CellSpec(r_cell=9.0, h_cell=65.0)
cell_21700 = replace(cell_18650, r_cell=10.5, h_cell=70.0)


def make_cell(spec: CellSpec):
    points = [
        (0, 0, 0),
        (spec.r_cell, 0, 0),
        (spec.r_cell, 0, spec.h_cell - spec.h_terminal),
        (spec.r_terminal, 0, spec.h_cell - spec.h_terminal),
        (spec.r_terminal, 0, spec.h_cell),
        (0, 0, spec.h_cell),
        (0, 0, 0),
    ]
    return cf.revolve(cf.face(cf.polyline(*points)), (0, 0, 0), (0, 0, 1))


cell_a = make_cell(cell_18650).translate((-20, 0, 0))
cell_b = make_cell(cell_21700).translate((20, 0, 0))

pv.OFF_SCREEN = True
plotter = pv.Plotter(off_screen=True, window_size=(1400, 1000))
plotter.background_color = "white"
pc.add_cad(
    plotter,
    cell_a.wrapped,
    color=FILL_COLOR,
    edges=True,
    edge_color=EDGE_COLOR,
    line_width=LINE_WIDTH,
    smooth=True,
    opacity=1.0,
)
pc.add_cad(
    plotter,
    cell_b.wrapped,
    color="#f0b562",
    edges=True,
    edge_color=EDGE_COLOR,
    line_width=LINE_WIDTH,
    smooth=True,
    opacity=1.0,
)
plotter.camera_position = "xz"
plotter.enable_parallel_projection()
plotter.reset_camera()
out = GENERATED_DIR / "ch04-cell-variants.png"
plotter.screenshot(str(out), scale=2)
_crop_to_content(out)
print(f"wrote {out}")
