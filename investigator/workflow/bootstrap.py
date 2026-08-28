from investigator.investigation.manager import InvestigationManager
from investigator.tools.git import inspect_git_history, compare_git_revisions
from investigator.investigation.evidence import build_git_history_evidence 

from investigator.domain.models import(
    Experiment,
    ExperimentResult,
    ExperimentStatus,
    Hypothesis,
    Investigation,
    Evidence,
)

from investigator.planning.candidates import DeterministicCandidateGenerator
from investigator.planning.planner import ExperimentPlanner
from investigator.execution.executor import ExperimentExecutor
from investigator.planning.generator import CandidateGenerator
from investigator.investigation.beliefs import BeliefUpdater

MAX_EXPERIMENTS = 5

def run_initial_investigation(manager: InvestigationManager, repository_path: str,) -> Investigation:
    """
    Run the first deterministic investigation workflow.

    right now This is not an AI agent yet.
    It exists to prove that our investigation state machinery works end-to-end.
    """

    investigation = manager.create(
        investigation_id="INV-001",
        problem="Validation accuracy dropped unexpectedly.",
    )

    manager.add_hypothesis(
        investigation,
        Hypothesis(
            hypothesis_id="H1",
            description="Preprocessing regression",
            confidence=0.31,
        ),
    )

    manager.add_hypothesis(
        investigation,
        Hypothesis(
            hypothesis_id="H2",
            description="Dataset distribution shift",
            confidence=0.26,
        ),
    )

    manager.add_hypothesis(
        investigation,
        Hypothesis(
            hypothesis_id="H3",
            description="Learning-rate/configuration issue",
            confidence=0.21,
        ),
    )

    manager.add_hypothesis(
        investigation,
        Hypothesis(
            hypothesis_id="H4",
            description="Label corruption",
            confidence=0.12,
        ),
    )

    manager.add_hypothesis(
        investigation,
        Hypothesis(
            hypothesis_id="H5",
            description="Model implementation regression",
            confidence=0.10,
        ),
    )

    manager.start(investigation)

    # Collect Observation
    git_result = inspect_git_history(
        repository_path,
        limit=5,
    )

    # Collect evidence
    evidence = build_git_history_evidence(
        evidence_id="E001",
        result=git_result,
    )

    # Store Evidence
    manager.add_evidence(
        investigation,
        evidence,
    )

    # Update confidence
    manager.update_hypothesis_confidence(
        investigation,
        hypothesis_id="H1",
        confidence=0.45,
    )


    remaining_hypotheses = [
        hypothesis
        for hypothesis in investigation.hypotheses
        if hypothesis.hypothesis_id != "H1"
    ]

    remaining_total = sum(
        hypothesis.confidence
        for hypothesis in remaining_hypotheses
    )

    remaining_probability = 1.0 - 0.45

    for hypothesis in remaining_hypotheses:
        updated_confidence = (
            hypothesis.confidence
            / remaining_total
            * remaining_probability
        )

        manager.update_hypothesis_confidence(
            investigation,
            hypothesis_id=hypothesis.hypothesis_id,
            confidence=updated_confidence,
        )
    

    return investigation


def candidate_to_experiment(candidate) -> Experiment:
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


def update_deterministic_beliefs(
    manager: InvestigationManager,
    investigation: Investigation,
    experiment: Experiment,
    result: ExperimentResult,
) -> None:

    if result.status != ExperimentStatus.SUCCEEDED:
        return

    confidence_by_experiment = {
        "EXP-GIT-DIFF": 0.45,
        "EXP-PREPROCESS-COMPARE": 0.82,
        "EXP-REPRODUCE": 0.96,
    }

    new_confidence = confidence_by_experiment.get(experiment.experiment_id)

    if new_confidence is None:
        return

    manager.update_hypothesis_confidence(investigation, "H1", new_confidence)

    others = [
        hypothesis
        for hypothesis in investigation.hypotheses
        if hypothesis.hypothesis_id != "H1"
    ]

    old_remaining_total = sum(
        hypothesis.confidence
        for hypothesis in others
    )

    new_remaining_total = 1.0 - new_confidence

    for hypothesis in others:
        manager.update_hypothesis_confidence(
            investigation,
            hypothesis.hypothesis_id,
            (
                hypothesis.confidence
                / old_remaining_total
                * new_remaining_total
            ),
        )


def should_resolve(experiment: Experiment, result: ExperimentResult) -> bool:

    return (
        experiment.experiment_id == "EXP-REPRODUCE"
        and result.status == ExperimentStatus.SUCCEEDED
        and any(
            "reproduction=PASS" in observation
            for observation in result.observations
        )
    )


def run_adaptive_investigation(
        manager: InvestigationManager,
        repository_path: str,
        candidate_generator: CandidateGenerator,
        result_analyzer,
        investigation: Investigation,
        ) -> Investigation:

    manager.start(investigation)

    # Initial evidence collection.
    history_result = inspect_git_history(repository_path, limit=5)

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

        candidates = candidate_generator.generate(investigation)

        print("\nGemini candidates:")

        for candidate in candidates:
            print(f"  {candidate.experiment_id}:{candidate.purpose}")
        
            print(f"    information_gain={candidate.expected_information_gain:.2f}")
        
            print(f"   coverage={candidate.hypothesis_coverage:.2f}")
        
            print(f"   cost={candidate.estimated_cost:.2f}")
        
            print(f"   risk={candidate.risk_level}")
        
        if not candidates:
            manager.mark_inconclusive(investigation)
            break

        selected_candidate = (planner.select_next_experiment(candidates))

        print(
            f"\nSelected experiment: "
            f"{selected_candidate.experiment_id}"
        )
        
        print(
            f"Reason: "
            f"{selected_candidate.rationale}"
        )

        experiment = candidate_to_experiment(selected_candidate)

        manager.add_experiment(investigation, experiment)

        result = executor.execute(experiment, repository_path)

        assessment = result_analyzer.analyze(investigation, result)
        
        belief_updater.update(
            manager,
            investigation,
            assessment,
        )
        
        manager.add_result(investigation, result)

        for evidence in result_to_evidence(result):
            manager.add_evidence(
                investigation,
                evidence,
            )

        update_deterministic_beliefs(
            manager,
            investigation,
            experiment,
            result,
        )

        if should_resolve(experiment, result):
            manager.resolve(investigation)
            break

    return investigation