from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .db import engine, Base
from .routers.contracts import router as contracts_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Car Contract AI Backend")

# Static & templates
app.mount("/static", StaticFiles(directory="backend/static"), name="static")
templates = Jinja2Templates(directory="backend/templates")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

app.include_router(contracts_router)
