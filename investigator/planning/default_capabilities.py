from investigator.domain.models import ExperimentCapability
from investigator.planning.capabilities import CapabilityRegistry


def build_default_registry() -> CapabilityRegistry:
    registry = CapabilityRegistry()

    registry.register(
        ExperimentCapability(
            capability_id="EXP-GIT-DIFF",
            name="Git revision comparison",
            description=("Compare the latest two Git revisions and identify changed files."),
            target_hypothesis_types=[
                "preprocessing",
                "model_implementation",
            ],
            allowed_tools=["git"],
            risk_level="low",
            timeout_seconds=30,
            estimated_cost=1.0,
            expected_outputs=["diff_stat"],
        )
    )

    registry.register(
        ExperimentCapability(
            capability_id="EXP-PREPROCESS-COMPARE",
            name="Preprocessing distribution comparison",
            description=("Compare preprocessing statistics from known-good and current runs."),
            target_hypothesis_types=["preprocessing"],
            allowed_tools=["filesystem"],
            risk_level="low",
            timeout_seconds=30,
            estimated_cost=1.5,
            expected_outputs=[
                "known_good_statistics",
                "current_statistics",
            ],
        )
    )

    registry.register(
        ExperimentCapability(
            capability_id="EXP-REPRODUCE",
            name="Preprocessing reproduction",
            description=("Reproduce model performance using known-good preprocessing."),
            target_hypothesis_types=["preprocessing"],
            allowed_tools=["python"],
            risk_level="low",
            timeout_seconds=60,
            estimated_cost=3.0,
            expected_outputs=[
                "accuracy_comparison",
                "reproduction_status",
            ],
        )
    )

    return registry