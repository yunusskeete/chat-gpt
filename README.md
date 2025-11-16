# chat-gpt
Chat-GPT: Chat Gateway for Personal Trainers.

A WhatsApp chatbot that qualifies personal training leads through conversational discovery, scores prospects against PT preferences, and automatically books intro calls for qualified leads.

## Features

- **Natural Conversation**: AI-powered discovery agent conducts warm, conversational lead qualification
- **Smart Extraction**: Automatically extracts structured data (goals, budget, location, etc.) from conversations
- **Intelligent Scoring**: Scores leads against PT preferences with explainable reasoning
- **Automated Actions**: Books calendar slots for qualified leads or sends polite rejections
- **Idempotent Processing**: Prevents duplicate message handling using Twilio MessageSid
- **Rate Limiting**: Built-in protection against message spam

## Tech Stack

- **Backend**: FastAPI + Python 3.11+
- **AI**: Pydantic AI + Claude Sonnet 4.5 (Anthropic)
- **Database**: SQLite + SQLAlchemy ORM
- **Messaging**: Twilio WhatsApp API
- **Calendar**: Google Calendar API (mock implementation for demo)

## Project Structure

```
qualify-ai/
├── app/
│   ├── agents/           # AI agents (discovery, extraction, scoring)
│   ├── api/              # FastAPI endpoints
│   ├── middleware/       # Rate limiting middleware
│   ├── models/           # SQLAlchemy database models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # External integrations (WhatsApp, Calendar)
│   ├── tasks/            # Background task processing
│   ├── config.py         # Configuration management
│   └── database.py       # Database setup
├── scripts/
│   └── init_db.py        # Database initialization script
├── main.py               # FastAPI application entry point
├── requirements.txt      # Python dependencies
└── .env.example          # Environment variables template
```

## Setup Instructions

### 1. Prerequisites

- Python 3.11 or higher
- Twilio account (for WhatsApp API)
- Anthropic API key (for Claude)
- ngrok (for local development) or a deployment platform

### 2. Clone and Install

```bash
# Clone the repository
git clone <your-repo-url>
cd qualify-ai

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Required environment variables:

```bash
# Anthropic API key (required)
ANTHROPIC_API_KEY=sk-ant-xxxx

# Twilio credentials (required for WhatsApp)
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=xxxx
TWILIO_WHATSAPP_NUMBER=+14155238886

# PT Configuration (customize for your PT)
PT_NAME=Adam Powe
PT_SPECIALTY=Weight loss and functional fitness for busy professionals
PT_TARGET_GOALS=weight loss, strength building, general fitness
PT_AGE_RANGE=25-45
PT_LOCATION=London (in-person or online)
PT_MIN_BUDGET=200
PT_REQUIRED_COMMITMENT=2
```

### 4. Initialize Database

```bash
# Run the database initialization script
python scripts/init_db.py
```

This will:
- Create all database tables
- Seed the PT preferences from your environment variables

### 5. Start the Server

```bash
# Development mode (with auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 6. Expose Webhook (Development)

Use ngrok to expose your local server to the internet:

```bash
# Install ngrok (if not already installed)
# Visit https://ngrok.com/download

# Start ngrok
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### 7. Configure Twilio Webhook

1. Go to [Twilio Console](https://console.twilio.com)
2. Navigate to Messaging → Try it out → Send a WhatsApp message
3. Join the sandbox by sending the code to the provided number
4. Configure the webhook URL:
   - **When a message comes in**: `https://your-ngrok-url.ngrok.io/webhook/whatsapp`
   - **Method**: POST
5. Save the configuration

## Testing the Chatbot

### Join Twilio Sandbox

1. From your phone, send the join code to the Twilio sandbox number
2. You should receive a confirmation message

### Start a Conversation

Send a message like:
```
Hi, I'm interested in personal training
```

### Expected Flow

The bot will:
1. Ask about your fitness goals
2. Ask about your age
3. Ask about your location
4. Ask about commitment level (sessions per week)
5. Ask about budget
6. Extract and score your information
7. Either book a call or send a polite rejection

### Example Conversation

**You**: Hi, I'm interested in personal training

**Bot**: Great to hear! I'd love to help you find the right fit with Adam. What are your main fitness goals right now?

**You**: I want to lose about 20 pounds and get stronger

**Bot**: Excellent goals! Weight loss and strength building are definitely achievable. Can I ask your age?

**You**: I'm 32

**Bot**: Perfect! Are you based in London, or would you be interested in online training?

**You**: I'm in Shoreditch actually

**Bot**: That's great - Adam trains in Central London! How many times per week could you realistically commit to training sessions?

**You**: Probably 2-3 times a week

**Bot**: That's a solid commitment. Just one more thing - what's your budget range for monthly training?

**You**: Yeah I can do £250/month

**Bot**: Great news! Based on what you've shared, I think you'd be a great fit for Adam's program...

## API Endpoints

### Health Check
```
GET /health
```

Returns:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-15T10:30:00Z"
}
```

### WhatsApp Webhook
```
POST /webhook/whatsapp
```

Receives incoming WhatsApp messages from Twilio. Responds within 1 second with empty TwiML and processes in background.

### Root
```
GET /
```

Returns API information and available endpoints.

## Database Schema

### Conversations
Tracks each lead conversation with status and timestamps.

### Messages
Stores all messages (user and assistant) with Twilio MessageSid for idempotency.

### LeadData
Contains extracted structured data and qualification scores.

### PTPreferences
Stores PT's preferences for lead matching.

## AI Agents

### Discovery Agent
- Conducts natural, conversational lead qualification
- Asks one question at a time
- Warm and encouraging tone
- Gradually extracts required information

### Extraction Agent
- Parses conversation history
- Extracts structured data conservatively
- Determines if enough info collected for scoring

### Scoring Agent
- Scores leads 1-100 based on:
  - Goal alignment (30%)
  - Budget fit (25%)
  - Location compatibility (20%)
  - Commitment level (15%)
  - Availability (10%)
- Provides reasoning for decisions
- Recommends action (book_call, send_rejection, needs_more_info)

## Rate Limiting

Built-in rate limiting:
- Max 1 message per 3 seconds from same number
- Prevents spam and abuse
- Returns 200 to Twilio to avoid retries

## Error Handling

- **Idempotency**: Duplicate MessageSids are ignored
- **Fallback Messages**: Errors trigger "Can you try again?" message
- **Logging**: Comprehensive logging for debugging
- **Graceful Degradation**: Always returns 200 to Twilio

## Deployment

### Quick Deploy Options

**Railway.app**:
```bash
# Connect GitHub repo
# Set environment variables in Railway dashboard
# Deploy
```

**Render.com**:
```bash
# Connect GitHub repo
# Set environment variables
# Build Command: pip install -r requirements.txt
# Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Production Considerations

For production use, consider:
- [ ] PostgreSQL instead of SQLite
- [ ] Proper error monitoring (Sentry)
- [ ] Real Google Calendar integration
- [ ] Twilio WhatsApp Business API (not sandbox)
- [ ] Multi-PT support with admin dashboard
- [ ] Webhook signature validation
- [ ] HTTPS only
- [ ] Environment-based configuration
- [ ] Conversation timeout (24 hours inactivity)
- [ ] Max messages per conversation limit (20)

## Troubleshooting

### Bot not responding
- Check ngrok is running and URL is correct in Twilio
- Check logs: `tail -f logs` or console output
- Verify environment variables are set correctly
- Test health endpoint: `curl http://localhost:8000/health`

### Database errors
- Re-run initialization: `python scripts/init_db.py`
- Check file permissions on `pt_chatbot.db`
- Delete database and reinitialize if needed

### Twilio errors
- Verify webhook URL is HTTPS
- Check Twilio credentials in `.env`
- Ensure phone number format is correct (+447123456789)
- Check Twilio console for error logs

### AI Agent errors
- Verify Anthropic API key is valid
- Check API quota/rate limits
- Review logs for specific error messages
- Ensure proper model name: `claude-sonnet-4-5-20250929`

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-asyncio

# Run tests (when implemented)
pytest tests/
```

### Code Structure

- Use async/await for all agent calls
- Follow FastAPI best practices
- Use SQLAlchemy ORM for database operations
- Keep agents stateless and functional
- Log important events and errors

## Future Enhancements

- [ ] Multi-PT platform support
- [ ] Admin dashboard for PTs
- [ ] Real Google Calendar integration with availability checking
- [ ] Instagram DM integration
- [ ] Payment integration (Stripe)
- [ ] Analytics and reporting
- [ ] Voice message support
- [ ] Multi-language support
- [ ] CRM integration (HubSpot, Salesforce)
- [ ] Fine-tuning on successful conversations

## License

MIT License - feel free to use and modify for your needs.

## Support

For issues or questions:
- Check logs for error messages
- Review Twilio console for webhook errors
- Verify all environment variables are set
- Check database was initialized properly

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

Built with Claude Sonnet 4.5 and Pydantic AI