from typing import Protocol

from investigator.domain.models import ExperimentResult, Investigation
from investigator.reasoning.result_schema import ResultAssessment


class ResultAnalyzer(Protocol):
    """Interface for interpreting experiment results."""

    def analyze(
        self,
        investigation: Investigation,
        result: ExperimentResult,
    ) -> ResultAssessment:
        ...