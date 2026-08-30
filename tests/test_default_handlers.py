from investigator.execution.default_handlers import (
    build_default_handler_registry,
)


def test_performance_handlers_are_registered() -> None:
    registry = build_default_handler_registry()

    assert registry.get(
        "PERF-CODE-DIFF"
    ).__class__.__name__ == (
        "PerformanceCodeDiffHandler"
    )

    assert registry.get(
        "PERF-QUERY-PROFILE"
    ).__class__.__name__ == (
        "PerformanceQueryProfileHandler"
    )

    assert registry.get(
        "PERF-REPRODUCE"
    ).__class__.__name__ == (
        "PerformanceReproduceHandler"
    )


def test_git_handler_is_registered() -> None:
    registry = build_default_handler_registry()

    assert registry.get(
        "EXP-GIT-DIFF"
    ).__class__.__name__ == "GitDiffHandler"