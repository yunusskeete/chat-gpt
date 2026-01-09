"""Discovery Agent - Conducts natural conversation to extract lead information"""
import logging
from pydantic_ai import Agent
from app.config import get_settings
from app.models import PTPreferences
from app.prompts import PromptManager

logger = logging.getLogger(__name__)


class DiscoveryAgent:
    """Agent for conducting conversational lead discovery with observable prompt management"""

    def __init__(self):
        self.settings = get_settings()
        self.agent = None

    def _create_system_prompt(self, pt: PTPreferences) -> str:
        """
        Create system prompt using PromptManager.

        Resolution: Database first, file template fallback.
        Source is logged for observability.
        """
        prompt_manager = PromptManager(pt)
        prompt = prompt_manager.get_discovery_prompt()

        # In debug mode, log full prompt for inspection
        if self.settings.debug:
            logger.debug("Discovery prompt for PT %s:\n%s", pt.id, prompt)

        return prompt

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
