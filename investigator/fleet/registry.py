from dataclasses import dataclass


@dataclass(frozen=True)
class AgentDefinition:
    """Definition of an approved fleet agent."""

    agent_id: str
    name: str
    role: str
    capabilities: tuple[str, ...]
    tools: tuple[str, ...]


class AgentRegistry:
    """Registry of approved investigation agents."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentDefinition] = {}

    def register(
        self,
        agent: AgentDefinition,
    ) -> None:

        if agent.agent_id in self._agents:
            raise ValueError(
                f"Agent already registered: "
                f"{agent.agent_id}"
            )

        self._agents[agent.agent_id] = agent

    def get(
        self,
        agent_id: str,
    ) -> AgentDefinition:

        try:
            return self._agents[agent_id]
        except KeyError as exc:
            raise ValueError(
                f"Unknown agent: {agent_id}"
            ) from exc

    def all(self) -> tuple[AgentDefinition, ...]:
        return tuple(
            self._agents.values()
        )


def build_default_agent_registry() -> AgentRegistry:
    registry = AgentRegistry()

    registry.register(
        AgentDefinition(
            agent_id="code-investigator",
            name="Code Investigator",
            role="Inspect source and deployment changes.",
            capabilities=(
                "git-diff",
                "code-regression",
                "query-pattern-analysis",
            ),
            tools=("git",),
        )
    )

    registry.register(
        AgentDefinition(
            agent_id="runtime-investigator",
            name="Runtime Investigator",
            role="Reproduce and measure runtime behavior.",
            capabilities=(
                "latency-reproduction",
                "performance-measurement",
            ),
            tools=("python",),
        )
    )

    registry.register(
        AgentDefinition(
            agent_id="cache-investigator",
            name="Cache Investigator",
            role="Inspect cache behavior and metrics.",
            capabilities=(
                "cache-analysis",
            ),
            tools=("filesystem",),
        )
    )

    registry.register(
        AgentDefinition(
            agent_id="evidence-verifier",
            name="Evidence Verifier",
            role="Verify root cause from collected findings.",
            capabilities=(
                "hypothesis-verification",
            ),
            tools=(),
        )
    )

    return registry    