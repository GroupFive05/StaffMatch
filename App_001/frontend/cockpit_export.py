import os
from datetime import datetime
from io import BytesIO

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

import fiscal

PURPLE = RGBColor(0x7C, 0x3A, 0xED)
PURPLE_DARK = RGBColor(0x5B, 0x21, 0xB6)
INK = RGBColor(0x1E, 0x1B, 0x4B)
MUTED = RGBColor(0x6B, 0x72, 0x80)
LAVENDER = RGBColor(0xF5, 0xF2, 0xFB)
BORDER = RGBColor(0xEC, 0xE6, 0xFA)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Calibri"

BAR_PURPLES = ["5B21B6", "7C3AED", "8B5CF6", "A78BFA", "C4B5FD", "DDD6FE"]
TECH_PALETTE = ["4C1D95", "7C3AED", "A855F7", "C084FC", "F97316", "FBBF24", "D1D5DB"]
AVAILABILITY_COLORS = {
    "Fully Allocated": "16A34A",
    "Partially Allocated": "F59E0B",
    "Available": "DC2626",
}

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "mira_logo_dark.png")


def _rgb(hex_value):
    return RGBColor.from_string(hex_value)


def _text(slide, x, y, w, h, text, size=14, bold=False, color=INK,
          align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(x, y, w, h)
    frame = box.text_frame
    frame.word_wrap = True
    frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
    frame.vertical_anchor = anchor
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    run = paragraph.add_run()
    run.text = str(text)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = FONT
    run.font.color.rgb = color
    return box


def _card(slide, x, y, w, h):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shape.adjustments[0] = 0.04
    shape.fill.solid()
    shape.fill.fore_color.rgb = WHITE
    shape.line.color.rgb = BORDER
    shape.line.width = Pt(0.75)
    shape.shadow.inherit = False
    return shape


def _base_slide(prs, title, subtitle, page, date_label):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = LAVENDER

    _text(slide, Inches(0.6), Inches(0.35), Inches(12), Inches(0.6), title, size=28, bold=True)
    if subtitle:
        _text(slide, Inches(0.6), Inches(0.95), Inches(12), Inches(0.35), subtitle, size=12, color=MUTED)

    _text(
        slide, Inches(0.6), Inches(7.05), Inches(9), Inches(0.25),
        f"MIRA · D&A Advisory Cockpit · {date_label}", size=9, color=MUTED
    )
    _text(
        slide, Inches(11.9), Inches(7.05), Inches(0.85), Inches(0.25),
        str(page), size=9, color=MUTED, align=PP_ALIGN.RIGHT
    )
    return slide


def _style_axes(chart, number_format):
    chart.font.size = Pt(11)
    chart.font.name = FONT
    chart.font.color.rgb = INK

    value_axis = chart.value_axis
    value_axis.has_major_gridlines = True
    value_axis.major_gridlines.format.line.color.rgb = BORDER
    value_axis.format.line.fill.background()
    value_axis.tick_labels.font.size = Pt(10)
    value_axis.tick_labels.number_format = number_format
    value_axis.tick_labels.number_format_is_linked = False

    chart.category_axis.tick_labels.font.size = Pt(11)
    chart.category_axis.format.line.color.rgb = BORDER


def _bar_chart(slide, x, y, w, h, categories, values, horizontal=False,
               number_format="0.00", label_format=None, colors=None):
    data = CategoryChartData()
    data.categories = categories
    data.add_series("Series", values)

    chart_type = XL_CHART_TYPE.BAR_CLUSTERED if horizontal else XL_CHART_TYPE.COLUMN_CLUSTERED
    chart = slide.shapes.add_chart(chart_type, x, y, w, h, data).chart
    chart.has_legend = False
    chart.has_title = False

    plot = chart.plots[0]
    plot.gap_width = 55
    plot.has_data_labels = True
    labels = plot.data_labels
    labels.number_format = label_format or number_format
    labels.number_format_is_linked = False
    labels.position = XL_LABEL_POSITION.OUTSIDE_END
    labels.font.size = Pt(11)
    labels.font.bold = True
    labels.font.color.rgb = INK

    series = plot.series[0]
    series.format.fill.solid()
    series.format.fill.fore_color.rgb = PURPLE
    if colors:
        for index, color in enumerate(colors):
            point = series.points[index]
            point.format.fill.solid()
            point.format.fill.fore_color.rgb = _rgb(color)

    _style_axes(chart, number_format)
    return chart


def _doughnut(slide, x, y, w, h, categories, values, colors):
    data = CategoryChartData()
    data.categories = categories
    data.add_series("Series", values)

    chart = slide.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, x, y, w, h, data).chart
    chart.has_title = False
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.RIGHT
    chart.legend.include_in_layout = False
    chart.legend.font.size = Pt(11)
    chart.legend.font.name = FONT
    chart.legend.font.color.rgb = INK

    plot = chart.plots[0]
    plot.has_data_labels = False
    series = plot.series[0]
    for index, color in enumerate(colors):
        point = series.points[index]
        point.format.fill.solid()
        point.format.fill.fore_color.rgb = _rgb(color)
        point.format.line.color.rgb = WHITE

    for hole in chart._chartSpace.xpath(".//c:holeSize"):
        hole.set("val", "62")
    return chart


def _chart_card(slide, x, y, w, h, title):
    _card(slide, x, y, w, h)
    _text(slide, x + Inches(0.3), y + Inches(0.2), w - Inches(0.6), Inches(0.4), title, size=15, bold=True)


def _empty(slide, x, y, w, h, message="No data for the selected filters"):
    _text(slide, x, y, w, h, message, size=12, color=MUTED, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


def _fmt_m(value):
    return f"€ {value / 1_000_000:.2f} M"


def _aggregate(ctx):
    commercial = ctx["commercial"]
    resources = ctx["resources"]
    osr_rows = ctx["osr"]

    technology_value, technology_count, industry_value = {}, {}, {}

    fy = ctx.get("fiscal_year")

    for row in commercial:
        value = float(row.get("opportunity_value") or 0)

        if fy:
            value = fiscal.fy_share(
                row.get("opportunity_value"), row.get("opportunity_start_date"),
                row.get("opportunity_end_date"), fy
            )

        technology = row.get("main_tech_cluster") or "Unclassified"
        industry = row.get("industry_sector") or "Unclassified"
        technology_value[technology] = technology_value.get(technology, 0) + value
        technology_count[technology] = technology_count.get(technology, 0) + 1
        industry_value[industry] = industry_value.get(industry, 0) + value

    by_value = lambda mapping: sorted(mapping.items(), key=lambda item: item[1], reverse=True)

    filtered_resources = resources
    if ctx["commercial_filters_active"]:
        visible = {row.get("opportunity_id") for row in commercial if row.get("opportunity_id")}
        eids = {row.get("resource_eid") for row in osr_rows if row.get("opportunity_id") in visible}
        filtered_resources = [r for r in resources if r.get("eid") in eids]

    availability = {"Fully Allocated": 0, "Partially Allocated": 0, "Available": 0}
    levels, certifications, managers = {}, {}, {}

    for resource in filtered_resources:
        status = resource.get("availability_status", "green")
        if status == "red":
            availability["Fully Allocated"] += 1
        elif status == "orange":
            availability["Partially Allocated"] += 1
        else:
            availability["Available"] += 1

        level_key = (resource.get("level"), resource.get("level_name") or "Unclassified")
        levels[level_key] = levels.get(level_key, 0) + 1

        names = {c.get("nome_cert") or c.get("cert_id") for c in resource.get("certifications", [])}
        for name in names:
            if name:
                certifications[name] = certifications.get(name, 0) + 1

        for manager in resource.get("managers", []):
            name = f"{manager.get('nome', '')} {manager.get('cognome', '')}".strip()
            if name:
                managers[name] = managers.get(name, 0) + 1

    total = len(filtered_resources)
    average_allocation = (
        sum(min(int(r.get("active_allocation") or 0), 100) for r in filtered_resources) / total
        if total else 0
    )

    return {
        "technology_value": by_value(technology_value),
        "technology_count": by_value(technology_count),
        "industry_value": by_value(industry_value),
        "total_resources": total,
        "availability": availability,
        "levels": sorted(levels.items(), key=lambda i: (i[0][0] is None, i[0][0] or 0)),
        "certifications": by_value(certifications)[:5],
        "managers": by_value(managers)[:5],
        "average_allocation": average_allocation,
        "fully_allocated": availability["Fully Allocated"],
        "available_resources": sum(
            1 for r in filtered_resources if int(r.get("disponibilita") or 0) > 0
        ),
    }


def _cover(prs, ctx, date_label):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    background.line.fill.background()
    background.shadow.inherit = False
    background.fill.gradient()
    background.fill.gradient_angle = 90
    stops = background.fill.gradient_stops
    stops[0].color.rgb = _rgb("1A0840")
    stops[1].color.rgb = _rgb("4B17A8")

    if os.path.exists(LOGO_PATH):
        slide.shapes.add_picture(LOGO_PATH, Inches(8.1), Inches(1.9), width=Inches(4.6))

    _text(slide, Inches(0.8), Inches(2.2), Inches(7.4), Inches(1.4),
          "D&A Advisory Cockpit", size=44, bold=True, color=WHITE)
    fy = ctx.get("fiscal_year")
    _text(slide, Inches(0.8), Inches(3.55), Inches(7.4), Inches(0.5),
          "Practice Cockpit report" + (f" — {fiscal.fy_label(fy)}" if fy else ""), size=22, color=_rgb("D4C4F7"))
    _text(slide, Inches(0.8), Inches(4.4), Inches(7.4), Inches(0.35),
          date_label, size=14, color=_rgb("D4C4F7"))
    _text(slide, Inches(0.8), Inches(5.0), Inches(7.4), Inches(1.0),
          ctx["filters_summary"], size=12, color=_rgb("C9B8F5"))
    return slide


def build_cockpit_pptx(ctx):
    agg = _aggregate(ctx)
    date_label = datetime.now().strftime("%d/%m/%Y")

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    _cover(prs, ctx, date_label)
    page = 2

    # ── Practice Indicators ───────────────────────────────────────────────────
    fy = ctx.get("fiscal_year")
    fy_text = f"{fiscal.fy_label(fy)} ({fiscal.fy_period_text(fy)}) · " if fy else ""
    slide = _base_slide(prs, "Practice Indicators", fy_text + ctx["filters_summary"], page, date_label)
    kpis = ctx["kpis"]
    tile_w, tile_h, gap = Inches(2.85), Inches(1.9), Inches(0.25)
    left, top = Inches(0.6), Inches(1.7)
    tone_colors = {"up": RGBColor(0x16, 0xA3, 0x4A), "down": RGBColor(0xDC, 0x26, 0x26)}
    for index, kpi in enumerate(kpis):
        label, value = kpi[0], kpi[1]
        sub = kpi[2] if len(kpi) > 2 else ""
        tone = kpi[3] if len(kpi) > 3 else ""
        row, col = divmod(index, 4)
        x = left + col * (tile_w + gap)
        y = top + row * (tile_h + gap)
        _card(slide, x, y, tile_w, tile_h)
        _text(slide, x + Inches(0.3), y + Inches(0.3), tile_w - Inches(0.6), Inches(0.4), label, size=14, color=MUTED)
        _text(slide, x + Inches(0.3), y + Inches(0.72), tile_w - Inches(0.6), Inches(0.7), value,
              size=30, bold=True, color=INK)
        if sub:
            _text(slide, x + Inches(0.3), y + Inches(1.42), tile_w - Inches(0.6), Inches(0.35), sub,
                  size=11, bold=bool(tone), color=tone_colors.get(tone, MUTED))
    page += 1

    # ── Commercial: technology ────────────────────────────────────────────────
    slide = _base_slide(prs, "Commercial Performance", "Opportunity value by technology", page, date_label)
    card_w, card_h, card_y = Inches(6.05), Inches(5.0), Inches(1.6)

    _chart_card(slide, Inches(0.6), card_y, card_w, card_h, "Opportunity Value & Technology Fragmentation (€ M)" + (f" · {fiscal.fy_label(fy)}" if fy else ""))
    if agg["technology_value"]:
        names = [n for n, _ in agg["technology_value"]]
        values = [v / 1_000_000 for _, v in agg["technology_value"]]
        colors = [BAR_PURPLES[min(i, len(BAR_PURPLES) - 1)] for i in range(len(names))]
        _bar_chart(slide, Inches(0.8), card_y + Inches(0.7), card_w - Inches(0.4), card_h - Inches(0.9),
                   names, values, colors=colors, number_format="0.0", label_format='"€ "0.00" M"')
    else:
        _empty(slide, Inches(0.6), card_y, card_w, card_h)

    _chart_card(slide, Inches(6.9), card_y, card_w, card_h, "Technology Distribution" + (f" · {fiscal.fy_label(fy)}" if fy else ""))
    distribution = list(agg["technology_value"][:6])
    others = sum(v for _, v in agg["technology_value"][6:])
    if others > 0:
        distribution.append(("Others", others))
    total_distribution = sum(v for _, v in distribution)
    if total_distribution > 0:
        labels = [f"{n} — {_fmt_m(v)} ({v / total_distribution:.0%})" for n, v in distribution]
        _doughnut(slide, Inches(7.0), card_y + Inches(0.7), card_w - Inches(0.2), card_h - Inches(0.9),
                  labels, [v for _, v in distribution], TECH_PALETTE[:len(distribution)])
    else:
        _empty(slide, Inches(6.9), card_y, card_w, card_h)
    page += 1

    # ── Commercial: industry + top 5 technologies ─────────────────────────────
    slide = _base_slide(prs, "Commercial Performance", "Industry and technology rankings", page, date_label)

    _chart_card(slide, Inches(0.6), card_y, card_w, card_h, "Opportunity Value by Industry (€ M)" + (f" · {fiscal.fy_label(fy)}" if fy else ""))
    industries = [(n, v) for n, v in agg["industry_value"] if v > 0]
    if industries:
        shown = list(reversed(industries[:8]))
        _bar_chart(slide, Inches(0.8), card_y + Inches(0.7), card_w - Inches(0.4), card_h - Inches(0.9),
                   [n for n, _ in shown], [v / 1_000_000 for _, v in shown], horizontal=True,
                   number_format="0.0", label_format='"€ "0.00" M"')
    else:
        _empty(slide, Inches(0.6), card_y, card_w, card_h)

    _chart_card(slide, Inches(6.9), card_y, card_w, card_h, "Top 5 Technologies (number of opportunities)")
    top5 = list(reversed(agg["technology_count"][:5]))
    if top5:
        _bar_chart(slide, Inches(7.1), card_y + Inches(0.7), card_w - Inches(0.4), card_h - Inches(0.9),
                   [n for n, _ in top5], [c for _, c in top5], horizontal=True, number_format="0")
    else:
        _empty(slide, Inches(6.9), card_y, card_w, card_h)
    page += 1

    # ── Staffing: indicators + availability + levels ──────────────────────────
    slide = _base_slide(prs, "Staffing Overview", ctx["filters_summary"], page, date_label)
    staffing_kpis = [
        ("Resources", str(agg["total_resources"])),
        ("Available", str(agg["available_resources"])),
        ("Fully Allocated", str(agg["fully_allocated"])),
        ("Average Allocation", f"{agg['average_allocation']:.1f}%"),
    ]
    small_w, small_h = Inches(2.85), Inches(1.05)
    for index, (label, value) in enumerate(staffing_kpis):
        x = Inches(0.6) + index * (small_w + gap)
        _card(slide, x, Inches(1.45), small_w, small_h)
        _text(slide, x + Inches(0.25), Inches(1.55), small_w - Inches(0.5), Inches(0.3), label, size=12, color=MUTED)
        _text(slide, x + Inches(0.25), Inches(1.85), small_w - Inches(0.5), Inches(0.55), value,
              size=24, bold=True)

    chart_y, chart_h = Inches(2.7), Inches(4.2)
    _chart_card(slide, Inches(0.6), chart_y, card_w, chart_h, "Resource Availability")
    availability = agg["availability"]
    if agg["total_resources"] > 0:
        names = list(availability.keys())
        labels = [
            f"{n} — {availability[n]} ({availability[n] / agg['total_resources']:.0%})" for n in names
        ]
        _doughnut(slide, Inches(0.7), chart_y + Inches(0.6), card_w - Inches(0.2), chart_h - Inches(0.8),
                  labels, [availability[n] for n in names], [AVAILABILITY_COLORS[n] for n in names])
    else:
        _empty(slide, Inches(0.6), chart_y, card_w, chart_h)

    _chart_card(slide, Inches(6.9), chart_y, card_w, chart_h, "Resources by Level")
    if agg["levels"]:
        level_items = list(reversed(agg["levels"]))
        level_names = [
            f"{key[1]} (L{key[0]})" if key[0] is not None else key[1] for key, _ in level_items
        ]
        _bar_chart(slide, Inches(7.1), chart_y + Inches(0.6), card_w - Inches(0.4), chart_h - Inches(0.8),
                   level_names, [count for _, count in level_items], horizontal=True, number_format="0")
    else:
        _empty(slide, Inches(6.9), chart_y, card_w, chart_h)
    page += 1

    # ── Staffing: certifications + managers ───────────────────────────────────
    slide = _base_slide(prs, "Staffing Overview", "Certifications and delivery managers", page, date_label)

    _chart_card(slide, Inches(0.6), card_y, card_w, card_h, "Top 5 Certifications")
    certs = list(reversed(agg["certifications"]))
    if certs:
        _bar_chart(slide, Inches(0.8), card_y + Inches(0.7), card_w - Inches(0.4), card_h - Inches(0.9),
                   [n for n, _ in certs], [c for _, c in certs], horizontal=True, number_format="0")
    else:
        _empty(slide, Inches(0.6), card_y, card_w, card_h, "No certifications for the selected filters")

    _chart_card(slide, Inches(6.9), card_y, card_w, card_h, "Top 5 Managers by Active OSR")
    managers = list(reversed(agg["managers"]))
    if managers:
        _bar_chart(slide, Inches(7.1), card_y + Inches(0.7), card_w - Inches(0.4), card_h - Inches(0.9),
                   [n for n, _ in managers], [c for _, c in managers], horizontal=True, number_format="0")
    else:
        _empty(slide, Inches(6.9), card_y, card_w, card_h, "No managers on active OSRs for the selected filters")

    buffer = BytesIO()
    prs.save(buffer)
    return buffer.getvalue()
