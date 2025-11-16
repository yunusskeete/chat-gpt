"""Email service for sending rejection emails (optional)"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SendGrid"""

    def __init__(self):
        # For demo purposes, email is optional
        # In production, this would use SendGrid API
        pass

    def send_rejection_email(
        self,
        to_email: str,
        name: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Send polite rejection email with alternative resources

        For demo: Just logs the email that would be sent
        Production: Would send actual email via SendGrid

        Args:
            to_email: Recipient email address
            name: Recipient name
            reason: Optional reason for rejection

        Returns:
            True if sent successfully
        """
        email_content = f"""
        Dear {name},

        Thank you for your interest in personal training with us.

        After reviewing your requirements, we think there might be better options
        that align more closely with your current goals and budget.

        We recommend:
        - Local gym memberships with group classes
        - Online fitness programs
        - Community fitness groups in your area

        We wish you all the best on your fitness journey!

        Best regards,
        The PT Team
        """

        # For demo, just log
        logger.info(f"Would send rejection email to {to_email}:\n{email_content}")

        # In production, send actual email via SendGrid
        return True


# Singleton instance
email_service = EmailService()
