"""Figure: convergence history of the sealed-can optimization from Chapter
12 ("Minimizing a Cell's Own Material") - the same objective and bounds
shown in the chapter's own code, tracked with a callback so the reader can
see the search actually settle rather than trusting the final number alone.
"""

import matplotlib.pyplot as plt
import numpy as np
from cadquery import Solid
from cadquery import func as cf
from matplotlib import font_manager
from scipy.optimize import differential_evolution

from _common import EDGE_COLOR, FILL_COLOR, GENERATED_DIR

for path in font_manager.findSystemFonts():
    if "LinLibertine_R." in path:
        font_manager.fontManager.addfont(path)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=path).get_name()
        break


def sealed_can(r_outer: float, wall: float, height: float) -> Solid:
    if not 0 < wall < r_outer or height <= 2 * wall:
        raise ValueError("invalid can parameters")
    outer = cf.cylinder(d=2 * r_outer, h=height)
    inner = cf.cylinder(d=2 * (r_outer - wall), h=height - 2 * wall).translate((0, 0, wall))
    can = outer - inner
    assert isinstance(can, Solid)
    return can


V_MIN = 15_000.0


def objective(x):
    r_outer, wall, height = x
    try:
        v_inner = np.pi * (r_outer - wall) ** 2 * (height - 2 * wall)
        penalty = max(0.0, V_MIN - v_inner) * 1.0
        return sealed_can(r_outer, wall, height).Volume() + penalty
    except Exception:
        return float("inf")


bounds = [(5, 25), (0.5, 5), (20, 120)]
history = []


def callback(xk, convergence=None):
    history.append(objective(xk))


differential_evolution(
    objective, bounds, seed=42, maxiter=300, tol=1e-6, polish=False, callback=callback, workers=1
)

fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(history, color=EDGE_COLOR, linewidth=1.5)
ax.set_xlabel("iteration")
ax.set_ylabel("material volume (mm$^3$)")
for spine in ax.spines.values():
    spine.set_visible(True)

fig.tight_layout()
out_path = GENERATED_DIR / "ch12-convergence.png"
fig.savefig(out_path, dpi=200)
print(f"wrote {out_path}")
