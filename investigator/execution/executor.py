from pathlib import Path
from investigator.tools.git import compare_git_revisions
from investigator.domain.models import (
    Experiment,
    ExperimentResult,
    ExperimentStatus,
)


class ExperimentExecutor:
    """Executes approved investigation experiments."""

    def execute(self, experiment: Experiment, repository_path: str,) -> ExperimentResult:
        try:
            if experiment.experiment_id == "EXP-GIT-DIFF":
                return self._execute_git_diff(
                    experiment,
                    repository_path,
                )

            if experiment.experiment_id == "EXP-PREPROCESS-COMPARE":
                return self._execute_preprocessing_compare(
                    experiment,
                    repository_path,
                )

            if experiment.experiment_id == "EXP-REPRODUCE":
                return self._execute_reproduction(
                    experiment,
                    repository_path,
                )

            return ExperimentResult(
                experiment_id=experiment.experiment_id,
                status=ExperimentStatus.FAILED,
                error=(
                    "No executor is registered for experiment "
                    f"{experiment.experiment_id}"
                ),
            )

        except Exception as exc:
            return ExperimentResult(
                experiment_id=experiment.experiment_id,
                status=ExperimentStatus.FAILED,
                error=str(exc),
            )

    def _execute_git_diff(self, experiment: Experiment, repository_path: str,) -> ExperimentResult:
        result = compare_git_revisions(
            repository_path,
            "HEAD~1",
            "HEAD",
        )

        return ExperimentResult(
            experiment_id=experiment.experiment_id,
            status=ExperimentStatus.SUCCEEDED,
            observations=[result["diff_stat"].strip(),],
            artifacts=[],
        )

    def _execute_preprocessing_compare(self, experiment: Experiment, repository_path: str,) -> ExperimentResult:
        benchmark_dir = (
            Path(repository_path)
            / "benchmark"
            / "preprocessing_regression"
        )

        good_stats = (
            benchmark_dir / "known_good_stats.txt"
        ).read_text(encoding="utf-8").strip()

        current_stats = (
            benchmark_dir / "current_stats.txt"
        ).read_text(encoding="utf-8").strip()

        return ExperimentResult(
            experiment_id=experiment.experiment_id,
            status=ExperimentStatus.SUCCEEDED,
            observations=[
            f"Known-good:\n{good_stats}",
            f"Current:\n{current_stats}",
            ],
            artifacts=[
                str(benchmark_dir / "known_good_stats.txt"),
                str(benchmark_dir / "current_stats.txt"),
            ],
        )

    def _execute_reproduction(self, experiment: Experiment, repository_path: str,) -> ExperimentResult:
        result_file = (
            Path(repository_path)
            / "benchmark"
            / "preprocessing_regression"
            / "reproduction_result.txt"
        )

        result = result_file.read_text(
            encoding="utf-8"
        ).strip()

        return ExperimentResult(
            experiment_id=experiment.experiment_id,
            status=ExperimentStatus.SUCCEEDED,
            observations=[result,],
            artifacts=[str(result_file)],
        )