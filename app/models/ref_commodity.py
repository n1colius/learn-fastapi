# ============================================================
# app/models/ref_commodity.py — RefCommodity ORM Model
#
# Laravel equivalent: app/Models/RefCommodity.php
# ============================================================

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class RefCommodity(Base):
    __tablename__ = "ref_commodity"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    # One commodity → many producers
    producers = relationship("Producer", back_populates="commodity")

    def __repr__(self):
        return f"<RefCommodity id={self.id} name={self.name}>"
