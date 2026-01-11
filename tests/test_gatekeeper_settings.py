from datetime import time
from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient

from mama.config import AppConfig, GatekeeperConfig, NetworkConfig
from mama.gatekeeper.app import create_app
from mama.gatekeeper.storage import load_state


def _build_client(tmp_path: Path, dns_apply_handler=None) -> TestClient:
    config = AppConfig(
        network=NetworkConfig(ssid="mama", passphrase="password123"),
        gatekeeper=GatekeeperConfig(
            auth_password="secret",
            openai_api_key="sk-test",
            state_path=tmp_path / "state.json",
            log_path=tmp_path / "requests.jsonl",
        ),
    )
    app = create_app(config, dns_apply_handler=dns_apply_handler)
    return TestClient(app)


def test_update_settings_persists_reward_time(tmp_path: Path) -> None:
    client = _build_client(tmp_path, dns_apply_handler=lambda *_: None)

    response = client.post(
        "/settings",
        json={"reward_start": "22:30", "reward_enabled": True},
        auth=("mama", "secret"),
    )

    assert response.status_code == status.HTTP_200_OK

    state = load_state(tmp_path / "state.json", reward=None)
    assert state.reward_start == time(22, 30)
    assert state.reward_enabled is True


def test_update_settings_rejects_bad_time(tmp_path: Path) -> None:
    client = _build_client(tmp_path, dns_apply_handler=lambda *_: None)

    response = client.post(
        "/settings",
        json={"reward_start": "25:00", "reward_enabled": True},
        auth=("mama", "secret"),
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_update_settings_accepts_form_payload(tmp_path: Path) -> None:
    client = _build_client(tmp_path, dns_apply_handler=lambda *_: None)

    response = client.post(
        "/settings",
        data={"reward_start": "22:30", "reward_enabled": "on"},
        auth=("mama", "secret"),
    )

    assert response.status_code == status.HTTP_200_OK

    state = load_state(tmp_path / "state.json", reward=None)
    assert state.reward_start == time(22, 30)
    assert state.reward_enabled is True
