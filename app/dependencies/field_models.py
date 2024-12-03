from typing import List, Dict
from pydantic import BaseModel, conlist, EmailStr

class UserCreate(BaseModel):
    user_name: str
    email: EmailStr
    password: str

class Add_Subject(BaseModel):
    subject_name : str
    
class Add_Topic(BaseModel):
    topic_name : str
    subject_id : int
    description : str

class Add_Question(BaseModel):
    topic_id: int
    question: str
    options: Dict[str, bool]  
    explanation: str = None  
    user_attempted: List[int] = []

    class Config:
        schema_extra = {
            "example": {
                "topic_id": 1,
                "question": "What is the capital of France?",
                "options": {
                    "Paris": True,
                    "Berlin": False,
                    "Madrid": False,
                    "Rome": False
                },
                "explanation": "Paris is the capital city of France.",
                "user_attempted": []
            }
        }
