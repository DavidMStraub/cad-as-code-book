"""Figure: the tray from Chapter 4 ("Building the Tray: Feature Order in
Practice") - hole_then_round order, where the lead-in selector, asked
after the mounting hole exists, finds two circular rims and rounds the
hole's rim along with the pocket's. Uses the exact numbers from the
chapter's code block."""

from cadquery import func as cf

from _common import render

width, depth, thickness = 40, 30, 6
plate = cf.box(width, depth, thickness)
pocket = cf.cylinder(d=18.6, h=3).moved(z=thickness - 3)
hole = cf.cylinder(d=3.4, h=thickness).moved(x=16, y=11)

base = plate - pocket - hole
lead_in = base.faces(">Z").edges("%CIRCLE")
hole_then_round = base.fillet(1.0, lead_in.Edges())

render(hole_then_round, "ch04-tray-feature-order")
