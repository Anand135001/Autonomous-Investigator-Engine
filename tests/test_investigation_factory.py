from investigator.benchmark.models import (
    BenchmarkCase,
    BenchmarkHypothesis,
)
from investigator.investigation.factory import create_from_benchmark
from investigator.investigation.manager import InvestigationManager


def test_create_investigation_from_benchmark() -> None:
    case = BenchmarkCase(
        case_id="test-case",
        problem="Something failed.",
        repository_path=".",
        root_cause_hypothesis_id="H1",
        root_cause_description="Cause A",
        expected_reproduction=True,
        capabilities=["EXP-GIT-DIFF"],
        hypotheses=[
            BenchmarkHypothesis(
                hypothesis_id="H1",
                description="Cause A",
                initial_confidence=0.7,
            ),
            BenchmarkHypothesis(
                hypothesis_id="H2",
                description="Cause B",
                initial_confidence=0.3,
            ),
        ],
    )

    manager = InvestigationManager()

    investigation = create_from_benchmark(
        manager,
        case,
    )

    assert investigation.investigation_id == (
        "BENCHMARK-test-case"
    )

    assert investigation.problem == (
        "Something failed."
    )

    assert len(investigation.hypotheses) == 2