"""Figure: an exact NURBS quarter circle against the ordinary polynomial
B-spline on the same three control points and knot vector, from Chapter
6 ("NURBS: Rational Curves and Exact Shape").

Both curves evaluated via raw OCP (OCCT) Geom_BSplineCurve, one rational
(weights 1, sqrt(2)/2, 1) and one not - matching the exact numbers
already verified and stated in the chapter text (max radius deviation
1.1e-16 for the NURBS curve, 1.0607 peak radius for the ordinary
B-spline).
"""

import math

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from OCP.Geom import Geom_BSplineCurve
from OCP.TColgp import TColgp_Array1OfPnt
from OCP.TColStd import TColStd_Array1OfInteger, TColStd_Array1OfReal
from OCP.gp import gp_Pnt

from _common import GENERATED_DIR

CURVE_COLOR = "#1E1E2E"
BULGE_COLOR = "#f0b562"
POLY_COLOR = "#5B9BD5"
POINT_COLOR = "#2C3E50"

for path in font_manager.findSystemFonts():
    if "LinLibertine_R." in path:
        font_manager.fontManager.addfont(path)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=path).get_name()
        break


def make_curve(weight):
    poles = TColgp_Array1OfPnt(1, 3)
    poles.SetValue(1, gp_Pnt(1, 0, 0))
    poles.SetValue(2, gp_Pnt(1, 1, 0))
    poles.SetValue(3, gp_Pnt(0, 1, 0))
    knots = TColStd_Array1OfReal(1, 2)
    knots.SetValue(1, 0.0)
    knots.SetValue(2, 1.0)
    mults = TColStd_Array1OfInteger(1, 2)
    mults.SetValue(1, 3)
    mults.SetValue(2, 3)
    if weight is None:
        return Geom_BSplineCurve(poles, knots, mults, 2)
    weights = TColStd_Array1OfReal(1, 3)
    weights.SetValue(1, 1.0)
    weights.SetValue(2, weight)
    weights.SetValue(3, 1.0)
    return Geom_BSplineCurve(poles, weights, knots, mults, 2)


exact = make_curve(math.sqrt(2) / 2)
bulge = make_curve(None)

us = np.linspace(0, 1, 200)
exact_xy = np.array([[exact.Value(u).X(), exact.Value(u).Y()] for u in us])
bulge_xy = np.array([[bulge.Value(u).X(), bulge.Value(u).Y()] for u in us])

fig, ax = plt.subplots(figsize=(5.2, 5.2))

# True reference circle, faint, underneath everything.
theta = np.linspace(0, np.pi / 2, 200)
ax.plot(np.cos(theta), np.sin(theta), color="#bbbbbb", linewidth=1.0, linestyle=(0, (1, 2)), zorder=1)

poly = np.array([[1, 0], [1, 1], [0, 1]])
ax.plot(poly[:, 0], poly[:, 1], "--", color=POLY_COLOR, linewidth=1.2, zorder=2)
ax.plot(poly[:, 0], poly[:, 1], "o", color=POINT_COLOR, markersize=6, zorder=4)

ax.plot(bulge_xy[:, 0], bulge_xy[:, 1], color=BULGE_COLOR, linewidth=2.4, zorder=3,
        label="ordinary B-spline, $h=1$ — bulges to $r=1.0607$")
ax.plot(exact_xy[:, 0], exact_xy[:, 1], color=CURVE_COLOR, linewidth=2.4, zorder=3,
        label=r"NURBS, $h=\sqrt{2}/2$ at $P_1$ — exact, $r=1$")

ax.text(1.04, -0.05, "$P_0$", fontsize=12, color=POINT_COLOR)
ax.text(1.02, 1.03, "$P_1$", fontsize=12, color=POINT_COLOR)
ax.text(-0.1, 1.04, "$P_2$", fontsize=12, color=POINT_COLOR)

ax.set_aspect("equal")
ax.axis("off")
ax.legend(loc="lower left", frameon=False, fontsize=13, bbox_to_anchor=(-0.05, -0.2))

fig.tight_layout()
out = GENERATED_DIR / "ch06-nurbs-circle.svg"
fig.savefig(out, bbox_inches="tight")
print(f"wrote {out}")
