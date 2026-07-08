"""Figure: an A350-scale swept, tapered wing with an upturned winglet,
from Chapter 7 ("Multisection Loft and Surface Fairness") - a spine
curve (cf.spline) carries the sweep and the winglet's upward bend, a
NACA 2412 profile is placed and oriented along it at each station
(positionAt/tangentAt, the same frame-building Sweep used earlier in
this chapter), and cf.loft connects the stations. Approximate,
illustrative dimensions (half-span ~32m, LE sweep ~32 degrees) matching
the general scale of a real widebody wing, not certified aircraft data.
Verified before drawing: wing.isValid() is True, faces are
['BSPLINE', 'PLANE', 'PLANE'].
"""

import math

import pyvista as pv
import pyvista_cad as pc
from cadquery import func as cf

from _common import EDGE_COLOR, FILL_COLOR, GENERATED_DIR, WINDOW_SIZE, _crop_to_content

SWEEP_DEG = 32.0
HALF_SPAN = 32000.0


def naca4_points(code, n=60):
    m, p, t = int(code[0]) / 100, int(code[1]) / 10, int(code[2:]) / 100
    a4 = -0.1036
    xs = [0.5 * (1 - math.cos(math.pi * i / n)) for i in range(n + 1)]

    def yt(x):
        poly = 0.2969 * math.sqrt(x) - 0.1260 * x - 0.3516 * x**2 + 0.2843 * x**3 + a4 * x**4
        return 5 * t * poly

    def camber(x):
        if x < p:
            return m / p**2 * (2 * p * x - x**2), 2 * m / p**2 * (p - x)
        return (
            m / (1 - p) ** 2 * ((1 - 2 * p) + 2 * p * x - x**2),
            2 * m / (1 - p) ** 2 * (p - x),
        )

    upper, lower = [], []
    for x in xs:
        yc, dyc = camber(x)
        theta = math.atan(dyc)
        thick = yt(x)
        upper.append((x - thick * math.sin(theta), yc + thick * math.cos(theta)))
        lower.append((x + thick * math.sin(theta), yc - thick * math.cos(theta)))
    return list(reversed(lower)) + upper[1:]


PTS01 = naca4_points("2412")

# Spine: (x_sweep, y_span, z_bend) - a straight sweep line for most of the
# span, curving up into a winglet over the last few percent.
sweep = math.tan(math.radians(SWEEP_DEG))
SPINE_PTS = [
    (0, 0, 0),
    (HALF_SPAN * 0.5 * sweep, HALF_SPAN * 0.5, 0),
    (HALF_SPAN * 0.90 * sweep, HALF_SPAN * 0.90, 100),
    (HALF_SPAN * 0.97 * sweep + 300, HALF_SPAN * 0.97, 900),
    (HALF_SPAN * 0.97 * sweep + 900, HALF_SPAN, 2400),
]
spine = cf.spline(SPINE_PTS)


def profile_at(frac, chord):
    p = spine.positionAt(frac, mode="length")
    t = spine.tangentAt(frac, mode="length")
    plane = cf.Plane(p, (1, 0, 0), t)
    pts = [(x * chord, y * chord) for x, y in PTS01]
    return cf.wire(cf.spline(pts)).located(plane.location)


STATIONS = [(0.001, 9500), (0.35, 6500), (0.65, 4200), (0.85, 2600), (0.95, 1500), (0.999, 700)]
wing = cf.loft([profile_at(f, c) for f, c in STATIONS], cap=True)
print("valid", wing.isValid(), [f.geomType() for f in wing.Faces()])

# Rotate the geometry itself to a known, reproducible orientation - wide
# (root to tip along +X) with a slight tilt to reveal the winglet - rather
# than hunt for a pyvista camera azimuth/elevation combination by trial.
bbox = wing.BoundingBox()
planform_angle = math.degrees(math.atan2(bbox.ymax, bbox.xmax))
wing_shown = wing.rotate((0, 0, 0), (0, 0, 1), -planform_angle)
wing_shown = wing_shown.rotate((0, 0, 0), (1, 0, 0), -25)

pv.OFF_SCREEN = True
plotter = pv.Plotter(off_screen=True, window_size=(1800, 900))
plotter.background_color = "white"
pc.add_cad(
    plotter, wing_shown.wrapped, color=FILL_COLOR, edges=True,
    edge_color=EDGE_COLOR, line_width=5.0, smooth=True, opacity=1.0,
)
plotter.camera_position = "xy"
plotter.enable_parallel_projection()
plotter.reset_camera()

out_path = GENERATED_DIR / "ch07-wing.png"
plotter.screenshot(str(out_path), scale=2)
_crop_to_content(out_path)
print(f"wrote {out_path}")
