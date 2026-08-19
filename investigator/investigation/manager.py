from investigator.domain.models import (
    Hypothesis,
    Evidence,
    Experiment,
    ExperimentResult,
    Investigation,
    InvestigationStatus,
)

# I will use manager to enforce rules
class InvestigationManager:
    """Provide controlled state-changing operations for investigations."""

    def create(self, investigation_id: str, problem: str,) -> Investigation:
        if not investigation_id.strip():
            raise ValueError("investigation_id cannot be empty")

        if not problem.strip():
            raise ValueError("problem cannot be empty")

        return Investigation(
            investigation_id=investigation_id,
            problem=problem,
        )

    

    # Add a Hypothesis to an Investigation
    def add_hypothesis(self, investigation: Investigation, hypothesis: Hypothesis) -> None:
        self._ensure_not_finished(investigation)

        # Every hypothesis ID must be unique
        if any(
            existing.hypothesis_id == hypothesis.hypothesis_id
            for existing in investigation.hypotheses
        ):
            raise ValueError(f"Hypothesis already exits:" f"{hypothesis.hypothesis_id}")

        investigation.hypotheses.append(hypothesis)



    # Add a Evidence to an Investigation
    def add_evidence(self, investigation: Investigation, evidence: Evidence) -> None:
        self._ensure_not_finished(investigation)
        if any(
            existing.evidence_id == evidence.evidence_id
            for existing in investigation.evidence
        ):
            raise ValueError(
                f"Evidence already exists: "
                f"{evidence.evidence_id}"
            )

        investigation.evidence.append(evidence)



    # Add a experiment to an Investigation 
    def add_experiment(self, investigation: Investigation, experiment: Experiment) -> None:
        self._ensure_not_finished(investigation)

        if any(
            existing.experiment_id == experiment.experiment_id
            for existing in investigation.experiments
        ):
            raise ValueError(
                f"Experiment already exists: "
                f"{experiment.experiment_id}"
            )

        investigation.experiments.append(experiment)



    # Add a result to an Investigation, result must belong to an existing experiment
    def add_result(self, investigation: Investigation, result: ExperimentResult) -> None:
        self._ensure_not_finished(investigation)

        experiment_ids = {
            experiment.experiment_id
            for experiment in investigation.experiments
        }
        
        if result.experiment_id not in experiment_ids:
            raise ValueError(
                "Cannot record a result for an unknown experiment: "
                f"{result.experiment_id}"
            )

        existing_result_ids = {
            existing.experiment_id
            for existing in investigation.results
        }

        if result.experiment_id in existing_result_ids:
            raise ValueError(
                "A result already exists for experiment: "
                f"{result.experiment_id}"
            )

        investigation.results.append(result)



    # changes the confidence of an existing hypothesis.
    def update_hypothesis_confidence(self, investigation: Investigation, hypothesis_id: str, confidence: float) -> None:
        self._ensure_not_finished(investigation)

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        for hypothesis in investigation.hypotheses:
            if hypothesis.hypothesis_id == hypothesis_id:
                hypothesis.confidence = confidence
                return

        raise ValueError(
            f"Unknown hypothesis: {hypothesis_id}"
        )



    #  manager controls the investigation's lifecycle 
    def start(self, investigation: Investigation, ) -> None:
        if investigation.status != InvestigationStatus.PENDING:
            raise ValueError(
                "Only pending investigations can be started"
            )

        investigation.status = InvestigationStatus.RUNNING


    def resolve(self, investigation: Investigation,) -> None:
        if investigation.status != InvestigationStatus.RUNNING:
            raise ValueError(
                "Only running investigations can be resolved"
            )

        investigation.status = InvestigationStatus.RESOLVED


    # Only a running investigation can become inconclusive
    def mark_inconclusive(self, investigation: Investigation) -> None:
        if investigation.status != InvestigationStatus.RUNNING:
            raise ValueError(
                "Only running investigations can become inconclusive"
            )

        investigation.status = InvestigationStatus.INCONCLUSIVE   


    # A resolved investigation cannot later become failed
    def fail(self, investigation: Investigation) -> None:
        if investigation.status == InvestigationStatus.RESOLVED:
            raise ValueError(
                "A resolved investigation cannot be marked failed"
            )

        investigation.status = InvestigationStatus.FAILED


    @staticmethod
    def _ensure_not_finished( investigation: Investigation ) -> None:
        finished_states = {
            InvestigationStatus.RESOLVED,
            InvestigationStatus.INCONCLUSIVE,
            InvestigationStatus.FAILED,
        }
        
        if investigation.status in finished_states:
            raise ValueError(
                "Cannot modify a finished investigation"
            )