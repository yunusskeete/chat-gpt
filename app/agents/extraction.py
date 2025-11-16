"""Extraction Agent - Extracts structured data from conversation"""
from pydantic_ai import Agent
from app.schemas.lead import ExtractedLeadData
from app.config import get_settings


class ExtractionAgent:
    """Agent for extracting structured lead data from conversation"""

    def __init__(self):
        self.settings = get_settings()
        self.system_prompt = """Extract structured lead information from the conversation history provided.

Be conservative - only extract information that was clearly stated.
If information wasn't mentioned, leave it as null.

Also determine if you have enough information to score this lead (goals, rough budget, commitment level are minimum required)."""

    async def extract_data(self, conversation_history: list[dict]) -> ExtractedLeadData:
        """
        Extract structured data from conversation history

        Args:
            conversation_history: List of dicts with 'role' and 'content' keys

        Returns:
            ExtractedLeadData with structured information
        """
        # Create agent with structured output
        agent = Agent(
            'claude-sonnet-4-5-20250929',
            system_prompt=self.system_prompt,
            output_type=ExtractedLeadData,
        )

        # Format conversation history
        conversation_text = "\n".join([
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in conversation_history
        ])

        prompt = f"""Based on the following conversation, extract the lead information:

{conversation_text}

Extract all available information and determine if we have enough to score this lead."""

        # Run the agent
        result = await agent.run(prompt)

        return result.output
