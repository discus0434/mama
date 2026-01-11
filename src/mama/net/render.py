from pathlib import Path
from typing import Iterable

from mama.config import NetworkConfig
from mama.net.dnsmasq import compile_blocklist, load_blocklists


def render_dnsmasq(config: NetworkConfig, blocklist_paths: Iterable[Path]) -> str:
    lines = [
        "domain-needed",
        "bogus-priv",
        "bind-interfaces",
        f"interface={config.wlan_interface}",
        (
            f"dhcp-range={config.dhcp_start},{config.dhcp_end},"
            f"{config.lan_netmask},{config.dhcp_lease}"
        ),
        f"dhcp-option=option:router,{config.lan_address}",
        f"dhcp-option=option:dns-server,{config.lan_address}",
    ]
    paths = list(blocklist_paths)
    blocked_domains = load_blocklists(paths) if paths else []
    blocklist = compile_blocklist(blocked_domains)
    if blocklist:
        lines.append(blocklist.rstrip("\n"))
    return "\n".join(lines) + "\n"


def render_hostapd(config: NetworkConfig) -> str:
    lines = [
        "driver=nl80211",
        f"interface={config.wlan_interface}",
        f"ssid={config.ssid}",
        f"country_code={config.country_code}",
        f"hw_mode={config.hw_mode}",
        f"channel={config.wifi_channel}",
        "auth_algs=1",
        "wpa=2",
        f"wpa_passphrase={config.passphrase}",
        "wpa_key_mgmt=WPA-PSK",
        "rsn_pairwise=CCMP",
        "wmm_enabled=1",
        "ieee80211n=1",
    ]
    if config.hw_mode == "a":
        lines.append("ieee80211ac=1")
    lines.append("ieee80211d=1")
    return "\n".join(lines) + "\n"


def render_nftables(config: NetworkConfig, gatekeeper_port: int) -> str:
    tcp_ports = sorted({53, gatekeeper_port})
    tcp_ports_str = ", ".join(str(port) for port in tcp_ports)
    lines = [
        "table inet filter {",
        "  chain input {",
        "    type filter hook input priority 0;",
        "    policy drop;",
        '    iif "lo" accept',
        "    ct state established,related accept",
        f'    iifname "{config.wlan_interface}" udp dport {{ 53, 67, 68 }} accept',
        f'    iifname "{config.wlan_interface}" tcp dport {{ {tcp_ports_str} }} accept',
        "    ip protocol icmp accept",
        "    ip6 nexthdr icmpv6 accept",
        "  }",
        "  chain forward {",
        "    type filter hook forward priority 0;",
        "    policy drop;",
        "    ct state established,related accept",
        f'    iifname "{config.wlan_interface}" oifname "{config.wan_interface}" accept',
        "  }",
        "}",
        "table ip nat {",
        "  chain postrouting {",
        "    type nat hook postrouting priority 100;",
        f'    oifname "{config.wan_interface}" masquerade',
        "  }",
        "}",
    ]
    return "\n".join(lines) + "\n"
