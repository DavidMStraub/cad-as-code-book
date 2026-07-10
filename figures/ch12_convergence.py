"""Figure: convergence history of the buoy optimization from Chapter 12
("Design Variables, Objective, Constraints" / "Choosing an Algorithm") -
the same objective and bounds shown in the chapter's code, tracked with a
callback so the reader can see the search actually settle rather than
trusting the final number alone.
"""

import matplotlib.pyplot as plt
import numpy as np
from cadquery import Solid
from cadquery import func as cf
from matplotlib import font_manager
from scipy.optimize import brentq, differential_evolution

from _common import EDGE_COLOR, GENERATED_DIR

for path in font_manager.findSystemFonts():
    if "LinLibertine_R." in path:
        font_manager.fontManager.addfont(path)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=path).get_name()
        break

R_HULL, R_NECK, H_NECK = 60.0, 20.0, 80.0  # mm
RHO_WATER, RHO_STEEL = 1.0e-6, 7.85e-6  # kg/mm^3, fresh water and steel
SHELL_AREAL = 4.0e-6  # kg/mm^2, molded plastic shell
M_PAYLOAD = 3.0  # kg, electronics mounted 40 mm below the hatch
R_BALLAST, Z_BALLAST = 45.0, 25.0  # mm, steel disk resting in the dome
FREEBOARD_MIN, STABILITY_MIN = 60.0, 10.0  # mm


def hull(body: float) -> Solid:
    bottom = cf.sphere(2 * R_HULL).translate((0, 0, R_HULL))
    middle = cf.cylinder(d=2 * R_HULL, h=body).translate((0, 0, R_HULL))
    neck = cf.cone(d1=2 * R_HULL, d2=2 * R_NECK, h=H_NECK).translate((0, 0, R_HULL + body))
    shape = bottom + middle + neck
    assert isinstance(shape, Solid)
    return shape


def submerged(shape: Solid, draft: float):
    below = cf.box(6 * R_HULL, 6 * R_HULL, draft)
    return shape * below


def evaluate(body: float, t_ballast: float) -> tuple[float, float, float]:
    shape = hull(body)
    hatch = R_HULL + body
    m_shell = shape.Area() * SHELL_AREAL
    z_shell = sum(f.Area() * f.Center().z for f in shape.Faces()) / shape.Area()
    m_ballast = RHO_STEEL * np.pi * R_BALLAST**2 * t_ballast
    m_total = m_shell + m_ballast + M_PAYLOAD
    z_com = (
        m_shell * z_shell
        + m_ballast * (Z_BALLAST + t_ballast / 2)
        + M_PAYLOAD * (hatch - 40)
    ) / m_total

    def net_lift(draft: float) -> float:
        return RHO_WATER * submerged(shape, draft).Volume() - m_total

    if net_lift(hatch + H_NECK - 1) < 0:
        raise ValueError("heavier than any displacement it can generate: it sinks")
    draft = brentq(net_lift, 1.0, hatch + H_NECK - 1, xtol=0.01)
    z_cob = submerged(shape, draft).Center().z
    return m_total, hatch - draft, z_cob - z_com


def objective(x, rho: float = 1.0) -> float:
    body, t_ballast = x
    try:
        m_total, freeboard, stability = evaluate(body, t_ballast)
    except Exception:
        return float("inf")
    penalty = max(0.0, FREEBOARD_MIN - freeboard) * rho
    penalty += max(0.0, STABILITY_MIN - stability) * rho
    return m_total + penalty


bounds = [(150, 800), (1, 150)]
history = []


def callback(xk, convergence=None):
    history.append(objective(xk))


differential_evolution(
    objective, bounds, seed=42, maxiter=60, popsize=12, tol=1e-8, polish=False,
    callback=callback, workers=1,
)

fig, (ax_full, ax_zoom) = plt.subplots(1, 2, figsize=(7, 3.2))
for ax in (ax_full, ax_zoom):
    ax.plot(history, color=EDGE_COLOR, linewidth=1.5)
    ax.set_xlabel("iteration")
    ax.set_ylabel("total mass (kg)")
    for spine in ax.spines.values():
        spine.set_visible(True)
ax_zoom.set_ylim(8.40, 8.60)

fig.tight_layout()
out_path = GENERATED_DIR / "ch12-convergence.png"
fig.savefig(out_path, dpi=200)
print(f"wrote {out_path}")
