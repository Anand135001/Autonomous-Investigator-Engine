from collections import Counter

from investigator.benchmark.models import BenchmarkCase
from investigator.benchmark.results import EvaluationResult
from investigator.domain.models import Investigation


class BenchmarkEvaluator:
    """Compare an investigation against benchmark ground truth."""

    def evaluate(
        self,
        case: BenchmarkCase,
        investigation: Investigation,
    ) -> EvaluationResult:

        root_cause = self._find_leading_hypothesis(
            investigation
        )

        root_cause_correct = (
            root_cause is not None
            and root_cause.hypothesis_id
            == case.root_cause_hypothesis_id
        )

        repeated_experiments = (
            self._count_repeated_experiments(
                investigation
            )
        )

        reproduction_success = any(
            "reproduction=PASS" in observation
            for result in investigation.results
            for observation in result.observations
        )

        final_confidence = (
            root_cause.confidence
            if root_cause is not None
            else 0.0
        )

        return EvaluationResult(
            case_id=case.case_id,
            root_cause_correct=root_cause_correct,
            reproduction_success=reproduction_success,
            experiment_count=len(
                investigation.experiments
            ),
            human_interventions=0,
            repeated_experiments=repeated_experiments,
            final_confidence=final_confidence,
            resolved=investigation.status.value
            == "resolved",
        )

    @staticmethod
    def _find_leading_hypothesis(investigation: Investigation):
        if not investigation.hypotheses:
            return None

        return max(
            investigation.hypotheses,
            key=lambda hypothesis: hypothesis.confidence,
        )

    @staticmethod
    def _count_repeated_experiments(investigation: Investigation) -> int:

        experiment_ids = [
            experiment.experiment_id
            for experiment in investigation.experiments
        ]

        counts = Counter(experiment_ids)

        return sum(
            count - 1
            for count in counts.values()
            if count > 1
        )