import json
from pathlib import Path

from investigator.benchmark.models import BenchmarkCase, BenchmarkHypothesis


def load_case(path: str) -> BenchmarkCase:

    case_path = Path(path)

    if not case_path.exists():
        raise FileNotFoundError(f"Benchmark case does not exist: {case_path}")

    data = json.loads(case_path.read_text(encoding="utf-8"))

    hypotheses = [
        BenchmarkHypothesis(
            hypothesis_id=item["hypothesis_id"],
            description=item["description"],
            initial_confidence=item[
                "initial_confidence"
            ],
        )
        for item in data["hypotheses"]
    ]

    return BenchmarkCase(
        case_id=data["case_id"],
        problem=data["problem"],
        root_cause_hypothesis_id=(data["root_cause_hypothesis_id"]),
        root_cause_description=(data["root_cause_description"]),
        expected_reproduction=(data["expected_reproduction"]),
        hypotheses=hypotheses,
        capabilities=data["capabilities"],
    )