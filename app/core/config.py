# app/core/config.py

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from functools import lru_cache

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Parking"
    API_V1_STR: str = "/api/v1"
    # Database Configuration
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = str(os.getenv("DB_PASSWORD", ""))
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "smart_parking")

    DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Google OAuth
    
    GOOGLE_CLIENT_ID: str = str(os.getenv("GOOGLE_CLIENT_ID"))
    GOOGLE_CLIENT_SECRET: str = str(os.getenv("GOOGLE_CLIENT_SECRET"))
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    GOOGLE_AUTH_URL: str = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL: str = "https://www.googleapis.com/oauth2/v2/userinfo"

    # GitHub OAuth
    GITHUB_CLIENT_ID: str = str(os.getenv("GITHUB_CLIENT_ID"))
    GITHUB_CLIENT_SECRET: str = str(os.getenv("GITHUB_CLIENT_SECRET"))
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/github/callback"
    GITHUB_AUTH_URL: str = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL: str = "https://github.com/login/oauth/access_token"
    GITHUB_USERINFO_URL: str = "https://api.github.com/user"

    # Security Configuration
    SECRET_KEY: str = "your_secret_key_here"  # Change this in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Token expiry in minutes

    # CORS Settings
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173", "https://smart-parking-frontend.onrender.com"]  # Allowed frontend origins

    # Payment Gateway (example)
    RAZORPAY_KEY_ID:str = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET:str = os.getenv("RAZORPAY_KEY_SECRET")

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
