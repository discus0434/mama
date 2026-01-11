import os
from datetime import time
from pathlib import Path
from typing import Mapping

from mama.config import (
    AppConfig,
    ExceptionPolicyConfig,
    GatekeeperConfig,
    NetworkConfig,
    RewardConfig,
)


def load_config_from_env(env: Mapping[str, str] | None = None) -> AppConfig:
    source = os.environ if env is None else env
    ssid = _require(source, "MAMA_SSID")
    passphrase = _require(source, "MAMA_PASSPHRASE")
    auth_password = _require(source, "MAMA_AUTH_PASSWORD")
    openai_api_key = _require(source, "MAMA_OPENAI_API_KEY")

    network = NetworkConfig(
        ssid=ssid,
        passphrase=passphrase,
        country_code=source.get("MAMA_COUNTRY_CODE", "JP"),
        wlan_interface=source.get("MAMA_WLAN_INTERFACE", "wlan0"),
        wan_interface=source.get("MAMA_WAN_INTERFACE", "eth0"),
        wifi_channel=_int(source.get("MAMA_WIFI_CHANNEL", "6"), "MAMA_WIFI_CHANNEL"),
        hw_mode=source.get("MAMA_WIFI_MODE", "g"),
        lan_address=source.get("MAMA_LAN_ADDRESS", "192.168.50.1"),
        lan_netmask=source.get("MAMA_LAN_NETMASK", "255.255.255.0"),
        dhcp_start=source.get("MAMA_DHCP_START", "192.168.50.50"),
        dhcp_end=source.get("MAMA_DHCP_END", "192.168.50.150"),
        dhcp_lease=source.get("MAMA_DHCP_LEASE", "12h"),
        dnsmasq_config_path=Path(
            source.get("MAMA_DNSMASQ_CONFIG", "/etc/dnsmasq.d/mama.conf")
        ),
        hostapd_config_path=Path(
            source.get("MAMA_HOSTAPD_CONFIG", "/etc/hostapd/hostapd.conf")
        ),
        nftables_config_path=Path(
            source.get("MAMA_NFTABLES_CONFIG", "/etc/nftables.conf")
        ),
        sysctl_config_path=Path(
            source.get("MAMA_SYSCTL_CONFIG", "/etc/sysctl.d/99-mama.conf")
        ),
        blocklist_paths=_blocklist_paths(source.get("MAMA_BLOCKLIST_DIR")),
    )

    gatekeeper = GatekeeperConfig(
        auth_username=source.get("MAMA_AUTH_USERNAME", "mama"),
        auth_password=auth_password,
        openai_api_key=openai_api_key,
        openai_model=source.get("MAMA_OPENAI_MODEL", "gpt-5.2"),
        reasoning_effort=source.get("MAMA_REASONING_EFFORT", "medium"),
        host=source.get("MAMA_GATEKEEPER_HOST", "0.0.0.0"),
        port=_int(source.get("MAMA_GATEKEEPER_PORT", "8080"), "MAMA_GATEKEEPER_PORT"),
        timezone=source.get("MAMA_TIMEZONE", "Asia/Tokyo"),
        log_path=Path(source.get("MAMA_LOG_PATH", "data/logs/requests.jsonl")),
        state_path=Path(source.get("MAMA_STATE_PATH", "data/state.json")),
    )

    reward = RewardConfig(
        enabled=_bool(source.get("MAMA_REWARD_ENABLED", "true"), "MAMA_REWARD_ENABLED"),
        start_time=_time(source.get("MAMA_REWARD_START", "21:00"), "MAMA_REWARD_START"),
        duration_minutes=60,
    )

    exception_policy = ExceptionPolicyConfig(
        daily_limit=_int(source.get("MAMA_DAILY_LIMIT", "10"), "MAMA_DAILY_LIMIT"),
        cooldown_minutes=_int(
            source.get("MAMA_COOLDOWN_MINUTES", "5"), "MAMA_COOLDOWN_MINUTES"
        ),
        min_minutes=_int(source.get("MAMA_MIN_MINUTES", "5"), "MAMA_MIN_MINUTES"),
        max_minutes=_int(source.get("MAMA_MAX_MINUTES", "30"), "MAMA_MAX_MINUTES"),
    )

    return AppConfig(
        network=network,
        gatekeeper=gatekeeper,
        reward=reward,
        exception_policy=exception_policy,
    )


def _require(env: Mapping[str, str], key: str) -> str:
    value = env.get(key)
    if value is None or value.strip() == "":
        raise ValueError(f"{key} is required")
    return value


def _int(raw: str, key: str) -> int:
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{key} must be an integer") from exc


def _bool(raw: str, key: str) -> bool:
    lowered = raw.strip().lower()
    if lowered in {"true", "1", "yes", "on"}:
        return True
    if lowered in {"false", "0", "no", "off"}:
        return False
    raise ValueError(f"{key} must be a boolean")


def _time(raw: str, key: str) -> time:
    try:
        hour_str, minute_str = raw.strip().split(":", 1)
        return time(int(hour_str), int(minute_str))
    except ValueError as exc:
        raise ValueError(f"{key} must be HH:MM") from exc


def _blocklist_paths(raw: str | None) -> list[Path]:
    if raw is None:
        return [
            Path("data/blocklists/x.txt"),
            Path("data/blocklists/youtube.txt"),
            Path("data/blocklists/tiktok.txt"),
        ]
    root = Path(raw)
    return [
        root / "x.txt",
        root / "youtube.txt",
        root / "tiktok.txt",
    ]
