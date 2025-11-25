"""Background task processing for WhatsApp messages"""

import logging
import re
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.agents import DiscoveryAgent, ExtractionAgent, ScoringAgent
from app.database import SessionLocal
from app.models import Conversation, LeadData, Message, PTPreferences
from app.schemas.lead import ExtractedLeadData
from app.services import calendar_service, whatsapp_service

logger = logging.getLogger(__name__)


def _filter_hallucinated_responses(response: str) -> str:
    """
    Remove any hallucinated user responses from the assistant's message.

    This is a safety filter to catch cases where the LLM generates fake user responses
    like "User: 34" or "User: I'm in London" in its output.

    Args:
        response: The raw response from the discovery agent

    Returns:
        Cleaned response with hallucinated user lines removed
    """
    lines = response.split('\n')
    filtered_lines = []

    for line in lines:
        # Skip lines that look like fake user responses
        line_stripped = line.strip()

        # Check for patterns like "User:", "User: something", etc.
        if re.match(r'^User\s*:', line_stripped, re.IGNORECASE):
            logger.warning(f"Filtered hallucinated user response: {line_stripped}")
            continue

        filtered_lines.append(line)

    cleaned = '\n'.join(filtered_lines).strip()

    # Log if we removed anything
    if cleaned != response.strip():
        logger.info(f"Removed hallucinated content. Original length: {len(response)}, Cleaned length: {len(cleaned)}")

    return cleaned


async def process_message(
    conversation_id: int, phone: str, user_message: str, message_sid: str
):
    """
    Process incoming WhatsApp message with LLM agents

    Steps:
    1. Check if MessageSid already processed (idempotency)
    2. Load conversation and message history
    3. Call Discovery Agent
    4. Save assistant response
    5. Send response via WhatsApp
    6. Call Extraction Agent
    7. Update LeadData
    8. If ready, score and take action

    Args:
        conversation_id: ID of the conversation
        phone: Phone number (without whatsapp: prefix)
        user_message: Message content from user
        message_sid: Twilio MessageSid for idempotency
    """
    db = SessionLocal()

    try:
        # 1. Check idempotency - if MessageSid exists, skip processing
        existing_message = (
            db.query(Message).filter_by(twilio_message_sid=message_sid).first()
        )
        if existing_message:
            logger.info(f"Message {message_sid} already processed, skipping")
            return

        # 2. Load conversation and history
        conversation = db.query(Conversation).filter_by(id=conversation_id).first()
        if not conversation:
            logger.error(f"Conversation {conversation_id} not found")
            return

        # Get message history
        messages = (
            db.query(Message)
            .filter_by(conversation_id=conversation_id)
            .order_by(Message.timestamp)
            .all()
        )
        conversation_history = [
            {"role": msg.role, "content": msg.content} for msg in messages
        ]

        # Add current user message to history
        conversation_history.append({"role": "user", "content": user_message})

        # 3. Load PT preferences
        pt = db.query(PTPreferences).filter_by(id=conversation.pt_id).first()
        if not pt:
            logger.error(f"PT preferences not found for conversation {conversation_id}")
            return

        # 4. Call Discovery Agent
        logger.info(f"Calling Discovery Agent for conversation {conversation_id}")
        discovery_agent = DiscoveryAgent()
        assistant_response = await discovery_agent.get_response(
            pt, conversation_history
        )

        # 4.5. Safety filter: Remove any hallucinated user responses
        assistant_response = _filter_hallucinated_responses(assistant_response)

        # 5. Save both messages to database
        user_msg = Message(
            conversation_id=conversation_id,
            role="user",
            content=user_message,
            twilio_message_sid=message_sid,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(user_msg)

        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_response,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(assistant_msg)
        db.commit()

        # 6. Send response via WhatsApp
        logger.info(f"Sending WhatsApp response to {phone}")
        whatsapp_service.send_message(phone, assistant_response)

        # 7. Call Extraction Agent to get structured data
        logger.info(f"Calling Extraction Agent for conversation {conversation_id}")
        extraction_agent = ExtractionAgent()

        # Add assistant response to history for extraction
        conversation_history.append(
            {"role": "assistant", "content": assistant_response}
        )
        extracted_data = await extraction_agent.extract_data(conversation_history)

        # 8. Update or create LeadData
        lead_data = (
            db.query(LeadData).filter_by(conversation_id=conversation_id).first()
        )
        if not lead_data:
            lead_data = LeadData(conversation_id=conversation_id)
            db.add(lead_data)

        # Update fields
        lead_data.goals = extracted_data.goals
        lead_data.age = extracted_data.age
        lead_data.location = extracted_data.location
        lead_data.budget_range = extracted_data.budget_range
        lead_data.commitment_level = extracted_data.commitment_level
        lead_data.availability = extracted_data.availability

        db.commit()

        # 9. If we have all info and haven't scored yet, score and take action
        if extracted_data.has_all_info and lead_data.is_qualified is None:
            logger.info(
                f"Lead has all info, proceeding to score for conversation {conversation_id}"
            )
            await score_and_take_action(conversation_id, phone, pt, extracted_data, db)

        # Update conversation timestamp
        conversation.updated_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as e:
        import traceback

        logger.error(
            f"Error processing message for conversation {conversation_id}: {e}"
        )
        logger.error(f"Traceback: {traceback.format_exc()}")
        db.rollback()

        # Send fallback message to user
        try:
            whatsapp_service.send_message(
                phone, "I'm having trouble processing that. Can you try again?"
            )
        except Exception as send_error:
            logger.error(f"Failed to send fallback message: {send_error}")

    finally:
        db.close()


async def score_and_take_action(
    conversation_id: int,
    phone: str,
    pt: PTPreferences,
    extracted_data: ExtractedLeadData,
    db: Session,
):
    """
    Score lead and take appropriate action (book call or send rejection)

    Args:
        conversation_id: ID of the conversation
        phone: Phone number
        pt: PT preferences
        extracted_data: Extracted lead data
        db: Database session
    """
    try:
        # 1. Call Scoring Agent
        logger.info(f"Calling Scoring Agent for conversation {conversation_id}")
        scoring_agent = ScoringAgent()
        score_result = await scoring_agent.score_lead(pt, extracted_data)

        # 2. Update LeadData with scores
        lead_data = (
            db.query(LeadData).filter_by(conversation_id=conversation_id).first()
        )
        lead_data.qualification_score = score_result.overall_score
        lead_data.is_qualified = score_result.is_qualified
        lead_data.reasoning = score_result.reasoning
        db.commit()

        # 3. Take action based on recommendation
        if score_result.recommended_action == "book_call" and score_result.is_qualified:
            await _handle_qualified_lead(conversation_id, phone, extracted_data, db)
        elif score_result.recommended_action == "send_rejection":
            await _handle_rejected_lead(
                conversation_id, phone, score_result.reasoning, db
            )
        else:
            logger.info(
                f"Needs more info for conversation {conversation_id}, continuing conversation"
            )

    except Exception as e:
        logger.error(
            f"Error scoring and taking action for conversation {conversation_id}: {e}"
        )
        raise


async def _handle_qualified_lead(
    conversation_id: int, phone: str, extracted_data: ExtractedLeadData, db: Session
):
    """Handle qualified lead by booking calendar slot"""
    try:
        # Find available slot
        available_slot = calendar_service.find_next_available_slot()

        # Book calendar event
        meeting_link = calendar_service.book_calendar_event(
            slot_time=available_slot,
            lead_name="Prospect",  # Could extract name if we added that field
            lead_phone=phone,
            lead_goals=extracted_data.goals,
        )

        # Format booking message
        slot_formatted = available_slot.strftime("%A, %B %d at %I:%M %p")
        booking_message = f"""Great news! Based on what you've shared, I think you'd be a great fit for our program. Your goals align perfectly with our specialty.

I've found an available slot for {slot_formatted}. This will be a free intro call to discuss your personalized program.

Looking forward to helping you reach your goals!"""

        # Send booking confirmation via WhatsApp
        whatsapp_service.send_message(phone, booking_message)

        # Save booking message to conversation
        booking_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=booking_message,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(booking_msg)

        # Update conversation status
        conversation = db.query(Conversation).filter_by(id=conversation_id).first()
        conversation.status = "qualified"
        db.commit()

        logger.info(f"Booked call for qualified lead in conversation {conversation_id}")

    except Exception as e:
        logger.error(f"Error handling qualified lead: {e}")
        raise


async def _handle_rejected_lead(
    conversation_id: int, phone: str, reasoning: str, db: Session
):
    """Handle rejected lead by sending polite rejection"""
    try:
        rejection_message = """Thank you so much for your interest in personal training with us!

After reviewing your requirements, I think there might be other options that could be a better fit for your current goals and situation.

I'd recommend exploring:
- Local gym memberships with group classes
- Online fitness programs
- Community fitness groups in your area

We wish you all the best on your fitness journey!"""

        # Send rejection via WhatsApp
        whatsapp_service.send_message(phone, rejection_message)

        # Save rejection message to conversation
        rejection_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=rejection_message,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(rejection_msg)

        # Update conversation status
        conversation = db.query(Conversation).filter_by(id=conversation_id).first()
        conversation.status = "rejected"
        db.commit()

        logger.info(f"Sent rejection for conversation {conversation_id}")

    except Exception as e:
        logger.error(f"Error handling rejected lead: {e}")
        raise
