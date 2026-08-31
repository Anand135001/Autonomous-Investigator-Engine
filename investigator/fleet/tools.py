from pathlib import Path

from investigator.tools.git import (
    compare_git_revisions,
)

PROJECT_ROOT = (
    Path(__file__).resolve().parents[2]
)

ALLOWED_REPOSITORIES = {
    (
        PROJECT_ROOT
        / "benchmark"
        / "fixtures"
        / "checkout-service"
    ).resolve()
}


def inspect_deployment_diff(
    repository_path: str,
) -> dict:
    """
    Inspect the latest Git revision change.

    Read-only operation.
    """

    repository = Path(
        repository_path
    ).resolve()


    if repository not in ALLOWED_REPOSITORIES:
        raise PermissionError(
            "Repository is not approved for this tool."
        )

    result = compare_git_revisions(
        str(repository),
        "HEAD~1",
        "HEAD",
    )

    return {
        "repository": result["repository"],
        "base_revision": result["base_revision"],
        "target_revision": result["target_revision"],
        "diff_stat": result["diff_stat"],
        "diff": result.get(
            "diff",
            "",
        ),
    }


def reproduce_performance(
    repository_path: str,
) -> dict:
    """
    Execute the controlled performance benchmark.

    The benchmark is isolated to the supplied repository.
    """
    
    repository = Path(
        repository_path
    ).resolve()    

    if repository not in ALLOWED_REPOSITORIES:
        raise PermissionError(
            "Repository is not approved for this tool."
        )
    
    benchmark_file = (
        Path(repository_path).resolve()
        / "benchmark_latency.py"
    )

    if not benchmark_file.exists():
        raise FileNotFoundError(
            f"Benchmark program does not exist: "
            f"{benchmark_file}"
        )

    import subprocess

    completed = subprocess.run(
        [
            "python",
            str(benchmark_file),
        ],
        cwd=str(benchmark_file.parent),
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            completed.stderr.strip()
            or "Performance benchmark failed."
        )

    return {
        "repository": str(
            benchmark_file.parent
        ),
        "output": completed.stdout.strip(),
    }