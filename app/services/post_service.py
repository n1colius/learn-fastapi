# ============================================================
# app/services/post_service.py — Post Business Logic
#
# Laravel equivalent: a PostService or the logic inside PostController
#
# This service handles:
#   - Paginated post queries (like Post::paginate(15))
#   - Slug generation from titles
# ============================================================

import math
import re
from sqlalchemy.orm import Session

from app.models.post import Post
from app.schemas.post import PaginatedPostResponse


def slugify(title: str) -> str:
    """
    Convert a title into a URL-friendly slug.

    Laravel equivalent: Str::slug($title)

    Example: "Hello World! My Post" → "hello-world-my-post"

    Steps:
    1. Lowercase everything
    2. Replace non-alphanumeric chars with hyphens
    3. Strip leading/trailing hyphens
    4. Collapse multiple hyphens into one
    """
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)   # Replace non-alphanumeric with -
    slug = slug.strip("-")                      # Remove leading/trailing hyphens
    slug = re.sub(r"-+", "-", slug)             # Collapse multiple hyphens
    return slug


def make_unique_slug(db: Session, title: str, exclude_id: int = None) -> str:
    """
    Generate a unique slug, appending a number if needed.

    Example: if "hello-world" exists, returns "hello-world-2"

    Laravel equivalent: using Str::slug() with a uniqueness check loop,
    or packages like spatie/laravel-sluggable.
    """
    base_slug = slugify(title)
    slug = base_slug
    counter = 1

    while True:
        query = db.query(Post).filter(Post.slug == slug)
        if exclude_id:
            query = query.filter(Post.id != exclude_id)

        if not query.first():
            break  # Slug is unique, use it

        counter += 1
        slug = f"{base_slug}-{counter}"

    return slug


def get_paginated_posts(
    db: Session,
    page: int = 1,
    per_page: int = 10,
    search: str = None,
) -> PaginatedPostResponse:
    """
    Return a paginated list of published posts, optionally filtered by search.

    Laravel equivalent:
        Post::where('published', true)
             ->when($search, fn($q) => $q->where('title', 'like', "%{$search}%"))
             ->paginate($perPage)

    SQLAlchemy uses offset/limit instead of page numbers:
        offset = (page - 1) * per_page  (how many records to skip)
        limit  = per_page               (how many records to take)

    Example: page=2, per_page=10 → skip 10, take 10
    """
    query = db.query(Post).filter(Post.published == True)  # noqa: E712

    # Optional search filter — like WHERE title LIKE '%search%'
    if search:
        query = query.filter(Post.title.ilike(f"%{search}%"))

    # Order by newest first — like orderBy('created_at', 'desc')
    query = query.order_by(Post.created_at.desc())

    # Count total before applying pagination
    # Laravel's paginate() does this automatically; we do it manually
    total = query.count()

    # Calculate pagination metadata
    # math.ceil(7 / 2) = 4 pages for 7 items at 2 per page
    last_page = math.ceil(total / per_page) if total > 0 else 1

    # Apply offset and limit
    offset = (page - 1) * per_page
    posts = query.offset(offset).limit(per_page).all()

    return PaginatedPostResponse(
        data=posts,
        total=total,
        page=page,
        per_page=per_page,
        last_page=last_page,
    )
