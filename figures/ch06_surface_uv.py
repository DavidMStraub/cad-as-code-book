"""Figure: a curved surface with its u- and v-isolines - the smooth loft
from Chapter 6's Surfaces section (circles of radius 10, 16, 10), whose
single BSPLINE face is curved in both parameter directions. Each isoline
is sampled from Face.positionAt(u, v) at a frozen parameter, lifted
0.12 mm along the local surface normal (drawn exactly in the surface,
the lines z-fight with the face tessellation and look broken), and
rebuilt as a spline edge. The u/v direction arrows and labels are drawn
in image space with PIL after rendering - dark, on the white margin
beside and below the surface, in the book's body font - because VTK's
in-scene labels were barely readable against the shaded face (and
screenshot(scale=2) drops 2D text actors outright)."""

import numpy as np
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont
from cadquery import func as cf

from _common import EDGE_COLOR, FILL_COLOR, GENERATED_DIR, render

LIGHT_EDGE = "#f0f4f8"
LIFT = 0.12  # mm along the local normal, against z-fighting

sections = [
    cf.wire(cf.circle(10.0)),
    cf.wire(cf.circle(16.0)).moved(z=25),
    cf.wire(cf.circle(10.0)).moved(z=50),
]
surface = cf.loft(sections, ruled=False)
face = surface.Faces()[0]
u0, u1, v0, v1 = face.uvBounds()  # this face: [0, 1] x [0, 1]


def lifted(u, v):
    p = face.positionAt(u, v)
    n = face.normalAt(p)
    return (p + n.multiply(LIFT)).toTuple()


isolines = []
for u in np.linspace(u0, u1, 13)[:-1]:  # u1 wraps back onto u0
    isolines.append(cf.spline([lifted(u, v) for v in np.linspace(v0, v1, 40)]))
for v in np.linspace(v0, v1, 7):
    isolines.append(cf.spline([lifted(u, v) for u in np.linspace(u0, u1, 80)]))

render(
    [surface, *isolines],
    "ch06-surface-uv",
    colors=[FILL_COLOR] + [LIGHT_EDGE] * len(isolines),
    edge_color=LIGHT_EDGE,
    elevation_offset=-10,
)

# --- image-space annotation: u along the bottom, v up the left side ---

out_path = GENERATED_DIR / "ch06-surface-uv.png"
im = Image.open(out_path).convert("RGB")
w, h = im.size

MARGIN_LEFT, MARGIN_BOTTOM = int(0.16 * w), int(0.14 * h)
canvas = Image.new("RGB", (w + MARGIN_LEFT, h + MARGIN_BOTTOM), "white")
canvas.paste(im, (MARGIN_LEFT, 0))
draw = ImageDraw.Draw(canvas)

font_path = None
for path in font_manager.findSystemFonts():
    if "LinLibertine_RI" in path:  # Linux Libertine italic, the body font
        font_path = path
        break
font = ImageFont.truetype(font_path or font_manager.findfont("serif"), int(0.075 * h))

LINE = max(6, int(0.006 * h))
color = EDGE_COLOR


def arrow(p, q):
    p, q = np.array(p, float), np.array(q, float)
    draw.line([tuple(p), tuple(q)], fill=color, width=LINE)
    d = (q - p) / np.linalg.norm(q - p)
    n = np.array([-d[1], d[0]])
    head = 4.5 * LINE
    draw.polygon(
        [tuple(q + d * head), tuple(q - n * head * 0.6), tuple(q + n * head * 0.6)],
        fill=color,
    )


# v: upward along the left margin
x = int(MARGIN_LEFT * 0.45)
arrow((x, int(0.62 * h)), (x, int(0.40 * h)))
draw.text((x - 2.2 * LINE, int(0.27 * h)), "v", font=font, fill=color, anchor="ma")

# u: rightward along the bottom margin
y = h + int(MARGIN_BOTTOM * 0.35)
arrow((int(MARGIN_LEFT + 0.32 * w), y), (int(MARGIN_LEFT + 0.55 * w), y))
draw.text((int(MARGIN_LEFT + 0.62 * w), y), "u", font=font, fill=color, anchor="lm")

canvas.save(out_path)
print(f"annotated {out_path}")
