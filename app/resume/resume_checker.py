from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, UploadFile, File


from app.database.models import User
from app.dependencies.db_dependencies import get_db
from app.dependencies.admin_dependencies import get_current_user
from app.controllers.resume_helper import resume_upload

router = APIRouter(prefix="/resume", tags=["resume"])

@router.post("/resume_review")
async def resume_upload_endpoint(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await resume_upload(file, db, current_user)