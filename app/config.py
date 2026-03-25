# ============================================================
# app/config.py — Application Settings
#
# Laravel equivalent: config/app.php + config/database.php
#
# In Laravel, you call config('app.key') anywhere.
# In FastAPI, you import the `settings` object from this file.
#
# Pydantic's BaseSettings automatically reads from .env,
# so you never need to call dotenv_values() manually.
# ============================================================

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Typed settings class — reads values from .env automatically.

    Laravel equivalent: the array returned by config/app.php,
    but here it's a typed Python object with IDE autocomplete.

    Type hints (e.g., `str`, `int`) tell Pydantic what to expect.
    If .env has a wrong type (e.g., a string where int is expected),
    Pydantic raises a clear error at startup — not at runtime.
    """

    # Database connection string
    # SQLite format: sqlite:///./blog.db  (3 slashes = relative path)
    # PostgreSQL format: postgresql://user:pass@localhost/dbname
    database_url: str = "sqlite:///./blog.db"

    # JWT settings — equivalent to config('jwt.secret') in tymon/jwt-auth
    secret_key: str = "change-this-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        # Tell Pydantic to read from the .env file
        # Laravel reads .env automatically; here we configure it explicitly
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.

    @lru_cache means this function only runs ONCE per process.
    The .env file is read once at startup, not on every request.

    Laravel equivalent: the config() helper caches config values
    after the first call via the config repository.
    """
    return Settings()


# A convenient module-level singleton — import this throughout the app:
#   from app.config import settings
#   print(settings.database_url)
settings = get_settings()
