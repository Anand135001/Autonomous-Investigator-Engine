from investigator.fleet.delegation import (
    DelegationRequest,
)
from investigator.fleet.registry import (
    AgentRegistry,
    build_default_agent_registry,
)
from investigator.fleet.state import (
    AgentFinding,
    FleetInvestigationState,
)


class FleetOrchestrator:
    """Coordinates registered specialist agents."""

    def __init__(
        self,
        registry: AgentRegistry | None = None,
    ) -> None:

        self.registry = (
            registry
            if registry is not None
            else build_default_agent_registry()
        )

    def validate_delegation(
        self,
        request: DelegationRequest,
    ) -> None:

        agent = self.registry.get(
            request.agent_id
        )

        allowed = {
            capability
            for capability in agent.capabilities
        }

        if not allowed:
            raise ValueError(
                f"Agent {request.agent_id} "
                "has no executable capabilities."
            )

    def record_finding(
        self,
        state: FleetInvestigationState,
        agent_id: str,
        summary: str,
        evidence: list[str],
    ) -> None:

        self.registry.get(
            agent_id
        )

        state.add_finding(
            AgentFinding(
                agent_id=agent_id,
                summary=summary,
                evidence=evidence,
            )
        )