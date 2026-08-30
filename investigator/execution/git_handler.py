from investigator.domain.models import (
    Experiment,
    ExperimentResult,
    ExperimentStatus,
)
from investigator.tools.git import compare_git_revisions


class GitDiffHandler:
    """Execute Git-based experiment capabilities."""

    def execute(
        self,
        experiment: Experiment,
        repository_path: str,
    ) -> ExperimentResult:

        result = compare_git_revisions(
            repository_path,
            "HEAD~1",
            "HEAD",
        )

        return ExperimentResult(
            experiment_id=experiment.experiment_id,
            status=ExperimentStatus.SUCCEEDED,
            observations=[
                result["diff_stat"].strip(),
            ],
            artifacts=[],
        )