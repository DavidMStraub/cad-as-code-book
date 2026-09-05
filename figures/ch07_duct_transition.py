"""Figure: a round-to-rectangular duct transition, from Chapter 7
("Loft: Interpolating Between Profiles") - a circle and a rectangle,
lofted, capped. Neither extrude nor revolve can build this: the two
end profiles are different shapes, not just different sizes of the
same one. Verified before drawing: cap=True gives a valid solid,
faces ['BSPLINE'] x5 (lateral) + ['PLANE'] x2 (the two flat ends).
"""

from cadquery import func as cf

from _common import FILL_COLOR, render

bottom = cf.wire(cf.circle(25.0))
top = cf.wire(cf.rect(60.0, 40.0)).moved(z=80)

duct = cf.loft([bottom, top], cap=True)

render([duct], "ch07-duct-transition", colors=[FILL_COLOR])
