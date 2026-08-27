from investigator.domain.models import ExperimentCapability


class CapabilityRegistry:
    """Registry of experiments the system can actually execute."""

    def __init__(self) -> None:
        self._capabilities: dict[str, ExperimentCapability] = {}


    def register(self, capability: ExperimentCapability) -> None:
        if (
            capability.capability_id
            in self._capabilities
        ):
            raise ValueError(f"Capability already registered: {capability.capability_id}")

        self._capabilities[capability.capability_id] = capability


    def get(self, capability_id: str) -> ExperimentCapability:
        try:
            return self._capabilities[capability_id]
        except KeyError as exc:
            raise ValueError(f"Unknown capability: {capability_id}") from exc

        
    def all(self) -> list[ExperimentCapability]:
        return list(self._capabilities.values())