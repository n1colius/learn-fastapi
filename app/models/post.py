# ============================================================
# app/models/post.py — Post ORM Model
#
# Laravel equivalent: app/Models/Post.php
#
# This is the most complex model — it contains:
#   - The post_tags pivot table (many-to-many)
#   - Relationships to User (author), Comment, and Tag
# ============================================================

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


# -------------------------------------------------------
# Pivot Table: post_tags
#
# Laravel equivalent: a migration with Schema::create('post_tags', ...)
# and then using belongsToMany() — you don't create a Model for it.
#
# In SQLAlchemy, you also don't create a Model class for a pivot table.
# Instead, you create a plain Table object with the two foreign keys.
# SQLAlchemy uses this `secondary` table automatically when you query
# the many-to-many relationship.
# -------------------------------------------------------
post_tags = Table(
    "post_tags",        # Table name in the database
    Base.metadata,      # Register it with SQLAlchemy's metadata
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("tag_id",  Integer, ForeignKey("tags.id"),  primary_key=True),
)


class Post(Base):
    """
    SQLAlchemy ORM model for the posts table.
    """

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(270), unique=True, nullable=False, index=True)
    body = Column(Text, nullable=False)
    published = Column(Boolean, default=False)

    # Foreign key — like $table->foreignId('author_id')->constrained('users')
    # ForeignKey("users.id") references the id column of the users table
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # -------------------------------------------------------
    # Relationships
    # -------------------------------------------------------

    # Many-to-One: Post belongs to a User (the author)
    # Laravel: public function author() { return $this->belongsTo(User::class); }
    author = relationship("User", back_populates="posts")

    # One-to-Many: Post has many Comments
    # Laravel: public function comments() { return $this->hasMany(Comment::class); }
    # cascade="all, delete-orphan" = like onDelete('cascade') in migrations
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

    # Many-to-Many: Post has many Tags (through post_tags pivot)
    # Laravel: public function tags() { return $this->belongsToMany(Tag::class, 'post_tags'); }
    # `secondary=post_tags` tells SQLAlchemy to use the pivot table
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")

    def __repr__(self):
        return f"<Post id={self.id} slug={self.slug}>"
