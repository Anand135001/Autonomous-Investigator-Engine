import pytest

from investigator.domain.models import ExperimentContract
from investigator.execution.validator import ExperimentValidator


@pytest.fixture
def validator() -> ExperimentValidator:
    return ExperimentValidator()


def make_contract(**overrides) -> ExperimentContract:

    values = {
        "experiment_id": "EXP-001",
        "purpose": "Inspect source changes",
        "target_hypothesis_id": "H1",
        "rationale": "Test",
        "allowed_tools": ["git"],
        "timeout_seconds": 30,
        "estimated_cost": 1.0,
        "risk_level": "low",
    }

    values.update(overrides)

    return ExperimentContract(**values)


def test_valid_contract_is_accepted(validator: ExperimentValidator) -> None:
    contract = make_contract()

    validator.validate(contract)


def test_unknown_tool_is_rejected(validator: ExperimentValidator) -> None:
    contract = make_contract(allowed_tools=["delete_database"])

    with pytest.raises(ValueError):
        validator.validate(contract)


def test_timeout_above_limit_is_rejected(validator: ExperimentValidator) -> None:
    contract = make_contract(timeout_seconds=301)

    with pytest.raises(ValueError):
        validator.validate(contract)


def test_negative_timeout_is_rejected(validator: ExperimentValidator) -> None:
    contract = make_contract(timeout_seconds=-1)

    with pytest.raises(ValueError):
        validator.validate(contract)


def test_cost_above_limit_is_rejected(validator: ExperimentValidator) -> None:
    contract = make_contract(estimated_cost=11.0)

    with pytest.raises(ValueError):
        validator.validate(contract)


def test_unknown_risk_level_is_rejected(validator: ExperimentValidator) -> None:
    contract = make_contract(risk_level="critical")

    with pytest.raises(ValueError):
        validator.validate(contract)