import pytest


from investigator.domain.models import (
    Evidence,
    Experiment,
    ExperimentResult,
    ExperimentStatus,
    Hypothesis,
    Investigation,
    InvestigationStatus,
    ExperimentCandidate,
    ExperimentContract,
    ExperimentCapability
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
        observations=[
            "Normalization code changed.",
        ],
    )
    assert result.status == ExperimentStatus.SUCCEEDED
    assert len(result.observations) == 1



def test_experiment_candidate_accepts_valid_values() -> None:
    candidate = ExperimentCandidate(
        experiment_id="EXP-001",
        purpose="Inspect recent preprocessing changes",
        target_hypothesis_ids=["H1", "H5"],
        rationale="Recent code changes may explain the regression.",
        expected_information_gain=0.8,
        hypothesis_coverage=0.7,
        estimated_cost=1.0,
        risk_level="low",
        timeout_seconds=60,
    )

    assert candidate.expected_information_gain == 0.8
    assert candidate.hypothesis_coverage == 0.7


def test_experiment_candidate_rejects_invalid_information_gain() -> None:
    with pytest.raises(ValueError):
        ExperimentCandidate(
            experiment_id="EXP-001",
            purpose="Test",
            target_hypothesis_ids=["H1"],
            rationale="Test",
            expected_information_gain=1.5,
            hypothesis_coverage=0.5,
            estimated_cost=1.0,
            risk_level="low",
            timeout_seconds=60,
        )


def test_experiment_contract_accepts_valid_values() -> None:
    contract = ExperimentContract(
        experiment_id="EXP-001",
        purpose="Inspect recent source changes",
        target_hypothesis_id="H1",
        rationale="Recent changes may explain the regression.",
        allowed_tools=["git"],
        timeout_seconds=30,
        estimated_cost=1.0,
        risk_level="low",
    )

    assert contract.experiment_id == "EXP-001"
    assert contract.allowed_tools == ["git"]


def test_experiment_contract_stores_expected_outputs() -> None:
    contract = ExperimentContract(
        experiment_id="EXP-001",
        purpose="Inspect recent source changes",
        target_hypothesis_id="H1",
        rationale="Test recent code changes.",
        allowed_tools=["git"],
        timeout_seconds=30,
        estimated_cost=1.0,
        risk_level="low",
        expected_outputs=["diff_stat"],
        )

    assert contract.expected_outputs == ["diff_stat"]


def test_experiment_capability_accepts_valid_values() -> None:
    capability = ExperimentCapability(
        capability_id="EXP-GIT-DIFF",
        name="Git revision comparison",
        description=(
            "Compare the latest two Git revisions."
        ),
        target_hypothesis_types=[
            "preprocessing",
            "model_implementation",
        ],
        allowed_tools=["git"],
        risk_level="low",
        timeout_seconds=30,
        estimated_cost=1.0,
        expected_outputs=["diff_stat"],
    )

    assert capability.capability_id == "EXP-GIT-DIFF"
    assert capability.allowed_tools == ["git"]


def test_experiment_capability_rejects_invalid_risk() -> None:
    with pytest.raises(ValueError):
        ExperimentCapability(
            capability_id="EXP-001",
            name="Invalid",
            description="Invalid capability.",
            target_hypothesis_types=["H1"],
            allowed_tools=["git"],
            risk_level="critical",
            timeout_seconds=30,
            estimated_cost=1.0,
        )