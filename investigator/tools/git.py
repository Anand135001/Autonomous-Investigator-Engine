from pathlib import Path
from typing import Any
import subprocess


def inspect_git_history(repository_path: str, limit: int = 10) -> dict[str, Any]:

    """
    Return recent Git commit history
    
    This fucntion only reads repostiory history.
    It does not modify the repository.
    """

    if limit <= 0:
        raise ValueError("Limit must be greater than zero")

    repository  = Path(repository_path)

    if not repository.exists():
        raise FileNotFoundError(
            f"Repository path does not exits: {repository}"
        )

    if not repository.is_dir():
        raise NotADirectoryError(
            f"Repository path is not a directory: {repository}"
        )

    command = [
        "git",
        "-C",
        str(repository),
        "log",
        f"-{limit}",
        "--format=%H%x09%an%x09%aI%x09%s",
    ]


    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )

    except FileNotFoundError as exc:
        raise RuntimeError(
            "git executable was not found on PATH"
        ) from exc


    if completed.returncode != 0:
        raise RuntimeError(
            f"Git command failed: {completed.stderr.strip()}"
        )

    commits: list[dict[str, str]] = []

    for line in completed.stdout.splitlines():
        commit_hash, author, authored_at, message = line.split(
            "\t",
            maxsplit=3,
        )

        commits.append(
            {
                "hash": commit_hash,
                "author": author,
                "authored_at": authored_at,
                "message": message,
            }
        )

    return {
        "repository": str(repository),
        "commit_count": len(commits),
        "commits": commits,
    }



def compare_git_revisions(repository_path: str, base_revision: str, target_revision: str,) -> dict[str, Any]:
    """
    Return a difference between two Git commits.

    This function only reads repository state. It does not modify the repository.
    """

    repository = Path(repository_path)

    if not repository.exists():
        raise FileNotFoundError(
            f"Repository path does not exist: {repository}"
        )

    if not repository.is_dir():
        raise NotADirectoryError(
            f"Repository path is not a directory: {repository}"
        )

    if not base_revision.strip():
        raise ValueError("base_revision cannot be empty")

    if not target_revision.strip():
        raise ValueError("target_revision cannot be empty")

    command = [
        "git",
        "-C",
        str(repository),
        "diff",
        "--stat",
        base_revision,
        target_revision,
    ]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Git executable was not found on PATH"
        ) from exc

    if completed.returncode != 0:
        raise RuntimeError(
            f"Git diff failed: {completed.stderr.strip()}"
        )

    return {
        "repository": str(repository),
        "base_revision": base_revision,
        "target_revision": target_revision,
        "diff_stat": completed.stdout,
    }