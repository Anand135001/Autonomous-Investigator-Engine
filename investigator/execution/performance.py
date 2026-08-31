from pathlib import Path
import subprocess
from investigator.domain.models import (
    Experiment,
    ExperimentResult,
    ExperimentStatus,
)
from investigator.tools.git import (
    compare_git_revisions,
)


class PerformanceCodeDiffHandler:
    """Execute PERF-CODE-DIFF using Git history."""

    def execute(
        self,
        experiment: Experiment,
        repository_path: str,
    ) -> ExperimentResult:

        result = compare_git_revisions(
            repository_path,
            "HEAD~1",
            "HEAD",
        )

        diff_stat = result.get(
            "diff_stat",
            "",
        ).strip()

        diff = result.get(
            "diff",
            "",
        ).strip()

        observations: list[str] = []

        if diff_stat:
            observations.append(
                f"Diff statistics:\n{diff_stat}"
            )

        if diff:
            observations.append(
                f"Source changes:\n{diff}"
            )

        return ExperimentResult(
            experiment_id=experiment.experiment_id,
            status=ExperimentStatus.SUCCEEDED,
            observations=observations,
            artifacts=[],
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
    """Execute PERF-REPRODUCE using the benchmark program."""

    def execute(
        self,
        experiment: Experiment,
        repository_path: str,
    ) -> ExperimentResult:

        benchmark_file = (
            Path(repository_path)
            / "benchmark_latency.py"
        ).resolve()

        if not benchmark_file.exists():
            raise FileNotFoundError(
                f"Benchmark program does not exist: "
                f"{benchmark_file}"
            )

        completed = subprocess.run(
            [
                "python",
                str(benchmark_file),
            ],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=False,
            timeout=experiment.timeout_seconds,
        )

        if completed.returncode != 0:
            return ExperimentResult(
                experiment_id=experiment.experiment_id,
                status=ExperimentStatus.FAILED,
                observations=[],
                artifacts=[
                    str(benchmark_file)
                ],
                error=(
                    completed.stderr.strip()
                    or "Benchmark execution failed."
                ),
            )

        output = completed.stdout.strip()

        return ExperimentResult(
            experiment_id=experiment.experiment_id,
            status=ExperimentStatus.SUCCEEDED,
            observations=[
                output
            ],
            artifacts=[
                str(benchmark_file)
            ],
        )