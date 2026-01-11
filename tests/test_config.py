import pytest
from pydantic import ValidationError

from python_template_for_codex.config import ApplicationConfig


def test_valid_config_accepts_values() -> None:
    config = ApplicationConfig(name="demo-service", version="0.1.0", debug=True)

    assert config.name == "demo-service"
    assert config.version == "0.1.0"
    assert config.debug is True


def test_debug_defaults_to_false() -> None:
    config = ApplicationConfig(name="demo", version="1.2.3")

    assert config.debug is False


def test_version_requires_semver_pattern() -> None:
    with pytest.raises(ValidationError) as excinfo:
        ApplicationConfig(name="demo", version="v1")

    message = str(excinfo.value)
    assert "version" in message
    assert "string_pattern_mismatch" in message


def test_name_is_required() -> None:
    with pytest.raises(ValidationError) as excinfo:
        ApplicationConfig(version="1.0.0")  # type: ignore[call-arg]

    assert "name" in str(excinfo.value)
