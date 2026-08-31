from investigator.evaluation.models import (
    InvestigationRunResult,
    SuiteResult,
)


class SuiteEvaluator:
    """Aggregate results from multiple benchmark runs."""

    def evaluate(
        self,
        results: list[InvestigationRunResult],
        requested_runs: int,
        failed_runs: int,
    ) -> SuiteResult:

        return SuiteResult(
            requested_runs=requested_runs,
            completed_runs=len(results),
            failed_runs=failed_runs,
            results=tuple(results),
        )