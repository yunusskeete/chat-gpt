from pydantic import BaseModel
from typing import Literal


class ExtractedLeadData(BaseModel):
    """Structured lead data extracted from conversation"""
    goals: str | None = None
    age: int | None = None
    location: str | None = None
    budget_range: str | None = None
    commitment_level: int | None = None  # 1-10 scale
    availability: str | None = None
    has_all_info: bool  # Ready to score?


class QualificationScore(BaseModel):
    """Lead qualification scoring result"""
    overall_score: int  # 1-100
    is_qualified: bool
    reasoning: str
    recommended_action: Literal["book_call", "send_rejection", "needs_more_info"]
