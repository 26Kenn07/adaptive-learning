from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

from app.database.models import Questions
from app.utils.return_message import Success, Failed

async def add_question(question, db):
    try:
        existing_question = db.query(Questions).filter(
            Questions.question == question.question,
            Questions.topic_id == question.topic_id
        ).first()

        if existing_question:
            return Failed(status_code=status.HTTP_409_CONFLICT, detail="A question with the same content already exists for this topic.")

        new_question = Questions(
            topic_id=question.topic_id,
            question=question.question,
            options=question.options,
            explanation=question.explanation,
            user_attempted=question.user_attempted
        )
        db.add(new_question)
        db.commit()
        db.refresh(new_question)
        return Success(message="Question added successfully", data={"question": new_question})
    
    except SQLAlchemyError as e:
        db.rollback()
        return Failed(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=e)
