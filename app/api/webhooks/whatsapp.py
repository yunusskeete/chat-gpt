"""WhatsApp webhook endpoint for receiving messages from Twilio"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Conversation, LeadData, Message, PTPreferences
from app.prompts.manager import PromptManager
from app.services import whatsapp_service
from app.tasks import process_message

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
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
            logger.error(
                f"Missing required fields. From: {from_number}, Body: {body}, MessageSid: {message_sid}"
            )
            twiml_response = """<?xml version='1.0' encoding='UTF-8'?>
<Response></Response>"""
            return Response(content=twiml_response, media_type="application/xml")

        # Extract phone number (remove whatsapp: prefix)
        phone = from_number.replace("whatsapp:", "")  # type: ignore

        logger.info(f"Received WhatsApp message from {phone}: {body[:50]}...")

        # Check for clear_chat command
        if body.strip().lower() == "clear_chat":  # type: ignore
            # Get the most recent active conversation
            conversation = (
                db.query(Conversation)
                .filter_by(phone_number=phone, status="active")
                .order_by(Conversation.created_at.desc())
                .first()
            )
            if conversation:
                # Delete all messages for this conversation
                db.query(Message).filter_by(conversation_id=conversation.id).delete()
                # Delete lead data
                db.query(LeadData).filter_by(conversation_id=conversation.id).delete()
                # Delete the conversation itself
                db.query(Conversation).filter_by(id=conversation.id).delete()
                db.commit()
                logger.info(f"Cleared conversation {conversation.id} for {phone}")
            else:
                logger.info(f"No active conversation to clear for {phone}")

            # Return empty TwiML response
            twiml_response = """<?xml version='1.0' encoding='UTF-8'?>
<Response></Response>"""
            return Response(content=twiml_response, media_type="application/xml")

        # Check for new_chat command
        if body.strip().lower() == "new_chat":  # type: ignore
            # Archive all active conversations for this number
            active_conversations = (
                db.query(Conversation)
                .filter_by(phone_number=phone, status="active")
                .all()
            )
            for conv in active_conversations:
                conv.status = "archived"
                logger.info(f"Archived conversation {conv.id} for {phone}")
            db.commit()

            # Return empty TwiML response - next message will create new conversation
            twiml_response = """<?xml version='1.0' encoding='UTF-8'?>
<Response></Response>"""
            return Response(content=twiml_response, media_type="application/xml")

        # Get or create active conversation (most recent active one)
        conversation = (
            db.query(Conversation)
            .filter_by(phone_number=phone, status="active")
            .order_by(Conversation.created_at.desc())
            .first()
        )

        if not conversation:
            # Create new conversation
            conversation = Conversation(
                phone_number=phone,
                status="active",
                pt_id=1,  # Default PT
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

            # Create empty lead data entry
            lead_data = LeadData(conversation_id=conversation.id)
            db.add(lead_data)
            db.commit()

            logger.info(f"Created new conversation {conversation.id} for {phone}")

            # Send intro message for new conversation
            pt = db.query(PTPreferences).filter_by(id=conversation.pt_id).first()
            if pt:
                prompt_manager = PromptManager(pt)
                intro_message = prompt_manager.get_intro_message()

                # Send intro message via WhatsApp
                whatsapp_service.send_message(phone, intro_message)

                # Save intro message to conversation
                intro_msg = Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=intro_message,
                    timestamp=datetime.now(timezone.utc),
                )
                db.add(intro_msg)
                db.commit()

                logger.info(f"Sent intro message for new conversation {conversation.id}")

            # Return early - don't process the first message that triggered conversation creation
            # User needs to respond to intro message first
            twiml_response = """<?xml version='1.0' encoding='UTF-8'?>
<Response></Response>"""
            return Response(content=twiml_response, media_type="application/xml")

        # Add background task to process message
        background_tasks.add_task(
            process_message,
            conversation_id=conversation.id,  # type: ignore
            phone=phone,
            user_message=body,  # type: ignore
            message_sid=message_sid,  # type: ignore
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
