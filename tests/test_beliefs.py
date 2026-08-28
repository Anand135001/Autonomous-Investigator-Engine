import pytest

from investigator.domain.models import Hypothesis, Investigation
from investigator.investigation.beliefs import BeliefUpdater
from investigator.investigation.manager import InvestigationManager
from investigator.reasoning.result_schema import HypothesisAssessment, ResultAssessment


def make_investigation() -> Investigation:
    return Investigation(
        investigation_id="INV-001",
        problem="Something failed.",
        hypotheses=[
            Hypothesis(
                hypothesis_id="H1",
                description="Cause A",
                confidence=0.50,
            ),
            Hypothesis(
                hypothesis_id="H2",
                description="Cause B",
                confidence=0.30,
            ),
            Hypothesis(
                hypothesis_id="H3",
                description="Cause C",
                confidence=0.20,
            ),
        ],
    )


def test_belief_update_normalizes_confidence() -> None:
    manager = InvestigationManager()

    investigation = make_investigation()

    assessment = ResultAssessment(
        summary="Evidence strongly supports H1.",
        assessments=[
            HypothesisAssessment(
                hypothesis_id="H1",
                new_confidence=0.8,
                evidence_effect="strongly supports",
            ),
            HypothesisAssessment(
                hypothesis_id="H2",
                new_confidence=0.1,
                evidence_effect="weakens",
            ),
            HypothesisAssessment(
                hypothesis_id="H3",
                new_confidence=0.1,
                evidence_effect="neutral",
            ),
        ],
        should_continue=True,
        recommended_next_focus="H1 verification",
        verification_sufficient=False,
    )

    updater = BeliefUpdater()

    updater.update(
        manager,
        investigation,
        assessment,
    )

    total = sum(
        hypothesis.confidence
        for hypothesis in investigation.hypotheses
    )

    assert total == pytest.approx(1.0)

    h1 = next(
        h
        for h in investigation.hypotheses
        if h.hypothesis_id == "H1"
    )

    assert h1.confidence == pytest.approx(
        0.8
    )


def test_missing_hypothesis_assessment_is_rejected() -> None:
    manager = InvestigationManager()

    investigation = make_investigation()

    assessment = ResultAssessment(
        summary="Incomplete assessment.",
        assessments=[
            HypothesisAssessment(
                hypothesis_id="H1",
                new_confidence=1.0,
                evidence_effect="supports",
            )
        ],
        should_continue=True,
        recommended_next_focus="unknown",
        verification_sufficient=False,
    )

    updater = BeliefUpdater()

    with pytest.raises(ValueError):
        updater.update(
            manager,
            investigation,
            assessment,
        )