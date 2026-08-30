from investigator.domain.models import (
    Experiment,
    ExperimentResult,
    ExperimentStatus,
)

from investigator.execution.validator import ExperimentValidator
from investigator.execution.default_handlers import build_default_handler_registry
from investigator.execution.handlers import HandlerRegistry

class ExperimentExecutor:
    """Executes approved investigation experiments."""

    def __init__(
        self,
        validator: ExperimentValidator | None = None,
        handler_registry: HandlerRegistry | None = None,
    )-> None:
        self.validator = (
            validator
            if validator is not None
            else ExperimentValidator()
        )

        self.handler_registry = (
            handler_registry
            if handler_registry is not None
            else build_default_handler_registry()
        )


    def execute(
        self,
        experiment: Experiment,
        repository_path: str,
    ) -> ExperimentResult:
    
        try:
            self.validator.validate(
                experiment,
            )
    
            handler = self.handler_registry.get(
                experiment.experiment_id,
            )
    
            return handler.execute(
                experiment,
                repository_path,
            )
    
        except Exception as exc:
            return ExperimentResult(
                experiment_id=experiment.experiment_id,
                status=ExperimentStatus.FAILED,
                error=str(exc),
            )