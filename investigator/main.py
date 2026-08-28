from investigator.investigation.manager import InvestigationManager
from investigator.workflow.bootstrap import run_adaptive_investigation
from investigator.planning.candidates import DeterministicCandidateGenerator
from investigator.reasoning.deterministic_analyzer import DeterministicResultAnalyzer
from investigator.domain.models import Hypothesis

def main() -> None:
    manager = InvestigationManager()

    candidate_generator = DeterministicCandidateGenerator()
    result_analyzer = DeterministicResultAnalyzer()

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
        result_analyzer=result_analyzer,
        investigation_id="INV-002",
        problem=(
            "Validation accuracy dropped "
            "from 72.4% to 41.2%"
        ),
        hypotheses=hypotheses,
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