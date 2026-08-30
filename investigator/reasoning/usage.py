from dataclasses import dataclass


@dataclass(frozen=True)
class ModelUsage:
    """Token usage from one Gemini request."""

    operation: str
    input_tokens: int
    output_tokens: int
    thoughts_tokens: int
    total_tokens: int