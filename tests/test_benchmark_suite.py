import json
from pathlib import Path

from investigator.benchmark.suite import (
    load_suite,
)


def test_load_suite(tmp_path: Path,) -> None:

    suite_path = (
        tmp_path / "suite.json"
    )

    suite_path.write_text(
        json.dumps(
            {
                "cases": [
                    "case_a",
                    "case_b",
                ]
            }
        ),
        encoding="utf-8",
    )

    cases = load_suite(
        str(suite_path)
    )

    assert cases == [
        "case_a",
        "case_b",
    ]