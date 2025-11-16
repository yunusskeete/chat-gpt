"""Google Calendar integration service"""
from datetime import datetime, timedelta
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CalendarService:
    """Service for managing calendar bookings"""

    def __init__(self):
        # For demo purposes, we'll mock calendar functionality
        # In production, this would use Google Calendar API
        pass

    def find_next_available_slot(self, days_ahead: int = 7) -> datetime:
        """
        Find next available 1-hour slot in PT's calendar

        For demo: Returns next weekday at 10am
        Production: Would query actual Google Calendar availability

        Args:
            days_ahead: Number of days to look ahead

        Returns:
            datetime of available slot
        """
        # Simple mock: find next weekday (Mon-Fri) at 10am
        current_date = datetime.now()
        next_date = current_date + timedelta(days=1)

        # Find next weekday
        while next_date.weekday() >= 5:  # Saturday=5, Sunday=6
            next_date += timedelta(days=1)

        # Set to 10am
        available_slot = next_date.replace(hour=10, minute=0, second=0, microsecond=0)

        logger.info(f"Found available slot: {available_slot}")
        return available_slot

    def book_calendar_event(
        self,
        slot_time: datetime,
        lead_name: str,
        lead_phone: str,
        lead_goals: Optional[str] = None
    ) -> str:
        """
        Create calendar event and return meeting link

        For demo: Returns mock Google Meet link
        Production: Would create actual Google Calendar event

        Args:
            slot_time: DateTime for the appointment
            lead_name: Name of the lead
            lead_phone: Phone number of the lead
            lead_goals: Fitness goals (optional)

        Returns:
            Meeting link or event details
        """
        # Mock calendar event creation
        event_details = {
            "time": slot_time,
            "duration": "1 hour",
            "attendee": lead_name,
            "phone": lead_phone,
            "goals": lead_goals or "Not specified"
        }

        # In production, this would create a real Google Calendar event
        # and return the actual Google Meet link
        mock_meet_link = f"https://meet.google.com/mock-{slot_time.strftime('%Y%m%d%H%M')}"

        logger.info(f"Created calendar event for {lead_name} at {slot_time}")
        return mock_meet_link


# Singleton instance
calendar_service = CalendarService()
