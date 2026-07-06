"""Figure: the revolved 18650 cylindrical cell from Chapter 3
("Revolve: A Profile Spun Around an Axis")."""

from cadquery import func as cf

from _common import render

r_cell, h_cell = 9.0, 65.0
r_terminal, h_terminal = 2.5, 1.0

points = [
    (0, 0, 0),
    (r_cell, 0, 0),
    (r_cell, 0, h_cell - h_terminal),
    (r_terminal, 0, h_cell - h_terminal),
    (r_terminal, 0, h_cell),
    (0, 0, h_cell),
    (0, 0, 0),
]
half_profile_outline = cf.polyline(*points)
half_profile = cf.face(half_profile_outline)

cell = cf.revolve(half_profile, (0, 0, 0), (0, 0, 1))

render(cell, "ch03-18650-cell")
