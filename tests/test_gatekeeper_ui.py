from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient

from mama.config import AppConfig, GatekeeperConfig, NetworkConfig
from mama.gatekeeper.app import create_app


def _build_client() -> TestClient:
    config = AppConfig(
        network=NetworkConfig(ssid="mama", passphrase="password123"),
        gatekeeper=GatekeeperConfig(
            auth_password="secret",
            openai_api_key="sk-test",
        ),
    )
    app = create_app(config, dns_apply_handler=lambda *_: None)
    return TestClient(app)


def test_index_returns_html_with_form(tmp_path: Path, monkeypatch) -> None:
    template = tmp_path / "index.html"
    template.write_text("<h2>Request access</h2><div>reward_start</div>")
    monkeypatch.setattr("mama.gatekeeper.app.TEMPLATE_PATH", template)

    client = _build_client()

    response = client.get("/", auth=("mama", "secret"))

    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]
    assert "Request access" in response.text
    assert "reward_start" in response.text
