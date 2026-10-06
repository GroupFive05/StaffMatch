from . import db, ai_service

SYSTEM_PROMPT = """Sei un assistente esperto di staffing per progetti SAP/IT di Accenture Italy.
Hai accesso ai dati reali del sistema StaffMatch: risorse (dipendenti), progetti, opportunity e skill.
Rispondi sempre in italiano, in modo preciso e conciso, basandoti esclusivamente sui dati forniti nel contesto.
Se la domanda non riguarda i dati del sistema, rispondi che puoi aiutare solo con informazioni relative alle risorse, progetti e opportunity presenti nel sistema.
Non inventare dati che non sono nel contesto."""


def _build_context() -> str:
    resources    = db.get_resources()
    projects     = db.get_projects()
    opportunities= db.get_opportunities()
    skills_map   = {s["id"]: s["nome"] for s in db.get_skills()}
    roles_map    = {r["id"]: r for r in db.get_roles()}
    groups_map   = {g["id"]: g["nome"] for g in db.get_role_groups()}

    lines = ["=== RISORSE (DIPENDENTI) ==="]
    for r in resources:
        ruolo = roles_map.get(r.get("ruolo_id", ""), {})
        skill_names = []
        for sk in r.get("skill_ids", []):
            if isinstance(sk, dict):
                nome = skills_map.get(sk.get("skill_id", ""), sk.get("skill_id", ""))
                skill_names.append(f"{nome} lv.{sk.get('livello','?')}")
        gruppi = [groups_map.get(gid, gid) for gid in r.get("gruppo_ruolo_ids", [])]
        lines.append(
            f"- {r.get('nome','')} {r.get('cognome','')} | "
            f"Mansione: {ruolo.get('nome','')} ({ruolo.get('seniority','')}) | "
            f"Disponibilità: {r.get('disponibilita', 0)}% | "
            f"Skills: {', '.join(skill_names) if skill_names else 'nessuna'} | "
            f"Lingue: {', '.join(r.get('lingue', []))} | "
            f"Ruolo auth: {', '.join(gruppi)} | "
            f"Email: {r.get('email','')}"
        )

    allocations  = db.get_allocations()
    alloc_by_proj = {}
    for a in allocations:
        alloc_by_proj.setdefault(a["progetto_id"], []).append(a)

    res_name_map = {r["id"]: f"{r.get('nome','')} {r.get('cognome','')}" for r in resources}

    lines.append("\n=== PROGETTI ===")
    for p in projects:
        allocs = alloc_by_proj.get(p["id"], [])
        alloc_desc = ", ".join(
            f"{res_name_map.get(a['risorsa_id'], a['risorsa_id'])} {a.get('percentuale','')}%"
            for a in allocs
        )
        lines.append(
            f"- {p.get('nome','')} | Cliente: {p.get('cliente','')} | "
            f"Stato: {p.get('stato','')} | "
            f"Inizio: {p.get('data_inizio','')} | Fine prev.: {p.get('data_fine_prevista','')} | "
            f"Risorse allocate: {len(allocs)}"
            + (f" ({alloc_desc})" if alloc_desc else "")
        )

    lines.append("\n=== OPPORTUNITY ===")
    for o in opportunities:
        slot_desc = []
        for sl in o.get("slot_risorse", []):
            mansione = roles_map.get(sl.get("mansione_id", ""), {})
            slot_desc.append(f"{mansione.get('nome', sl.get('mansione_id','?'))} {sl.get('percentuale_allocazione','')}%")
        skill_req = []
        for sk in o.get("skill_richieste", []):
            nome = skills_map.get(sk.get("skill_id", ""), sk.get("skill_id", ""))
            skill_req.append(f"{nome} lv.>={sk.get('livello_minimo','?')}")
        lines.append(
            f"- {o.get('titolo','')} | Cliente: {o.get('cliente','')} | "
            f"Stato: {o.get('stato','')} | "
            f"Inizio: {o.get('data_inizio','')} | Fine prev.: {o.get('data_fine_prevista','')} | "
            f"Slot: {'; '.join(slot_desc) if slot_desc else 'nessuno'} | "
            f"Skills richieste: {', '.join(skill_req) if skill_req else 'nessuna'}"
        )

    return "\n".join(lines)


def ask(question: str) -> str:
    context = _build_context()
    user_message = f"Contesto dati StaffMatch:\n{context}\n\nDomanda: {question}"
    return ai_service.call_claude(SYSTEM_PROMPT, user_message, max_tokens=1024)
