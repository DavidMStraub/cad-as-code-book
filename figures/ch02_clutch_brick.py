"""Figure: the clutch brick worked example from Chapter 2."""

from cadquery import func as cf

from _common import render


def clutch_brick(
    length: float,
    width: float,
    height: float,
    stud_diameter: float,
    stud_height: float,
    stud_spacing: float,
):
    body = cf.box(length, width, height)
    stud = cf.cylinder(d=stud_diameter, h=stud_height)

    left_stud = stud.translate((-stud_spacing / 2, 0, height))
    right_stud = stud.translate((stud_spacing / 2, 0, height))

    return body + left_stud + right_stud


brick = clutch_brick(
    length=15.6,
    width=7.8,
    height=9.6,
    stud_diameter=4.8,
    stud_height=1.7,
    stud_spacing=8.0,
)

render(brick, "ch02-clutch-brick")
