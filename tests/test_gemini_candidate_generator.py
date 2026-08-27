from investigator.domain.models import Evidence, Hypothesis, Investigation
from investigator.reasoning.candidate_generator import GeminiCandidateGenerator
from investigator.reasoning.schemas import ExperimentProposal, ProposedExperiment
from investigator.planning.default_capabilities import build_default_registry

class FakeGeminiReasoner:
    """Fake reasoner used to test conversion logic."""

    def __init__(self, proposal: ExperimentProposal) -> None:
        self.proposal = proposal

    def propose_experiments(self, investigation: Investigation, capabilities) -> ExperimentProposal:
        return self.proposal


def make_investigation() -> Investigation:
    return Investigation(
        investigation_id="INV-001",
        problem="Validation accuracy dropped.",
        hypotheses=[
            Hypothesis(
                hypothesis_id="H1",
                description="Preprocessing regression",
                confidence=0.4,
            ),
            Hypothesis(
                hypothesis_id="H2",
                description="Dataset shift",
                confidence=0.3,
            ),
        ],
        evidence=[
            Evidence(
                evidence_id="E1",
                source="git",
                observation="preprocess.py changed",
            )
        ],
    )


def make_proposal(experiment_id: str, hypothesis_ids: list[str]) -> ProposedExperiment:

    return ProposedExperiment(
        experiment_id=experiment_id,
        purpose="Test a hypothesis.",
        target_hypothesis_ids=hypothesis_ids,
        rationale="This could reduce uncertainty.",
        expected_information_gain=0.8,
        hypothesis_coverage=0.8,
        estimated_cost=1.0,
        risk_level="low",
        timeout_seconds=30,
        allowed_tools=["git"],
    )


def test_gemini_candidates_are_converted() -> None:
    proposal = ExperimentProposal(
        candidates=[
            make_proposal(
                "EXP-GIT-DIFF",
                ["H1"],
            )
        ]
    )

    registry = build_default_registry()

    generator = GeminiCandidateGenerator(
        reasoner=FakeGeminiReasoner(proposal),
        capabilities=registry.all()
        )

    candidates = generator.generate(make_investigation())

    assert len(candidates) == 1

    candidate = candidates[0]

    assert candidate.experiment_id == "EXP-GIT-DIFF"
    assert candidate.target_hypothesis_ids == ["H1"]


def test_completed_experiment_is_filtered() -> None:
    investigation = make_investigation()

    # Pretend EXP-GIT-DIFF has already been executed.
    from investigator.domain.models import Experiment

    investigation.experiments.append(
        Experiment(
            experiment_id="EXP-GIT-DIFF",
            purpose="Already performed.",
            target_hypothesis_id="H1",
            rationale="Already done.",
            estimated_cost=1.0,
            timeout_seconds=30,
            risk_level="low",
        )
    )

    proposal = ExperimentProposal(
        candidates=[
            make_proposal(
                "EXP-GIT-DIFF",
                ["H1"],
            ),
            ProposedExperiment(
                experiment_id="EXP-PREPROCESS-COMPARE",
                purpose="Test a hypothesis.",
                target_hypothesis_ids=["H1"],
                rationale="This could reduce uncertainty.",
                expected_information_gain=0.8,
                hypothesis_coverage=0.8,
                estimated_cost=1.0,
                risk_level="low",
                timeout_seconds=30,
                allowed_tools=["filesystem"],
            ),
        ]
    )

    registry =  build_default_registry()
    
    generator = GeminiCandidateGenerator(
        reasoner=FakeGeminiReasoner(proposal),
        capabilities=registry.all()
        )

    candidates = generator.generate(investigation)

    assert [
        candidate.experiment_id
        for candidate in candidates
    ] == ["EXP-PREPROCESS-COMPARE"]


def test_unknown_hypothesis_is_filtered() -> None:
    proposal = ExperimentProposal(
        candidates=[
            make_proposal(
                "EXP-001",
                ["H99"],
            )
        ]
    )

    registry = build_default_registry()

    generator = GeminiCandidateGenerator(
        reasoner=FakeGeminiReasoner(proposal),
        capabilities=registry.all()
        )

    candidates = generator.generate(make_investigation())

    assert candidates == []



def test_unknown_capability_is_filtered() -> None:
    proposal = ExperimentProposal(
        candidates=[
            make_proposal(
                "EXP-NONEXISTENT",
                ["H1"],
            )
        ]
    )

    registry = build_default_registry()

    generator = GeminiCandidateGenerator(
        reasoner=FakeGeminiReasoner(proposal),
        capabilities=registry.all(),
    )

    candidates = generator.generate(
        make_investigation()
    )

    assert candidates == []


def test_unsupported_tool_is_filtered() -> None:
    proposed = make_proposal(
        "EXP-GIT-DIFF",
        ["H1"],
    )

    proposed.allowed_tools = [
        "git",
        "shell",
    ]

    proposal = ExperimentProposal(candidates=[proposed])

    registry = build_default_registry()

    generator = GeminiCandidateGenerator(
        reasoner=FakeGeminiReasoner(proposal),
        capabilities=registry.all(),
    )

    candidates = generator.generate(make_investigation())

    assert candidates == []


def test_unknown_capability_is_filtered() -> None:
    proposal = ExperimentProposal(
        candidates=[
            make_proposal(
                "EXP-NONEXISTENT",
                ["H1"],
            )
        ]
    )

    registry = build_default_registry()

    generator = GeminiCandidateGenerator(
        reasoner=FakeGeminiReasoner(proposal),
        capabilities=registry.all(),
    )

    candidates = generator.generate(make_investigation())

    assert candidates == []


def test_unsupported_tool_is_filtered() -> None:
    proposed = make_proposal(
        "EXP-GIT-DIFF",
        ["H1"],
    )

    proposed.allowed_tools = [
        "git",
        "shell",
    ]

    proposal = ExperimentProposal(candidates=[proposed])

    registry = build_default_registry()

    generator = GeminiCandidateGenerator(
        reasoner=FakeGeminiReasoner(proposal),
        capabilities=registry.all(),
    )

    candidates = generator.generate(make_investigation())

    assert candidates == []
