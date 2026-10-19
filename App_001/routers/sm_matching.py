"""
Router temporaneo per il test del nuovo modello dati (SM_*, Valerio/GroupFive05).
NOTA: nessuna autenticazione richiesta — solo per test interno su ambiente -dev.
"""
from fastapi import APIRouter, HTTPException
from services.db import sm_get_risorse, sm_get_opportunities, sm_match_score

router = APIRouter(prefix="/sm", tags=["sm-matching-test"])


@router.get("/opportunities")
def sm_list_opportunities():
    opps = sm_get_opportunities()
    return [
        {
            "opportunity_id": o["opportunity_id"],
            "titolo": o["titolo"],
            "main_tech_cluster": o["main_tech_cluster"],
            "cliente": o["cliente"],
        }
        for o in opps
    ]


@router.get("/match/{opportunity_id}")
def sm_run_match(opportunity_id: str):
    opps = sm_get_opportunities()
    opp = next((o for o in opps if o["opportunity_id"] == opportunity_id), None)
    if not opp:
        raise HTTPException(status_code=404, detail=f"Opportunity {opportunity_id} non trovata")

    risorse = sm_get_risorse()
    risultati = sorted(
        [sm_match_score(r, opp) for r in risorse],
        key=lambda x: -x["score"]
    )
    return {
        "opportunity": {
            "id": opp["opportunity_id"],
            "titolo": opp["titolo"],
            "main_tech_cluster": opp["main_tech_cluster"],
            "cliente": opp["cliente"],
        },
        "candidati": risultati[:10],
    }
