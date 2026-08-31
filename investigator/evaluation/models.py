from dataclasses import dataclass

from investigator.reasoning.usage import ModelUsage


@dataclass(frozen=True)
class InvestigationRunResult:
    """Measured outcome of one investigation run."""

    run_number: int
    case_id: str
    resolved: bool
    root_cause_correct: bool
    reproduction_success: bool
    experiment_count: int
    repeated_experiments: int
    final_confidence: float
    selected_experiments: tuple[str, ...]
    usage: tuple[ModelUsage, ...]


@dataclass(frozen=True)
class SuiteResult:
    """Aggregated evaluation results across benchmark cases."""

    requested_runs: int
    completed_runs: int
    failed_runs: int
    results: tuple[InvestigationRunResult, ...]