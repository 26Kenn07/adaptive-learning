from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from sqlalchemy import Column, PickleType, Boolean, ForeignKey, Integer, String, DateTime, Enum, Text, ARRAY, Float

from app.database.database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Role(PyEnum):
    USER = 'user'
    ADMIN = 'admin'


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(Role), default=Role.USER)
    weak_topics_ids = Column(ARRAY(Integer), nullable=True)
    strong_topics_ids = Column(ARRAY(Integer), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    scores = relationship("Scores", backref="user")
    
    def verify_password(self, password: str):
        return pwd_context.verify(password, self.password_hash)


    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)


class Subjects(Base):
    __tablename__ = 'subjects'
    
    id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String, nullable=False, index=True, unique=True)
    

    topics = relationship("Topics", backref="subject")


class Topics(Base):
    __tablename__ = 'topics'
    
    id = Column(Integer, primary_key=True, index=True)
    topic_name = Column(String, nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    description = Column(Text, nullable=True)
    

    questions = relationship("Questions", backref="related_topic")


class Questions(Base):
    __tablename__ = 'questions'
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False) 
    question = Column(Text, nullable=False)
    options = Column(PickleType, nullable=False)
    explanation = Column(Text, nullable=True)
    user_attempted = Column(ARRAY(Integer), nullable=False, default=[])
    

    topic = relationship("Topics", backref="related_questions")


class Scores(Base):
    __tablename__ = 'scores'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)  
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)      
    score = Column(Float, nullable=False)  
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    

    subject = relationship("Subjects", backref="scores")
    topic = relationship("Topics", backref="scores")


class Resume(Base):
    __tablename__ = 'resume_details'
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(100), index=True, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Integer, nullable=False, default=0)
    location = Column(String(500), index=True, nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    resume_results = Column(Text, index=True, nullable=False)