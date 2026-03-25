# ============================================================
# app/models/comment.py — Comment ORM Model
#
# Laravel equivalent: app/Models/Comment.php
# ============================================================

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    body = Column(Text, nullable=False)

    # Two foreign keys: which post, and who wrote it
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # Laravel: public function post() { return $this->belongsTo(Post::class); }
    post = relationship("Post", back_populates="comments")

    # Laravel: public function author() { return $this->belongsTo(User::class); }
    author = relationship("User", back_populates="comments")

    def __repr__(self):
        return f"<Comment id={self.id} post_id={self.post_id}>"
