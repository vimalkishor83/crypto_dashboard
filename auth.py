from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .db import get_db
from .models import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/register")
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register_user(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    hashed_pw = pwd_context.hash(password)
    user = User(username=username, password=hashed_pw)
    db.add(user)
    db.commit()
    return RedirectResponse("/", status_code=303)

@router.get("/")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/")
def login_user(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.password):
        return templates.TemplateResponse("login.html", {"request": {}, "msg": "Invalid credentials"})
    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie("user", user.username)
    return response

@router.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("user")
    return response
