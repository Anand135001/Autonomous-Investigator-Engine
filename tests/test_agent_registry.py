from investigator.fleet.registry import (
    AgentDefinition,
    AgentRegistry,
    build_default_agent_registry,
)


def test_register_and_get_agent() -> None:

    registry = AgentRegistry()

    agent = AgentDefinition(
        agent_id="test-agent",
        name="Test Agent",
        role="Testing",
        capabilities=("test",),
        tools=("python",),
    )

    registry.register(agent)

    assert registry.get(
        "test-agent"
    ) == agent


def test_default_registry_contains_fleet() -> None:

    registry = build_default_agent_registry()

    agent_ids = {
        agent.agent_id
        for agent in registry.all()
    }

    assert agent_ids == {
        "code-investigator",
        "runtime-investigator",
        "cache-investigator",
        "evidence-verifier",
    }