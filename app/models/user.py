# ============================================================
# app/models/user.py — User ORM Model
#
# Laravel equivalent: app/Models/User.php (Eloquent model)
#
# Key differences from Eloquent:
# - Columns are declared explicitly as class attributes
# - Table name is set via __tablename__ (Eloquent auto-pluralizes)
# - Relationships are also declared explicitly
# - There is no $fillable / $guarded — that's handled by Pydantic schemas
# ============================================================

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """
    SQLAlchemy ORM model for the users table.

    In Laravel:
        class User extends Model { ... }

    In SQLAlchemy:
        class User(Base): ...
        where Base = declarative_base() from database.py
    """

    # The database table name.
    # In Eloquent this is auto-derived (User → users).
    # In SQLAlchemy, you must declare it explicitly.
    __tablename__ = "users"

    # -------------------------------------------------------
    # Columns — like Eloquent's $casts + migration columns combined
    #
    # Column(Integer, primary_key=True) → $table->id() in Laravel migration
    # Column(String, unique=True)       → $table->string('email')->unique()
    # Column(Boolean, default=True)     → $table->boolean('is_active')->default(true)
    # -------------------------------------------------------
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

    # Timestamps — Eloquent adds these automatically via $timestamps = true
    # In SQLAlchemy, you declare them manually
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # -------------------------------------------------------
    # Relationships
    #
    # Laravel:
    #   public function posts() { return $this->hasMany(Post::class); }
    #
    # SQLAlchemy:
    #   posts = relationship("Post", back_populates="author")
    #
    # `back_populates` links the two sides of the relationship.
    # "Post" is a string reference (avoids circular import issues).
    # -------------------------------------------------------
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")

    def __repr__(self):
        # Like __toString() in PHP — used for debugging
        return f"<User id={self.id} email={self.email}>"
