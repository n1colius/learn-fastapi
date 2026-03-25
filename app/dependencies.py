# ============================================================
# app/dependencies.py — Reusable Dependencies (Middleware)
#
# Laravel equivalent: app/Http/Middleware/Authenticate.php
#
# In Laravel, you protect routes with:
#   Route::middleware('auth:api')->group(...)
#
# In FastAPI, you protect routes with:
#   @router.get("/me", dependencies=[Depends(get_current_user)])
# OR inject the user directly:
#   def get_me(current_user: User = Depends(get_current_user)):
#
# The `Depends()` system is FastAPI's dependency injection.
# Dependencies can depend on other dependencies (chain/nest them).
# FastAPI resolves the entire chain automatically before your handler runs.
#
# Think of it like: Laravel's middleware stack, but per-function instead
# of per-route-group, and expressed as plain Python functions.
# ============================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth_service import decode_access_token


# -------------------------------------------------------
# OAuth2 Password Bearer Scheme
#
# This tells FastAPI: "to authenticate, the client should send
# a Bearer token in the Authorization header."
#
# tokenUrl="/api/auth/login" is the endpoint that ISSUES tokens.
# FastAPI uses this to add an "Authorize" button in Swagger UI.
#
# Laravel equivalent: there's no explicit declaration — Laravel's
# auth:api middleware just knows to look for a Bearer token.
# -------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# -------------------------------------------------------
# get_current_user — the core auth dependency
#
# Laravel equivalent: $request->user() / auth()->user()
# or the Authenticate middleware that calls Auth::guard()->user()
#
# FastAPI automatically injects:
#   - `token`: extracted from the "Authorization: Bearer <token>" header
#              by oauth2_scheme (raises 401 automatically if missing)
#   - `db`: a database session from get_db()
#
# This function then:
#   1. Decodes the JWT to get the user ID
#   2. Fetches the User from the database
#   3. Returns the User object (or raises 401)
#
# Usage in a router:
#   @router.get("/me")
#   def get_me(current_user: User = Depends(get_current_user)):
#       return current_user
#       # current_user is the User ORM object — like $request->user() in Laravel
# -------------------------------------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Validates the JWT and returns the authenticated User.
    Raises HTTP 401 if the token is missing, invalid, or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},  # Standard OAuth2 header
    )

    try:
        token_data = decode_access_token(token)
    except ValueError:
        raise credentials_exception

    # Fetch user from DB — like User::find($tokenData->user_id) in Laravel
    user = db.query(User).filter(User.id == token_data.user_id).first()

    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Same as get_current_user, but also checks if the user is active.

    Laravel equivalent: a middleware that checks $user->is_active
    or using the 'verified' middleware.

    Use this instead of get_current_user when you want to also
    reject soft-banned or deactivated accounts.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated.",
        )
    return current_user
