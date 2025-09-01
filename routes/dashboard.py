from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
import requests

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

DELTA_API = "https://api.testnet.delta.exchange/v2/tickers"

@router.get("/dashboard")
def dashboard(request: Request):
    user = request.cookies.get("user")
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "msg": "Please login first"})
    r = requests.get(DELTA_API).json()
    tickers = r.get("result", [])[:4]
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "tickers": tickers})
