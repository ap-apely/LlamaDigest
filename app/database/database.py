from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from rich import print as rprint

from app.schemas.request import UserCreate

DATABASE_URL = "sqlite+aiosqlite:///./digest.db"  

engine = create_async_engine(DATABASE_URL, echo=True)

Base = declarative_base()

def SessionLocal():
    SessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    return SessionLocal

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

"""
This function fetches a user from the database based on their username.

Parameters:
    db_session (AsyncSession): The asynchronous session object used to interact with the database.
    username (str): The username of the user to retrieve.

Returns:
    User: The retrieved user object, or None if no user is found.
"""
async def get_user(db_session: AsyncSession, username: str):
    async with db_session() as session:
        result = await session.execute(select(User).filter(User.username == username))
        print(result)
        user = result.scalars().first()
        return user

"""
Creates a new user in the database.

This function takes in a `UserCreate` object and uses it to create a new `User`
instance, which is then added to the database session and committed.
"""
async def create_user(db_session: AsyncSession, user_data: UserCreate):
    async with db_session() as session:
        user = User(username=user_data.username, password=user_data.password)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

async def init_db():
    rprint("[D]Init database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        
