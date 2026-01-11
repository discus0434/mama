from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from mama.gatekeeper.models import State
from mama.gatekeeper.scheduler import current_window, next_transition, should_unblock


def test_reward_window_matches_start_time() -> None:
    tz = ZoneInfo("Asia/Tokyo")
    state = State(
        reward_start=datetime(2026, 1, 11, 21, 0, tzinfo=tz).time(),
        reward_enabled=True,
        reward_duration_minutes=60,
    )

    now = datetime(2026, 1, 11, 21, 30, tzinfo=tz)

    window = current_window(state, now, tz)

    assert window.reward_active is True
    assert should_unblock(window) is True


def test_reward_window_false_when_disabled() -> None:
    tz = ZoneInfo("Asia/Tokyo")
    state = State(
        reward_start=datetime(2026, 1, 11, 21, 0, tzinfo=tz).time(),
        reward_enabled=False,
    )

    now = datetime(2026, 1, 11, 21, 30, tzinfo=tz)

    window = current_window(state, now, tz)

    assert window.reward_active is False
    assert should_unblock(window) is False


def test_exception_active_uses_active_until() -> None:
    tz = ZoneInfo("Asia/Tokyo")
    now = datetime(2026, 1, 11, 9, 0, tzinfo=tz)
    state = State(
        reward_start=datetime(2026, 1, 11, 21, 0, tzinfo=tz).time(),
        active_until=now + timedelta(minutes=5),
    )

    window = current_window(state, now, tz)

    assert window.exception_active is True


def test_should_unblock_combines_reward_and_exception() -> None:
    tz = ZoneInfo("Asia/Tokyo")
    state = State(
        reward_start=datetime(2026, 1, 11, 21, 0, tzinfo=tz).time(),
        reward_enabled=True,
    )
    now = datetime(2026, 1, 11, 21, 30, tzinfo=tz)

    window = current_window(state, now, tz)

    assert should_unblock(window) is True


def test_next_transition_picks_reward_start_before_window() -> None:
    tz = ZoneInfo("Asia/Tokyo")
    now = datetime(2026, 1, 11, 8, 0, tzinfo=tz)
    state = State(
        reward_start=datetime(2026, 1, 11, 21, 0, tzinfo=tz).time(),
        reward_enabled=True,
        reward_duration_minutes=60,
    )

    next_time = next_transition(state, now, tz)

    assert next_time == datetime(2026, 1, 11, 21, 0, tzinfo=tz)


def test_next_transition_picks_reward_end_inside_window() -> None:
    tz = ZoneInfo("Asia/Tokyo")
    now = datetime(2026, 1, 11, 21, 30, tzinfo=tz)
    state = State(
        reward_start=datetime(2026, 1, 11, 21, 0, tzinfo=tz).time(),
        reward_enabled=True,
        reward_duration_minutes=60,
    )

    next_time = next_transition(state, now, tz)

    assert next_time == datetime(2026, 1, 11, 22, 0, tzinfo=tz)


def test_next_transition_prefers_exception_end() -> None:
    tz = ZoneInfo("Asia/Tokyo")
    now = datetime(2026, 1, 11, 21, 30, tzinfo=tz)
    state = State(
        reward_start=datetime(2026, 1, 11, 21, 0, tzinfo=tz).time(),
        reward_enabled=True,
        reward_duration_minutes=60,
        active_until=now + timedelta(minutes=5),
    )

    next_time = next_transition(state, now, tz)

    assert next_time == now + timedelta(minutes=5)
