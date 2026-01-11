import json
from pathlib import Path

from mama.config import RewardConfig
from mama.gatekeeper.models import State


def initial_state(reward: RewardConfig) -> State:
    return State(
        reward_start=reward.start_time,
        reward_enabled=reward.enabled,
        reward_duration_minutes=reward.duration_minutes,
    )


def load_state(path: Path, reward: RewardConfig | None = None) -> State:
    if not path.exists():
        if reward is None:
            raise FileNotFoundError(path)
        return initial_state(reward)
    data = json.loads(path.read_text())
    return State.model_validate(data)


def save_state(path: Path, state: State) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = state.model_dump(mode="json")
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False))
    tmp_path.replace(path)


def append_log(path: Path, entry: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False))
        handle.write("\n")
