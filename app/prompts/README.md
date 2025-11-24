# Prompt Management System

Simple, observable prompt system: **Database first, file fallback**.

## How It Works

1. **Database (Production)**: Store custom prompts in `PTPreferences` table
2. **File Templates (Development)**: Default prompts in `templates.py`
3. **Observable**: All resolutions logged

## Usage

```python
from app.prompts import PromptManager

# In your agent
manager = PromptManager(pt_preferences)

# Get prompts (database first, file fallback)
bio = manager.get_bio()
discovery = manager.get_discovery_prompt()
qualification = manager.get_qualification_prompt()
```

## Customizing Prompts

### Option 1: Database (per-PT, production)

```python
pt = db.query(PTPreferences).first()

# Custom bio
pt.bio = "Hi! I'm {name}, specializing in {specialty}..."

# Custom discovery prompt
pt.discovery_prompt_override = "You are {pt_name}'s assistant..."

db.commit()
```

### Option 2: File Templates (default, version-controlled)

Edit [templates.py](templates.py):

```python
class PromptTemplates:
    DISCOVERY_SYSTEM_PROMPT = """Your prompt here..."""
```

## Available Variables

All prompts have access to:

- `{pt_name}` / `{name}` - PT's name
- `{specialty}` - PT's specialty
- `{target_goals}` - Target client goals
- `{age_range}` - Preferred age range
- `{location}` - Location/service area
- `{min_budget}` - Minimum monthly budget
- `{required_commitment}` - Required sessions/week
- `{years_experience}` - Years of experience (optional)
- `{certifications}` - Certifications (optional)
- `{additional_info}` - Extra info (optional)

### Prompt-specific variables

**Discovery**: `{pt_bio}` (auto-populated)
**Rejection Email**: `{lead_name}`, `{alternative_specialty}`
**Booking**: `{availability_info}`

## Observability

All prompt resolutions logged:

```
INFO [PT 1] Prompt 'discovery' from file
INFO [PT 1] Prompt 'bio' from database
```

In DEBUG mode, full prompts are logged for inspection.

## Database Schema

```sql
-- Optional override fields (nullable)
ALTER TABLE pt_preferences ADD COLUMN bio TEXT;
ALTER TABLE pt_preferences ADD COLUMN discovery_prompt_override TEXT;
ALTER TABLE pt_preferences ADD COLUMN qualification_prompt_override TEXT;
ALTER TABLE pt_preferences ADD COLUMN rejection_email_override TEXT;
ALTER TABLE pt_preferences ADD COLUMN booking_confirmation_override TEXT;

-- Optional metadata
ALTER TABLE pt_preferences ADD COLUMN years_experience INTEGER;
ALTER TABLE pt_preferences ADD COLUMN certifications TEXT;
ALTER TABLE pt_preferences ADD COLUMN additional_info TEXT;
```

## Architecture Benefits

✅ **Production-ready**: Database storage for per-PT customization
✅ **Development-friendly**: Edit prompts in files, instant feedback
✅ **Observable**: Know exactly where each prompt comes from
✅ **Scalable**: Supports multiple PTs with different prompts
✅ **Simple**: ~100 lines of code, easy to understand
