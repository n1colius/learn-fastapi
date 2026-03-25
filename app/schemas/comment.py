# ============================================================
# app/schemas/comment.py — Comment Pydantic Schemas
# ============================================================

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserResponse


class CommentBase(BaseModel):
    body: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    # All fields are Optional — this is a PATCH-style update.
    # Laravel equivalent: UpdateCommentRequest with sometimes() rules
    # `Optional[str] = None` means: field is not required, defaults to None
    body: Optional[str] = None


class CommentResponse(CommentBase):
    id: int
    post_id: int
    author: UserResponse
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
