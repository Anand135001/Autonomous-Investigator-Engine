from investigator.benchmark.models import (
    BenchmarkCase,
    BenchmarkHypothesis,
)
from investigator.domain.models import (
    Experiment,
    ExperimentResult,
    ExperimentStatus,
    Hypothesis,
    Investigation,
    InvestigationStatus,
)
from investigator.evaluation.evaluator import InvestigationRunEvaluator


def test_evaluate_successful_run() -> None:

    case = BenchmarkCase(
        case_id="test-case",
        problem="Something failed.",
        repository_path=".",
        root_cause_hypothesis_id="H1",
        root_cause_description="Cause A",
        expected_reproduction=True,
        capabilities=["EXP-001"],
        hypotheses=[
            BenchmarkHypothesis(
                hypothesis_id="H1",
                description="Cause A",
                initial_confidence=0.5,
            ),
            BenchmarkHypothesis(
                hypothesis_id="H2",
                description="Cause B",
                initial_confidence=0.5,
            ),
        ],
    )

    investigation = Investigation(
        investigation_id="INV-001",
        problem="Something failed.",
        status=InvestigationStatus.RESOLVED,
        hypotheses=[
            Hypothesis(
                hypothesis_id="H1",
                description="Cause A",
                confidence=0.9,
            ),
            Hypothesis(
                hypothesis_id="H2",
                description="Cause B",
                confidence=0.1,
            ),
        ],
        experiments=[
            Experiment(
                experiment_id="EXP-001",
                purpose="Test",
                target_hypothesis_id="H1",
                rationale="Test",
                estimated_cost=1.0,
                timeout_seconds=30,
                risk_level="low",
            )
        ],
        results=[
            ExperimentResult(
                experiment_id="EXP-001",
                status=ExperimentStatus.SUCCEEDED,
                observations=[
                    "reproduction=PASS"
                ],
            )
        ],
    )

    evaluator = InvestigationRunEvaluator()

    result = evaluator.evaluate(
        run_number=1,
        case=case,
        investigation=investigation,
        usage=[],
    )

    assert result.resolved is True
    assert result.root_cause_correct is True
    assert result.reproduction_success is True
    assert result.experiment_count == 1
    assert result.final_confidence == 0.9
    assert result.selected_experiments == (
        "EXP-001",
    )