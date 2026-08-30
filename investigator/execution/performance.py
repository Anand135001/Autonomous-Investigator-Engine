from pathlib import Path

from investigator.domain.models import (
    Experiment,
    ExperimentResult,
    ExperimentStatus,
)


class PerformanceCodeDiffHandler:
    """Execute PERF-CODE-DIFF."""

    def execute(
        self,
        experiment: Experiment,
        repository_path: str,
    ) -> ExperimentResult:

        result_file = (
            Path(repository_path)
            / "benchmark"
            / "api_latency_regression"
            / "deployment_diff.txt"
        )

        result = result_file.read_text(
            encoding="utf-8"
        ).strip()

        return ExperimentResult(
            experiment_id=experiment.experiment_id,
            status=ExperimentStatus.SUCCEEDED,
            observations=[result],
            artifacts=[str(result_file)],
        )


class PerformanceQueryProfileHandler:
    """Execute PERF-QUERY-PROFILE."""

    def execute(
        self,
        experiment: Experiment,
        repository_path: str,
    ) -> ExperimentResult:

        result_file = (
            Path(repository_path)
            / "benchmark"
            / "api_latency_regression"
            / "query_profile.txt"
        )

        result = result_file.read_text(
            encoding="utf-8"
        ).strip()

        return ExperimentResult(
            experiment_id=experiment.experiment_id,
            status=ExperimentStatus.SUCCEEDED,
            observations=[result],
            artifacts=[str(result_file)],
        )


class PerformanceReproduceHandler:
    """Execute PERF-REPRODUCE."""

    def execute(
        self,
        experiment: Experiment,
        repository_path: str,
    ) -> ExperimentResult:

        result_file = (
            Path(repository_path)
            / "benchmark"
            / "api_latency_regression"
            / "reproduction_result.txt"
        )

        result = result_file.read_text(
            encoding="utf-8"
        ).strip()

        return ExperimentResult(
            experiment_id=experiment.experiment_id,
            status=ExperimentStatus.SUCCEEDED,
            observations=[result],
            artifacts=[str(result_file)],
        )