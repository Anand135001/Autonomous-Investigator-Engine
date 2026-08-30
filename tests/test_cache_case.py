from investigator.benchmark.loader import load_case


def test_cache_regression_case() -> None:
    case = load_case(
        "benchmark/cases/cache_regression.json"
    )

    assert case.case_id == "cache_regression"

    assert (
        case.root_cause_hypothesis_id
        == "H1"
    )

    assert case.capabilities == [
        "CACHE-METRICS"
    ]

    assert len(case.hypotheses) == 5