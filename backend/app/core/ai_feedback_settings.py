"""Server-side configuration for AI feedback drafting.

Everything here is read from the backend environment only. Nothing is exposed
to the browser: the provider key, model and prices never leave the server.

The feature is OFF unless ``AEOS_AI_FEEDBACK_ENABLED=true``. When it is on but
incompletely configured, requests fail closed with a sanitized 503 rather
than falling back to a default model, price or rubric. No model ID is
hard-coded: the configured model is checked against the provider's live model
list before use (see ``app.services.ai_feedback.provider``).
"""

import os
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import FrozenSet, List, Optional

SUPPORTED_PROVIDERS = ("anthropic",)

# Hard ceilings so a configuration typo cannot create an unbounded request.
MAX_TIMEOUT_SECONDS = 120.0
MAX_RETRIES_CEILING = 3
MAX_OUTPUT_TOKENS_CEILING = 16000


def _bool(name: str) -> bool:
    return os.getenv(name, "false").strip().lower() == "true"


def _int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return -1  # reported by configuration_errors()


def _float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return float(raw)
    except ValueError:
        return -1.0


def _decimal(name: str) -> Optional[Decimal]:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return None
    try:
        return Decimal(raw.strip())
    except InvalidOperation:
        return Decimal(-1)


def _set(name: str) -> FrozenSet[str]:
    raw = os.getenv(name, "")
    return frozenset(item.strip() for item in raw.split(",") if item.strip())


@dataclass(frozen=True)
class AiFeedbackSettings:
    enabled: bool = False
    provider: str = "anthropic"
    model_id: str = ""
    api_key: str = field(default="", repr=False)
    base_url: str = "https://api.anthropic.com"
    timeout_seconds: float = 30.0
    max_retries: int = 2
    max_output_tokens: int = 4096
    # USD per million tokens for the configured model. Required: prices are
    # model-specific and change, so there is no default to go stale.
    input_usd_per_mtok: Optional[Decimal] = None
    output_usd_per_mtok: Optional[Decimal] = None
    # Organizations allowed to use the feature in this synthetic-only phase.
    organization_allowlist: FrozenSet[str] = frozenset()
    # "<rubric_id>@<version>:<sha256>" entries pinned by a human approver.
    approved_rubrics: FrozenSet[str] = frozenset()
    user_hourly_requests: int = 10
    org_daily_requests: int = 100
    user_daily_cost_microusd: int = 1_000_000  # $1.00
    org_daily_cost_microusd: int = 5_000_000  # $5.00
    model_check_ttl_seconds: int = 600

    def configuration_errors(self) -> List[str]:
        """Return configuration problems by setting name, never by value."""
        errors: List[str] = []
        if self.provider not in SUPPORTED_PROVIDERS:
            errors.append("AEOS_AI_FEEDBACK_PROVIDER")
        if not self.model_id:
            errors.append("AEOS_AI_FEEDBACK_MODEL")
        if not self.api_key:
            errors.append("AEOS_AI_FEEDBACK_API_KEY")
        if not self.base_url.startswith("https://"):
            errors.append("AEOS_AI_FEEDBACK_BASE_URL")
        if not 0 < self.timeout_seconds <= MAX_TIMEOUT_SECONDS:
            errors.append("AEOS_AI_FEEDBACK_TIMEOUT_SECONDS")
        if not 0 <= self.max_retries <= MAX_RETRIES_CEILING:
            errors.append("AEOS_AI_FEEDBACK_MAX_RETRIES")
        if not 256 <= self.max_output_tokens <= MAX_OUTPUT_TOKENS_CEILING:
            errors.append("AEOS_AI_FEEDBACK_MAX_OUTPUT_TOKENS")
        if self.input_usd_per_mtok is None or self.input_usd_per_mtok <= 0:
            errors.append("AEOS_AI_FEEDBACK_INPUT_USD_PER_MTOK")
        if self.output_usd_per_mtok is None or self.output_usd_per_mtok <= 0:
            errors.append("AEOS_AI_FEEDBACK_OUTPUT_USD_PER_MTOK")
        for name, value in (
            ("AEOS_AI_FEEDBACK_USER_HOURLY_REQUESTS", self.user_hourly_requests),
            ("AEOS_AI_FEEDBACK_ORG_DAILY_REQUESTS", self.org_daily_requests),
            ("AEOS_AI_FEEDBACK_USER_DAILY_COST_MICROUSD", self.user_daily_cost_microusd),
            ("AEOS_AI_FEEDBACK_ORG_DAILY_COST_MICROUSD", self.org_daily_cost_microusd),
            ("AEOS_AI_FEEDBACK_MODEL_CHECK_TTL_SECONDS", self.model_check_ttl_seconds),
        ):
            if value < 1:
                errors.append(name)
        return errors

    def limits(self) -> dict:
        return {
            "user_hourly_requests": self.user_hourly_requests,
            "org_daily_requests": self.org_daily_requests,
            "user_daily_cost_microusd": self.user_daily_cost_microusd,
            "org_daily_cost_microusd": self.org_daily_cost_microusd,
        }


def load_ai_feedback_settings() -> AiFeedbackSettings:
    return AiFeedbackSettings(
        enabled=_bool("AEOS_AI_FEEDBACK_ENABLED"),
        provider=os.getenv("AEOS_AI_FEEDBACK_PROVIDER", "anthropic").strip(),
        model_id=os.getenv("AEOS_AI_FEEDBACK_MODEL", "").strip(),
        api_key=os.getenv("AEOS_AI_FEEDBACK_API_KEY", "").strip(),
        base_url=os.getenv("AEOS_AI_FEEDBACK_BASE_URL", "https://api.anthropic.com").strip(),
        timeout_seconds=_float("AEOS_AI_FEEDBACK_TIMEOUT_SECONDS", 30.0),
        max_retries=_int("AEOS_AI_FEEDBACK_MAX_RETRIES", 2),
        max_output_tokens=_int("AEOS_AI_FEEDBACK_MAX_OUTPUT_TOKENS", 4096),
        input_usd_per_mtok=_decimal("AEOS_AI_FEEDBACK_INPUT_USD_PER_MTOK"),
        output_usd_per_mtok=_decimal("AEOS_AI_FEEDBACK_OUTPUT_USD_PER_MTOK"),
        organization_allowlist=_set("AEOS_AI_FEEDBACK_ORG_ALLOWLIST"),
        approved_rubrics=_set("AEOS_AI_FEEDBACK_APPROVED_RUBRICS"),
        user_hourly_requests=_int("AEOS_AI_FEEDBACK_USER_HOURLY_REQUESTS", 10),
        org_daily_requests=_int("AEOS_AI_FEEDBACK_ORG_DAILY_REQUESTS", 100),
        user_daily_cost_microusd=_int("AEOS_AI_FEEDBACK_USER_DAILY_COST_MICROUSD", 1_000_000),
        org_daily_cost_microusd=_int("AEOS_AI_FEEDBACK_ORG_DAILY_COST_MICROUSD", 5_000_000),
        model_check_ttl_seconds=_int("AEOS_AI_FEEDBACK_MODEL_CHECK_TTL_SECONDS", 600),
    )


def get_ai_feedback_settings() -> AiFeedbackSettings:
    """FastAPI dependency. Read per request so a flag change needs no redeploy
    of code, and so tests can override it."""
    return load_ai_feedback_settings()
