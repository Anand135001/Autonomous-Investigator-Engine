from investigator.domain.models import Hypothesis, Investigation
from investigator.investigation.manager import InvestigationManager
from investigator.tools.git import inspect_git_history
from investigator.investigation.evidence import build_git_history_evidence 


def run_initial_investigation( manager: InvestigationManager, repository_path: str,  
) -> Investigation:

    """
    Run the first deterministic investigation workflow.

    right now This is not an AI agent yet.
    It exists to prove that our investigation state machinery
    works end-to-end.
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