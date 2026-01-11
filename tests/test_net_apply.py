from mama.config import NetworkConfig
from mama.net.apply import render_sysctl


def test_render_sysctl_enables_forwarding() -> None:
    config = NetworkConfig(ssid="mama", passphrase="password123")

    rendered = render_sysctl(config)

    assert "net.ipv4.ip_forward=1" in rendered
    assert "net.ipv6.conf.all.forwarding=1" in rendered
    assert "net.ipv6.conf.default.forwarding=1" in rendered
