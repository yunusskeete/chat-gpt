from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # user or assistant
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    twilio_message_sid = Column(String, unique=True, nullable=True)  # For idempotency

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
