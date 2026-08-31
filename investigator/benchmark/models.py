from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkHypothesis:
    """Hypothesis definition from a benchmark case."""

    hypothesis_id: str
    description: str
    initial_confidence: float


@dataclass(frozen=True)
class BenchmarkCase:
    """Ground-truth definition of one investigation case."""

    case_id: str
    problem: str
    repository_path: str
    root_cause_hypothesis_id: str
    root_cause_description: str
    expected_reproduction: bool
    hypotheses: list[BenchmarkHypothesis]
    capabilities: list[str]