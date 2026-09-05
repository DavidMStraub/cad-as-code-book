"""Figure: ruled vs. smooth loft through the same three circular
sections, from Chapter 6 ("Surfaces from Curves: Sweep and Loft") - the
surface analogue of piecewise Bezier vs. B-spline earlier in the
chapter. Three circles, radius 10/16/10 stacked on the z-axis; `ruled`
joins them with two straight-line CONE patches meeting at a visible
crease at the middle circle, the default smooth loft (continuity="C2")
blends them into one BSPLINE face with no crease - verified via
geomType() before drawing: ruled -> ['CONE', 'CONE'], smooth ->
['BSPLINE'].
"""

from cadquery import func as cf

from _common import EDGE_COLOR, FILL_COLOR, render

w1 = cf.wire(cf.circle(10.0))
w2 = cf.wire(cf.circle(16.0)).moved(z=25)
w3 = cf.wire(cf.circle(10.0)).moved(z=50)

ruled = cf.loft([w1, w2, w3], ruled=True).moved(x=30)
smooth = cf.loft([w1, w2, w3], ruled=False).moved(x=-30)

render(
    [ruled, smooth],
    "ch06-loft-continuity",
    colors=[FILL_COLOR, FILL_COLOR],
)
