from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services import auth_service, notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class StaffingRequestMail(BaseModel):
    subject: str
    body: str


@router.post("/staffing-request")
def staffing_request(
    payload: StaffingRequestMail,
    current_user: dict = Depends(auth_service.is_manager_or_admin),
):
    if not payload.subject.strip() or not payload.body.strip():
        raise HTTPException(status_code=400, detail="Subject and body are required.")
    try:
        notification_service.send_staffing_request(payload.subject.strip(), payload.body)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Notification failed: {e}")
    return {"status": "sent"}
