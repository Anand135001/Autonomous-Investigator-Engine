from investigator.investigation.manager import InvestigationManager
from investigator.workflow.bootstrap import (
    run_adaptive_investigation,
)


def main() -> None:
    manager = InvestigationManager()

    investigation = run_adaptive_investigation(manager=manager, repository_path=".")

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