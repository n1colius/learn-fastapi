# ============================================================
# app/routers/comments.py — Comment Routes (nested under Posts)
#
# Laravel equivalent: routes/api.php + CommentController
#
# Routes (prefix /api/posts added in main.py):
#   GET    /api/posts/{post_id}/comments              → list comments (public)
#   POST   /api/posts/{post_id}/comments              → add comment (authenticated)
#   PUT    /api/posts/{post_id}/comments/{comment_id} → edit comment (owner only)
#   DELETE /api/posts/{post_id}/comments/{comment_id} → delete comment (owner only)
#
# Note: These are "nested resources" — like Laravel's:
#   Route::apiResource('posts.comments', CommentController::class)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse


router = APIRouter()


def get_post_or_404(post_id: int, db: Session) -> Post:
    """
    Helper to fetch a post or raise 404.
    Reusable across multiple endpoints in this file.

    Laravel equivalent: route model binding (Post $post) which
    automatically throws 404 if the post doesn't exist.
    FastAPI does NOT have automatic route model binding.
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")
    return post


# -------------------------------------------------------
# GET /api/posts/{post_id}/comments
# -------------------------------------------------------
@router.get("/{post_id}/comments", response_model=list[CommentResponse])
def list_comments(post_id: int, db: Session = Depends(get_db)):
    """List all comments for a post. Public."""
    get_post_or_404(post_id, db)  # Ensure post exists first
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    return comments


# -------------------------------------------------------
# POST /api/posts/{post_id}/comments
# -------------------------------------------------------
@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    post_id: int,
    body: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add a comment to a post. Requires authentication."""
    get_post_or_404(post_id, db)

    comment = Comment(
        body=body.body,
        post_id=post_id,
        author_id=current_user.id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


# -------------------------------------------------------
# PUT /api/posts/{post_id}/comments/{comment_id}
# -------------------------------------------------------
@router.put("/{post_id}/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    post_id: int,
    comment_id: int,
    body: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Edit a comment. Only the comment's author can edit it."""
    get_post_or_404(post_id, db)

    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.post_id == post_id,
    ).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found.")

    # Authorization: only the author can edit their own comment
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own comments.",
        )

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(comment, field, value)

    db.commit()
    db.refresh(comment)
    return comment


# -------------------------------------------------------
# DELETE /api/posts/{post_id}/comments/{comment_id}
# -------------------------------------------------------
@router.delete("/{post_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a comment. Only the comment's author can delete it."""
    get_post_or_404(post_id, db)

    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.post_id == post_id,
    ).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found.")

    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments.",
        )

    db.delete(comment)
    db.commit()
    return None
