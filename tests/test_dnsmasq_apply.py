from dataclasses import dataclass
from pathlib import Path

import pytest

from mama.config import NetworkConfig
from mama.net.apply import (
    apply_dns_block_state,
    apply_dnsmasq_config,
    apply_nftables_rules,
    apply_sysctl,
    reload_dnsmasq,
)
from mama.net.firewall import render_nftables


def test_apply_sysctl_writes_conf(tmp_path: Path) -> None:
    config = NetworkConfig(ssid="mama", passphrase="password123")

    path = tmp_path / "sysctl.conf"
    apply_sysctl(config, path)

    assert "net.ipv4.ip_forward=1" in path.read_text()


def test_apply_dnsmasq_config_writes_config(tmp_path: Path) -> None:
    config = NetworkConfig(ssid="mama", passphrase="password123")

    blocklist = tmp_path / "x.txt"
    blocklist.write_text("x.com\n")
    path = tmp_path / "dnsmasq.conf"
    apply_dnsmasq_config(config, [blocklist], path)

    content = path.read_text()
    assert "interface=wlan0" in content
    assert "address=/x.com/0.0.0.0" in content


def test_apply_dnsmasq_config_rejects_missing_path(tmp_path: Path) -> None:
    config = NetworkConfig(ssid="mama", passphrase="password123")

    blocklist = tmp_path / "x.txt"
    blocklist.write_text("x.com\n")
    missing = tmp_path / "missing" / "dnsmasq.conf"
    with pytest.raises(FileNotFoundError):
        apply_dnsmasq_config(config, [blocklist], missing)


def test_apply_nftables_rules_writes_rules(tmp_path: Path) -> None:
    config = NetworkConfig(ssid="mama", passphrase="password123")
    rules = render_nftables(config, gatekeeper_port=8080)
    path = tmp_path / "nftables.conf"

    apply_nftables_rules(rules, path)

    assert "table inet filter" in path.read_text()


@dataclass
class _RunResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


def test_reload_dnsmasq_invokes_systemctl(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def _fake_run(cmd, check, capture_output, text):  # type: ignore[no-untyped-def]
        captured["cmd"] = cmd
        captured["check"] = check
        captured["capture_output"] = capture_output
        captured["text"] = text
        return _RunResult(returncode=0)

    monkeypatch.setattr("mama.net.apply.subprocess.run", _fake_run)

    reload_dnsmasq()

    assert captured["cmd"] == ["systemctl", "reload", "dnsmasq"]
    assert captured["check"] is False
    assert captured["capture_output"] is True
    assert captured["text"] is True


def test_reload_dnsmasq_raises_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake_run(cmd, check, capture_output, text):  # type: ignore[no-untyped-def]
        return _RunResult(returncode=1, stderr="boom")

    monkeypatch.setattr("mama.net.apply.subprocess.run", _fake_run)

    with pytest.raises(RuntimeError, match="dnsmasq reload failed"):
        reload_dnsmasq()


def test_apply_dns_block_state_unblocks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = NetworkConfig(
        ssid="mama",
        passphrase="password123",
        dnsmasq_config_path=tmp_path / "dnsmasq.conf",
        blocklist_paths=[tmp_path / "x.txt"],
    )
    (tmp_path / "dnsmasq.conf").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "x.txt").write_text("x.com\n")

    called: dict[str, object] = {}

    def _fake_reload() -> None:
        called["reloaded"] = True

    monkeypatch.setattr("mama.net.apply.reload_dnsmasq", _fake_reload)

    apply_dns_block_state(config, unblock=True)

    content = (tmp_path / "dnsmasq.conf").read_text()
    assert "address=/" not in content
    assert called["reloaded"] is True


def test_apply_dns_block_state_blocks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = NetworkConfig(
        ssid="mama",
        passphrase="password123",
        dnsmasq_config_path=tmp_path / "dnsmasq.conf",
        blocklist_paths=[tmp_path / "x.txt"],
    )
    (tmp_path / "dnsmasq.conf").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "x.txt").write_text("x.com\n")

    monkeypatch.setattr("mama.net.apply.reload_dnsmasq", lambda: None)

    apply_dns_block_state(config, unblock=False)

    content = (tmp_path / "dnsmasq.conf").read_text()
    assert "address=/x.com/0.0.0.0" in content
