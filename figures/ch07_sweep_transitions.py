"""Figure: sweeping the same circular profile along the same two-kink
polyline path with the three transition modes, from Chapter 7 ("Sweep:
A Profile Carried Along a Path"). Verified before drawing: at this 90-
degree bend, 'transformed' (the default) actually self-intersects and
pinches near-shut at the joint - isValid() still reports True - while
'right' and 'round' both build a clean elbow. A gentler 30-degree bend
with 'transformed' (checked separately, not shown here) comes out clean,
confirming the pinch is specific to how sharp this bend is, not a
general breakage of the mode.
"""

from cadquery import func as cf

from _common import FILL_COLOR, render

PATH_PTS = [(0, 0, 0), (30, 0, 0), (30, 30, 0), (60, 30, 0)]


def make(transition, offset):
    path = cf.polyline(*PATH_PTS)
    edge0 = path.Edges()[0]
    p0 = edge0.positionAt(0.0, mode="parameter")
    t0 = edge0.tangentAt(0.0, mode="parameter")
    plane = cf.Plane(p0, (0, 0, 1), t0)
    profile = cf.face(cf.wire(cf.circle(6.0))).located(plane.location)
    return cf.sweep(profile, path, transition=transition).moved(offset)

shapes = [
    make("transformed", (-90, 0, 0)),
    make("right", (0, 0, 0)),
    make("round", (90, 0, 0)),
]

render(shapes, "ch07-sweep-transitions", colors=[FILL_COLOR] * 3, azimuth_offset=20)
