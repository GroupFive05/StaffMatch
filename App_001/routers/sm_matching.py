"""
Router temporaneo per il test del nuovo modello dati (SM_*, Valerio/GroupFive05).
NOTA: nessuna autenticazione richiesta — solo per test interno su ambiente -dev.
"""
from fastapi import APIRouter, Depends, HTTPException
from services.db import sm_get_risorse, sm_get_opportunities, sm_match_score, sm_get_risorse_v2, sm_get_resource_form_catalogs,sm_create_resource_v2,sm_get_dashboard_v2,sm_get_staffing_management_v2,sm_get_matching_context,sm_run_matching_ai,sm_get_data_entry_catalogs,sm_create_contract,sm_create_opportunity,sm_create_osr
from services import practice_alerts
from services.match_service import (
    suggest_matching_weights,
    generate_resource_selection_rationale,
)
from services.auth_service import is_manager_or_admin
from models.schemas import (
    ContractCreate,
    OpportunityCreate,
    OSRCreate,
    ResourceV2Create, 
    MatchingAIRequest,
    MatchingWeightsSuggestionRequest,
    ResourceSelectionRationaleRequest,
)
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
@router.get("/risorse-v2")
def get_risorse_v2():
    return sm_get_risorse_v2()
@router.get("/resource-form-catalogs")
def get_resource_form_catalogs():
    return sm_get_resource_form_catalogs()
@router.post("/risorse-v2")
def create_resource_v2(payload: ResourceV2Create):
    try:
        return sm_create_resource_v2(
            payload.model_dump()
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante la creazione della risorsa: {str(exc)}"
        )
@router.get("/dashboard-v2")
def get_dashboard_v2():
    return sm_get_dashboard_v2()        
    
@router.get("/staffing-management-v2")
def get_staffing_management_v2():
    return sm_get_staffing_management_v2()    

@router.get("/practice-alerts")
def get_practice_alerts(days: int = 30):
    return practice_alerts.build_practice_alerts(
        expiry_days=max(1, min(days, 365))
    )

@router.get("/matching-context")
def get_matching_context():
    return sm_get_matching_context()

@router.post("/matching")
def run_matching_ai(payload: MatchingAIRequest):
    try:
        return sm_run_matching_ai(
            payload.model_dump()
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Matching error: {str(exc)}"
        )
@router.post("/matching/suggest-weights")
def suggest_weights(
    payload: MatchingWeightsSuggestionRequest
):
    try:
        return suggest_matching_weights(
            payload.model_dump()
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to generate AI weight suggestion: "
                f"{str(exc)}"
            )
        )

@router.post("/matching/selection-rationale")
def selection_rationale(
    payload: ResourceSelectionRationaleRequest
):
    try:
        return generate_resource_selection_rationale(
            payload.model_dump()
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to generate selection rationale: "
                f"{str(exc)}"
            )
        )


# ── DATA ENTRY (Practice Hub) — richiede ruolo Manager/Executive/Administrator ──

@router.get("/data-entry-catalogs")
def get_data_entry_catalogs(user: dict = Depends(is_manager_or_admin)):
    return sm_get_data_entry_catalogs()


def _create_with_validation(creator, payload, label):
    try:
        return creator(payload.model_dump())

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"{label} creation error: {str(exc)}"
        )


@router.post("/contracts", status_code=201)
def create_contract(payload: ContractCreate, user: dict = Depends(is_manager_or_admin)):
    return _create_with_validation(sm_create_contract, payload, "Contract")


@router.post("/opportunities", status_code=201)
def create_opportunity(payload: OpportunityCreate, user: dict = Depends(is_manager_or_admin)):
    return _create_with_validation(sm_create_opportunity, payload, "Opportunity")


@router.post("/osr", status_code=201)
def create_osr(payload: OSRCreate, user: dict = Depends(is_manager_or_admin)):
    return _create_with_validation(sm_create_osr, payload, "OSR")
