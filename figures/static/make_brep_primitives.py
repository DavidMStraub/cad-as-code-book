#!/usr/bin/env python3
"""Generate figures/static/ch05-brep-primitives.svg.

The seven topological primitives of Chapter 5, side by side in increasing
dimension. Replaces an earlier raster version of the same diagram; this one
is vector, so it stays sharp in print and picks up the book's body font.

The 3D primitives (shell, solid, and the little solid inside the compound)
are drawn in true isometric projection so they sit in the same visual world
as the rendered CAD figures; the 0D-2D ones are plain planar drawings.

Usage:
    python make_brep_primitives.py > ch05-brep-primitives.svg
"""

from math import cos, radians

# Palette: the fill/edge pair the rendered CAD figures use (see
# figures/_common.py), plus a lighter and a darker shade of the fill to
# give the isometric bodies their faces, and the book's text color.
FILL = "#a2cbf0"
FILL_LIGHT = "#cbe4f9"
FILL_DARK = "#7db2e3"
EDGE = "#2c5a8a"
TEXT = "#1e1e2e"

STROKE_WIDTH = 2.6
DOT_RADIUS = 8.0
FONT_SIZE = 28

# Panels are packed about as tightly as the widest drawing (the compound's
# container) and the longest label ("compound") allow: the figure runs the
# full text width in print, so the tighter the row, the larger everything in
# it ends up on the page.
PANEL_STEP = 145  # horizontal distance between panel centers
PANEL_PAD = 12  # left/right margin, so the compound's container has air
SHAPE_Y = 80  # vertical center of the shape area, in SVG coordinates
LABEL_Y = 180  # baseline of the label row
WIDTH = 7 * PANEL_STEP + 2 * PANEL_PAD
HEIGHT = 200

COS30 = cos(radians(30))


def iso(x, y, z, size):
    """Isometric projection of a point in a `size`-cubed box, with the
    box's own center mapped to the local origin."""
    c = size / 2
    sx = ((x - c) - (y - c)) * COS30
    sy = ((x - c) + (y - c)) * 0.5 - (z - c)
    return sx, sy


def cube_corners(size):
    """The eight corners of a `size` cube, keyed by which of the low (0)
    or high (1) face each coordinate sits on."""
    return {
        (i, j, k): iso(i * size, j * size, k * size, size)
        for i in (0, 1)
        for j in (0, 1)
        for k in (0, 1)
    }


def poly(points, fill):
    pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    return f'<polygon class="face" points="{pts}" fill="{fill}"/>'


def dot(x, y, r=DOT_RADIUS):
    return f'<circle class="dot" cx="{x:.2f}" cy="{y:.2f}" r="{r}"/>'


def panel(index, body):
    """Wrap one primitive's drawing in a group centered on its panel."""
    cx = PANEL_PAD + PANEL_STEP * index + PANEL_STEP / 2
    inner = "\n      ".join(body)
    return (
        f'    <g transform="translate({cx:.1f},{SHAPE_Y})">\n'
        f"      {inner}\n"
        f"    </g>"
    )


# --- the seven primitives -------------------------------------------------

def vertex():
    return [dot(0, 0, DOT_RADIUS + 1)]


def edge():
    return [
        '<path class="line" d="M -55,37 Q 0,-25 55,-37"/>',
        dot(-55, 37),
        dot(55, -37),
    ]


# One closed chain of four edges - three straight, one curved, so that the
# "chain of curves" reading survives. The face panel reuses it filled, which
# is the point: a face is this boundary plus a surface to span it.
WIRE_CORNERS = [(-52, -34), (45, -47), (55, 34), (-43, 45)]
WIRE_PATH = "M -52,-34 L 45,-47 Q 84,-9 55,34 L -43,45 Z"


def wire():
    return [f'<path class="line" d="{WIRE_PATH}"/>'] + [
        dot(x, y) for x, y in WIRE_CORNERS
    ]


def face():
    return [f'<path class="face" fill="{FILL}" d="{WIRE_PATH}"/>']


def shell(size=64, height=0.5):
    """An open box missing its lid - the example the chapter builds in code
    right after this figure. Faces are shaded by the direction they face, so
    the two we see from inside read as interior surfaces and the box reads as
    open. Squatter than a cube because at this viewing angle a full-height
    open box hides its own floor behind the near walls.

    Painter's order: far walls, floor, near walls."""
    h = size * height

    def p(x, y, z):
        return iso(x * size, y * size, z * size, size)

    # `iso` centers the notional cube the footprint came from; the squat box
    # runs from -h to +size on screen, so recenter on that instead.
    dy = -(size - h) / 2
    far_x = [p(0, 0, 0), p(0, 1, 0), p(0, 1, height), p(0, 0, height)]
    far_y = [p(0, 0, 0), p(1, 0, 0), p(1, 0, height), p(0, 0, height)]
    floor = [p(0, 0, 0), p(1, 0, 0), p(1, 1, 0), p(0, 1, 0)]
    near_x = [p(1, 0, 0), p(1, 1, 0), p(1, 1, height), p(1, 0, height)]
    near_y = [p(0, 1, 0), p(1, 1, 0), p(1, 1, height), p(0, 1, height)]
    faces = [
        poly(far_x, FILL),
        poly(far_y, FILL_DARK),
        poly(floor, FILL_LIGHT),
        poly(near_x, FILL),
        poly(near_y, FILL_DARK),
    ]
    return [f'<g transform="translate(0,{dy:.2f})">'] + faces + ["</g>"]


def solid(size=60):
    """A closed box, shaded as three visible faces."""
    c = cube_corners(size)
    top = [c[0, 0, 1], c[1, 0, 1], c[1, 1, 1], c[0, 1, 1]]
    right = [c[1, 0, 1], c[1, 1, 1], c[1, 1, 0], c[1, 0, 0]]
    left = [c[0, 1, 1], c[1, 1, 1], c[1, 1, 0], c[0, 1, 0]]
    return [
        poly(top, FILL_LIGHT),
        poly(right, FILL),
        poly(left, FILL_DARK),
    ]


def compound():
    """A dashed container holding one of each kind of thing, with nothing
    connecting them - which is all a compound promises."""
    box = (
        '<rect class="container" x="-65" y="-58" width="130" height="116" rx="6"/>'
    )
    little = (
        '<g transform="translate(27,15)">\n        '
        + "\n        ".join(solid(size=34))
        + "\n      </g>"
    )
    return [
        box,
        dot(-38, -33, 7),
        '<path class="line" d="M -50,34 Q -40,2 -14,-6"/>',
        dot(-50, 34, 6),
        dot(-14, -6, 6),
        little,
    ]


PRIMITIVES = [
    ("vertex", vertex),
    ("edge", edge),
    ("wire", wire),
    ("face", face),
    ("shell", shell),
    ("solid", solid),
    ("compound", compound),
]


def render():
    panels = [panel(i, fn()) for i, (_, fn) in enumerate(PRIMITIVES)]
    labels = [
        f'    <text x="{PANEL_PAD + PANEL_STEP * i + PANEL_STEP / 2:.1f}"'
        f' y="{LABEL_Y}">{name}</text>'
        for i, (name, _) in enumerate(PRIMITIVES)
    ]
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- The seven B-Rep topological primitives (Chapter 5). Generated by
     make_brep_primitives.py; edit that script rather than this file. -->
<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}"
     viewBox="0 0 {WIDTH} {HEIGHT}">
  <style type="text/css">
    <![CDATA[
      .face{{stroke:{EDGE};stroke-width:{STROKE_WIDTH}px;stroke-linejoin:round}}
      .line{{fill:none;stroke:{EDGE};stroke-width:{STROKE_WIDTH}px;
             stroke-linejoin:round;stroke-linecap:round}}
      .dot{{fill:{FILL};stroke:{EDGE};stroke-width:{STROKE_WIDTH}px}}
      .container{{fill:none;stroke:{EDGE};stroke-width:{STROKE_WIDTH}px;
                  stroke-dasharray:3 7;stroke-linecap:round}}
      text{{fill:{TEXT};font-family:'Linux Libertine O',Libertinus Serif,Georgia,serif;
            font-size:{FONT_SIZE}px;text-anchor:middle}}
    ]]>
  </style>
  <g id="primitives">
{chr(10).join(panels)}
  </g>
  <g id="labels">
{chr(10).join(labels)}
  </g>
</svg>
"""


if __name__ == "__main__":
    print(render(), end="")
