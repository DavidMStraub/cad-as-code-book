"""Figure: the plate-with-hole solid from Chapter 2 ("A First Solid")."""

from cadquery import func as cf

from _common import render

plate = cf.box(80, 50, 10)
hole = cf.cylinder(d=20, h=10)
part = plate - hole

render(part, "ch02-plate-with-hole")
