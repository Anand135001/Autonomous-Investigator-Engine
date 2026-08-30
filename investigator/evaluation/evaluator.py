from collections import Counter

from investigator.benchmark.models import BenchmarkCase
from investigator.domain.models import Investigation
from investigator.evaluation.models import InvestigationRunResult
from investigator.reasoning.usage import ModelUsage


class InvestigationRunEvaluator:
    """Convert one investigation into measurable evaluation results."""

    def evaluate(
        self,
        run_number: int,
        case: BenchmarkCase,
        investigation: Investigation,
        usage: list[ModelUsage],
    ) -> InvestigationRunResult:

        leading_hypothesis = self._leading_hypothesis(
            investigation
        )

        root_cause_correct = (
            leading_hypothesis is not None
            and leading_hypothesis.hypothesis_id
            == case.root_cause_hypothesis_id
        )

        reproduction_success = any(
            "reproduction=PASS" in observation
            for result in investigation.results
            for observation in result.observations
        )

        experiment_ids = [
            experiment.experiment_id
            for experiment in investigation.experiments
        ]

        repeated_experiments = self._count_repeated(
            experiment_ids
        )

        final_confidence = (
            leading_hypothesis.confidence
            if leading_hypothesis is not None
            else 0.0
        )

        return InvestigationRunResult(
            run_number=run_number,
            case_id=case.case_id,
            resolved=(
                investigation.status.value
                == "resolved"
            ),
            root_cause_correct=root_cause_correct,
            reproduction_success=reproduction_success,
            experiment_count=len(experiment_ids),
            repeated_experiments=repeated_experiments,
            final_confidence=final_confidence,
            selected_experiments=tuple(
                experiment_ids
            ),
            usage=tuple(usage),
        )

    @staticmethod
    def _leading_hypothesis(
        investigation: Investigation,
    ):
        if not investigation.hypotheses:
            return None

        return max(
            investigation.hypotheses,
            key=lambda hypothesis: hypothesis.confidence,
        )

    @staticmethod
    def _count_repeated(experiment_ids: list[str]) -> int:

        counts = Counter(experiment_ids)

        return sum(
            count - 1
            for count in counts.values()
            if count > 1
        )