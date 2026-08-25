from investigator.domain.models import Hypothesis, Investigation
from investigator.planning.candidates import DeterministicCandidateGenerator


def test_candidate_generator_creates_git_diff_candidate() -> None:
    investigation = Investigation(
        investigation_id="INV-001",
        problem="Validation accuracy dropped.",
        hypotheses=[
            Hypothesis(
                hypothesis_id="H1",
                description="Preprocessing regression",
                confidence=0.45,
            ),
            Hypothesis(
                hypothesis_id="H2",
                description="Dataset shift",
                confidence=0.20,
            ),
            Hypothesis(
                hypothesis_id="H5",
                description="Model regression",
                confidence=0.15,
            ),
        ],
    )

    generator = DeterministicCandidateGenerator()

    candidates = generator.generate(investigation)

    assert len(candidates) == 1
    assert candidates[0].experiment_id == "EXP-GIT-DIFF"
    assert set(candidates[0].target_hypothesis_ids) == {
        "H1",
        "H5",
    }