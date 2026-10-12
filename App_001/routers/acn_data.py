from fastapi import APIRouter, Depends
from services import db, auth_service

router = APIRouter(prefix="/acn", tags=["ACN Data"])

@router.get("/risorse")
def list_risorse_acn(current_user: dict = Depends(auth_service.get_current_user)):
    return db.get_risorse_acn()

@router.get("/cert-catalog")
def list_cert_catalog(current_user: dict = Depends(auth_service.get_current_user)):
    return db.get_cert_catalog()

@router.get("/contracts")
def list_contracts(current_user: dict = Depends(auth_service.get_current_user)):
    return db.get_contracts()

@router.get("/milestones")
def list_milestones(current_user: dict = Depends(auth_service.get_current_user)):
    return db.get_milestones()

@router.get("/osr")
def list_osr(current_user: dict = Depends(auth_service.get_current_user)):
    return db.get_osr()