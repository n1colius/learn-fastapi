# ============================================================
# app/routers/posts.py — Post CRUD Routes
#
# Laravel equivalent: routes/api.php + PostController
#
# Routes (prefix /api/posts added in main.py):
#   GET    /api/posts          → list posts (public, paginated)
#   POST   /api/posts          → create post (authenticated)
#   GET    /api/posts/{id}     → get single post (public)
#   PUT    /api/posts/{id}     → update post (authenticated, owner only)
#   DELETE /api/posts/{id}     → delete post (authenticated, owner only)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.post import Post
from app.models.tag import Tag
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostResponse, PaginatedPostResponse
from app.services.post_service import get_paginated_posts, make_unique_slug


router = APIRouter()


# -------------------------------------------------------
# GET /api/posts — List all published posts (paginated)
#
# Laravel equivalent:
#   public function index(Request $request) {
#       return PostResource::collection(
#           Post::published()->paginate($request->per_page ?? 10)
#       );
#   }
#
# Query parameters (?page=1&per_page=10&search=hello) are declared
# as function parameters with `Query()` or with default values.
# FastAPI automatically reads them from the URL.
# -------------------------------------------------------
@router.get("/", response_model=PaginatedPostResponse)
def list_posts(
    page: int = Query(default=1, ge=1, description="Page number (starts at 1)"),
    per_page: int = Query(default=10, ge=1, le=100, description="Items per page"),
    search: str = Query(default=None, description="Search posts by title"),
    db: Session = Depends(get_db),
):
    """
    List all published posts with pagination.

    Examples:
        GET /api/posts
        GET /api/posts?page=2&per_page=5
        GET /api/posts?search=fastapi
    """
    return get_paginated_posts(db, page=page, per_page=per_page, search=search)


# -------------------------------------------------------
# POST /api/posts — Create a new post
#
# Laravel equivalent:
#   public function store(StorePostRequest $request) { ... }
# -------------------------------------------------------
@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    body: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new post. Requires authentication.

    Send tag_ids as a list of existing tag IDs to attach them.
    Example body:
    {
        "title": "My First Post",
        "body": "Hello FastAPI!",
        "published": true,
        "tag_ids": [1, 2]
    }
    """
    # Generate a unique slug from the title
    # Laravel: Str::slug($request->title)
    slug = make_unique_slug(db, body.title)

    # Create the Post ORM object
    post = Post(
        title=body.title,
        slug=slug,
        body=body.body,
        published=body.published,
        author_id=current_user.id,  # Set from the JWT, not from the request body
    )

    # Attach tags (many-to-many)
    # Laravel: $post->tags()->sync($request->tag_ids)
    if body.tag_ids:
        # Fetch all requested tags from DB
        tags = db.query(Tag).filter(Tag.id.in_(body.tag_ids)).all()
        post.tags = tags  # SQLAlchemy handles the pivot table automatically

    db.add(post)
    db.commit()
    db.refresh(post)
    return post


# -------------------------------------------------------
# GET /api/posts/{post_id} — Get a single post
#
# Laravel equivalent:
#   public function show(Post $post) { return new PostResource($post); }
#   (Laravel uses route model binding automatically)
#   (FastAPI does NOT have route model binding — you fetch manually)
# -------------------------------------------------------
@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a single post by ID. Public — no authentication required."""
    # db.query(Post).filter(Post.id == post_id).first()
    # = Post::find($postId) in Laravel
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        # HTTP 404 Not Found
        # Laravel: abort(404) or throws ModelNotFoundException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id={post_id} not found.",
        )

    return post


# -------------------------------------------------------
# PUT /api/posts/{post_id} — Update a post (owner only)
#
# Laravel equivalent:
#   public function update(UpdatePostRequest $request, Post $post) {
#       $this->authorize('update', $post); // Policy check
#       $post->update($request->validated());
#   }
# -------------------------------------------------------
@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    body: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a post. Only the post's author can update it.
    All fields are optional — send only the ones you want to change.
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    # Authorization check — like a Laravel Policy
    # Laravel: $this->authorize('update', $post)
    # FastAPI: manual check (no built-in policy system)
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own posts.",
        )

    # Update only the fields that were sent in the request
    # body.model_dump(exclude_unset=True) returns only the fields the client sent,
    # skipping fields that are still at their default `None` value.
    # Laravel equivalent: $request->only(['title', 'body']) or $request->validated()
    update_data = body.model_dump(exclude_unset=True)

    # Handle tags separately (many-to-many sync)
    if "tag_ids" in update_data:
        tag_ids = update_data.pop("tag_ids")
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        post.tags = tags  # Replaces all existing tags (like ->sync())

    # Handle title change → regenerate slug
    if "title" in update_data:
        update_data["slug"] = make_unique_slug(db, update_data["title"], exclude_id=post.id)

    # Apply the updates to the ORM object
    for field, value in update_data.items():
        setattr(post, field, value)  # Like $post->$field = $value in PHP

    db.commit()
    db.refresh(post)
    return post


# -------------------------------------------------------
# DELETE /api/posts/{post_id} — Delete a post (owner only)
#
# Laravel equivalent:
#   public function destroy(Post $post) {
#       $this->authorize('delete', $post);
#       $post->delete();
#       return response()->noContent();
#   }
# -------------------------------------------------------
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a post. Only the post's author can delete it.
    Returns HTTP 204 No Content on success (no body in the response).
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own posts.",
        )

    # Delete the post — cascade will also delete its comments (configured in the model)
    # Laravel: $post->delete()
    db.delete(post)
    db.commit()

    # Return None — FastAPI sends 204 No Content with no body
    # Laravel: return response()->noContent()
    return None
