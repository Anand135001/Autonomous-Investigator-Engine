from investigator.domain.models import ExperimentCandidate, Investigation



class CandidateGenerator:
    """Generates safe experiment candidates for an investigation."""

    def generate(self, investigation: Investigation, ) -> list[ExperimentCandidate]:
        candidates: list[ExperimentCandidate] = []

        hypothesis_ids = {
            hypothesis.hypothesis_id
            for hypothesis in investigation.hypotheses
        }

        if {"H1", "H5"} & hypothesis_ids:
            candidates.append(
                ExperimentCandidate(
                    experiment_id="EXP-GIT-DIFF",
                    purpose="Inspect recent source changes",
                    target_hypothesis_ids=[
                        hypothesis_id
                        for hypothesis_id in ["H1", "H5"]
                        if hypothesis_id in hypothesis_ids
                    ],
                    rationale=(
                        "Recent source changes may distinguish "
                        "a preprocessing or model regression."
                    ),
                    expected_information_gain=0.80,
                    hypothesis_coverage=0.80,
                    estimated_cost=1.0,
                    risk_level="low",
                    timeout_seconds=30,
                    allowed_tools=["git"],
                )
            )

        return candidates