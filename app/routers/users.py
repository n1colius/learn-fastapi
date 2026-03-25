# ============================================================
# app/routers/users.py — User Routes (Protected)
#
# Laravel equivalent: routes/api.php + UserController
#
# Routes (prefix /api/users added in main.py):
#   GET /api/users/me → return the authenticated user's profile
# ============================================================

from fastapi import APIRouter, Depends

from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse


router = APIRouter()


# -------------------------------------------------------
# GET /api/users/me
#
# Laravel equivalent:
#   public function me(Request $request) {
#       return new UserResource($request->user());
#   }
#
# `current_user: User = Depends(get_current_active_user)` is the
# key pattern to learn. FastAPI calls get_current_active_user(),
# which calls get_current_user(), which validates the JWT and
# queries the DB — all before your function body runs.
#
# If the token is missing or invalid, FastAPI returns 401 automatically
# before even entering this function. Your function only runs
# if authentication succeeded.
# -------------------------------------------------------
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    """
    Get the currently authenticated user's profile.

    Requires: Authorization: Bearer <your_token>

    In Swagger UI: click "Authorize" first, then call this endpoint.
    """
    # No DB query needed — get_current_active_user already fetched the user
    # Just return it and FastAPI serializes it via UserResponse
    return current_user
