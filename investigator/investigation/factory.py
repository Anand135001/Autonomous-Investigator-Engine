from investigator.benchmark.models import BenchmarkCase
from investigator.domain.models import Hypothesis
from investigator.investigation.manager import (
    InvestigationManager,
)


def create_from_benchmark(
    manager: InvestigationManager,
    case: BenchmarkCase,
):
    investigation = manager.create(
        investigation_id=(
            f"BENCHMARK-{case.case_id}"
        ),
        problem=case.problem,
    )

    for benchmark_hypothesis in case.hypotheses:
        manager.add_hypothesis(
            investigation,
            Hypothesis(
                hypothesis_id=(
                    benchmark_hypothesis.hypothesis_id
                ),
                description=(
                    benchmark_hypothesis.description
                ),
                confidence=(
                    benchmark_hypothesis.initial_confidence
                ),
            ),
        )

    return investigation