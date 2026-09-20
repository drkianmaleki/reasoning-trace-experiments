#!/usr/bin/env python3
"""fig1_instrument.py -- the instrument, in two panels, on one portrait letter page.

  Fig a.  The trace as a chain of blocks running down the page. At each block's foot the trace is
          cut and resampled; the 25 continuations reach the answers shown, with their shares on
          the lines. The dashed segment stands for the blocks not drawn, and the circle at the
          foot is the trace's own answer.
  Fig b.  One block opened out. One row per sentence; the three columns are that same span of
          text described at Level 1, Level 2 and Level 3, and the sentence itself is at the right.
          A Level 3 box is drawn only where the label has a third level.

Alignment is computed, not drawn. Each sentence's row is as tall as its wrapped text needs, and
the Level 1 and Level 2 boxes are the sums of the rows they cover, so the columns always line up
however the text is edited.

  python scripts/figures/fig1_instrument.py              -> figures/fig1_instrument.svg
  python scripts/figures/fig1_instrument.py --page       -> also *_page.svg with margin guides,
                                                            a caption and body text at 10 pt

Units are PostScript points: the page is 612 x 792 pt, so 10 pt here is 10 pt on paper.
LAYOUT holds every coordinate, FIG_A and FIG_B the content, HUES and STYLE the colours.
"""
from __future__ import annotations

import argparse
from pathlib import Path

PAGE = {"w": 612, "h": 792, "margin": 54}

# ============================================================================
# LAYOUT
# ============================================================================

LAYOUT = {
    "label_dy": -11,             # "Fig a." / "Fig b." above its panel

    "a": {
        "x": 112,                # centre of the spine blocks
        "y0": 124,               # centre of Block 0
        "dy": 74,                # spacing between spine blocks
        "w": 74, "h": 22,        # a spine block
        "branch_dy": 0.5,        # where the branch leaves the connector, 0..1 between blocks
        "cont_x": 220,           # centre of the resampled block
        "cont_w": 78, "cont_h": 20,
        "vertex_dx": 26,         # the fan's vertex, right of the resampled block
        "fan_x": 350,            # centre of the answer circles
        "circle_r": 10,
        "fan_dy": 25,            # vertical spacing of the answer circles
        "pct_dx": -7,            # the share, left of its circle
        "dash_len": 30,          # the dashed segment standing for the blocks not drawn
        "final_r": 13,
    },

    "b": {
        "x": 200, "y": 520, "w": 400,      # the block; its height is computed from the rows
        "pad_x": 10, "pad_y": 9,
        "text_right_pad": -20,     # keep the sentences clear of the panel edge
        "col_w": [70, 65, 25],   # Level 1, Level 2, Level 3 column widths
        "col_gap": 4,
        "text_gap": 11,          # gap between column 3 and the sentence column
        "row_gap": [2.4, 2.0, 2.0],
        "radius": [7, 6, 5],
        "row_pad": 5.0,          # air above and below a sentence's lines, inside its row
        "row_min": 15.0,         # least a row may be, so a one-word sentence still reads
        "line_h": 9.2,           # line spacing inside a sentence
        # A faint dashed rule on every sentence boundary inside the block. x0 and x1 are where
        # it starts and ends, measured from the block's LEFT edge; give a negative x1 to measure
        # from the right edge instead. dy shifts every rule up or down.
        "rule_x0": 6,            # start, from the block's left edge
        "rule_x1": -6,           # end; negative means "this far in from the right edge"
        "rule_dy": 0,            # shift every rule up (negative) or down (positive)
        "rule_ends": "both",     # "both", "first" (also above the first row), "last", "none"
    },
    "caption": {"x": 54, "y": 660, "line_h": 11.5},
}

STYLE = {
    "font": "Georgia, 'Times New Roman', serif",
    "fs_panel": 9,
    "fs_name": 7.6,              # Block 0, inside its box
    "fs_ans": 8.5,               # the answer letter in a circle
    "fs_pct": 7,
    "fs_l1": 7.4, "fs_l2": 6.8, "fs_l3": 6.2,
    "fs_text": 7.0,
    "ink": "#000000", "mid": "#000000", "pale": "#000000",
    "block_fill": "#f0f0ee", "block_stroke": "#6f6f6c", "block_sw": 1.0,
    "panel_fill": "#f4f4f2", "panel_stroke": "#8c8c88",
    "line": "#6f6f6c", "line_sw": 1.1,
    "dash": "3 3",
    "node_sw": 0.8,
    "rule_colour": "#c9c9c4",    # the dashed rules between sentences: one colour for all
    "rule_sw": 0.5,
    "rule_dash": "2 2.6",
    "show_rules": True,
    "text_fill": "#333330",
    "show_text": True,
}

# One hue per Level 1 label, as (Level 1, Level 2, Level 3) tints.
HUES = {
    "Planning":    ("#803f5c", "#913d60", "#eed3de"),
    "Reasoning":   ("#15131a", "#625192", "#dcd6ea"),
    "Knowledge":   ("#214f58", "#3a7481", "#d2e3e7"),
    "Example":     ("#6b4e20", "#88662b", "#eddfc4"),
    "Conclusion":  ("#305534", "#2e7937", "#d5e6d7"),
    "Restatement": ("#5c432b", "#644a28", "#e6dbcb"),
    "Assumption":  ("#643d21", "#7c5131", "#ebdccf"),
    "Reflection":  ("#4a6e96", "#26415e", "#d5dfea"),
}
NEUTRAL = ("#8c8c88", "#c3c3bf", "#e4e4e0")

# Answer colours in Fig a.
ANSWER_HUES = {"C": "#6a55a0", "E": "#b0567f", "?": "#8c8c88"}

# ============================================================================
# CONTENT
# ============================================================================

FIG_A = {
    "label": "a)",
    "spine": ["Block 0", "Block 1", "Block 2"],
    # the fan at the foot of each block: (answer, share). Real figures, C-trace, strict reading.
    "fans": [
        [("C", "48%"), ("E", "4%"), ("?", "48%")],
        [("C", "28%"), ("E", "32%"), ("?", "40%")],
        None,                     # Block 2 leads into the blocks not drawn
    ],
    "final": "C",
}

# Fig b: one row per sentence, with its three label levels. A blank l3 draws no Level 3 box.
# This is the real block at sentences 288-301 of the E-trace.
FIG_B = {
    "label": "b)",
    "rows": [
        ("Planning",   "Initiate ver.",    "Wait",   "Wait, hold on."),
        ("Reasoning",  "Logical reasoning", "",      "Is there a linguistic interpretation where \u201cThe bat costs more than the ball\u201d implies a specific relationship?"),
        ("Reasoning",  "Logical reasoning", "",      "No."),
        ("Reasoning",  "Speculation",      "Intent", "Is it possible the user made a typo and wants me to correct it and answer (A)?"),
        ("Knowledge",  "Self-knowledge",   "Role",   "If I am an AI assistant, being helpful usually means spotting the typo."),
        ("Knowledge",  "Self-knowledge",   "Role",   "But being accurate means following the prompt."),
        ("Reasoning",  "Speculation",      "Intent", "The prompt includes options that specifically cater to the typo/omission (Option C)."),
        ("Reasoning",  "Speculation",      "Intent", "If the user just wanted the answer to the riddle, they would provide options like:"),
        ("Example",    "Rhetorical ex.",   "",       "(A) 0.05 (B) 0.10 (C) 1.05."),
        ("Reasoning",  "Speculation",      "Intent", "The presence of meta-options (C, D, E) indicates a logic test, not a riddle check."),
        ("Reasoning",  "Speculation",      "Intent", "In a logic test, literal interpretation is king."),
        ("Reasoning",  "Logical reasoning", "",      "Literal interpretation = Underdetermined."),
        ("Reasoning",  "Option eval.",     "(C)",    "Option (C) = Underdetermined + Context guess."),
        ("Conclusion", "Intermediate",     "",       "Therefore, (C) is the intended answer for this specific multiple choice setup."),
    ],
}

CAPTION = [   # not drawn: copy this into the LaTeX \caption{}
    "Figure 1: The instrument. (a) A trace is a chain of blocks. Cutting it at a block's foot and resampling gives 25",
    "continuations, which reach the answers shown with the given shares; the dashed segment stands for the blocks not",
    "drawn, and the circle at the foot is the trace's own answer. (b) One block: one row per sentence, described at",
    "Level 1, Level 2 and Level 3, with the sentence itself at the right. A Level 3 box appears only where the label",
    "has a third level; colour marks the Level 1 kind.",
]
BODY = [
    "sample body text at 10 pt, for scale — a node is a run of consecutive sentences carrying the same",
    "Level 1 label, and a block opens where the model announces a new phase, opens a case, or says \"Wait\".",
]


# ============================================================================
# ------------------------------ DRAWING -------------------------------------
# ============================================================================

CHAR_W = 0.475      # estimated width of a character as a fraction of the font size


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Svg:
    def __init__(self, w, h):
        self.p = ['<rect id="bg" width="100%" height="100%" fill="#ffffff"/>']
        self.w, self.h = w, h
        self.bbox = [1e9, 1e9, -1e9, -1e9]      # x0, y0, x1, y1 of everything drawn

    def _see(self, x0, y0, x1, y1):
        b = self.bbox
        b[0], b[1] = min(b[0], x0), min(b[1], y0)
        b[2], b[3] = max(b[2], x1), max(b[3], y1)

    def rect(self, x, y, w, h, fill, stroke, sw=1.0, rx=2.5, dash=None):
        self._see(x - sw, y - sw, x + w + sw, y + h + sw)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.p.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" '
                      f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def circle(self, cx, cy, r, fill, stroke, sw=1.0):
        self._see(cx - r - sw, cy - r - sw, cx + r + sw, cy + r + sw)
        self.p.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}" '
                      f'stroke="{stroke}" stroke-width="{sw}"/>')

    def line(self, x1, y1, x2, y2, stroke, sw=1.0, dash=None, marker=False):
        self._see(min(x1, x2) - sw, min(y1, y2) - sw, max(x1, x2) + sw, max(y1, y2) + sw)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = ' marker-end="url(#a)"' if marker else ""
        self.p.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                      f'stroke="{stroke}" stroke-width="{sw}"{d}{m} stroke-linecap="round"/>')

    def text(self, x, y, s, size, fill, anchor="middle", style="", weight="normal", halo=False,
             see=True):
        """see=False for text that sits inside a drawn shape, so its estimated width cannot
        push the crop box past that shape."""
        if see:
            w = len(s) * size * CHAR_W
            x0 = x if anchor == "start" else (x - w / 2 if anchor == "middle" else x - w)
            self._see(x0, y - size, x0 + w, y + size * 0.3)

        def one(fill_, extra):
            self.p.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{STYLE["font"]}" '
                          f'font-size="{size:.2f}" fill="{fill_}" text-anchor="{anchor}" '
                          f'font-style="{style or "normal"}" font-weight="{weight}"{extra}>'
                          f'{esc(s)}</text>')
        if halo:
            one("#ffffff", ' stroke="#ffffff" stroke-width="2.2" stroke-linejoin="round"')
        one(fill, "")

    def render(self, crop_pad=None):
        """crop_pad: points of white kept around the drawing; None keeps the whole page."""
        x0, y0, w, h = 0.0, 0.0, float(self.w), float(self.h)
        body = self.p
        if crop_pad is not None and self.bbox[2] > self.bbox[0]:
            x0 = self.bbox[0] - crop_pad
            y0 = self.bbox[1] - crop_pad
            w = (self.bbox[2] - self.bbox[0]) + 2 * crop_pad
            h = (self.bbox[3] - self.bbox[1]) + 2 * crop_pad
            body = [p for p in self.p if not p.startswith('<rect id="bg"')]
            body = [f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{w:.2f}" height="{h:.2f}" '
                    f'fill="#ffffff"/>'] + body
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.2f}pt" height="{h:.2f}pt" '
                f'viewBox="{x0:.2f} {y0:.2f} {w:.2f} {h:.2f}">\n<defs>'
                f'<marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" '
                f'orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="{STYLE["line"]}"/>'
                f'</marker></defs>\n' + "\n".join(body) + "\n</svg>\n")


def wrap(text: str, width: float, size: float) -> list[str]:
    per = size * CHAR_W
    out, line = [], ""
    for w in text.split():
        trial = (line + " " + w).strip()
        if len(trial) * per > width and line:
            out.append(line)
            line = w
        else:
            line = trial
    if line:
        out.append(line)
    return out or [""]


def shrink(s: str, width: float, size: float) -> float:
    while size > 4.4 and len(s) * size * CHAR_W > width:
        size -= 0.2
    return size


def runs(rows: list, key) -> list[tuple[int, int]]:
    """Consecutive rows sharing key(row), as (start, count)."""
    out, i = [], 0
    while i < len(rows):
        j = i
        while j + 1 < len(rows) and key(rows[j + 1]) == key(rows[i]):
            j += 1
        out.append((i, j - i + 1))
        i = j + 1
    return out


# ---------------------------------------------------------------- Fig a

def draw_fig_a(s: Svg):
    L = LAYOUT["a"]
    s.text(L["x"] - L["w"] / 2, L["y0"] - L["h"] / 2 + LAYOUT["label_dy"], FIG_A["label"],
           STYLE["fs_panel"], STYLE["mid"], anchor="start", style="italic")
    ys = [L["y0"] + i * L["dy"] for i in range(len(FIG_A["spine"]))]
    for i, (name, y) in enumerate(zip(FIG_A["spine"], ys)):
        s.rect(L["x"] - L["w"] / 2, y - L["h"] / 2, L["w"], L["h"],
               STYLE["block_fill"], STYLE["block_stroke"], STYLE["block_sw"], rx=3)
        s.text(L["x"], y + 2.8, name, STYLE["fs_name"], STYLE["ink"])
        if i < len(ys) - 1:
            s.line(L["x"], y + L["h"] / 2, L["x"], ys[i + 1] - L["h"] / 2 - 3,
                   STYLE["line"], STYLE["line_sw"], marker=True)
        fan = FIG_A["fans"][i]
        if not fan:
            continue
        # the branch leaves the connector at the block's foot and runs right
        by = y + L["h"] / 2 + (ys[i + 1] - ys[i] - L["h"]) * L["branch_dy"] if i < len(ys) - 1 \
            else y + L["h"] / 2 + 20
        s.line(L["x"], by, L["cont_x"] - L["cont_w"] / 2 - 3, by, STYLE["line"],
               STYLE["line_sw"], marker=True)
        s.rect(L["cont_x"] - L["cont_w"] / 2, by - L["cont_h"] / 2, L["cont_w"], L["cont_h"],
               "#ffffff", STYLE["block_stroke"], STYLE["block_sw"], rx=3)
        vx = L["cont_x"] + L["cont_w"] / 2 + L["vertex_dx"]
        s.line(L["cont_x"] + L["cont_w"] / 2 + 2, by, vx, by, STYLE["line"], 0.9, dash="3 2.5")
        for j, (ans, pct) in enumerate(fan):
            fy = by + (j - (len(fan) - 1) / 2) * L["fan_dy"]
            hue = ANSWER_HUES.get(ans, NEUTRAL[0])
            s.line(vx, by, L["fan_x"] - L["circle_r"] - 2, fy, hue, 0.9)
            s.text(L["fan_x"] - L["circle_r"] + L["pct_dx"], fy - 2.5, pct, STYLE["fs_pct"],
                   STYLE["mid"], anchor="end", halo=True)
            s.circle(L["fan_x"], fy, L["circle_r"], HUES.get(ans, (None, None, "#eeeeea"))[2]
                     if ans in HUES else _tint(hue), hue, 1.2)
            s.text(L["fan_x"], fy + 3, ans, STYLE["fs_ans"], hue, weight="bold")

    y = ys[-1] + L["h"] / 2
    s.line(L["x"], y + 3, L["x"], y + L["dash_len"], STYLE["line"], STYLE["line_sw"],
           dash=STYLE["dash"], marker=True)
    fy = y + L["dash_len"] + L["final_r"] + 6
    hue = ANSWER_HUES.get(FIG_A["final"], NEUTRAL[0])
    s.circle(L["x"], fy, L["final_r"], _tint(hue), hue, 1.5)
    s.text(L["x"], fy + 3.6, FIG_A["final"], STYLE["fs_ans"] + 1, hue, weight="bold")


def _tint(hex_colour: str) -> str:
    """A pale wash of a hue, for a circle's fill."""
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))
    f = 0.85
    return "#%02x%02x%02x" % tuple(int(c + (255 - c) * f) for c in (r, g, b))


# ---------------------------------------------------------------- Fig b

def fig_b_rows() -> list[dict]:
    """Each sentence's wrapped lines and row height."""
    L = LAYOUT["b"]
    text_w = (L["w"] - 2 * L["pad_x"] - sum(L["col_w"]) - 2 * L["col_gap"] - L["text_gap"]
             - L["text_right_pad"])
    out = []
    for l1, l2, l3, sent in FIG_B["rows"]:
        lines = wrap(sent, text_w, STYLE["fs_text"])
        h = max(L["row_min"], len(lines) * L["line_h"] + L["row_pad"])
        out.append({"l1": l1, "l2": l2, "l3": l3, "lines": lines, "h": h})
    return out


def draw_fig_b(s: Svg):
    L = LAYOUT["b"]
    rows = fig_b_rows()
    inner_h = sum(r["h"] for r in rows)
    h = inner_h + 2 * L["pad_y"]
    x0 = L["x"] - L["w"] / 2
    y0 = L["y"] - h / 2
    s.text(x0, y0 + LAYOUT["label_dy"], FIG_B["label"], STYLE["fs_panel"], STYLE["mid"],
           anchor="start", style="italic")
    s.rect(x0, y0, L["w"], h, STYLE["panel_fill"], STYLE["panel_stroke"], STYLE["block_sw"] + 0.3, rx=4)

    xs, x = [], x0 + L["pad_x"]
    for w in L["col_w"]:
        xs.append((x, w))
        x += w + L["col_gap"]
    text_x = x + L["text_gap"]

    tops, y = [], y0 + L["pad_y"]
    for r in rows:
        tops.append(y)
        y += r["h"]
    bottom = y

    # the sentence boundaries, drawn first so everything else sits on top of them
    if STYLE["show_rules"]:
        rx0 = x0 + L["rule_x0"]
        rx1 = x0 + L["rule_x1"] if L["rule_x1"] >= 0 else x0 + L["w"] + L["rule_x1"]
        edges = list(tops[1:])
        if L["rule_ends"] in ("both", "first"):
            edges.insert(0, tops[0])
        if L["rule_ends"] in ("both", "last"):
            edges.append(bottom)
        for ey in edges:
            s.line(rx0, ey + L["rule_dy"], rx1, ey + L["rule_dy"],
                   STYLE["rule_colour"], STYLE["rule_sw"], dash=STYLE["rule_dash"])

    def band(i, n):
        return tops[i], sum(rows[k]["h"] for k in range(i, i + n))

    # Level 1: runs of the same label
    for i, n in runs(rows, lambda r: r["l1"]):
        top, hh = band(i, n)
        hue = HUES.get(rows[i]["l1"], NEUTRAL)
        cx, cw = xs[0]
        s.rect(cx, top + L["row_gap"][0] / 2, cw, hh - L["row_gap"][0], hue[1], hue[0],
               STYLE["node_sw"], rx=L["radius"][0])
        s.text(cx + cw / 2, top + hh / 2 + 2.6, rows[i]["l1"],
               shrink(rows[i]["l1"], cw - 8, STYLE["fs_l1"]), "#ffffff", weight="bold")

    # Level 2: runs of the same (Level 1, Level 2) pair
    for i, n in runs(rows, lambda r: (r["l1"], r["l2"])):
        top, hh = band(i, n)
        hue = HUES.get(rows[i]["l1"], NEUTRAL)
        cx, cw = xs[1]
        s.rect(cx, top + L["row_gap"][1] / 2, cw, hh - L["row_gap"][1], hue[2], hue[0],
               STYLE["node_sw"], rx=L["radius"][1])
        s.text(cx + cw / 2, top + hh / 2 + 2.3, rows[i]["l2"],
               shrink(rows[i]["l2"], cw - 8, STYLE["fs_l2"]), hue[0])

    # Level 3: one box per sentence that has a third level
    for i, r in enumerate(rows):
        if not r["l3"]:
            continue
        hue = HUES.get(r["l1"], NEUTRAL)
        cx, cw = xs[2]
        s.rect(cx, tops[i] + L["row_gap"][2] / 2, cw, r["h"] - L["row_gap"][2], "#ffffff", hue[0],
               STYLE["node_sw"], rx=L["radius"][2])
        s.text(cx + cw / 2, tops[i] + r["h"] / 2 + 2.1, r["l3"],
               shrink(r["l3"], cw - 6, STYLE["fs_l3"]), hue[0])

    # the sentences
    if STYLE["show_text"]:
        for i, r in enumerate(rows):
            ty = tops[i] + (r["h"] - (len(r["lines"]) - 1) * L["line_h"]) / 2 + 2.4
            for ln in r["lines"]:
                s.text(text_x, ty, ln, STYLE["fs_text"], STYLE["text_fill"], anchor="start",
                       see=False)
                ty += L["line_h"]
    return y0 + h


def build(proof: bool, crop_pad: float | None) -> str:
    """proof=True adds the page margin guide and a 10 pt line, for judging the sizes only.
    The figure itself never carries a caption: that belongs in the LaTeX float."""
    s = Svg(PAGE["w"], PAGE["h"])
    if proof:
        m = PAGE["margin"]
        s.rect(m, m, PAGE["w"] - 2 * m, PAGE["h"] - 2 * m, "none", "#e6e6e6", 0.7, rx=0, dash="3 4")
    draw_fig_a(s)
    bottom = draw_fig_b(s)
    if proof:
        y = bottom + 26
        for i, line in enumerate(BODY):
            s.text(PAGE["margin"], y + i * 13, line, 10, STYLE["ink"], anchor="start")
    return s.render(None if proof else crop_pad)


# ---------------------------------------------------------------- output

def repo_root(start: Path) -> Path:
    """The repository root, whether this script sits in scripts/ or scripts/figures/."""
    for d in [start] + list(start.parents):
        if (d / ".git").exists():                      # the usual case
            return d
    for d in [start] + list(start.parents):
        if (d / "scripts").is_dir():                   # a copy without .git
            return d
    return start.parent


def write_png(svg_path: Path, png_path: Path, dpi: int, pts: tuple[float, float] | None) -> bool:
    """Rasterise at `dpi`. Tries cairosvg, then Inkscape, rsvg-convert, ImageMagick."""
    try:
        import cairosvg
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path),
                         scale=dpi / 72.0, background_color="white")
        return True
    except Exception:
        pass
    import shutil
    import subprocess
    exe = shutil.which("inkscape")
    if exe:
        subprocess.run([exe, str(svg_path), "--export-type=png", f"--export-dpi={dpi}",
                        f"--export-filename={png_path}"], check=True)
        return True
    exe = shutil.which("rsvg-convert")
    if exe:
        subprocess.run([exe, "-d", str(dpi), "-p", str(dpi), "-b", "white",
                        "-o", str(png_path), str(svg_path)], check=True)
        return True
    exe = shutil.which("magick") or shutil.which("convert")
    if exe:
        subprocess.run([exe, "-density", str(dpi), "-background", "white",
                        str(svg_path), "-flatten", str(png_path)], check=True)
        return True
    print("  no rasteriser found. For a PNG install one of:\n"
          "    pip install cairosvg      (also needs the Cairo library on Windows)\n"
          "    Inkscape, rsvg-convert, or ImageMagick on the PATH\n"
          "  the SVG and the PDF are written either way.")
    return False


def write_pdf(svg_path: Path, pdf_path: Path) -> bool:
    try:
        import cairosvg
        cairosvg.svg2pdf(url=str(svg_path), write_to=str(pdf_path))
        return True
    except Exception:
        pass
    import shutil
    import subprocess
    exe = shutil.which("inkscape")
    if exe:
        subprocess.run([exe, str(svg_path), "--export-type=pdf",
                        f"--export-filename={pdf_path}"], check=True)
        return True
    print("  no PDF: install cairosvg or put Inkscape on the PATH (open a new terminal after)")
    return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Figure 1: the instrument. Writes an SVG, a PNG and a PDF into figures/.")
    ap.add_argument("--out", default=None,
                    help="output SVG; default <repo>/figures/fig1_instrument.svg")
    ap.add_argument("--dpi", type=int, default=600, help="PNG resolution (default 600)")
    ap.add_argument("--pad", type=float, default=6.0,
                    help="points of white kept around the drawing (default 6)")
    ap.add_argument("--no-png", action="store_true")
    ap.add_argument("--no-pdf", action="store_true")
    ap.add_argument("--proof", action="store_true",
                    help="also write *_proof.svg: the figure on a letter page with the margin "
                         "guide and a 10 pt line, to judge the sizes")
    args = ap.parse_args(argv)

    here = Path(__file__).resolve().parent
    out = Path(args.out) if args.out else repo_root(here) / "figures" / "fig1_instrument.svg"
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    out.write_text(build(False, args.pad), encoding="utf-8")
    print(f"wrote {out}")
    if not args.no_pdf and write_pdf(out, out.with_suffix(".pdf")):
        print(f"wrote {out.with_suffix('.pdf')}")
    if not args.no_png and write_png(out, out.with_suffix(".png"), args.dpi, None):
        print(f"wrote {out.with_suffix('.png')} at {args.dpi} dpi")
    if args.proof:
        p2 = out.with_name(out.stem + "_proof.svg")
        p2.write_text(build(True, None), encoding="utf-8")
        print(f"wrote {p2}")
        if not args.no_png:
            write_png(p2, p2.with_suffix(".png"), min(args.dpi, 200), None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
