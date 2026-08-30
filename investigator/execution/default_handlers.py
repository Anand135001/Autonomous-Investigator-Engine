from investigator.execution.handlers import (
    HandlerRegistry,
)
from investigator.execution.performance import (
    PerformanceCodeDiffHandler,
    PerformanceQueryProfileHandler,
    PerformanceReproduceHandler,
)


def build_default_handler_registry() -> HandlerRegistry:
    registry = HandlerRegistry()

    registry.register(
        "PERF-CODE-DIFF",
        PerformanceCodeDiffHandler(),
    )

    registry.register(
        "PERF-QUERY-PROFILE",
        PerformanceQueryProfileHandler(),
    )

    registry.register(
        "PERF-REPRODUCE",
        PerformanceReproduceHandler(),
    )

    return registry