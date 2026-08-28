import json
from pathlib import Path

from investigator.benchmark.loader import load_case


def test_load_benchmark_case(tmp_path: Path) -> None:
    case_path = tmp_path / "case.json"

    case_path.write_text(
        json.dumps(
            {
                "case_id": "test-case",
                "problem": "Something failed.",
                "root_cause_hypothesis_id": "H1",
                "root_cause_description": "Cause A",
                "expected_reproduction": True,
                "hypotheses": [
                    {
                        "hypothesis_id": "H1",
                        "description": "Cause A",
                        "initial_confidence": 0.7,
                    },
                    {
                        "hypothesis_id": "H2",
                        "description": "Cause B",
                        "initial_confidence": 0.3,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    case = load_case(str(case_path))

    assert case.case_id == "test-case"
    assert case.root_cause_hypothesis_id == "H1"
    assert len(case.hypotheses) == 2