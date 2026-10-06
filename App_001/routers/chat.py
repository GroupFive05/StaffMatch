from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services import auth_service, chat_service

router = APIRouter(prefix="/chat", tags=["Chatbot"])


class ChatRequest(BaseModel):
    question: str


@router.post("/")
def chat(
    body: ChatRequest,
    current_user: dict = Depends(auth_service.get_current_user),
):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="La domanda non può essere vuota.")
    try:
        answer = chat_service.ask(body.question.strip())
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
