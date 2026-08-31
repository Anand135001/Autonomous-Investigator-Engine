from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class AgentFinding:
    agent_id: str
    summary: str
    evidence: list[str] = field(
        default_factory=list
    )
    timestamp: str = field(
        default_factory=lambda:
            datetime.now(timezone.utc).isoformat()
    )


@dataclass
class FleetInvestigationState:
    investigation_id: str
    problem: str
    hypotheses: list[dict]
    findings: list[AgentFinding] = field(
        default_factory=list
    )
    status: str = "running"

    def add_finding(
        self,
        finding: AgentFinding,
    ) -> None:
        self.findings.append(finding)