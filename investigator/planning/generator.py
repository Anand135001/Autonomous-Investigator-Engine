from typing import Protocol

from investigator.domain.models import (
    ExperimentCandidate,
    Investigation,
)


class CandidateGenerator(Protocol):
    """Interface for generating experiment candidates."""

    def generate(self, investigation: Investigation) -> list[ExperimentCandidate]:
        ...
        