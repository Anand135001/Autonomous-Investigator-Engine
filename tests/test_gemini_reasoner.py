from investigator.domain.models import (
    Evidence,
    Hypothesis,
    Investigation,
)
from investigator.reasoning.gemini import GeminiReasoner
from investigator.planning.default_capabilities import build_default_registry


def test_prompt_contains_investigation_state() -> None:
    investigation = Investigation(
        investigation_id="INV-001",
        problem="Validation accuracy dropped.",
        hypotheses=[
            Hypothesis(
                hypothesis_id="H1",
                description="Preprocessing regression",
                confidence=0.4,
            )
        ],
        evidence=[
            Evidence(
                evidence_id="E1",
                source="git",
                observation="preprocess.py changed",
            )
        ],
    )

    registry = build_default_registry()
    
    prompt = GeminiReasoner._build_prompt(
        investigation,
        registry.all()        
    )

    assert "Validation accuracy dropped." in prompt
    assert "H1" in prompt
    assert "Preprocessing regression" in prompt
    assert "preprocess.py changed" in prompt
    assert "EXP-GIT-DIFF" in prompt
