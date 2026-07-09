"""Figure: the geometric diff from Chapter 9 ("The Geometric Diff") -
two revisions of a plate differ only in one mounting hole's position;
(v1 - v2) + (v2 - v1) leaves only the two crescents where they actually
disagree, everything unchanged left out of the shape entirely."""

from cadquery import func as cf

from _common import render

plate = cf.box(60, 30, 6)
hole_v1 = cf.cylinder(d=6, h=8).translate((-15, 0, 0))
hole_v2 = cf.cylinder(d=6, h=8).translate((-13, 0, 0))

v1 = plate - hole_v1
v2 = plate - hole_v2

changed = (v1 - v2) + (v2 - v1)

render(changed, "ch09-geometric-diff", colors=["#d1653d"])
