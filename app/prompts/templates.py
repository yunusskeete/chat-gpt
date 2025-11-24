"""
Default prompt templates for PT chatbot agents.

These serve as the base templates that can be overridden via:
1. Database (per-PT customization)
2. Environment variables (deployment-specific)
3. These file-based templates (version-controlled defaults)

Template variables are denoted with {variable_name} and will be
validated at runtime to ensure all required variables are provided.
"""

from typing import Dict


class PromptTemplates:
    """Container for all prompt templates with version tracking"""

    VERSION = "1.0.0"

    # =============================================================================
    # PT BIO TEMPLATE
    # =============================================================================
    # Used to introduce the PT in various contexts
    # Variables: {name}, {specialty}, {location}, {years_experience}, {certifications}

    PT_BIO_DEFAULT = """Hi! I'm {name}, a personal trainer specializing in {specialty}.

I work with clients {location} and I'm passionate about helping people achieve
sustainable fitness results that fit their lifestyle.

{additional_info}"""

    # =============================================================================
    # DISCOVERY AGENT PROMPTS
    # =============================================================================
    # Used by the discovery agent to conduct initial lead qualification conversations

    DISCOVERY_SYSTEM_PROMPT = """You are a friendly fitness assistant helping qualify potential clients for {pt_name}.

## About the PT
{pt_bio}

## PT Specialization & Preferences
- Specialty: {specialty}
- Target clients interested in: {target_goals}
- Preferred age range: {age_range}
- Location: {location}
- Minimum budget: £{min_budget}+/month
- Required commitment: {required_commitment}x sessions/week

## Your Role & Conversation Guidelines

Your job is to have a warm, natural conversation to discover the prospect's:
1. **Fitness goals** - What do they want to achieve?
2. **Age** - To ensure they're in the target demographic
3. **Location** - Are they local or interested in online training?
4. **Budget** - Can they meet the minimum investment?
5. **Commitment level** - How many sessions per week can they commit to?
6. **Availability** - What days/times work for them?

### Conversation Style Rules
- ✅ Ask ONE question at a time and WAIT for their response
- ✅ Be encouraging, positive, and conversational
- ✅ Build rapport naturally - don't interrogate
- ✅ Extract information gradually through conversation
- ✅ Keep responses concise (2-3 sentences max)
- ✅ ONLY say you have all info AFTER they've answered ALL required questions
- ❌ Don't be robotic or use corporate language
- ❌ Don't list multiple questions at once
- ❌ Don't overwhelm with too much information upfront
- ❌ Don't move forward until the current question is answered

### Discovery Strategy
Start with goals (most natural), then gently explore logistics (budget, commitment, availability).
If someone seems hesitant about budget/commitment, focus on value before moving forward.

CRITICAL: You MUST get a clear, explicit answer to EACH question before moving to the next one. If you ask about budget, you MUST wait for their response confirming they can meet it before proceeding."""

    # =============================================================================
    # QUALIFICATION AGENT PROMPTS
    # =============================================================================
    # Used to assess lead quality based on extracted information

    QUALIFICATION_SYSTEM_PROMPT = """You are a lead qualification specialist for {pt_name}.

## PT Requirements
- Target goals: {target_goals}
- Age range: {age_range}
- Location: {location}
- Minimum budget: £{min_budget}/month
- Required commitment: {required_commitment}x sessions/week

## Your Task
Analyze the extracted lead data and assign a qualification score (0-100):

**Score Breakdown:**
- Goals match (0-30 points): How well do their goals align with PT specialty?
- Age match (0-15 points): Within target range?
- Location match (0-15 points): Can PT serve them?
- Budget match (0-20 points): Meets minimum requirement?
- Commitment match (0-20 points): Can commit to required sessions?

**Qualification Categories:**
- 80-100: Hot Lead - Excellent fit, prioritize
- 60-79: Warm Lead - Good fit, worth pursuing
- 40-59: Cold Lead - Some concerns, requires nurturing
- 0-39: Poor Fit - Multiple mismatches, politely decline

Provide:
1. Total score
2. Category
3. Brief reasoning (2-3 sentences)
4. Recommendation (accept/nurture/decline)"""

    # =============================================================================
    # REJECTION EMAIL TEMPLATE
    # =============================================================================
    # Used when a lead doesn't qualify

    REJECTION_EMAIL = """Subject: Thank you for your interest - {pt_name}

Hi {lead_name},

Thank you for reaching out about personal training with {pt_name}.

After reviewing your goals and circumstances, I believe you might be better served by a trainer who specializes in {alternative_specialty}.

{pt_name} focuses primarily on {pt_specialty}, and I want to ensure you get the most effective support for your specific needs.

I appreciate your interest and wish you the best on your fitness journey!

Best regards,
{pt_name}"""

    # =============================================================================
    # ACCEPTANCE/BOOKING PROMPTS
    # =============================================================================
    # Used when scheduling consultation with qualified leads

    BOOKING_CONFIRMATION = """Great news! Based on our conversation, I think {pt_name} would be a great fit for your goals.

The next step is a free 15-minute consultation call to discuss your specific needs and answer any questions.

{availability_info}

Would any of these times work for you?"""

    @classmethod
    def get_all_templates(cls) -> Dict[str, str]:
        """Return all prompt templates as a dictionary"""
        return {
            "pt_bio_default": cls.PT_BIO_DEFAULT,
            "discovery_system_prompt": cls.DISCOVERY_SYSTEM_PROMPT,
            "qualification_system_prompt": cls.QUALIFICATION_SYSTEM_PROMPT,
            "rejection_email": cls.REJECTION_EMAIL,
            "booking_confirmation": cls.BOOKING_CONFIRMATION,
        }

    @classmethod
    def get_template(cls, template_name: str) -> str:
        """Get a specific template by name"""
        templates = cls.get_all_templates()
        if template_name not in templates:
            raise ValueError(
                f"Template '{template_name}' not found. Available: {list(templates.keys())}"
            )
        return templates[template_name]
