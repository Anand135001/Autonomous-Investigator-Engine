from google.genai import errors

from investigator.reasoning.retry import (
    generate_with_retry,
)


def test_successful_request_is_not_retried() -> None:

    calls = 0

    def generate():
        nonlocal calls
        calls += 1
        return "success"

    result = generate_with_retry(
        generate,
    )

    assert result == "success"
    assert calls == 1


def test_503_is_retried(monkeypatch) -> None:

    calls = 0

    def generate():
        nonlocal calls
        calls += 1

        if calls < 3:
            raise errors.ServerError(
                503,
                {
                    "error": {
                        "code": 503,
                        "message": "temporary",
                        "status": "UNAVAILABLE",
                    }
                },
            )

        return "success"

    monkeypatch.setattr(
        "time.sleep",
        lambda _: None,
    )

    result = generate_with_retry(
        generate,
    )

    assert result == "success"
    assert calls == 3


def test_503_failure_after_max_attempts(
    monkeypatch,
) -> None:

    calls = 0

    def generate():
        nonlocal calls
        calls += 1

        raise errors.ServerError(
            503,
            {
                "error": {
                    "code": 503,
                    "message": "temporary",
                    "status": "UNAVAILABLE",
                }
            },
        )

    monkeypatch.setattr(
        "time.sleep",
        lambda _: None,
    )

    try:
        generate_with_retry(
            generate,
            max_attempts=3,
        )
    except errors.ServerError:
        pass
    else:
        raise AssertionError(
            "Expected ServerError"
        )

    assert calls == 3