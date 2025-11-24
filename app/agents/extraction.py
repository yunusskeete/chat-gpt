"""Extraction Agent - Extracts structured data from conversation"""
from pydantic_ai import Agent
from app.schemas.lead import ExtractedLeadData
from app.config import get_settings


class ExtractionAgent:
    """Agent for extracting structured lead data from conversation"""

    def __init__(self):
        self.settings = get_settings()
        self.system_prompt = """Extract structured lead information from the conversation history provided.

Be conservative - only extract information that was clearly stated by the user.
If information wasn't mentioned or confirmed, leave it as null.

## Required Information Checklist

To set has_all_info = true, the user must have CONFIRMED all of these:
1. **Goals** - Clear fitness goals stated
2. **Budget** - User explicitly confirmed they can meet the budget requirement (not just asked, but answered affirmatively)
3. **Commitment level** - Number of sessions per week confirmed
4. **Age** - Age or age range stated
5. **Location** - Location confirmed or online preference stated
6. **Availability** - Days/times they can train

CRITICAL: If the assistant just ASKED about budget but the user hasn't RESPONDED yet, budget is null and has_all_info = false.
Do NOT mark has_all_info = true if any question is still awaiting a response."""

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
