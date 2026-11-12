from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from services import auth_service, db

router = APIRouter(prefix="/access", tags=["Accessi"])


class AccessCreate(BaseModel):
    eid: int
    group: str
    password: str = Field(min_length=6)


class GroupUpdate(BaseModel):
    group: str


class ActiveUpdate(BaseModel):
    is_active: bool


class PasswordReset(BaseModel):
    password: str = Field(min_length=6)


def _check_group(group: str):
    if group not in db.ACCESS_GROUPS:
        raise HTTPException(status_code=400, detail=f"Gruppo non valido: {group}")


def _get_access_or_404(access_email: str) -> dict:
    row = next((a for a in db.sm_list_access() if a["access_email"].lower() == access_email.lower()), None)
    if not row:
        raise HTTPException(status_code=404, detail="Accesso non trovato")
    return row


def _other_active_admins(access_email: str) -> int:
    return sum(
        1 for a in db.sm_list_access()
        if a["is_active"] and a["access_group"] == "Administrator"
        and a["access_email"].lower() != access_email.lower()
    )


def _guard_last_admin(row: dict):
    # evita di restare senza amministratori attivi
    if row["access_group"] == "Administrator" and row["is_active"] and not _other_active_admins(row["access_email"]):
        raise HTTPException(status_code=400, detail="Deve restare almeno un Administrator attivo")


@router.get("/")
def list_access(current_user: dict = Depends(auth_service.is_admin)):
    return [{k: v for k, v in a.items() if k != "password_hash"} for a in db.sm_list_access()]


@router.get("/available-resources")
def available_resources(current_user: dict = Depends(auth_service.is_admin)):
    return db.sm_list_resources_without_access()


@router.post("/", status_code=201)
def create_access(body: AccessCreate, current_user: dict = Depends(auth_service.is_admin)):
    _check_group(body.group)
    try:
        res = db.sm_create_access(body.eid, body.group, auth_service.hash_password(body.password))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"eid": res["eid"], "email": res["email"], "group": body.group}


@router.patch("/{access_email}/group")
def update_group(access_email: str, body: GroupUpdate, current_user: dict = Depends(auth_service.is_admin)):
    _check_group(body.group)
    row = _get_access_or_404(access_email)
    if body.group != "Administrator":
        _guard_last_admin(row)
    db.sm_update_access(row["access_email"], access_group=body.group)
    return {"email": row["email"], "group": body.group}


@router.patch("/{access_email}/active")
def update_active(access_email: str, body: ActiveUpdate, current_user: dict = Depends(auth_service.is_admin)):
    row = _get_access_or_404(access_email)
    if not body.is_active:
        _guard_last_admin(row)
        if row["access_email"].lower() == current_user["access_email"].lower():
            raise HTTPException(status_code=400, detail="Non puoi disattivare il tuo stesso accesso")
    db.sm_update_access(row["access_email"], is_active=body.is_active)
    return {"email": row["email"], "is_active": body.is_active}


@router.post("/{access_email}/reset-password")
def reset_password(access_email: str, body: PasswordReset, current_user: dict = Depends(auth_service.is_admin)):
    row = _get_access_or_404(access_email)
    db.sm_update_access(row["access_email"], password_hash=auth_service.hash_password(body.password))
    return {"email": row["email"]}
