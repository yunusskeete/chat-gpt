from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class PTPreferences(Base):
    __tablename__ = "pt_preferences"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    target_goals = Column(Text, nullable=False)  # e.g., "weight loss, muscle building"
    age_range = Column(String, nullable=False)  # e.g., "25-45"
    preferred_location = Column(String, nullable=False)
    min_budget = Column(Integer, nullable=False)  # Minimum monthly budget
    required_commitment = Column(Integer, nullable=False)  # Sessions per week
    specialty = Column(Text, nullable=False)

    # Relationships
    conversations = relationship("Conversation", back_populates="pt")
