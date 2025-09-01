from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
import requests

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/alerts")
def alert_form(request: Request):
    user_cookie = request.cookies.get("user")
    if not user_cookie:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("alerts.html", {"request": request, "user": user_cookie})

@router.post("/alerts")
def enable_alerts(telegram_token: str = Form(...), telegram_chatid: str = Form(...), db: Session = Depends(get_db), request: Request = None):
    user_cookie = request.cookies.get("user")
    user = db.query(User).filter(User.username == user_cookie).first()
    if user:
        user.telegram_enabled = True
        user.telegram_token = telegram_token
        user.telegram_chatid = telegram_chatid
        db.commit()
    return RedirectResponse("/dashboard", status_code=303)

@router.get("/alerts/disable")
def disable_alerts(request: Request, db: Session = Depends(get_db)):
    user_cookie = request.cookies.get("user")
    user = db.query(User).filter(User.username == user_cookie).first()
    if user:
        user.telegram_enabled = False
        user.telegram_token = None
        user.telegram_chatid = None
        db.commit()
    return RedirectResponse("/dashboard", status_code=303)

def send_telegram(user: User, message: str):
    if user.telegram_enabled and user.telegram_token and user.telegram_chatid:
        url = f"https://api.telegram.org/bot{user.telegram_token}/sendMessage"
        payload = {"chat_id": user.telegram_chatid, "text": message}
        try:
            requests.post(url, data=payload)
        except Exception as e:
            print("Telegram error:", e)
