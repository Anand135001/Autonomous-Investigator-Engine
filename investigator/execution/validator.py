from investigator.domain.models import ExperimentContract


class ExperimentValidator:
    """Validate whether an experiment may be executed."""

    ALLOWED_RISK_LEVELS = {
        "low",
        "medium",
        "high",
    }

    ALLOWED_TOOLS = {
        "filesystem",
        "git",
        "python",
    }

    MAX_TIMEOUT_SECONDS = 300
    MAX_ESTIMATED_COST = 10.0


    def validate(self, contract: ExperimentContract) -> None:
        self._validate_tools(contract)
        self._validate_timeout(contract)
        self._validate_cost(contract)
        self._validate_risk(contract)


    def _validate_tools(self, contract: ExperimentContract) -> None:
        unknown_tools = (
            set(contract.allowed_tools)
            - self.ALLOWED_TOOLS
        )

        if unknown_tools:
            raise ValueError(f"Experiment requests unsupported tools: {sorted(unknown_tools)}")


    def _validate_timeout(self, contract: ExperimentContract) -> None:
        if contract.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")

        if contract.timeout_seconds > self.MAX_TIMEOUT_SECONDS:
            raise ValueError("timeout_seconds exceeds the maximum allowed value")


    def _validate_cost(self, contract: ExperimentContract) -> None:
        if contract.estimated_cost < 0:
            raise ValueError("estimated_cost cannot be negative")

        if contract.estimated_cost > self.MAX_ESTIMATED_COST:
            raise ValueError("estimated_cost exceeds the maximum allowed value")


    def _validate_risk(self, contract: ExperimentContract) -> None:
        if contract.risk_level not in self.ALLOWED_RISK_LEVELS:
            raise ValueError(f"Unsupported risk level: {contract.risk_level}")