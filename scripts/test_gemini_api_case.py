from pathlib import Path

from investigator.benchmark.loader import load_case
from investigator.investigation.factory import create_from_benchmark
from investigator.investigation.manager import InvestigationManager
from investigator.planning.default_capabilities import build_default_registry
from investigator.reasoning.gemini import GeminiReasoner


def main() -> None:
    project_root = (
        Path(__file__).resolve().parents[1]
    )

    case_path = (
        project_root
        / "benchmark"
        / "cases"
        / "api_latency_regression.json"
    )

    case = load_case(str(case_path))

    manager = InvestigationManager()

    investigation = create_from_benchmark(
        manager,
        case,
    )

    registry = build_default_registry()

    capabilities = [
        registry.get(capability_id)
        for capability_id in case.capabilities
    ]

    print("\nCASE")
    print("----")
    print(case.case_id)

    print("\nAVAILABLE CAPABILITIES")
    print("----------------------")

    for capability in capabilities:
        print(
            f"- {capability.capability_id}: "
            f"{capability.name}"
        )

    print("\nHYPOTHESES")
    print("----------")

    for hypothesis in investigation.hypotheses:
        print(
            f"- {hypothesis.hypothesis_id}: "
            f"{hypothesis.description} "
            f"({hypothesis.confidence:.0%})"
        )

    reasoner = GeminiReasoner()

    proposal = reasoner.propose_experiments(
        investigation,
        capabilities,
    )

    print("\nGEMINI PROPOSALS")
    print("----------------")

    for candidate in proposal.candidates:

        print(
            f"\nID: {candidate.experiment_id}"
        )

        print(
            f"Purpose: {candidate.purpose}"
        )

        print(
            f"Targets: "
            f"{candidate.target_hypothesis_ids}"
        )

        print(
            f"Rationale: {candidate.rationale}"
        )

        print(
            "Information gain: "
            f"{candidate.expected_information_gain:.2f}"
        )

        print(
            "Coverage: "
            f"{candidate.hypothesis_coverage:.2f}"
        )

        print(
            f"Cost: {candidate.estimated_cost:.2f}"
        )

        print(
            f"Risk: {candidate.risk_level}"
        )

        print(
            f"Timeout: "
            f"{candidate.timeout_seconds}s"
        )

        print(
            f"Tools: "
            f"{candidate.allowed_tools}"
        )


if __name__ == "__main__":
    main()