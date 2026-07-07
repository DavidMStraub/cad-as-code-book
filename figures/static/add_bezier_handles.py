#!/usr/bin/env python3
"""Add Inkscape-style node/handle visualization to a single-path SVG.

Parses the first <path> element's `d` attribute (and, if present, its
sodipodi:nodetypes) and appends the control-handle lines, handle knobs and
path nodes that Inkscape's node tool draws on screen, as real SVG elements
layered on top of the original path.

Usage:
    python add_bezier_handles.py bezier.svg bezier-handles.svg
"""

import re
import sys
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"
SODIPODI_NS = "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"

ET.register_namespace("", SVG_NS)
ET.register_namespace("inkscape", INKSCAPE_NS)
ET.register_namespace("sodipodi", SODIPODI_NS)

# Visual constants, tuned to look like Inkscape's node tool at typical
# zoom, scaled to this document's coordinate units (~mm). Colors chosen
# to match the book's blueish figure palette (see curvature.svg).
HANDLE_LINE_COLOR = "#5B9BD5"
HANDLE_LINE_WIDTH = 0.04
HANDLE_KNOB_COLOR = "#5B9BD5"
HANDLE_KNOB_RADIUS = 0.13
NODE_CUSP_COLOR = "#2C3E50"
NODE_SMOOTH_COLOR = "#2C3E50"
NODE_SIZE = 0.28  # side length of the square (smooth) node marker
NODE_DIAMOND_SIZE = 0.36  # tip-to-tip size of the diamond (cusp) node marker


TOKEN_RE = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|-?\d*\.?\d+(?:e-?\d+)?")


def tokenize(d):
    return TOKEN_RE.findall(d)


def parse_path(d):
    """Return (points, node_kinds) where points is a list of absolute
    (x, y) anchor points in path order, and segments is a list of
    (c1, c2, end) tuples (all absolute) for each cubic bezier segment,
    in order. Only M/m, C/c, L/l and Z/z are supported, which is enough
    for Inkscape-exported single-letter glyph paths."""
    tokens = tokenize(d)
    i = 0
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    anchors = [None]  # placeholder, filled below; anchors[0] is the moveto point
    segments = []  # list of (c1, c2, end)
    cmd = None

    def read_floats(n):
        nonlocal i
        vals = tokens[i:i + n]
        i += n
        return [float(v) for v in vals]

    anchors = []
    while i < len(tokens):
        tok = tokens[i]
        if tok.isalpha():
            cmd = tok
            i += 1
        # else: repeated implicit command, reuse previous cmd

        if cmd in ("M", "m"):
            x, y = read_floats(2)
            if cmd == "m" and anchors:
                x, y = cur[0] + x, cur[1] + y
            elif cmd == "m":
                x, y = cur[0] + x, cur[1] + y
            cur = (x, y)
            start = cur
            anchors.append(cur)
            cmd = "L" if cmd == "M" else "l"  # subsequent coord pairs are implicit lineto
        elif cmd in ("L", "l"):
            x, y = read_floats(2)
            if cmd == "l":
                x, y = cur[0] + x, cur[1] + y
            cur = (x, y)
            anchors.append(cur)
            segments.append((cur, cur, cur))  # degenerate handles for a line
        elif cmd in ("C", "c"):
            x1, y1, x2, y2, x, y = read_floats(6)
            if cmd == "c":
                x1, y1 = cur[0] + x1, cur[1] + y1
                x2, y2 = cur[0] + x2, cur[1] + y2
                x, y = cur[0] + x, cur[1] + y
            c1, c2, end = (x1, y1), (x2, y2), (x, y)
            segments.append((c1, c2, end))
            cur = end
            anchors.append(cur)
        elif cmd in ("Z", "z"):
            if cur != start:
                segments.append((cur, start, start))
                anchors.append(start)
            cur = start
            i += 1 if tokens[i - 1] in ("Z", "z") else 0
        else:
            raise ValueError(f"Unsupported path command: {cmd!r}")

    return anchors, segments


def make_el(tag, **attrs):
    el = ET.Element(f"{{{SVG_NS}}}{tag}")
    for k, v in attrs.items():
        el.set(k.replace("_", "-"), str(v))
    return el


def diamond_points(cx, cy, size):
    h = size / 2
    return f"{cx},{cy - h} {cx + h},{cy} {cx},{cy + h} {cx - h},{cy}"


def square_points(cx, cy, size):
    h = size / 2
    return (cx - h, cy - h, size, size)


def build_overlay(anchors, segments, nodetypes, group):
    """Append handle-line / handle-knob / node markers to `group`."""
    # For a closed path the final anchor coincides with the first one
    # (same node) -- drop the duplicate so node markers aren't drawn twice.
    node_anchors = anchors
    if len(anchors) > 1 and anchors[-1] == anchors[0]:
        node_anchors = anchors[:-1]

    n = len(node_anchors)
    nodetypes = (nodetypes or "").ljust(n, "c")

    # Handle lines + knobs (skip degenerate line-to segments where
    # control points coincide with the anchors).
    for start_anchor, (c1, c2, end) in zip(anchors, segments):
        if c1 != start_anchor:
            group.append(make_el(
                "path", d=f"M {start_anchor[0]},{start_anchor[1]} L {c1[0]},{c1[1]}",
                style=f"stroke:{HANDLE_LINE_COLOR};stroke-width:{HANDLE_LINE_WIDTH};"
                      f"fill:none",
            ))
            group.append(make_el(
                "circle", cx=c1[0], cy=c1[1], r=HANDLE_KNOB_RADIUS,
                style=f"fill:{HANDLE_KNOB_COLOR};stroke:none",
            ))
        if c2 != end:
            group.append(make_el(
                "path", d=f"M {end[0]},{end[1]} L {c2[0]},{c2[1]}",
                style=f"stroke:{HANDLE_LINE_COLOR};stroke-width:{HANDLE_LINE_WIDTH};"
                      f"fill:none",
            ))
            group.append(make_el(
                "circle", cx=c2[0], cy=c2[1], r=HANDLE_KNOB_RADIUS,
                style=f"fill:{HANDLE_KNOB_COLOR};stroke:none",
            ))

    # Path nodes (anchors), drawn last so they sit on top of handle lines.
    for idx, (x, y) in enumerate(node_anchors):
        kind = nodetypes[idx] if idx < len(nodetypes) else "c"
        if kind == "c":  # cusp -> diamond
            group.append(make_el(
                "polygon", points=diamond_points(x, y, NODE_DIAMOND_SIZE),
                style=f"fill:#ffffff;stroke:{NODE_CUSP_COLOR};stroke-width:0.05",
            ))
        else:  # smooth / symmetric -> square
            x0, y0, w, h = square_points(x, y, NODE_SIZE)
            group.append(make_el(
                "rect", x=x0, y=y0, width=w, height=h,
                style=f"fill:#ffffff;stroke:{NODE_SMOOTH_COLOR};stroke-width:0.05",
            ))


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} input.svg output.svg", file=sys.stderr)
        sys.exit(1)

    in_path, out_path = sys.argv[1], sys.argv[2]

    tree = ET.parse(in_path)
    root = tree.getroot()

    path_el = root.find(f".//{{{SVG_NS}}}path")
    if path_el is None:
        raise SystemExit("No <path> element found in the input SVG.")

    d = path_el.get("d")
    nodetypes = path_el.get(f"{{{SODIPODI_NS}}}nodetypes")

    anchors, segments = parse_path(d)

    layer = path_el.getparent() if hasattr(path_el, "getparent") else None
    # ElementTree has no getparent(); find it manually.
    if layer is None:
        for parent in root.iter():
            if path_el in list(parent):
                layer = parent
                break

    overlay = make_el("g", id="bezier-handles", **{
        f"{{{INKSCAPE_NS}}}label": "Bezier handles",
    })
    build_overlay(anchors, segments, nodetypes, overlay)
    layer.append(overlay)

    tree.write(out_path, xml_declaration=True, encoding="UTF-8")
    print(f"Wrote {out_path} ({len(anchors)} nodes, {len(segments)} segments)")


if __name__ == "__main__":
    main()
