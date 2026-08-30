from typing import Protocol

from investigator.domain.models import (
    Experiment,
    ExperimentResult,
)


class ExperimentHandler(Protocol):
    """Interface implemented by an experiment handler."""

    def execute(
        self,
        experiment: Experiment,
        repository_path: str,
    ) -> ExperimentResult:
        ...