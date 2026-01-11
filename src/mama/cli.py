import argparse
from typing import Callable, Sequence

from mama.config import AppConfig
from mama.env import load_config_from_env
from mama.net.apply import apply_dns_block_state, apply_network_stack


def main(
    argv: Sequence[str] | None = None,
    *,
    config_loader: Callable[[], AppConfig] = load_config_from_env,
    apply_network: Callable[[AppConfig], None] = apply_network_stack,
    apply_dns: Callable[[object, bool], None] = apply_dns_block_state,
) -> int:
    parser = argparse.ArgumentParser(prog="mama")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("apply-net")

    apply_dns_parser = subparsers.add_parser("apply-dns")
    apply_dns_parser.add_argument(
        "--unblock",
        action="store_true",
        help="Disable blocklist temporarily",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)
    config = config_loader()

    if args.command == "apply-net":
        apply_network(config)
        return 0
    if args.command == "apply-dns":
        apply_dns(config.network, bool(args.unblock))
        return 0
    raise RuntimeError("unknown command")


if __name__ == "__main__":
    raise SystemExit(main())
