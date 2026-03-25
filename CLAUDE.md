# CLAUDE.md — Learn FastAPI Blog API

## Project Overview

A hands-on learning project for a PHP Laravel developer learning Python FastAPI. Every file contains inline comments mapping FastAPI concepts to their Laravel equivalents.

**Stack:** FastAPI · Uvicorn · SQLite · SQLAlchemy 2.x · Alembic · Pydantic v2 · python-jose · passlib/bcrypt

## Development Commands

```bash
# Activate virtual environment (required every new terminal)
source venv/Scripts/activate   # Windows Git Bash / WSL
source venv/bin/activate       # Mac / Linux

# Start dev server (like php artisan serve)
uvicorn app.main:app --reload

# Install dependencies (like composer install)
pip install -r requirements.txt
```

## Migration Commands

```bash
alembic revision --autogenerate -m "description"  # like php artisan make:migration
alembic upgrade head                               # like php artisan migrate
alembic downgrade -1                               # like php artisan migrate:rollback
alembic downgrade base                             # roll back all migrations
alembic history                                    # view migration history
alembic current                                    # see current version
```

## Project Structure

```
app/
├── main.py           # Entry point (bootstrap/app.php + public/index.php)
├── config.py         # Settings (config/app.php)
├── database.py       # DB engine + session + Base (config/database.php)
├── dependencies.py   # Auth middleware (app/Http/Middleware/)
├── models/           # SQLAlchemy ORM models (app/Models/)
├── schemas/          # Pydantic validation + serialization (Form Requests + API Resources)
├── routers/          # Routes + controllers (routes/api.php + Controllers)
└── services/         # Business logic (app/Services/)
```

## API Endpoints

Base path: `/api`

- `POST /auth/register`, `POST /auth/login`
- `GET /users/me` (auth required)
- `GET /posts`, `POST /posts`, `GET /posts/{id}`, `PUT /posts/{id}`, `DELETE /posts/{id}`
- `GET /posts/{id}/comments`, `POST /posts/{id}/comments`, `PUT/DELETE /posts/{id}/comments/{cid}`
- `GET /tags`, `POST /tags`

Auto-generated docs at `http://127.0.0.1:8000/docs` (Swagger UI).

## Key Conventions

- **Schemas follow `*Create` / `*Update` / `*Response` naming** (like Form Requests + API Resources)
- **All response schemas need `model_config = ConfigDict(from_attributes=True)`** to read ORM objects
- **Auth is `Depends(get_current_user)`** — declare it per route function, not in a container
- **`get_db()` uses `yield`** — code before yield = setup, after yield = teardown (always runs)
- **`model_dump(exclude_unset=True)`** for partial updates — only apply fields the client sent

## Laravel → FastAPI Quick Reference

| Laravel | FastAPI |
|---|---|
| `routes/api.php` + Controller | `app/routers/*.py` (APIRouter) |
| Form Request | Pydantic `*Create` / `*Update` schema |
| API Resource | Pydantic `*Response` schema |
| Eloquent Model | SQLAlchemy Model |
| `->middleware('auth:api')` | `Depends(get_current_user)` |
| `abort(404)` | `raise HTTPException(status_code=404, detail="...")` |
| `Hash::make()` / `Hash::check()` | `hash_password()` / `verify_password()` via passlib |
| `config('app.key')` | `settings.secret_key` from `app/config.py` |
| `dd()` / `dump()` | `print()` or `breakpoint()` |

## Debugging

| Problem | Fix |
|---|---|
| `ImportError` / `ModuleNotFoundError` | Venv not activated, or missing `__init__.py` |
| `422 Unprocessable Entity` | Check the JSON response — FastAPI shows exactly which field failed |
| See all SQL queries | Add `echo=True` to `create_engine()` in `database.py` |
| Drop into debugger | Add `breakpoint()` anywhere (like `dd()`) |
| Inspect DB | Open `blog.db` with DB Browser for SQLite |
| Reset DB | Delete `blog.db`, then `alembic upgrade head` |
