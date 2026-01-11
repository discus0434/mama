from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from mama.config import ExceptionPolicyConfig, RewardConfig
from mama.gatekeeper.models import Decision, State
from mama.gatekeeper.policy import (
    apply_decision,
    clamp_minutes,
    evaluate_local_limits,
    fallback_minutes,
)


def test_evaluate_local_limits_resets_daily_count() -> None:
    tz = ZoneInfo("Asia/Tokyo")
    now = datetime(2026, 1, 11, 9, 0, tzinfo=tz)
    yesterday = now.date().replace(day=10)
    state = State(
        reward_start=RewardConfig().start_time,
        daily_count=10,
        last_reset_date=yesterday,
    )
    policy = ExceptionPolicyConfig(daily_limit=10)

    verdict = evaluate_local_limits(state, policy, now, tz)

    assert verdict.allowed is True
    assert state.daily_count == 0
    assert state.last_reset_date == now.date()


def test_evaluate_local_limits_does_not_reset_when_last_reset_is_future() -> None:
    tz = ZoneInfo("Asia/Tokyo")
    now = datetime(2026, 1, 11, 9, 0, tzinfo=tz)
    tomorrow = now.date().replace(day=12)
    state = State(
        reward_start=RewardConfig().start_time,
        daily_count=10,
        last_reset_date=tomorrow,
    )
    policy = ExceptionPolicyConfig(daily_limit=10)

    verdict = evaluate_local_limits(state, policy, now, tz)

    assert verdict.allowed is False
    assert "daily_limit" in verdict.flags
    assert state.daily_count == 10
    assert state.last_reset_date == tomorrow


def test_evaluate_local_limits_blocks_on_daily_limit() -> None:
    tz = ZoneInfo("Asia/Tokyo")
    now = datetime(2026, 1, 11, 9, 0, tzinfo=tz)
    state = State(
        reward_start=RewardConfig().start_time,
        daily_count=10,
        last_reset_date=now.date(),
    )
    policy = ExceptionPolicyConfig(daily_limit=10)

    verdict = evaluate_local_limits(state, policy, now, tz)

    assert verdict.allowed is False
    assert "daily_limit" in verdict.flags


def test_evaluate_local_limits_allows_at_daily_limit_minus_one() -> None:
    tz = ZoneInfo("Asia/Tokyo")
    now = datetime(2026, 1, 11, 9, 0, tzinfo=tz)
    state = State(
        reward_start=RewardConfig().start_time,
        daily_count=9,
        last_reset_date=now.date(),
    )
    policy = ExceptionPolicyConfig(daily_limit=10)

    verdict = evaluate_local_limits(state, policy, now, tz)

    assert verdict.allowed is True


def test_evaluate_local_limits_blocks_on_cooldown() -> None:
    tz = ZoneInfo("Asia/Tokyo")
    now = datetime(2026, 1, 11, 9, 0, tzinfo=tz)
    state = State(
        reward_start=RewardConfig().start_time,
        last_denied_at=now - timedelta(minutes=3),
    )
    policy = ExceptionPolicyConfig(cooldown_minutes=5)

    verdict = evaluate_local_limits(state, policy, now, tz)

    assert verdict.allowed is False
    assert "cooldown" in verdict.flags


def test_apply_decision_clamps_and_updates_state() -> None:
    tz = ZoneInfo("Asia/Tokyo")
    now = datetime(2026, 1, 11, 9, 0, tzinfo=tz)
    state = State(reward_start=RewardConfig().start_time)
    policy = ExceptionPolicyConfig(min_minutes=5, max_minutes=30)
    decision = Decision(approved=True, minutes=120, reason="ok", policy_flags=[])

    updated, final_decision = apply_decision(state, decision, policy, now)

    assert final_decision.minutes == 30
    assert updated.daily_count == 1
    assert updated.active_until == now + timedelta(minutes=30)


def test_fallback_minutes_clamps_requested_value() -> None:
    policy = ExceptionPolicyConfig(min_minutes=5, max_minutes=30)

    assert fallback_minutes(1, policy) == 5
    assert fallback_minutes(25, policy) == 25
    assert fallback_minutes(60, policy) == 30
    assert clamp_minutes(60, policy) == 30
