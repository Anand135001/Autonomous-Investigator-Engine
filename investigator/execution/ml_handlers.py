from pathlib import Path

from investigator.domain.models import (
    Experiment,
    ExperimentResult,
    ExperimentStatus,
)


class PreprocessingCompareHandler:
    """Execute EXP-PREPROCESS-COMPARE."""

    def execute(
        self,
        experiment: Experiment,
        repository_path: str,
    ) -> ExperimentResult:

        benchmark_dir = (
            Path(repository_path)
            / "benchmark"
            / "preprocessing_regression"
        )

        good_stats = (
            benchmark_dir
            / "known_good_stats.txt"
        ).read_text(
            encoding="utf-8"
        ).strip()

        current_stats = (
            benchmark_dir
            / "current_stats.txt"
        ).read_text(
            encoding="utf-8"
        ).strip()

        return ExperimentResult(
            experiment_id=experiment.experiment_id,
            status=ExperimentStatus.SUCCEEDED,
            observations=[
                f"Known-good:\n{good_stats}",
                f"Current:\n{current_stats}",
            ],
            artifacts=[
                str(
                    benchmark_dir
                    / "known_good_stats.txt"
                ),
                str(
                    benchmark_dir
                    / "current_stats.txt"
                ),
            ],
        )


class PreprocessingReproduceHandler:
    """Execute EXP-REPRODUCE."""

    def execute(
        self,
        experiment: Experiment,
        repository_path: str,
    ) -> ExperimentResult:

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
            observations=[
                result,
            ],
            artifacts=[
                str(result_file),
            ],
        )