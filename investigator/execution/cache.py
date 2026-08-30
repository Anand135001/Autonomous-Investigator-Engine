import json
from pathlib import Path

from investigator.domain.models import (
    Experiment,
    ExperimentResult,
    ExperimentStatus,
)


class CacheMetricsHandler:
    """Execute CACHE-METRICS."""

    def execute(
        self,
        experiment: Experiment,
        repository_path: str,
    ) -> ExperimentResult:

        metrics_file = (
            Path(repository_path)
            / "benchmark"
            / "cache_metrics"
            / "metrics.json"
        )

        if not metrics_file.exists():
            raise FileNotFoundError(
                f"Cache metrics file does not exist: "
                f"{metrics_file}"
            )

        data = json.loads(
            metrics_file.read_text(
                encoding="utf-8"
            )
        )

        baseline = data["baseline"]
        current = data["current"]

        observations = [
            (
                f"baseline_hit_rate="
                f"{baseline['hit_rate']}"
            ),
            (
                f"current_hit_rate="
                f"{current['hit_rate']}"
            ),
            (
                f"baseline_miss_count="
                f"{baseline['miss_count']}"
            ),
            (
                f"current_miss_count="
                f"{current['miss_count']}"
            ),
            (
                f"baseline_request_count="
                f"{baseline['request_count']}"
            ),
            (
                f"current_request_count="
                f"{current['request_count']}"
            ),
        ]

        return ExperimentResult(
            experiment_id=experiment.experiment_id,
            status=ExperimentStatus.SUCCEEDED,
            observations=observations,
            artifacts=[
                str(metrics_file)
            ],
        )