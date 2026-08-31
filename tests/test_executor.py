from pathlib import Path
import subprocess

from investigator.domain.models import Experiment, ExperimentStatus
from investigator.execution.executor import ExperimentExecutor


def initialize_git_repository(path: Path) -> None:
    subprocess.run(
        ["git", "init"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=path,
        check=True,
    )

    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=path,
        check=True,
    )


def create_commit(
    repository: Path,
    filename: str,
    content: str,
    message: str,
) -> None:
    file_path = repository / filename

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    subprocess.run(
        ["git", "add", filename],
        cwd=repository,
        check=True,
    )

    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )


def test_executor_runs_git_diff(tmp_path: Path) -> None:
    initialize_git_repository(tmp_path)

    create_commit(
        tmp_path,
        "preprocess.py",
        "version_1",
        "initial preprocessing",
    )

    create_commit(
        tmp_path,
        "preprocess.py",
        "version_2",
        "change preprocessing",
    )

    experiment = Experiment(
        experiment_id="EXP-GIT-DIFF",
        purpose="Inspect recent source changes",
        target_hypothesis_id="H1",
        rationale="Test",
        estimated_cost=1.0,
        timeout_seconds=30,
        risk_level="low",
    )

    executor = ExperimentExecutor()

    result = executor.execute(
        experiment,
        str(tmp_path),
    )

    assert result.status == ExperimentStatus.SUCCEEDED
    assert result.observations
    assert "preprocess.py" in result.observations[0]


def test_executor_runs_preprocessing_compare(tmp_path: Path) -> None:
    benchmark_dir = (
        tmp_path
        / "benchmark"
        / "preprocessing_regression"
    )

    benchmark_dir.mkdir(parents=True)

    (benchmark_dir / "known_good_stats.txt").write_text(
        "mean=0.02\nstd=0.99\n",
        encoding="utf-8",
    )

    (benchmark_dir / "current_stats.txt").write_text(
        "mean=0.73\nstd=1.81\n",
        encoding="utf-8",
    )

    experiment = Experiment(
        experiment_id="EXP-PREPROCESS-COMPARE",
        purpose="Compare preprocessing distributions",
        target_hypothesis_id="H1",
        rationale="Test",
        estimated_cost=1.0,
        timeout_seconds=30,
        risk_level="low",
    )

    executor = ExperimentExecutor()

    result = executor.execute(
        experiment,
        str(tmp_path),
    )

    assert result.status == ExperimentStatus.SUCCEEDED

    assert any(
        "mean=0.73" in observation
        for observation in result.observations
    )


def test_executor_runs_reproduction(tmp_path: Path) -> None:
    benchmark_dir = (
        tmp_path
        / "benchmark"
        / "preprocessing_regression"
    )

    benchmark_dir.mkdir(parents=True)

    (benchmark_dir / "reproduction_result.txt").write_text(
        "known_good_preprocessing_accuracy=73.1\n"
        "failed_preprocessing_accuracy=41.2\n"
        "reproduction=PASS\n",
        encoding="utf-8",
    )

    experiment = Experiment(
        experiment_id="EXP-REPRODUCE",
        purpose="Reproduce preprocessing result",
        target_hypothesis_id="H1",
        rationale="Test",
        estimated_cost=1.0,
        timeout_seconds=60,
        risk_level="low",
    )

    executor = ExperimentExecutor()

    result = executor.execute(
        experiment,
        str(tmp_path),
    )

    assert result.status == ExperimentStatus.SUCCEEDED
    assert "reproduction=PASS" in result.observations[0]


def test_performance_code_diff_experiment(tmp_path: Path,) -> None:

    subprocess.run(
        ["git", "init"],
        cwd=tmp_path,
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
        cwd=tmp_path,
        check=True,
    )

    subprocess.run(
        [
            "git",
            "config",
            "user.email",
            "test@example.com",
        ],
        cwd=tmp_path,
        check=True,
    )

    source_file = (
        tmp_path
        / "src"
        / "checkout"
        / "orders.py"
    )

    source_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    source_file.write_text(
        """
def load_orders(cart_items, db):
    ids = [item.id for item in cart_items]
    return db.query_orders(ids)
""".strip()
        + "\n",
        encoding="utf-8",
    )

    subprocess.run(
        ["git", "add", "."],
        cwd=tmp_path,
        check=True,
    )

    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            "efficient order loading",
        ],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    source_file.write_text(
        """
def load_orders(cart_items, db):
    orders = []

    for item in cart_items:
        orders.append(
            db.query_orders(item.id)
        )

    return orders
""".strip()
        + "\n",
        encoding="utf-8",
    )

    subprocess.run(
        ["git", "add", "."],
        cwd=tmp_path,
        check=True,
    )

    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            "introduce query regression",
        ],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    experiment = Experiment(
        experiment_id="PERF-CODE-DIFF",
        purpose="Inspect deployment changes",
        target_hypothesis_id="H1",
        rationale="Test deployment changes.",
        estimated_cost=1.0,
        timeout_seconds=30,
        risk_level="low",
        allowed_tools=["git"],
    )

    executor = ExperimentExecutor()

    result = executor.execute(
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