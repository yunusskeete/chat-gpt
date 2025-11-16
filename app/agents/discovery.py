"""Discovery Agent - Conducts natural conversation to extract lead information"""
from pydantic_ai import Agent
from app.config import get_settings
from app.models import PTPreferences


class DiscoveryAgent:
    """Agent for conducting conversational lead discovery"""

    def __init__(self):
        self.settings = get_settings()
        self.agent = None

    def _create_system_prompt(self, pt: PTPreferences) -> str:
        """Create system prompt based on PT preferences"""
        return f"""You are a friendly fitness assistant helping qualify potential clients for {pt.name}.

PT Specialization: {pt.specialty}
PT Preferences:
- Target clients: {pt.target_goals}
- Age range: {pt.age_range}
- Location: {pt.preferred_location}
- Budget: £{pt.min_budget}+/month
- Commitment: {pt.required_commitment}x sessions/week

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

Keep responses concise (2-3 sentences max) and conversational."""

    async def get_response(self, pt: PTPreferences, conversation_history: list[dict]) -> str:
        """
        Generate conversational response based on conversation history

        Args:
            pt: PT preferences
            conversation_history: List of dicts with 'role' and 'content' keys

        Returns:
            Assistant's conversational response
        """
        system_prompt = self._create_system_prompt(pt)

        # Create agent with system prompt
        agent = Agent(
            'claude-sonnet-4-5-20250929',
            system_prompt=system_prompt,
        )

        # Format conversation history for the agent
        # The last message should be the user's message
        user_message = conversation_history[-1]["content"] if conversation_history else ""

        # Get previous context (all but the last message)
        context = ""
        if len(conversation_history) > 1:
            context = "\n".join([
                f"{msg['role'].capitalize()}: {msg['content']}"
                for msg in conversation_history[:-1]
            ])

        # Combine context with current message
        prompt = f"{context}\n\nUser: {user_message}" if context else user_message

        # Run the agent
        result = await agent.run(prompt)

        return result.output
