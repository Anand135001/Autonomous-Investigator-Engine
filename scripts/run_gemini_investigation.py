from investigator.investigation.manager import InvestigationManager
from investigator.planning.default_capabilities import build_default_registry
from investigator.reasoning.candidate_generator import GeminiCandidateGenerator
from investigator.reasoning.gemini import GeminiReasoner
from investigator.workflow.bootstrap import run_adaptive_investigation
from investigator.benchmark.loader import load_case
from investigator.investigation.factory import create_from_benchmark

def main() -> None:
    manager = InvestigationManager()

    registry = build_default_registry()

    reasoner = GeminiReasoner()

    available_capabilities = [
        registry.get(capability_id)
        for capability_id in case.capabilities
    ]
    candidate_generator = GeminiCandidateGenerator(
        reasoner=reasoner,
        capabilities=available_capabilities,
    )

    case = load_case("benchmark/cases/preprocessing_regression.json")
    
    investigation = create_from_benchmark(
        manager,
        case,
    )

    investigation = run_adaptive_investigation(
        manager=manager,
        repository_path=".", 
        candidate_generator=candidate_generator,
        result_analyzer=reasoner,
        investigation=investigation,
    )

    print(f"\nInvestigation:{investigation.investigation_id}")

    print(f"Status:{investigation.status.value}")

    print(f"\nProblem:\n{investigation.problem}")

    print("\nHypotheses:")

    for hypothesis in investigation.hypotheses:
        print(
            f"{hypothesis.hypothesis_id}: "
            f"{hypothesis.description} "
            f"({hypothesis.confidence:.2%})"
        )

    print("\nExperiments:")

    for experiment in investigation.experiments:
        print(
            f"{experiment.experiment_id}: "
            f"{experiment.purpose}"
        )

    print("\nEvidence:")

    for evidence in investigation.evidence:
        print(
            f"{evidence.evidence_id}: "
            f"{evidence.observation}"
        )


if __name__ == "__main__":
    main()