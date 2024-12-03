from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends


from app.dependencies.db_dependencies import get_db
from app.dependencies.field_models import Add_Subject
from app.controllers.subject_helper import add_subject
from app.dependencies.admin_dependencies import admin_required

router = APIRouter(prefix="/subjects", tags=["subjects"])

@router.post("/add_subjects", dependencies=[Depends(admin_required)])
async def add_subject_endpoint(subject: Add_Subject, db: Session = Depends(get_db)):
    return await add_subject(subject=subject, db=db)
    