from pydantic import BaseModel, Field, field_validator


class ProposedExperiment(BaseModel):
    """One experiment proposed by Gemini."""

    experiment_id: str = Field(description="Unique identifier for this proposed experiment.")

    purpose: str = Field(description="What this experiment is trying to determine.")

    target_hypothesis_ids: list[str] = Field(description="Hypotheses this experiment is intended to test.")

    rationale: str = Field(description="Why this experiment is useful given the current evidence.")

    expected_information_gain: float = Field(description=("Expected information gain from 0.0 to 1.0."))

    hypothesis_coverage: float = Field(
        description=(
            "Fraction of relevant hypotheses this experiment can distinguish, "
            "from 0.0 to 1.0."
        )
    )

    estimated_cost: float = Field(description="Relative execution cost. Must be non-negative.")

    risk_level: str = Field(description="Expected execution risk: low, medium, or high.")

    timeout_seconds: int = Field(description="Maximum expected execution time.")

    allowed_tools: list[str] = Field(description="Tools required to perform this experiment.")


    @field_validator("expected_information_gain")
    @classmethod
    def validate_information_gain(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("expected_information_gain must be between 0.0 and 1.0")

        return value


    @field_validator("hypothesis_coverage")
    @classmethod
    def validate_hypothesis_coverage(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("hypothesis_coverage must be between 0.0 and 1.0")

        return value


    @field_validator("estimated_cost")
    @classmethod
    def validate_cost(cls, value: float) -> float:
        if value < 0:
            raise ValueError("estimated_cost cannot be negative")

        return value


    @field_validator("risk_level")
    @classmethod
    def validate_risk(cls, value: str) -> str:
        if value not in {"low", "medium", "high"}:
            raise ValueError("risk_level must be low, medium, or high")

        return value


    @field_validator("timeout_seconds")
    @classmethod
    def validate_timeout(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("timeout_seconds must be greater than zero")

        return value

class ExperimentProposal(BaseModel):
    """Structured set of experiments proposed by Gemini."""

    candidates: list[ProposedExperiment]