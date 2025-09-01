from sqlalchemy import Column, Integer, String, Boolean
from .db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    telegram_enabled = Column(Boolean, default=False)
    telegram_token = Column(String, nullable=True)
    telegram_chatid = Column(String, nullable=True)
