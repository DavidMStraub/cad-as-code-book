"""Figure: the extruded prismatic-cell housing from Chapter 3
("Extrude: A Profile Pushed Straight Up")."""

from cadquery import func as cf

from _common import render

profile = cf.face(cf.rect(27, 148))
housing = cf.extrude(profile, (0, 0, 91))

render(housing, "ch03-housing", azimuth_offset=110)
