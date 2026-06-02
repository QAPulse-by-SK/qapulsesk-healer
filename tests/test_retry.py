"""Tests for the retry / transient-error helpers in `llm.base`."""

from __future__ import annotations

import pytest

from qapulsesk_healer.llm.base import _is_transient, _with_retry


class _FakeAPIError(Exception):
    def __init__(self, status_code: int, message: str = "") -> None:
        super().__init__(message or f"{status_code} error")
        self.status_code = status_code


class TestIsTransient:
    @pytest.mark.parametrize("code", [429, 500, 502, 503, 504])
    def test_status_code_attribute_marks_transient(self, code: int) -> None:
        assert _is_transient(_FakeAPIError(code)) is True

    @pytest.mark.parametrize("code", [400, 401, 403, 404, 422])
    def test_client_errors_are_not_transient(self, code: int) -> None:
        assert _is_transient(_FakeAPIError(code)) is False

    def test_503_in_message_marks_transient(self) -> None:
        assert _is_transient(Exception("Server returned 503 Service Unavailable")) is True

    def test_overloaded_in_message_marks_transient(self) -> None:
        assert _is_transient(Exception("Model is currently overloaded")) is True

    def test_unrelated_error_is_not_transient(self) -> None:
        assert _is_transient(ValueError("bad input")) is False


class TestWithRetry:
    def test_returns_immediately_on_success(self) -> None:
        calls = []

        def fn() -> str:
            calls.append(1)
            return "ok"

        result = _with_retry(fn, sleep=lambda _s: None)

        assert result == "ok"
        assert len(calls) == 1

    def test_retries_then_succeeds(self) -> None:
        attempts: list[int] = []

        def fn() -> str:
            attempts.append(1)
            if len(attempts) < 3:
                raise _FakeAPIError(503)
            return "ok"

        result = _with_retry(fn, attempts=5, sleep=lambda _s: None)

        assert result == "ok"
        assert len(attempts) == 3

    def test_reraises_after_exhausting_attempts(self) -> None:
        def fn() -> str:
            raise _FakeAPIError(503, "still down")

        with pytest.raises(_FakeAPIError) as exc_info:
            _with_retry(fn, attempts=3, sleep=lambda _s: None)

        assert exc_info.value.status_code == 503

    def test_does_not_retry_on_non_transient_error(self) -> None:
        attempts: list[int] = []

        def fn() -> str:
            attempts.append(1)
            raise _FakeAPIError(400, "bad request")

        with pytest.raises(_FakeAPIError):
            _with_retry(fn, attempts=5, sleep=lambda _s: None)

        assert len(attempts) == 1, "Client errors must not be retried"

    def test_exponential_backoff_delay_sequence(self) -> None:
        delays: list[float] = []

        def always_503() -> str:
            raise _FakeAPIError(503)

        with pytest.raises(_FakeAPIError):
            _with_retry(
                always_503,
                attempts=4,
                initial_delay=1.0,
                sleep=delays.append,
            )

        # 4 attempts → 3 sleeps between them, doubling each time
        assert delays == [1.0, 2.0, 4.0]
