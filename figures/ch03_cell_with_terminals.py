"""Figure: the prismatic cell with two terminals from Chapter 3
("A Plane Derived from a Face")."""

from cadquery import func as cf
from cadquery import Location, Plane

from _common import render

profile = cf.face(cf.rect(27, 148))
housing = cf.extrude(profile, (0, 0, 91))

top_face = housing.faces(">Z")
top_plane = Plane(origin=top_face.Center())

terminal = cf.cylinder(d=8, h=5)
left_terminal = terminal.moved(Location(top_plane) * Location((0, -48.5, 0)))
right_terminal = terminal.moved(Location(top_plane) * Location((0, 48.5, 0)))

cell = housing + left_terminal + right_terminal

render(cell, "ch03-cell-with-terminals", azimuth_offset=110)
