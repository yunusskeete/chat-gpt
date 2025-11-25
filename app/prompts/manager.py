"""
Simple PromptManager: Database first, file fallback.

Priority:
1. Database (PTPreferences.bio, discovery_prompt_override, etc.)
2. File template (app/prompts/templates.py)

Logs which source was used for observability.
"""

import logging
from typing import Any, Dict, Optional

from app.models import PTPreferences
from app.prompts.templates import PromptTemplates

logger = logging.getLogger(__name__)


class PromptManager:
    """Simple prompt manager: database first, file template fallback"""

    def __init__(self, pt: PTPreferences):
        self.pt = pt
        self.templates = PromptTemplates()

    def _get_base_vars(self) -> Dict[str, Any]:
        """Get variables from PT preferences"""
        return {
            "pt_name": self.pt.name,
            "name": self.pt.name,
            "specialty": self.pt.specialty,
            "target_goals": self.pt.target_goals,
            "age_range": self.pt.age_range,
            "location": self.pt.preferred_location,
            "min_budget": self.pt.min_budget,
            "required_commitment": self.pt.required_commitment,
            "years_experience": self.pt.years_experience or "",
            "certifications": self.pt.certifications or "",
            "additional_info": self.pt.additional_info or "",
        }

    def _resolve(
        self,
        db_field: Optional[str],
        file_template: str,
        variables: Dict[str, Any],
        name: str,
    ) -> str:
        """
        Resolve prompt: database first, file fallback.

        Args:
            db_field: Value from database (e.g., pt.bio)
            file_template: Default template from PromptTemplates
            variables: Variables to inject
            name: Prompt name for logging

        Returns:
            Formatted prompt string
        """
        if db_field:
            template = db_field
            source = "database"
        else:
            template = file_template
            source = "file"

        logger.info("[PT %s] Prompt '%s' from %s", self.pt.id, name, source)

        try:
            return template.format(**variables)
        except KeyError as e:
            logger.error("[PT %s] Missing variable in '%s': %s", self.pt.id, name, e)
            raise

    # Public API

    def get_bio(self) -> str:
        """Get PT bio (database or default template)"""
        vars = self._get_base_vars()
        return self._resolve(
            self.pt.bio,  # type: ignore
            PromptTemplates.PT_BIO_DEFAULT,
            vars,
            "bio",
        )

    def get_discovery_prompt(self) -> str:
        """Get discovery agent system prompt"""
        bio = self.get_bio()
        vars = {**self._get_base_vars(), "pt_bio": bio}
        return self._resolve(
            self.pt.discovery_prompt_override,  # type: ignore
            PromptTemplates.DISCOVERY_SYSTEM_PROMPT,
            vars,
            "discovery",
        )

    def get_qualification_prompt(self) -> str:
        """Get qualification agent system prompt"""
        vars = self._get_base_vars()
        return self._resolve(
            self.pt.qualification_prompt_override,  # type: ignore
            PromptTemplates.QUALIFICATION_SYSTEM_PROMPT,
            vars,
            "qualification",
        )

    def get_rejection_email(
        self, lead_name: str, alternative: str = "your goals"
    ) -> str:
        """Get rejection email template"""
        vars = {
            **self._get_base_vars(),
            "lead_name": lead_name,
            "alternative_specialty": alternative,
            "pt_specialty": self.pt.specialty,
        }
        return self._resolve(
            self.pt.rejection_email_override,  # type: ignore
            PromptTemplates.REJECTION_EMAIL,
            vars,
            "rejection_email",
        )

    def get_booking_confirmation(self, availability_info: str) -> str:
        """Get booking confirmation message"""
        vars = {**self._get_base_vars(), "availability_info": availability_info}
        return self._resolve(
            self.pt.booking_confirmation_override,  # type: ignore
            PromptTemplates.BOOKING_CONFIRMATION,
            vars,
            "booking",
        )

    def get_intro_message(self) -> str:
        """Get intro message for new conversations"""
        vars = self._get_base_vars()
        return self._resolve(
            self.pt.intro_message_override,  # type: ignore
            PromptTemplates.INTRO_MESSAGE,
            vars,
            "intro_message",
        )
