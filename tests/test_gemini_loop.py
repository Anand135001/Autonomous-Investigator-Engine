from investigator.domain.models import Investigation
from investigator.investigation.manager import InvestigationManager
from investigator.planning.default_capabilities import build_default_registry
from investigator.reasoning.candidate_generator import GeminiCandidateGenerator
from investigator.reasoning.schemas import ExperimentProposal, ProposedExperiment
from investigator.workflow.bootstrap import run_adaptive_investigation


class FakeReasoner:
    def __init__(self) -> None:
        self.call_count = 0

    def propose_experiments(self, investigation: Investigation, capabilities) -> ExperimentProposal:

        self.call_count += 1

        if self.call_count == 1:
            experiment_id = "EXP-GIT-DIFF"

        elif self.call_count == 2:
            experiment_id = ("EXP-PREPROCESS-COMPARE")

        else:
            experiment_id = "EXP-REPRODUCE"

        experiment = ProposedExperiment(
            experiment_id=experiment_id,
            purpose=f"Run {experiment_id}",
            target_hypothesis_ids=["H1"],
            rationale="Fake reasoning for testing.",
            expected_information_gain=0.9,
            hypothesis_coverage=0.9,
            estimated_cost=1.0,
            risk_level="low",
            timeout_seconds=60,
            allowed_tools=["git"]
            if experiment_id == "EXP-GIT-DIFF"
            else (
                ["filesystem"]
                if experiment_id
                == "EXP-PREPROCESS-COMPARE"
                else ["python"]
            ),
        )

        return ExperimentProposal(
            candidates=[experiment]
        )


    def test_gemini_candidate_generator_can_drive_repeated_loop(tmp_path) -> None:

        import subprocess
    
        subprocess.run(
            ["git", "init"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
        )
    
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            check=True,
        )
    
        subprocess.run(
            [
                "git",
                "config",
                "user.email",
                "test@example.com",
            ],
            cwd=tmp_path,
            check=True,
        )
    
        file_path = tmp_path / "preprocess.py"
    
        file_path.write_text(
            "version_1\n",
            encoding="utf-8",
        )
    
        subprocess.run(
            ["git", "add", "."],
            cwd=tmp_path,
            check=True,
        )
    
        subprocess.run(
            ["git", "commit", "-m", "initial"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
        )
    
        file_path.write_text(
            "version_2\n",
            encoding="utf-8",
        )
    
        subprocess.run(
            ["git", "add", "."],
            cwd=tmp_path,
            check=True,
        )
    
        subprocess.run(
            ["git", "commit", "-m", "change preprocessing"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
        )
    
        reasoner = FakeReasoner()
    
        registry = build_default_registry()
    
        generator = GeminiCandidateGenerator(
            reasoner=reasoner,
            capabilities=registry.all(),
        )
    
        manager = InvestigationManager()
    
        investigation = run_adaptive_investigation(
            manager=manager,
            repository_path=str(tmp_path),
            candidate_generator=generator,
        )
    
        experiment_ids = [
            experiment.experiment_id
            for experiment in investigation.experiments
        ]
    
        assert experiment_ids == [
            "EXP-GIT-DIFF",
            "EXP-PREPROCESS-COMPARE",
            "EXP-REPRODUCE",
        ]
    
        assert (reasoner.call_count == 3)