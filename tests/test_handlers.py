from investigator.domain.models import (
    Experiment,
    ExperimentResult,
    ExperimentStatus,
)
from investigator.execution.handlers import (
    HandlerRegistry,
)


class FakeHandler:
    def execute(
        self,
        experiment: Experiment,
        repository_path: str,
    ) -> ExperimentResult:

        return ExperimentResult(
            experiment_id=experiment.experiment_id,
            status=ExperimentStatus.SUCCEEDED,
            observations=["fake"],
        )


def test_handler_can_be_registered() -> None:
    registry = HandlerRegistry()

    handler = FakeHandler()

    registry.register(
        "EXP-001",
        handler,
    )

    assert registry.get("EXP-001") is handler


def test_duplicate_handler_is_rejected() -> None:
    registry = HandlerRegistry()

    handler = FakeHandler()

    registry.register(
        "EXP-001",
        handler,
    )

    try:
        registry.register(
            "EXP-001",
            handler,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected duplicate registration to fail"
        )


def test_unknown_handler_is_rejected() -> None:
    registry = HandlerRegistry()

    try:
        registry.get("EXP-UNKNOWN")
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected unknown handler lookup to fail"
        )