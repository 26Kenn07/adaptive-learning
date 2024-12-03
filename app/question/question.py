from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends


from app.dependencies.db_dependencies import get_db
from app.dependencies.field_models import Add_Question
from app.controllers.question_helper import add_question
from app.dependencies.admin_dependencies import admin_required

router = APIRouter(prefix="/question", tags=["question"])

@router.post("/add_question", dependencies=[Depends(admin_required)])
async def add_question_endpoint(question: Add_Question, db: Session = Depends(get_db)):
    return await add_question(question=question, db=db)
    