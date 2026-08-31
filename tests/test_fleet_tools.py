from pathlib import Path
import pytest

from investigator.fleet.tools import (
    inspect_deployment_diff,
    reproduce_performance,
)

from scripts.setup_benchmark_fixtures import(
    main as setup_fixtures,
)

def test_inspect_deployment_diff() -> None:

    setup_fixtures()
    
    repository = (
        Path("benchmark")
        / "fixtures"
        / "checkout-service"
    )
    result = inspect_deployment_diff(
        str(repository)
    )
    assert result["base_revision"] == "HEAD~1"
    assert result["target_revision"] == "HEAD"

    assert (
        "query_orders(item.id)"
        in result["diff"]
    )


def test_reproduce_performance() -> None:

    repository = (
        Path("benchmark")
        / "fixtures"
        / "checkout-service"
    )

    result = reproduce_performance(
        str(repository)
    )

    output = result["output"]

    assert (
        "baseline_query_count=1"
        in output
    )

    assert (
        "regressed_query_count=47"
        in output
    )


def test_git_tool_rejects_unapproved_repository() -> None:

    with pytest.raises(
        PermissionError
    ):
        inspect_deployment_diff(
            "."
        )