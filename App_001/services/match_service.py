import json
import uuid
from . import db, ai_service

SYSTEM_PROMPT = """Sei un esperto di staffing per progetti SAP/IT di Accenture Italy.
Ricevi i dettagli di uno slot risorsa di un'opportunità e una lista di candidati pre-filtrati.
Devi restituire SOLO un JSON valido (senza markdown, senza ```json) con questa struttura:
{
  "candidates": [
    {
      "risorsa_id": "R001",
      "score": 85,
      "motivazione": "Spiegazione concisa in italiano (max 2 frasi)"
    }
  ]
}
Ordina per score decrescente. Includi solo candidati con score >= 40.
Score 0-100: match skill richieste (50%), disponibilità vs % richiesta (30%), aderenza mansione/seniority (20%)."""

WEIGHTS_SYSTEM_PROMPT = """
You are an expert workforce staffing advisor for SAP and Data & AI projects.

Your task is to suggest relative weights for the matching criteria selected
by the user.

You receive:
- Opportunity context
- Requested role
- Requested staffing period
- Selected skills
- Selected certifications
- Selected languages

Return ONLY valid JSON, without markdown or additional text.

Required structure:

{
  "weights": {
    "skill:Python": 40,
    "certification:CERT-001": 35,
    "language:ENG": 25
  },
  "rationale": "Concise explanation of the proposed relative importance."
}

Rules:
- Return exactly the criterion keys received in the input.
- Do not introduce new criteria.
- Every weight must be a number between 0 and 100.
- The sum of the returned weights must equal 100.
- Assign higher weights to the criteria most relevant to the Opportunity,
  technology, functional area and requested role.
- The rationale must be concise and written in English.
"""

def run_matching(opportunity_id: str) -> list:
    opportunities = db.get_opportunities()
    opp = next((o for o in opportunities if o["id"] == opportunity_id), None)
    if not opp:
        raise ValueError(f"Opportunità {opportunity_id} non trovata")

    resources = db.get_resources()
    skills_map = {s["id"]: s for s in db.get_skills()}
    roles_map  = {r["id"]: r for r in db.get_roles()}

    skill_names = [
        {"nome": skills_map[s["skill_id"]]["nome"], "livello_minimo": s["livello_minimo"]}
        for s in opp.get("skill_richieste", []) if s["skill_id"] in skills_map
    ]

    all_results = []

    for slot_idx, slot in enumerate(opp.get("slot_risorse", [])):
        mansione_id  = slot["mansione_id"]
        perc_req     = slot["percentuale_allocazione"]
        mansione     = roles_map.get(mansione_id, {})
        mansione_nome = mansione.get("nome", mansione_id)
        seniority_target = mansione.get("seniority", "")

        candidates = []
        for r in resources:
            if r.get("id") == "R000":
                continue
            disp = db.disponibilita_risorsa(r["id"])
            if disp < perc_req:
                continue
            ruolo = roles_map.get(r["ruolo_id"], {})
            candidates.append({
                "id": r["id"],
                "nome": f"{r['nome']} {r['cognome']}",
                "mansione": ruolo.get("nome", ""),
                "seniority": ruolo.get("seniority", ""),
                "disponibilita": disp,
                "skills": [
                    {"nome": skills_map[s["skill_id"]]["nome"], "livello": s["livello"]}
                    for s in r.get("skill_ids", []) if s["skill_id"] in skills_map
                ],
                "lingue": r.get("lingue", []),
            })

        if not candidates:
            continue

        user_message = f"""
Opportunità: {opp['titolo']}
Cliente: {opp['cliente']}
Descrizione: {opp['descrizione']}
Skills richieste dal progetto: {json.dumps(skill_names, ensure_ascii=False)}

Slot {slot_idx + 1}: {mansione_nome} (Seniority target: {seniority_target})
Allocazione richiesta: {perc_req}%

Candidati disponibili:
{json.dumps(candidates, ensure_ascii=False, indent=2)}
"""

        raw = ai_service.call_claude(SYSTEM_PROMPT, user_message)
        result = json.loads(raw)

        for item in result.get("candidates", []):
            all_results.append({
                "id": str(uuid.uuid4()),
                "opportunity_id": opportunity_id,
                "slot_index": slot_idx,
                "risorsa_id": item["risorsa_id"],
                "score": item["score"],
                "motivazione": item["motivazione"],
                "stato": "Proposed",
            })

    existing = [m for m in db.get_match_results() if m["opportunity_id"] != opportunity_id]
    db.save_match_results(existing + all_results)
    return all_results

def suggest_matching_weights(payload: dict) -> dict:
    """
    Uses Claude through the existing SAP AI Core client to suggest
    normalized weights for the selected matching criteria.
    """

    opportunity = payload.get("opportunity") or {}
    role = (payload.get("role") or "").strip()
    start_date = payload.get("start_date")
    end_date = payload.get("end_date")

    selected_skills = list(
        payload.get("skills") or []
    )

    selected_certifications = list(
        payload.get("certifications") or []
    )

    selected_languages = list(
        payload.get("languages") or []
    )

    criterion_keys = []

    for skill in selected_skills:
        criterion_keys.append(
            f"skill:{skill}"
        )

    for certification_id in selected_certifications:
        criterion_keys.append(
            f"certification:{certification_id}"
        )

    for language in selected_languages:
        criterion_keys.append(
            f"language:{language}"
        )

    if not criterion_keys:
        raise ValueError(
            "At least one matching criterion is required."
        )

    user_message = f"""
Opportunity:
{json.dumps(opportunity, ensure_ascii=False, indent=2)}

Requested role:
{role}

Requested period:
{start_date} to {end_date}

Selected criterion keys:
{json.dumps(criterion_keys, ensure_ascii=False, indent=2)}
"""

    raw_response = ai_service.call_claude(
        WEIGHTS_SYSTEM_PROMPT,
        user_message
    )

    # Claude should return pure JSON, but make parsing resilient
    # to markdown fences or explanatory text.
    cleaned_response = (
        raw_response
        or ""
    ).strip()

    if cleaned_response.startswith("```"):
        cleaned_response = cleaned_response.replace(
            "```json",
            "",
            1
        ).replace(
            "```",
            ""
        ).strip()

    json_start = cleaned_response.find("{")
    json_end = cleaned_response.rfind("}")

    if json_start == -1 or json_end == -1:
        raise ValueError(
            "The AI weight suggestion did not contain a JSON object."
        )

    cleaned_response = cleaned_response[
        json_start:json_end + 1
    ]

    try:
        suggestion = json.loads(
            cleaned_response
        )

    except json.JSONDecodeError as exc:
        raise ValueError(
            "The AI weight suggestion returned invalid JSON."
        ) from exc

    suggested_weights = suggestion.get(
        "weights"
    ) or {}

    # Accept only criteria selected by the user.
    clean_weights = {}

    for criterion_key in criterion_keys:
        try:
            value = float(
                suggested_weights.get(
                    criterion_key,
                    0
                )
            )

        except (TypeError, ValueError):
            value = 0

        clean_weights[criterion_key] = max(
            0,
            min(100, value)
        )

    total_weight = sum(
        clean_weights.values()
    )

    # Defensive fallback if Claude returns all weights at zero.
    if total_weight == 0:
        uniform_weight = (
            100 / len(criterion_keys)
        )

        clean_weights = {
            criterion_key: uniform_weight
            for criterion_key in criterion_keys
        }

    else:
        clean_weights = {
            criterion_key: (
                value
                / total_weight
                * 100
            )
            for criterion_key, value
            in clean_weights.items()
        }

    return {
        "weights": {
            criterion_key: round(
                value,
                2
            )
            for criterion_key, value
            in clean_weights.items()
        },

        "rationale": (
            suggestion.get("rationale")
            or "Weights suggested from the selected staffing context."
        )
    }    
