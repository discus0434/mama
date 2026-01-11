from mama.config import GatekeeperConfig, NetworkConfig
from mama.net.firewall import render_nftables
from mama.net.hostapd import render_hostapd


def test_render_hostapd_includes_basic_wifi_settings() -> None:
    config = NetworkConfig(ssid="mama", passphrase="password123")

    rendered = render_hostapd(config)

    assert "interface=wlan0" in rendered
    assert "ssid=mama" in rendered
    assert "country_code=JP" in rendered
    assert "wpa_passphrase=password123" in rendered
    assert "wpa=2" in rendered
    assert "driver=nl80211" in rendered


def test_render_nftables_allows_gateway_traffic() -> None:
    network = NetworkConfig(ssid="mama", passphrase="password123")
    gatekeeper = GatekeeperConfig(auth_password="secret", openai_api_key="sk-test")

    rendered = render_nftables(network, gatekeeper.port)

    assert "table inet filter" in rendered
    assert 'iifname "wlan0"' in rendered
    assert 'oifname "eth0" masquerade' in rendered
    assert "tcp dport { 53, 8080 }" in rendered
    assert "udp dport { 53, 67, 68 }" in rendered
