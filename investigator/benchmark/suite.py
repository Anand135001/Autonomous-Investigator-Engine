import json
from pathlib import Path


def load_suite(path: str,) -> list[str]:

    suite_path = Path(path)

    if not suite_path.exists():
        raise FileNotFoundError(
            f"Benchmark suite does not exist: "
            f"{suite_path}"
        )

    data = json.loads(
        suite_path.read_text(encoding="utf-8")
    )

    cases = data.get("cases")

    if not isinstance(cases, list):
        raise ValueError(
            "Benchmark suite 'cases' must be a list."
        )

    if not cases:
        raise ValueError(
            "Benchmark suite must contain at least one case."
        )

    return cases