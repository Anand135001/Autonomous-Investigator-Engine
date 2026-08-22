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

from investigator.planning.candidates import CandidateGenerator
from investigator.planning.planner import ExperimentPlanner


def run_initial_investigation( manager: InvestigationManager, repository_path: str,) -> Investigation:
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



def run_adaptive_investigation(manager: InvestigationManager, repository_path: str,) -> Investigation:
    """
    Run one complete deterministic adaptive investigation step.

    Gemini is intentionally not involved yet.
    """

    investigation = manager.create(
        investigation_id="INV-002",
        problem="Validation accuracy dropped unexpectedly.",
    )

    hypotheses = [
        Hypothesis(
            hypothesis_id="H1",
            description="Preprocessing regression",
            confidence=0.31,
        ),
        Hypothesis(
            hypothesis_id="H2",
            description="Dataset distribution shift",
            confidence=0.26,
        ),
        Hypothesis(
            hypothesis_id="H3",
            description="Learning-rate/configuration issue",
            confidence=0.21,
        ),
        Hypothesis(
            hypothesis_id="H4",
            description="Label corruption",
            confidence=0.12,
        ),
        Hypothesis(
            hypothesis_id="H5",
            description="Model implementation regression",
            confidence=0.10,
        ),
    ]

    for hypothesis in hypotheses:
        manager.add_hypothesis(
            investigation,
            hypothesis,
        )

    manager.start(investigation)

    history_result = inspect_git_history(
        repository_path,
        limit=5,
    )

    history_evidence = build_git_history_evidence(
        evidence_id="E001",
        result=history_result,
    )

    manager.add_evidence(
        investigation,
        history_evidence,
    )

    candidate_generator = CandidateGenerator()
    planner = ExperimentPlanner()

    candidates = candidate_generator.generate(
        investigation,
    )

    selected_candidate = planner.select_next_experiment(
        candidates,
    )

    experiment = Experiment(
        experiment_id=selected_candidate.experiment_id,
        purpose=selected_candidate.purpose,
        target_hypothesis_id=(
            selected_candidate.target_hypothesis_ids[0]
        ),
        rationale=selected_candidate.rationale,
        estimated_cost=selected_candidate.estimated_cost,
        timeout_seconds=selected_candidate.timeout_seconds,
        risk_level=selected_candidate.risk_level,
        allowed_tools=selected_candidate.allowed_tools,
    )

    manager.add_experiment(
        investigation,
        experiment,
    )

    diff_result = compare_git_revisions(
        repository_path,
        "HEAD~1",
        "HEAD",
    )

    experiment_result = ExperimentResult(
        experiment_id=experiment.experiment_id,
        status=ExperimentStatus.SUCCEEDED,
        observations=[
            diff_result["diff_stat"].strip(),
        ],
    )

    manager.add_result(
        investigation,
        experiment_result,
    )

    manager.add_evidence(
        investigation,
        Evidence(
            evidence_id="E002",
            source="git",
            observation=(
                "Compared the most recent two revisions "
                "to identify changed files."
            ),
            experiment_id=experiment.experiment_id,
            metadata=diff_result,
        ),
    )

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
        manager.update_hypothesis_confidence(
            investigation,
            hypothesis_id=hypothesis.hypothesis_id,
            confidence=(
                hypothesis.confidence / remaining_total * remaining_probability
            ),
        )

    return investigation