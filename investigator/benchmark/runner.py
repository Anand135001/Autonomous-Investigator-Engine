from investigator.benchmark.evaluator import BenchmarkEvaluator
from investigator.benchmark.loader import load_case
from investigator.domain.models import Hypothesis
from investigator.investigation.manager import InvestigationManager
from investigator.reasoning.deterministic_analyzer import DeterministicResultAnalyzer
from investigator.planning.candidates import DeterministicCandidateGenerator
from investigator.workflow.bootstrap import run_adaptive_investigation


def run_benchmark(
    case_path: str,
    repository_path: str,
):
    case = load_case(case_path)

    hypotheses = [
        Hypothesis(
            hypothesis_id=hypothesis.hypothesis_id,
            description=hypothesis.description,
            confidence=hypothesis.initial_confidence,
        )
        for hypothesis in case.hypotheses
    ]

    manager = InvestigationManager()

    investigation = run_adaptive_investigation(
        manager=manager,
        repository_path=repository_path,
        candidate_generator=(DeterministicCandidateGenerator()),
        result_analyzer=(DeterministicResultAnalyzer()),
        investigation_id=(f"BENCHMARK-{case.case_id}"),
        problem=case.problem,
        hypotheses=hypotheses,
    )

    evaluator = BenchmarkEvaluator()

    return evaluator.evaluate(
        case,
        investigation,
    )