from typing import Any

from investigator.domain.models import Evidence, Investigation


def record_evidence(
    investigation: Investigation,
    evidence: Evidence,
) -> None:
    """Add one evidence item to an investigation."""

    investigation.evidence.append(evidence)


def build_file_evidence(
    *,
    evidence_id: str,
    result: dict[str, Any],
) -> Evidence:
    """Convert file-inspection output into investigation evidence."""

    return Evidence(
        evidence_id=evidence_id,
        source="filesystem",
        observation=(
            f"Inspected file '{result['path']}' "
            f"containing {result['line_count']} lines."
        ),
        metadata=result,
    )


def build_git_history_evidence(
    *,
    evidence_id: str,
    result: dict[str, Any],
) -> Evidence:
    """Convert Git-history output into investigation evidence."""

    commit_count = result["commit_count"]

    return Evidence(
        evidence_id=evidence_id,
        source="git",
        observation=(
            f"Inspected Git history and found "
            f"{commit_count} commits."
        ),
        metadata=result,
    )