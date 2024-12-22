from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import auth
from app.topics import topics
from app.subjects import subjects
from app.question import question
from app.resume import resume_checker
from app.database.database import engine
from app.database.models import Base, User, Role
from app.dependencies.db_dependencies import get_db
from app.controllers.auth_helper import create_admin

app = FastAPI()
app.include_router(auth.router)
app.include_router(topics.router)
app.include_router(subjects.router)
app.include_router(question.router)
app.include_router(resume_checker.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def create_default_admin():
    db = next(get_db())
    admin_exists = db.query(User).filter(User.role == Role.ADMIN).first()
    if not admin_exists:
        return await create_admin(db)
    
@app.get("/")
async def health_check():
    return {"status": "healthy"}





# from sqlalchemy.orm import Session
# from app.database.models import Questions

# def print_question_options_from_db(question_id: int, db: Session):

#     question_record = db.query(Questions).filter(Questions.id == question_id).first()

#     if not question_record:
#         print("Question not found.")
#         return

#     print(f"Question: {question_record.question}")
#     print("Options:")
#     for option, is_correct in question_record.options.items():
#         correctness = "Correct" if is_correct else "Incorrect"
#         print(f"- {option}: {correctness}")
        
# from fastapi import Depends
# from sqlalchemy.orm import Session


# @app.get("/question/{question_id}/options")
# def get_question_options(question_id: int, db: Session = Depends(get_db)):
#     print_question_options_from_db(question_id, db)
#     return {"message": "Options printed to the console"}
