from investigator.benchmark.evaluator import BenchmarkEvaluator
from investigator.benchmark.loader import load_case
from investigator.benchmark.results import EvaluationResult
from investigator.investigation.factory import create_from_benchmark
from investigator.investigation.manager import InvestigationManager
from investigator.planning.candidates import DeterministicCandidateGenerator
from investigator.reasoning.deterministic_analyzer import DeterministicResultAnalyzer
from investigator.workflow.bootstrap import run_adaptive_investigation


def run_benchmark(case_path: str, repository_path: str) -> EvaluationResult:

    case = load_case(case_path)

    manager = InvestigationManager()

    investigation = create_from_benchmark(
        manager,
        case,
    )

    investigation = run_adaptive_investigation(
        manager=manager,
        investigation=investigation,
        repository_path=repository_path,
        candidate_generator=(DeterministicCandidateGenerator()),
        result_analyzer=(DeterministicResultAnalyzer()),
    )

    evaluator = BenchmarkEvaluator()

    return evaluator.evaluate(
        case,
        investigation,
    )