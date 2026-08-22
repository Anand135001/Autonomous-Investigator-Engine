from dataclasses import dataclass, field
from typing import Any
from enum import Enum



class InvestigationStatus(str, Enum):
    """ Lifecycle state of an investigation."""

    PENDING ="pending"
    RUNNING = "running"
    RESOLVED = "resolved"
    INCONCLUSIVE = "inconclusive"
    FAILED = "failed"


class ExperimentStatus(str, Enum):
    """After execution, we need to store what happened """

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class Evidence:
    """observation produced by an investigation"""

    evidence_id: str
    source: str
    observation: str
    experiment_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Hypothesis:
    """possible explanation for the problem."""

    hypothesis_id: str
    description: str
    confidence: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")


@dataclass
class Experiment:
    """An action I(people) perform to obtain information"""

    experiment_id: str
    purpose: str
    target_hypothesis_id: str
    rationale: str
    estimated_cost: float
    timeout_seconds: int
    risk_level: str
    allowed_tools: list[str] = field(default_factory=list)
    status: ExperimentStatus = ExperimentStatus.PENDING


@dataclass
class ExperimentResult:
    """ experiment outcome"""

    experiment_id: str
    status: ExperimentStatus
    observations: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass
class Investigation:
    """State of one technical investigation"""

    investigation_id: str
    problem: str
    status: InvestigationStatus = InvestigationStatus.PENDING
    hypotheses: list[Hypothesis] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    experiments: list[Experiment] = field(default_factory=list)
    results: list[ExperimentResult] = field(default_factory=list)


@dataclass
class ExperimentCandidate:
    """ candidate experiment considered during planning."""

    experiment_id: str
    purpose: str
    target_hypothesis_ids: list[str]
    rationale: str
    expected_information_gain: float
    hypothesis_coverage: float
    estimated_cost: float
    risk_level: str
    timeout_seconds: int
    allowed_tools: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not 0.0 <= self.expected_information_gain <= 1.0:
            raise ValueError(
                "expected_information_gain must be between 0.0 and 1.0"
            )

        if not 0.0 <= self.hypothesis_coverage <= 1.0:
            raise ValueError(
                "hypothesis_coverage must be between 0.0 and 1.0"
            )

        if self.estimated_cost < 0:
            raise ValueError(
                "estimated_cost cannot be negative"
            )

        if self.timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be greater than zero"
            )

        if not self.target_hypothesis_ids:
            raise ValueError(
                "target_hypothesis_ids cannot be empty"
            )