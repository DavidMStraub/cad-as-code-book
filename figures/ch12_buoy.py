"""Figure: the optimized buoy from Chapter 12, split at its computed
waterline - the part of the hull below the waterline rendered in a deeper
blue than the part above it. Hull dimensions and draft are the verified
optimum of the chapter's own search (body=764.2 mm, draft=764.2 mm,
freeboard exactly 60 mm); rerunning the search to regenerate a static
render would cost a minute for no change, so the numbers are pinned here.
"""

from cadquery import func as cf

from _common import FILL_COLOR, render

R_HULL, R_NECK, H_NECK = 60.0, 20.0, 80.0  # mm
BODY = 764.2  # mm, optimized
DRAFT = 764.2  # mm, equilibrium at the optimum

SUBMERGED_COLOR = "#5e93c5"

bottom = cf.sphere(2 * R_HULL).translate((0, 0, R_HULL))
middle = cf.cylinder(d=2 * R_HULL, h=BODY).translate((0, 0, R_HULL))
neck = cf.cone(d1=2 * R_HULL, d2=2 * R_NECK, h=H_NECK).translate((0, 0, R_HULL + BODY))
hull = bottom + middle + neck

below_box = cf.box(6 * R_HULL, 6 * R_HULL, DRAFT)
below = hull * below_box
above = hull - below_box

# Laid over toward the viewer like any other iso view: upright, the 7.5:1
# hull renders as a page-filling column.
TILT = 60  # degrees from vertical, about the y-axis
above = above.rotate((0, 0, 0), (0, 1, 0), TILT)
below = below.rotate((0, 0, 0), (0, 1, 0), TILT)

render(
    [above, below],
    "ch12-buoy",
    colors=[FILL_COLOR, SUBMERGED_COLOR],
    elevation_offset=-10,
)
