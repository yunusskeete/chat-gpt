from pydantic import BaseModel
from functools import lru_cache
from typing import Optional
import os
from dotenv import load_dotenv

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

    # PT Configuration
    pt_name: str = "Adam Powe"
    pt_specialty: str = "Weight loss and functional fitness for busy professionals"
    pt_target_goals: str = "weight loss, strength building, general fitness"
    pt_age_range: str = "25-45"
    pt_location: str = "London (in-person or online)"
    pt_min_budget: int = 200
    pt_required_commitment: int = 2


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
        google_calendar_credentials_path=os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH", "./google_credentials.json"),
        google_calendar_id=os.getenv("GOOGLE_CALENDAR_ID", "primary"),

        # Email
        sendgrid_api_key=os.getenv("SENDGRID_API_KEY", ""),
        rejection_email_from=os.getenv("REJECTION_EMAIL_FROM", "noreply@demo.com"),

        # PT Configuration
        pt_name=os.getenv("PT_NAME", "Adam Powe"),
        pt_specialty=os.getenv("PT_SPECIALTY", "Weight loss and functional fitness for busy professionals"),
        pt_target_goals=os.getenv("PT_TARGET_GOALS", "weight loss, strength building, general fitness"),
        pt_age_range=os.getenv("PT_AGE_RANGE", "25-45"),
        pt_location=os.getenv("PT_LOCATION", "London (in-person or online)"),
        pt_min_budget=int(os.getenv("PT_MIN_BUDGET", "200")),
        pt_required_commitment=int(os.getenv("PT_REQUIRED_COMMITMENT", "2")),
    )
