from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
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

    # ===========================================================================
    # PROMPT CUSTOMIZATION FIELDS (Optional overrides for default templates)
    # ===========================================================================
    # If NULL, falls back to default templates in app/prompts/templates.py

    # Bio & brand information
    bio = Column(Text, nullable=True)  # Custom PT bio/introduction
    years_experience = Column(Integer, nullable=True)  # Years in the industry
    certifications = Column(Text, nullable=True)  # Comma-separated certs
    additional_info = Column(Text, nullable=True)  # Extra bio details

    # Agent prompt overrides
    intro_message_override = Column(Text, nullable=True)  # Custom intro message when conversation starts
    discovery_prompt_override = Column(Text, nullable=True)  # Custom discovery system prompt
    qualification_prompt_override = Column(Text, nullable=True)  # Custom qualification prompt
    rejection_email_override = Column(Text, nullable=True)  # Custom rejection template
    booking_confirmation_override = Column(Text, nullable=True)  # Custom booking message

    # Prompt metadata for observability
    prompt_version = Column(String, nullable=True)  # Track which prompt version is active
    prompts_last_updated = Column(
        DateTime, nullable=True, default=lambda: datetime.now(timezone.utc)
    )  # When prompts were last customized

    # Relationships
    conversations = relationship("Conversation", back_populates="pt")
