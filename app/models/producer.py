# ============================================================
# app/models/producer.py — Producer ORM Model
#
# Laravel equivalent: app/Models/Producer.php
#
# Notes:
# - gender uses String(1): 'm', 'f', or '0'
# - is_active uses SmallInteger: 1 = active, 0 = inactive
# - created_by / updated_by store a user id (Integer)
# - commodity_id → FK to ref_commodity.id
# - region_id    → FK to ref_region.id
# ============================================================

from datetime import datetime
from sqlalchemy import Column, Integer, SmallInteger, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Producer(Base):
    __tablename__ = "producers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    external_id = Column(String(100), nullable=True)

    # 'm' = male, 'f' = female, '0' = not specified
    gender = Column(String(1), nullable=True)

    date_of_birth = Column(Date, nullable=True)

    # Foreign keys — like $table->foreignId('commodity_id') in Laravel
    commodity_id = Column(Integer, ForeignKey("ref_commodity.id"), nullable=True)
    region_id = Column(Integer, ForeignKey("ref_region.id"), nullable=True)

    total_plot = Column(Integer, default=0, nullable=True)

    # 1 = active, 0 = inactive
    is_active = Column(SmallInteger, default=1, nullable=False)

    # Timestamps + audit columns
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, nullable=True)   # store user id of creator
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(Integer, nullable=True)   # store user id of last updater

    # Relationships — like $this->belongsTo(RefCommodity::class)
    commodity = relationship("RefCommodity", back_populates="producers")
    region = relationship("RefRegion", back_populates="producers")

    def __repr__(self):
        return f"<Producer id={self.id} name={self.name}>"
