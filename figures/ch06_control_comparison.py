"""Figure: moving one control point in a Bezier curve versus in a
B-spline, from Chapter 6 ("B-Splines: Knots and Local Control") - the
same 7 control points used in the basis-functions figure, once as a
single degree-6 Bezier curve (7 points forces degree 6) and once as a
cubic B-spline on the same clamped knot vector, P_1 moved the same
amount in both.

Verified before drawing: on the B-spline side, the curve for u in [2,4]
is bit-for-bit identical before and after moving P_1 (P_1's basis
function is zero there); on the Bezier side nothing is identical
anywhere except the two fixed endpoints.
"""

from math import comb

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

from _common import GENERATED_DIR

CURVE_COLOR = "#1E1E2E"
MOVED_COLOR = "#f0b562"
POLY_COLOR = "#5B9BD5"
POINT_COLOR = "#2C3E50"

for path in font_manager.findSystemFonts():
    if "LinLibertine_R." in path:
        font_manager.fontManager.addfont(path)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=path).get_name()
        break

POINTS = [(20, 80), (80, 20), (160, 140), (240, 20), (320, 140), (400, 20), (460, 80)]
POINTS_MOVED = list(POINTS)
POINTS_MOVED[1] = (80, 150)

KNOTS = [0, 0, 0, 0, 1, 2, 3, 4, 4, 4, 4]
K = 4


def bernstein(i, n, u):
    return comb(n, i) * u**i * (1 - u) ** (n - i)


def bezier_curve(points, us):
    n = len(points) - 1
    xs = np.zeros_like(us)
    ys = np.zeros_like(us)
    for i, (px, py) in enumerate(points):
        w = np.array([bernstein(i, n, u) for u in us])
        xs += w * px
        ys += w * py
    return xs, ys


def bspline_basis(i, k, knots, u):
    if k == 1:
        lo, hi = knots[i], knots[i + 1]
        if lo <= u < hi:
            return 1.0
        if u == knots[-1] and lo < u <= hi:
            return 1.0
        return 0.0
    term1 = term2 = 0.0
    d1 = knots[i + k - 1] - knots[i]
    if d1 > 0:
        term1 = (u - knots[i]) / d1 * bspline_basis(i, k - 1, knots, u)
    d2 = knots[i + k] - knots[i + 1]
    if d2 > 0:
        term2 = (knots[i + k] - u) / d2 * bspline_basis(i + 1, k - 1, knots, u)
    return term1 + term2


def bspline_curve(points, knots, k, us):
    xs = np.zeros_like(us)
    ys = np.zeros_like(us)
    for i, (px, py) in enumerate(points):
        w = np.array([bspline_basis(i, k, knots, u) for u in us])
        xs += w * px
        ys += w * py
    return xs, ys


def draw_panel(ax, curve_fn, points, points_moved, title, split_point=None):
    xs0, ys0 = curve_fn(points)
    xs1, ys1 = curve_fn(points_moved)

    poly_x = [p[0] for p in points]
    poly_y = [p[1] for p in points]
    ax.plot(poly_x, poly_y, "--", color=POLY_COLOR, linewidth=1.2, zorder=1)
    ax.plot(
        [p[0] for p in points], [p[1] for p in points], "o",
        color=POINT_COLOR, markersize=5, zorder=3,
    )

    ax.plot(xs0, ys0, color=CURVE_COLOR, linewidth=2.4, zorder=2, label="original")
    ax.plot(xs1, ys1, color=MOVED_COLOR, linewidth=2.4, zorder=2, label="$P_1$ moved")

    old_p, new_p = points[1], points_moved[1]
    ax.annotate(
        "", xy=new_p, xytext=old_p,
        arrowprops=dict(arrowstyle="->", color=MOVED_COLOR, linewidth=1.6),
        zorder=4,
    )
    ax.plot(*new_p, "o", color=MOVED_COLOR, markersize=6, zorder=4)
    ax.text(
        new_p[0] - 30, new_p[1] + 2, "$P_1$", color=MOVED_COLOR, fontsize=12,
        ha="right", va="center",
    )

    if split_point is not None:
        ax.plot(*split_point, "o", color="#888888", markersize=5, zorder=5)
        ax.annotate(
            "identical from\nhere on",
            xy=split_point, xytext=(split_point[0] + 15, split_point[1] - 55),
            fontsize=9.5, color="#555555",
            arrowprops=dict(arrowstyle="-", color="#888888", linewidth=0.8),
        )

    ax.set_title(title)
    ax.set_xlim(-15, 495)
    ax.set_ylim(0, 165)
    ax.set_aspect("equal")
    ax.axis("off")


fig, (ax_bez, ax_bsp) = plt.subplots(1, 2, figsize=(11, 3.1))

draw_panel(
    ax_bez,
    lambda pts: bezier_curve(pts, np.linspace(0, 1, 400)),
    POINTS, POINTS_MOVED,
    "Single Bézier, degree 6\nmoving $P_1$ reshapes the entire curve",
)

split_u = np.array([2.0])
split_xy = bspline_curve(POINTS, KNOTS, K, split_u)
split_point = (split_xy[0][0], split_xy[1][0])

draw_panel(
    ax_bsp,
    lambda pts: bspline_curve(pts, KNOTS, K, np.linspace(0, 4, 400)),
    POINTS, POINTS_MOVED,
    "Cubic B-spline, same 7 points\nmoving $P_1$ reshapes only a local stretch",
    split_point=split_point,
)

handles, labels = ax_bez.get_legend_handles_labels()
fig.tight_layout(rect=(0, 0.08, 1, 1))
fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.0))
out = GENERATED_DIR / "ch06-control-comparison.svg"
fig.savefig(out, bbox_inches="tight")
print(f"wrote {out}")
