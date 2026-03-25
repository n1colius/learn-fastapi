# Learn FastAPI — Blog API Project

A hands-on learning project for **PHP Laravel developers** learning Python FastAPI from scratch.

Every file in this project contains inline comments mapping FastAPI concepts to their Laravel equivalents.

---

## Laravel → FastAPI Mental Model

| Laravel | FastAPI Equivalent |
|---|---|
| `composer.json` / `composer install` | `requirements.txt` / `pip install -r requirements.txt` |
| `php artisan serve` | `uvicorn app.main:app --reload` |
| `routes/api.php` + Controller | `app/routers/*.py` (APIRouter) |
| Form Request | Pydantic `*Create` / `*Update` schema |
| API Resource | Pydantic `*Response` schema |
| Eloquent Model | SQLAlchemy Model |
| `php artisan make:migration` | `alembic revision --autogenerate -m "..."` |
| `php artisan migrate` | `alembic upgrade head` |
| `php artisan migrate:rollback` | `alembic downgrade -1` |
| `->middleware('auth:api')` | `Depends(get_current_user)` |
| `$request->user()` | `current_user: User = Depends(get_current_user)` |
| `->paginate(15)` | `.offset(skip).limit(limit)` + manual count |
| Service Provider `boot()` | `lifespan` async context manager in `main.py` |
| `Hash::make($password)` | `hash_password(password)` via passlib/bcrypt |
| `Hash::check($plain, $hash)` | `verify_password(plain, hashed)` |
| `config('app.key')` | `settings.secret_key` from `app/config.py` |
| `abort(404)` | `raise HTTPException(status_code=404, detail="...")` |
| `dd()` / `dump()` | `print()` or `breakpoint()` (drops into Python debugger) |

---

## Tech Stack

| Tool | Purpose | Laravel Equivalent |
|---|---|---|
| **FastAPI** | Web framework | Laravel |
| **Uvicorn** | ASGI server | php artisan serve / Nginx Unit |
| **SQLite** | Database (file-based, zero setup) | SQLite (via `DB_CONNECTION=sqlite`) |
| **SQLAlchemy 2.x** | ORM | Eloquent |
| **Alembic** | Database migrations | `php artisan migrate` |
| **Pydantic v2** | Validation + serialization | Form Requests + API Resources |
| **pydantic-settings** | Reads `.env` into typed class | `config/app.php` |
| **python-jose** | JWT tokens | `tymon/jwt-auth` |
| **passlib + bcrypt** | Password hashing | `Hash::make()` / `Hash::check()` |
| **python-dotenv** | `.env` file loading | Laravel's built-in `.env` support |

---

## Project Structure

```
learn-fastapi/
│
├── venv/                        # Virtual environment — like vendor/ (never commit)
├── .env                         # Environment variables — same as Laravel's .env
├── .env.example                 # Committed template
├── .gitignore
├── requirements.txt             # Dependencies — like composer.json
│
├── alembic.ini                  # Alembic config
├── alembic/                     # Migrations — like database/migrations/
│   ├── env.py                   # Alembic runtime config (connects to your models)
│   └── versions/                # Auto-generated migration files
│       └── *_create_initial_tables.py
│
└── app/                         # Application — like Laravel's app/
    │
    ├── main.py                  # Entry point — like bootstrap/app.php + public/index.php
    ├── config.py                # Settings object — like config/app.php
    ├── database.py              # Engine + session + Base — like config/database.php
    ├── dependencies.py          # Auth middleware — like app/Http/Middleware/
    │
    ├── models/                  # ORM models — like app/Models/
    │   ├── __init__.py          # Imports all models (needed by Alembic)
    │   ├── user.py              # User model
    │   ├── post.py              # Post model (includes post_tags pivot table)
    │   ├── comment.py           # Comment model
    │   └── tag.py               # Tag model
    │
    ├── schemas/                 # Pydantic schemas — like Form Requests + API Resources combined
    │   ├── __init__.py
    │   ├── user.py              # UserCreate, UserResponse, Token, TokenData
    │   ├── post.py              # PostCreate, PostUpdate, PostResponse, PaginatedPostResponse
    │   ├── comment.py           # CommentCreate, CommentUpdate, CommentResponse
    │   └── tag.py               # TagCreate, TagResponse
    │
    ├── routers/                 # Routes + Controllers — like routes/api.php + Controllers
    │   ├── __init__.py
    │   ├── auth.py              # POST /auth/register, POST /auth/login
    │   ├── users.py             # GET /users/me
    │   ├── posts.py             # Full CRUD for /posts
    │   ├── comments.py          # Full CRUD for /posts/{id}/comments
    │   └── tags.py              # GET + POST /tags
    │
    └── services/                # Business logic — like app/Services/
        ├── __init__.py
        ├── auth_service.py      # Password hashing, JWT create/decode
        └── post_service.py      # Paginated queries, slug generation
```

---

## Getting Started

### 1. Activate the virtual environment

```bash
# Windows (Git Bash / WSL)
source venv/Scripts/activate

# Mac / Linux
source venv/bin/activate
```

> Virtual env is Python's equivalent of `vendor/`. You must activate it every time you open a terminal. Your prompt will show `(venv)` when it's active.

### 2. Start the development server

```bash
uvicorn app.main:app --reload
```

> `app.main` = the module path (`app/main.py`)
> `app` = the `FastAPI()` instance variable inside that file
> `--reload` = auto-restart on file changes, like `php artisan serve`

### 3. Open the auto-generated API docs

| URL | Description |
|---|---|
| http://127.0.0.1:8000/docs | Swagger UI — interactive API explorer |
| http://127.0.0.1:8000/redoc | ReDoc documentation |
| http://127.0.0.1:8000/openapi.json | Raw OpenAPI schema (JSON) |

> FastAPI generates these **automatically** from your type hints — no extra setup needed. Laravel has no built-in equivalent.

---

## API Endpoints

### Auth (no authentication required)

| Method | URL | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register a new user |
| `POST` | `/api/auth/login` | Login, returns a JWT token |

### Users (authentication required)

| Method | URL | Description |
|---|---|---|
| `GET` | `/api/users/me` | Get your own profile |

### Posts

| Method | URL | Auth | Description |
|---|---|---|---|
| `GET` | `/api/posts` | No | List published posts (paginated, searchable) |
| `POST` | `/api/posts` | Yes | Create a post |
| `GET` | `/api/posts/{id}` | No | Get a single post |
| `PUT` | `/api/posts/{id}` | Yes (owner) | Update a post |
| `DELETE` | `/api/posts/{id}` | Yes (owner) | Delete a post |

### Comments (nested under posts)

| Method | URL | Auth | Description |
|---|---|---|---|
| `GET` | `/api/posts/{id}/comments` | No | List comments on a post |
| `POST` | `/api/posts/{id}/comments` | Yes | Add a comment |
| `PUT` | `/api/posts/{id}/comments/{cid}` | Yes (owner) | Edit a comment |
| `DELETE` | `/api/posts/{id}/comments/{cid}` | Yes (owner) | Delete a comment |

### Tags

| Method | URL | Auth | Description |
|---|---|---|---|
| `GET` | `/api/tags` | No | List all tags |
| `POST` | `/api/tags` | Yes | Create a tag |

### Query Parameters for `GET /api/posts`

| Param | Type | Default | Description |
|---|---|---|---|
| `page` | int | `1` | Page number |
| `per_page` | int | `10` | Items per page (max 100) |
| `search` | string | — | Filter posts by title |

Example: `GET /api/posts?page=2&per_page=5&search=fastapi`

---

## Migration Commands

```bash
# Generate a new migration from model changes (like php artisan make:migration)
alembic revision --autogenerate -m "add is_published to posts"

# Apply all pending migrations (like php artisan migrate)
alembic upgrade head

# Roll back one migration (like php artisan migrate:rollback)
alembic downgrade -1

# Roll back ALL migrations
alembic downgrade base

# See migration history
alembic history

# See current migration version
alembic current
```

---

## End-to-End Test Flow (using Swagger UI)

1. Start the server: `uvicorn app.main:app --reload`
2. Open http://127.0.0.1:8000/docs
3. **Register** → `POST /api/auth/register` with name, email, password
4. **Login** → `POST /api/auth/login` with email (as "username") + password → copy the `access_token`
5. **Authorize** → click the "Authorize" button at the top of Swagger UI → paste your token
6. **Create tags** → `POST /api/tags` with `{"name": "Python"}` and `{"name": "FastAPI"}`
7. **Create post** → `POST /api/posts` with title, body, `tag_ids: [1, 2]`
8. **List posts** → `GET /api/posts?page=1&per_page=5` → check pagination metadata
9. **Add comment** → `POST /api/posts/1/comments`
10. **Try forbidden action** → log in as a different user, try to delete the first user's post → expect `403 Forbidden`
11. **Delete post** → `DELETE /api/posts/1` → expect `204 No Content`
12. **View OpenAPI schema** → http://127.0.0.1:8000/openapi.json

---

## Key Python Concepts for Laravel Developers

### Virtual Environment
PHP's `vendor/` is managed automatically by Composer per project.
In Python, you manually create and activate a virtual environment:

```bash
python -m venv venv          # Create (only once)
source venv/Scripts/activate # Activate (every new terminal)
pip install -r requirements.txt # Install packages
```

### Type Hints
Python is dynamically typed, but FastAPI **requires** type hints. FastAPI reads them to build validation, docs, and serialization automatically.

```python
# PHP 8
function createPost(string $title, string $body): PostResponse { ... }

# Python / FastAPI
def create_post(title: str, body: str) -> PostResponse: ...
```

### `Optional` and `None`
PHP's `?string` becomes `Optional[str] = None` in Python. Both the type hint AND the default are required:

```python
# PHP
?string $title = null

# Python
title: Optional[str] = None
# or in Python 3.10+
title: str | None = None
```

### The `Depends()` System
FastAPI's dependency injection is declared per-function, not registered in a container:

```php
// Laravel — register in a service provider, inject via type hint
public function __construct(PostService $postService) { ... }

// FastAPI — declare inline, resolved automatically
def create_post(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
```

### `yield` in `get_db()`
The database session uses a Python generator. Code before `yield` = setup, code after `yield` = teardown (always runs):

```python
def get_db():
    db = SessionLocal()
    try:
        yield db       # Route handler runs here
    finally:
        db.close()    # Always runs after, like a destructor
```

### Pydantic `model_config = ConfigDict(from_attributes=True)`
Without this, Pydantic can't read SQLAlchemy ORM objects (it only reads plain dicts by default).
This is like calling `->toArray()` on an Eloquent model automatically.

```python
class PostResponse(BaseModel):
    id: int
    title: str
    model_config = ConfigDict(from_attributes=True)  # Required for ORM objects
```

### `model_dump(exclude_unset=True)` for PATCH updates
Only apply fields the client actually sent (not all defaults):

```python
update_data = body.model_dump(exclude_unset=True)
# Laravel equivalent: $request->only(['title', 'body'])
for field, value in update_data.items():
    setattr(post, field, value)  # Like $post->$field = $value
```

### f-strings
Same as PHP's string interpolation:

```php
// PHP
"Hello {$name}, you have {$count} posts"

// Python
f"Hello {name}, you have {count} posts"
```

### No `$this` — it's `self`
In Python class methods, the first parameter is always `self`:

```python
class MyClass:
    def my_method(self, arg):  # self = $this in PHP
        self.value = arg       # $this->value = $arg
```

---

## Suggested Learning Order

Read the files in this order to build understanding progressively:

1. [app/config.py](app/config.py) — Settings vs Laravel's `config()`
2. [app/database.py](app/database.py) — `get_db()` and the session lifecycle
3. [app/models/user.py](app/models/user.py) — simple model, understand column declarations
4. [app/models/post.py](app/models/post.py) — complex model: pivot table + 3 relationships
5. [app/schemas/user.py](app/schemas/user.py) — understand Base/Create/Response pattern
6. [app/schemas/post.py](app/schemas/post.py) — full Pydantic pattern with nested schemas
7. [app/services/auth_service.py](app/services/auth_service.py) — JWT + password hashing
8. [app/dependencies.py](app/dependencies.py) — how `Depends()` replaces Laravel middleware
9. [app/routers/auth.py](app/routers/auth.py) — register + login routes
10. [app/routers/posts.py](app/routers/posts.py) — full CRUD with ownership checks

---

## Debugging Tips

| Situation | What to do |
|---|---|
| `ImportError` or `ModuleNotFoundError` | Virtual env not activated, or missing `__init__.py` |
| `422 Unprocessable Entity` | FastAPI returns detailed JSON showing exactly which field failed validation |
| See all SQL queries | Add `echo=True` to `create_engine()` in `database.py` |
| Drop into debugger | Add `breakpoint()` anywhere in your code (like `dd()`) |
| Check DB tables | Open `blog.db` with [DB Browser for SQLite](https://sqlitebrowser.org/) |
| Reset database | Delete `blog.db`, then `alembic upgrade head` |
