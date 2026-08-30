from pathlib import Path
import subprocess

from investigator.domain.models import (
    Experiment,
    ExperimentStatus,
)
from investigator.execution.git_handler import (
    GitDiffHandler,
)


def initialize_git_repository(
    path: Path,
) -> None:

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


def commit_file(
    repository: Path,
    filename: str,
    content: str,
    message: str,
) -> None:

    file_path = repository / filename

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


def test_git_diff_handler(
    tmp_path: Path,
) -> None:

    initialize_git_repository(
        tmp_path
    )

    commit_file(
        tmp_path,
        "example.py",
        "version_one\n",
        "initial",
    )

    commit_file(
        tmp_path,
        "example.py",
        "version_two\n",
        "change",
    )

    experiment = Experiment(
        experiment_id="EXP-GIT-DIFF",
        purpose="Inspect Git changes",
        target_hypothesis_id="H1",
        rationale="Test recent changes.",
        estimated_cost=1.0,
        timeout_seconds=30,
        risk_level="low",
    )

    handler = GitDiffHandler()

    result = handler.execute(
        experiment,
        str(tmp_path),
    )

    assert result.status == (
        ExperimentStatus.SUCCEEDED
    )

    assert "example.py" in (
        result.observations[0]
    )