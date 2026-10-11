"""Provider adapter: error sanitization, model checks and response handling.

Uses the SDK's real exception classes against a stub client. No network.
Every response object here is a DETERMINISTIC FIXTURE, not model output.
"""

import logging
from types import SimpleNamespace

import anthropic
import httpx2
import pytest

from app.services.ai_feedback.provider import (
    AnthropicFeedbackProvider,
    ModelUnavailable,
    ProviderError,
    ProviderMisconfigured,
    ProviderUnavailable,
)
from tests.test_ai_feedback import settings

SECRET_ECHO = "student wrote: my secret synthetic sentence"
REQUEST = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")


def status_error(cls, code):
    response = httpx2.Response(code, request=REQUEST, headers={"request-id": "req_synthetic"})
    return cls(SECRET_ECHO, response=response, body={"error": {"message": SECRET_ECHO}})


class StubMessages:
    def __init__(self, outcome):
        self.outcome = outcome
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


class StubModels:
    def __init__(self, outcome):
        self.outcome = outcome

    def retrieve(self, model_id):
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


def adapter(messages=None, models=None):
    client = SimpleNamespace(messages=StubMessages(messages), models=StubModels(models))
    return AnthropicFeedbackProvider(settings(), client=client), client


def complete(provider):
    return provider.complete(
        model_id="configured-model-under-test",
        system="server instructions",
        user_content="data",
        output_schema={"type": "object"},
        max_output_tokens=1024,
    )


@pytest.mark.parametrize(
    ("exc", "expected_type", "code"),
    [
        (anthropic.APITimeoutError(request=REQUEST), ProviderUnavailable, "provider_timeout"),
        (anthropic.APIConnectionError(message=SECRET_ECHO, request=REQUEST), ProviderUnavailable, "provider_unavailable"),
        (status_error(anthropic.RateLimitError, 429), ProviderUnavailable, "provider_rate_limited"),
        (status_error(anthropic.InternalServerError, 500), ProviderUnavailable, "provider_unavailable"),
        (status_error(anthropic.APIStatusError, 529), ProviderUnavailable, "provider_unavailable"),
        (status_error(anthropic.AuthenticationError, 401), ProviderMisconfigured, "provider_misconfigured"),
        (status_error(anthropic.PermissionDeniedError, 403), ProviderMisconfigured, "provider_misconfigured"),
        (status_error(anthropic.NotFoundError, 404), ModelUnavailable, "model_unavailable"),
        (status_error(anthropic.BadRequestError, 400), ProviderError, "provider_rejected_request"),
        (RuntimeError(SECRET_ECHO), ProviderError, "provider_error"),
    ],
)
def test_provider_errors_map_to_fixed_codes_without_echoing_content(exc, expected_type, code, caplog):
    provider, _ = adapter(messages=exc)
    with caplog.at_level(logging.WARNING, logger="aeos.ai_feedback.provider"):
        with pytest.raises(expected_type) as raised:
            complete(provider)

    assert raised.value.code == code
    assert SECRET_ECHO not in str(raised.value)
    assert raised.value.__cause__ is None and raised.value.__suppress_context__
    assert SECRET_ECHO not in caplog.text


def response(stop_reason="end_turn", text='{"ok": true}'):
    blocks = [SimpleNamespace(type="thinking", thinking="")]
    if text is not None:
        blocks.append(SimpleNamespace(type="text", text=text))
    return SimpleNamespace(
        content=blocks,
        model="configured-model-under-test",
        stop_reason=stop_reason,
        usage=SimpleNamespace(input_tokens=100, output_tokens=50,
                              cache_creation_input_tokens=0, cache_read_input_tokens=7),
    )


def test_completion_sends_server_instructions_and_structured_output_schema():
    provider, client = adapter(messages=response())
    result = complete(provider)

    sent = client.messages.kwargs
    assert sent["system"] == "server instructions"
    assert sent["messages"] == [{"role": "user", "content": "data"}]
    assert sent["output_config"] == {"format": {"type": "json_schema", "schema": {"type": "object"}}}
    assert sent["model"] == "configured-model-under-test" and sent["max_tokens"] == 1024
    assert "temperature" not in sent and "thinking" not in sent
    assert result.text == '{"ok": true}'
    assert (result.input_tokens, result.output_tokens) == (107, 50)


@pytest.mark.parametrize("stop_reason", ["refusal", "max_tokens"])
def test_stop_reason_is_reported_for_the_service_to_handle(stop_reason):
    provider, _ = adapter(messages=response(stop_reason=stop_reason))
    assert complete(provider).stop_reason == stop_reason


def model_info(model_id="configured-model-under-test", structured=True, max_tokens=128000):
    return SimpleNamespace(
        id=model_id,
        max_tokens=max_tokens,
        capabilities={"structured_outputs": {"supported": structured}},
    )


def test_model_check_accepts_an_available_model_with_structured_output():
    provider, _ = adapter(models=model_info())
    provider.check_model("configured-model-under-test", 4096)


@pytest.mark.parametrize(
    ("info", "expected", "code"),
    [
        (status_error(anthropic.NotFoundError, 404), ModelUnavailable, "model_unavailable"),
        (model_info(model_id="some-other-model"), ModelUnavailable, "model_unavailable"),
        (model_info(structured=False), ModelUnavailable, "model_unsupported"),
        (SimpleNamespace(id="configured-model-under-test", max_tokens=128000, capabilities=None), ModelUnavailable, "model_unsupported"),
        (model_info(max_tokens=1000), ProviderMisconfigured, "provider_misconfigured"),
        (anthropic.APIConnectionError(message="down", request=REQUEST), ProviderUnavailable, "provider_unavailable"),
    ],
)
def test_model_check_fails_closed(info, expected, code):
    provider, _ = adapter(models=info)
    with pytest.raises(expected) as raised:
        provider.check_model("configured-model-under-test", 4096)
    assert raised.value.code == code
