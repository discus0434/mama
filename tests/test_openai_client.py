from typing import Any

import pytest

from mama.config import AppConfig, GatekeeperConfig, NetworkConfig
from mama.gatekeeper.models import AccessRequest, Decision, DecisionResult
from mama.gatekeeper.openai_client import request_decision


class _DummyResponse:
    def __init__(self, parsed: Decision | None) -> None:
        self.output_parsed = parsed


class _DummyResponses:
    def __init__(self, parsed: Decision | None) -> None:
        self.parsed = parsed
        self.kwargs: dict[str, Any] | None = None

    def parse(self, **kwargs: Any) -> _DummyResponse:
        self.kwargs = kwargs
        return _DummyResponse(self.parsed)


class _DummyClient:
    def __init__(self, api_key: str, parsed: Decision | None) -> None:
        self.api_key = api_key
        self.responses = _DummyResponses(parsed)


def _config() -> AppConfig:
    return AppConfig(
        network=NetworkConfig(ssid="mama", passphrase="password123"),
        gatekeeper=GatekeeperConfig(
            auth_password="secret",
            openai_api_key="sk-test",
            openai_model="gpt-5.2",
            reasoning_effort="medium",
        ),
    )


def test_request_decision_calls_responses_parse(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    decision = Decision(
        approved=True,
        minutes=10,
        reason="ok",
        policy_flags=["work"],
    )
    client = _DummyClient("sk-test", decision)

    def _factory(api_key: str) -> _DummyClient:
        assert api_key == "sk-test"
        return client

    monkeypatch.setattr(
        "mama.gatekeeper.openai_client.OpenAI",
        _factory,
    )

    request = AccessRequest(purpose="work", requested_minutes=12)
    result = request_decision(request, _config())

    assert isinstance(result, DecisionResult)
    assert result.decision == decision
    assert result.meta.source == "gpt"
    assert client.responses.kwargs is not None
    assert client.responses.kwargs["model"] == "gpt-5.2"
    assert client.responses.kwargs["reasoning"]["effort"] == "medium"
    assert client.responses.kwargs["text_format"] is Decision


def test_request_decision_raises_when_parse_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _DummyClient("sk-test", parsed=None)

    def _factory(api_key: str) -> _DummyClient:
        return client

    monkeypatch.setattr(
        "mama.gatekeeper.openai_client.OpenAI",
        _factory,
    )

    request = AccessRequest(purpose="work", requested_minutes=12)

    with pytest.raises(RuntimeError, match="OpenAI response was not parsed"):
        request_decision(request, _config())
