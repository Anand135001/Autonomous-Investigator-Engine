from investigator.domain.models import Investigation
from investigator.investigation.manager import InvestigationManager
from investigator.reasoning.result_schema import ResultAssessment


class BeliefUpdater:
    """Apply a validated Gemini result assessment."""

    def update(
        self,
        manager: InvestigationManager,
        investigation: Investigation,
        assessment: ResultAssessment,
    ) -> None:

        known_ids = {
            hypothesis.hypothesis_id
            for hypothesis in investigation.hypotheses
        }

        assessment_ids = {
            item.hypothesis_id
            for item in assessment.assessments
        }

        if known_ids != assessment_ids:
            raise ValueError(
                "Gemini must assess every known hypothesis "
                "exactly once."
            )

        total = sum(
            item.new_confidence
            for item in assessment.assessments
        )

        if total <= 0:
            raise ValueError("Confidence total must be greater than zero.")

        normalized = {
            item.hypothesis_id: (
                item.new_confidence / total
            )
            for item in assessment.assessments
        }

        for hypothesis_id, confidence in normalized.items():
            manager.update_hypothesis_confidence(
                investigation,
                hypothesis_id,
                confidence,
            )