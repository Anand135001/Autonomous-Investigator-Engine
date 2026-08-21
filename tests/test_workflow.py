from pathlib import Path
import subprocess
import pytest

from investigator.domain.models import InvestigationStatus
from investigator.investigation.manager import InvestigationManager
from investigator.workflow.bootstrap import (
    run_initial_investigation,
)


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


def test_initial_investigation_workflow(
    tmp_path: Path,
) -> None:
    initialize_git_repository(tmp_path)

    create_commit(
        tmp_path,
        "README.md",
        "initial project",
        "initial commit",
    )

    create_commit(
        tmp_path,
        "preprocess.py",
        "normalization",
        "change preprocessing",
    )

    manager = InvestigationManager()

    investigation = run_initial_investigation(
        manager=manager,
        repository_path=str(tmp_path),
    )

    assert (
        investigation.status
        == InvestigationStatus.RUNNING
    )

    assert investigation.investigation_id == "INV-001"

    assert len(investigation.hypotheses) == 5

    assert len(investigation.evidence) == 1

    assert (
        investigation.evidence[0].evidence_id
        == "E001"
    )

    preprocessing = next(
        hypothesis
        for hypothesis in investigation.hypotheses
        if hypothesis.hypothesis_id == "H1"
    )

    assert preprocessing.confidence == 0.45

    total_confidence = sum(
        hypothesis.confidence
        for hypothesis in investigation.hypotheses
    )

    assert total_confidence == pytest.approx(1.0)