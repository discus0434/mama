from fastapi import status
from fastapi.testclient import TestClient

from mama.config import AppConfig, GatekeeperConfig, NetworkConfig
from mama.gatekeeper.app import create_app


def _build_app() -> TestClient:
    config = AppConfig(
        network=NetworkConfig(ssid="mama", passphrase="password123"),
        gatekeeper=GatekeeperConfig(
            auth_password="secret",
            openai_api_key="sk-test",
        ),
    )
    app = create_app(config, dns_apply_handler=lambda *_: None)
    return TestClient(app)


def test_health_requires_basic_auth() -> None:
    client = _build_app()

    response = client.get("/health")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["www-authenticate"].startswith("Basic")


def test_health_accepts_basic_auth() -> None:
    client = _build_app()

    response = client.get("/health", auth=("mama", "secret"))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


def test_lifespan_initializes_scheduler_state() -> None:
    config = AppConfig(
        network=NetworkConfig(ssid="mama", passphrase="password123"),
        gatekeeper=GatekeeperConfig(
            auth_password="secret",
            openai_api_key="sk-test",
        ),
    )
    app = create_app(config, dns_apply_handler=lambda *_: None)

    assert getattr(app.state, "stop_event", None) is None

    with TestClient(app):
        assert app.state.stop_event is not None
        assert app.state.scheduler_task is not None

    assert app.state.stop_event.is_set() is True
    task = app.state.scheduler_task
    assert task is not None
    assert task.cancelled() or task.done()
