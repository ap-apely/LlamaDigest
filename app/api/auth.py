from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.schemas.request import UserCreate, UserLogin
from app.schemas.response import Token
from app.services.auth_service import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.database.database import get_user, create_user, SessionLocal

from rich import print as rprint

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=Token)
async def register(user_data:UserLogin, db_session: Session = Depends(SessionLocal)):
    """Register a new user.

    Register a new user by creating an account with the provided username and password.
    
    - **user_data**: The user data to be registered. Must contain `username` and `password`.

    - **db_session**: A SQLAlchemy session object used for database operations.

    Returns:
        Token: An access token that can be used to authenticate subsequent requests.
    """

    user = await get_user(db_session, user_data.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = get_password_hash(user_data.password)
    await create_user(db_session, UserCreate(username=user_data.username, password=hashed_password))
    access_token = create_access_token(data={"sub": user_data.username})
    return Token(access_token=access_token, token_type='bearer')

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db_session: Session = Depends(SessionLocal)):
    """Get an access token for a registered user.

    Login into the system using the provided username and password.
    
    - **user_data**: The user data to be logged in. Must contain `username` and `password`.

    Returns:
        Token: An access token that can be used to authenticate subsequent requests.
    """
    user = await get_user(db_session, user_data.username)
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user_data.username})
    return Token(access_token=access_token, token_type='bearer')