"""Shared rendering style for book figures.

Not part of the book itself -- tooling used to regenerate figures/generated/*.png
from the same CadQuery code shown in the chapters. Change the constants below
and re-run `python3 figures/generate_all.py` to restyle every figure at once.
"""

from pathlib import Path

import numpy as np
import pyvista as pv
import pyvista_cad as pc
from PIL import Image

FILL_COLOR = "#a2cbf0"
EDGE_COLOR = "#2c5a8a"
LINE_WIDTH = 8.0
BACKGROUND = "white"
WINDOW_SIZE = (1400, 1000)
SCALE = 2
CROP_PADDING = 40  # pixels of margin kept around the shape, at SCALE resolution

GENERATED_DIR = Path(__file__).parent / "generated"


def _crop_to_content(path: Path, padding: int = CROP_PADDING) -> None:
    """Crop a screenshot to its non-background content plus a fixed margin,
    so every figure carries the same relative whitespace regardless of the
    rendered shape's own proportions or how tightly the camera happened to
    fit it."""

    im = Image.open(path)
    gray = np.array(im.convert("L"))
    mask = gray < 250
    ys, xs = np.where(mask)
    left = max(int(xs.min()) - padding, 0)
    right = min(int(xs.max()) + padding, im.width)
    top = max(int(ys.min()) - padding, 0)
    bottom = min(int(ys.max()) + padding, im.height)
    im.crop((left, top, right, bottom)).save(path)


def render(shapes, name, *, azimuth_offset=20, colors=None):
    """Render one or more CadQuery Shapes to figures/generated/<name>.png."""

    if not isinstance(shapes, (list, tuple)):
        shapes = [shapes]
    if colors is None:
        colors = [FILL_COLOR] * len(shapes)

    pv.OFF_SCREEN = True
    plotter = pv.Plotter(off_screen=True, window_size=WINDOW_SIZE)
    plotter.background_color = BACKGROUND

    for shape, color in zip(shapes, colors):
        pc.add_cad(
            plotter,
            shape.wrapped,
            color=color,
            edges=True,
            edge_color=EDGE_COLOR,
            line_width=LINE_WIDTH,
            smooth=True,
            opacity=1.0,
        )

    plotter.camera_position = "iso"
    plotter.camera.azimuth += azimuth_offset
    plotter.enable_parallel_projection()
    plotter.reset_camera()

    GENERATED_DIR.mkdir(exist_ok=True)
    out_path = GENERATED_DIR / f"{name}.png"
    plotter.screenshot(str(out_path), scale=SCALE)
    _crop_to_content(out_path)
    print(f"wrote {out_path}")
