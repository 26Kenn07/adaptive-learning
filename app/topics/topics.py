from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends


from app.controllers.topic_helper import add_topic
from app.dependencies.field_models import Add_Topic
from app.dependencies.db_dependencies import get_db
from app.dependencies.admin_dependencies import admin_required

router = APIRouter(prefix="/topics", tags=["topics"])

@router.post("/add_topics", dependencies=[Depends(admin_required)])
async def add_topic_endpoint(topic: Add_Topic, db: Session = Depends(get_db)):
    return await add_topic(topic=topic, db=db)