import re
from . import db, ai_service

SYSTEM_PROMPT = """
Sei il Practice Advisor di StaffMatch, esperto di staffing per progetti
SAP, Data e AI.

Hai accesso ai dati correnti del modello StaffMatch V2:
risorse, level, esperienza, skill, certificazioni, lingue,
disponibilità, current assignments, OSR, opportunity,
contratti, clienti e manager.

Lo stato operativo delle OSR non deriva mai dal campo STATO del database.

Usa esclusivamente lo stato calcolato da DATAFINE:
- Closed: DATAFINE precedente a oggi
- Rolling-off: DATAFINE compresa fra oggi e i prossimi 3 mesi
- Active: DATAFINE successiva alla soglia dei prossimi 3 mesi

La disponibilità delle risorse deriva dalle OSR e dalle relative
percentuali di allocazione, non da campi legacy.

Rispondi nella stessa lingua utilizzata dall'utente:
- se la domanda è in italiano, rispondi in italiano;
- se la domanda è in inglese, rispondi in inglese;
- se la domanda contiene prevalentemente una delle due lingue, usa quella prevalente.

Mantieni un tono professionale, preciso e conciso.
Basa ogni risposta esclusivamente sui dati presenti nel contesto.

Non inventare risorse, skill, certificazioni, date, percentuali,
clienti, contratti, manager o stati OSR.

Se una risposta non è determinabile dai dati forniti,
dichiara chiaramente che l'informazione non è disponibile.
"""

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

    now = datetime.now().strftime(
        "%A %d %B %Y, ore %H:%M"
    )

    lines = [
        f"=== DATA E ORA CORRENTE ===\n{now}"
    ]

    # Dati V2 reali
    resources = db.sm_get_risorse_v2()
    staffing = db.sm_get_staffing_management_v2()

    osr_rows = staffing.get(
        "osr",
        []
    )

    opportunity_rows = staffing.get(
        "opportunities",
        []
    )

    contract_rows = staffing.get(
        "contracts",
        []
    )

    include_skills = "skills" in categories

    # ── RESOURCES V2 ──────────────────────────────────────────────
    lines.append(
        "\n=== RISORSE STAFFMATCH V2 ==="
    )

    for resource in resources:
        resource_name = (
            f"{resource.get('nome') or ''} "
            f"{resource.get('cognome') or ''}"
        ).strip()

        parts = [
            f"- {resource_name}",
            f"EID: {resource.get('eid')}",
            (
                f"Level: "
                f"{resource.get('level_name') or 'non disponibile'}"
            ),
            (
                f"Esperienza: "
                f"{resource.get('anni_esperienza') or 0} anni"
            ),
            (
                f"Disponibilità attuale: "
                f"{resource.get('disponibilita') or 0}%"
            ),
            (
                f"Allocazione attuale: "
                f"{resource.get('active_allocation') or 0}%"
            ),
            (
                f"Disponibile dal: "
                f"{resource.get('available_from') or 'immediatamente'}"
            ),
            (
                f"Email: "
                f"{resource.get('email') or 'non disponibile'}"
            )
        ]

        # Skill / Certification / Languages
        if include_skills:
            skills = [
                item.get("skill_name")
                for item in resource.get(
                    "skills",
                    []
                )
                if item.get("skill_name")
            ]

            certifications = [
                item.get("nome_cert")
                for item in resource.get(
                    "certifications",
                    []
                )
                if item.get("nome_cert")
            ]

            languages = [
                item.get("language_code")
                for item in resource.get(
                    "languages",
                    []
                )
                if item.get("language_code")
            ]

            parts.append(
                "Skills: "
                + (
                    ", ".join(skills)
                    if skills
                    else "nessuna"
                )
            )

            parts.append(
                "Certificazioni: "
                + (
                    ", ".join(certifications)
                    if certifications
                    else "nessuna"
                )
            )

            parts.append(
                "Lingue: "
                + (
                    ", ".join(languages)
                    if languages
                    else "nessuna"
                )
            )

        # Reference Manager
        managers = []

        for manager in resource.get(
            "managers",
            []
        ):
            manager_name = (
                f"{manager.get('nome') or ''} "
                f"{manager.get('cognome') or ''}"
            ).strip()

            if manager_name:
                managers.append(
                    manager_name
                )

        parts.append(
            "Manager di riferimento: "
            + (
                ", ".join(managers)
                if managers
                else "nessuno"
            )
        )

        # Current Assignments
        assignments = []

        for assignment in resource.get(
            "current_assignments",
            []
        ):
            assignments.append(
                (
                    f"{assignment.get('osr_id') or 'OSR non disponibile'}"
                    f" | Opportunity: "
                    f"{assignment.get('opportunity_title') or 'non disponibile'}"
                    f" | Cliente: "
                    f"{assignment.get('client_name') or 'non disponibile'}"
                    f" | Ruolo: "
                    f"{assignment.get('project_role') or 'non disponibile'}"
                    f" | Allocazione: "
                    f"{assignment.get('allocation_pct') or 0}%"
                    f" | Fine: "
                    f"{assignment.get('end_date') or 'non disponibile'}"
                    f" | Stato calcolato: "
                    f"{assignment.get('osr_status') or 'Unknown'}"
                )
            )

        parts.append(
            "Current assignments: "
            + (
                " ; ".join(assignments)
                if assignments
                else "nessuna OSR corrente"
            )
        )

        lines.append(
            " | ".join(parts)
        )

    # ── OSR V2 ────────────────────────────────────────────────────
    if (
        "projects" in categories
        or "availability" in categories
    ):
        lines.append(
            "\n=== OSR E ASSEGNAZIONI "
            "(STATO CALCOLATO DA DATAFINE) ==="
        )

        for osr in osr_rows:
            resource_name = (
                f"{osr.get('resource_nome') or ''} "
                f"{osr.get('resource_cognome') or ''}"
            ).strip()

            manager_name = (
                f"{osr.get('manager_nome') or ''} "
                f"{osr.get('manager_cognome') or ''}"
            ).strip()

            lines.append(
                (
                    f"- OSR: "
                    f"{osr.get('osr_id')}"
                    f" | Risorsa: "
                    f"{resource_name or osr.get('resource_eid')}"
                    f" | Opportunity: "
                    f"{osr.get('opportunity_title') or osr.get('opportunity_id')}"
                    f" | Cliente: "
                    f"{osr.get('client_name') or 'non disponibile'}"
                    f" | Ruolo: "
                    f"{osr.get('project_role') or 'non disponibile'}"
                    f" | Allocazione: "
                    f"{osr.get('allocation_pct') or 0}%"
                    f" | Inizio: "
                    f"{osr.get('start_date') or 'non disponibile'}"
                    f" | Fine: "
                    f"{osr.get('end_date') or 'non disponibile'}"
                    f" | Stato calcolato: "
                    f"{osr.get('calculated_status') or 'Unknown'}"
                    f" | Manager: "
                    f"{manager_name or 'non disponibile'}"
                )
            )

    # ── OPPORTUNITIES V2 ──────────────────────────────────────────
    if "opportunities" in categories:
        lines.append(
            "\n=== OPPORTUNITY STAFFMATCH V2 ==="
        )

        for opportunity in opportunity_rows:
            lines.append(
                (
                    f"- ID: "
                    f"{opportunity.get('opportunity_id')}"
                    f" | Titolo: "
                    f"{opportunity.get('opportunity_title') or 'non disponibile'}"
                    f" | Cliente: "
                    f"{opportunity.get('client_name') or 'non disponibile'}"
                    f" | Technology: "
                    f"{opportunity.get('main_tech_cluster') or 'non disponibile'}"
                    f" | Functional Area: "
                    f"{opportunity.get('functional_area') or 'non disponibile'}"
                    f" | Stato: "
                    f"{opportunity.get('opportunity_status') or 'non disponibile'}"
                    f" | Inizio: "
                    f"{opportunity.get('start_date') or 'non disponibile'}"
                    f" | Fine: "
                    f"{opportunity.get('end_date') or 'non disponibile'}"
                    f" | Contratto: "
                    f"{opportunity.get('contract_id') or 'non disponibile'}"
                )
            )

    # ── CONTRACTS V2 ──────────────────────────────────────────────
    if (
        "projects" in categories
        or "opportunities" in categories
    ):
        lines.append(
            "\n=== CONTRATTI STAFFMATCH V2 ==="
        )

        for contract in contract_rows:
            manager_name = (
                f"{contract.get('manager_nome') or ''} "
                f"{contract.get('manager_cognome') or ''}"
            ).strip()

            lines.append(
                (
                    f"- ID: "
                    f"{contract.get('contract_id')}"
                    f" | Titolo: "
                    f"{contract.get('contract_title') or 'non disponibile'}"
                    f" | Cliente: "
                    f"{contract.get('client_name') or 'non disponibile'}"
                    f" | Settore: "
                    f"{contract.get('industry_sector') or 'non disponibile'}"
                    f" | Service Group: "
                    f"{contract.get('service_group') or 'non disponibile'}"
                    f" | Stato contratto: "
                    f"{contract.get('contract_status') or 'non disponibile'}"
                    f" | Inizio: "
                    f"{contract.get('start_date') or 'non disponibile'}"
                    f" | Fine: "
                    f"{contract.get('end_date') or 'non disponibile'}"
                    f" | Manager: "
                    f"{manager_name or 'non disponibile'}"
                    f" | Opportunity collegate: "
                    f"{contract.get('opportunity_count') or 0}"
                    f" | OSR collegate: "
                    f"{contract.get('osr_count') or 0}"
                )
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
