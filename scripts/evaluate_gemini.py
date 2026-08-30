import argparse
from pathlib import Path

from investigator.benchmark.loader import load_case
from investigator.benchmark.models import BenchmarkCase
from investigator.evaluation.evaluator import (
    InvestigationRunEvaluator,
)
from investigator.investigation.factory import (
    create_from_benchmark,
)
from investigator.investigation.manager import (
    InvestigationManager,
)
from investigator.planning.default_capabilities import (
    build_default_registry,
)
from investigator.reasoning.candidate_generator import (
    GeminiCandidateGenerator,
)
from investigator.reasoning.gemini import (
    GeminiReasoner,
)
from investigator.workflow.bootstrap import (
    run_adaptive_investigation,
)


def run_one(
    run_number: int,
    case: BenchmarkCase,
    project_root: Path,
):
    manager = InvestigationManager()

    investigation = create_from_benchmark(
        manager,
        case,
    )

    registry = build_default_registry()

    capabilities = [
        registry.get(capability_id)
        for capability_id in case.capabilities
    ]

    reasoner = GeminiReasoner()

    candidate_generator = GeminiCandidateGenerator(
        reasoner=reasoner,
        capabilities=capabilities,
    )

    investigation = run_adaptive_investigation(
        manager=manager,
        investigation=investigation,
        repository_path=str(project_root),
        candidate_generator=candidate_generator,
        result_analyzer=reasoner,
    )

    evaluator = InvestigationRunEvaluator()

    return evaluator.evaluate(
        run_number=run_number,
        case=case,
        investigation=investigation,
        usage=reasoner.usage_records,
    )


def print_summary(results) -> None:

    total_runs = len(results)

    resolved_count = sum(
        result.resolved
        for result in results
    )

    correct_count = sum(
        result.root_cause_correct
        for result in results
    )

    reproduction_count = sum(
        result.reproduction_success
        for result in results
    )

    average_experiments = (
        sum(
            result.experiment_count
            for result in results
        )
        / total_runs
    )

    average_confidence = (
        sum(
            result.final_confidence
            for result in results
        )
        / total_runs
    )

    average_planning_tokens = (
        sum(
            usage.input_tokens
            for result in results
            for usage in result.usage
            if usage.operation == "planning"
        )
        / total_runs
    )

    average_analysis_tokens = (
        sum(
            usage.input_tokens
            for result in results
            for usage in result.usage
            if usage.operation == "analysis"
        )
        / total_runs
    )

    average_total_tokens = (
        sum(
            usage.total_tokens
            for result in results
            for usage in result.usage
        )
        / total_runs
    )

    print("\nEvaluation")
    print("----------")

    print(
        f"Runs: {total_runs}"
    )

    print(
        f"Resolved: "
        f"{resolved_count}/{total_runs}"
    )

    print(
        f"Correct root cause: "
        f"{correct_count}/{total_runs}"
    )

    print(
        f"Reproduction success: "
        f"{reproduction_count}/{total_runs}"
    )

    print(
        f"Average experiments: "
        f"{average_experiments:.2f}"
    )

    print(
        f"Average final confidence: "
        f"{average_confidence:.2%}"
    )

    print(
        f"Average planning input tokens: "
        f"{average_planning_tokens:.0f}"
    )

    print(
        f"Average analysis input tokens: "
        f"{average_analysis_tokens:.0f}"
    )

    print(
        f"Average total tokens: "
        f"{average_total_tokens:.0f}"
    )

    print("\nTrajectories")
    print("------------")

    for result in results:
        print(
            f"Run {result.run_number}: "
            f"{' -> '.join(result.selected_experiments)}"
        )


def main() -> None:

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--case",
        required=True,
    )

    parser.add_argument(
        "--runs",
        type=int,
        default=5,
    )

    args = parser.parse_args()

    if args.runs <= 0:
        raise ValueError(
            "--runs must be greater than zero"
        )

    project_root = (
        Path(__file__).resolve().parents[1]
    )

    case_path = (
        project_root
        / "benchmark"
        / "cases"
        / f"{args.case}.json"
    )

    case = load_case(
        str(case_path)
    )

    results = []

    for run_number in range(
        1,
        args.runs + 1,
    ):
        print(f"\n===== RUN {run_number}/{args.runs} =====")
        try:
            result = run_one(
                run_number=run_number,
                case=case,
                project_root=project_root,
            )
    
        except Exception as exc:
            print(
                f"Run {run_number} failed: "
                f"{type(exc).__name__}: {exc}"
            )
            continue
    
        results.append(result)

    print_summary(results)


if __name__ == "__main__":
    main()