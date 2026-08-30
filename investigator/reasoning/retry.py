import time

from google.genai import errors


RETRYABLE_STATUS_CODES = {
    500,
    503,
}


def generate_with_retry(
    generate_function,
    max_attempts: int = 4,
    initial_delay: float = 2.0,
):
    """
    Execute a Gemini request with exponential backoff.

    Retries transient API failures such as 429, 500 and 503.
    """

    for attempt in range(max_attempts):
        try:
            return generate_function()

        except errors.APIError as exc:

            if exc.code not in RETRYABLE_STATUS_CODES:
                raise

            if attempt == max_attempts - 1:
                raise

            delay = initial_delay * (
                2 ** attempt
            )

            print(
                f"Gemini request failed with "
                f"{exc.code}. "
                f"Retrying in {delay:.1f}s..."
            )

            time.sleep(delay)

    raise RuntimeError(
        "Gemini request failed after retries."
    )