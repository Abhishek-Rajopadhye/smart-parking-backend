# app/db/oauth_model.py

from sqlalchemy import Column, Integer, String
from app.db.db import Base

class OAuthUser(Base):
    __tablename__ = "oauth_users"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, index=True)  # "google", "github", etc.
    provider_id = Column(String, unique=True, index=True)  # OAuth2 ID
    email = Column(String, unique=True, index=True)
    name = Column(String)
    phone = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    access_token = Column(String)
    refresh_token = Column(String, nullable=True)  # If provider supports refresh tokens

 