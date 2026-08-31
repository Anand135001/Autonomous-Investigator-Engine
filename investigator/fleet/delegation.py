from dataclasses import dataclass


@dataclass(frozen=True)
class DelegationRequest:
    agent_id: str
    task: str
    investigation_id: str
    repository_path: str