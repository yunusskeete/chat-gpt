import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel

from app.config.pt_defaults import PTDefaults

load_dotenv()


class Settings(BaseModel):
    # FastAPI
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "sqlite:///./pt_chatbot.db"

    # Anthropic
    anthropic_api_key: str = ""

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_number: str = ""

    # Google Calendar (optional)
    google_calendar_credentials_path: str = "./google_credentials.json"
    google_calendar_id: str = "primary"

    # Email (optional)
    sendgrid_api_key: str = ""
    rejection_email_from: str = "noreply@demo.com"

    # PT Configuration (defaults from pt_defaults.py)
    pt_name: str = PTDefaults.NAME
    pt_specialty: str = PTDefaults.SPECIALTY
    pt_target_goals: str = PTDefaults.TARGET_GOALS
    pt_age_range: str = PTDefaults.AGE_RANGE
    pt_location: str = PTDefaults.LOCATION
    pt_min_budget: int = PTDefaults.MIN_BUDGET
    pt_required_commitment: int = PTDefaults.REQUIRED_COMMITMENT

    # Extended PT context fields
    pt_bio: str = PTDefaults.BIO
    pt_years_experience: int = PTDefaults.YEARS_EXPERIENCE
    pt_certifications: str = PTDefaults.CERTIFICATIONS
    pt_additional_info: str = PTDefaults.ADDITIONAL_INFO
    pt_training_philosophy: str = PTDefaults.TRAINING_PHILOSOPHY
    pt_ideal_client: str = PTDefaults.IDEAL_CLIENT
    pt_disqualifiers: str = PTDefaults.DISQUALIFIERS


@lru_cache()
def get_settings() -> Settings:
    return Settings(
        # FastAPI
        debug=os.getenv("DEBUG", "True").lower() == "true",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        # Database
        database_url=os.getenv("DATABASE_URL", "sqlite:///./pt_chatbot.db"),
        # Anthropic
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        # Twilio
        twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID", ""),
        twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN", ""),
        twilio_whatsapp_number=os.getenv("TWILIO_WHATSAPP_NUMBER", ""),
        # Google Calendar
        google_calendar_credentials_path=os.getenv(
            "GOOGLE_CALENDAR_CREDENTIALS_PATH", "./google_credentials.json"
        ),
        google_calendar_id=os.getenv("GOOGLE_CALENDAR_ID", "primary"),
        # Email
        sendgrid_api_key=os.getenv("SENDGRID_API_KEY", ""),
        rejection_email_from=os.getenv("REJECTION_EMAIL_FROM", "noreply@demo.com"),
        # PT Configuration (env vars override pt_defaults.py)
        pt_name=os.getenv("PT_NAME", PTDefaults.NAME),
        pt_specialty=os.getenv("PT_SPECIALTY", PTDefaults.SPECIALTY),
        pt_target_goals=os.getenv("PT_TARGET_GOALS", PTDefaults.TARGET_GOALS),
        pt_age_range=os.getenv("PT_AGE_RANGE", PTDefaults.AGE_RANGE),
        pt_location=os.getenv("PT_LOCATION", PTDefaults.LOCATION),
        pt_min_budget=int(os.getenv("PT_MIN_BUDGET", str(PTDefaults.MIN_BUDGET))),
        pt_required_commitment=int(
            os.getenv("PT_REQUIRED_COMMITMENT", str(PTDefaults.REQUIRED_COMMITMENT))
        ),
        # Extended context fields (env vars override, or use file defaults)
        pt_bio=os.getenv("PT_BIO", PTDefaults.BIO),
        pt_years_experience=int(
            os.getenv("PT_YEARS_EXPERIENCE", str(PTDefaults.YEARS_EXPERIENCE))
        ),
        pt_certifications=os.getenv("PT_CERTIFICATIONS", PTDefaults.CERTIFICATIONS),
        pt_additional_info=os.getenv("PT_ADDITIONAL_INFO", PTDefaults.ADDITIONAL_INFO),
        pt_training_philosophy=os.getenv(
            "PT_TRAINING_PHILOSOPHY", PTDefaults.TRAINING_PHILOSOPHY
        ),
        pt_ideal_client=os.getenv("PT_IDEAL_CLIENT", PTDefaults.IDEAL_CLIENT),
        pt_disqualifiers=os.getenv("PT_DISQUALIFIERS", PTDefaults.DISQUALIFIERS),
    )
