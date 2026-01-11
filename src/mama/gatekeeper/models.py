from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, Field


class AccessRequest(BaseModel):
    purpose: str = Field(..., min_length=1)
    deadline: str | None = None
    no_alternative: str | None = None
    requested_minutes: int = Field(..., ge=1, le=120)


class Decision(BaseModel):
    approved: bool
    minutes: int
    reason: str
    policy_flags: list[str] = Field(default_factory=list)


class DecisionMeta(BaseModel):
    source: Literal["gpt", "fallback", "local_limit"]


class DecisionResult(BaseModel):
    decision: Decision
    meta: DecisionMeta


class State(BaseModel):
    active_until: datetime | None = None
    reward_start: time
    reward_enabled: bool = True
    reward_duration_minutes: int = 60
    daily_count: int = 0
    last_denied_at: datetime | None = None
    last_reset_date: date | None = None
