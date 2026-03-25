# ============================================================
# app/schemas/tag.py — Tag Pydantic Schemas
# ============================================================

from pydantic import BaseModel, ConfigDict


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass  # No additional fields needed beyond name


class TagResponse(TagBase):
    id: int
    slug: str

    model_config = ConfigDict(from_attributes=True)
