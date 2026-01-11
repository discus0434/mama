from pathlib import Path

import pytest

from mama.config import AppConfig, GatekeeperConfig, NetworkConfig
from mama.net.apply import (
    apply_hostapd_config,
    apply_network_stack,
    reload_hostapd,
    reload_nftables,
    reload_sysctl,
)


def test_apply_hostapd_config_writes_file(tmp_path: Path) -> None:
    config = NetworkConfig(
        ssid="mama",
        passphrase="password123",
        hostapd_config_path=tmp_path / "hostapd.conf",
    )
    config.hostapd_config_path.parent.mkdir(parents=True, exist_ok=True)

    apply_hostapd_config(config, config.hostapd_config_path)

    content = config.hostapd_config_path.read_text()
    assert "ssid=mama" in content
    assert "wpa_passphrase=password123" in content


def test_reload_hostapd_runs_systemctl(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def _fake_run(cmd, check, capture_output, text):  # type: ignore[no-untyped-def]
        captured["cmd"] = cmd
        return type("Result", (), {"returncode": 0, "stderr": ""})()

    monkeypatch.setattr("mama.net.apply.subprocess.run", _fake_run)

    reload_hostapd()

    assert captured["cmd"] == ["systemctl", "restart", "hostapd"]


def test_reload_nftables_runs_nft(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: dict[str, object] = {}

    def _fake_run(cmd, check, capture_output, text):  # type: ignore[no-untyped-def]
        captured["cmd"] = cmd
        return type("Result", (), {"returncode": 0, "stderr": ""})()

    monkeypatch.setattr("mama.net.apply.subprocess.run", _fake_run)

    reload_nftables(tmp_path / "nftables.conf")

    assert captured["cmd"] == ["nft", "-f", str(tmp_path / "nftables.conf")]


def test_reload_sysctl_runs_system(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def _fake_run(cmd, check, capture_output, text):  # type: ignore[no-untyped-def]
        captured["cmd"] = cmd
        return type("Result", (), {"returncode": 0, "stderr": ""})()

    monkeypatch.setattr("mama.net.apply.subprocess.run", _fake_run)

    reload_sysctl()

    assert captured["cmd"] == ["sysctl", "--system"]


def test_apply_network_stack_invokes_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    config = AppConfig(
        network=NetworkConfig(
            ssid="mama",
            passphrase="password123",
            hostapd_config_path=Path("/tmp/hostapd.conf"),
            dnsmasq_config_path=Path("/tmp/dnsmasq.conf"),
            nftables_config_path=Path("/tmp/nftables.conf"),
            sysctl_config_path=Path("/tmp/sysctl.conf"),
        ),
        gatekeeper=GatekeeperConfig(
            auth_password="secret",
            openai_api_key="sk-test",
        ),
    )
    calls: list[str] = []

    monkeypatch.setattr(
        "mama.net.apply.apply_sysctl",
        lambda *_: calls.append("apply_sysctl"),
    )
    monkeypatch.setattr(
        "mama.net.apply.reload_sysctl",
        lambda *_: calls.append("reload_sysctl"),
    )
    monkeypatch.setattr(
        "mama.net.apply.apply_hostapd_config",
        lambda *_: calls.append("apply_hostapd"),
    )
    monkeypatch.setattr(
        "mama.net.apply.reload_hostapd",
        lambda *_: calls.append("reload_hostapd"),
    )
    monkeypatch.setattr(
        "mama.net.apply.apply_nftables_rules",
        lambda *_: calls.append("apply_nftables"),
    )
    monkeypatch.setattr(
        "mama.net.apply.reload_nftables",
        lambda *_: calls.append("reload_nftables"),
    )
    monkeypatch.setattr(
        "mama.net.apply.apply_dns_block_state",
        lambda *_: calls.append("apply_dns"),
    )

    apply_network_stack(config)

    assert "apply_sysctl" in calls
    assert "reload_sysctl" in calls
    assert "apply_hostapd" in calls
    assert "reload_hostapd" in calls
    assert "apply_nftables" in calls
    assert "reload_nftables" in calls
    assert "apply_dns" in calls
