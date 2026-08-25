from investigator.domain.models import (
    ExperimentCandidate,
    Investigation,
)
from investigator.reasoning.gemini import GeminiReasoner


class GeminiCandidateGenerator:
    """Generate experiment candidates using Gemini."""

    def __init__(self, reasoner: GeminiReasoner) -> None:
        self.reasoner = reasoner

    def generate(self, investigation: Investigation) -> list[ExperimentCandidate]:

        proposal = self.reasoner.propose_experiments(investigation)

        existing_experiment_ids = {
            experiment.experiment_id
            for experiment in investigation.experiments
        }

        existing_hypothesis_ids = {
            hypothesis.hypothesis_id
            for hypothesis in investigation.hypotheses
        }

        candidates: list[ExperimentCandidate] = []

        for proposed in proposal.candidates:

            # Ignore experiments already executed.
            if (
                proposed.experiment_id
                in existing_experiment_ids
            ):
                continue

            # Ignore candidates referring to unknown hypotheses.
            if not set(proposed.target_hypothesis_ids).issubset(existing_hypothesis_ids):
                continue

            candidates.append(
                ExperimentCandidate(
                    experiment_id=proposed.experiment_id,
                    purpose=proposed.purpose,
                    target_hypothesis_ids=proposed.target_hypothesis_ids,
                    rationale=proposed.rationale,
                    expected_information_gain=proposed.expected_information_gain,
                    hypothesis_coverage=proposed.hypothesis_coverage,
                    estimated_cost=proposed.estimated_cost,
                    risk_level=proposed.risk_level,
                    timeout_seconds=proposed.timeout_seconds,
                    allowed_tools=proposed.allowed_tools,
                )
            )

        return candidates