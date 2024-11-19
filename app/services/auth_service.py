from datetime import datetime, timedelta
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from pydantic import BaseModel
from sqlalchemy.orm import Session

from omegaconf import DictConfig

from database.database import get_user, SessionLocal

from rich import print as rprint

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def set_oauth2(cfg: DictConfig):
    global SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
    SECRET_KEY = cfg.oauth2.secretKey
    ALGORITHM = cfg.oauth2.algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES = cfg.oauth2.accessTokenExpireMinutes

class TokenData(BaseModel):
    username: str

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db_session: Session = Depends(SessionLocal)):
    """
    Retrieves the current user based on the provided token.

    Args:
        token (str): The access token.
        db_session (Session): The database session.
        
    Returns:
        User: The current user object if valid, otherwise raises an HTTPException.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(db_session=db_session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload if payload.get("sub") else None
    except:
        print("Error while decode")