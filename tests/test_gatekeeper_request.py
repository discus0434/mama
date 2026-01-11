from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from mama.config import AppConfig, GatekeeperConfig, NetworkConfig
from mama.gatekeeper.app import create_app
from mama.gatekeeper.models import (
    AccessRequest,
    Decision,
    DecisionMeta,
    DecisionResult,
    State,
)
from mama.gatekeeper.storage import load_state, save_state


def _build_client(
    tmp_path: Path, decision_provider=None, dns_apply_handler=None, now_provider=None
) -> TestClient:
    config = AppConfig(
        network=NetworkConfig(ssid="mama", passphrase="password123"),
        gatekeeper=GatekeeperConfig(
            auth_password="secret",
            openai_api_key="sk-test",
            state_path=tmp_path / "state.json",
            log_path=tmp_path / "requests.jsonl",
        ),
    )
    app = create_app(
        config,
        decision_provider=decision_provider,
        dns_apply_handler=dns_apply_handler,
        now_provider=now_provider,
    )
    return TestClient(app)


def test_request_denied_by_daily_limit(tmp_path: Path) -> None:
    tz = ZoneInfo("Asia/Tokyo")
    now = datetime(2026, 1, 11, 9, 0, tzinfo=tz)
    state = State(
        reward_start=datetime(2026, 1, 11, 21, 0, tzinfo=tz).time(),
        daily_count=10,
        last_reset_date=now.date(),
    )
    state_path = tmp_path / "state.json"
    save_state(state_path, state)

    client = _build_client(
        tmp_path,
        dns_apply_handler=lambda *_: None,
        now_provider=lambda _: now,
    )
    payload = AccessRequest(purpose="work", requested_minutes=10).model_dump()

    response = client.post("/request", json=payload, auth=("mama", "secret"))

    assert response.status_code == 200
    data = response.json()["decision"]
    assert data["approved"] is False
    assert data["minutes"] == 0
    assert response.json()["meta"]["source"] == "local_limit"


def test_request_fallback_when_decider_fails(tmp_path: Path) -> None:
    def failing_decider(_: AccessRequest, __: AppConfig) -> DecisionResult:
        raise RuntimeError("boom")

    client = _build_client(
        tmp_path,
        decision_provider=failing_decider,
        dns_apply_handler=lambda *_: None,
    )
    payload = AccessRequest(purpose="work", requested_minutes=12).model_dump()

    response = client.post("/request", json=payload, auth=("mama", "secret"))

    assert response.status_code == 200
    data = response.json()["decision"]
    assert data["approved"] is True
    assert data["minutes"] == 12
    assert "fallback" in data["policy_flags"]
    assert response.json()["meta"]["source"] == "fallback"

    state = load_state(tmp_path / "state.json")
    assert state.daily_count == 1


def test_request_triggers_dns_apply_handler(tmp_path: Path) -> None:
    called: dict[str, object] = {}

    def _handler(config: AppConfig, should_unblock: bool) -> None:
        called["ssid"] = config.network.ssid
        called["unblock"] = should_unblock

    def _decision(_: AccessRequest, __: AppConfig) -> DecisionResult:
        return DecisionResult(
            decision=Decision(approved=True, minutes=5, reason="ok", policy_flags=[]),
            meta=DecisionMeta(source="gpt"),
        )

    client = _build_client(
        tmp_path, decision_provider=_decision, dns_apply_handler=_handler
    )
    payload = AccessRequest(purpose="work", requested_minutes=5).model_dump()

    response = client.post("/request", json=payload, auth=("mama", "secret"))

    assert response.status_code == 200
    assert called["ssid"] == "mama"
    assert called["unblock"] is True


def test_request_uses_default_dns_apply_handler_with_network_config(
    tmp_path: Path, monkeypatch
) -> None:
    captured: dict[str, object] = {}

    def _fake_apply_dns_block_state(config, unblock: bool) -> None:  # type: ignore[no-untyped-def]
        captured["config"] = config
        captured["unblock"] = unblock

    monkeypatch.setattr(
        "mama.gatekeeper.app.apply_dns_block_state", _fake_apply_dns_block_state
    )

    def _decision(_: AccessRequest, __: AppConfig) -> DecisionResult:
        return DecisionResult(
            decision=Decision(approved=True, minutes=5, reason="ok", policy_flags=[]),
            meta=DecisionMeta(source="gpt"),
        )

    client = _build_client(tmp_path, decision_provider=_decision)
    payload = AccessRequest(purpose="work", requested_minutes=5).model_dump()

    response = client.post("/request", json=payload, auth=("mama", "secret"))

    assert response.status_code == 200
    assert isinstance(captured["config"], NetworkConfig)
    assert captured["unblock"] is True


def test_request_accepts_form_payload(tmp_path: Path) -> None:
    def _decision(_: AccessRequest, __: AppConfig) -> DecisionResult:
        return DecisionResult(
            decision=Decision(approved=True, minutes=5, reason="ok", policy_flags=[]),
            meta=DecisionMeta(source="gpt"),
        )

    client = _build_client(
        tmp_path,
        decision_provider=_decision,
        dns_apply_handler=lambda *_: None,
    )

    response = client.post(
        "/request",
        data={"purpose": "work", "requested_minutes": "5"},
        auth=("mama", "secret"),
    )

    assert response.status_code == 200
    data = response.json()["decision"]
    assert data["approved"] is True


def test_request_rejects_invalid_requested_minutes(tmp_path: Path) -> None:
    client = _build_client(tmp_path, dns_apply_handler=lambda *_: None)

    response = client.post(
        "/request",
        json={"purpose": "work", "requested_minutes": 0},
        auth=("mama", "secret"),
    )

    assert response.status_code == 422
