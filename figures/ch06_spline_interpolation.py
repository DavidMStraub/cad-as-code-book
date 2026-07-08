"""Figure: interpolating a curve through data points, from Chapter 6
("Interpolating Curves Through Points") - the same 5 points used in the
chapter's own cf.spline code example, shown against the control points
GeomAPI_Interpolate actually solves for. The curve passes exactly
through every data point (verified in the chapter text by evaluating
the curve at each chord-length knot); the control polygon does not -
only the first and last control point coincide with a data point, the
interior ones sit elsewhere, exactly the distinction the section makes.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from cadquery import func as cf

from _common import GENERATED_DIR

CURVE_COLOR = "#1E1E2E"
DATA_COLOR = "#e34948"
CONTROL_COLOR = "#5B9BD5"

for path in font_manager.findSystemFonts():
    if "LinLibertine_R." in path:
        font_manager.fontManager.addfont(path)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=path).get_name()
        break

points = [(0, 0, 0), (10, 15, 0), (25, 5, 0), (40, 20, 0), (50, 0, 0)]
edge = cf.spline(points)
curve = BRep_Tool.Curve_s(edge.wrapped, TopLoc_Location(), 0.0, 1.0)

u0, u1 = curve.FirstParameter(), curve.LastParameter()
us = np.linspace(u0, u1, 400)
curve_xy = np.array([[curve.Value(u).X(), curve.Value(u).Y()] for u in us])

poles = [curve.Pole(i) for i in range(1, curve.NbPoles() + 1)]
poles_xy = np.array([[p.X(), p.Y()] for p in poles])

data_xy = np.array([[p[0], p[1]] for p in points])

fig, ax = plt.subplots(figsize=(7.5, 4.2))

ax.plot(poles_xy[:, 0], poles_xy[:, 1], "--", color=CONTROL_COLOR, linewidth=1.2, zorder=1)
ax.plot(poles_xy[:, 0], poles_xy[:, 1], "o", color=CONTROL_COLOR, markersize=7,
        zorder=3, label="control points $\\mathbf{P}_i$ (solved for)")
mean_x = poles_xy[:, 0].mean()
for i, (x, y) in enumerate(poles_xy):
    dx = -12 if x < mean_x else 8
    ha = "right" if x < mean_x else "left"
    ax.annotate(f"$P_{{{i}}}$", (x, y), textcoords="offset points", xytext=(dx, 9),
                fontsize=10, color=CONTROL_COLOR, ha=ha)

ax.plot(curve_xy[:, 0], curve_xy[:, 1], color=CURVE_COLOR, linewidth=2.4, zorder=2,
        label="interpolating spline")

ax.plot(data_xy[:, 0], data_xy[:, 1], "o", color=DATA_COLOR, markersize=9,
        zorder=4, label="data points $\\mathbf{Q}_i$ (given)")
for i, (x, y) in enumerate(data_xy):
    dy = -16 if i not in (0, 4) else -16
    ax.annotate(f"$Q_{{{i}}}$", (x, y), textcoords="offset points", xytext=(-4, dy),
                fontsize=11, color=DATA_COLOR, ha="right")

ax.set_aspect("equal")
ax.axis("off")
ax.legend(loc="upper center", frameon=False, fontsize=11, ncol=3,
          bbox_to_anchor=(0.5, -0.02))

fig.tight_layout()
out = GENERATED_DIR / "ch06-spline-interpolation.svg"
fig.savefig(out, bbox_inches="tight")
print(f"wrote {out}")
