from collections import defaultdict
from datetime import date, datetime, timedelta
from io import BytesIO

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt
from lxml import etree

from cv_export import (
    BORDER, FONT, INK, LAVENDER, MUTED, PURPLE, PURPLE_BAR, PURPLE_DARK, SOFT, WHITE,
    _fit, _month_year, _rect, _text,
)

GREEN = RGBColor(0x16, 0xA3, 0x4A)
RED = RGBColor(0xDC, 0x26, 0x26)
GREY = RGBColor(0x9C, 0xA3, 0xAF)
TINT = RGBColor(0xED, 0xE9, 0xFE)
TINT_SOFT = RGBColor(0xFA, 0xF8, 0xFF)
ROW_ALT = RGBColor(0xFB, 0xFA, 0xFF)

MAX_CONTRACTS = 30


# ── Formattazione ────────────────────────────────────────────────────────────
def _num(value):
    return f"{float(value or 0):,.0f}".replace(",", ".")


def _eur(value):
    return "€ " + _num(value)


def _signed(value):
    """Importo con i negativi tra parentesi, come nel financial summary."""
    value = float(value or 0)
    return f"({_num(abs(value))})" if value < -0.5 else _num(value)


def _parse(value):
    if not value:
        return None

    if isinstance(value, date):
        return value

    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def _business_days(start, end):
    start, end = _parse(start), _parse(end)

    if not start or not end or end < start:
        return 0

    total = (end - start).days + 1
    weeks, rest = divmod(total, 7)
    days = weeks * 5

    for offset in range(rest):
        if (start + timedelta(days=offset)).weekday() < 5:
            days += 1

    return days


def _period(start, end):
    return f"{_month_year(start) or '—'} – {_month_year(end) or '—'}"


# ── Componenti grafici ───────────────────────────────────────────────────────
def _bar(slide, x, y, w, title, right_text=None):
    _rect(slide, x, y, w, Inches(0.3), PURPLE_BAR)
    _text(slide, x + Inches(0.14), y, w - Inches(0.28), Inches(0.3), title, size=12, bold=True,
          color=WHITE, anchor=MSO_ANCHOR.MIDDLE)

    if right_text:
        _text(slide, x + Inches(0.14), y, w - Inches(0.28), Inches(0.3), right_text, size=10,
              color=SOFT, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)


def _cell_bottom_border(cell, color="ECE6FA"):
    tc_pr = cell._tc.get_or_add_tcPr()

    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        for old in tc_pr.findall(qn(tag)):
            tc_pr.remove(old)

    for tag, show in (("a:lnL", False), ("a:lnR", False), ("a:lnT", False), ("a:lnB", True)):
        line = etree.SubElement(tc_pr, qn(tag), w="6350" if show else "0")

        if show:
            fill = etree.SubElement(line, qn("a:solidFill"))
            etree.SubElement(fill, qn("a:srgbClr"), val=color)
        else:
            etree.SubElement(line, qn("a:noFill"))

    # lnX devono precedere il riempimento nel tcPr: sposta il fill in fondo
    for fill in tc_pr.findall(qn("a:solidFill")):
        tc_pr.remove(fill)
        tc_pr.append(fill)


def _table(slide, x, y, col_widths, rows, row_h=0.22, size=9.5):
    """`rows`: lista di righe; ogni cella e' un dict {t, bold, color, align, fill} oppure una stringa."""
    shape = slide.shapes.add_table(len(rows), len(col_widths), x, y, Inches(sum(col_widths)), Inches(row_h * len(rows)))
    table = shape.table
    table.first_row = False
    table.horz_banding = False

    for index, width in enumerate(col_widths):
        table.columns[index].width = Inches(width)

    for r, row in enumerate(rows):
        table.rows[r].height = Inches(row_h)

        for c, cell_def in enumerate(row):
            spec = cell_def if isinstance(cell_def, dict) else {"t": cell_def}
            cell = table.cell(r, c)
            cell.margin_left = Inches(0.08)
            cell.margin_right = Inches(0.08)
            cell.margin_top = Inches(0.01)
            cell.margin_bottom = Inches(0.01)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = spec.get("fill", WHITE)

            frame = cell.text_frame
            frame.word_wrap = False
            paragraph = frame.paragraphs[0]
            paragraph.alignment = spec.get("align", PP_ALIGN.LEFT)
            run = paragraph.add_run()
            run.text = _fit(spec.get("t", ""), spec.get("size", size), col_widths[c] - 0.16, spec.get("bold", False))
            run.font.size = Pt(spec.get("size", size))
            run.font.bold = spec.get("bold", False)
            run.font.italic = spec.get("italic", False)
            run.font.name = FONT
            run.font.color.rgb = spec.get("color", INK)
            _cell_bottom_border(cell)

    return shape


def _doughnut(slide, x, y, w, h, values, colors):
    data = CategoryChartData()
    data.categories = ["Paid", "Planned", "Overdue"]
    data.add_series("Billing", values)
    chart = slide.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, x, y, w, h, data).chart
    chart.has_title = False
    chart.has_legend = False
    plot = chart.plots[0]
    plot.has_data_labels = False
    series = plot.series[0]

    for index, color in enumerate(colors):
        point = series.points[index]
        point.format.fill.solid()
        point.format.fill.fore_color.rgb = color
        point.format.line.color.rgb = WHITE

    for hole in chart._chartSpace.xpath(".//c:holeSize"):
        hole.set("val", "62")


# ── Calcolo dei dati di un contratto ─────────────────────────────────────────
def _contract_model(contract, data):
    contract_id = contract.get("contract_id")
    opportunities = sorted(
        (o for o in data.get("opportunities", []) if o.get("contract_id") == contract_id),
        key=lambda o: str(o.get("opportunity_id")),
    )
    opp_ids = {o.get("opportunity_id") for o in opportunities}
    osr_rows = [r for r in data.get("osr", []) if r.get("opportunity_id") in opp_ids]
    milestones = [m for m in data.get("milestones", []) if m.get("opportunity_id") in opp_ids]

    paid = planned = overdue = 0.0
    next_milestone = None

    for m in milestones:
        amount = float(m.get("amount") or 0)

        if m.get("status") == "Paid" or m.get("actual_date"):
            paid += amount
        elif m.get("status") == "Overdue":
            overdue += amount
        else:
            planned += amount

        if m.get("status") != "Paid" and not m.get("actual_date"):
            when = m.get("planned_date") or "9999-12-31"

            if next_milestone is None or when < (next_milestone.get("planned_date") or "9999-12-31"):
                next_milestone = m

    resources = defaultdict(lambda: {"roles": [], "alloc": 0, "start": None, "end": None, "days": 0.0, "name": "", "eid": None})
    fte = 0.0

    for r in osr_rows:
        item = resources[r.get("resource_eid")]
        item["eid"] = r.get("resource_eid")
        item["name"] = f"{r.get('resource_nome') or ''} {r.get('resource_cognome') or ''}".strip() or "Unassigned"

        if r.get("project_role") and r.get("project_role") not in item["roles"]:
            item["roles"].append(r.get("project_role"))

        start, end = r.get("start_date"), r.get("end_date")
        item["start"] = min(filter(None, [item["start"], start]), default=None)
        item["end"] = max(filter(None, [item["end"], end]), default=None)
        alloc = int(r.get("allocation_pct") or 0)
        item["days"] += _business_days(start, end) * alloc / 100

        if r.get("calculated_status") in ("Active", "Rolling-off"):
            item["alloc"] += alloc
            fte += alloc / 100

    team = sorted(resources.values(), key=lambda item: -item["days"])

    return {
        "opportunities": opportunities,
        "milestones": milestones,
        "paid": paid, "planned": planned, "overdue": overdue,
        "next": next_milestone,
        "team": team,
        "fte": fte,
    }


# ── Slide del contratto ──────────────────────────────────────────────────────
def _contract_slide(prs, contract, data, date_label):
    model = _contract_model(contract, data)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = WHITE

    left, full_w = Inches(0.4), Inches(12.53)

    # Testata
    band = _rect(slide, 0, 0, prs.slide_width, Inches(1.15), PURPLE_DARK)
    band.fill.gradient()
    band.fill.gradient_angle = 0
    stops = band.fill.gradient_stops
    stops[0].color.rgb = PURPLE_DARK
    stops[1].color.rgb = PURPLE

    pill = _rect(slide, left, Inches(0.16), Inches(1.5), Inches(0.28), PURPLE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    pill.adjustments[0] = 0.5
    _text(slide, left, Inches(0.16), Inches(1.5), Inches(0.28), _fit(contract.get("contract_id") or "—", 11, 1.4, True),
          size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    _text(slide, left, Inches(0.46), Inches(10.4), Inches(0.45),
          _fit(contract.get("contract_title") or "Contract", 24, 10.4, True), size=24, bold=True, color=WHITE)

    manager = f"{contract.get('manager_nome') or ''} {contract.get('manager_cognome') or ''}".strip()
    subtitle = " · ".join(p for p in (
        contract.get("client_name"), contract.get("industry_sector"), contract.get("service_group"),
        f"Manager: {manager}" if manager else "",
    ) if p)
    _text(slide, left, Inches(0.88), Inches(10.4), Inches(0.25), _fit(subtitle, 11.5, 10.4), size=11.5, color=SOFT)

    status = contract.get("contract_status") or "n/a"
    badge = _rect(slide, Inches(11.58), Inches(0.2), Inches(1.35), Inches(0.3),
                  RGBColor(0xDC, 0xFC, 0xE7) if status == "Active" else RGBColor(0xFE, 0xE2, 0xE2),
                  shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    badge.adjustments[0] = 0.5
    _text(slide, Inches(11.58), Inches(0.2), Inches(1.35), Inches(0.3), status, size=12, bold=True,
          color=RGBColor(0x16, 0x65, 0x34) if status == "Active" else RGBColor(0x99, 0x1B, 0x1B),
          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    _text(slide, Inches(10.4), Inches(0.62), Inches(2.53), Inches(0.28),
          f"{contract.get('start_date') or '—'} → {contract.get('end_date') or '—'}", size=11, color=SOFT, align=PP_ALIGN.RIGHT)

    # Financial summary (EAC / SAP ODE / Delta)
    revenue = float(contract.get("contract_revenue") or 0)
    costs = float(contract.get("contract_costs") or 0)
    cci = revenue - costs
    cci_pct = (cci / revenue * 100) if revenue else 0

    sap_revenue = contract.get("revenue_sap_ode")
    sap_costs = contract.get("costs_sap_ode")
    direct_costs = contract.get("direct_costs")
    other_costs = contract.get("other_costs")
    sap_cci = (float(sap_revenue) - float(sap_costs)) if sap_revenue is not None and sap_costs is not None else None

    def sap_cells(eac, sap, pct=False):
        if sap is None:
            return [{"t": "—", "color": GREY, "align": PP_ALIGN.RIGHT, "fill": TINT_SOFT},
                    {"t": "—", "color": GREY, "align": PP_ALIGN.RIGHT, "fill": TINT_SOFT}]

        delta = float(eac) - float(sap)
        if pct:
            return [{"t": f"{float(sap):.1f}%", "align": PP_ALIGN.RIGHT, "fill": TINT_SOFT},
                    {"t": f"{delta:.1f}%", "align": PP_ALIGN.RIGHT, "fill": TINT_SOFT, "color": RED if delta < -0.05 else INK}]

        return [{"t": _num(sap), "align": PP_ALIGN.RIGHT, "fill": TINT_SOFT},
                {"t": _signed(delta), "align": PP_ALIGN.RIGHT, "fill": TINT_SOFT, "color": RED if delta < -0.5 else INK}]

    def fin_row(label, eac, sap, bold=False, indent=False, pct=False):
        eac_text = "—" if eac is None else (f"{eac:.1f}%" if pct else _num(eac))
        return [
            {"t": ("    " if indent else "") + label, "bold": bold, "color": INK if bold else RGBColor(0x44, 0x44, 0x44)},
            {"t": eac_text, "bold": bold, "align": PP_ALIGN.RIGHT, "color": INK if eac is not None else GREY},
            *sap_cells(eac, sap, pct),
        ]

    other = (costs - float(direct_costs)) if direct_costs is not None and other_costs is None else other_costs
    header = [{"t": "", "fill": LAVENDER}] + [
        {"t": label, "bold": True, "color": MUTED, "align": PP_ALIGN.RIGHT, "fill": fill}
        for label, fill in (("EAC", LAVENDER), ("SAP ODE", TINT), ("Delta", TINT))
    ]
    fin_rows = [
        header,
        fin_row("Revenue", revenue, sap_revenue, bold=True),
        fin_row("Total cost", costs, sap_costs, bold=True),
        fin_row("Direct costs", None if direct_costs is None else float(direct_costs), None, indent=True),
        fin_row("Other contract costs", None if other is None else float(other), None, indent=True),
        fin_row("CCI", cci, sap_cci, bold=True),
        fin_row("CCI %", cci_pct, (sap_cci / float(sap_revenue) * 100) if sap_cci is not None and float(sap_revenue) else None, pct=True),
    ]

    _bar(slide, left, Inches(1.28), Inches(7.55), "Financial summary", "EAC vs SAP ODE")
    _table(slide, left, Inches(1.58), [2.75, 1.6, 1.6, 1.6], fin_rows, row_h=0.25, size=10)

    # Fatturazione e team
    right_x, right_w = Inches(8.15), Inches(4.78)
    _bar(slide, right_x, Inches(1.28), right_w, "Billing and team")
    _rect(slide, right_x, Inches(1.58), right_w, Inches(1.75), WHITE, BORDER)

    total_billing = model["paid"] + model["planned"] + model["overdue"]

    if total_billing > 0:
        _doughnut(slide, right_x + Inches(0.1), Inches(1.66), Inches(1.5), Inches(1.5),
                  [model["paid"], model["planned"], model["overdue"]],
                  [GREEN, RGBColor(0xDD, 0xD6, 0xFE), RED])
        pct = model["paid"] / total_billing * 100
        _text(slide, right_x + Inches(0.1), Inches(2.18), Inches(1.5), Inches(0.45), f"{pct:.0f}%", size=15, bold=True,
              align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        legend = [
            ("Paid", model["paid"], GREEN), ("Planned", model["planned"], RGBColor(0xA7, 0x8B, 0xFA)),
            ("Overdue", model["overdue"], RED),
        ]
        for index, (label, value, color) in enumerate(legend):
            top = 1.74 + index * 0.27
            _rect(slide, right_x + Inches(1.75), Inches(top + 0.06), Inches(0.12), Inches(0.12), color)
            _text(slide, right_x + Inches(1.95), Inches(top), Inches(2.7), Inches(0.25), f"{label} {_eur(value)}", size=11)

        if model["next"]:
            nxt = model["next"]
            _text(slide, right_x + Inches(1.75), Inches(2.55), Inches(2.9), Inches(0.4),
                  f"Next: {nxt.get('description') or 'milestone'} · {nxt.get('planned_date') or 'date n/a'} · {_eur(nxt.get('amount'))}",
                  size=9.5, color=MUTED)
    else:
        _text(slide, right_x, Inches(1.58), right_w, Inches(1.2), "No purchase orders or milestones yet", size=11,
              italic=True, color=MUTED, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    people = len(model["team"])
    _text(slide, right_x + Inches(1.75), Inches(3.03), Inches(2.9), Inches(0.26),
          f"{people} {'person' if people == 1 else 'people'} · {model['fte']:.1f} FTE active", size=11, bold=True)

    # Opportunity e PO
    _bar(slide, left, Inches(3.47), full_w, "Opportunities and purchase orders")
    box_top, box_h = Inches(3.77), Inches(1.5)
    _rect(slide, left, box_top, full_w, box_h, WHITE, BORDER)

    by_opp = defaultdict(lambda: defaultdict(list))
    for m in model["milestones"]:
        by_opp[m.get("opportunity_id")][(m.get("po_number") or "").strip()].append(m)

    lines = []
    for o in model["opportunities"]:
        pos = by_opp.get(o.get("opportunity_id"), {})
        po_total = sum(float(m.get("amount") or 0) for ms in pos.values() for m in ms)
        gap = float(o.get("opportunity_value") or 0) - po_total if o.get("opportunity_stage") == "Won" else 0
        warn = "  ⚠ POs differ by " + _eur(abs(gap)) if abs(gap) >= 1 else ""
        head = f"{o.get('opportunity_id')}  {o.get('opportunity_title') or ''}"
        meta = " · ".join(p for p in (o.get("main_tech_cluster"), o.get("opportunity_stage"), o.get("opportunity_status")) if p)
        lines.append(("opp", f"{head}  ·  {meta}{warn}", _eur(o.get("opportunity_value"))))

        for po, ms in sorted(pos.items(), key=lambda item: (item[0] == "", item[0])):
            total = sum(float(m.get("amount") or 0) for m in ms)
            open_ms = [m for m in ms if m.get("status") != "Paid" and not m.get("actual_date")]
            state = "invoiced" if not open_ms else f"{len(open_ms)} to invoice"
            lines.append(("po", f"{po or 'No PO assigned'}  ·  {len(ms)} MS", f"{_eur(total)} · {state}"))

    capacity = 7
    shown = lines[:capacity]
    hidden = len(lines) - len(shown)

    for index, (kind, label, amount) in enumerate(shown):
        top = 3.82 + index * 0.2
        indent = 0.14 if kind == "opp" else 0.34
        bold = kind == "opp"
        _text(slide, left + Inches(indent), Inches(top), Inches(9.2), Inches(0.2),
              _fit(label, 10.5, 9.0, bold), size=10.5, bold=bold, color=INK if bold else RGBColor(0x44, 0x44, 0x44))
        _text(slide, left + Inches(9.9), Inches(top), Inches(2.5), Inches(0.2), amount, size=10.5, bold=bold, align=PP_ALIGN.RIGHT)

    if hidden > 0:
        _text(slide, left + Inches(0.14), Inches(3.82 + capacity * 0.2), Inches(5), Inches(0.2),
              f"+ {hidden} more lines", size=10, italic=True, color=MUTED)

    if not lines:
        _text(slide, left, box_top, full_w, box_h, "No opportunities linked to this contract", size=11, italic=True,
              color=MUTED, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # Team e costi per risorsa
    _bar(slide, left, Inches(5.4), full_w, "Team and cost per resource", "daily rate and cost to be imported")

    team_rows = [[
        {"t": "Resource", "bold": True, "color": MUTED, "fill": LAVENDER},
        {"t": "Role", "bold": True, "color": MUTED, "fill": LAVENDER},
        {"t": "Alloc.", "bold": True, "color": MUTED, "fill": LAVENDER, "align": PP_ALIGN.RIGHT},
        {"t": "Period", "bold": True, "color": MUTED, "fill": LAVENDER},
        {"t": "Est. days", "bold": True, "color": MUTED, "fill": LAVENDER, "align": PP_ALIGN.RIGHT},
        {"t": "Daily rate", "bold": True, "color": MUTED, "fill": TINT, "align": PP_ALIGN.RIGHT},
        {"t": "Cost", "bold": True, "color": MUTED, "fill": TINT, "align": PP_ALIGN.RIGHT},
    ]]

    shown_team = model["team"][:3]
    for index, member in enumerate(shown_team):
        fill = WHITE if index % 2 == 0 else ROW_ALT
        team_rows.append([
            {"t": f"{member['name']}  ·  {member['eid']}", "fill": fill},
            {"t": ", ".join(member["roles"]) or "—", "fill": fill},
            {"t": f"{member['alloc']}%" if member["alloc"] else "—", "fill": fill, "align": PP_ALIGN.RIGHT},
            {"t": _period(member["start"], member["end"]), "fill": fill},
            {"t": _num(member["days"]), "fill": fill, "align": PP_ALIGN.RIGHT},
            {"t": "€ —", "fill": TINT_SOFT, "color": GREY, "align": PP_ALIGN.RIGHT},
            {"t": "€ —", "fill": TINT_SOFT, "color": GREY, "align": PP_ALIGN.RIGHT},
        ])

    if len(model["team"]) > 3:
        team_rows.append([{"t": f"+ {len(model['team']) - 3} more resources", "italic": True, "color": MUTED}] + [""] * 4
                         + [{"t": "", "fill": TINT_SOFT}, {"t": "", "fill": TINT_SOFT}])

    if not model["team"]:
        team_rows.append([{"t": "No OSR assigned to this contract", "italic": True, "color": MUTED}] + [""] * 4
                         + [{"t": "", "fill": TINT_SOFT}, {"t": "", "fill": TINT_SOFT}])

    team_rows.append([
        {"t": "Total resources", "bold": True}, "", "", "",
        {"t": _num(sum(m["days"] for m in model["team"])), "bold": True, "align": PP_ALIGN.RIGHT},
        {"t": "", "fill": TINT},
        {"t": "to be imported", "fill": TINT, "color": MUTED, "align": PP_ALIGN.RIGHT},
    ])

    _table(slide, left, Inches(5.7), [3.3, 3.0, 0.8, 2.2, 1.0, 1.1, 1.13], team_rows, row_h=0.205, size=9.5)

    footer = f"MIRA · D&A Advisory Cockpit · {date_label} · revenue and costs shown as EAC"
    _text(slide, left, Inches(7.2), Inches(11), Inches(0.22), footer, size=9, color=MUTED)

    return slide


# ── Copertina (solo con più contratti) ───────────────────────────────────────
def _cover(prs, contracts, data, date_label, filters_summary):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    background = _rect(slide, 0, 0, prs.slide_width, prs.slide_height, PURPLE_DARK)
    background.fill.gradient()
    background.fill.gradient_angle = 90
    stops = background.fill.gradient_stops
    stops[0].color.rgb = RGBColor(0x1A, 0x08, 0x40)
    stops[1].color.rgb = RGBColor(0x4B, 0x17, 0xA8)

    revenue = sum(float(c.get("contract_revenue") or 0) for c in contracts)
    costs = sum(float(c.get("contract_costs") or 0) for c in contracts)
    margin = revenue - costs

    _text(slide, Inches(0.7), Inches(1.7), Inches(5.6), Inches(1.3), "Contracts overview", size=40, bold=True, color=WHITE)
    _text(slide, Inches(0.7), Inches(3.0), Inches(5.6), Inches(0.4),
          f"{len(contracts)} contracts · {date_label}", size=18, color=SOFT)

    kpis = [("Total value", _eur(revenue)), ("Total costs", _eur(costs)),
            ("Margin", f"{_eur(margin)}" + (f"  ({margin / revenue * 100:.1f}%)" if revenue else ""))]

    for index, (label, value) in enumerate(kpis):
        top = 3.8 + index * 0.7
        _text(slide, Inches(0.7), Inches(top), Inches(5.6), Inches(0.25), label, size=11, color=SOFT)
        _text(slide, Inches(0.7), Inches(top + 0.22), Inches(5.6), Inches(0.4), value, size=20, bold=True, color=WHITE)

    _text(slide, Inches(0.7), Inches(6.3), Inches(5.6), Inches(0.6), _fit(filters_summary or "", 10, 5.6),
          size=10, color=RGBColor(0xC9, 0xB8, 0xF5))

    card_x, card_w = Inches(6.8), Inches(6.0)
    shown_rows = min(len(contracts), 14)
    card_h = min(5.9, 1.0 + shown_rows * 0.325 + (0.55 if len(contracts) > 14 else 0.3))
    _rect(slide, card_x, Inches(0.8), card_w, Inches(card_h), WHITE, shape=MSO_SHAPE.ROUNDED_RECTANGLE).adjustments[0] = 0.03
    _text(slide, card_x + Inches(0.3), Inches(1.0), card_w - Inches(0.6), Inches(0.35), "Included contracts", size=15, bold=True)

    rows = []
    for contract in contracts[:14]:
        rows.append([
            {"t": contract.get("contract_id") or "—", "bold": True, "color": PURPLE_BAR},
            {"t": contract.get("contract_title") or "—"},
            {"t": _eur(contract.get("contract_revenue")), "align": PP_ALIGN.RIGHT},
        ])

    if rows:
        _table(slide, card_x + Inches(0.25), Inches(1.45), [1.15, 3.2, 1.15], rows, row_h=0.325, size=10)

    if len(contracts) > 14:
        _text(slide, card_x + Inches(0.3), Inches(1.5 + shown_rows * 0.325 + 0.05), card_w - Inches(0.6), Inches(0.3),
              f"+ {len(contracts) - 14} more contracts in the following pages", size=11, italic=True, color=MUTED)


def build_contracts_pptx(contract_ids, data, filters_summary=""):
    """Un PowerPoint con una slide per contratto; con piu' contratti aggiunge una copertina."""
    by_id = {c.get("contract_id"): c for c in data.get("contracts", [])}
    contracts = [by_id[cid] for cid in contract_ids if cid in by_id][:MAX_CONTRACTS]

    if not contracts:
        raise ValueError("No contracts selected.")

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    date_label = datetime.now().strftime("%d/%m/%Y")

    if len(contracts) > 1:
        _cover(prs, contracts, data, date_label, filters_summary)

    for contract in contracts:
        _contract_slide(prs, contract, data, date_label)

    buffer = BytesIO()
    prs.save(buffer)
    return buffer.getvalue()
