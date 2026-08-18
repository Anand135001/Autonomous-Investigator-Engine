import pytest


from investigator.domain.models import (
    Evidence,
    Experiment,
    ExperimentResult,
    ExperimentStatus,
    Hypothesis,
    Investigation,
    InvestigationStatus,
)


def test_hypothesis_accpets_vaild_confidence() -> None:
    hypothesis = Hypothesis(
        hypothesis_id="H1",
        description="just testing hypothesis",
        confidence=0.31
    )
    assert hypothesis.confidence == 0.31


def test_hypothesis_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError):
        Hypothesis(
            hypothesis_id="H1",
            description="Invalid hypothesis",
            confidence=1.5,
        )


def test_investigation_starts_pending() -> None:
    investigation = Investigation(
        investigation_id="INV-922",
        problem="investigation acccuracy drop"
    )
    assert investigation.status == InvestigationStatus.PENDING
    assert investigation.hypotheses == []
    assert investigation.evidence == []
    assert investigation.experiments == []
    assert investigation.results == []



def test_experiment_as_pending() -> None:
    experiment = Experiment(
        experiment_id="EXP-001",
        purpose="Inspect recent preprocessing changes",
        target_hypothesis_id="H1",
        rationale="Recent code changes may explain the regression.",
        estimated_cost=1.0,
        timeout_seconds=60,
        risk_level="low",
    )
    assert experiment.status == ExperimentStatus.PENDING


def test_experiment_result_stored_observations() -> None:
    result = ExperimentResult(
        experiment_id="EXP-001",
        status=ExperimentStatus.SUCCEEDED,
        observation=[
            "Normalization code changed.",
        ],
    )
    assert result.status == ExperimentStatus.SUCCEEDED
    assert len(result.observation) == 1



