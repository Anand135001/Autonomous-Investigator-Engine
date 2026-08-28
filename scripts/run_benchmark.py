from pathlib import Path

from investigator.benchmark.runner import run_benchmark


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]

    result = run_benchmark(
        case_path=str(
            project_root
            / "benchmark"
            / "cases"
            / "preprocessing_regression.json"
        ),
        repository_path=str(project_root),
    )

    print("\nBenchmark Result")
    print("----------------")

    print(
        f"Case: "
        f"{result.case_id}"
    )

    print(
        f"Root cause correct: "
        f"{result.root_cause_correct}"
    )

    print(
        f"Reproduction success: "
        f"{result.reproduction_success}"
    )

    print(
        f"Experiments: "
        f"{result.experiment_count}"
    )

    print(
        f"Repeated experiments: "
        f"{result.repeated_experiments}"
    )

    print(
        f"Human interventions: "
        f"{result.human_interventions}"
    )

    print(
        f"Final confidence: "
        f"{result.final_confidence:.2%}"
    )

    print(
        f"Resolved: "
        f"{result.resolved}"
    )


if __name__ == "__main__":
    main()