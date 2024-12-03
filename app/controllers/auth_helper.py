import os
from jose import jwt
from fastapi import status
from dotenv import load_dotenv
from datetime import datetime, timedelta

from app.database.models import User, Role
from app.utils.return_message import Success, Failed

load_dotenv()

SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = os.environ['ALGORITHM']

def create_access_token(user_id: int, role: Role, expires_delta: timedelta):
    encode = {"id": user_id, "role": role.value}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    print(token)
    return token

async def signup(user, db):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        return Failed(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    
    new_user = User(
        user_name=user.user_name,
        email=user.email,
    )
    new_user.set_password(user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return Success(message= "User created successfully", data=new_user)

async def login(form_data, db):
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not user.verify_password(form_data.password):
        return Failed(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    
    access_token_expires = timedelta(days=1)
    access_token = create_access_token(
        user_id=user.id, role=user.role, expires_delta=access_token_expires
    )
    print(access_token)
    return {"access_token": access_token, "token_type": "bearer"}

async def create_admin(db):
    admin_user = User(
            user_name="admin",
            email="admin@example.com",
            role=Role.ADMIN, 
            is_deleted=False,
            created_at=datetime.utcnow()
        )
    
    admin_user.set_password("Admin@123")
    
    db.add(admin_user)
    db.commit()
    print("Default admin created with username: 'admin' and password: 'adminpassword'")