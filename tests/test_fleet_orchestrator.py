from investigator.fleet.delegation import (
    DelegationRequest,
)
from investigator.fleet.orchestrator import (
    FleetOrchestrator,
)
from investigator.fleet.state import (
    FleetInvestigationState,
)


def test_registered_agent_can_be_delegated() -> None:

    orchestrator = (
        FleetOrchestrator()
    )

    request = DelegationRequest(
        agent_id="code-investigator",
        task="Inspect deployment changes.",
        investigation_id="INV-1",
        repository_path="benchmark/fixtures/checkout-service",
    )

    orchestrator.validate_delegation(
        request
    )


def test_finding_is_recorded() -> None:

    orchestrator = (
        FleetOrchestrator()
    )

    state = FleetInvestigationState(
        investigation_id="INV-1",
        problem="Latency regression",
        hypotheses=[],
    )

    orchestrator.record_finding(
        state=state,
        agent_id="code-investigator",
        summary="Found suspicious query loop.",
        evidence=[
            "query_orders(item.id)"
        ],
    )

    assert len(
        state.findings
    ) == 1

    assert (
        state.findings[0].agent_id
        == "code-investigator"
    )