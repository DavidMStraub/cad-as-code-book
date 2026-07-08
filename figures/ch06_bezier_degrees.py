"""Figure: degree-1, degree-2, and degree-3 Bezier curves with their
control points, from Chapter 6 ("The Power Basis and Bezier Curves") -
a straight segment, a parabola, and the cubic curve most CAD systems
default to, side by side at the same visual scale.

Generated as real SVG path data (L / Q / C commands), which are exactly
linear/quadratic/cubic Bezier curves by the SVG spec - the curve drawn
is the mathematical Bezier curve itself, not a sampled approximation.

Visual vocabulary matches bezier-handles.svg: squares for on-curve
anchor points (P_0 and P_n, the only points the curve actually touches),
circles for off-curve control points, thin lines for the control
polygon, dark stroke for the curve itself.
"""

from _common import GENERATED_DIR

CURVE_COLOR = "#1E1E2E"
POLY_COLOR = "#5B9BD5"
ANCHOR_COLOR = "#2C3E50"
LABEL_COLOR = "#2C3E50"

ANCHOR_SIZE = 7  # side length of the square anchor marker
HANDLE_R = 3.5  # radius of the circular control-point marker

PANELS = [
    {
        "title": "degree 1",
        "points": [(20, 130), (160, 45)],
    },
    {
        "title": "degree 2",
        "points": [(240, 130), (310, 30), (380, 130)],
    },
    {
        "title": "degree 3",
        "points": [(440, 145), (490, 30), (530, 145), (580, 30)],
    },
]

WIDTH, HEIGHT = 620, 190


def path_d(points):
    (x0, y0), *rest = points
    if len(points) == 2:
        (x1, y1) = rest[0]
        return f"M {x0},{y0} L {x1},{y1}"
    if len(points) == 3:
        (x1, y1), (x2, y2) = rest
        return f"M {x0},{y0} Q {x1},{y1} {x2},{y2}"
    if len(points) == 4:
        (x1, y1), (x2, y2), (x3, y3) = rest
        return f"M {x0},{y0} C {x1},{y1} {x2},{y2} {x3},{y3}"
    raise ValueError("only degree 1-3 supported")


def panel_svg(panel):
    points = panel["points"]
    n = len(points) - 1
    parts = []

    # Control polygon.
    poly_d = "M " + " L ".join(f"{x},{y}" for x, y in points)
    parts.append(
        f'<path d="{poly_d}" style="stroke:{POLY_COLOR};stroke-width:1.2;'
        f'fill:none;stroke-dasharray:3,3" />'
    )

    # The curve itself.
    parts.append(
        f'<path d="{path_d(points)}" style="stroke:{CURVE_COLOR};'
        f'stroke-width:2.2;fill:none;stroke-linecap:round" />'
    )

    # Control points: squares for the two anchors (P_0, P_n), circles
    # for everything in between.
    for i, (x, y) in enumerate(points):
        label = f'P<tspan baseline-shift="sub" font-size="9">{i}</tspan>'
        if i == 0 or i == n:
            h = ANCHOR_SIZE / 2
            parts.append(
                f'<rect x="{x - h}" y="{y - h}" width="{ANCHOR_SIZE}" '
                f'height="{ANCHOR_SIZE}" style="fill:#ffffff;'
                f'stroke:{ANCHOR_COLOR};stroke-width:1.4" />'
            )
        else:
            parts.append(
                f'<circle cx="{x}" cy="{y}" r="{HANDLE_R}" '
                f'style="fill:{POLY_COLOR};stroke:none" />'
            )
        label_y = y - 12 if y < 100 else y + 16
        parts.append(
            f'<text x="{x}" y="{label_y}" '
            f'style="fill:{LABEL_COLOR};font-family:Georgia,serif;'
            f'font-style:italic;font-size:15px;text-anchor:middle">{label}</text>'
        )

    cx = sum(x for x, _ in points) / len(points)
    parts.append(
        f'<text x="{cx}" y="{HEIGHT - 6}" '
        f'style="fill:{LABEL_COLOR};font-family:Georgia,serif;'
        f'font-size:12px;text-anchor:middle">{panel["title"]}</text>'
    )
    return "\n    ".join(parts)


def build_svg():
    body = "\n  ".join(panel_svg(p) for p in PANELS)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}"
     xmlns="http://www.w3.org/2000/svg">
  {body}
</svg>
'''


if __name__ == "__main__":
    out = GENERATED_DIR / "ch06-bezier-degrees.svg"
    out.write_text(build_svg())
    print(f"wrote {out}")
