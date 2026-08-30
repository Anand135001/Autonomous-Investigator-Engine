import json
from pathlib import Path

from investigator.domain.models import (
    Experiment,
    ExperimentStatus,
)
from investigator.execution.cache import (
    CacheMetricsHandler,
)


def test_cache_metrics_handler(tmp_path: Path,) -> None:

    metrics_dir = (
        tmp_path
        / "benchmark"
        / "cache_metrics"
    )

    metrics_dir.mkdir(
        parents=True
    )

    metrics = {
        "baseline": {
            "hit_rate": 0.94,
            "miss_count": 120,
            "request_count": 2000,
        },
        "current": {
            "hit_rate": 0.21,
            "miss_count": 1820,
            "request_count": 2310,
        },
    }

    metrics_file = (
        metrics_dir / "metrics.json"
    )

    metrics_file.write_text(
        json.dumps(metrics),
        encoding="utf-8",
    )

    experiment = Experiment(
        experiment_id="CACHE-METRICS",
        purpose="Inspect cache metrics",
        target_hypothesis_id="H1",
        rationale="Check cache behavior.",
        estimated_cost=1.0,
        timeout_seconds=30,
        risk_level="low",
        allowed_tools=["filesystem"],
    )

    handler = CacheMetricsHandler()

    result = handler.execute(
        experiment,
        str(tmp_path),
    )

    assert result.status == (
        ExperimentStatus.SUCCEEDED
    )

    assert (
        "baseline_hit_rate=0.94"
        in result.observations
    )

    assert (
        "current_hit_rate=0.21"
        in result.observations
    )

    assert (
        "current_miss_count=1820"
        in result.observations
    )