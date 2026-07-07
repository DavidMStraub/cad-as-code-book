"""Figure: the widened tray from Chapter 4 ("Multiplying Geometry: Symmetry
and Patterns") - mirrored mounting holes and three cell pockets placed by
a loop."""

from cadquery import func as cf

from _common import render

width, depth, thickness = 100, 30, 6
mounting_hole = cf.cylinder(d=3.4, h=thickness).translate((44, 12, 0))
mounting_holes = mounting_hole + mounting_hole.mirror("YZ", basePointVector=(0, 0, 0))

plate = cf.box(width, depth, thickness)
plate_with_holes = plate - mounting_holes

cell_radius, clearance, pocket_depth = 9.0, 0.3, 3.0
pocket = cf.cylinder(d=2 * (cell_radius + clearance), h=pocket_depth)
pocket = pocket.translate((0, 0, thickness - pocket_depth))

tray = plate_with_holes
for i in range(3):
    x = (i - 1) * 24.0
    tray = tray - pocket.translate((x, 0, 0))

render(tray, "ch04-tray-patterns")
