from datetime import time
from pathlib import Path

import pytest

from mama.env import load_config_from_env


def test_load_config_from_env_minimal() -> None:
    env = {
        "MAMA_SSID": "mama",
        "MAMA_PASSPHRASE": "password123",
        "MAMA_AUTH_PASSWORD": "secret",
        "MAMA_OPENAI_API_KEY": "sk-test",
    }

    config = load_config_from_env(env)

    assert config.network.ssid == "mama"
    assert config.gatekeeper.auth_password == "secret"
    assert config.gatekeeper.reasoning_effort == "medium"
    assert config.reward.start_time == time(21, 0)


def test_load_config_from_env_overrides_values(tmp_path: Path) -> None:
    env = {
        "MAMA_SSID": "mama",
        "MAMA_PASSPHRASE": "password123",
        "MAMA_AUTH_PASSWORD": "secret",
        "MAMA_OPENAI_API_KEY": "sk-test",
        "MAMA_GATEKEEPER_PORT": "9090",
        "MAMA_REWARD_START": "22:15",
        "MAMA_REWARD_ENABLED": "false",
        "MAMA_DAILY_LIMIT": "3",
        "MAMA_WIFI_CHANNEL": "11",
        "MAMA_WIFI_MODE": "a",
        "MAMA_LOG_PATH": str(tmp_path / "log.jsonl"),
        "MAMA_STATE_PATH": str(tmp_path / "state.json"),
        "MAMA_DNSMASQ_CONFIG": str(tmp_path / "dnsmasq.conf"),
        "MAMA_BLOCKLIST_DIR": str(tmp_path / "blocklists"),
        "MAMA_HOSTAPD_CONFIG": str(tmp_path / "hostapd.conf"),
        "MAMA_NFTABLES_CONFIG": str(tmp_path / "nftables.conf"),
        "MAMA_SYSCTL_CONFIG": str(tmp_path / "sysctl.conf"),
    }

    config = load_config_from_env(env)

    assert config.gatekeeper.port == 9090
    assert config.reward.start_time == time(22, 15)
    assert config.reward.enabled is False
    assert config.exception_policy.daily_limit == 3
    assert config.network.wifi_channel == 11
    assert config.network.hw_mode == "a"
    assert config.gatekeeper.log_path == tmp_path / "log.jsonl"
    assert config.gatekeeper.state_path == tmp_path / "state.json"
    assert config.network.dnsmasq_config_path == tmp_path / "dnsmasq.conf"
    assert config.network.blocklist_paths[0] == tmp_path / "blocklists" / "x.txt"
    assert config.network.hostapd_config_path == tmp_path / "hostapd.conf"
    assert config.network.nftables_config_path == tmp_path / "nftables.conf"
    assert config.network.sysctl_config_path == tmp_path / "sysctl.conf"


def test_load_config_from_env_requires_keys() -> None:
    env = {
        "MAMA_SSID": "mama",
        "MAMA_PASSPHRASE": "password123",
    }

    with pytest.raises(ValueError, match="MAMA_AUTH_PASSWORD"):
        load_config_from_env(env)
