import os
from dotenv import load_dotenv
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from app.database.models import User, Role
from app.dependencies.db_dependencies import get_db
from app.utils.return_message import Failed

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authentication/login")

ALGORITHM = os.environ['ALGORITHM']
SECRET_KEY = os.environ['SECRET_KEY']

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        if user_id is None or role is None:
            return Failed(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
        
        return {"id": user_id, "role": Role(role)}
    
    except JWTError:
        return Failed(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT Error")


def admin_required(current_user: User = Depends(get_current_user)):
    if current_user['role'] != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the necessary permissions",
        )
    return current_user
