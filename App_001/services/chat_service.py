import re
from . import db, ai_service

SYSTEM_PROMPT = """Sei un assistente esperto di staffing per progetti SAP/IT di Accenture Italy.
Hai accesso ai dati reali del sistema StaffMatch: risorse (dipendenti), progetti, opportunity e skill.
Rispondi sempre in italiano, in modo preciso e conciso, basandoti esclusivamente sui dati forniti nel contesto.
Se la domanda non riguarda i dati del sistema, rispondi che puoi aiutare solo con informazioni relative alle risorse, progetti e opportunity presenti nel sistema.
Non inventare dati che non sono nel contesto."""

# ── Classificazione domanda ────────────────────────────────────────────────────

_SKILLS_KEYWORDS = re.compile(
    r"specializ|competenz|skill|espert|conosc|certific|linguaggi|sa fare|capac|brav|tecnolog|livello",
    re.IGNORECASE
)
_PROJECTS_KEYWORDS = re.compile(
    r"progett|staffat|allocat|assegnat|scad|fine prev|data fine|team|lavora su|lavora in|quando finisce|cliente del progetto",
    re.IGNORECASE
)
_OPPORTUNITY_KEYWORDS = re.compile(
    r"opportunit|opportunity|aperta|nuov.{0,5}ricerca|cerca risorsa|posizione aperta",
    re.IGNORECASE
)
_AVAILABILITY_KEYWORDS = re.compile(
    r"disponibil|libero|libera|bench|non staffat|non allocat|occupat|pieno",
    re.IGNORECASE
)


def _classify(question: str) -> set:
    """Restituisce il set di sezioni dati necessarie per rispondere."""
    categories = set()
    if _SKILLS_KEYWORDS.search(question):
        categories.add("skills")
    if _PROJECTS_KEYWORDS.search(question):
        categories.add("projects")
    if _OPPORTUNITY_KEYWORDS.search(question):
        categories.add("opportunities")
    if _AVAILABILITY_KEYWORDS.search(question):
        categories.add("availability")
    # fallback: se nessuna categoria specifica, carica tutto
    if not categories:
        categories = {"skills", "projects", "opportunities", "availability"}
    return categories


# ── Costruzione contesto selettivo ─────────────────────────────────────────────

def _build_context(categories: set) -> str:
    from datetime import datetime
    now = datetime.now().strftime("%A %d %B %Y, ore %H:%M")
    lines = [f"=== DATA E ORA CORRENTE ===\n{now}"]

    resources  = db.get_resources()
    roles_map  = {r["id"]: r for r in db.get_roles()}
    res_name_map = {r["id"]: f"{r.get('nome','')} {r.get('cognome','')}" for r in resources}

    # Sezione RISORSE — sempre inclusa, ma il dettaglio delle skill dipende dalla categoria
    include_skills = "skills" in categories
    skills_map = {s["id"]: s["nome"] for s in db.get_skills()} if include_skills else {}
    groups_map = {g["id"]: g["nome"] for g in db.get_role_groups()}

    lines.append("\n=== RISORSE (DIPENDENTI) ===")
    for r in resources:
        ruolo = roles_map.get(r.get("ruolo_id", ""), {})
        parts = [
            f"- {r.get('nome','')} {r.get('cognome','')}",
            f"Mansione: {ruolo.get('nome','')} ({ruolo.get('seniority','')})",
        ]
        if include_skills:
            skill_names = [
                f"{skills_map.get(sk.get('skill_id',''), sk.get('skill_id',''))} lv.{sk.get('livello','?')}"
                for sk in r.get("skill_ids", []) if isinstance(sk, dict)
            ]
            parts.append(f"Skills: {', '.join(skill_names) if skill_names else 'nessuna'}")
            parts.append(f"Lingue: {', '.join(r.get('lingue', []))}")
        if "availability" in categories or "projects" in categories:
            parts.append(f"Disponibilità: {r.get('disponibilita', 0)}%")
        gruppi = [groups_map.get(gid, gid) for gid in r.get("gruppo_ruolo_ids", [])]
        parts.append(f"Ruolo: {', '.join(gruppi)}")
        parts.append(f"Email: {r.get('email','')}")
        lines.append(" | ".join(parts))

    # Sezione PROGETTI + ALLOCAZIONI
    if "projects" in categories:
        allocations = db.get_allocations()
        alloc_by_proj = {}
        alloc_by_res = {}
        for a in allocations:
            alloc_by_proj.setdefault(a["progetto_id"], []).append(a)
            alloc_by_res.setdefault(a["risorsa_id"], []).append(a)

        projects = db.get_projects()
        lines.append("\n=== PROGETTI ===")
        for p in projects:
            allocs = alloc_by_proj.get(p["id"], [])
            alloc_desc = ", ".join(
                f"{res_name_map.get(a['risorsa_id'], a['risorsa_id'])} {a.get('percentuale','')}% (fino al {a.get('data_fine','')})"
                for a in allocs
            )
            lines.append(
                f"- {p.get('nome','')} | Cliente: {p.get('cliente','')} | "
                f"Stato: {p.get('stato','')} | "
                f"Inizio: {p.get('data_inizio','')} | Fine prev.: {p.get('data_fine_prevista','')} | "
                f"Risorse allocate: {len(allocs)}"
                + (f" ({alloc_desc})" if alloc_desc else "")
            )

    # Sezione OPPORTUNITY
    if "opportunities" in categories:
        opportunities = db.get_opportunities()
        opp_skills_map = {s["id"]: s["nome"] for s in db.get_skills()} if not include_skills else skills_map
        lines.append("\n=== OPPORTUNITY ===")
        for o in opportunities:
            slot_desc = [
                f"{roles_map.get(sl.get('mansione_id',''), {}).get('nome', sl.get('mansione_id','?'))} {sl.get('percentuale_allocazione','')}%"
                for sl in o.get("slot_risorse", [])
            ]
            skill_req = [
                f"{opp_skills_map.get(sk.get('skill_id',''), sk.get('skill_id',''))} lv.>={sk.get('livello_minimo','?')}"
                for sk in o.get("skill_richieste", [])
            ]
            lines.append(
                f"- {o.get('titolo','')} | Cliente: {o.get('cliente','')} | "
                f"Stato: {o.get('stato','')} | "
                f"Inizio: {o.get('data_inizio','')} | Fine prev.: {o.get('data_fine_prevista','')} | "
                f"Slot: {'; '.join(slot_desc) if slot_desc else 'nessuno'} | "
                f"Skills richieste: {', '.join(skill_req) if skill_req else 'nessuna'}"
            )

    return "\n".join(lines)


# ── Entry point ────────────────────────────────────────────────────────────────

def ask(question: str, history: list = None) -> str:
    categories = _classify(question)
    context = _build_context(categories)

    # Il contesto dati va nel system prompt (sempre aggiornato per la domanda corrente)
    system_with_context = f"{SYSTEM_PROMPT}\n\n{context}"

    # History: turni precedenti come Q&A puliti, poi la domanda corrente
    messages = []
    if history:
        for msg in history:
            role = msg.role if hasattr(msg, "role") else msg.get("role")
            content = msg.content if hasattr(msg, "content") else msg.get("content")
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": question})

    return ai_service.call_claude_messages(system_with_context, messages, max_tokens=1024)
