# ============================================================
# app/models/ref_region.py — RefRegion ORM Model
#
# Laravel equivalent: app/Models/RefRegion.php
# ============================================================

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class RefRegion(Base):
    __tablename__ = "ref_region"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    country_code = Column(String(10), nullable=False)
    country_name = Column(String(100), nullable=False)

    # One region → many producers
    producers = relationship("Producer", back_populates="region")

    def __repr__(self):
        return f"<RefRegion id={self.id} name={self.name}>"
