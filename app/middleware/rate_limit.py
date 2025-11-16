"""Rate limiting middleware for WhatsApp messages"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent abuse

    Limits:
    - Max 1 message per 3 seconds from same number
    - Max 20 messages per conversation before manual review
    """

    def __init__(self, app, rate_limit_seconds: int = 3):
        super().__init__(app)
        self.rate_limit_seconds = rate_limit_seconds
        self.last_message_time = defaultdict(float)

    async def dispatch(self, request: Request, call_next):
        # Only apply rate limiting to webhook endpoint
        if request.url.path == "/webhook/whatsapp":
            # Get phone number from form data if available
            form_data = await request.form()
            phone_from = form_data.get("From", "")

            if phone_from:
                phone = phone_from.replace("whatsapp:", "")
                current_time = time.time()
                last_time = self.last_message_time.get(phone, 0)

                # Check if enough time has passed
                time_since_last = current_time - last_time

                if time_since_last < self.rate_limit_seconds:
                    logger.warning(
                        f"Rate limit exceeded for {phone}. "
                        f"Time since last: {time_since_last:.2f}s"
                    )
                    # Still return 200 to Twilio but don't process
                    twiml_response = """<?xml version='1.0' encoding='UTF-8'?>
<Response></Response>"""
                    return Response(content=twiml_response, media_type="application/xml")

                # Update last message time
                self.last_message_time[phone] = current_time

        response = await call_next(request)
        return response
