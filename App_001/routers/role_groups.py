from fastapi import APIRouter, HTTPException, Depends
from services import auth_service, db

router = APIRouter(prefix="/roles", tags=["Ruoli Autorizzativi"])

@router.get("/")
def list_role_groups(current_user: dict = Depends(auth_service.get_current_user)):
    return [{"id": name, "nome": name} for name in db.ACCESS_GROUPS]
