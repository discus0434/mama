from pathlib import Path

from mama.net.dnsmasq import load_blocklists


def test_blocklist_files_are_valid() -> None:
    root = Path(__file__).resolve().parents[1]
    paths = [
        root / "data" / "blocklists" / "x.txt",
        root / "data" / "blocklists" / "youtube.txt",
        root / "data" / "blocklists" / "tiktok.txt",
    ]

    domains = load_blocklists(paths)

    assert "x.com" in domains
    assert "youtube.com" in domains
    assert "tiktok.com" in domains
