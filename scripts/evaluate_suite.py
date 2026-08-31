import argparse
from pathlib import Path

from investigator.benchmark.loader import load_case
from investigator.benchmark.suite import load_suite
from investigator.evaluation.evaluator import (
    InvestigationRunEvaluator,
)
from investigator.evaluation.models import (
    InvestigationRunResult,
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
from investigator.evaluation.suite import SuiteEvaluator

def run_case(
    case_id: str,
    project_root: Path,
    run_number: int,
) -> InvestigationRunResult:

    case_path = (
        project_root
        / "benchmark"
        / "cases"
        / f"{case_id}.json"
    )

    case = load_case(str(case_path))

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


def print_suite_results(
    results: list[InvestigationRunResult],
    requested_cases: int,
    failed_cases: int,
) -> None:

    print("\nBenchmark Suite")
    print("===============")

    print(
        f"Requested runs: {requested_cases}"
    )

    print(
        f"Completed runs: {len(results)}"
    )

    print(
        f"Failed runs: {failed_cases}"
    )

    print()

    print(
        f"{'CASE':30}"
        f"{'RESOLVED':12}"
        f"{'CORRECT':12}"
        f"{'EXPERIMENTS':12}"
    )

    print("-" * 66)

    for result in results:
        print(
            f"{result.case_id:30}"
            f"{str(result.resolved):12}"
            f"{str(result.root_cause_correct):12}"
            f"{result.experiment_count:<12}"
        )

    print("\nTrajectories")
    print("------------")

    for result in results:
        print(
            f"{result.case_id}: "
            f"{' -> '.join(result.selected_experiments)}"
        )


def main() -> None:

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--suite",
        default="benchmark/suite.json",
        help="Path to benchmark suite JSON.",
    )

    parser.add_argument(
        "--runs-per-case",
        type=int,
        default=1,
        help="Number of Gemini runs per case.",
    )

    args = parser.parse_args()

    if args.runs_per_case <= 0:
        raise ValueError(
            "--runs-per-case must be greater than zero"
        )

    project_root = (
        Path(__file__).resolve().parents[1]
    )

    suite_path = Path(
        args.suite
    )

    if not suite_path.is_absolute():
        suite_path = (
            project_root
            / suite_path
        )

    case_ids = load_suite(
        str(suite_path)
    )

    results: list[
        InvestigationRunResult
    ] = []

    failed_cases = 0

    total_requested_runs = (
        len(case_ids)
        * args.runs_per_case
    )

    for case_id in case_ids:

        for run_number in range(
            1,
            args.runs_per_case + 1,
        ):

            print(
                f"\n===== "
                f"{case_id} "
                f"RUN {run_number}/"
                f"{args.runs_per_case} "
                f"====="
            )

            try:
                result = run_case(
                    case_id=case_id,
                    project_root=project_root,
                    run_number=run_number,
                )

            except Exception as exc:

                failed_cases += 1

                print(
                    f"FAILED: "
                    f"{type(exc).__name__}: {exc}"
                )

                continue

            results.append(result)


    suite_result = SuiteEvaluator().evaluate(
        results=results,
        requested_cases=total_requested_runs,
        failed_cases=failed_cases,
    )    

    print_suite_results(
        results=list(suite_result.results),
        requested_cases=suite_result.requested_cases,
        failed_cases=suite_result.failed_cases,
    )


if __name__ == "__main__":
    main()