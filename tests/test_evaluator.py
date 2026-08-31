from investigator.benchmark.evaluator import BenchmarkEvaluator
from investigator.benchmark.models import BenchmarkCase, BenchmarkHypothesis
from investigator.domain.models import (
    Experiment,
    ExperimentResult,
    ExperimentStatus,
    Hypothesis,
    Investigation,
    InvestigationStatus,
)


def test_evaluator_identifies_correct_root_cause() -> None:
    case = BenchmarkCase(
        case_id="test",
        problem="Something failed.",
        repository_path=".",
        root_cause_hypothesis_id="H1",
        root_cause_description="Preprocessing regression",
        expected_reproduction=True,
        hypotheses=[
            BenchmarkHypothesis(
                hypothesis_id="H1",
                description="Preprocessing",
                initial_confidence=0.3,
            ),
            BenchmarkHypothesis(
                hypothesis_id="H2",
                description="Data shift",
                initial_confidence=0.7,
            ),
        ],
        capabilities=[
            "EXP-GIT-DIFF",
            "EXP-PREPROCESS-COMPARE",
            "EXP-REPRODUCE",
        ],
    )

    investigation = Investigation(
        investigation_id="INV-001",
        problem="Something failed.",
        status=InvestigationStatus.RESOLVED,
        hypotheses=[
            Hypothesis(
                hypothesis_id="H1",
                description="Preprocessing",
                confidence=0.9,
            ),
            Hypothesis(
                hypothesis_id="H2",
                description="Data shift",
                confidence=0.1,
            ),
        ],
        experiments=[
            Experiment(
                experiment_id="EXP-1",
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
                experiment_id="EXP-1",
                status=ExperimentStatus.SUCCEEDED,
                observations=[
                    "reproduction=PASS"
                ],
            )
        ],
    )

    evaluator = BenchmarkEvaluator()

    result = evaluator.evaluate(
        case,
        investigation,
    )

    assert result.root_cause_correct is True
    assert result.reproduction_success is True
    assert result.experiment_count == 1
    assert result.final_confidence == 0.9
    assert result.resolved is True