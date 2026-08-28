import os

from google import genai
from google.genai import types

from investigator.domain.models import Investigation
from investigator.reasoning.schemas import ExperimentProposal
from investigator.domain.models import Investigation, ExperimentCapability, ExperimentResult
from investigator.reasoning.result_schema import ResultAssessment


DEFAULT_MODEL = "gemini-3.6-flash"


class GeminiReasoner:
    """Uses Gemini to reason about the current investigation."""

    def __init__(self, model: str | None = None) -> None:

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is not set")

        self.model = (
            model
            or os.getenv(
                "GEMINI_MODEL",
                DEFAULT_MODEL,
            )
        )

        self.client = genai.Client(api_key=api_key)


    def propose_experiments(self, investigation: Investigation, capabilities: list[ExperimentCapability]) -> ExperimentProposal:

        prompt = self._build_prompt(
            investigation,
            capabilities,
            )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExperimentProposal,
            ),
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response")

        return ExperimentProposal.model_validate_json(response.text)


    
    
    @staticmethod
    def _build_prompt(investigation: Investigation, capabilities: list[ExperimentCapability]) -> str:

        hypotheses = "\n".join(
            (
                f"- {hypothesis.hypothesis_id}: "
                f"{hypothesis.description} "
                f"(confidence={hypothesis.confidence:.2f})"
            )
            for hypothesis in investigation.hypotheses
        )

        evidence = "\n".join(
            (
                f"- {item.evidence_id}: "
                f"{item.observation}"
            )
            for item in investigation.evidence
        )

        completed_experiments = "\n".join(
            (
                f"- {experiment.experiment_id}: "
                f"{experiment.purpose}"
            )
            for experiment in investigation.experiments
        )

        capability_text = "\n".join(
            (
                f"- ID: {capability.capability_id}\n"
                f"  Name: {capability.name}\n"
                f"  Description: {capability.description}\n"
                f"  Hypothesis types: "
                f"{capability.target_hypothesis_types}\n"
                f"  Allowed tools: "
                f"{capability.allowed_tools}\n"
                f"  Risk: {capability.risk_level}\n"
                f"  Timeout: "
                f"{capability.timeout_seconds}s\n"
                f"  Cost: {capability.estimated_cost}\n"
                f"  Outputs: "
                f"{capability.expected_outputs}"
            )
            for capability in capabilities
        )

        return f"""
You are the reasoning component of an autonomous
technical investigation system.

Your job is to propose candidate experiments that
reduce uncertainty about the current investigation.

You are NOT allowed to:
- execute commands
- claim that a hypothesis is proven
- invent evidence
- assume an experiment succeeded
- bypass safety constraints

You are ONLY proposing experiments.

INVESTIGATION

Problem:
{investigation.problem}

Current hypotheses:
{hypotheses or "None"}

Evidence collected so far:
{evidence or "None"}

Experiments already performed:
{completed_experiments or "None"}

Generate a small set of useful candidate experiments.

For each experiment:
- explain what it tests
- identify the target hypotheses
- explain why it is useful now
- estimate information gain
- estimate hypothesis coverage
- estimate relative cost
- assign risk level
- specify required tools
- give a reasonable timeout

Do not repeat experiments that have already been completed.
Prefer experiments that are informative, cheap, safe,
and relevant to the current uncertainty.

AVAILABLE CAPABILITIES

You may propose ONLY experiments that correspond
to one of the capabilities below.

{capability_text}

Do not invent experiment types.
Do not invent tools.
Do not request tools not listed by a capability.
"""
    
    def analyze(self, investigation: Investigation, result: ExperimentResult) -> ResultAssessment:

        prompt = self._build_result_assessment_prompt(
            investigation,
            result,
        )
    
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ResultAssessment,
            ),
        )
    
        if not response.text:
            raise RuntimeError("Gemini returned an empty result assessment")
    
        return ResultAssessment.model_validate_json(response.text)



    @staticmethod
    def _build_result_assessment_prompt(investigation: Investigation, result: ExperimentResult) -> str:
    
        hypotheses = "\n".join(
            (
                f"- {hypothesis.hypothesis_id}: "
                f"{hypothesis.description} "
                f"(confidence={hypothesis.confidence:.3f})"
            )
            for hypothesis in investigation.hypotheses
        )
    
        evidence = "\n".join(
            (
                f"- {item.evidence_id}: "
                f"{item.observation}"
            )
            for item in investigation.evidence
        )
    
        observations = "\n".join(
            f"- {observation}"
            for observation in result.observations
        )
    
        return f"""
You are the result-analysis component of an
autonomous technical investigation engine.

The system just executed one experiment.

Your task is to interpret the observed result and
update the investigation's beliefs.

You MUST:
- reason only from the supplied evidence
- assess every known hypothesis
- assign confidence values between 0.0 and 1.0
- explain how the result affects each hypothesis
- determine whether more investigation is needed
- identify the most useful next uncertainty to investigate

You MUST NOT:
- invent evidence
- claim an experiment succeeded when it failed
- modify files
- execute tools
- invent hypotheses that are not already present

IMPORTANT:
The confidence values should form a normalized
distribution across the hypotheses.

INVESTIGATION PROBLEM:
{investigation.problem}

CURRENT HYPOTHESES:
{hypotheses}

EVIDENCE SO FAR:
{evidence or "None"}

CURRENT EXPERIMENT RESULT:
Experiment ID:
{result.experiment_id}

Status:
{result.status.value}

Observations:
{observations or "None"}

Error:
{result.error or "None"}

Assess the result carefully.
"""