# ============================================================
# app/main.py — Application Entry Point
#
# Laravel equivalent: bootstrap/app.php + public/index.php combined
#
# This file:
#   1. Creates the FastAPI app instance
#   2. Registers all routers (like route files in Laravel)
#   3. Adds middleware (like Kernel.php)
#   4. Handles startup/shutdown events (like Service Providers)
#
# Run the server with:
#   uvicorn app.main:app --reload
#
# `app.main` = the module path (app/main.py)
# `app`      = the FastAPI() instance variable name inside that file
# `--reload` = auto-restart on file changes (like php artisan serve)
# ============================================================

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base


# -------------------------------------------------------
# Lifespan — Startup & Shutdown events
#
# Laravel equivalent: Service Provider boot() method
#
# Code before `yield` runs at startup.
# Code after `yield` runs at shutdown.
#
# Here we create all database tables that don't exist yet.
# This is a quick dev shortcut — in production, always use Alembic migrations.
# -------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import models so SQLAlchemy knows about them before creating tables
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)  # Creates tables if they don't exist
    yield
    # Shutdown logic here (e.g., close connections)


# -------------------------------------------------------
# FastAPI App Instance
#
# Laravel equivalent: the $app object in bootstrap/app.php
#
# title, description, version → auto-populate the Swagger UI at /docs
# This is something Laravel does NOT give you out of the box!
# -------------------------------------------------------
app = FastAPI(
    title="Blog API",
    description="A learning project for Python FastAPI — built by a Laravel developer.",
    version="1.0.0",
    lifespan=lifespan,
)


# -------------------------------------------------------
# CORS Middleware
#
# Laravel equivalent: config/cors.php
#
# allow_origins=["*"] allows all domains — fine for local dev.
# In production, replace "*" with your frontend URL.
# -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------
# Register Routers
#
# Laravel equivalent: registering routes in routes/api.php
#
# include_router() = like Route::prefix('auth')->group(...)
# prefix="/api/auth" → all routes in auth router start with /api/auth
# tags=["Auth"]      → groups routes in the Swagger UI
# -------------------------------------------------------
from app.routers import auth, users, posts, comments, tags  # noqa: E402

app.include_router(auth.router,     prefix="/api/auth",     tags=["Auth"])
app.include_router(users.router,    prefix="/api/users",    tags=["Users"])
app.include_router(posts.router,    prefix="/api/posts",    tags=["Posts"])
app.include_router(comments.router, prefix="/api/posts",    tags=["Comments"])
app.include_router(tags.router,     prefix="/api/tags",     tags=["Tags"])


# -------------------------------------------------------
# Root Health Check
#
# Laravel equivalent: Route::get('/', fn() => response()->json(['status' => 'ok']))
# -------------------------------------------------------
@app.get("/", tags=["Health"])
def health_check():
    """
    Simple health check endpoint.
    Visit /docs to see the interactive Swagger UI.
    Visit /redoc for the ReDoc documentation.
    Visit /openapi.json for the raw OpenAPI schema.
    """
    return {
        "status": "ok",
        "message": "Blog API is running",
        "docs": "/docs",
    }
