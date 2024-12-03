from fastapi import status

from app.database.models import Subjects
from app.utils.return_message import Success, Failed

async def add_subject(subject, db):
    new_subject = Subjects(subject_name=subject.subject_name)
    
    existing_subject = db.query(Subjects).filter(Subjects.subject_name == subject.subject_name).first()
    if existing_subject:
        return Failed(status_code=status.HTTP_409_CONFLICT, detail="Subject already exists.")
    
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return Success(message="Subject added successfully", data={'subject': new_subject})