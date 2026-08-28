from investigator.investigation.manager import InvestigationManager
from investigator.workflow.bootstrap import run_adaptive_investigation
from investigator.planning.candidates import DeterministicCandidateGenerator
from investigator.reasoning.deterministic_analyzer import DeterministicResultAnalyzer
from investigator.benchmark.loader import load_case
from investigator.investigation.factory import create_from_benchmark

def main() -> None:
    manager = InvestigationManager()

    candidate_generator = DeterministicCandidateGenerator()
    result_analyzer = DeterministicResultAnalyzer()

    case = load_case("benchmark/preprocessing_regression.json")
    investigation = create_from_benchmark(
        manager, 
        case,
    )

    investigation = run_adaptive_investigation(
        manager=manager,
        repository_path=".", 
        candidate_generator=candidate_generator,
        result_analyzer=result_analyzer,
        investigation=investigation
    )

    print(f"\nInvestigation: {investigation.investigation_id}")

    print(f"Status: {investigation.status.value}")

    print(f"\nProblem:\n {investigation.problem}")

    print("\nHypotheses:")

    for hypothesis in investigation.hypotheses:
        print(
            f"  {hypothesis.hypothesis_id}: "
            f"{hypothesis.description} "
            f"({hypothesis.confidence:.2%})"
        )

    print("\nExperiments:")

    for experiment in investigation.experiments:
        print(f" {experiment.experiment_id}: {experiment.purpose}")

    print("\nResults:")

    for result in investigation.results:
        print(f"  {result.experiment_id}: {result.status.value}")

        for observation in result.observations:
            print(f"    {observation}")

    print("\nEvidence:")

    for evidence in investigation.evidence:
        print(f"  {evidence.evidence_id}: {evidence.observation}")


if __name__ == "__main__":
    main()