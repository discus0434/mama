from openai import OpenAI

from mama.config import AppConfig
from mama.gatekeeper.models import AccessRequest, Decision, DecisionMeta, DecisionResult


def request_decision(request: AccessRequest, config: AppConfig) -> DecisionResult:
    policy = config.exception_policy
    prompt = (
        "You are a strict gatekeeper for WiFi exceptions. "
        "Default to deny unless the request is clearly necessary. "
        f"If approved, choose the smallest reasonable minutes between {policy.min_minutes} "
        f"and {policy.max_minutes}. If denied, minutes must be 0. "
        "Return a short reason and any policy flags as a list."
    )
    user_payload = (
        "Access request:\n"
        f"- purpose: {request.purpose}\n"
        f"- deadline: {request.deadline or 'n/a'}\n"
        f"- no_alternative: {request.no_alternative or 'n/a'}\n"
        f"- requested_minutes: {request.requested_minutes}\n"
    )
    client = OpenAI(api_key=config.gatekeeper.openai_api_key)
    response = client.responses.parse(
        model=config.gatekeeper.openai_model,
        input=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_payload},
        ],
        text_format=Decision,
        reasoning={"effort": config.gatekeeper.reasoning_effort},
    )
    decision = response.output_parsed
    if decision is None:
        raise RuntimeError("OpenAI response was not parsed")
    return DecisionResult(decision=decision, meta=DecisionMeta(source="gpt"))
