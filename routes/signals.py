from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
import requests, pandas as pd
from ..db import get_db
from ..models import User
from .alerts import send_telegram
from sqlalchemy.orm import Session

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

CANDLE_API = "https://api.testnet.delta.exchange/v2/candles?resolution=1m&symbol=BTCUSDT"

def ema_signal():
    r = requests.get(CANDLE_API).json()
    candles = r.get("result", {}).get("candles", [])
    if not candles:
        return "NO DATA"
    df = pd.DataFrame(candles, columns=["time","open","high","low","close","volume"])
    df["close"] = df["close"].astype(float)
    df["EMA9"] = df["close"].ewm(span=9).mean()
    df["EMA15"] = df["close"].ewm(span=15).mean()
    last = df.iloc[-1]
    if last["close"] > last["EMA9"] and last["close"] > last["EMA15"]:
        return "BUY"
    elif last["close"] < last["EMA9"] and last["close"] < last["EMA15"]:
        return "SELL"
    else:
        return "HOLD"

@router.get("/signals")
def signals(request: Request, db: Session = Depends(get_db)):
    signal = ema_signal()
    user_cookie = request.cookies.get("user")
    user = db.query(User).filter(User.username == user_cookie).first()
    if user and signal in ["BUY", "SELL"]:
        send_telegram(user, f"BTC EMA Signal: {signal}")
    return templates.TemplateResponse("signals.html", {"request": request, "signal": signal})
