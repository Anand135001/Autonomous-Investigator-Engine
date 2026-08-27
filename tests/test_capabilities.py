import pytest
from investigator.planning.capabilities import CapabilityRegistry
from investigator.planning.default_capabilities import build_default_registry


def test_registry_starts_empty() -> None:
    registry = CapabilityRegistry()
    assert registry.all() == []


def test_registry_can_register_capability() -> None:
    registry = build_default_registry()
    capabilities = registry.all()
    assert len(capabilities) == 3


def test_registry_can_lookup_capability() -> None:
    registry = build_default_registry()
    capability = registry.get("EXP-GIT-DIFF")
    assert capability.name == ("Git revision comparison")


def test_unknown_capability_is_rejected() -> None:
    registry = build_default_registry()

    with pytest.raises(ValueError):
        registry.get("EXP-NONEXISTENT")


def test_duplicate_capability_is_rejected() -> None:
    registry = build_default_registry()
    capability = registry.get("EXP-GIT-DIFF")

    with pytest.raises(ValueError):
        registry.register(capability)