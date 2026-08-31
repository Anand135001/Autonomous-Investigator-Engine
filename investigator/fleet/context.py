from dataclasses import dataclass


@dataclass(frozen=True)
class FleetContext:
    investigation_id: str
    problem: str
    repository_path: str