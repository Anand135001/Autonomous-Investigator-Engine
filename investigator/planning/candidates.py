from investigator.domain.models import ExperimentCandidate, Investigation


class CandidateGenerator:
    """Generates safe experiment candidates from investigation state."""

    def generate(self, investigation: Investigation) -> list[ExperimentCandidate]:

        candidates: list[ExperimentCandidate] = []
    
        experiment_ids = {
            experiment.experiment_id
            for experiment in investigation.experiments
        }
    
        evidence_text = " ".join(
            evidence.observation.lower()
            for evidence in investigation.evidence
        )
    
        if not experiment_ids:
            candidates.append(
                ExperimentCandidate(
                    experiment_id="EXP-GIT-DIFF",
                    purpose="Inspect recent source changes",
                    target_hypothesis_ids=["H1", "H5"],
                    rationale=(
                        "Recent source changes may explain "
                        "the regression."
                    ),
                    expected_information_gain=0.80,
                    hypothesis_coverage=0.80,
                    estimated_cost=1.0,
                    risk_level="low",
                    timeout_seconds=30,
                    allowed_tools=["git"],
                )
            )

        elif (
            "EXP-GIT-DIFF" in experiment_ids
            and "EXP-PREPROCESS-COMPARE" not in experiment_ids
        ):
            candidates.append(
                ExperimentCandidate(
                    experiment_id="EXP-PREPROCESS-COMPARE",
                    purpose="Compare preprocessing distributions",
                    target_hypothesis_ids=["H1"],
                    rationale=(
                        "The previous experiment identified a "
                        "possible preprocessing change."
                    ),
                    expected_information_gain=0.90,
                    hypothesis_coverage=0.95,
                    estimated_cost=1.5,
                    risk_level="low",
                    timeout_seconds=30,
                    allowed_tools=["filesystem"],
                )
            )

        elif (
            "EXP-PREPROCESS-COMPARE" in experiment_ids
            and "EXP-REPRODUCE" not in experiment_ids
        ):
            candidates.append(
                ExperimentCandidate(
                    experiment_id="EXP-REPRODUCE",
                    purpose="Reproduce the suspected preprocessing cause",
                    target_hypothesis_ids=["H1"],
                    rationale=(
                        "The preprocessing comparison provides "
                        "enough evidence to perform direct reproduction."
                    ),
                    expected_information_gain=1.0,
                    hypothesis_coverage=1.0,
                    estimated_cost=3.0,
                    risk_level="low",
                    timeout_seconds=60,
                    allowed_tools=["python"],
                )
            )
    
        return candidates