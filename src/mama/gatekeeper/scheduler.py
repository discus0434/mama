from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from mama.gatekeeper.models import State


@dataclass(frozen=True)
class WindowState:
    reward_active: bool
    exception_active: bool


def _reward_active(state: State, now: datetime, tz: ZoneInfo) -> bool:
    if not state.reward_enabled:
        return False
    local_now = now.astimezone(tz)
    start_dt = datetime.combine(local_now.date(), state.reward_start, tzinfo=tz)
    end_dt = start_dt + timedelta(minutes=state.reward_duration_minutes)
    return start_dt <= local_now < end_dt


def _exception_active(state: State, now: datetime) -> bool:
    if state.active_until is None:
        return False
    return now < state.active_until


def current_window(state: State, now: datetime, tz: ZoneInfo) -> WindowState:
    return WindowState(
        reward_active=_reward_active(state, now, tz),
        exception_active=_exception_active(state, now),
    )


def next_transition(state: State, now: datetime, tz: ZoneInfo) -> datetime | None:
    candidates: list[datetime] = []
    local_now = now.astimezone(tz)

    if state.active_until is not None and state.active_until > now:
        candidates.append(state.active_until)

    if state.reward_enabled:
        start_dt = datetime.combine(local_now.date(), state.reward_start, tzinfo=tz)
        end_dt = start_dt + timedelta(minutes=state.reward_duration_minutes)
        if local_now < start_dt:
            candidates.append(start_dt)
        elif start_dt <= local_now < end_dt:
            candidates.append(end_dt)
        else:
            candidates.append(start_dt + timedelta(days=1))

    if not candidates:
        return None
    return min(candidates)


def should_unblock(window: WindowState) -> bool:
    return window.reward_active or window.exception_active
