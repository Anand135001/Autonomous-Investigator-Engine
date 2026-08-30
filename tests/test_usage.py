from investigator.reasoning.usage import ModelUsage


def test_model_usage_stores_token_counts() -> None:
    usage = ModelUsage(
        operation="planning",
        input_tokens=434,
        output_tokens=541,
        thoughts_tokens=883,
        total_tokens=1858,
    )

    assert usage.operation == "planning"
    assert usage.input_tokens == 434
    assert usage.output_tokens == 541
    assert usage.thoughts_tokens == 883
    assert usage.total_tokens == 1858