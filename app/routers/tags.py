# ============================================================
# app/routers/tags.py — Tag Routes
#
# Routes (prefix /api/tags added in main.py):
#   GET  /api/tags      → list all tags (public)
#   POST /api/tags      → create a tag (authenticated)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.tag import Tag
from app.models.user import User
from app.schemas.tag import TagCreate, TagResponse
from app.services.post_service import slugify


router = APIRouter()


@router.get("/", response_model=list[TagResponse])
def list_tags(db: Session = Depends(get_db)):
    """List all tags. Public — no authentication required."""
    # db.query(Tag).all() = Tag::all() in Laravel
    return db.query(Tag).order_by(Tag.name).all()


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    body: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),  # Auth required
):
    """Create a new tag. Requires authentication."""
    # Check for duplicate tag name
    existing = db.query(Tag).filter(Tag.name == body.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag '{body.name}' already exists.",
        )

    tag = Tag(
        name=body.name,
        slug=slugify(body.name),
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag
