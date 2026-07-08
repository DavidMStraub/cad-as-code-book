"""Figure: Bernstein basis functions (Bezier) next to B-spline basis
functions, from Chapter 6 ("Building Curves from Control Points") - the
same-degree pair, drawn to the same style, so global support (left)
versus local support (right) is visible at a glance rather than asserted
in prose.

Cox-de Boor recursion implemented directly (not imported from CadQuery/
OCCT) since this is a pure function-of-u plot, not a modeling operation;
verified against partition of unity (sum of all N_i,k(u) == 1 everywhere)
before use.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

from _common import GENERATED_DIR

# Validated categorical palette (dataviz skill, references/palette.md,
# light mode, slots 1-7) - fixed order, reused across both panels so the
# shared low indices (0-3) read as the same "identity" in each plot.
COLORS = [
    "#2a78d6",  # 1 blue
    "#1baf7a",  # 2 aqua
    "#eda100",  # 3 yellow
    "#008300",  # 4 green
    "#4a3aa7",  # 5 violet
    "#e34948",  # 6 red
    "#e87ba4",  # 7 magenta
]

for path in font_manager.findSystemFonts():
    if "LinLibertine_R." in path:
        font_manager.fontManager.addfont(path)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=path).get_name()
        break


def bernstein(i, n, u):
    from math import comb
    return comb(n, i) * u**i * (1 - u) ** (n - i)


def bspline_basis(i, k, knots, u):
    """Cox-de Boor recursion, N_{i,k}(u); k = order (degree + 1)."""
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


fig, (ax_bez, ax_bsp) = plt.subplots(1, 2, figsize=(11, 4.2))

# Left: Bernstein basis, degree 3, matches the book's running cubic example.
u = np.linspace(0, 1, 400)
for i in range(4):
    y = bernstein(i, 3, u)
    ax_bez.plot(u, y, color=COLORS[i], linewidth=2.2)
    peak_u = i / 3
    ax_bez.text(
        peak_u, bernstein(i, 3, peak_u) + 0.04, f"$B_{{{i},3}}$",
        color=COLORS[i], ha="center", fontsize=12,
    )
ax_bez.set_xlim(0, 1)
ax_bez.set_ylim(0, 1.12)
ax_bez.set_xlabel("$u$")
ax_bez.set_title("Bernstein basis (Bézier, degree 3)\nevery function nonzero on all of $[0,1]$")

# Right: cubic B-spline basis, classic clamped knot vector with three
# simple interior knots - degree 3, order k=4, 7 control points.
knots = [0, 0, 0, 0, 1, 2, 3, 4, 4, 4, 4]
k = 4
n_basis = len(knots) - k
uu = np.linspace(0, 4, 800)
for i in range(n_basis):
    y = np.array([bspline_basis(i, k, knots, uv) for uv in uu])
    ax_bsp.plot(uu, y, color=COLORS[i], linewidth=2.2)
    peak_idx = np.argmax(y)
    ax_bsp.text(
        uu[peak_idx], y[peak_idx] + 0.04, f"$N_{{{i},4}}$",
        color=COLORS[i], ha="center", fontsize=11,
    )
for kv in sorted(set(knots)):
    ax_bsp.axvline(kv, color="#cccccc", linewidth=0.8, zorder=0)
ax_bsp.set_xlim(0, 4)
ax_bsp.set_ylim(0, 1.12)
ax_bsp.set_xlabel("$u$")
ax_bsp.set_title("B-spline basis (order $k=4$, knots $0,0,0,0,1,2,3,4,4,4,4$)\neach function nonzero on only 4 spans")

for ax in (ax_bez, ax_bsp):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylabel("")

fig.tight_layout()
out = GENERATED_DIR / "ch06-basis-functions.svg"
fig.savefig(out)
print(f"wrote {out}")
