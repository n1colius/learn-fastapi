# ============================================================
# app/database.py — Database Engine, Session & Base Model
#
# Laravel equivalent: config/database.php + the DB facade combined
#
# In Laravel, database connections are managed automatically.
# In FastAPI, you manage the session lifecycle explicitly.
# This file sets up three things:
#   1. engine       — the raw connection pool (like PDO)
#   2. SessionLocal — a factory that creates DB sessions per request
#   3. Base         — the base class all your ORM models inherit from
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# -------------------------------------------------------
# 1. Engine — the database connection pool
#
# Laravel equivalent: the PDO connection behind DB::connection()
#
# `connect_args={"check_same_thread": False}` is SQLite-specific.
# SQLite by default only allows one thread. Since FastAPI can use
# multiple threads, we disable that check. Not needed for PostgreSQL.
# -------------------------------------------------------
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # SQLite only
)

# -------------------------------------------------------
# 2. SessionLocal — DB session factory
#
# Laravel equivalent: DB::connection() or a new Eloquent query builder
#
# autocommit=False: changes are NOT saved until you call db.commit()
#                   (like wrapping everything in DB::transaction())
# autoflush=False:  SQLAlchemy won't auto-sync before queries
#                   (gives you more control)
# -------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -------------------------------------------------------
# 3. Base — the parent class for all ORM models
#
# Laravel equivalent: Eloquent's Model class
# All your models will inherit from this Base.
# It tracks all models so Alembic can auto-generate migrations.
# -------------------------------------------------------
Base = declarative_base()


# -------------------------------------------------------
# 4. get_db() — the database session dependency
#
# Laravel equivalent: Laravel automatically gives each request
# a fresh DB connection. In FastAPI, you inject it explicitly
# using Depends(get_db) in your route functions.
#
# This is a Python generator function (note the `yield`).
# Code before yield = setup (open session)
# yield db          = the route handler runs here with `db`
# Code after yield  = teardown (always runs, like a finally block)
#
# Usage in a router:
#   @router.get("/posts")
#   def list_posts(db: Session = Depends(get_db)):
#       return db.query(Post).all()
# -------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db        # Hand the session to the route handler
    finally:
        db.close()      # Always close, even if an exception occurred
