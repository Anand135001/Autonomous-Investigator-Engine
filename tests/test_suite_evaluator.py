from investigator.evaluation.models import (
    InvestigationRunResult,
)
from investigator.evaluation.suite import (
    SuiteEvaluator,
)


def test_suite_evaluator_aggregates_results() -> None:

    result = InvestigationRunResult(
        run_number=1,
        case_id="case_a",
        resolved=True,
        root_cause_correct=True,
        reproduction_success=False,
        experiment_count=1,
        repeated_experiments=0,
        final_confidence=0.9,
        selected_experiments=(
            "EXP-001",
        ),
        usage=(),
    )

    suite = SuiteEvaluator().evaluate(
        results=[result],
        requested_runs=2,
        failed_runs=1,
    )

    assert suite.requested_runs == 2
    assert suite.completed_runs == 1
    assert suite.failed_runs == 1
    assert suite.results == (result,)