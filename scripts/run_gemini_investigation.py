from investigator.investigation.manager import InvestigationManager
from investigator.reasoning.candidate_generator import GeminiCandidateGenerator
from investigator.reasoning.gemini import GeminiReasoner
from investigator.workflow.bootstrap import run_adaptive_investigation


def main() -> None:
    manager = InvestigationManager()

    reasoner = GeminiReasoner()

    candidate_generator = (GeminiCandidateGenerator(reasoner=reasoner))

    investigation = run_adaptive_investigation(
        manager=manager,
        repository_path=".",
        candidate_generator=candidate_generator,
    )

    print(f"Investigation:{investigation.investigation_id}")
    print(f"Status:{investigation.status.value}")
    print("\nExperiments:")

    for experiment in investigation.experiments:
        print(f"- {experiment.experiment_id}: {experiment.purpose}")


if __name__ == "__main__":
    main()