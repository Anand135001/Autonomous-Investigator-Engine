from investigator.planning.default_capabilities import build_default_registry

from investigator.domain.models import (
    Evidence,
    Hypothesis,
    Investigation,
)
from investigator.reasoning.gemini import GeminiReasoner


def main() -> None:

    investigation = Investigation(
        investigation_id="GEMINI-TEST-001",
        problem=(
            "Validation accuracy dropped from 72.4% "
            "to 41.2%."
        ),
        hypotheses=[
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
                description=(
                    "Learning-rate/configuration issue"
                ),
                confidence=0.21,
            ),
            Hypothesis(
                hypothesis_id="H4",
                description="Label corruption",
                confidence=0.12,
            ),
            Hypothesis(
                hypothesis_id="H5",
                description=(
                    "Model implementation regression"
                ),
                confidence=0.10,
            ),
        ],
        evidence=[
            Evidence(
                evidence_id="E001",
                source="git",
                observation=(
                    "A recent preprocessing-related "
                    "change was found."
                ),
            )
        ],
    )

    reasoner = GeminiReasoner()

    registry = build_default_registry()
     
    proposal = reasoner.propose_experiments(
        investigation,
        registry.all()
    )

    print("\nGemini proposed:")
    
    for candidate in proposal.candidates:
        print(f"\n{candidate.experiment_id}")

        print(f"Purpose: {candidate.purpose}")

        print(f"Targets:{candidate.target_hypothesis_ids}")

        print(f"Reason: {candidate.rationale}")

        print(f"Information gain:{candidate.expected_information_gain}")

        print(f"Coverage: {candidate.hypothesis_coverage}")

        print(f"Cost: {candidate.estimated_cost}")

        print(f"Risk: {candidate.risk_level}")

        print(f"Tools: {candidate.allowed_tools}")


if __name__ == "__main__":
    main()
