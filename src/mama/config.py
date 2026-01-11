from datetime import time
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator

ReasoningEffort = Literal["none", "low", "medium", "high"]


def _default_blocklist_paths() -> list[Path]:
    return [
        Path("data/blocklists/x.txt"),
        Path("data/blocklists/youtube.txt"),
        Path("data/blocklists/tiktok.txt"),
    ]


class NetworkConfig(BaseModel):
    ssid: str = Field(..., min_length=1)
    passphrase: str = Field(..., min_length=8, max_length=63)
    country_code: str = Field(default="JP", min_length=2, max_length=2)
    wlan_interface: str = Field(default="wlan0", min_length=1)
    wan_interface: str = Field(default="eth0", min_length=1)
    wifi_channel: int = Field(default=6, ge=1, le=13)
    hw_mode: Literal["g", "a"] = Field(default="g")
    lan_address: str = Field(default="192.168.50.1")
    lan_netmask: str = Field(default="255.255.255.0")
    dhcp_start: str = Field(default="192.168.50.50")
    dhcp_end: str = Field(default="192.168.50.150")
    dhcp_lease: str = Field(default="12h")
    dnsmasq_config_path: Path = Field(default=Path("/etc/dnsmasq.d/mama.conf"))
    hostapd_config_path: Path = Field(default=Path("/etc/hostapd/hostapd.conf"))
    nftables_config_path: Path = Field(default=Path("/etc/nftables.conf"))
    sysctl_config_path: Path = Field(default=Path("/etc/sysctl.d/99-mama.conf"))
    blocklist_paths: list[Path] = Field(default_factory=_default_blocklist_paths)


class GatekeeperConfig(BaseModel):
    auth_username: str = Field(default="mama", min_length=1)
    auth_password: str = Field(..., min_length=1)
    openai_api_key: str = Field(..., min_length=1)
    openai_model: str = Field(default="gpt-5.2", min_length=1)
    reasoning_effort: ReasoningEffort = Field(default="medium")
    host: str = Field(default="0.0.0.0", min_length=1)
    port: int = Field(default=8080, ge=1, le=65535)
    timezone: str = Field(default="Asia/Tokyo", min_length=1)
    log_path: Path = Field(default=Path("data/logs/requests.jsonl"))
    state_path: Path = Field(default=Path("data/state.json"))


class RewardConfig(BaseModel):
    enabled: bool = Field(default=True)
    start_time: time = Field(default=time(21, 0))
    duration_minutes: int = Field(default=60, ge=60, le=60)


class RewardSettings(BaseModel):
    reward_start: time
    reward_enabled: bool


class ExceptionPolicyConfig(BaseModel):
    daily_limit: int = Field(default=10, ge=1)
    cooldown_minutes: int = Field(default=5, ge=0)
    min_minutes: int = Field(default=5, ge=5)
    max_minutes: int = Field(default=30, ge=1, le=30)

    @model_validator(mode="after")
    def _validate_range(self) -> "ExceptionPolicyConfig":
        if self.min_minutes > self.max_minutes:
            raise ValueError("min_minutes must be <= max_minutes")
        return self


class AppConfig(BaseModel):
    network: NetworkConfig
    gatekeeper: GatekeeperConfig
    reward: RewardConfig = Field(default_factory=RewardConfig)
    exception_policy: ExceptionPolicyConfig = Field(
        default_factory=ExceptionPolicyConfig
    )
