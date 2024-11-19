from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
import asyncio

from omegaconf import DictConfig
import hydra

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api import auth, endpoints
from app.database import database
from app.services.auth_service import set_oauth2

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request, token: str | None = Depends(oauth2_scheme)):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@hydra.main(version_base=None, config_path="../config", config_name="config")
def init_app(cfg: DictConfig):
    """
    Initialize the application with Hydra configuration.

    This function initializes the app by performing several tasks:
    - Initializing the model using endpoints.initialize_model() based on the provided config.
    - Setting up OAuth2 authentication using set_oauth2().
    - Initializing the database asynchronously with database.init_db().
    - Including the routers for endpoints and auth in the FastAPI application.
    - Running the FastAPI app using Uvicorn with host and port configured in the Hydra config.

    Args:
        cfg (DictConfig): The Hydra configuration dictionary.
    """
    endpoints.initialize_model(cfg)
    set_oauth2(cfg)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(database.init_db())

    app.include_router(endpoints.router)
    app.include_router(auth.router)

    import uvicorn
    uvicorn.run(app, host=cfg.server.host, port=int(cfg.server.port))

if __name__ == "__main__":
    init_app()
