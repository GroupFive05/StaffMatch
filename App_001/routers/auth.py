from fastapi import APIRouter, HTTPException, Depends
from models.schemas import LoginRequest, TokenResponse, ChangePasswordRequest
from services import auth_service, db

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    user = auth_service.authenticate_user(body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    gruppi = [user["access_group"]] if user.get("access_group") else []
    token = auth_service.create_token({"sub": user["email"], "gruppi": gruppi})
    return TokenResponse(
        access_token=token,
        nome=user["nome"],
        cognome=user["cognome"],
        gruppi=gruppi,
    )

@router.post("/change-password")
def change_password(
    body: ChangePasswordRequest,
    current_user: dict = Depends(auth_service.get_current_user),
):
    if not auth_service.authenticate_user(current_user["email"], body.password_attuale):
        raise HTTPException(status_code=400, detail="Password attuale non corretta")
    db.sm_update_access(
        current_user["access_email"],
        password_hash=auth_service.hash_password(body.nuova_password),
    )
    return {"message": "Password aggiornata con successo"}

@router.get("/me")
def me(current_user: dict = Depends(auth_service.get_current_user)):
    return {
        "id": current_user["id"],
        "nome": current_user["nome"],
        "cognome": current_user["cognome"],
        "email": current_user["email"],
        "ruolo": current_user["ruolo"],
        "gruppi": current_user["gruppi"],
    }
