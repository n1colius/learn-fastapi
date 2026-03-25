# ============================================================
# alembic/env.py — Alembic Migration Environment Config
#
# Laravel equivalent: database/migrations/ + config/database.php
#
# This file tells Alembic:
#   1. Where the database is (from our settings)
#   2. What models to watch for changes (our SQLAlchemy models)
#
# After editing this, you can run:
#   alembic revision --autogenerate -m "create initial tables"
#   alembic upgrade head
#
# Laravel equivalents:
#   php artisan make:migration create_posts_table → alembic revision --autogenerate -m "..."
#   php artisan migrate                           → alembic upgrade head
#   php artisan migrate:rollback                  → alembic downgrade -1
# ============================================================

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# -------------------------------------------------------
# Import our app settings to get the database URL
# This reads from .env via pydantic-settings
# -------------------------------------------------------
import sys
import os

# Add the project root to Python's path so we can import from `app`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.database import Base

# Import ALL models so Alembic can detect them for autogenerate.
# Without these imports, Alembic won't know your tables exist.
# This is like Laravel's migrations knowing all your table structures.
import app.models  # noqa: F401 — imports user, post, comment, tag via __init__.py

# Alembic Config object — reads from alembic.ini
config = context.config

# Override the sqlalchemy.url from alembic.ini with our .env value
# This way you only need to set DATABASE_URL in one place (.env)
config.set_main_option("sqlalchemy.url", settings.database_url)

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -------------------------------------------------------
# target_metadata — tells Alembic what your schema SHOULD look like
#
# Laravel equivalent: Eloquent models + migration files define the schema.
# Alembic compares `target_metadata` against the actual database schema
# to auto-generate migration files.
# -------------------------------------------------------
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode (no DB connection needed).
    Generates SQL statements you can apply manually.
    Rarely used — most developers use online mode.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode (connects to the database).
    This is the standard mode — what runs when you do `alembic upgrade head`.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
