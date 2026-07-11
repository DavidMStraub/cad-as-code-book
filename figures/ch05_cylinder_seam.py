"""Figure: the bare cylinder from Chapter 5 ("Geometry and Topology") with
its topological edges drawn - the two circular rims and the seam running up
the lateral face, whose two endpoints are the cylinder's only vertices.
The renderer skips seam edges when drawing a solid's edge set, so the seam
is passed as an explicit second shape. Edges are near-white here (instead
of the book's usual dark edge color) so they stay visible against the
shaded lateral face - this figure is *about* the edges."""

from cadquery import func as cf

from _common import FILL_COLOR, render

LIGHT_EDGE = "#f0f4f8"

cyl = cf.cylinder(d=10, h=10).moved(rz=115)  # turn the seam toward the camera
seam = [e for e in cyl.Edges() if e.geomType() == "LINE"][0]

render(
    [cyl, seam],
    "ch05-cylinder-seam",
    colors=[FILL_COLOR, LIGHT_EDGE],
    edge_color=LIGHT_EDGE,
)
