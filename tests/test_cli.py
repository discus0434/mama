from mama.cli import main
from mama.config import AppConfig, GatekeeperConfig, NetworkConfig


def _config() -> AppConfig:
    return AppConfig(
        network=NetworkConfig(ssid="mama", passphrase="password123"),
        gatekeeper=GatekeeperConfig(
            auth_password="secret",
            openai_api_key="sk-test",
        ),
    )


def test_cli_apply_net_calls_apply_network_stack() -> None:
    called: dict[str, object] = {}

    def _loader() -> AppConfig:
        return _config()

    def _apply(config: AppConfig) -> None:
        called["ssid"] = config.network.ssid

    exit_code = main(
        ["apply-net"],
        config_loader=_loader,
        apply_network=_apply,
        apply_dns=lambda *_: None,
    )

    assert exit_code == 0
    assert called["ssid"] == "mama"


def test_cli_apply_dns_defaults_to_block() -> None:
    called: dict[str, object] = {}

    def _loader() -> AppConfig:
        return _config()

    def _apply(network, unblock: bool) -> None:  # type: ignore[no-untyped-def]
        called["unblock"] = unblock

    exit_code = main(
        ["apply-dns"],
        config_loader=_loader,
        apply_network=lambda *_: None,
        apply_dns=_apply,
    )

    assert exit_code == 0
    assert called["unblock"] is False


def test_cli_apply_dns_unblock() -> None:
    called: dict[str, object] = {}

    def _loader() -> AppConfig:
        return _config()

    def _apply(network, unblock: bool) -> None:  # type: ignore[no-untyped-def]
        called["unblock"] = unblock

    exit_code = main(
        ["apply-dns", "--unblock"],
        config_loader=_loader,
        apply_network=lambda *_: None,
        apply_dns=_apply,
    )

    assert exit_code == 0
    assert called["unblock"] is True
