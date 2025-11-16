# PT Lead Qualification Chatbot - Project Specification

## Project Overview

Build a WhatsApp chatbot that qualifies personal training leads through conversational discovery, scores prospects against PT preferences, and automatically books intro calls for qualified leads or sends polite rejections.

## Target User

Personal trainers who receive prospect inquiries via WhatsApp and need to efficiently qualify leads before investing time in calls.

## Core Workflow

1. **Discovery Phase**: Chatbot converses with prospect to discover goals, age, location, budget, commitment level, and availability
2. **Qualification Phase**: System extracts structured data and scores prospect against PT's pre-specified preferences
3. **Action Phase**: 
   - If qualified: Book intro call via Google Calendar and send booking confirmation
   - If not qualified: Send polite rejection message with alternative resources

## Technical Stack

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: SQLite with SQLAlchemy ORM
- **AI Framework**: Pydantic AI
- **LLM**: Claude Sonnet 4.5 (via Anthropic API)

### Integrations
- **WhatsApp**: Twilio WhatsApp API (sandbox for demo)
- **Calendar**: Google Calendar API
- **Email**: SendGrid or Resend (for rejection emails)

### Development Tools
- **Environment Management**: python-venv
- **Dependencies**: pip with requirements.txt
- **Configuration**: python-dotenv for secrets

## System Architecture

```
WhatsApp Message → Twilio Webhook → FastAPI Endpoint → Background Task → LLM Agents → Action (Calendar/Email) → Response to WhatsApp
```

### Key Design Patterns

1. **Async Webhook Processing**: Respond to Twilio within 1s, process LLM calls in background
2. **Multi-Agent System**: Separate agents for discovery, extraction, and scoring
3. **Stateful Conversations**: Track conversation state in SQLite
4. **Idempotent Message Handling**: Prevent duplicate processing using Twilio's MessageSid

## Database Schema

### Conversations Table
```python
- id: Integer (Primary Key)
- phone_number: String (Unique, Indexed)
- status: String (active, qualified, rejected, completed)
- pt_id: Integer (which PT this conversation belongs to)
- created_at: DateTime
- updated_at: DateTime
```

### Messages Table
```python
- id: Integer (Primary Key)
- conversation_id: Integer (Foreign Key)
- role: String (user, assistant)
- content: Text
- timestamp: DateTime
- twilio_message_sid: String (Unique, for idempotency)
```

### LeadData Table
```python
- id: Integer (Primary Key)
- conversation_id: Integer (Foreign Key, Unique)
- goals: String (nullable)
- age: Integer (nullable)
- location: String (nullable)
- budget_range: String (nullable)
- commitment_level: Integer (nullable, 1-10)
- availability: String (nullable)
- qualification_score: Integer (nullable, 1-100)
- is_qualified: Boolean (nullable)
- reasoning: Text (nullable)
```

### PTPreferences Table
```python
- id: Integer (Primary Key)
- name: String
- target_goals: Text (e.g., "weight loss, muscle building")
- age_range: String (e.g., "25-45")
- preferred_location: String
- min_budget: Integer
- required_commitment: Integer (sessions per week)
- specialty: Text
```

## AI Agent Architecture

### Agent 1: Discovery Agent
**Purpose**: Conduct natural conversation to extract lead information

**System Prompt Template**:
```
You are a friendly fitness assistant helping qualify potential clients for {pt_name}.

PT Specialization: {pt_specialty}
PT Preferences:
- Target clients: {target_goals}
- Age range: {age_range}
- Location: {location}
- Budget: £{min_budget}+/month
- Commitment: {required_commitment}x sessions/week

Your job:
- Have a warm, natural conversation to discover the prospect's:
  * Fitness goals
  * Age
  * Location
  * Budget expectations
  * Commitment level (how many sessions per week)
  * Availability (days/times)
- Ask ONE question at a time
- Be encouraging and positive
- Don't be robotic or interrogate
- Extract information gradually through conversation
- When you have gathered all information naturally, acknowledge you have what you need

Keep responses concise (2-3 sentences max) and conversational.
```

**Input**: User message + conversation history
**Output**: String (next conversational response)

### Agent 2: Extraction Agent
**Purpose**: Extract structured data from conversation history

**System Prompt**:
```
Extract structured lead information from the conversation history provided.

Be conservative - only extract information that was clearly stated.
If information wasn't mentioned, leave it as null.

Also determine if you have enough information to score this lead (goals, rough budget, commitment level are minimum required).
```

**Input**: Full conversation history
**Output**: Pydantic model `ExtractedLeadData`
```python
class ExtractedLeadData(BaseModel):
    goals: str | None
    age: int | None
    location: str | None
    budget_range: str | None
    commitment_level: int | None  # 1-10 scale
    availability: str | None
    has_all_info: bool  # Ready to score?
```

### Agent 3: Scoring Agent
**Purpose**: Score lead against PT preferences and recommend action

**System Prompt Template**:
```
Score this lead based on the PT's preferences.

PT Preferences:
{pt_preferences}

Lead Data:
{lead_data}

Scoring Criteria:
- Goal alignment (30%): Do their goals match PT specialty?
- Budget fit (25%): Can they afford the PT's rates?
- Location compatibility (20%): Are they in the right location?
- Commitment level (15%): Will they commit to required frequency?
- Availability match (10%): Can they train at PT's available times?

Provide:
1. Overall score (1-100)
2. Boolean: is_qualified (true if score >= 70)
3. Reasoning (brief explanation)
4. Recommended action: book_call, send_rejection, or needs_more_info
```

**Input**: PT preferences + Lead data
**Output**: Pydantic model `QualificationScore`
```python
class QualificationScore(BaseModel):
    overall_score: int  # 1-100
    is_qualified: bool
    reasoning: str
    recommended_action: Literal["book_call", "send_rejection", "needs_more_info"]
```

## API Endpoints

### POST /webhook/whatsapp
**Purpose**: Receive incoming WhatsApp messages from Twilio

**Request Body** (form-data from Twilio):
```
From: whatsapp:+447123456789
To: whatsapp:+14155238886
Body: "Hi, I'm interested in personal training"
MessageSid: SM1234567890abcdef
```

**Response**: Empty TwiML XML (respond within 1 second)
```xml
<?xml version='1.0' encoding='UTF-8'?>
<Response></Response>
```

**Processing Flow**:
1. Parse Twilio webhook data
2. Extract phone number and message body
3. Store message with MessageSid (for idempotency)
4. Trigger background task for LLM processing
5. Return empty TwiML immediately

### GET /health
**Purpose**: Health check endpoint

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-15T10:30:00Z"
}
```

### POST /admin/test-message (Optional for demo)
**Purpose**: Send test message without WhatsApp (for development)

**Request Body**:
```json
{
  "phone": "+447123456789",
  "message": "Hi, I want to get fit"
}
```

## Background Task Processing

### process_message(conversation_id, phone, user_message, message_sid)

**Steps**:
1. Check if MessageSid already processed (idempotency)
2. Load conversation and message history from DB
3. Load PT preferences
4. Call Discovery Agent with conversation history
5. Save assistant response to DB
6. Send response via Twilio
7. Call Extraction Agent to get structured data
8. Update LeadData table with extracted information
9. If `has_all_info == True` and not already scored:
   - Call score_and_take_action()

### score_and_take_action(conversation_id, phone, pt_preferences)

**Steps**:
1. Load LeadData from DB
2. Call Scoring Agent with PT preferences and lead data
3. Update LeadData with scores
4. If qualified:
   - Call Google Calendar API to find available slot
   - Create calendar event
   - Send booking confirmation via WhatsApp
5. If not qualified:
   - Send polite rejection via WhatsApp
   - Optionally send rejection email with resources

## Integration Specifications

### Twilio WhatsApp Setup

**Sandbox Setup** (for demo):
1. Create Twilio account
2. Navigate to Messaging → Try it out → Send a WhatsApp message
3. Join sandbox by sending code to provided number
4. Configure webhook URL: `https://your-domain.com/webhook/whatsapp`

**Environment Variables**:
```
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=xxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

**Send Message Function**:
```python
from twilio.rest import Client

def send_whatsapp_message(to_phone: str, message: str):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_=f'whatsapp:{TWILIO_WHATSAPP_NUMBER}',
        body=message,
        to=f'whatsapp:{to_phone}'
    )
    return message.sid
```

### Google Calendar Integration

**Setup**:
1. Create Google Cloud project
2. Enable Google Calendar API
3. Create OAuth 2.0 credentials (or service account for demo)
4. Download credentials JSON

**Environment Variables**:
```
GOOGLE_CALENDAR_CREDENTIALS_PATH=./google_credentials.json
GOOGLE_CALENDAR_ID=primary
```

**Find Available Slot Function** (simplified for demo):
```python
def find_next_available_slot(days_ahead: int = 7) -> datetime:
    """Find next available 1-hour slot in PT's calendar"""
    # For demo: return next weekday at 10am
    # Production: query actual calendar availability
    pass

def book_calendar_event(lead_data, slot_time: datetime) -> str:
    """Create calendar event and return meeting link"""
    # Create Google Calendar event
    # Return Google Meet link or event link
    pass
```

### Email Service (Optional for demo)

**Environment Variables**:
```
SENDGRID_API_KEY=SG.xxxx
REJECTION_EMAIL_FROM=noreply@yourpt.com
```

**Send Rejection Email**:
```python
def send_rejection_email(to_email: str, name: str):
    # Send polite rejection with alternative resources
    pass
```

### Anthropic API

**Environment Variables**:
```
ANTHROPIC_API_KEY=sk-ant-xxxx
```

**Pydantic AI Setup**:
```python
from pydantic_ai import Agent

agent = Agent(
    'claude-opus-4-1-20250805',
    system_prompt="...",
    output_type=YourPydanticModel
)
```

## Project Structure

```
pt-chatbot/
├── .env                          # Environment variables (not committed)
├── .env.example                  # Template for environment variables
├── requirements.txt              # Python dependencies
├── README.md                     # Setup and usage instructions
├── main.py                       # FastAPI application entry point
├── app/
│   ├── __init__.py
│   ├── config.py                 # Configuration and environment variables
│   ├── database.py               # Database connection and session
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── conversation.py      # Conversation SQLAlchemy model
│   │   ├── message.py           # Message SQLAlchemy model
│   │   ├── lead_data.py         # LeadData SQLAlchemy model
│   │   └── pt_preferences.py    # PTPreferences SQLAlchemy model
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── lead.py              # Pydantic schemas for lead data
│   │   └── webhook.py           # Pydantic schemas for webhooks
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── discovery.py         # Discovery agent
│   │   ├── extraction.py        # Extraction agent
│   │   └── scoring.py           # Scoring agent
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── whatsapp.py          # Twilio WhatsApp integration
│   │   ├── calendar.py          # Google Calendar integration
│   │   └── email.py             # Email service (optional)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── webhooks/
│   │       ├── __init__.py
│   │       └── whatsapp.py      # WhatsApp webhook endpoint
│   │
│   └── tasks/
│       ├── __init__.py
│       └── message_processor.py # Background task processing
│
├── scripts/
│   ├── init_db.py               # Initialize database with sample PT
│   └── seed_data.py             # Seed sample conversations (for testing)
│
└── tests/
    ├── __init__.py
    ├── test_agents.py           # Test AI agents
    ├── test_webhooks.py         # Test webhook endpoints
    └── test_services.py         # Test integrations
```

## Environment Variables (.env.example)

```bash
# FastAPI
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./pt_chatbot.db

# Anthropic
ANTHROPIC_API_KEY=sk-ant-xxxx

# Twilio
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=xxxx
TWILIO_WHATSAPP_NUMBER=+14155238886

# Google Calendar (optional for demo - can mock)
GOOGLE_CALENDAR_CREDENTIALS_PATH=./google_credentials.json
GOOGLE_CALENDAR_ID=primary

# Email (optional for demo)
SENDGRID_API_KEY=SG.xxxx
REJECTION_EMAIL_FROM=noreply@demo.com

# PT Configuration (could also be in DB)
PT_NAME=Adam Powe
PT_SPECIALTY=Weight loss and functional fitness for busy professionals
PT_TARGET_GOALS=weight loss, strength building, general fitness
PT_AGE_RANGE=25-45
PT_LOCATION=London (in-person or online)
PT_MIN_BUDGET=200
PT_REQUIRED_COMMITMENT=2
```

## Dependencies (requirements.txt)

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-ai==0.0.13
anthropic==0.37.0
twilio==8.10.0
python-dotenv==1.0.0
httpx==0.25.1

# Google Calendar (optional)
google-api-python-client==2.108.0
google-auth-httplib2==0.1.1
google-auth-oauthlib==1.1.0

# Email (optional)
sendgrid==6.11.0

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
```

## Sample PT Preferences (for database seeding)

```python
sample_pt = {
    "name": "Adam Powe",
    "target_goals": "weight loss, functional fitness, strength training for professionals",
    "age_range": "25-45",
    "preferred_location": "London (Shoreditch/Central), also offers online",
    "min_budget": 200,  # £200/month
    "required_commitment": 2,  # 2x per week minimum
    "specialty": "Specialized in helping busy professionals lose weight and build strength through efficient, science-based training programs"
}
```

## Demo Conversation Flow Example

**User**: Hi, I'm interested in personal training

**Bot**: Great to hear! I'd love to help you find the right fit with Adam. What are your main fitness goals right now?

**User**: I want to lose about 20 pounds and get stronger

**Bot**: Excellent goals! Weight loss and strength building are definitely achievable. Can I ask your age? (Just to ensure the program is tailored appropriately)

**User**: I'm 32

**Bot**: Perfect! Are you based in London, or would you be interested in online training?

**User**: I'm in Shoreditch actually

**Bot**: That's great - Adam trains in Central London! How many times per week could you realistically commit to training sessions?

**User**: Probably 2-3 times a week

**Bot**: That's a solid commitment. Just one more thing - what's your budget range for monthly training? Adam's programs typically start around £200/month for 2x weekly sessions.

**User**: Yeah I can do £250/month

**Bot**: Fantastic! Let me check if you'd be a good match... 

[System scores lead: 85/100 - Qualified]

**Bot**: Great news! Based on what you've shared, I think you'd be a great fit for Adam's program. Your goals align perfectly with his specialty in weight loss and strength training for busy professionals. Would you like to book a free intro call with Adam to discuss your program?

**User**: Yes please!

**Bot**: Perfect! I've found an available slot for Tuesday, Nov 19th at 10:00 AM. I've sent you a calendar invite to book@demo.com. Looking forward to helping you reach your goals! 🎯

## Error Handling

### Webhook Errors
- If MessageSid already exists: Log and return 200 (idempotent)
- If database error: Log error, send fallback message to user
- If Twilio timeout: Background task continues processing

### LLM Errors
- If API rate limit: Retry with exponential backoff
- If API error: Send fallback message: "I'm having trouble processing that. Can you try again?"
- If timeout: Log error, notify PT manually

### Integration Errors
- If Calendar API fails: Fall back to manual booking message
- If Email send fails: Log error, continue with WhatsApp notification

## Rate Limiting & Safety

1. **Message Rate Limiting**: Max 1 message per 3 seconds from same number
2. **Conversation Timeout**: Auto-close conversations after 24 hours of inactivity
3. **Max Messages**: Limit to 20 messages per conversation before manual review
4. **Duplicate Prevention**: Use Twilio MessageSid for idempotency

## Testing Strategy

### Unit Tests
- Test each agent with sample inputs
- Test extraction logic with various conversation formats
- Test scoring algorithm with edge cases

### Integration Tests
- Mock Twilio webhooks
- Test database operations
- Test background task execution

### Manual Testing
1. Join Twilio sandbox
2. Send test messages from your phone
3. Verify conversation flow
4. Check database state
5. Test qualification and rejection paths

## Demo Limitations & Production Considerations

### Demo Limitations
- Twilio sandbox (only 5 test numbers)
- SQLite database (not for production scale)
- Simplified calendar booking (mock availability)
- No authentication/authorization
- Single PT hardcoded in environment

### Production Improvements
- Full Twilio WhatsApp Business API with verified number
- PostgreSQL database
- Multi-PT support with admin dashboard
- Real calendar availability checking
- Proper error monitoring (Sentry)
- Analytics and reporting
- Conversation review interface for PTs
- Instagram DM integration (requires Meta Business verification)
- More sophisticated scoring (ML-based eventually)

## Success Metrics

For the demo, success means:
1. ✅ Receive WhatsApp message via Twilio webhook
2. ✅ Conduct natural multi-turn conversation
3. ✅ Extract structured data correctly
4. ✅ Score lead accurately against PT preferences
5. ✅ Send appropriate booking or rejection message
6. ✅ Complete flow in <30 seconds end-to-end

## Development Workflow

1. **Setup**: Clone repo, create `.env` from template, install dependencies
2. **Initialize DB**: Run `python scripts/init_db.py`
3. **Start Server**: `uvicorn main:app --reload`
4. **Expose Webhook**: Use ngrok to expose localhost to Twilio
5. **Configure Twilio**: Point webhook to ngrok URL
6. **Test**: Send WhatsApp message to Twilio sandbox number
7. **Iterate**: Monitor logs, test different conversation flows

## Deployment (for demo)

**Quick Deploy with Railway/Render**:
1. Connect GitHub repo
2. Set environment variables
3. Deploy with `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Use production URL in Twilio webhook config

**Ngrok (local development)**:
```bash
ngrok http 8000
# Use HTTPS URL in Twilio webhook config
```

## Security Considerations

- Never commit `.env` file
- Use environment variables for all secrets
- Validate webhook signatures from Twilio (production)
- Rate limit endpoints to prevent abuse
- Sanitize user input before storing in DB
- Use HTTPS for all webhooks

## Future Enhancements

1. **Multi-PT Platform**: Support multiple PTs with admin dashboard
2. **Advanced Scheduling**: Integration with Calendly or similar
3. **Payment Integration**: Stripe for booking deposits
4. **Instagram DM Support**: When user gets Meta Business approval
5. **Analytics Dashboard**: Track conversion rates, popular goals, etc.
6. **Conversation Templates**: Allow PTs to customize conversation flow
7. **AI Training**: Fine-tune on successful vs unsuccessful conversations
8. **Voice Notes**: Handle WhatsApp voice messages
9. **Multi-language**: Support multiple languages
10. **CRM Integration**: Export leads to HubSpot, Salesforce, etc.

---

## Implementation Notes for Claude Code

**Priority Build Order**:
1. Database models and initialization script
2. FastAPI app with health endpoint
3. Twilio webhook endpoint (basic parsing)
4. Discovery agent (get basic conversation working)
5. Background task processing
6. Extraction and scoring agents
7. Calendar/Email integration
8. Error handling and polish

**Key Testing Points**:
- Can receive webhook from Twilio ✓
- Can save message to database ✓
- Can retrieve conversation history ✓
- Can generate conversational response ✓
- Can extract structured data ✓
- Can score and make decision ✓
- Can send WhatsApp message back ✓

**Simplifications for Demo**:
- Mock calendar availability (just return "next Tuesday at 10am")
- Skip email rejection, just do WhatsApp
- Single PT hardcoded in config
- No admin UI, just API and WhatsApp

**Critical Success Factors**:
1. Respond to Twilio webhook within 1 second
2. Natural conversation flow (not robotic)
3. Accurate data extraction
4. Sensible scoring decisions
5. Clear booking/rejection messages

Good luck building! 🚀