from fastapi import FastAPI
from .db import Base, engine
from .auth import router as auth_router
from .routes import dashboard, signals, alerts

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router)
app.include_router(dashboard.router)
app.include_router(signals.router)
app.include_router(alerts.router)
