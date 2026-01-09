"""
Default PT configuration values.

These serve as fallback defaults when environment variables are not set.
Can include longer text contexts, detailed descriptions, etc.
"""


class PTDefaults:
    """Default PT configuration - easily editable in one place"""

    # Basic info
    NAME = "Adam Powe"
    SPECIALTY = "Bodybuilding and physique development for dedicated lifters"

    # Target client profile
    TARGET_GOALS = "muscle gain, competition prep, bodybuilding, physique development"
    AGE_RANGE = "18-55"
    LOCATION = "London (in-person or online)"

    # Business requirements
    MIN_BUDGET = 300  # £/month
    REQUIRED_COMMITMENT = 3  # sessions per week

    # ===========================================================================
    # Extended context fields (can be multi-paragraph)
    # ===========================================================================

    # Detailed bio/background
    BIO = """Hi! I'm Adam Powe, a professional bodybuilder and coach specializing in
helping clients build lean muscle mass and achieve bodybuilding-level physiques.

As a competitive bodybuilder myself, I've walked the path from beginner to stage-ready,
and I use that experience to guide my clients through their transformation journey.

Whether you're a complete beginner looking to build serious size, an intermediate lifter
ready to take it to the next level, or preparing for your first bodybuilding competition,
I provide expert programming, nutrition guidance, and posing coaching to help you reach
your physique goals."""

    # Years of professional experience
    YEARS_EXPERIENCE = 7

    # Professional certifications (comma-separated)
    CERTIFICATIONS = "ISSA Bodybuilding Specialist, Precision Nutrition L2, IFBB Pro Card"

    # Additional contextual information
    ADDITIONAL_INFO = """I work with dedicated lifters who are serious about building
muscle and transforming their physiques. My clients range from beginners taking their
first steps into structured bodybuilding training, to advanced lifters preparing for
competition.

My coaching approach includes:
- Structured hypertrophy-focused training programs
- Periodized programming for muscle growth and definition
- Evidence-based nutrition protocols for bulking and cutting
- Competition prep coaching (posing, peaking, show day strategy)
- Regular progress assessments and program adjustments

I offer both in-person training in London and comprehensive online coaching for
remote clients, with check-ins, form reviews, and ongoing support."""

    # Training philosophy (for more detailed prompts)
    TRAINING_PHILOSOPHY = """Building an impressive physique requires dedication,
consistency, and intelligent programming. I believe in progressive overload,
proper recovery, and nutrition that supports your goals - whether that's gaining
lean size or getting stage-ready. No shortcuts, just proven methods that work."""

    # Ideal client description (for qualification criteria)
    IDEAL_CLIENT = """Dedicated lifters who:
- Are serious about building muscle and transforming their physique
- Can commit to 3-4+ training sessions per week
- Understand this is a long-term process requiring consistency
- Have a realistic budget (£300+/month for comprehensive coaching)
- Are willing to track nutrition and follow structured programming
- May be interested in competing or just want to look like they could
- Want expert guidance from someone who's competed at a high level"""

    # Disqualifying factors (for lead scoring)
    DISQUALIFIERS = """Not a good fit if:
- Looking for general fitness or weight loss without muscle-building focus
- Can't commit to at least 3 structured training sessions per week
- Budget below £300/month
- Not willing to track nutrition or follow a structured program
- Seeking quick fixes or shortcuts
- Not interested in the bodybuilding/physique development process"""