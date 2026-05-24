"""Regenerate publication-quality PNG figures for the OACCS position paper.

This script uses Pillow rather than Matplotlib so it works in the bundled
Codex document runtime.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PAPER_DIR = Path(__file__).resolve().parent
ROOT_DIR = PAPER_DIR.parent
FONT_DIR = Path("C:/Windows/Fonts")

NAVY = "#073763"
NAVY_2 = "#0B4A78"
INK = "#1F2937"
MUTED = "#667085"
GRID = "#D9DEE7"
PANEL = "#F6F8FB"
WHITE = "#FFFFFF"
BLUE = "#4E91C6"
LIGHT_BLUE = "#8EC2E6"
GREEN = "#146B3A"
GOLD = "#D6A63A"
ORANGE = "#C85F3D"
RED = "#9F1D2A"
PALE_RED = "#E9A1A5"

MODEL_LABELS = {
    "harness": "Harness\n(Multi-Agent)",
    "opus": "Opus\n(Single-Agent)",
    "sonnet_cli": "Sonnet\n(CLI)",
    "haiku_cli": "Haiku\n(CLI)",
    "gpt55_codex": "GPT-5.5\n(Codex)",
    "gpt54_codex": "GPT-5.4\n(Codex)",
    "gpt54mini_codex": "GPT-5.4-mini\n(Codex)",
}

MODEL_ORDER = [
    "harness",
    "opus",
    "sonnet_cli",
    "haiku_cli",
    "gpt55_codex",
    "gpt54_codex",
    "gpt54mini_codex",
]

TECH_LABELS = {
    "T1": "T1\nDecomposition",
    "T2": "T2\nPersona",
    "T3": "T3\nDAN Override",
    "T4": "T4\nInjection",
}
TECH_ORDER = ["T1", "T2", "T3", "T4"]


def font(size: int, bold: bool = False, italic: bool = False) -> ImageFont.FreeTypeFont:
    if bold:
        name = "segoeuib.ttf"
    elif italic:
        name = "segoeuii.ttf"
    else:
        name = "segoeui.ttf"
    path = FONT_DIR / name
    if path.exists():
        return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


F = {
    "title": font(62, bold=True),
    "subtitle": font(34, bold=True),
    "axis": font(34, bold=True),
    "axis_small": font(28, bold=True),
    "label": font(34),
    "label_bold": font(34, bold=True),
    "small": font(26),
    "small_bold": font(26, bold=True),
    "tiny": font(22),
    "value": font(44, bold=True),
    "value_big": font(72, bold=True),
    "italic": font(30, italic=True),
}


def rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def blend(a: str, b: str, t: float) -> str:
    ar, ag, ab = rgb(a)
    br, bg, bb = rgb(b)
    return "#{:02X}{:02X}{:02X}".format(
        round(ar + (br - ar) * t),
        round(ag + (bg - ag) * t),
        round(ab + (bb - ab) * t),
    )


def risk_color(rate: float) -> str:
    stops = [
        (0.00, GREEN),
        (0.35, "#7DBE55"),
        (0.55, "#F2CF4A"),
        (0.78, ORANGE),
        (1.00, RED),
    ]
    x = max(0, min(100, rate)) / 100
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        if x <= p1:
            return blend(c0, c1, (x - p0) / (p1 - p0))
    return RED


def value_text_color(rate: float) -> str:
    return WHITE if rate < 12 or rate >= 72 else INK


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.multiline_textbbox((0, 0), text, font=fnt, spacing=6, align="center")
    return box[2] - box[0], box[3] - box[1]


def draw_center(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    fnt: ImageFont.ImageFont,
    fill: str = INK,
    spacing: int = 6,
) -> None:
    w, h = text_size(draw, text, fnt)
    draw.multiline_text((xy[0] - w / 2, xy[1] - h / 2), text, font=fnt, fill=fill, spacing=spacing, align="center")


def draw_right(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    fnt: ImageFont.ImageFont,
    fill: str = INK,
    spacing: int = 6,
) -> None:
    w, h = text_size(draw, text, fnt)
    draw.multiline_text((xy[0] - w, xy[1] - h / 2), text, font=fnt, fill=fill, spacing=spacing, align="right")


def draw_rotated_text(
    image: Image.Image,
    center: tuple[int, int],
    text: str,
    fnt: ImageFont.ImageFont,
    fill: str = INK,
) -> None:
    scratch = Image.new("RGBA", (900, 160), (255, 255, 255, 0))
    d = ImageDraw.Draw(scratch)
    box = d.textbbox((0, 0), text, font=fnt)
    d.text(((900 - (box[2] - box[0])) / 2, (160 - (box[3] - box[1])) / 2), text, font=fnt, fill=fill)
    rotated = scratch.rotate(90, expand=True)
    image.alpha_composite(rotated, (center[0] - rotated.width // 2, center[1] - rotated.height // 2))


def rounded_box(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str, outline: str = "#CDD5DF", width: int = 2) -> None:
    draw.rounded_rectangle(box, radius=22, fill=fill, outline=outline, width=width)


def save(image: Image.Image, filename: str) -> None:
    out = PAPER_DIR / filename
    image.convert("RGB").save(out, "PNG", optimize=True)
    print(f"Saved {out}")


def safety_rates() -> dict[str, dict[str, float]]:
    return {
        "harness": {"T1": 80.6, "T2": 16.0, "T3": 0.5, "T4": 0.2},
        "opus": {"T1": 96.8, "T2": 27.9, "T3": 1.7, "T4": 0.9},
        "sonnet_cli": {"T1": 90.2, "T2": 71.8, "T3": 61.2, "T4": 47.4},
        "haiku_cli": {"T1": 75.4, "T2": 40.0, "T3": 42.1, "T4": 35.6},
        "gpt55_codex": {"T1": 27.6, "T2": 25.2, "T3": 20.4, "T4": 23.9},
        "gpt54_codex": {"T1": 93.8, "T2": 92.4, "T3": 95.6, "T4": 91.6},
        "gpt54mini_codex": {"T1": 95.7, "T2": 93.7, "T3": 97.4, "T4": 95.6},
    }


def fig1_safety_matrix() -> None:
    W, H = 3200, 2300
    image = Image.new("RGBA", (W, H), WHITE)
    draw = ImageDraw.Draw(image)

    draw_center(draw, (W / 2, 92), "Jailbreak Success Rate by Model-Interface and Technique", F["title"], NAVY)

    left, top = 400, 250
    cell_w, cell_h = 575, 235
    plot_w, plot_h = cell_w * 4, cell_h * 7

    for ci, tech in enumerate(TECH_ORDER):
        draw_center(draw, (left + ci * cell_w + cell_w / 2, top - 72), TECH_LABELS[tech], F["axis_small"], INK)

    rates = safety_rates()
    for ri, model in enumerate(MODEL_ORDER):
        y = top + ri * cell_h
        draw_right(draw, (left - 28, y + cell_h / 2), MODEL_LABELS[model], F["axis_small"], INK)
        for ci, tech in enumerate(TECH_ORDER):
            x = left + ci * cell_w
            rate = rates[model][tech]
            draw.rectangle((x, y, x + cell_w, y + cell_h), fill=risk_color(rate), outline=WHITE, width=7)
            draw_center(draw, (x + cell_w / 2, y + cell_h / 2), f"{rate:.1f}%", F["value"], value_text_color(rate))

    draw.rectangle((left, top, left + plot_w, top + plot_h), outline="#B8C2D0", width=6)

    cb_x, cb_y, cb_w, cb_h = left + plot_w + 120, top + 120, 70, plot_h - 240
    for i in range(cb_h):
        rate = 100 - (i / cb_h) * 100
        draw.line((cb_x, cb_y + i, cb_x + cb_w, cb_y + i), fill=risk_color(rate), width=1)
    draw.rectangle((cb_x, cb_y, cb_x + cb_w, cb_y + cb_h), outline="#CDD5DF", width=4)
    for rate in [100, 80, 60, 40, 20, 0]:
        y = cb_y + (100 - rate) / 100 * cb_h
        draw.line((cb_x + cb_w + 6, y, cb_x + cb_w + 22, y), fill=INK, width=3)
        draw.text((cb_x + cb_w + 34, y - 20), f"{rate}", font=F["small"], fill=INK)
    draw_rotated_text(image, (cb_x + cb_w + 155, cb_y + cb_h // 2), "Success Rate (%)", F["axis"], INK)

    note = "Green indicates lower jailbreak success; red indicates higher success. Values are model-plus-interface observations."
    draw.text((left, top + plot_h + 75), note, font=F["small"], fill=MUTED)

    save(image, "fig1_safety_matrix.png")


def fig2_technique_profiles() -> None:
    W, H = 3200, 1550
    image = Image.new("RGBA", (W, H), WHITE)
    draw = ImageDraw.Draw(image)
    draw_center(draw, (W / 2, 86), "Technique Profiles Are Model-Specific", F["title"], NAVY)

    left, top, right, bottom = 260, 235, 2920, 1160
    plot_w, plot_h = right - left, bottom - top
    x_positions = [left + i * plot_w / 3 for i in range(4)]

    for rate in range(0, 101, 20):
        y = bottom - rate / 100 * plot_h
        draw.line((left, y, right, y), fill=GRID, width=3)
        draw_right(draw, (left - 24, y), f"{rate}%", F["small"], INK)
    draw.line((left, top, left, bottom), fill=INK, width=5)
    draw.line((left, bottom, right, bottom), fill=INK, width=5)
    draw_rotated_text(image, (70, (top + bottom) // 2), "Jailbreak Success Rate", F["axis"], INK)

    for x, tech in zip(x_positions, TECH_ORDER):
        draw.line((x, bottom, x, bottom + 14), fill=INK, width=4)
        draw_center(draw, (x, bottom + 88), TECH_LABELS[tech], F["axis_small"], INK)

    colors = {
        "harness": "#334E68",
        "opus": NAVY,
        "sonnet_cli": "#1D73A6",
        "haiku_cli": "#4E9CC5",
        "gpt55_codex": "#C7443E",
        "gpt54_codex": "#D9777B",
        "gpt54mini_codex": PALE_RED,
    }
    rates = safety_rates()
    for model in MODEL_ORDER:
        pts = []
        for x, tech in zip(x_positions, TECH_ORDER):
            y = bottom - rates[model][tech] / 100 * plot_h
            pts.append((x, y))
        draw.line(pts, fill=colors[model], width=8, joint="curve")
        for x, y in pts:
            draw.ellipse((x - 16, y - 16, x + 16, y + 16), fill=colors[model], outline=WHITE, width=4)

    box = (1610, 300, 2460, 535)
    rounded_box(draw, box, PANEL, "#B8C2D0", 3)
    draw.text((1665, 340), "No single technique is\nuniversally effective or defeated.", font=F["small_bold"], fill=NAVY, spacing=8)
    draw.line((1588, 492, 1285, 670), fill=NAVY, width=5)
    draw.polygon([(1285, 670), (1328, 663), (1302, 630)], fill=NAVY)

    legend_y = 1335
    legend_xs = [320, 740, 1160, 1580, 2010, 2390, 2750]
    for x, model in zip(legend_xs, MODEL_ORDER):
        draw.line((x, legend_y, x + 75, legend_y), fill=colors[model], width=10)
        draw.ellipse((x + 30, legend_y - 15, x + 45, legend_y + 15), fill=colors[model])
        draw.text((x + 88, legend_y - 20), MODEL_LABELS[model].replace("\n", " "), font=F["tiny"], fill=INK)

    save(image, "fig1_technique_hierarchy.png")


def fig3_gpt55() -> None:
    W, H = 3200, 2050
    image = Image.new("RGBA", (W, H), WHITE)
    draw = ImageDraw.Draw(image)
    draw_center(draw, (W / 2, 82), "GPT-5.5: Interface Safety vs Model Alignment", F["title"], NAVY)

    panels = [(230, 270, 1470, 1400), (1730, 270, 2970, 1400)]
    titles = ["Codex Interface Refusal", "Model Compliance\nWhen Responding"]
    ylabels = ["Refusal Rate (%)", "Compliance Rate (%)"]
    data = [[42.8, 100.0], [99.6, 0.0]]
    bar_colors = [[BLUE, NAVY], [GREEN, "#E8EBEF"]]
    labels = ["Phase 1\nTrials 1-853", "Phase 2\nTrials 854-2,007"]

    for pi, (x0, y0, x1, y1) in enumerate(panels):
        draw_center(draw, ((x0 + x1) / 2, y0 - 95), titles[pi], F["subtitle"], NAVY)
        draw_rotated_text(image, (x0 - 120, (y0 + y1) // 2), ylabels[pi], F["axis"], INK)
        for rate in range(0, 101, 20):
            y = y1 - rate / 110 * (y1 - y0)
            draw.line((x0, y, x1, y), fill=GRID, width=3)
            draw_right(draw, (x0 - 20, y), f"{rate}", F["small"], INK)
        draw.line((x0, y0, x0, y1), fill=INK, width=5)
        draw.line((x0, y1, x1, y1), fill=INK, width=5)

        bar_w = 300
        xs = [x0 + (x1 - x0) * 0.30, x0 + (x1 - x0) * 0.70]
        for i, (x, rate) in enumerate(zip(xs, data[pi])):
            h = max(0, rate / 110 * (y1 - y0))
            top = y1 - h if rate > 0 else y1 - 55
            if pi == 1 and i == 1:
                draw.rectangle((x - bar_w / 2, top, x + bar_w / 2, y1), fill=bar_colors[pi][i], outline="#CDD5DF", width=4)
                for sx in range(int(x - bar_w / 2), int(x + bar_w / 2), 28):
                    draw.line((sx, y1, sx + 90, top), fill="#D4DAE3", width=4)
            else:
                draw.rectangle((x - bar_w / 2, top, x + bar_w / 2, y1), fill=bar_colors[pi][i], outline=WHITE, width=4)
            draw_center(draw, (x, y1 + 92), labels[i], F["label"], INK)

        if pi == 0:
            draw_center(draw, (xs[0], y1 - data[0][0] / 110 * (y1 - y0) - 62), "42.8%", F["value_big"], BLUE)
            draw_center(draw, (xs[1], y1 - data[0][1] / 110 * (y1 - y0) - 62), "100.0%", F["value_big"], NAVY)
            draw.line((xs[0] + 110, y1 - 430, xs[1] - 150, y0 + 355), fill=ORANGE, width=12)
            draw.polygon([(xs[1] - 150, y0 + 355), (xs[1] - 220, y0 + 370), (xs[1] - 180, y0 + 420)], fill=ORANGE)
            draw_center(draw, ((xs[0] + xs[1]) / 2 - 45, y0 + 610), "account-level\nmonitoring", F["italic"], ORANGE)
            draw_center(draw, (xs[0], y1 + 230), "N=853\n488 responses", F["small"], MUTED)
            draw_center(draw, (xs[1], y1 + 230), "N=1,154\n0 responses", F["small"], MUTED)
        else:
            draw_center(draw, (xs[0], y1 - data[1][0] / 110 * (y1 - y0) - 62), "99.6%", F["value_big"], GREEN)
            draw_center(draw, (xs[1], y1 - 145), "N/A", F["value"], "#8A94A6")
            draw_center(draw, (xs[1], y1 - 72), "100% refused\nby interface", F["small"], "#8A94A6")

    note = (610, 1780, 2590, 1940)
    rounded_box(draw, note, PANEL, NAVY, 4)
    draw_center(
        draw,
        ((note[0] + note[2]) / 2, (note[1] + note[3]) / 2),
        "Observed non-success is dominated by Codex zero-output behavior,\nnot by GPT-5.5 declining offensive content.",
        F["label"],
        NAVY,
    )

    save(image, "fig3_gpt55_temporal.png")


def fig4_severity() -> None:
    with open(ROOT_DIR / "analysis" / "severity_full_results.json", encoding="utf-8") as f:
        data = json.load(f)

    W, H = 3400, 2000
    image = Image.new("RGBA", (W, H), WHITE)
    draw = ImageDraw.Draw(image)
    draw_center(draw, (W / 2, 85), "Response Severity Distribution by Model-Interface Pair", F["title"], NAVY)

    models_order = ["claude-haiku", "claude-sonnet", "claude-opus", "gpt-5.5", "gpt-5.4", "gpt-5.4-mini"]
    labels = ["Haiku\n(CLI)", "Sonnet\n(CLI)", "Opus\n(Harness)", "GPT-5.5\n(Codex)", "GPT-5.4\n(Codex)", "GPT-5.4-mini\n(Codex)"]
    levels = ["L0", "L1", "L2", "L3", "L4"]
    level_labels = ["L0 Refusal", "L1 Educational", "L2 Procedural", "L3 Actionable", "L4 Exploit"]
    colors = [GREEN, "#5B9BD5", GOLD, ORANGE, RED]

    rows = []
    for model in models_order:
        sd = data["by_model"][model]["severity_distribution"]
        n = sd.get("n", 1)
        rows.append([sd.get(level, 0) / n * 100 for level in levels])

    left, top, right, bottom = 260, 240, 2580, 1550
    plot_h = bottom - top
    for rate in range(0, 101, 20):
        y = bottom - rate / 100 * plot_h
        draw.line((left, y, right, y), fill=GRID, width=3)
        draw_right(draw, (left - 22, y), f"{rate}", F["small"], INK)
    draw.line((left, top, left, bottom), fill=INK, width=5)
    draw.line((left, bottom, right, bottom), fill=INK, width=5)
    draw_rotated_text(image, (72, (top + bottom) // 2), "Percentage of Responses", F["axis"], INK)

    bar_w = 230
    xs = [
        left + 230 + i * ((right - 230) - (left + 230)) / (len(labels) - 1)
        for i in range(len(labels))
    ]
    for x, label, row in zip(xs, labels, rows):
        y_cursor = bottom
        for li, val in enumerate(row):
            h = val / 100 * plot_h
            y0 = y_cursor - h
            draw.rectangle((x - bar_w / 2, y0, x + bar_w / 2, y_cursor), fill=colors[li], outline=WHITE, width=4)
            if val >= 7:
                txt_color = WHITE if li in [0, 3, 4] else INK
                draw_center(draw, (x, y0 + h / 2), f"{val:.0f}%", F["small_bold"], txt_color)
            y_cursor = y0
        draw_center(draw, (x, bottom + 105), label, F["label"], INK)

    card_x0, card_y0, card_x1, card_y1 = 2670, 320, 3300, 1500
    rounded_box(draw, (card_x0, card_y0, card_x1, card_y1), PANEL, "#CDD5DF", 3)
    draw.text((card_x0 + 50, card_y0 + 55), 'Among Binary\n"Successes"', font=F["subtitle"], fill=NAVY, spacing=8)
    draw.text((card_x0 + 50, card_y0 + 305), "71%", font=F["value_big"], fill=NAVY)
    draw.text((card_x0 + 50, card_y0 + 425), "are L1-L2\neducational or\nprocedural", font=F["small"], fill=INK, spacing=8)
    draw.line((card_x0 + 50, card_y0 + 665, card_x1 - 50, card_y0 + 665), fill="#CDD5DF", width=3)
    draw.text((card_x0 + 50, card_y0 + 720), "17%", font=F["value_big"], fill=ORANGE)
    draw.text((card_x0 + 50, card_y0 + 840), "are L3-L4\nactionable or\nexploit-level", font=F["small"], fill=INK, spacing=8)
    draw.text(
        (card_x0 + 50, card_y1 - 175),
        "Binary compliance\nsubstantially overstates\noperational risk.",
        font=F["tiny"],
        fill=MUTED,
        spacing=7,
    )

    legend_y = 1810
    legend_x = 450
    gap = 500
    for i, (lab, col) in enumerate(zip(level_labels, colors)):
        x = legend_x + i * gap
        draw.rectangle((x, legend_y - 22, x + 70, legend_y + 22), fill=col)
        draw.text((x + 90, legend_y - 25), lab, font=F["small"], fill=INK)

    save(image, "fig2_severity_distribution.png")


def fig5_factorial() -> None:
    W, H = 2500, 1600
    image = Image.new("RGBA", (W, H), WHITE)
    draw = ImageDraw.Draw(image)
    draw_center(draw, (W / 2, 82), "2x2 Factorial: Batch Presentation Increases Compliance", F["title"], NAVY)

    values = [[73.3, 36.0], [76.8, 28.0]]
    ns = [[101, 100], [99, 100]]
    rows = ["Role Priming", "No Role Priming"]
    cols = ["Batch\nPresentation", "Sequential\nPresentation"]

    left, top = 310, 290
    cell_w, cell_h = 560, 370
    for ci, col in enumerate(cols):
        draw_center(draw, (left + ci * cell_w + cell_w / 2, top - 90), col, F["axis"], INK)
    for ri, row in enumerate(rows):
        draw_right(draw, (left - 40, top + ri * cell_h + cell_h / 2), row, F["axis"], INK)
        for ci in range(2):
            rate = values[ri][ci]
            x, y = left + ci * cell_w, top + ri * cell_h
            draw.rectangle((x, y, x + cell_w, y + cell_h), fill=risk_color(rate), outline=WHITE, width=8)
            draw_center(draw, (x + cell_w / 2, y + cell_h / 2 - 35), f"{rate:.1f}%", F["value_big"], value_text_color(rate))
            draw_center(draw, (x + cell_w / 2, y + cell_h / 2 + 70), f"N={ns[ri][ci]}", F["small_bold"], value_text_color(rate))
    draw.rectangle((left, top, left + cell_w * 2, top + cell_h * 2), outline="#B8C2D0", width=5)

    side_x = 1620
    rounded_box(draw, (side_x, 300, 2320, 1295), PANEL, "#CDD5DF", 3)
    draw.text((side_x + 55, 365), "Batch mean", font=F["small_bold"], fill=MUTED)
    draw.text((side_x + 55, 430), "75.0%", font=F["value_big"], fill=RED)
    draw.text((side_x + 55, 625), "Sequential mean", font=F["small_bold"], fill=MUTED)
    draw.text((side_x + 55, 690), "32.0%", font=F["value_big"], fill=GREEN)
    draw.line((side_x + 55, 905, side_x + 645, 905), fill="#CDD5DF", width=3)
    draw.text((side_x + 55, 965), "Odds ratio", font=F["small_bold"], fill=MUTED)
    draw.text((side_x + 55, 1030), "6.4x", font=F["value_big"], fill=NAVY)
    draw.text((side_x + 55, 1200), "N=400 valid Sonnet\nT1 decomposition trials", font=F["tiny"], fill=MUTED, spacing=7)

    cb_x, cb_y, cb_w, cb_h = 310, 1235, 1120, 36
    for i in range(cb_w):
        rate = i / cb_w * 100
        draw.line((cb_x + i, cb_y, cb_x + i, cb_y + cb_h), fill=risk_color(rate))
    draw.rectangle((cb_x, cb_y, cb_x + cb_w, cb_y + cb_h), outline="#CDD5DF", width=3)
    draw.text((cb_x, cb_y + 62), "Lower compliance", font=F["tiny"], fill=MUTED)
    draw.text((cb_x + cb_w - 195, cb_y + 62), "Higher compliance", font=F["tiny"], fill=MUTED)

    save(image, "fig4_factorial.png")


if __name__ == "__main__":
    fig1_safety_matrix()
    fig2_technique_profiles()
    fig3_gpt55()
    fig4_severity()
    fig5_factorial()
