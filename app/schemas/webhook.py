from pydantic import BaseModel, Field


class WhatsAppWebhook(BaseModel):
    """Schema for Twilio WhatsApp webhook data"""
    From: str = Field(..., alias="From")
    To: str = Field(..., alias="To")
    Body: str = Field(..., alias="Body")
    MessageSid: str = Field(..., alias="MessageSid")

    class Config:
        populate_by_name = True
