from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class LeadData(Base):
    __tablename__ = "lead_data"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), unique=True, nullable=False)

    # Extracted information
    goals = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    location = Column(String, nullable=True)
    budget_range = Column(String, nullable=True)
    commitment_level = Column(Integer, nullable=True)  # 1-10 scale
    availability = Column(String, nullable=True)

    # Qualification results
    qualification_score = Column(Integer, nullable=True)  # 1-100
    is_qualified = Column(Boolean, nullable=True)
    reasoning = Column(Text, nullable=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="lead_data")
