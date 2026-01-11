import subprocess
from pathlib import Path

from mama.config import AppConfig, NetworkConfig
from mama.net.firewall import render_nftables
from mama.net.hostapd import render_hostapd
from mama.net.render import render_dnsmasq


def render_sysctl(_: NetworkConfig) -> str:
    lines = [
        "net.ipv4.ip_forward=1",
        "net.ipv6.conf.all.forwarding=1",
        "net.ipv6.conf.default.forwarding=1",
    ]
    return "\n".join(lines) + "\n"


def apply_sysctl(config: NetworkConfig, path: Path) -> None:
    _write_file(path, render_sysctl(config))


def apply_dnsmasq_config(
    config: NetworkConfig, blocklist_paths: list[Path], path: Path
) -> None:
    if not path.parent.exists():
        raise FileNotFoundError(path)
    content = render_dnsmasq(config, blocklist_paths)
    _write_file(path, content)


def apply_nftables_rules(rules: str, path: Path) -> None:
    if not path.parent.exists():
        raise FileNotFoundError(path)
    _write_file(path, rules)


def apply_hostapd_config(config: NetworkConfig, path: Path) -> None:
    if not path.parent.exists():
        raise FileNotFoundError(path)
    _write_file(path, render_hostapd(config))


def apply_network_stack(config: AppConfig) -> None:
    network = config.network
    apply_sysctl(network, network.sysctl_config_path)
    reload_sysctl()
    apply_hostapd_config(network, network.hostapd_config_path)
    reload_hostapd()
    rules = render_nftables(network, config.gatekeeper.port)
    apply_nftables_rules(rules, network.nftables_config_path)
    reload_nftables(network.nftables_config_path)
    apply_dns_block_state(network, False)


def apply_dns_block_state(config: NetworkConfig, unblock: bool) -> None:
    paths = [] if unblock else list(config.blocklist_paths)
    apply_dnsmasq_config(config, paths, config.dnsmasq_config_path)
    reload_dnsmasq()


def reload_dnsmasq(command: list[str] | None = None) -> None:
    cmd = command or ["systemctl", "reload", "dnsmasq"]
    result = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or "dnsmasq reload failed"
        raise RuntimeError(f"dnsmasq reload failed: {message}")


def reload_hostapd(command: list[str] | None = None) -> None:
    cmd = command or ["systemctl", "restart", "hostapd"]
    result = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or "hostapd restart failed"
        raise RuntimeError(f"hostapd restart failed: {message}")


def reload_nftables(path: Path, command: list[str] | None = None) -> None:
    cmd = command or ["nft", "-f", str(path)]
    result = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or "nftables apply failed"
        raise RuntimeError(f"nftables apply failed: {message}")


def reload_sysctl(command: list[str] | None = None) -> None:
    cmd = command or ["sysctl", "--system"]
    result = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or "sysctl reload failed"
        raise RuntimeError(f"sysctl reload failed: {message}")


def _write_file(path: Path, content: str) -> None:
    path.write_text(content)
