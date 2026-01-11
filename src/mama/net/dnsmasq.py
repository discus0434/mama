import re
from pathlib import Path
from typing import Iterable

_DOMAIN_LABEL = re.compile(r"^[a-z0-9-]{1,63}$")


def _normalize_domain(raw: str) -> str:
    candidate = raw.strip().lower()
    if not candidate:
        raise ValueError("domain is empty")
    if candidate.startswith("."):
        candidate = candidate[1:]
    if candidate.endswith("."):
        candidate = candidate[:-1]
    if not candidate:
        raise ValueError("domain is empty")
    return candidate


def _validate_domain(domain: str) -> None:
    if len(domain) > 253:
        raise ValueError(f"invalid domain: {domain}")
    labels = domain.split(".")
    if any(label == "" for label in labels):
        raise ValueError(f"invalid domain: {domain}")
    for label in labels:
        if not _DOMAIN_LABEL.match(label):
            raise ValueError(f"invalid domain: {domain}")
        if label.startswith("-") or label.endswith("-"):
            raise ValueError(f"invalid domain: {domain}")


def parse_blocklist_lines(lines: Iterable[str]) -> list[str]:
    domains: set[str] = set()
    for line in lines:
        content = line.split("#", 1)[0].strip()
        if not content:
            continue
        domain = _normalize_domain(content)
        _validate_domain(domain)
        domains.add(domain)
    return sorted(domains)


def load_blocklists(paths: Iterable[Path]) -> list[str]:
    domains: set[str] = set()
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(path)
        entries = parse_blocklist_lines(path.read_text().splitlines())
        domains.update(entries)
    return sorted(domains)


def compile_blocklist(domains: Iterable[str]) -> str:
    normalized: set[str] = set()
    for raw in domains:
        domain = _normalize_domain(raw)
        _validate_domain(domain)
        normalized.add(domain)
    lines: list[str] = []
    for domain in sorted(normalized):
        lines.append(f"address=/{domain}/0.0.0.0")
        lines.append(f"address=/{domain}/::")
    return "\n".join(lines) + ("\n" if lines else "")
