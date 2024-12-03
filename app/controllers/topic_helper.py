from fastapi import status

from app.database.models import Topics
from app.utils.return_message import Success, Failed

async def add_topic(topic, db):
    existing_topic = db.query(Topics).filter(
        Topics.topic_name == topic.topic_name,
        Topics.subject_id == topic.subject_id
    ).first()
    
    if existing_topic:
        return Failed(status_code=status.HTTP_409_CONFLICT, detail="Topic with this name already exists for the given subject")
    
    new_topic = Topics(topic_name=topic.topic_name, subject_id=topic.subject_id, description=topic.description)
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)
    
    return Success(message="Topic added successfully", data={'topic': new_topic})