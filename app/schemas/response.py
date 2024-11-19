from pydantic import BaseModel

class SummarizationResponse(BaseModel):
    summary: str

class Token(BaseModel):
    access_token: str
    token_type: str