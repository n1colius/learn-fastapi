# ============================================================
# app/schemas/post.py — Post Pydantic Schemas
#
# This file demonstrates the full Pydantic pattern:
#   Base → Create → Update → Response → PaginatedResponse
#
# Study this file to understand all other schema files — they follow
# the exact same pattern, just with different fields.
# ============================================================

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserResponse
from app.schemas.tag import TagResponse
from app.schemas.comment import CommentResponse


# -------------------------------------------------------
# Base Schema — fields shared by Create and Response
# -------------------------------------------------------
class PostBase(BaseModel):
    title: str
    body: str
    published: bool = False  # Default to draft (unpublished)


# -------------------------------------------------------
# Create Schema — for POST /api/posts
#
# Laravel equivalent: StorePostRequest
# `tag_ids` is a list of integers — e.g., [1, 2, 3]
# `list[int]` = PHP's array type hint
# `= []` means it defaults to an empty list if not provided
# -------------------------------------------------------
class PostCreate(PostBase):
    tag_ids: list[int] = []


# -------------------------------------------------------
# Update Schema — for PUT /api/posts/{id}
#
# Laravel equivalent: UpdatePostRequest
#
# For PATCH/PUT, ALL fields should be optional so the client
# can send only the fields they want to change.
# `Optional[str] = None` means: type is str OR None, default is None
# -------------------------------------------------------
class PostUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    published: Optional[bool] = None
    tag_ids: Optional[list[int]] = None


# -------------------------------------------------------
# Response Schema — for outgoing JSON
#
# Laravel equivalent: PostResource
#
# Notice we nest UserResponse and TagResponse inside PostResponse.
# In Laravel this is done with nested API Resources.
# In Pydantic, you simply use another schema as a type hint.
# -------------------------------------------------------
class PostResponse(PostBase):
    id: int
    slug: str
    author_id: int
    author: UserResponse
    tags: list[TagResponse] = []
    comments: list[CommentResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------
# Paginated Response — wraps a list of posts with metadata
#
# Laravel equivalent: PostCollection (ResourceCollection)
# with pagination links from ->paginate()
#
# Laravel's paginate() gives you total, per_page, current_page, last_page.
# We replicate that structure here manually.
# -------------------------------------------------------
class PaginatedPostResponse(BaseModel):
    data: list[PostResponse]     # The actual list of posts
    total: int                   # Total number of posts (all pages)
    page: int                    # Current page number
    per_page: int                # Items per page
    last_page: int               # Total number of pages

    model_config = ConfigDict(from_attributes=True)
