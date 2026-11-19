from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Category(str, Enum):
    recipient_absent = "recipient_absent"
    address_issue = "address_issue"
    customs_hold = "customs_hold"
    damaged = "damaged"
    refused = "refused"
    delay = "delay"
    other = "other"


class Urgency(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class LLMOutput(BaseModel):
    """What the LLM must return. Pydantic enforces the shape."""
    category: Category
    urgency: Urgency
    language: Literal["de", "en", "mixed"]
    summary_en: str = Field(description="One-sentence English summary of the note")
    next_action: str = Field(description="The action to take, based on the cited rule")
    rule_id: str = Field(description="ID of the handling rule the action follows, or 'none'")


class ClassifyRequest(BaseModel):
    note: str = Field(min_length=3, max_length=2000)


class ClassifyResponse(LLMOutput):
    provider: str
    latency_ms: float
