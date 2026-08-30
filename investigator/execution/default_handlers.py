from investigator.execution.handlers import (
    HandlerRegistry,
)
from investigator.execution.performance import (
    PerformanceCodeDiffHandler,
    PerformanceQueryProfileHandler,
    PerformanceReproduceHandler,
)
from investigator.execution.git_handler import(
    GitDiffHandler,
)
from investigator.execution.ml_handlers import(
    PreprocessingCompareHandler,
    PreprocessingReproduceHandler
)
from investigator.execution.cache import CacheMetricsHandler



def build_default_handler_registry() -> HandlerRegistry:
    registry = HandlerRegistry()

    registry.register(
        "EXP-GIT-DIFF",
        GitDiffHandler(),
    )

    registry.register(
        "EXP-PREPROCESS-COMPARE",
        PreprocessingCompareHandler(),
    )
    
    registry.register(
        "EXP-REPRODUCE",
        PreprocessingReproduceHandler(),
    )

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

    registry.register(
        "CACHE-METRICS",
        CacheMetricsHandler(),
    )

    return registry