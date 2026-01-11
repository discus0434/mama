from pathlib import Path

import pytest

from mama.config import NetworkConfig
from mama.net.dnsmasq import compile_blocklist, load_blocklists, parse_blocklist_lines
from mama.net.render import render_dnsmasq


def test_parse_blocklist_lines_normalizes_and_dedupes() -> None:
    lines = [
        "# comment",
        " X.com ",
        "x.com",
        "youtube.com # note",
        "",
        ".m.youtube.com",
        "tiktok.com.",
    ]

    assert parse_blocklist_lines(lines) == [
        "m.youtube.com",
        "tiktok.com",
        "x.com",
        "youtube.com",
    ]


def test_parse_blocklist_lines_rejects_invalid_domain() -> None:
    with pytest.raises(ValueError):
        parse_blocklist_lines(["http://x.com"])


def test_load_blocklists_reads_multiple_files(tmp_path: Path) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("x.com\n")
    second.write_text("# comment\nyoutube.com\nx.com\n")

    assert load_blocklists([first, second]) == ["x.com", "youtube.com"]


def test_compile_blocklist_outputs_ipv4_ipv6_lines() -> None:
    rendered = compile_blocklist(["x.com"])

    assert rendered == "address=/x.com/0.0.0.0\naddress=/x.com/::\n"


def test_render_dnsmasq_includes_config_and_blocklist(tmp_path: Path) -> None:
    config = NetworkConfig(ssid="mama", passphrase="password123")

    blocklist = tmp_path / "x.txt"
    blocklist.write_text("x.com\n")

    rendered = render_dnsmasq(config, [blocklist])

    assert "interface=wlan0" in rendered
    assert "dhcp-range=192.168.50.50,192.168.50.150" in rendered
    assert "address=/x.com/0.0.0.0" in rendered
