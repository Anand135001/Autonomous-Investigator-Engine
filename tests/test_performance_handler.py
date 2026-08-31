import subprocess
from pathlib import Path

from investigator.domain.models import (
    Experiment,
    ExperimentStatus,
)
from investigator.execution.performance import (
    PerformanceCodeDiffHandler,
    PerformanceReproduceHandler,
)


def _init_repo(path: Path) -> None:
    subprocess.run(
        ["git", "init"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [
            "git",
            "config",
            "user.name",
            "Test User",
        ],
        cwd=path,
        check=True,
    )

    subprocess.run(
        [
            "git",
            "config",
            "user.email",
            "test@example.com",
        ],
        cwd=path,
        check=True,
    )


def _commit(
    repo: Path,
    file_path: str,
    content: str,
    message: str,
) -> None:

    target = repo / file_path
    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    target.write_text(
        content,
        encoding="utf-8",
    )

    subprocess.run(
        ["git", "add", file_path],
        cwd=repo,
        check=True,
    )

    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def test_performance_code_diff_uses_real_git(tmp_path: Path,) -> None:

    _init_repo(tmp_path)

    _commit(
        tmp_path,
        "src/checkout/orders.py",
        """
def load_orders(cart_items, db):
    ids = [item.id for item in cart_items]
    return db.query_orders(ids)
""",
        "add efficient order loading",
    )

    _commit(
        tmp_path,
        "src/checkout/orders.py",
        """
def load_orders(cart_items, db):
    orders = []

    for item in cart_items:
        orders.append(
            db.query_orders(item.id)
        )

    return orders
""",
        "introduce query regression",
    )

    experiment = Experiment(
        experiment_id="PERF-CODE-DIFF",
        purpose="Inspect deployment code changes",
        target_hypothesis_id="H1",
        rationale="Identify performance regressions.",
        estimated_cost=1.0,
        timeout_seconds=30,
        risk_level="low",
        allowed_tools=["git"],
    )

    handler = PerformanceCodeDiffHandler()

    result = handler.execute(
        experiment,
        str(tmp_path),
    )

    assert result.status == (
        ExperimentStatus.SUCCEEDED
    )

    combined_output = "\n".join(
        result.observations
    )

    assert (
        "query_orders(item.id)"
        in combined_output
    )

    assert (
        "for item in cart_items"
        in combined_output
    )


def test_performance_reproduce_executes_benchmark(tmp_path: Path,) -> None:

    benchmark_file = (
        tmp_path / "benchmark_latency.py"
    )

    benchmark_file.write_text(
        """
print("baseline_p95_ms=20")
print("regressed_p95_ms=940")
print("baseline_query_count=1")
print("regressed_query_count=47")
""".strip(),
        encoding="utf-8",
    )

    experiment = Experiment(
        experiment_id="PERF-REPRODUCE",
        purpose="Reproduce performance regression",
        target_hypothesis_id="H1",
        rationale="Measure actual regression.",
        estimated_cost=3.0,
        timeout_seconds=30,
        risk_level="low",
        allowed_tools=["python"],
    )

    handler = PerformanceReproduceHandler()

    result = handler.execute(
        experiment,
        str(tmp_path),
    )

    assert result.status == (
        ExperimentStatus.SUCCEEDED
    )

    output = result.observations[0]

    assert (
        "baseline_p95_ms=20"
        in output
    )

    assert (
        "regressed_p95_ms=940"
        in output
    )

    assert (
        "regressed_query_count=47"
        in output
    )