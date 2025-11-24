from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="active")  # active, qualified, rejected, completed
    pt_id = Column(Integer, ForeignKey("pt_preferences.id"), default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
    lead_data = relationship(
        "LeadData",
        back_populates="conversation",
        uselist=False,
        cascade="all, delete-orphan",
    )
    pt = relationship("PTPreferences", back_populates="conversations")
