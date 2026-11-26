import os
from datetime import date, datetime
from io import BytesIO

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt
from reportlab.pdfbase.pdfmetrics import stringWidth

PURPLE = RGBColor(0x7C, 0x3A, 0xED)
PURPLE_DARK = RGBColor(0x4C, 0x1D, 0x95)
PURPLE_BAR = RGBColor(0x5B, 0x21, 0xB6)
INK = RGBColor(0x1E, 0x1B, 0x4B)
MUTED = RGBColor(0x6B, 0x72, 0x80)
LAVENDER = RGBColor(0xF5, 0xF2, 0xFB)
BORDER = RGBColor(0xEC, 0xE6, 0xFA)
SOFT = RGBColor(0xD4, 0xC4, 0xF7)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Calibri"

PHOTOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "photos")

LANGUAGE_NAMES = {
    "ITA": "Italian", "ENG": "English", "FRA": "French", "DEU": "German", "ESP": "Spanish",
    "POR": "Portuguese", "NLD": "Dutch", "RUS": "Russian", "ZHO": "Chinese",
}

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _fit(text, size, max_width_in, bold=False):
    """Tronca il testo perché stia in una riga (stima prudente con Helvetica, più larga di Calibri)."""
    font = "Helvetica-Bold" if bold else "Helvetica"
    text = str(text)
    limit = max_width_in * 72

    if stringWidth(text, font, size) <= limit:
        return text

    while text and stringWidth(text + "…", font, size) > limit:
        text = text[:-1]

    return text.rstrip() + "…"


def _wrap(text, size, max_width_in, max_lines, bold=False):
    font = "Helvetica-Bold" if bold else "Helvetica"
    limit = max_width_in * 72
    lines, current = [], ""

    for word in str(text).split():
        trial = (current + " " + word).strip()

        if stringWidth(trial, font, size) <= limit or not current:
            current = trial
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = _fit(lines[-1] + " …", size, max_width_in, bold)

    return lines


def _month_year(value):
    if not value:
        return None

    try:
        parsed = datetime.strptime(str(value)[:10], "%Y-%m-%d")
    except ValueError:
        return None

    return f"{MONTHS[parsed.month - 1]} {parsed.year}"


def _text(slide, x, y, w, h, text, size=12, bold=False, italic=False, color=INK,
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
    run.font.italic = italic
    run.font.name = FONT
    run.font.color.rgb = color
    return box


def _lines(slide, x, y, w, h, items, size=11, line_gap=1.0):
    """Più righe in un solo box; ogni item è una lista di (testo, bold, italic, colore)."""
    box = slide.shapes.add_textbox(x, y, w, h)
    frame = box.text_frame
    frame.word_wrap = True
    frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0

    first = True
    for item in items:
        paragraph = frame.paragraphs[0] if first else frame.add_paragraph()
        first = False
        paragraph.line_spacing = line_gap
        paragraph.space_after = Pt(item.get("after", 0))

        for text, bold, italic, color in item["runs"]:
            run = paragraph.add_run()
            run.text = text
            run.font.size = Pt(item.get("size", size))
            run.font.bold = bold
            run.font.italic = italic
            run.font.name = FONT
            run.font.color.rgb = color

    return box


def _rect(slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.RECTANGLE):
    shape = slide.shapes.add_shape(shape, x, y, w, h)
    shape.shadow.inherit = False

    if fill is None:
        shape.fill.background()
    else:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill

    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(0.75)

    return shape


def _section_bar(slide, x, y, w, title):
    bar = _rect(slide, x, y, w, Inches(0.42), PURPLE_BAR)
    _text(slide, x + Inches(0.18), y, w - Inches(0.3), Inches(0.42), title,
          size=15, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    return bar


def _photo_path(eid):
    path = os.path.join(PHOTOS_DIR, f"{eid}.png")
    return path if eid and os.path.exists(path) else None


def _square_photo(path):
    image = Image.open(path).convert("RGBA")
    side = min(image.size)
    left, top = (image.width - side) // 2, (image.height - side) // 4
    top = max(0, min(top, image.height - side))
    cropped = image.crop((left, top, left + side, top + side)).resize((600, 600))
    buffer = BytesIO()
    cropped.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def _summary(resource, history):
    name = f"{resource.get('nome', '')} {resource.get('cognome', '')}".strip()
    level_name = resource.get("level_name") or "consultant"
    parts = [f"{name} is {'an' if level_name[:1].lower() in 'aeiou' else 'a'} {level_name} in the Data & Analytics practice"]

    if resource.get("city"):
        parts[0] += f", based in {resource['city']}"

    parts[0] += "."

    hire = str(resource.get("hire_date") or "")[:4]
    years = resource.get("anni_esperienza")
    previous = resource.get("previous_experience_years")

    experience = []
    if hire.isdigit():
        experience.append(f"Joined in {hire}")
    if years:
        experience.append(f"{years} years of total experience")
    if previous:
        experience.append(f"of which {previous} before joining")
    if experience:
        parts.append(", ".join(experience) + ".")

    skills = [s.get("skill_name") for s in resource.get("skills", []) if s.get("skill_name")]
    if skills:
        parts.append("Core skills: " + ", ".join(skills[:4]) + ".")

    clients = list(dict.fromkeys(h.get("client_name") for h in history if h.get("client_name")))
    if clients:
        parts.append("Delivered work for " + ", ".join(clients[:3]) + ".")

    return " ".join(parts)


def build_resource_cv_pptx(resource):
    history = resource.get("assignment_history")
    if history is None:
        history = (resource.get("current_assignments") or []) + (
            [resource["last_assignment"]] if resource.get("last_assignment") else []
        )

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = WHITE

    name = f"{resource.get('nome', '')} {resource.get('cognome', '')}".strip()
    eid = resource.get("eid")

    # ── Fascia superiore ──────────────────────────────────────────────────────
    band = _rect(slide, 0, 0, prs.slide_width, Inches(1.5), PURPLE_DARK)
    band.fill.gradient()
    band.fill.gradient_angle = 0
    stops = band.fill.gradient_stops
    stops[0].color.rgb = PURPLE_DARK
    stops[1].color.rgb = PURPLE

    _text(slide, Inches(2.95), Inches(0.28), Inches(8.6), Inches(0.75),
          _fit(name.upper(), 36, 8.6, bold=True), size=36, bold=True, color=WHITE)

    subtitle = " · ".join(
        part for part in (
            (resource.get("level_name") or "").upper(),
            "D&A PRACTICE",
            (resource.get("city") or "").upper(),
        ) if part
    )
    _text(slide, Inches(2.95), Inches(0.98), Inches(8.6), Inches(0.4),
          _fit(subtitle, 17, 8.6), size=17, color=SOFT)

    # Badge del livello (in alto a destra)
    badge = _rect(slide, Inches(11.95), Inches(0.22), Inches(1.0), Inches(1.0), WHITE, shape=MSO_SHAPE.OVAL)
    badge.line.color.rgb = SOFT
    badge.line.width = Pt(2)
    _text(slide, Inches(11.95), Inches(0.37), Inches(1.0), Inches(0.45),
          f"L{resource.get('level') if resource.get('level') is not None else '–'}",
          size=24, bold=True, color=PURPLE_DARK, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    _text(slide, Inches(11.95), Inches(0.8), Inches(1.0), Inches(0.25), "LEVEL",
          size=9, bold=True, color=MUTED, align=PP_ALIGN.CENTER)

    # ── Foto (o iniziali) ─────────────────────────────────────────────────────
    diameter, px, py = Inches(2.25), Inches(0.35), Inches(0.2)
    photo = _photo_path(eid)

    if photo:
        picture = slide.shapes.add_picture(_square_photo(photo), px, py, diameter, diameter)
        picture.auto_shape_type = MSO_SHAPE.OVAL
        picture.line.color.rgb = WHITE
        picture.line.width = Pt(3)
    else:
        circle = _rect(slide, px, py, diameter, diameter, PURPLE, shape=MSO_SHAPE.OVAL)
        circle.fill.gradient()
        circle.fill.gradient_angle = 45
        gradient = circle.fill.gradient_stops
        gradient[0].color.rgb = RGBColor(0xEC, 0x48, 0x99)
        gradient[1].color.rgb = RGBColor(0x5B, 0x21, 0xB6)
        circle.line.color.rgb = WHITE
        circle.line.width = Pt(3)
        initials = ((resource.get("nome") or "")[:1] + (resource.get("cognome") or "")[:1]).upper() or "?"
        _text(slide, px, py, diameter, diameter, initials, size=60, bold=True, color=WHITE,
              align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    left_x, left_w = Inches(0.35), Inches(6.35)
    right_x, right_w = Inches(6.95), Inches(6.03)

    # ── Professional qualification ───────────────────────────────────────────
    _section_bar(slide, left_x, Inches(2.62), left_w, "PROFESSIONAL QUALIFICATION")
    _rect(slide, left_x, Inches(3.04), left_w, Inches(2.42), LAVENDER, BORDER)

    text_w = 6.0
    items = []

    for line in _wrap(_summary(resource, history), 11, text_w, 4):
        items.append({"runs": [(line, False, False, INK)], "size": 11})
    items[-1]["after"] = 5 if items else 0

    certifications = resource.get("certifications") or []
    if certifications:
        items.append({"runs": [("Certifications", True, False, PURPLE_BAR)], "size": 11, "after": 1})
        for cert in certifications[:4]:
            until = _month_year(cert.get("expiration_date"))
            label = f"• {cert.get('nome_cert') or cert.get('cert_id')}" + (f" (valid until {until})" if until else "")
            items.append({"runs": [(_fit(label, 10, text_w), False, False, INK)], "size": 10})
        if len(certifications) > 4:
            items.append({"runs": [(f"+ {len(certifications) - 4} more", False, True, MUTED)], "size": 10})

    languages = [
        LANGUAGE_NAMES.get(l.get("language_code"), l.get("language_code"))
        for l in resource.get("languages", []) if l.get("language_code")
    ]
    if languages:
        items.append({"runs": [("Languages: ", True, False, PURPLE_BAR), (", ".join(languages), False, False, INK)],
                      "size": 10.5, "after": 0})

    _lines(slide, left_x + Inches(0.18), Inches(3.14), left_w - Inches(0.36), Inches(2.25), items)

    # ── Areas of expertise ───────────────────────────────────────────────────
    _section_bar(slide, left_x, Inches(5.58), left_w, "AREAS OF EXPERTISE")
    _rect(slide, left_x, Inches(6.0), left_w, Inches(1.0), LAVENDER, BORDER)

    functional = list(dict.fromkeys(h.get("functional_area") for h in history if h.get("functional_area")))
    industries = list(dict.fromkeys(h.get("industry_sector") for h in history if h.get("industry_sector")))
    roles = list(dict.fromkeys(h.get("project_role") for h in history if h.get("project_role")))
    functional_items = (functional + industries + roles)[:4]

    skills = [s.get("skill_name") for s in resource.get("skills", []) if s.get("skill_name")]
    clusters = [h.get("main_tech_cluster") for h in history if h.get("main_tech_cluster")]
    technical_items = list(dict.fromkeys(skills + clusters))[:4]

    col_w = 2.95

    def column(x, title, entries, empty):
        rows = [{"runs": [(title, True, False, INK)], "size": 10.5, "after": 1}]
        for entry in entries:
            rows.append({"runs": [("• " + _fit(entry, 10, col_w - 0.1), False, False, INK)], "size": 10})
        if not entries:
            rows.append({"runs": [(empty, False, True, MUTED)], "size": 10})
        _lines(slide, x, Inches(6.05), Inches(col_w), Inches(0.92), rows)

    column(left_x + Inches(0.18), "FUNCTIONAL EXPERTISE", functional_items, "No project history yet")
    column(left_x + Inches(3.3), "TECHNICAL EXPERTISE", technical_items, "No skills recorded")

    # ── Selected project examples ────────────────────────────────────────────
    _section_bar(slide, right_x, Inches(1.78), right_w, "SELECTED PROJECT EXAMPLES")
    _rect(slide, right_x, Inches(2.2), right_w, Inches(4.8), LAVENDER, BORDER)

    projects = history[:4]
    block_h = 1.18
    inner_w = 5.65

    if not projects:
        _text(slide, right_x, Inches(2.2), right_w, Inches(4.8), "No project history available",
              size=12, italic=True, color=MUTED, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    for index, project in enumerate(projects):
        top = 2.32 + index * block_h
        start, end = _month_year(project.get("start_date")), _month_year(project.get("end_date"))
        status = project.get("osr_status") or project.get("status")
        period = f"{start or '—'} – {end or 'Today'}"
        if status in ("Active", "Rolling-off"):
            period += " (ongoing)"

        title = project.get("opportunity_title") or "Project"
        client = project.get("client_name")
        head_lines = _wrap(title + (f" ({client})" if client else ""), 12.5, inner_w, 2, bold=True)

        detail = [
            ("Role: ", True, False, INK),
            (_fit(project.get("project_role") or "—", 10.5, 2.4), False, False, INK),
            (f"  ·  Allocation: {project.get('allocation_pct') if project.get('allocation_pct') is not None else '—'}%", False, False, INK),
        ]
        extras = " · ".join(
            part for part in (
                project.get("main_tech_cluster"),
                project.get("functional_area"),
                project.get("industry_sector"),
            ) if part
        )
        rows = [{"runs": [(line, True, False, INK)], "size": 12.5, "after": 0} for line in head_lines]
        rows += [
            {"runs": [(period, True, True, PURPLE_BAR)], "size": 10.5, "after": 1},
            {"runs": detail, "size": 10.5, "after": 1},
        ]
        if extras:
            rows.append({"runs": [(_fit(extras, 10, inner_w), False, True, MUTED)], "size": 10})
        elif project.get("manager_name"):
            rows.append({"runs": [(_fit(f"Manager: {project['manager_name']}", 10, inner_w), False, True, MUTED)], "size": 10})

        _lines(slide, right_x + Inches(0.18), Inches(top), Inches(inner_w), Inches(block_h - 0.1), rows)

    if len(history) > 4:
        _text(slide, right_x + Inches(0.18), Inches(6.72), Inches(inner_w), Inches(0.22),
              f"+ {len(history) - 4} more assignments", size=10, italic=True, color=MUTED)

    # ── Piè di pagina ────────────────────────────────────────────────────────
    _text(slide, left_x, Inches(7.14), Inches(9), Inches(0.25),
          f"MIRA · D&A Advisory Cockpit · EID {eid} · generated {date.today():%d/%m/%Y}", size=9, color=MUTED)

    buffer = BytesIO()
    prs.save(buffer)
    return buffer.getvalue()
