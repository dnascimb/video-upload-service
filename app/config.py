from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    database_url: str = "sqlite:///./test.db"  # Default for development
    db_username: str = "username"
    db_password: str = "password"
    secret_key: str = "your-secret-key-here"

    class Config:
        env_file = ".env"

settings = Settings()

# Database session factory
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

if "postgresql" in settings.database_url.lower():
    # Use PostgreSQL dialect
    engine = create_engine(settings.database_url)
else:
    # Use SQLite for development
    engine = create_engine(settings.database_url)

async_session_maker = async_sessionmaker(engine)

from fastapi import Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
from fastapi_rate_limiting import RateLimitingMiddleware
from fastapi_rate_limiting.utils import (
    RequestRateLimiter,
    UserRateLimiter,
)

app.add_middleware(
    RateLimitingMiddleware,
    limiter=UserRateLimiter(key="user_id", max_count=10, interval=60),
    exempt_if=lambda request: False,  # Skip rate limiting for certain paths if needed
)