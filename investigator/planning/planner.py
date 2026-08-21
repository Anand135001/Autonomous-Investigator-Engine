from investigator.domain.models import ExperimentCandidate


class ExperimentPlanner:
    """Select the highest-scoring experiment candidate."""

    def score( self, candidate: ExperimentCandidate,) -> float:
        denominator = (
            candidate.estimated_cost
            + self._risk_penalty(candidate.risk_level)
        )

        if denominator <= 0:
            raise ValueError("Experiment cost and risk penalty must be positive")

        return (
            candidate.expected_information_gain
            * candidate.hypothesis_coverage
        ) / denominator


    def select_next_experiment(self, candidates: list[ExperimentCandidate],) -> ExperimentCandidate:
        if not candidates:
            raise ValueError("At least one experiment candidate is required")

        return max(
            candidates,
            key=self.score,
        )


    @staticmethod
    def _risk_penalty(risk_level: str) -> float:
        penalties = {
            "low": 0.5,
            "medium": 1.0,
            "high": 2.0,
        }

        try:
            return penalties[risk_level]
        except KeyError as exc:
            raise ValueError(
                f"Unknown risk level: {risk_level}"
            ) from exc

        
        