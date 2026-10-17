"""Server-mediated provider adapter for feedback drafting.

Only the backend calls the provider. The browser never receives the key, the
model name or the provider endpoint.

Safety properties:
  * The API key and base URL are passed explicitly, so ambient environment
    credentials or base-URL overrides are never consulted.
  * The configured model is checked against the provider's live model list
    before use, including whether it supports structured output and the
    configured output size. Nothing falls back to another model.
  * Each call has a bounded timeout and a bounded number of SDK retries
    (connection errors, 408, 409, 429 and 5xx only).
  * Errors are mapped to fixed codes. Provider messages, which may echo
    request content, are never returned to clients or written to logs.
"""

import logging
import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional, Protocol, Tuple

from app.core.ai_feedback_settings import AiFeedbackSettings

logger = logging.getLogger("aeos.ai_feedback.provider")


class ProviderError(Exception):
    """Base error. ``code`` is safe to return; nothing else is."""

    code = "provider_error"
    http_status = 502

    def __init__(self, code: Optional[str] = None):
        super().__init__(code or self.code)
        if code:
            self.code = code


class ProviderUnavailable(ProviderError):
    code = "provider_unavailable"
    http_status = 503


class ProviderMisconfigured(ProviderError):
    code = "provider_misconfigured"
    http_status = 503


class ModelUnavailable(ProviderError):
    code = "model_unavailable"
    http_status = 503


class ProviderRefused(ProviderError):
    code = "provider_refused"
    http_status = 502


@dataclass(frozen=True)
class ProviderCompletion:
    text: Optional[str]
    response_model_id: Optional[str]
    stop_reason: Optional[str]
    input_tokens: int
    output_tokens: int


class FeedbackProvider(Protocol):
    name: str

    def check_model(self, model_id: str, required_output_tokens: int) -> None: ...

    def complete(
        self,
        *,
        model_id: str,
        system: str,
        user_content: str,
        output_schema: dict,
        max_output_tokens: int,
    ) -> ProviderCompletion: ...


# Successful model checks are cached for the configured TTL; failures for a
# short time, so an outage is rechecked soon without a check on every request.
_FAILURE_CACHE_SECONDS = 30
_model_check_cache: Dict[Tuple[str, str, str, int], Tuple[float, Optional[ProviderError]]] = {}
_model_check_lock = threading.Lock()


def reset_model_check_cache() -> None:
    with _model_check_lock:
        _model_check_cache.clear()


def checked_model(provider: FeedbackProvider, settings: AiFeedbackSettings) -> None:
    key = (provider.name, settings.base_url, settings.model_id, settings.max_output_tokens)
    now = time.monotonic()
    with _model_check_lock:
        cached = _model_check_cache.get(key)
    if cached and cached[0] > now:
        if cached[1] is not None:
            raise cached[1]
        return
    try:
        provider.check_model(settings.model_id, settings.max_output_tokens)
    except ProviderError as exc:
        with _model_check_lock:
            _model_check_cache[key] = (now + _FAILURE_CACHE_SECONDS, exc)
        raise
    with _model_check_lock:
        _model_check_cache[key] = (now + settings.model_check_ttl_seconds, None)


def _capability_supported(capabilities, name: str) -> bool:
    if not isinstance(capabilities, dict):
        return False
    entry = capabilities.get(name)
    return isinstance(entry, dict) and entry.get("supported") is True


class AnthropicFeedbackProvider:
    name = "anthropic"

    def __init__(self, settings: AiFeedbackSettings, client=None):
        if client is None:
            import anthropic

            client = anthropic.Anthropic(
                api_key=settings.api_key,
                base_url=settings.base_url,
                timeout=settings.timeout_seconds,
                max_retries=settings.max_retries,
            )
        self._client = client

    def _map_error(self, exc: Exception, operation: str) -> ProviderError:
        import anthropic

        # Log the class and request id only; the message may echo input.
        request_id = getattr(exc, "request_id", None)
        logger.warning(
            "ai_feedback provider %s failed: %s request_id=%s",
            operation,
            type(exc).__name__,
            request_id,
        )
        if isinstance(exc, anthropic.APITimeoutError):
            return ProviderUnavailable("provider_timeout")
        if isinstance(exc, anthropic.APIConnectionError):
            return ProviderUnavailable()
        if isinstance(exc, anthropic.RateLimitError):
            return ProviderUnavailable("provider_rate_limited")
        if isinstance(exc, (anthropic.AuthenticationError, anthropic.PermissionDeniedError)):
            return ProviderMisconfigured()
        if isinstance(exc, anthropic.NotFoundError):
            return ModelUnavailable()
        if isinstance(exc, anthropic.APIStatusError):
            if exc.status_code >= 500:
                return ProviderUnavailable()
            return ProviderError("provider_rejected_request")
        return ProviderError()

    def check_model(self, model_id: str, required_output_tokens: int) -> None:
        try:
            info = self._client.models.retrieve(model_id)
        except Exception as exc:  # noqa: BLE001 - mapped to a sanitized code
            raise self._map_error(exc, "model_check") from None
        if getattr(info, "id", None) != model_id:
            raise ModelUnavailable()
        if not _capability_supported(getattr(info, "capabilities", None), "structured_outputs"):
            raise ModelUnavailable("model_unsupported")
        max_tokens = getattr(info, "max_tokens", None)
        if isinstance(max_tokens, int) and max_tokens < required_output_tokens:
            raise ProviderMisconfigured()

    def complete(
        self,
        *,
        model_id: str,
        system: str,
        user_content: str,
        output_schema: dict,
        max_output_tokens: int,
    ) -> ProviderCompletion:
        try:
            response = self._client.messages.create(
                model=model_id,
                max_tokens=max_output_tokens,
                system=system,
                messages=[{"role": "user", "content": user_content}],
                output_config={"format": {"type": "json_schema", "schema": output_schema}},
            )
        except Exception as exc:  # noqa: BLE001 - mapped to a sanitized code
            raise self._map_error(exc, "messages") from None

        usage = getattr(response, "usage", None)
        input_tokens = int(getattr(usage, "input_tokens", 0) or 0)
        input_tokens += int(getattr(usage, "cache_creation_input_tokens", 0) or 0)
        input_tokens += int(getattr(usage, "cache_read_input_tokens", 0) or 0)
        text = None
        for block in getattr(response, "content", None) or []:
            if getattr(block, "type", None) == "text":
                text = block.text
                break
        return ProviderCompletion(
            text=text,
            response_model_id=getattr(response, "model", None),
            stop_reason=getattr(response, "stop_reason", None),
            input_tokens=input_tokens,
            output_tokens=int(getattr(usage, "output_tokens", 0) or 0),
        )


def get_feedback_provider_factory():
    """FastAPI dependency returning a factory, so tests inject a fake provider
    and no client is constructed while the feature is disabled."""
    return AnthropicFeedbackProvider
