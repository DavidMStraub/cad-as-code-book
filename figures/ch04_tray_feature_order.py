"""Figure: the tray from Chapter 4 ("Building the Tray: Feature Order in
Practice") - fillet_then_boss order, where a locating boss placed at the
corner's original coordinates overhangs the corner's new, rounded
boundary. Uses the exact numbers from the chapter's code block."""

from cadquery import func as cf

from _common import render

width, depth, thickness = 40, 30, 6
locating_boss = cf.cylinder(d=8, h=3).translate((16, 11, thickness))

plate = cf.box(width, depth, thickness)
corners = plate.edges("|Z")

fillet_then_boss = plate.fillet(8, corners) + locating_boss

render(fillet_then_boss, "ch04-tray-feature-order")
