import pytest
from pydantic import ValidationError

from investigator.reasoning.schemas import (
    ExperimentProposal,
    ProposedExperiment,
)


def make_experiment(**overrides) -> dict:
    values = {
        "experiment_id": "EXP-001",
        "purpose": "Inspect recent source changes.",
        "target_hypothesis_ids": ["H1"],
        "rationale": "Recent changes may explain the regression.",
        "expected_information_gain": 0.8,
        "hypothesis_coverage": 0.9,
        "estimated_cost": 1.0,
        "risk_level": "low",
        "timeout_seconds": 30,
        "allowed_tools": ["git"],
    }

    values.update(overrides)
    return values


def test_valid_proposed_experiment() -> None:
    experiment = ProposedExperiment(
        **make_experiment()
    )

    assert experiment.experiment_id == "EXP-001"


def test_invalid_information_gain_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ProposedExperiment(
            **make_experiment(
                expected_information_gain=1.5
            )
        )


def test_invalid_risk_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ProposedExperiment(
            **make_experiment(
                risk_level="critical"
            )
        )


def test_proposal_contains_candidates() -> None:
    proposal = ExperimentProposal(
        candidates=[
            ProposedExperiment(
                **make_experiment()
            )
        ]
    )

    assert len(proposal.candidates) == 1