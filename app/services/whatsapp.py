"""Twilio WhatsApp integration service"""
from twilio.rest import Client
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Service for sending WhatsApp messages via Twilio"""

    def __init__(self):
        self.settings = get_settings()
        self.client = Client(
            self.settings.twilio_account_sid,
            self.settings.twilio_auth_token
        )
        self.from_number = f"whatsapp:{self.settings.twilio_whatsapp_number}"

    def send_message(self, to_phone: str, message: str) -> str:
        """
        Send WhatsApp message to a phone number

        Args:
            to_phone: Phone number in format +447123456789
            message: Message content to send

        Returns:
            Message SID from Twilio
        """
        try:
            # Ensure phone number has whatsapp: prefix
            to_whatsapp = f"whatsapp:{to_phone}" if not to_phone.startswith("whatsapp:") else to_phone

            message_obj = self.client.messages.create(
                from_=self.from_number,
                body=message,
                to=to_whatsapp
            )

            logger.info(f"Sent WhatsApp message to {to_phone}: {message_obj.sid}")
            return message_obj.sid

        except Exception as e:
            logger.error(f"Failed to send WhatsApp message to {to_phone}: {e}")
            raise


# Singleton instance
whatsapp_service = WhatsAppService()
