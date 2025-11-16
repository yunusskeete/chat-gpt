"""WhatsApp webhook endpoint for receiving messages from Twilio"""
from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging

from app.database import get_db
from app.models import Conversation, Message, LeadData
from app.tasks import process_message

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Receive incoming WhatsApp messages from Twilio

    Must respond within 1 second with empty TwiML.
    Processing happens in background task.

    Args:
        request: FastAPI request object
        background_tasks: Background tasks
        db: Database session
    """
    try:
        # Get form data from request
        form_data = await request.form()

        # Log all received data for debugging
        logger.info(f"Received webhook data: {dict(form_data)}")

        # Extract required fields
        from_number = form_data.get("From", "")
        body = form_data.get("Body", "")
        message_sid = form_data.get("MessageSid", "")

        if not from_number or not body or not message_sid:
            logger.error(f"Missing required fields. From: {from_number}, Body: {body}, MessageSid: {message_sid}")
            twiml_response = """<?xml version='1.0' encoding='UTF-8'?>
<Response></Response>"""
            return Response(content=twiml_response, media_type="application/xml")

        # Extract phone number (remove whatsapp: prefix)
        phone = from_number.replace("whatsapp:", "")

        logger.info(f"Received WhatsApp message from {phone}: {body[:50]}...")

        # Get or create conversation
        conversation = db.query(Conversation).filter_by(phone_number=phone).first()

        if not conversation:
            # Create new conversation
            conversation = Conversation(
                phone_number=phone,
                status="active",
                pt_id=1,  # Default PT
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

            # Create empty lead data entry
            lead_data = LeadData(conversation_id=conversation.id)
            db.add(lead_data)
            db.commit()

            logger.info(f"Created new conversation {conversation.id} for {phone}")

        # Add background task to process message
        background_tasks.add_task(
            process_message,
            conversation_id=conversation.id,
            phone=phone,
            user_message=body,
            message_sid=message_sid
        )

        # Return empty TwiML response immediately (within 1 second)
        twiml_response = """<?xml version='1.0' encoding='UTF-8'?>
<Response></Response>"""

        return Response(content=twiml_response, media_type="application/xml")

    except Exception as e:
        logger.error(f"Error in WhatsApp webhook: {e}")
        # Still return 200 to Twilio to prevent retries
        twiml_response = """<?xml version='1.0' encoding='UTF-8'?>
<Response></Response>"""
        return Response(content=twiml_response, media_type="application/xml")
