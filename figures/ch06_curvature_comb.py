"""Figure: curvature comb across a line-to-arc join, from Chapter 6
("Continuity Classes") - a straight line meeting a circular arc
tangentially (G1: no visible kink) but with curvature jumping
discontinuously from 0 to 1/R at the join (not G2).

Curvature computed analytically for both pieces (0 for the line, 1/R
for the arc) rather than estimated numerically, so the comb's jump is
exact by construction, not a finite-difference artifact.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

from _common import GENERATED_DIR

CURVE_COLOR = "#1E1E2E"
COMB_COLOR = "#f0b562"
JOIN_COLOR = "#2C3E50"

for path in font_manager.findSystemFonts():
    if "LinLibertine_R." in path:
        font_manager.fontManager.addfont(path)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=path).get_name()
        break

R = 60.0
LINE_LEN = 140.0
ARC_SWEEP_DEG = 100.0  # from -90 deg (join point) sweeping this many degrees

# Line: from (-LINE_LEN, 0) to (0, 0), tangent (1, 0), curvature 0.
n_line = 60
line_x = np.linspace(-LINE_LEN, 0, n_line)
line_y = np.zeros_like(line_x)
line_pts = np.stack([line_x, line_y], axis=1)
line_tangent = np.tile([1.0, 0.0], (n_line, 1))
line_kappa = np.zeros(n_line)

# Arc: center (0, R), starting at (0,0) (angle -90 deg from center),
# tangent (1,0) there, sweeping counterclockwise. Curvature 1/R constant.
n_arc = 60
theta0 = -np.pi / 2
theta1 = theta0 + np.radians(ARC_SWEEP_DEG)
thetas = np.linspace(theta0, theta1, n_arc)
arc_x = R * np.cos(thetas)
arc_y = R + R * np.sin(thetas)
arc_pts = np.stack([arc_x, arc_y], axis=1)
# tangent = d/dtheta (R cos, R+R sin) normalized = (-sin, cos)
arc_tangent = np.stack([-np.sin(thetas), np.cos(thetas)], axis=1)
arc_kappa = np.full(n_arc, 1.0 / R)

all_pts = np.concatenate([line_pts, arc_pts])
all_tangent = np.concatenate([line_tangent, arc_tangent])
all_kappa = np.concatenate([line_kappa, arc_kappa])

# Left normal (rotate tangent +90 deg): (x,y) -> (-y, x)
normals = np.stack([-all_tangent[:, 1], all_tangent[:, 0]], axis=1)

COMB_SCALE = 1000.0
comb_len = all_kappa * COMB_SCALE

fig, ax = plt.subplots(figsize=(9, 4.6))

ax.plot(all_pts[:, 0], all_pts[:, 1], color=CURVE_COLOR, linewidth=2.4, zorder=3)

# Comb teeth, sparser than the sample density for clarity.
stride = 3
for i in range(0, len(all_pts), stride):
    p = all_pts[i]
    tip = p + normals[i] * comb_len[i]
    ax.plot([p[0], tip[0]], [p[1], tip[1]], color=COMB_COLOR, linewidth=1.0, zorder=2)

# Comb envelope (connecting the tooth tips) to make the jump legible as a shape.
tips = all_pts + normals * comb_len[:, None]
ax.plot(tips[:, 0], tips[:, 1], color=COMB_COLOR, linewidth=1.2, alpha=0.6, zorder=1)

# Mark the join.
join = np.array([0.0, 0.0])
ax.plot(*join, "o", color=JOIN_COLOR, markersize=6, zorder=4)
ax.annotate(
    "join: position and tangent\nmatch, curvature does not",
    xy=join, xytext=(-70, 55),
    fontsize=10, color="#333333",
    arrowprops=dict(arrowstyle="-", color="#888888", linewidth=0.8),
)

ax.text(-90, -14, "line, $\\kappa=0$", fontsize=11, color="#555555", ha="center")
ax.text(85, 60, "arc, $\\kappa=1/R$", fontsize=11, color="#555555", ha="center")

ax.set_aspect("equal")
ax.set_ylim(-25, 105)
ax.axis("off")
fig.tight_layout()

out = GENERATED_DIR / "ch06-curvature-comb.svg"
fig.savefig(out, bbox_inches="tight")
print(f"wrote {out}")
