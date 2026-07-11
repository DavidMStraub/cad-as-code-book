"""Figure: the cell can from Chapter 8 ("Models You Can Trust") - the
chapter's finished function (validated inputs, soft-capped rim fillet,
both isinstance narrowings), shown as a three-quarter cutaway so the
wall thickness and the rounded rim are both visible. Same numbers as the
chapter's running example: r_outer=9, wall=2, height=65, rim_fillet
requested at 1.0 and capped to 0.9."""

from cadquery import Solid
from cadquery import func as cf

from _common import render


def cell_can(r_outer: float, wall: float, height: float, rim_fillet: float = 1.0) -> Solid:
    if not 0 < wall < r_outer:
        raise ValueError(f"wall must be between 0 and {r_outer}, got {wall}")
    if height <= 0:
        raise ValueError(f"height must be positive, got {height}")
    outer = cf.cylinder(d=2 * r_outer, h=height)
    inner = cf.cylinder(d=2 * (r_outer - wall), h=height)
    can = outer - inner
    assert isinstance(can, Solid)
    rim_fillet = min(rim_fillet, wall * 0.45)
    top_outer_edge = max(can.edges(">Z").Edges(), key=lambda e: e.radius())
    filleted = cf.fillet(can, top_outer_edge, rim_fillet)
    assert isinstance(filleted, Solid)
    return filleted


can = cell_can(9.0, 2.0, 65.0)
# cut the quadrant facing the default iso camera, then lay the can over
# toward the viewer - upright, a 65 x 18 mm can renders as a page-filling
# column (same lesson as the ch12 buoy figure)
cutaway = can - cf.box(20, 20, 67).translate((10, 10, -1))
cutaway = cutaway.rotate((0, 0, 0), (0, 1, 0), 60)

render(cutaway, "ch08-cell-can", elevation_offset=-10)
