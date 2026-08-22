from pathlib import Path
import subprocess

import pytest

from investigator.tools.git import inspect_git_history, compare_git_revisions


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
    file_path.write_text(content, encoding="utf-8")

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


def test_inspect_git_history_returns_recent_commits(tmp_path: Path,) -> None:
    initialize_git_repository(tmp_path)

    create_commit(
        tmp_path,
        "first.txt",
        "first",
        "initial commit",
    )

    create_commit(
        tmp_path,
        "second.txt",
        "second",
        "add second file",
    )

    result = inspect_git_history(str(tmp_path), limit=2)

    assert result["repository"] == str(tmp_path)
    assert result["commit_count"] == 2

    messages = [
        commit["message"]
        for commit in result["commits"]
    ]

    assert messages == [
        "add second file",
        "initial commit",
    ]


def test_inspect_git_history_rejects_invalid_limit(tmp_path: Path,) -> None:
    with pytest.raises(ValueError):
        inspect_git_history(str(tmp_path), limit=0)


def test_inspect_git_history_rejects_missing_repository(tmp_path: Path,) -> None:
    missing_path = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        inspect_git_history(str(missing_path))


def test_inspect_git_history_rejects_file_path(tmp_path: Path,) -> None:
    file_path = tmp_path / "not-a-directory"
    file_path.write_text("hello", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        inspect_git_history(str(file_path))



def test_compare_git_revisions_returns_diff_stat(tmp_path: Path,) -> None:
    initialize_git_repository(tmp_path)

    create_commit(
        tmp_path,
        "preprocess.py",
        "normalization_v1\n",
        "initial preprocessing",
    )

    base_revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    create_commit(
        tmp_path,
        "preprocess.py",
        "normalization_v2\n",
        "change preprocessing",
    )

    target_revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    result = compare_git_revisions(
        str(tmp_path),
        base_revision,
        target_revision,
    )

    assert result["base_revision"] == base_revision
    assert result["target_revision"] == target_revision
    assert "preprocess.py" in result["diff_stat"]