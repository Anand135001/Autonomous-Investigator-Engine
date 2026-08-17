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


def hypothesis_test_accpets_vaild_confidence() -> None:
    hypothesis = hypothesis(
        hypothesis_id="H1",
        description="just testing hypothesis",
        confidence=0.31
    )
    assert hypothesis.confidence == 0.31



def investigation_test_starts_pending() -> None:
    investigation = Investigation(
        investigation_id="INV-922",
        problem="investigation acccuracy drop"
    )
    assert investigation.status == InvestigationStatus.PENDING
    assert investigation.hypotheses == []
    assert investigation.evidence == []
    assert investigation.experiments == []
    assert investigation.results == []



def experiment_test_as_pending() -> None:
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



def experiment_test_result__stored_observations() -> None:
    result = ExperimentResult(
        experiment_id="EXP-001",
        status=ExperimentStatus.SUCCEEDED,
        observations=[
            "Normalization code changed.",
        ],
    )
    assert result.status == ExperimentStatus.SUCCEEDED
    assert len(result.observations) == 1