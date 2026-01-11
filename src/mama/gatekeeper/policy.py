from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from mama.config import ExceptionPolicyConfig
from mama.gatekeeper.models import Decision, State


@dataclass(frozen=True)
class PolicyVerdict:
    allowed: bool
    reason: str
    flags: list[str]


def clamp_minutes(requested: int, policy: ExceptionPolicyConfig) -> int:
    return max(policy.min_minutes, min(requested, policy.max_minutes))


def fallback_minutes(requested: int, policy: ExceptionPolicyConfig) -> int:
    return clamp_minutes(requested, policy)


def evaluate_local_limits(
    state: State,
    policy: ExceptionPolicyConfig,
    now: datetime,
    tz: ZoneInfo,
) -> PolicyVerdict:
    local_date = now.astimezone(tz).date()
    if state.last_reset_date != local_date:
        state.daily_count = 0
        state.last_reset_date = local_date
    if state.daily_count >= policy.daily_limit:
        return PolicyVerdict(False, "daily limit reached", ["daily_limit"])
    if state.last_denied_at is not None:
        cooldown = timedelta(minutes=policy.cooldown_minutes)
        if now - state.last_denied_at < cooldown:
            return PolicyVerdict(False, "cooldown active", ["cooldown"])
    return PolicyVerdict(True, "ok", [])


def apply_decision(
    state: State,
    decision: Decision,
    policy: ExceptionPolicyConfig,
    now: datetime,
) -> tuple[State, Decision]:
    if decision.approved:
        decision.minutes = clamp_minutes(decision.minutes, policy)
        state.active_until = now + timedelta(minutes=decision.minutes)
        state.daily_count += 1
    else:
        decision.minutes = 0
        state.last_denied_at = now
    return state, decision
