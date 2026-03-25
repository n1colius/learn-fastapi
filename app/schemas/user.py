# ============================================================
# app/schemas/user.py — User Pydantic Schemas
#
# This is the BIGGEST conceptual shift from Laravel.
#
# In Laravel, you have TWO separate things:
#   - Form Request  → validates incoming request data
#   - API Resource  → shapes outgoing JSON response
#
# In FastAPI + Pydantic, ONE schema file handles BOTH,
# but you use DIFFERENT schema classes for each direction:
#   - *Create / *Update schemas → used for request body validation
#   - *Response schemas         → used for response serialization
#
# Laravel equivalent mapping:
#   UserCreate  → StoreUserRequest (Form Request)
#   UserUpdate  → UpdateUserRequest
#   UserResponse → UserResource (API Resource)
# ============================================================

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


# -------------------------------------------------------
# Base Schema — shared fields
#
# In Laravel this is like an abstract base Form Request
# that holds common validation rules.
#
# Pydantic classes can inherit from each other just like PHP classes.
# -------------------------------------------------------
class UserBase(BaseModel):
    name: str
    email: EmailStr  # Pydantic validates this is a real email format


# -------------------------------------------------------
# Create Schema — for POST /api/auth/register
#
# Laravel equivalent: StoreUserRequest with rules()
#
# This schema validates the incoming JSON body.
# FastAPI reads the type hints and auto-validates.
# If validation fails, it automatically returns 422 with details.
# (In Laravel, validation failure returns 422 via Form Requests too)
# -------------------------------------------------------
class UserCreate(UserBase):
    password: str  # Plain-text password from the request (we hash it before saving)


# -------------------------------------------------------
# Response Schema — for outgoing JSON
#
# Laravel equivalent: UserResource (API Resource)
#
# Key config: `from_attributes=True`
# By default, Pydantic works with plain dicts.
# But our route handlers return SQLAlchemy ORM objects (like Eloquent models).
# `from_attributes=True` tells Pydantic: "read attributes from ORM objects".
# Laravel's ->toArray() does the same thing automatically on Eloquent models.
# -------------------------------------------------------
class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None

    # This config is REQUIRED when returning SQLAlchemy ORM objects directly
    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------
# Token Schemas — for login response
#
# These don't map to a DB model; they just shape the JSON response.
# Laravel equivalent: whatever your AuthController returns after login
# -------------------------------------------------------
class Token(BaseModel):
    """The response body for POST /api/auth/login"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """The decoded payload inside a JWT token (internal use only)"""
    user_id: Optional[int] = None
