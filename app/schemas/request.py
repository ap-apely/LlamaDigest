from pydantic import BaseModel, Field

class SummarizationRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Текст для реферирования")

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str