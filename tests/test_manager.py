import pytest

from investigator.domain.models import (
    Evidence,
    Experiment,
    ExperimentResult,
    ExperimentStatus,
    Hypothesis,
    InvestigationStatus,
)
from investigator.investigation.manager import InvestigationManager


@pytest.fixture
def manager() -> InvestigationManager:
    return InvestigationManager()


@pytest.fixture
def investigation(manager: InvestigationManager):
    return manager.create(
        investigation_id="INV-001",
        problem="Validation accuracy dropped.",
    )


def make_experiment(experiment_id: str = "EXP-001",) -> Experiment:
    return Experiment(
        experiment_id=experiment_id,
        purpose="Inspect preprocessing",
        target_hypothesis_id="H1",
        rationale="Determine whether preprocessing changed.",
        estimated_cost=1.0,
        timeout_seconds=60,
        risk_level="low",
    )


def test_create_investigation(manager: InvestigationManager,) -> None:
    investigation = manager.create(
        investigation_id="INV-001",
        problem="Something failed.",
    )

    assert investigation.investigation_id == "INV-001"
    assert investigation.status == InvestigationStatus.PENDING


def test_create_rejects_empty_values(manager: InvestigationManager,) -> None:
    with pytest.raises(ValueError):
        manager.create("", "Something failed.")

    with pytest.raises(ValueError):
        manager.create("INV-001", "")



def test_start_changes_status(manager: InvestigationManager, investigation,) -> None:
    manager.start(investigation)

    assert investigation.status == InvestigationStatus.RUNNING



def test_add_hypothesis(manager: InvestigationManager, investigation,) -> None:
    hypothesis = Hypothesis(
        hypothesis_id="H1",
        description="Preprocessing regression",
        confidence=0.3,
    )
    manager.add_hypothesis(investigation, hypothesis,)

    assert investigation.hypotheses == [hypothesis]


def test_duplicate_hypothesis_is_rejected(manager: InvestigationManager, investigation,) -> None:
    hypothesis = Hypothesis(
        hypothesis_id="H1",
        description="Preprocessing regression",
        confidence=0.3,
    )
    manager.add_hypothesis(investigation, hypothesis,)

    with pytest.raises(ValueError):
        manager.add_hypothesis(investigation, hypothesis,)



def test_add_evidence(manager: InvestigationManager, investigation,) -> None:
    evidence = Evidence(
        evidence_id="E1",
        source="git",
        observation="A preprocessing file changed.",
    )
    manager.add_evidence(investigation, evidence,)

    assert investigation.evidence == [evidence]



def test_add_experiment_and_result(manager: InvestigationManager, investigation,) -> None:
    experiment = make_experiment()

    manager.add_experiment(investigation, experiment,)
    result = ExperimentResult(
        experiment_id="EXP-001",
        status=ExperimentStatus.SUCCEEDED,
        observation=["Observed a preprocessing change."],
    )
    manager.add_result(investigation, result,)

    assert investigation.experiments == [experiment]
    assert investigation.results == [result]


def test_unknown_experiment_result_is_rejected(manager: InvestigationManager, investigation,) -> None:
    result = ExperimentResult(
        experiment_id="EXP-999",
        status=ExperimentStatus.SUCCEEDED,
    )

    with pytest.raises(ValueError):
        manager.add_result(investigation, result,)


def test_update_confidence(manager: InvestigationManager, investigation,) -> None:
    hypothesis = Hypothesis(hypothesis_id="H1", description="Preprocessing regression", confidence=0.3,)
    manager.add_hypothesis(investigation, hypothesis,)
    manager.update_hypothesis_confidence(investigation, "H1", 0.8,)

    assert investigation.hypotheses[0].confidence == 0.8


def test_finished_investigation_cannot_be_modified(manager: InvestigationManager, investigation,) -> None:
    manager.start(investigation)
    manager.resolve(investigation)

    with pytest.raises(ValueError):
        manager.add_evidence(
            investigation,
            Evidence(
                evidence_id="E1",
                source="test",
                observation="Late evidence",
            ),
        )