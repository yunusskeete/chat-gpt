# Configuration System

Clean configuration pattern: **Environment variables override file defaults**.

## How It Works

**3-tier resolution for PT configuration:**

1. **Database** (runtime, per-PT) - PTPreferences table
2. **Environment variables** (.env file) - deployment-specific overrides
3. **File defaults** (pt_defaults.py) - version-controlled defaults with long text contexts

## Usage

### Edit Default PT Configuration

Edit [pt_defaults.py](pt_defaults.py) to change defaults:

```python
class PTDefaults:
    NAME = "Your PT Name"
    SPECIALTY = "Your specialty..."

    # Long-form text contexts
    BIO = """Multi-paragraph bio here..."""

    TRAINING_PHILOSOPHY = """Your training philosophy..."""

    IDEAL_CLIENT = """Description of your ideal client..."""
```

### Override with Environment Variables

Create/edit `.env` file:

```bash
PT_NAME="Different Name"
PT_BIO="Custom bio that overrides the file default"
PT_YEARS_EXPERIENCE=15
```

### Runtime Database Override

The PromptManager checks database first:

```python
# This uses PTPreferences from database
manager = PromptManager(pt_preferences)
bio = manager.get_bio()  # Database first, then settings, then file
```

## Resolution Priority

```
Database (PTPreferences.bio)
    ↓ (if NULL)
Environment variable (PT_BIO)
    ↓ (if not set)
File default (PTDefaults.BIO)
```

## Available Configuration Fields

### Basic Fields
- `PT_NAME` - PT's name
- `PT_SPECIALTY` - Area of specialization
- `PT_TARGET_GOALS` - Target client goals
- `PT_AGE_RANGE` - Preferred client age range
- `PT_LOCATION` - Location/service area
- `PT_MIN_BUDGET` - Minimum monthly budget (int)
- `PT_REQUIRED_COMMITMENT` - Required sessions/week (int)

### Extended Context Fields (Perfect for Long Text)
- `PT_BIO` - Multi-paragraph bio
- `PT_YEARS_EXPERIENCE` - Years of experience (int)
- `PT_CERTIFICATIONS` - Professional certifications
- `PT_ADDITIONAL_INFO` - Extra context
- `PT_TRAINING_PHILOSOPHY` - Training philosophy/approach
- `PT_IDEAL_CLIENT` - Ideal client description
- `PT_DISQUALIFIERS` - Disqualifying factors

## Benefits

✅ **Development**: Edit rich text contexts in `pt_defaults.py`
✅ **Deployment**: Override with env vars per environment
✅ **Production**: Customize per-PT in database
✅ **Version Control**: All defaults tracked in git
✅ **Observable**: Clear where each value comes from

## Example: Adding New Field

1. Add to [pt_defaults.py](pt_defaults.py):
   ```python
   CONSULTATION_SCRIPT = """Your consultation script..."""
   ```

2. Add to Settings class in [config.py](../config.py):
   ```python
   pt_consultation_script: str = PTDefaults.CONSULTATION_SCRIPT
   ```

3. Add to get_settings():
   ```python
   pt_consultation_script=os.getenv("PT_CONSULTATION_SCRIPT", PTDefaults.CONSULTATION_SCRIPT),
   ```

4. Use in code:
   ```python
   settings = get_settings()
   script = settings.pt_consultation_script
   ```
