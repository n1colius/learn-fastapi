# ============================================================
# app/models/tag.py — Tag ORM Model
#
# Laravel equivalent: app/Models/Tag.php
# ============================================================

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
# The pivot table is defined in post.py to avoid circular imports
from app.models.post import post_tags


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(60), unique=True, nullable=False)

    # -------------------------------------------------------
    # Many-to-Many with Post (the other side)
    #
    # Laravel:
    #   public function posts() {
    #       return $this->belongsToMany(Post::class, 'post_tags');
    #   }
    #
    # SQLAlchemy:
    #   posts = relationship("Post", secondary=post_tags, back_populates="tags")
    #
    # `secondary=post_tags` tells SQLAlchemy to use the pivot table.
    # This is equivalent to specifying the pivot table in belongsToMany().
    # -------------------------------------------------------
    posts = relationship("Post", secondary=post_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag id={self.id} name={self.name}>"
