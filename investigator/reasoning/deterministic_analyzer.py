from investigator.domain.models import ExperimentResult, Investigation
from investigator.reasoning.result_schema import HypothesisAssessment, ResultAssessment


class DeterministicResultAnalyzer:
    """Deterministic result interpreter for benchmark tests."""

    def analyze(self, investigation: Investigation, result: ExperimentResult) -> ResultAssessment:

        confidence_by_experiment = {
            "EXP-GIT-DIFF": 0.45,
            "EXP-PREPROCESS-COMPARE": 0.82,
            "EXP-REPRODUCE": 0.96,
        }

        confidence = confidence_by_experiment.get(result.experiment_id)

        if confidence is None:
            raise ValueError(
                f"No deterministic assessment for "
                f"{result.experiment_id}"
            )

        assessments: list[
            HypothesisAssessment
        ] = []

        for hypothesis in investigation.hypotheses:

            if hypothesis.hypothesis_id == "H1":
                new_confidence = confidence
                effect = "supports"

            else:
                new_confidence = (
                    hypothesis.confidence
                    * (1.0 - confidence)
                    / (1.0 - hypothesis.confidence + 1e-12)
                )

                effect = "weakens"

            assessments.append(
                HypothesisAssessment(
                    hypothesis_id=hypothesis.hypothesis_id,
                    new_confidence=new_confidence,
                    evidence_effect=effect,
                )
            )

        resolved = (
            result.experiment_id == "EXP-REPRODUCE"
            and result.status.value == "succeeded"
        )

        return ResultAssessment(
            summary=(
                f"Deterministic analysis of "
                f"{result.experiment_id}."
            ),
            assessments=assessments,
            should_continue=not resolved,
            recommended_next_focus=("preprocessing verification"),
            verification_sufficient=resolved,
        )