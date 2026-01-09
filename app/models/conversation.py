from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, index=True, nullable=False)  # Removed unique=True to allow multiple chats
    status = Column(String, default="active")  # active, qualified, rejected, completed, archived
    pt_id = Column(Integer, ForeignKey("pt_preferences.id"), default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

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
