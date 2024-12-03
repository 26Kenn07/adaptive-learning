from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.dependencies.db_dependencies import get_db
from app.dependencies.field_models import UserCreate
from app.controllers.auth_helper import signup, login


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(prefix="/authentication", tags=["authentication"])


@router.post("/signup")
async def signup_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    return await signup(user=user, db=db)

@router.post("/login")
async def login_endpoint(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    return await login(form_data=form_data, db=db)
