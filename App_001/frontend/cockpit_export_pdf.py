import math
import os
from datetime import datetime
from io import BytesIO

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

import fiscal
from cockpit_export import (
    AVAILABILITY_COLORS,
    BAR_PURPLES,
    TECH_PALETTE,
    _aggregate,
    _fmt_m,
)

PAGE_W, PAGE_H = landscape(A4)
MARGIN = 40

INK = HexColor("#1E1B4B")
MUTED = HexColor("#6B7280")
LAVENDER = HexColor("#F5F2FB")
BORDER = HexColor("#ECE6FA")
PURPLE = HexColor("#7C3AED")
UP = HexColor("#16A34A")
DOWN = HexColor("#DC2626")

FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "mira_logo_dark.png")


def _s(value):
    """Testo compatibile con i font standard del PDF (Latin-1/WinAnsi)."""
    return str(value).encode("cp1252", "replace").decode("cp1252")


def _fit(text, font, size, max_width):
    text = _s(text)
    if stringWidth(text, font, size) <= max_width:
        return text
    while text and stringWidth(text + "...", font, size) > max_width:
        text = text[:-1]
    return text.rstrip() + "..."


def _wrap(text, font, size, max_width, max_lines=2):
    """Spezza il testo su piu' righe (massimo `max_lines`); l'ultima riga viene troncata."""
    words, lines, current = _s(text).split(), [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if stringWidth(trial, font, size) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines - 1] + [" ".join(lines[max_lines - 1:])]
    return [_fit(line, font, size, max_width) for line in lines]


def _text(c, x, y, text, size=12, bold=False, color=INK, align="left", max_width=None):
    font = FONT_BOLD if bold else FONT
    text = _fit(text, font, size, max_width) if max_width else _s(text)
    c.setFont(font, size)
    c.setFillColor(color)
    if align == "right":
        c.drawRightString(x, y, text)
    elif align == "center":
        c.drawCentredString(x, y, text)
    else:
        c.drawString(x, y, text)


def _background(c):
    c.setFillColor(LAVENDER)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)


def _base_page(c, title, subtitle, page, date_label):
    _background(c)
    _text(c, MARGIN, PAGE_H - 55, title, size=26, bold=True, max_width=PAGE_W - 2 * MARGIN)
    if subtitle:
        _text(c, MARGIN, PAGE_H - 78, subtitle, size=11, color=MUTED, max_width=PAGE_W - 2 * MARGIN)
    _text(c, MARGIN, 24, f"MIRA · D&A Advisory Cockpit · {date_label}", size=8, color=MUTED)
    _text(c, PAGE_W - MARGIN, 24, str(page), size=8, color=MUTED, align="right")


def _card(c, x, y_top, w, h):
    c.setFillColor(white)
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.8)
    c.roundRect(x, y_top - h, w, h, 10, stroke=1, fill=1)


def _chart_card(c, x, y_top, w, h, title):
    _card(c, x, y_top, w, h)
    _text(c, x + 16, y_top - 26, title, size=10.5, bold=True, max_width=w - 32)


def _empty(c, x, y_top, w, h, message="No data for the selected filters"):
    _text(c, x + w / 2, y_top - h / 2, message, size=11, color=MUTED, align="center")


def _hbar(c, x, y_top, w, h, items, value_fmt, colors=None):
    """Barre orizzontali; `items` dall'alto verso il basso."""
    if not items:
        return
    label_w = min(150, w * 0.38)
    value_w = 62
    bar_x = x + label_w + 8
    bar_max = max(w - label_w - value_w - 16, 20)
    peak = max(v for _, v in items) or 1
    slot = h / len(items)
    bar_h = min(slot * 0.58, 24)
    for index, (label, value) in enumerate(items):
        center = y_top - slot * index - slot / 2
        lines = _wrap(label, FONT, 9, label_w, 2)
        top_line = center + (len(lines) - 1) * 5.5 - 3.5
        for n, line in enumerate(lines):
            _text(c, x + label_w, top_line - n * 11, line, size=9, align="right")
        color = HexColor("#" + (colors[index] if colors else "7C3AED"))
        length = max(bar_max * value / peak, 1.5)
        c.setFillColor(color)
        c.roundRect(bar_x, center - bar_h / 2, length, bar_h, 3, stroke=0, fill=1)
        _text(c, bar_x + length + 6, center - 3.5, value_fmt(value), size=9, bold=True)


def _vbar(c, x, y_top, w, h, items, value_fmt, colors=None):
    """Barre verticali; `items` da sinistra a destra."""
    if not items:
        return
    label_h, value_h = 34, 16
    base_y = y_top - h + label_h
    chart_h = h - label_h - value_h
    peak = max(v for _, v in items) or 1
    slot = w / len(items)
    bar_w = min(slot * 0.58, 46)
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.6)
    c.line(x, base_y, x + w, base_y)
    for index, (label, value) in enumerate(items):
        center = x + slot * index + slot / 2
        height = max(chart_h * value / peak, 1.5)
        color = HexColor("#" + (colors[index] if colors else "7C3AED"))
        c.setFillColor(color)
        c.roundRect(center - bar_w / 2, base_y, bar_w, height, 3, stroke=0, fill=1)
        _text(c, center, base_y + height + 5, value_fmt(value), size=8, bold=True, align="center")
        for n, line in enumerate(_wrap(label, FONT, 8, slot - 6, 2)):
            _text(c, center, base_y - 13 - n * 10, line, size=8, align="center")


def _doughnut(c, x, y_top, w, h, items, colors):
    """Ciambella a sinistra e legenda a destra; `items` = [(etichetta, valore)]."""
    total = sum(item[-1] for item in items)
    if total <= 0:
        return
    diameter = min(h - 10, w * 0.42)
    cx = x + diameter / 2 + 6
    cy = y_top - h / 2
    left, bottom = cx - diameter / 2, cy - diameter / 2
    start = 90.0
    for (label, detail, value), color in zip(items, colors):
        extent = 360.0 * value / total
        if extent <= 0:
            continue
        c.setFillColor(HexColor("#" + color))
        c.setStrokeColor(white)
        c.setLineWidth(1)
        c.wedge(left, bottom, left + diameter, bottom + diameter, start, -extent, stroke=1, fill=1)
        start -= extent
    c.setFillColor(white)
    c.circle(cx, cy, diameter * 0.31, stroke=0, fill=1)

    legend_x = x + diameter + 28
    legend_w = w - diameter - 34
    row_h = 30
    first = cy + (len(items) * row_h) / 2 - 14
    for index, ((label, detail, value), color) in enumerate(zip(items, colors)):
        ly = first - index * row_h
        c.setFillColor(HexColor("#" + color))
        c.roundRect(legend_x, ly - 1, 9, 9, 2, stroke=0, fill=1)
        _text(c, legend_x + 15, ly, label, size=9, bold=True, max_width=legend_w - 15)
        _text(c, legend_x + 15, ly - 11, detail, size=8.5, color=MUTED, max_width=legend_w - 15)


def _cover(c, ctx, date_label):
    steps = 80
    top, bottom = (0x1A, 0x08, 0x40), (0x4B, 0x17, 0xA8)
    band = PAGE_H / steps
    for i in range(steps):
        ratio = i / (steps - 1)
        r, g, b = (top[k] + (bottom[k] - top[k]) * ratio for k in range(3))
        c.setFillColorRGB(r / 255, g / 255, b / 255)
        c.rect(0, PAGE_H - band * (i + 1), PAGE_W, band + 1, stroke=0, fill=1)
    if os.path.exists(LOGO_PATH):
        logo_w = 270
        logo_h = logo_w * 516 / 691
        c.drawImage(LOGO_PATH, PAGE_W - logo_w - 60, (PAGE_H - logo_h) / 2, width=logo_w, height=logo_h,
                    mask="auto", preserveAspectRatio=True)
    _text(c, 55, PAGE_H / 2 + 40, "D&A Advisory Cockpit", size=38, bold=True, color=white, max_width=430)
    fy = ctx.get("fiscal_year")
    _text(c, 55, PAGE_H / 2 + 6, "Practice Cockpit report" + (f" - {fiscal.fy_label(fy)}" if fy else ""),
          size=18, color=HexColor("#D4C4F7"))
    _text(c, 55, PAGE_H / 2 - 24, date_label, size=12, color=HexColor("#D4C4F7"))
    _text(c, 55, PAGE_H / 2 - 56, ctx["filters_summary"], size=10, color=HexColor("#C9B8F5"), max_width=430)


def build_cockpit_pdf(ctx):
    agg = _aggregate(ctx)
    date_label = datetime.now().strftime("%d/%m/%Y")
    fy = ctx.get("fiscal_year")
    fy_suffix = f" · {fiscal.fy_label(fy)}" if fy else ""

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    c.setTitle("MIRA - D&A Advisory Cockpit")
    c.setAuthor("MIRA")

    gap = 16
    card_w = (PAGE_W - 2 * MARGIN - gap) / 2
    card_h = 360
    card_top = PAGE_H - 105

    # ── Cover ─────────────────────────────────────────────────────────────────
    _cover(c, ctx, date_label)
    c.showPage()
    page = 2

    # ── Practice Indicators ───────────────────────────────────────────────────
    fy_text = f"{fiscal.fy_label(fy)} ({fiscal.fy_period_text(fy)}) · " if fy else ""
    _base_page(c, "Practice Indicators", fy_text + ctx["filters_summary"], page, date_label)
    tile_gap = 14
    tile_w = (PAGE_W - 2 * MARGIN - 3 * tile_gap) / 4
    tile_h = 128
    for index, kpi in enumerate(ctx["kpis"]):
        label, value = kpi[0], kpi[1]
        sub = kpi[2] if len(kpi) > 2 else ""
        tone = kpi[3] if len(kpi) > 3 else ""
        row, col = divmod(index, 4)
        x = MARGIN + col * (tile_w + tile_gap)
        y_top = card_top - row * (tile_h + tile_gap)
        _card(c, x, y_top, tile_w, tile_h)
        _text(c, x + 16, y_top - 30, label, size=10, color=MUTED, max_width=tile_w - 32)
        _text(c, x + 16, y_top - 66, value, size=24, bold=True, max_width=tile_w - 32)
        if sub:
            color = {"up": UP, "down": DOWN}.get(tone, MUTED)
            _text(c, x + 16, y_top - 98, sub, size=8.5, bold=bool(tone), color=color, max_width=tile_w - 32)
    c.showPage()
    page += 1

    # ── Commercial: tecnologia ────────────────────────────────────────────────
    _base_page(c, "Commercial Performance", "Opportunity value by technology", page, date_label)
    left_x, right_x = MARGIN, MARGIN + card_w + gap

    _chart_card(c, left_x, card_top, card_w, card_h, "Opportunity Value & Technology Fragmentation (€ M)" + fy_suffix)
    if agg["technology_value"]:
        items = [(n, v / 1_000_000) for n, v in agg["technology_value"][:8]]
        colors = [BAR_PURPLES[min(i, len(BAR_PURPLES) - 1)] for i in range(len(items))]
        _vbar(c, left_x + 16, card_top - 40, card_w - 32, card_h - 56, items, lambda v: f"€ {v:.2f} M", colors)
    else:
        _empty(c, left_x, card_top, card_w, card_h)

    _chart_card(c, right_x, card_top, card_w, card_h, "Technology Distribution" + fy_suffix)
    distribution = list(agg["technology_value"][:6])
    others = sum(v for _, v in agg["technology_value"][6:])
    if others > 0:
        distribution.append(("Others", others))
    total_distribution = sum(v for _, v in distribution)
    if total_distribution > 0:
        labels = [(n, f"{_fmt_m(v)} ({v / total_distribution:.0%})", v) for n, v in distribution]
        _doughnut(c, right_x + 16, card_top - 36, card_w - 32, card_h - 52, labels, TECH_PALETTE[:len(distribution)])
    else:
        _empty(c, right_x, card_top, card_w, card_h)
    c.showPage()
    page += 1

    # ── Commercial: industry + top 5 technologies ─────────────────────────────
    _base_page(c, "Commercial Performance", "Industry and technology rankings", page, date_label)
    _chart_card(c, left_x, card_top, card_w, card_h, "Opportunity Value by Industry (€ M)" + fy_suffix)
    industries = [(n, v) for n, v in agg["industry_value"] if v > 0][:8]
    if industries:
        _hbar(c, left_x + 16, card_top - 40, card_w - 32, card_h - 56,
              [(n, v / 1_000_000) for n, v in industries], lambda v: f"€ {v:.2f} M")
    else:
        _empty(c, left_x, card_top, card_w, card_h)

    _chart_card(c, right_x, card_top, card_w, card_h, "Top 5 Technologies (number of opportunities)")
    top5 = agg["technology_count"][:5]
    if top5:
        _hbar(c, right_x + 16, card_top - 40, card_w - 32, card_h - 56, top5, lambda v: f"{int(v)}")
    else:
        _empty(c, right_x, card_top, card_w, card_h)
    c.showPage()
    page += 1

    # ── Staffing: indicatori + disponibilità + livelli ────────────────────────
    _base_page(c, "Staffing Overview", ctx["filters_summary"], page, date_label)
    staffing_kpis = [
        ("Resources", str(agg["total_resources"])),
        ("Available", str(agg["available_resources"])),
        ("Fully Allocated", str(agg["fully_allocated"])),
        ("Average Allocation", f"{agg['average_allocation']:.1f}%"),
    ]
    small_h = 76
    for index, (label, value) in enumerate(staffing_kpis):
        x = MARGIN + index * (tile_w + tile_gap)
        _card(c, x, card_top + 8, tile_w, small_h)
        _text(c, x + 16, card_top + 8 - 24, label, size=9.5, color=MUTED)
        _text(c, x + 16, card_top + 8 - 56, value, size=20, bold=True)

    chart_top = card_top - small_h - 6
    chart_h = 270
    _chart_card(c, left_x, chart_top, card_w, chart_h, "Resource Availability")
    availability = agg["availability"]
    if agg["total_resources"] > 0:
        names = list(availability.keys())
        labels = [(n, f"{availability[n]} ({availability[n] / agg['total_resources']:.0%})", availability[n])
                  for n in names]
        _doughnut(c, left_x + 16, chart_top - 36, card_w - 32, chart_h - 52, labels,
                  [AVAILABILITY_COLORS[n] for n in names])
    else:
        _empty(c, left_x, chart_top, card_w, chart_h)

    _chart_card(c, right_x, chart_top, card_w, chart_h, "Resources by Level")
    if agg["levels"]:
        level_items = [
            (f"{key[1]} (L{key[0]})" if key[0] is not None else key[1], count)
            for key, count in agg["levels"]
        ]
        _hbar(c, right_x + 16, chart_top - 40, card_w - 32, chart_h - 56, level_items, lambda v: f"{int(v)}")
    else:
        _empty(c, right_x, chart_top, card_w, chart_h)
    c.showPage()
    page += 1

    # ── Staffing: certificazioni + manager ────────────────────────────────────
    _base_page(c, "Staffing Overview", "Certifications and delivery managers", page, date_label)
    _chart_card(c, left_x, card_top, card_w, card_h, "Top 5 Certifications")
    if agg["certifications"]:
        _hbar(c, left_x + 16, card_top - 40, card_w - 32, card_h - 56, agg["certifications"], lambda v: f"{int(v)}")
    else:
        _empty(c, left_x, card_top, card_w, card_h, "No certifications for the selected filters")

    _chart_card(c, right_x, card_top, card_w, card_h, "Top 5 Managers by Active OSR")
    if agg["managers"]:
        _hbar(c, right_x + 16, card_top - 40, card_w - 32, card_h - 56, agg["managers"], lambda v: f"{int(v)}")
    else:
        _empty(c, right_x, card_top, card_w, card_h, "No managers on active OSRs for the selected filters")
    c.showPage()

    c.save()
    return buffer.getvalue()
