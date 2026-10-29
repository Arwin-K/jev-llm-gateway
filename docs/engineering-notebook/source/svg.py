"""Tiny SVG drawing helper used by figures.py. Keeps every diagram on one visual system."""

from html import escape
from pathlib import Path

FONT = "Avenir Next, Helvetica Neue, Helvetica, Arial, sans-serif"
MONO = "Menlo, SF Mono, monospace"

INK = "#2f2a25"
MUTED = "#6f665c"
LINE = "#5a4e44"
ACCENT = "#a8512a"

KINDS = {
    #          fill       stroke     dash     text
    "mac":    ("#f4ecdf", "#8a6a48", None,   INK),
    "ext":    ("#e7edf2", "#55697d", "5 3",  INK),
    "colab":  ("#e6efe5", "#5c7a5c", "5 3",  INK),
    "jev":    ("#f6e2d4", ACCENT,    None,   INK),
    "plain":  ("#ffffff", "#b3a491", None,   INK),
    "muted":  ("#f7f4ef", "#b9ae9f", "4 3",  MUTED),
    "ok":     ("#e4eee2", "#5c7a5c", None,   INK),
    "warn":   ("#f8ecd2", "#b08532", None,   INK),
    "bad":    ("#f5dfd8", "#a24b36", None,   INK),
    "dark":   ("#3b342e", "#3b342e", None,   "#fbf8f2"),
    "lock":   ("#efe9f1", "#6d5a7a", "5 3",  INK),
}


class Svg:
    def __init__(self, width, height):
        self.w, self.h = width, height
        self.parts = []

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, size=12.5, anchor="start", weight=400, color=INK,
             italic=False, mono=False, lh=1.25):
        lines = s if isinstance(s, (list, tuple)) else [s]
        style = ' font-style="italic"' if italic else ""
        fam = MONO if mono else FONT
        out = [f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" '
               f'text-anchor="{anchor}" font-weight="{weight}" fill="{color}"{style}>']
        for i, line in enumerate(lines):
            dy = 0 if i == 0 else size * lh
            out.append(f'<tspan x="{x}" dy="{dy:.1f}">{escape(line) or "&#160;"}</tspan>')
        out.append("</text>")
        self.add("".join(out))

    def rect(self, x, y, w, h, kind="plain", rx=7, sw=1.3, fill=None, stroke=None, dash="kind"):
        f, s, d, _ = KINDS[kind]
        f = fill or f
        s = stroke or s
        d = d if dash == "kind" else dash
        da = f' stroke-dasharray="{d}"' if d else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{f}" '
                 f'stroke="{s}" stroke-width="{sw}"{da}/>')

    def box(self, x, y, w, h, lines, kind="plain", size=12.5, sub_size=None, align="middle",
            mono_sub=False, rx=7, sw=1.3, title_weight=600):
        """Box with a bold title line and optional smaller subtitle lines, vertically centered."""
        self.rect(x, y, w, h, kind, rx=rx, sw=sw)
        lines = lines if isinstance(lines, (list, tuple)) else [lines]
        sub_size = sub_size or size - 1.8
        color = KINDS[kind][3]
        heights = [size] + [sub_size * 1.22] * (len(lines) - 1)
        total = size + sum(heights[1:])
        cy = y + (h - total) / 2 + size * 0.82
        tx = x + w / 2 if align == "middle" else x + 10
        anchor = "middle" if align == "middle" else "start"
        self.text(tx, cy, lines[0], size, anchor, title_weight, color)
        yy = cy
        for line in lines[1:]:
            yy += sub_size * 1.22
            sub_color = color if kind == "dark" else MUTED
            self.text(tx, yy, line, sub_size, anchor, 400, sub_color, mono=mono_sub)

    def frame(self, x, y, w, h, title, kind="mac", size=11.5):
        f, s, d, _ = KINDS[kind]
        da = f' stroke-dasharray="{d}"' if d else ' stroke-dasharray="6 4"'
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{f}" '
                 f'fill-opacity="0.35" stroke="{s}" stroke-width="1.2"{da}/>')
        self.text(x + 12, y + 18, title.upper(), size - 1.5, "start", 600, s)

    def line(self, pts, color=LINE, sw=1.4, dash=None, arrow=True, start_arrow=False):
        d = "M" + " L".join(f"{px},{py}" for px, py in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        me = f' marker-end="url(#ah-{self._mid(color)})"' if arrow else ""
        ms = f' marker-start="url(#ah-{self._mid(color)})"' if start_arrow else ""
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{da}{me}{ms}/>')

    def arrow(self, x1, y1, x2, y2, **kw):
        self.line([(x1, y1), (x2, y2)], **kw)

    def label(self, x, y, s, size=10.5, anchor="middle", color=MUTED, bg=True, italic=False, weight=400):
        if bg:
            lines = s if isinstance(s, (list, tuple)) else [s]
            wmax = max(len(t) for t in lines) * size * 0.56 + 8
            hh = size * 1.25 * len(lines) + 3
            bx = x - wmax / 2 if anchor == "middle" else (x - 4 if anchor == "start" else x - wmax + 4)
            self.add(f'<rect x="{bx:.1f}" y="{y - size * 1.0:.1f}" width="{wmax:.1f}" height="{hh:.1f}" '
                     f'rx="3" fill="#fffdf9" fill-opacity="0.92"/>')
        self.text(x, y, s, size, anchor, weight, color, italic=italic)

    def circle(self, cx, cy, r, fill, stroke=None, sw=1.2):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{st}/>')

    def badge(self, cx, cy, n, color=ACCENT, r=10, size=11):
        self.circle(cx, cy, r, color)
        self.text(cx, cy + size * 0.36, str(n), size, "middle", 700, "#ffffff")

    def note(self, x, y, s, size=10.5, anchor="start", color=MUTED, italic=True):
        self.text(x, y, s, size, anchor, 400, color, italic=italic)

    _colors = {}

    def _mid(self, color):
        return color.strip("#")

    def save(self, path):
        colors = {LINE, ACCENT, MUTED, "#55697d", "#5c7a5c", "#a24b36", "#b08532", "#8a6a48", "#6d5a7a"}
        markers = "".join(
            f'<marker id="ah-{c.strip("#")}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto-start-reverse"><path d="M0,1 L10,5 L0,9 z" fill="{c}"/></marker>'
            for c in colors)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
               f'width="{self.w}" height="{self.h}"><defs>{markers}</defs>' + "".join(self.parts) + "</svg>\n")
        Path(path).write_text(svg)
