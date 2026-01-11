from pydantic import BaseModel, Field, field_validator


class ApplicationConfig(BaseModel):
    """Minimal application configuration used as a template example."""

    name: str = Field(
        ..., min_length=1, description="Service or application identifier"
    )
    version: str = Field(
        ...,
        pattern=r"^\d+\.\d+\.\d+$",
        description="Semantic version string (e.g. 1.0.0)",
    )
    debug: bool = Field(
        default=False,
        description="Toggles debug behavior; defaults to False for production safety.",
    )

    @field_validator("version")
    @classmethod
    def _normalize_version(cls, value: str) -> str:
        # Strip a leading "v" to keep config forgiving while still enforcing semver.
        return value.lstrip("v")
