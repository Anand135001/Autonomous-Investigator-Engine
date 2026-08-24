from investigator.domain.models import (
    Experiment,
    ExperimentCandidate,
    ExperimentContract,
)


def candidate_to_contract(candidate: ExperimentCandidate) -> ExperimentContract:

    return ExperimentContract(
        experiment_id=candidate.experiment_id,
        purpose=candidate.purpose,
        target_hypothesis_id=(
            candidate.target_hypothesis_ids[0]
        ),
        rationale=candidate.rationale,
        allowed_tools=candidate.allowed_tools,
        timeout_seconds=candidate.timeout_seconds,
        estimated_cost=candidate.estimated_cost,
        risk_level=candidate.risk_level,
    )


def contract_to_experiment(contract: ExperimentContract) -> Experiment:

    return Experiment(
        experiment_id=contract.experiment_id,
        purpose=contract.purpose,
        target_hypothesis_id=contract.target_hypothesis_id,
        rationale=contract.rationale,
        estimated_cost=contract.estimated_cost,
        timeout_seconds=contract.timeout_seconds,
        risk_level=contract.risk_level,
        allowed_tools=contract.allowed_tools,
    )