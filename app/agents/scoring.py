"""Scoring Agent - Scores leads against PT preferences"""
from pydantic_ai import Agent
from app.schemas.lead import ExtractedLeadData, QualificationScore
from app.models import PTPreferences
from app.config import get_settings


class ScoringAgent:
    """Agent for scoring leads and recommending actions"""

    def __init__(self):
        self.settings = get_settings()

    def _create_system_prompt(self, pt: PTPreferences) -> str:
        """Create system prompt with PT preferences"""
        return f"""Score this lead based on the PT's preferences.

PT Preferences:
- Name: {pt.name}
- Specialty: {pt.specialty}
- Target goals: {pt.target_goals}
- Age range: {pt.age_range}
- Location: {pt.preferred_location}
- Minimum budget: £{pt.min_budget}/month
- Required commitment: {pt.required_commitment}x sessions/week

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
4. Recommended action: book_call, send_rejection, or needs_more_info"""

    async def score_lead(self, pt: PTPreferences, lead_data: ExtractedLeadData) -> QualificationScore:
        """
        Score lead against PT preferences

        Args:
            pt: PT preferences
            lead_data: Extracted lead data

        Returns:
            QualificationScore with scoring results
        """
        system_prompt = self._create_system_prompt(pt)

        # Create agent with structured output
        agent = Agent(
            'claude-sonnet-4-5-20250929',
            system_prompt=system_prompt,
            output_type=QualificationScore,
        )

        # Format lead data
        prompt = f"""Score this lead:

Goals: {lead_data.goals}
Age: {lead_data.age}
Location: {lead_data.location}
Budget Range: {lead_data.budget_range}
Commitment Level: {lead_data.commitment_level}/10
Availability: {lead_data.availability}

Provide a comprehensive scoring assessment."""

        # Run the agent
        result = await agent.run(prompt)

        return result.output
