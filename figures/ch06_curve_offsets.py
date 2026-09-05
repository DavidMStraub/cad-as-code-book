"""Figure: offsetting a circle and an ellipse by the same 3mm, from
Chapter 6 ("The Limits of Analytic Curves") - the circle's offset stays
concentric and circular, the ellipse's offset does not stay an ellipse.
Two flat curve pairs side by side, top-down orthographic view (the curves
lie in the XY plane, so an isometric angle would only foreshorten them).
"""

import pyvista as pv
import pyvista_cad as pc
from cadquery import func as cf

from _common import EDGE_COLOR, GENERATED_DIR, LINE_WIDTH, _crop_to_content

OFFSET_COLOR = "#f0b562"

circle = cf.circle(10.0)
circle_offset = cf.offset2D(cf.wire(circle), 3.0)

ellipse = cf.ellipse(20.0, 10.0)
ellipse_offset = cf.offset2D(cf.wire(ellipse), 3.0)

shapes_and_colors = [
    (cf.wire(circle).moved(x=-35), EDGE_COLOR),
    (circle_offset.moved(x=-35), OFFSET_COLOR),
    (cf.wire(ellipse).moved(x=35), EDGE_COLOR),
    (ellipse_offset.moved(x=35), OFFSET_COLOR),
]

pv.OFF_SCREEN = True
plotter = pv.Plotter(off_screen=True, window_size=(1400, 700))
plotter.background_color = "white"

for shape, color in shapes_and_colors:
    pc.add_cad(
        plotter,
        shape.wrapped,
        color=color,
        edges=True,
        edge_color=color,
        line_width=LINE_WIDTH,
        smooth=True,
        opacity=1.0,
    )

plotter.camera_position = "xy"
plotter.enable_parallel_projection()
plotter.reset_camera()

out = GENERATED_DIR / "ch06-curve-offsets.png"
plotter.screenshot(str(out), scale=2)
_crop_to_content(out)
print(f"wrote {out}")
