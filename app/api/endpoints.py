from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from omegaconf import DictConfig
from typing import Annotated

from app.services.auth_service import get_current_user
from model.llama import LlamaModel
from app.schemas.request import SummarizationRequest
from app.schemas.response import SummarizationResponse

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

llama_model = None


def initialize_model(cfg: DictConfig):
    global llama_model
    llama_model = LlamaModel(
        model_path=cfg.model.path,
        max_length=cfg.model.max_length,
        temperature=cfg.model.temperature,
        default_promt=cfg.model.default_promt
    )

@router.post("/summarize", response_model=SummarizationResponse)
async def summarize(request: SummarizationRequest, token: Annotated[str | None, Depends(oauth2_scheme)]):
    """This endpoint takes in a text request and returns a summarized version of the text.
    Args:
        request (SummarizationRequest): The text to be summarized.
        token (str | None): The authentication token.

    Returns:
        SummarizationResponse: The summarized text.

    Raises:
        HTTPException: If the user is not logged in or if the model is not loaded.
    """
    try:
        user = await get_current_user(token)
    except:
        raise HTTPException(status_code=401, detail="Not log in")

    if llama_model is None:
        raise HTTPException(status_code=500, detail="Model is not loaded")

    summary = llama_model.summarize(request.text)
    return SummarizationResponse(summary=summary)
