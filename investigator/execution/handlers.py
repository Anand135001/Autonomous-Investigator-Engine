from investigator.execution.handler import (
    ExperimentHandler,
)


class HandlerRegistry:
    """Maps capability IDs to experiment handlers."""

    def __init__(self) -> None:
        self._handlers: dict[
            str,
            ExperimentHandler,
        ] = {}

    def register(
        self,
        capability_id: str,
        handler: ExperimentHandler,
    ) -> None:

        if capability_id in self._handlers:
            raise ValueError(
                f"Handler already registered: "
                f"{capability_id}"
            )

        self._handlers[
            capability_id
        ] = handler

    def get(self, capability_id: str,) -> ExperimentHandler:

        try:
            return self._handlers[
                capability_id
            ]
        except KeyError as exc:
            raise ValueError(
                f"No handler registered for "
                f"{capability_id}"
            ) from exc