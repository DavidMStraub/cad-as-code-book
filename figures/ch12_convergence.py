"""Figure: convergence history of the strut optimization from Chapter 12
("Design Variables, Objective, Constraints" / "Choosing an Algorithm") -
the same objective and bounds shown in the chapter's own code, tracked
with a callback so the reader can see the search actually settle rather
than trusting the final number alone.
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


def strut(r_outer: float, wall: float, length: float) -> Solid:
    if not 0 < wall < r_outer:
        raise ValueError("invalid strut parameters")
    outer = cf.cylinder(d=2 * r_outer, h=length)
    inner = cf.cylinder(d=2 * (r_outer - wall), h=length + 2).translate((0, 0, -1))
    tube = outer - inner
    assert isinstance(tube, Solid)
    return tube


E, SIGMA_ALLOW = 70e3, 150.0  # MPa, aluminum with margin below yield
P, LENGTH, K = 5000.0, 1200.0, 1.0  # N, mm, pinned-pinned


def section(r_outer: float, wall: float) -> tuple[float, float]:
    r_inner = r_outer - wall
    area = np.pi * (r_outer**2 - r_inner**2)
    moment = np.pi / 4 * (r_outer**4 - r_inner**4)
    return area, moment


def objective(x, rho: float = 20.0) -> float:
    r_outer, wall = x
    try:
        area, moment = section(r_outer, wall)
        p_crit = np.pi**2 * E * moment / (K * LENGTH) ** 2
        stress = P / area
        penalty = max(0.0, P - p_crit) * rho / 1000 + max(0.0, stress - SIGMA_ALLOW) * rho
        return strut(r_outer, wall, LENGTH).Volume() / LENGTH + penalty
    except Exception:
        return float("inf")


bounds = [(3, 40), (0.3, 5)]
history = []


def callback(xk, convergence=None):
    history.append(objective(xk))


differential_evolution(
    objective, bounds, seed=42, maxiter=1000, tol=1e-10, popsize=25, polish=False, callback=callback, workers=1
)

fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(history, color=EDGE_COLOR, linewidth=1.5)
ax.set_xlabel("iteration")
ax.set_ylabel("cross-section area (mm$^2$)")
for spine in ax.spines.values():
    spine.set_visible(True)

fig.tight_layout()
out_path = GENERATED_DIR / "ch12-convergence.png"
fig.savefig(out_path, dpi=200)
print(f"wrote {out_path}")
