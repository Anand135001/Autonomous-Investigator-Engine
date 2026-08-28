from pydantic import BaseModel, Field, field_validator


class HypothesisAssessment(BaseModel):
    """Gemini's assessment of one hypothesis."""

    hypothesis_id: str = Field(description="ID of the hypothesis being assessed.")

    new_confidence: float = Field(description="Updated confidence from 0.0 to 1.0.")

    evidence_effect: str = Field(
        description=(
            "Explain whether the result supports, "
            "weakens, or is neutral toward this hypothesis."
        )
    )

    @field_validator("new_confidence")
    @classmethod
    def validate_confidence(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("new_confidence must be between 0.0 and 1.0")

        return value


class ResultAssessment(BaseModel):
    """Structured interpretation of an experiment result."""

    summary: str = Field(description="Concise interpretation of the experiment result.")

    assessments: list[HypothesisAssessment]

    should_continue: bool = Field(description=("Whether additional investigation is needed."))

    recommended_next_focus: str = Field(description=("What uncertainty should receive attention next."))

    verification_sufficient: bool = Field(
        description=(
            "Whether the evidence is sufficient to consider "
            "the current leading hypothesis verified."
        )
    )