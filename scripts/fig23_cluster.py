#!/usr/bin/env python3
"""fig23_cluster.py -- what the 25 continuations of each cut answered, beside the blocks.

The block column is the one from Figure 1: the blocks of the trace, stacked and touching, each
box as tall as the block is long. A cut is a BOUNDARY between blocks, so twelve blocks give
thirteen cuts: the top edge of the first block (the empty prefix), then each junction, then the
foot of the last block. At every boundary a curly brace opens to the right onto that cut's box,
holding one bar per answer: how many of the 25 continuations ended there. The brace's tip sits on
the block's top line, and each box carries its own ticks, so a cluster is a self-contained
small multiple.

WHAT TO EDIT. Five blocks of settings at the top, all in points (1 point = 1/72 inch):

  BLOCK   the block column: width, total height, the floor, the M and alpha of the height rule,
          the fill, the stroke, the label and token sizes and colours
  BOX     a plot box: width, padding, tick spacing, fill, stroke, baseline and tick colours
  BAR     the bars: thickness, gap, the order down a cluster, one colour per answer, the letter
          printed at each bar's foot and its size
  BRACE   depth, gap from the block column, colour, weight
  PAGE    padding, the gutter where the letters go, the axis caption, the key, the font

Each has a "show" flag where it makes sense, so a part can be switched off without deleting it.
A block's height is proportional to M + alpha * Tk, with Tk its length in the model's own tokens:
M = 0 and alpha = 1 is the plain token scale, a larger M flattens the differences.

  python scripts/fig23_cluster.py                 -> figures/fig2_E_trace.{svg,pdf,png}
                                                     figures/fig3_C_trace.{svg,pdf,png}
  python scripts/fig23_cluster.py --dpi 300 --M 60 --alpha 0.7
  python scripts/fig23_cluster.py --height tokens

Reads figures/fig23_data.csv.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

# ============================================================================
# SETTINGS -- everything you are likely to want to change lives here, in points
# (1 point = 1/72 inch, so a width of 84 is about 1.17 in on paper).
# ============================================================================

# ---------------------------------------------------------------- the blocks
BLOCK = {
    "width": 65,                 # width of every block box
    "height_total": 470,         # the column's total height, before the floor below
    "height_min": 24,            # least a block may be; it must hold a whole cluster
    # A block's height is proportional to M + alpha * Tk, with Tk its length in tokens.
    # M = 0, alpha = 1 is the plain token scale; a large M flattens the differences.
    "M": 90,
    "alpha": 0.5,
    "height_equal": 36,          # the height used when --height equal
    "fill": "#f0f0ee",
    "stroke": "#000000",
    "stroke_w": 0.9,
    "label_size": 7.6,           # "Block 0"
    "label_colour": "#1a1a1a",
    "token_size": 6.0,           # the token count at the block's right
    "token_colour": "#313030",
    "token_dx": -6,
    "token_below": False,        # True puts the token count under the label, for a narrow column
    "show_tokens": True,
}

# ---------------------------------------------------------------- the plot boxes
BOX = {
    "width": 150,                # width of a box, from count 0 to count 25
    "pad": 2.6,                  # air above and below the cluster, inside its box
    "tick_step": 5,              # an interior rule at every multiple of this
    "fill": "#fbfbfa",
    "stroke": "#c4c4bf",
    "stroke_w": 0.6,
    "base": "#8c8c88",           # the left edge, which is count 0
    "base_w": 0.9,
    "tick": "#e4e4e0",
    "tick_w": 0.5,
    "show": True,
}

# ---------------------------------------------------------------- the bars
BAR = {
    "height": 5,              # thickness of one bar, the same in every cluster
    "gap": 0.5,                  # between two bars of a cluster
    "anchor": "centred",         # "centred": the cluster straddles the cut, so the brace's tip
                                 # lands on the block's top line; "top": it hangs below the line
    "colour": {                  # one per answer
        "C": "#4D8052",
        "E": "#615394",
        "no_answer": "#aa6182",
        "other": "#91764b",
    },
    # the order down a cluster; the trace's own answer is substituted for "target"
    "order": ["target", "alternative", "no_answer", "other"],
    "letter": {"C": "C", "E": "E", "no_answer": "?", "other": "\u2013"},
    "letter_size": 5.6,          # printed at the foot of each bar, in the bar's own colour
    "letter_dx": -3,             # left of the baseline
    "letter_dy": 1.4,            # against the bar's own centre line
    "show_letters": True,
}

# ---------------------------------------------------------------- the brace
BRACE = {
    "depth": 8,                 # from its tip to its arms
    "gap": 5,                    # between the block column and the tip
    "extend": 1.5,                 # how far the brace reaches above and below its cluster
    "colour": "#0F0F00",
    "stroke_w": 0.75,
    "show": True,
}

# ---------------------------------------------------------------- everything else
PAGE = {
    "pad_top": 40, "pad_left": 8, "pad_bottom": 34,
    "letter_gutter": 11,         # between the brace's arms and the boxes, where the letters go
    "tick_size": 6.8,            # the count labels above the chart
    "tick_gap": 6,
    "tick_dy": -11,
    "axis_size": 7.4,            # the caption above the chart
    "axis_dy": -23,
    "axis_text": "continuations of 25, by the answer they reached",
    "key_size": 7.2,
    "key_dy": 26,
    "key_gap": 14,
    "key_names": {"C": "answer C", "E": "answer E",
                  "no_answer": "no answer", "other": "other answer"},
    "font": "Georgia, 'Times New Roman', serif",
    "mid": "#5c5c5c", "pale": "#9a9a9a",
    "crop_pad": 6,               # white kept around the drawing
    "show_key": True,            # off when the two panels share one key (--pair does this)
    # --pair: both traces in ONE figure, side by side, under one key
    "pair_order": ["C-trace", "E-trace"],
    "pair_gap": 26,              # between the two panels
    "pair_labels": ["(a) the C-trace", "(b) the E-trace"],
    "pair_label_size": 8,
    "pair_label_dy": 16,         # the panel label, below the taller panel
    "pair_key_dy": 20,           # the shared key, below the panel labels
}

# Applied by --side-by-side: the figure is then drawn at the size it will be printed, so nothing
# is scaled down and the type stays the size set above. The key is dropped, because it is what
# makes the figure wide; put it once under both figures in the LaTeX float instead.
SIDE_BY_SIDE = {
    "BLOCK": {"width": 50, "height_total": 380, "token_below": True},
    "BOX": {"width": 98},
    "PAGE": {"show_key": False, "axis_text": "continuations of 25"},
}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Svg:
    def __init__(self):
        self.p = []
        self.bbox = [1e9, 1e9, -1e9, -1e9]

    def _see(self, x0, y0, x1, y1):
        b = self.bbox
        b[0], b[1] = min(b[0], x0), min(b[1], y0)
        b[2], b[3] = max(b[2], x1), max(b[3], y1)

    def rect(self, x, y, w, h, fill, stroke="none", sw=0.0, rx=0):
        if w <= 0 or h <= 0:
            return
        self._see(x, y, x + w, y + h)
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke != "none" else ""
        self.p.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" '
                      f'fill="{fill}"{st}/>')

    def line(self, x1, y1, x2, y2, stroke, sw=1.0, dash=None):
        self._see(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.p.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                      f'stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def path(self, d, stroke, sw=1.0):
        self.p.append(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}" '
                      f'stroke-linecap="round" stroke-linejoin="round"/>')

    def text(self, x, y, s, size, fill, anchor="middle", weight="normal", style=""):
        w = len(s) * size * 0.52
        x0 = x if anchor == "start" else (x - w / 2 if anchor == "middle" else x - w)
        self._see(x0, y - size, x0 + w, y + size * 0.3)
        self.p.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{PAGE["font"]}" '
                      f'font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
                      f'font-weight="{weight}" font-style="{style or "normal"}">{esc(s)}</text>')

    def render(self, pad=6.0):
        x0, y0 = self.bbox[0] - pad, self.bbox[1] - pad
        w = self.bbox[2] - self.bbox[0] + 2 * pad
        h = self.bbox[3] - self.bbox[1] + 2 * pad
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.2f}pt" height="{h:.2f}pt" '
                f'viewBox="{x0:.2f} {y0:.2f} {w:.2f} {h:.2f}">\n'
                f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{w:.2f}" height="{h:.2f}" fill="#ffffff"/>\n'
                + "\n".join(self.p) + "\n</svg>\n")


def brace_path(x_tip: float, x_arm: float, y0: float, y1: float) -> str:
    """A curly brace: tip at the left on the boundary, arms opening to the right."""
    mid = (y0 + y1) / 2
    spine = x_tip + (x_arm - x_tip) * 0.55
    q = min((mid - y0) * 0.55, (x_arm - x_tip) * 0.9)
    return (f"M {x_arm:.2f} {y0:.2f} "
            f"Q {spine:.2f} {y0:.2f} {spine:.2f} {y0 + q:.2f} "
            f"L {spine:.2f} {mid - q:.2f} "
            f"Q {spine:.2f} {mid:.2f} {x_tip:.2f} {mid:.2f} "
            f"Q {spine:.2f} {mid:.2f} {spine:.2f} {mid + q:.2f} "
            f"L {spine:.2f} {y1 - q:.2f} "
            f"Q {spine:.2f} {y1:.2f} {x_arm:.2f} {y1:.2f}")


def load(path: Path) -> dict:
    out: dict[str, list[dict]] = {}
    for r in csv.DictReader(open(path, encoding="utf-8")):
        out.setdefault(r["trace"], []).append(r)
    return out


def block_heights(blocks: list[dict], mode: str) -> list[float]:
    """A block's height: proportional to M + alpha * tokens, or all the same."""
    B = BLOCK
    if mode == "equal":
        return [max(B["height_equal"], B["height_min"])] * len(blocks)
    tok = [float(b["block_tokens"]) for b in blocks]
    raw = [B["M"] + B["alpha"] * x for x in tok] if mode == "affine" else tok
    scale = B["height_total"] / sum(raw)
    return [max(B["height_min"], v * scale) for v in raw]


def bands(letter: str) -> list[str]:
    """BAR["order"] with "target" and "alternative" resolved for this trace."""
    alt = "E" if letter == "C" else "C"
    return [letter if k == "target" else alt if k == "alternative" else k for k in BAR["order"]]


def build_panel(rows: list[dict], mode: str) -> tuple[Svg, float]:
    """One trace as an Svg, without the key. Returns it and the y of its foot."""
    P = PAGE
    letter = rows[0]["trace_answer"]
    order = bands(letter)
    n_max = int(rows[0]["n"])
    blocks = rows[1:]

    s = Svg()
    hs = block_heights(blocks, mode)
    x_block = P["pad_left"]
    x_tip = x_block + BLOCK["width"] + BRACE["gap"]
    x_arm = x_tip + BRACE["depth"]
    x_chart = x_arm + P["letter_gutter"]

    # the boundaries: the top of the first block, every junction, the foot of the last
    y = P["pad_top"]
    bounds = [y]
    for h in hs:
        y += h
        bounds.append(y)
    col_bottom = y

    def cx(count):
        return x_chart + BOX["width"] * count / n_max

    span = len(order) * BAR["height"] + (len(order) - 1) * BAR["gap"]
    half = span / 2 if BAR["anchor"] == "centred" else 0.0
    edge = BOX["pad"] + 2
    chart_top = min(P["pad_top"] - 3, bounds[0] - half - edge)
    chart_bottom = max(col_bottom, bounds[-1] - half + span + edge)

    y_tick = chart_top - P["tick_gap"]
    for c in range(0, n_max + 1, BOX["tick_step"]):
        s.text(cx(c), y_tick + P["tick_dy"] + 11, str(c), P["tick_size"], P["pale"])
    s.text(x_chart + BOX["width"] / 2, y_tick + P["axis_dy"] + 11, P["axis_text"],
           P["axis_size"], P["mid"])

    # the block column
    for i, b in enumerate(blocks):
        top, h = bounds[i], hs[i]
        s.rect(x_block, top, BLOCK["width"], h, BLOCK["fill"], BLOCK["stroke"], BLOCK["stroke_w"])
        stacked = BLOCK.get("token_below", False)
        dy = -2.0 if (stacked and BLOCK["show_tokens"]) else 2.5
        s.text(x_block + BLOCK["width"] / 2, top + h / 2 + dy, "Block " + str(int(b["cut"])),
               BLOCK["label_size"], BLOCK["label_colour"])
        if BLOCK["show_tokens"] and mode != "equal" and h > 16:
            if stacked:                      # under the label, for a narrow column
                s.text(x_block + BLOCK["width"] / 2, top + h / 2 + dy + BLOCK["token_size"] + 2.0,
                       b["block_tokens"], BLOCK["token_size"], BLOCK["token_colour"])
            else:                            # at the block's right edge
                s.text(x_block + BLOCK["width"] + BLOCK["token_dx"], top + h / 2 + 2.5,
                       b["block_tokens"], BLOCK["token_size"], BLOCK["token_colour"], anchor="end")

    # one cluster per cut: its brace, its box, its bars
    for j, r in enumerate(rows):
        y_top = bounds[j] - half
        if BRACE["show"]:
            s.path(brace_path(x_tip, x_arm, y_top - BRACE["extend"],
                              y_top + span + BRACE["extend"]), BRACE["colour"],
                   BRACE["stroke_w"])
        by0, by1 = y_top - BOX["pad"], y_top + span + BOX["pad"]
        if BOX["show"]:
            s.rect(cx(0), by0, cx(n_max) - cx(0), by1 - by0, BOX["fill"], BOX["stroke"],
                   BOX["stroke_w"])
            for c in range(BOX["tick_step"], n_max, BOX["tick_step"]):
                s.line(cx(c), by0, cx(c), by1, BOX["tick"], BOX["tick_w"])
        s.line(cx(0), by0, cx(0), by1, BOX["base"], BOX["base_w"])
        for k_i, k in enumerate(order):
            c = int(r["count_" + k])
            yy = y_top + k_i * (BAR["height"] + BAR["gap"])
            s.rect(cx(0), yy, cx(c) - cx(0), BAR["height"], BAR["colour"][k])
            if BAR["show_letters"]:
                s.text(x_chart + BAR["letter_dx"], yy + BAR["height"] / 2 + BAR["letter_dy"],
                       BAR["letter"][k], BAR["letter_size"], BAR["colour"][k],
                       anchor="end", weight="bold")

    return s, chart_bottom


def draw_key(s: Svg, order: list[str], x: float, y: float) -> float:
    """The key, laid out left to right from (x, y). Returns the x it ends at."""
    P = PAGE
    for k in order:
        name = P["key_names"][k]
        s.rect(x, y - 6, 9, 9, BAR["colour"][k])
        s.text(x + 12, y + 1.5, name, P["key_size"], P["mid"], anchor="start")
        x += 12 + len(name) * P["key_size"] * 0.52 + P["key_gap"]
    return x - P["key_gap"]


def key_width(order: list[str]) -> float:
    P = PAGE
    return sum(12 + len(P["key_names"][k]) * P["key_size"] * 0.52 + P["key_gap"]
               for k in order) - P["key_gap"]


def draw(rows: list[dict], mode: str) -> str:
    """One trace, on its own, with or without the key."""
    s, chart_bottom = build_panel(rows, mode)
    if PAGE["show_key"]:
        order = bands(rows[0]["trace_answer"])
        x_chart = (PAGE["pad_left"] + BLOCK["width"] + BRACE["gap"] + BRACE["depth"]
                   + PAGE["letter_gutter"])
        draw_key(s, order, x_chart, chart_bottom + PAGE["key_dy"])
    return s.render(PAGE["crop_pad"])


def draw_pair(traces: dict, mode: str) -> str:
    """Both traces in one figure, side by side, under a single key."""
    P = PAGE
    panels = []
    for name in P["pair_order"]:
        panel, _ = build_panel(traces[name], mode)
        panels.append(panel)

    out = Svg()
    dx = 0.0
    tops, bots = [], []
    for i, panel in enumerate(panels):
        x0, y0, x1, y1 = panel.bbox
        shift = dx - x0                      # left edges flush, tops already aligned
        out.p.append(f'<g transform="translate({shift:.2f} 0)">')
        out.p.extend(panel.p)
        out.p.append('</g>')
        out._see(x0 + shift, y0, x1 + shift, y1)
        tops.append(y0)
        bots.append(y1)
        dx = x1 + shift + P["pair_gap"]
        panels[i] = (panel, shift)

    foot = max(bots)
    for (panel, shift), label in zip(panels, P["pair_labels"]):
        x0, _, x1, _ = panel.bbox
        out.text((x0 + x1) / 2 + shift, foot + P["pair_label_dy"], label,
                 P["pair_label_size"], P["mid"])

    order = bands(traces[P["pair_order"][0]][0]["trace_answer"])
    full = out.bbox[0] + out.bbox[2]
    kx = (full - key_width(order)) / 2
    draw_key(out, order, kx, foot + P["pair_label_dy"] + P["pair_key_dy"])
    return out.render(P["crop_pad"])


def write(svg: str, stem: Path, dpi: int):
    """Write the SVG, then a PDF and a PNG beside it. Tries cairosvg, then Inkscape, then
    ImageMagick (PNG only)."""
    import shutil
    import subprocess
    stem.parent.mkdir(parents=True, exist_ok=True)
    svg_path, pdf_path, png_path = (stem.with_suffix(s) for s in (".svg", ".pdf", ".png"))
    svg_path.write_text(svg, encoding="utf-8")
    print(f"wrote {svg_path}")
    try:
        import cairosvg
        cairosvg.svg2pdf(url=str(svg_path), write_to=str(pdf_path))
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path),
                         scale=dpi / 72.0, background_color="white")
        print(f"wrote {pdf_path}\nwrote {png_path} at {dpi} dpi")
        return
    except Exception:
        pass
    exe = shutil.which("inkscape")
    if exe:
        subprocess.run([exe, str(svg_path), "--export-type=pdf",
                        f"--export-filename={pdf_path}"], check=True)
        subprocess.run([exe, str(svg_path), "--export-type=png", f"--export-dpi={dpi}",
                        "--export-background=white", f"--export-filename={png_path}"], check=True)
        print(f"wrote {pdf_path}\nwrote {png_path} at {dpi} dpi")
        return
    print("  no PDF: install cairosvg or put Inkscape on the PATH")
    exe = shutil.which("magick")
    if exe:
        subprocess.run([exe, "-density", str(dpi), "-background", "white",
                        str(svg_path), "-flatten", str(png_path)], check=True)
        print(f"wrote {png_path} at {dpi} dpi")
    else:
        print("  no PNG: install cairosvg, or put Inkscape or ImageMagick on the PATH")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Figures 2 and 3: the cuts, their answers, and the blocks.")
    ap.add_argument("--height", choices=("affine", "tokens"), default="affine",
                    help="row height proportional to M + alpha*tokens (default), or to tokens alone")
    ap.add_argument("--M", type=float, default=None)
    ap.add_argument("--alpha", type=float, default=None)
    ap.add_argument("--dpi", type=int, default=600)
    ap.add_argument("--data", default=None)
    ap.add_argument("--pair", action="store_true",
                    help="both traces in ONE figure, side by side, under a single key")
    ap.add_argument("--side-by-side", action="store_true",
                    help="size the figure for half a single-column text width, and drop the key")
    args = ap.parse_args(argv)
    if args.M is not None:
        BLOCK["M"] = args.M
    if args.alpha is not None:
        BLOCK["alpha"] = args.alpha
    if args.side_by_side:
        for name, over in SIDE_BY_SIDE.items():
            globals()[name].update(over)

    here = Path(__file__).resolve().parent
    root = next((p for p in [here] + list(here.parents) if (p / ".git").exists()), here.parent)
    traces = load(Path(args.data) if args.data else root / "figures" / "fig23_data.csv")
    tag = "" if args.height == "affine" else f"_{args.height}"
    if args.side_by_side:
        tag += "_sbs"
    if args.pair:
        PAGE["show_key"] = False             # the pair draws one key of its own
        write(draw_pair(traces, args.height),
              root / "figures" / f"fig23_answer_trajectory{tag}", args.dpi)
        return 0
    for fig, name in (("fig2", "E-trace"), ("fig3", "C-trace")):
        write(draw(traces[name], args.height),
              root / "figures" / f"{fig}_{name.replace('-', '_')}{tag}", args.dpi)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
