from investigator.investigation.manager import InvestigationManager
from investigator.planning.default_capabilities import build_default_registry
from investigator.reasoning.candidate_generator import GeminiCandidateGenerator
from investigator.reasoning.gemini import GeminiReasoner
from investigator.workflow.bootstrap import run_adaptive_investigation
from investigator.domain.models import Hypothesis 

def main() -> None:
    manager = InvestigationManager()

    registry = build_default_registry()

    reasoner = GeminiReasoner()

    candidate_generator = GeminiCandidateGenerator(
        reasoner=reasoner,
        capabilities=registry.all(),
    )

    hypotheses = [
        Hypothesis(
            hypothesis_id="H1",
            description="Preprocessing regression",
            confidence=0.31,
        ),
        Hypothesis(
            hypothesis_id="H2",
            description="Dataset distribution shift",
            confidence=0.26,
        ),
        Hypothesis(
            hypothesis_id="H3",
            description="Learning-rate/configuration issue",
            confidence=0.21,
        ),
        Hypothesis(
            hypothesis_id="H4",
            description="Label corruption",
            confidence=0.12,
        ),
        Hypothesis(
            hypothesis_id="H5",
            description="Model implementation regression",
            confidence=0.10,
        ),
    ]           

    investigation = run_adaptive_investigation(
        manager=manager,
        repository_path=".", 
        candidate_generator=candidate_generator,
        result_analyzer=reasoner,
        investigation_id="INV-002",
        problem=(
            "Validation accuracy dropped "
            "from 72.4% to 41.2%"
        ),
        hypotheses=hypotheses,
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