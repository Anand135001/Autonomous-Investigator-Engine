import pytest
from pydantic import ValidationError

from investigator.reasoning.result_schema import (
    HypothesisAssessment,
    ResultAssessment,
)


def test_valid_hypothesis_assessment() -> None:
    assessment = HypothesisAssessment(
        hypothesis_id="H1",
        new_confidence=0.82,
        evidence_effect="strongly supports",
    )

    assert assessment.hypothesis_id == "H1"
    assert assessment.new_confidence == 0.82


def test_invalid_confidence_is_rejected() -> None:
    with pytest.raises(ValidationError):
        HypothesisAssessment(
            hypothesis_id="H1",
            new_confidence=1.5,
            evidence_effect="supports",
        )


def test_valid_result_assessment() -> None:
    result = ResultAssessment(
        summary="The preprocessing distributions differ.",
        assessments=[
            HypothesisAssessment(
                hypothesis_id="H1",
                new_confidence=0.82,
                evidence_effect="strongly supports",
            )
        ],
        should_continue=True,
        recommended_next_focus="direct reproduction",
        verification_sufficient=False,
    )

    assert result.should_continue is True
    assert len(result.assessments) == 1