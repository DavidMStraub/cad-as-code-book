"""Figure: the battery module from Chapter 9 ("Assembling the Battery
Module") - Chapter 4's tray plus three of Chapter 3/4's make_cell
cylinders, placed by a plain loop over Locations and named as a
cq.Assembly. The figure itself renders the plain shapes (pyvista_cad
draws Shapes, not Assembly trees), colored the same way the assembly's
cq.Color calls do, to match the book's screenshot conventions. Cells
seat in their pockets (z = thickness - pocket_depth), matching the
chapter's placement fix.
"""

from cadquery import func as cf

from _common import render

width, depth, thickness = 100, 30, 6
mounting_hole = cf.cylinder(d=3.4, h=thickness).moved(x=44, y=12)
mounting_holes = mounting_hole + mounting_hole.mirror("YZ", basePointVector=(0, 0, 0))
tray = cf.box(width, depth, thickness) - mounting_holes

cell_radius, clearance, pocket_depth = 9.0, 0.3, 3.0
pocket = cf.cylinder(d=2 * (cell_radius + clearance), h=pocket_depth)
pocket = pocket.moved(z=thickness - pocket_depth)
for i in range(3):
    tray = tray - pocket.moved(x=(i - 1) * 24.0)


def make_cell(r_cell, h_cell, r_terminal=2.5, h_terminal=1.0):
    points = [
        (0, 0, 0),
        (r_cell, 0, 0),
        (r_cell, 0, h_cell - h_terminal),
        (r_terminal, 0, h_cell - h_terminal),
        (r_terminal, 0, h_cell),
        (0, 0, h_cell),
        (0, 0, 0),
    ]
    return cf.revolve(cf.face(cf.polyline(*points)), (0, 0, 0), (0, 0, 1))


cell = make_cell(9.0, 65.0)
cells = [cell.moved(x=(i - 1) * 24.0, z=thickness - pocket_depth) for i in range(3)]

shapes = [tray] + cells
colors = ["#b0b0b0"] + ["#4a86c5"] * 3
render(shapes, "ch09-battery-module", colors=colors)
