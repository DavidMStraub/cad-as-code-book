"""Figure: the completed clutch_brick from Chapter 10 ("Maker Payoff:
Printing the Clutch Brick"), rendered semi-transparent so the hollow
underside, the two long grip walls, and the center reinforcement post -
all invisible from the outside - are visible through the outer shell.
"""

from cadquery import Solid
from cadquery import func as cf

import pyvista as pv
import pyvista_cad as pc

from _common import EDGE_COLOR, FILL_COLOR, GENERATED_DIR, _crop_to_content


def clutch_brick(
    length: float,
    width: float,
    height: float,
    stud_diameter: float,
    stud_height: float,
    stud_spacing: float,
    wall: float = 1.2,
    roof: float = 1.0,
    grip_clearance: float = 0.0,
    post_diameter: float = 2.5,
) -> Solid:
    body = cf.box(length, width, height)
    stud = cf.cylinder(d=stud_diameter, h=stud_height)
    left_stud = stud.moved(x=-stud_spacing / 2, z=height)
    right_stud = stud.moved(x=stud_spacing / 2, z=height)

    cavity_width = stud_diameter - grip_clearance
    cavity_height = height - roof
    cavity = cf.box(length - 2 * wall, cavity_width, cavity_height + 1)
    cavity = cavity.moved(z=-0.5)
    hollowed = body - cavity

    post_height = cavity_height + 0.5
    post = cf.cylinder(d=post_diameter, h=post_height)

    result = hollowed + post + left_stud + right_stud
    assert isinstance(result, Solid)
    return result


brick = clutch_brick(15.6, 7.8, 9.6, 4.8, 1.7, 8.0, grip_clearance=0.15)

pv.OFF_SCREEN = True
plotter = pv.Plotter(off_screen=True, window_size=(1400, 1000))
plotter.background_color = "white"
pc.add_cad(
    plotter,
    brick.wrapped,
    color=FILL_COLOR,
    edges=True,
    edge_color=EDGE_COLOR,
    line_width=6.0,
    smooth=True,
    opacity=0.35,
)
plotter.camera_position = "iso"
plotter.camera.azimuth += 20
plotter.camera.elevation -= 10
plotter.enable_parallel_projection()
plotter.reset_camera()

out_path = GENERATED_DIR / "ch10-clutch-brick-cutaway.png"
plotter.screenshot(str(out_path), scale=2)
_crop_to_content(out_path)
print(f"wrote {out_path}")
