"""Figure: the NACA 2412 airfoil from Chapter 7 ("Multisection Loft: A
Curved Spine of Profiles") - the outline naca4_points produces, with its
two ingredients drawn in: the camber line (dashed), and the thickness
distribution indicated by the perpendicular segment at its widest point
(x ~ 0.3, thickness 0.12 of chord). Same formulas as the chapter's
listing, evaluated here for plotting."""

import math

import matplotlib.pyplot as plt
from matplotlib import font_manager

from _common import GENERATED_DIR

OUTLINE_COLOR = "#1E1E2E"
CAMBER_COLOR = "#f0b562"
CHORD_COLOR = "#9aa3ab"

for path in font_manager.findSystemFonts():
    if "LinLibertine_R." in path:
        font_manager.fontManager.addfont(path)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=path).get_name()
        break


def naca4_points(code, n=60):
    m, p, t = int(code[0]) / 100, int(code[1]) / 10, int(code[2:]) / 100
    xs = [0.5 * (1 - math.cos(math.pi * i / n)) for i in range(n + 1)]

    def thickness(x):
        poly = 0.2969 * math.sqrt(x) - 0.1260 * x - 0.3516 * x**2 + 0.2843 * x**3
        return 5 * t * (poly - 0.1036 * x**4)

    def camber(x):
        if x < p:
            return m / p**2 * (2 * p * x - x**2), 2 * m / p**2 * (p - x)
        k = m / (1 - p) ** 2
        return k * ((1 - 2 * p) + 2 * p * x - x**2), 2 * k * (p - x)

    upper, lower = [], []
    for x in xs:
        yc, dyc = camber(x)
        theta, yt = math.atan(dyc), thickness(x)
        upper.append((x - yt * math.sin(theta), yc + yt * math.cos(theta)))
        lower.append((x + yt * math.sin(theta), yc - yt * math.cos(theta)))
    return list(reversed(lower)) + upper[1:], camber, thickness


outline, camber, thickness = naca4_points("2412")

fig, ax = plt.subplots(figsize=(7, 2.2))
ox, oy = zip(*outline)
ax.plot(ox, oy, color=OUTLINE_COLOR, linewidth=1.8)

# chord line
ax.plot([0, 1], [0, 0], color=CHORD_COLOR, linewidth=1.0, linestyle=":")

# camber line
cx = [i / 200 for i in range(201)]
cy = [camber(x)[0] for x in cx]
ax.plot(cx, cy, color=CAMBER_COLOR, linewidth=1.6, linestyle="--")

# thickness at its widest: perpendicular segment through the camber line
x_t = 0.297
yc, dyc = camber(x_t)
theta, yt = math.atan(dyc), thickness(x_t)
ax.plot(
    [x_t + yt * math.sin(theta), x_t - yt * math.sin(theta)],
    [yc - yt * math.cos(theta), yc + yt * math.cos(theta)],
    color=OUTLINE_COLOR,
    linewidth=1.2,
    marker="_",
    markersize=7,
)

ax.set_aspect("equal")
ax.axis("off")
fig.tight_layout()
out_path = GENERATED_DIR / "ch07-airfoil.svg"
fig.savefig(out_path, bbox_inches="tight")
print(f"wrote {out_path}")
