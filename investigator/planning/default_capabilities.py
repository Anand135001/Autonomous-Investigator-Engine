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

    registry.register(
        ExperimentCapability(
            capability_id="PERF-CODE-DIFF",
            name="Deployment code comparison",
            description=(
                "Inspect source changes associated with the "
                "deployment and identify suspicious performance-related changes."
            ),
            target_hypothesis_types=[
                "database",
                "application_code",
                "performance",
            ],
            allowed_tools=["git"],
            risk_level="low",
            timeout_seconds=30,
            estimated_cost=1.0,
            expected_outputs=[
                "changed_files",
                "performance_related_changes",
            ],
        )
    )
    
    registry.register(
        ExperimentCapability(
            capability_id="PERF-QUERY-PROFILE",
            name="Database query profile comparison",
            description=(
                "Compare baseline and regressed database query counts "
                "and execution time."
            ),
            target_hypothesis_types=[
                "database",
                "performance",
            ],
            allowed_tools=["filesystem"],
            risk_level="low",
            timeout_seconds=30,
            estimated_cost=1.5,
            expected_outputs=[
                "query_count",
                "database_time",
            ],
        )
    )
    
    registry.register(
        ExperimentCapability(
            capability_id="PERF-REPRODUCE",
            name="API latency reproduction",
            description=(
                "Reproduce the latency difference between the "
                "baseline and regressed implementation."
            ),
            target_hypothesis_types=[
                "database",
                "performance",
                "application_code",
            ],
            allowed_tools=["python"],
            risk_level="low",
            timeout_seconds=60,
            estimated_cost=3.0,
            expected_outputs=[
                "baseline_latency",
                "regressed_latency",
                "fixed_latency",
                "reproduction_status",
            ],
        )
    )


    registry.register(
        ExperimentCapability(
            capability_id="CACHE-METRICS",
            name="Cache metrics inspection",
            description=(
                "Compare baseline and current cache hit rate, "
                "misses, and related cache metrics to determine "
                "whether cache behavior changed."
            ),
            target_hypothesis_types=[
                "cache",
                "performance",
            ],
            allowed_tools=["filesystem"],
            risk_level="low",
            timeout_seconds=30,
            estimated_cost=1.0,
            expected_outputs=[
                "hit_rate",
                "miss_count",
            ],
        )
    )
     
    return registry