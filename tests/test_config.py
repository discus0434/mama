from datetime import time

import pytest
from pydantic import ValidationError

from mama.config import (
    AppConfig,
    ExceptionPolicyConfig,
    GatekeeperConfig,
    NetworkConfig,
    RewardConfig,
)


def test_app_config_defaults() -> None:
    config = AppConfig(
        network=NetworkConfig(ssid="mama", passphrase="password123"),
        gatekeeper=GatekeeperConfig(
            auth_password="secret",
            openai_api_key="sk-test",
        ),
    )

    assert config.reward.start_time == time(21, 0)
    assert config.reward.duration_minutes == 60
    assert config.exception_policy.daily_limit == 10
    assert config.exception_policy.min_minutes == 5
    assert config.exception_policy.max_minutes == 30
    assert config.gatekeeper.reasoning_effort == "medium"
    assert config.gatekeeper.timezone == "Asia/Tokyo"


def test_network_config_rejects_short_passphrase() -> None:
    with pytest.raises(ValidationError):
        NetworkConfig(ssid="mama", passphrase="short")


def test_gatekeeper_rejects_invalid_reasoning_effort() -> None:
    with pytest.raises(ValidationError):
        GatekeeperConfig(
            auth_password="secret",
            openai_api_key="sk-test",
            reasoning_effort="extreme",
        )


def test_exception_policy_rejects_invalid_range() -> None:
    with pytest.raises(ValidationError):
        ExceptionPolicyConfig(min_minutes=20, max_minutes=10)


def test_reward_duration_is_fixed_one_hour() -> None:
    with pytest.raises(ValidationError):
        RewardConfig(duration_minutes=30)
