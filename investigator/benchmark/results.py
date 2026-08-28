from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationResult:
    """Evaluation result for one benchmark execution."""

    case_id: str
    root_cause_correct: bool
    reproduction_success: bool
    experiment_count: int
    human_interventions: int
    repeated_experiments: int
    final_confidence: float
    resolved: bool