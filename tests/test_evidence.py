from investigator.domain.models import (
    Evidence,
    Investigation,
)
from investigator.investigation.evidence import (
    build_file_evidence,
    build_git_history_evidence,
    record_evidence,
)


def test_record_evidence_adds_evidence_to_investigation() -> None:
    investigation = Investigation(
        investigation_id="INV-001",
        problem="Something went wrong",
    )

    evidence = Evidence(
        evidence_id="E001",
        source="test",
        observation="Something was observed.",
    )

    record_evidence(investigation, evidence)

    assert len(investigation.evidence) == 1
    assert investigation.evidence[0] is evidence


def test_build_file_evidence() -> None:
    result = {
        "path": "preprocess.py",
        "content": "print('hello')\n",
        "line_count": 1,
    }

    evidence = build_file_evidence(
        evidence_id="E001",
        result=result,
    )

    assert evidence.evidence_id == "E001"
    assert evidence.source == "filesystem"
    assert "preprocess.py" in evidence.observation
    assert evidence.metadata == result


def test_build_git_history_evidence() -> None:
    result = {
        "repository": ".",
        "commit_count": 3,
        "commits": [
            {
                "hash": "abc",
                "author": "Test",
                "authored_at": "2026-08-19T00:00:00Z",
                "message": "test commit",
            }
        ],
    }

    evidence = build_git_history_evidence(
        evidence_id="E002",
        result=result,
    )

    assert evidence.evidence_id == "E002"
    assert evidence.source == "git"
    assert "3 commits" in evidence.observation
    assert evidence.metadata == result