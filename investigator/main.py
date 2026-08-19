from investigator.domain.models import Investigation
from investigator.tools.git import inspect_git_history
from investigator.investigation.evidence import (
    build_git_history_evidence,
    record_evidence,
)


def main() -> None:
    investigation = Investigation(
        investigation_id="INV-001",
        problem="Investigate unexpected system behavior.",
    )

    result = inspect_git_history(".", limit=5)
    print("=========== inspect git history ===========: \n", result)
    print(type(result))

    evidence = build_git_history_evidence(
        evidence_id="E001",
        result=result,
    )
    print("========== evidence git history ========== :\n", evidence)
    print(type(evidence))

    record_evidence(
        investigation,
        evidence,
    )
    
    print("\n================ investigation evidence ================\n")
    print(investigation.evidence)


if __name__ == "__main__":
    main()