import asyncio
import contextlib
import secrets
from datetime import datetime
from pathlib import Path
from typing import Callable
from urllib.parse import parse_qs
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import ValidationError

from mama.config import AppConfig, GatekeeperConfig, RewardSettings
from mama.gatekeeper import openai_client
from mama.gatekeeper.models import (
    AccessRequest,
    Decision,
    DecisionMeta,
    DecisionResult,
    State,
)
from mama.gatekeeper.policy import (
    apply_decision,
    evaluate_local_limits,
    fallback_minutes,
)
from mama.gatekeeper.scheduler import current_window, next_transition, should_unblock
from mama.gatekeeper.storage import append_log, load_state, save_state
from mama.net.apply import apply_dns_block_state

security = HTTPBasic()
TEMPLATE_PATH = Path("templates/index.html")

DecisionProvider = Callable[[AccessRequest, AppConfig], DecisionResult]
DnsApplyHandler = Callable[[AppConfig, bool], None]


def create_app(
    config: AppConfig,
    *,
    decision_provider: DecisionProvider | None = None,
    dns_apply_handler: DnsApplyHandler | None = None,
) -> FastAPI:
    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.stop_event = asyncio.Event()
        app.state.scheduler_task = asyncio.create_task(_dns_scheduler(app))
        try:
            yield
        finally:
            stop_event: asyncio.Event = app.state.stop_event
            stop_event.set()
            task = app.state.scheduler_task
            if task is not None:
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

    app = FastAPI(title="mama gatekeeper", lifespan=lifespan)
    app.state.config = config
    app.state.decision_provider = decision_provider or openai_client.request_decision

    def _default_dns_apply_handler(app_config: AppConfig, unblock: bool) -> None:
        apply_dns_block_state(app_config.network, unblock)

    app.state.dns_apply_handler = dns_apply_handler or _default_dns_apply_handler

    def require_auth(
        credentials: HTTPBasicCredentials = Depends(security),
    ) -> str:
        gatekeeper_config = _get_gatekeeper_config(app)
        username_ok = secrets.compare_digest(
            credentials.username, gatekeeper_config.auth_username
        )
        password_ok = secrets.compare_digest(
            credentials.password, gatekeeper_config.auth_password
        )
        if not (username_ok and password_ok):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
                headers={"WWW-Authenticate": "Basic"},
            )
        return credentials.username

    @app.get("/health")
    def health(_: str = Depends(require_auth)) -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse)
    def index(_: str = Depends(require_auth)) -> str:
        return _render_index()

    @app.post("/request")
    async def request_access(
        request: Request, _: str = Depends(require_auth)
    ) -> dict[str, object]:
        payload = await _parse_access_request(request)
        gatekeeper_config = _get_gatekeeper_config(app)
        tz = ZoneInfo(gatekeeper_config.timezone)
        now = datetime.now(tz)
        state = load_state(gatekeeper_config.state_path, config.reward)
        verdict = evaluate_local_limits(state, config.exception_policy, now, tz)
        if not verdict.allowed:
            result = DecisionResult(
                decision=Decision(
                    approved=False,
                    minutes=0,
                    reason=verdict.reason,
                    policy_flags=verdict.flags,
                ),
                meta=DecisionMeta(source="local_limit"),
            )
            state, result.decision = apply_decision(
                state, result.decision, config.exception_policy, now
            )
            save_state(gatekeeper_config.state_path, state)
            append_log(
                gatekeeper_config.log_path,
                {
                    "time": now.isoformat(),
                    "request": payload.model_dump(mode="json"),
                    "decision": result.decision.model_dump(mode="json"),
                    "source": result.meta.source,
                },
            )
            _apply_dns_state(app, config, state, now, tz)
            return result.model_dump(mode="json")

        try:
            result = _get_decision_provider(app)(payload, config)
        except Exception:
            result = DecisionResult(
                decision=Decision(
                    approved=True,
                    minutes=fallback_minutes(
                        payload.requested_minutes, config.exception_policy
                    ),
                    reason="fallback",
                    policy_flags=["fallback"],
                ),
                meta=DecisionMeta(source="fallback"),
            )

        state, result.decision = apply_decision(
            state, result.decision, config.exception_policy, now
        )
        save_state(gatekeeper_config.state_path, state)
        append_log(
            gatekeeper_config.log_path,
            {
                "time": now.isoformat(),
                "request": payload.model_dump(mode="json"),
                "decision": result.decision.model_dump(mode="json"),
                "source": result.meta.source,
            },
        )
        _apply_dns_state(app, config, state, now, tz)
        return result.model_dump(mode="json")

    @app.post("/settings")
    async def update_settings(
        request: Request, _: str = Depends(require_auth)
    ) -> dict[str, object]:
        payload = await _parse_reward_settings(request)
        gatekeeper_config = _get_gatekeeper_config(app)
        tz = ZoneInfo(gatekeeper_config.timezone)
        now = datetime.now(tz)
        state = load_state(gatekeeper_config.state_path, config.reward)
        state.reward_start = payload.reward_start
        state.reward_enabled = payload.reward_enabled
        save_state(gatekeeper_config.state_path, state)
        _apply_dns_state(app, config, state, now, tz)
        return {
            "reward_start": state.reward_start,
            "reward_enabled": state.reward_enabled,
        }

    return app


def _get_gatekeeper_config(app: FastAPI) -> GatekeeperConfig:
    config = getattr(app.state, "config", None)
    if config is None:
        raise RuntimeError("Gatekeeper config is not set")
    return config.gatekeeper


def _get_app_config(app: FastAPI) -> AppConfig:
    config = getattr(app.state, "config", None)
    if config is None:
        raise RuntimeError("App config is not set")
    return config


def _get_decision_provider(app: FastAPI) -> DecisionProvider:
    provider = getattr(app.state, "decision_provider", None)
    if provider is None:
        raise RuntimeError("Decision provider is not set")
    return provider


def _get_dns_apply_handler(app: FastAPI) -> DnsApplyHandler:
    handler = getattr(app.state, "dns_apply_handler", None)
    if handler is None:
        raise RuntimeError("DNS apply handler is not set")
    return handler


def _apply_dns_state(
    app: FastAPI, config: AppConfig, state: State, now: datetime, tz: ZoneInfo
) -> None:
    window = current_window(state, now, tz)
    unblock = should_unblock(window)
    _get_dns_apply_handler(app)(config, unblock)


async def _dns_scheduler(app: FastAPI) -> None:
    stop_event: asyncio.Event = app.state.stop_event
    last_unblock: bool | None = None
    while not stop_event.is_set():
        config = _get_app_config(app)
        tz = ZoneInfo(config.gatekeeper.timezone)
        now = datetime.now(tz)
        state = load_state(config.gatekeeper.state_path, config.reward)
        window = current_window(state, now, tz)
        unblock = should_unblock(window)
        if last_unblock is None or unblock != last_unblock:
            _get_dns_apply_handler(app)(config, unblock)
            last_unblock = unblock
        next_time = next_transition(state, now, tz)
        if next_time is None:
            sleep_for = 30.0
        else:
            delta = (next_time - now).total_seconds()
            sleep_for = max(1.0, delta)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=sleep_for)
        except asyncio.TimeoutError:
            continue


def _is_json_request(request: Request) -> bool:
    content_type = request.headers.get("content-type", "")
    return "application/json" in content_type.lower()


async def _parse_access_request(request: Request) -> AccessRequest:
    raw: object
    if _is_json_request(request):
        raw = await request.json()
    else:
        body = (await request.body()).decode("utf-8")
        parsed = parse_qs(body, keep_blank_values=True)
        raw = {key: values[0] for key, values in parsed.items() if values}
    try:
        return AccessRequest.model_validate(raw)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc


async def _parse_reward_settings(request: Request) -> RewardSettings:
    raw: dict[str, object]
    if _is_json_request(request):
        loaded = await request.json()
        raw = loaded if isinstance(loaded, dict) else {"reward_start": loaded}
    else:
        body = (await request.body()).decode("utf-8")
        parsed = parse_qs(body, keep_blank_values=True)
        raw = {key: values[0] for key, values in parsed.items() if values}
        raw["reward_enabled"] = "reward_enabled" in raw
    try:
        return RewardSettings.model_validate(raw)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc


def _render_index() -> str:
    if not TEMPLATE_PATH.exists():
        raise RuntimeError(f"template not found: {TEMPLATE_PATH}")
    return TEMPLATE_PATH.read_text(encoding="utf-8")
