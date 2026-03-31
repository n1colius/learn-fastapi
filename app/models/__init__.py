# Import all models here so that:
# 1. Alembic can discover them when generating migrations
# 2. SQLAlchemy can resolve relationships between models
#
# Laravel equivalent: Laravel's autoloader discovers all Model classes
# automatically. In Python, we explicitly import them here.

from app.models.user import User
from app.models.post import Post, post_tags
from app.models.comment import Comment
from app.models.tag import Tag
from app.models.ref_commodity import RefCommodity
from app.models.ref_region import RefRegion
from app.models.producer import Producer
