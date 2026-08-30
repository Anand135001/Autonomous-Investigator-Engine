from investigator.domain.models import (
    Evidence,
    Experiment,
    ExperimentResult,
    ExperimentStatus,
    Investigation,
)
from investigator.execution.executor import ExperimentExecutor
from investigator.investigation.beliefs import BeliefUpdater
from investigator.investigation.manager import InvestigationManager
from investigator.planning.generator import CandidateGenerator
from investigator.planning.planner import ExperimentPlanner
from investigator.reasoning.result_schema import ResultAssessment
from investigator.tools.git import inspect_git_history


MAX_EXPERIMENTS = 5


def candidate_to_experiment(candidate) -> Experiment:
    """Convert a planned candidate into an executable experiment."""

    return Experiment(
        experiment_id=candidate.experiment_id,
        purpose=candidate.purpose,
        target_hypothesis_id=(
            candidate.target_hypothesis_ids[0]
        ),
        rationale=candidate.rationale,
        estimated_cost=candidate.estimated_cost,
        timeout_seconds=candidate.timeout_seconds,
        risk_level=candidate.risk_level,
        allowed_tools=candidate.allowed_tools,
    )


def result_to_evidence(result: ExperimentResult) -> list[Evidence]:
    """Convert observations from an experiment into evidence."""

    evidence_items: list[Evidence] = []

    for index, observation in enumerate(
        result.observations,
        start=1,
    ):
        evidence_items.append(
            Evidence(
                evidence_id=(
                    f"{result.experiment_id}-E{index}"
                ),
                source="experiment",
                observation=observation,
                experiment_id=result.experiment_id,
                metadata={
                    "status": result.status.value,
                    "artifacts": result.artifacts,
                },
            )
        )

    return evidence_items


def should_resolve(
    result: ExperimentResult,
    assessment: ResultAssessment,
) -> bool:
    """Determine whether the investigation has enough evidence."""

    return (
        result.status == ExperimentStatus.SUCCEEDED
        and assessment.verification_sufficient
    )


def run_adaptive_investigation(
    manager: InvestigationManager,
    investigation: Investigation,
    repository_path: str,
    candidate_generator: CandidateGenerator,
    result_analyzer,
) -> Investigation:
    """
    Run the investigation loop.

    The caller provides the candidate generator and result analyzer,
    allowing deterministic and Gemini-backed implementations to use
    the same investigation engine.
    """

    manager.start(investigation)

    # Collect initial repository evidence.
    history_result = inspect_git_history(
        repository_path,
        limit=5,
    )

    manager.add_evidence(
        investigation,
        Evidence(
            evidence_id="E001",
            source="git",
            observation=(
                "Initial Git history inspection completed."
            ),
            metadata=history_result,
        ),
    )

    planner = ExperimentPlanner()
    executor = ExperimentExecutor()
    belief_updater = BeliefUpdater()

    for _ in range(MAX_EXPERIMENTS):

        candidates = candidate_generator.generate(
            investigation
        )

        if not candidates:
            manager.mark_inconclusive(
                investigation
            )
            break

        selected_candidate = (
            planner.select_next_experiment(
                candidates
            )
        )

        experiment = candidate_to_experiment(
            selected_candidate
        )

        manager.add_experiment(
            investigation,
            experiment,
        )

        result = executor.execute(
            experiment,
            repository_path,
        )

        manager.add_result(
            investigation,
            result,
        )

        evidence_items = result_to_evidence(
            result
        )

        for evidence in evidence_items:
            manager.add_evidence(
                investigation,
                evidence,
            )

        assessment = result_analyzer.analyze(
            investigation,
            result,
        )

        belief_updater.update(
            manager,
            investigation,
            assessment,
        )

        if should_resolve(
            result,
            assessment,
        ):
            manager.resolve(
                investigation
            )
            break

    return investigation