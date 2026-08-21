import pytest

from investigator.domain.models import ExperimentCandidate
from investigator.planning.planner import ExperimentPlanner


@pytest.fixture
def planner() -> ExperimentPlanner:
    return ExperimentPlanner()


def make_candidate(
    experiment_id: str,
    information_gain: float,
    coverage: float,
    cost: float,
    risk: str = "low",
) -> ExperimentCandidate:
    return ExperimentCandidate(
        experiment_id=experiment_id,
        purpose=f"Test {experiment_id}",
        target_hypothesis_ids=["H1"],
        rationale="Test candidate.",
        expected_information_gain=information_gain,
        hypothesis_coverage=coverage,
        estimated_cost=cost,
        risk_level=risk,
        timeout_seconds=60,
    )


def test_score_prefers_high_information_low_cost( planner: ExperimentPlanner,) -> None:
    cheap = make_candidate(
        "EXP-001",
        information_gain=0.8,
        coverage=0.9,
        cost=1.0,
    )

    expensive = make_candidate(
        "EXP-002",
        information_gain=0.95,
        coverage=0.95,
        cost=5.0,
    )

    assert planner.score(cheap) > planner.score(expensive)


def test_select_next_experiment(planner: ExperimentPlanner,) -> None:
    first = make_candidate(
        "EXP-001",
        information_gain=0.5,
        coverage=0.5,
        cost=2.0,
    )

    second = make_candidate(
        "EXP-002",
        information_gain=0.9,
        coverage=0.9,
        cost=1.0,
    )

    selected = planner.select_next_experiment(
        [first, second]
    )

    assert selected.experiment_id == "EXP-002"


def test_risk_affects_score(planner: ExperimentPlanner,) -> None:
    low_risk = make_candidate(
        "EXP-LOW",
        information_gain=0.8,
        coverage=0.8,
        cost=1.0,
        risk="low",
    )

    high_risk = make_candidate(
        "EXP-HIGH",
        information_gain=0.8,
        coverage=0.8,
        cost=1.0,
        risk="high",
    )

    assert (
        planner.score(low_risk)
        > planner.score(high_risk)
    )


def test_empty_candidates_are_rejected(planner: ExperimentPlanner,) -> None:
    with pytest.raises(ValueError):
        planner.select_next_experiment([])


def test_unknown_risk_is_rejected(planner: ExperimentPlanner,) -> None:
    candidate = make_candidate(
        "EXP-001",
        information_gain=0.8,
        coverage=0.8,
        cost=1.0,
        risk="extreme",
    )

    with pytest.raises(ValueError):
        planner.score(candidate)