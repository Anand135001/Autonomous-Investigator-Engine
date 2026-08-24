from investigator.domain.models import ExperimentCandidate
from investigator.execution.contracts import (
    candidate_to_contract,
    contract_to_experiment,
)


def test_candidate_to_contract() -> None:
    candidate = ExperimentCandidate(
        experiment_id="EXP-001",
        purpose="Inspect source changes",
        target_hypothesis_ids=["H1"],
        rationale="Recent changes may explain the regression.",
        expected_information_gain=0.8,
        hypothesis_coverage=0.9,
        estimated_cost=1.0,
        risk_level="low",
        timeout_seconds=30,
        allowed_tools=["git"],
    )

    contract = candidate_to_contract(candidate)

    assert contract.experiment_id == "EXP-001"
    assert contract.target_hypothesis_id == "H1"
    assert contract.allowed_tools == ["git"]


def test_contract_to_experiment() -> None:
    from investigator.domain.models import ExperimentContract

    contract = ExperimentContract(
        experiment_id="EXP-001",
        purpose="Inspect source changes",
        target_hypothesis_id="H1",
        rationale="Test",
        allowed_tools=["git"],
        timeout_seconds=30,
        estimated_cost=1.0,
        risk_level="low",
    )

    experiment = contract_to_experiment(contract)

    assert experiment.experiment_id == "EXP-001"
    assert experiment.target_hypothesis_id == "H1"