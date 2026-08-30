import os

from google import genai
from google.genai import types

from investigator.domain.models import (
    ExperimentCapability,
    ExperimentResult,
    Investigation,
)
from investigator.reasoning.result_schema import (
    ResultAssessment,
)
from investigator.reasoning.schemas import (
    ExperimentProposal,
)
from investigator.reasoning.usage import ModelUsage
from investigator.reasoning.retry import generate_with_retry


DEFAULT_MODEL = "gemini-3.6-flash"


class GeminiReasoner:
    """Uses Gemini to reason about the current investigation."""

    def __init__(self, model: str | None = None) -> None:

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable "
                "is not set"
            )

        self.model = (
            model
            or os.getenv(
                "GEMINI_MODEL",
                DEFAULT_MODEL,
            )
        )

        self.client = genai.Client(api_key=api_key,)
        self.usage_records: list[ModelUsage] = []


    def propose_experiments(
        self,
        investigation: Investigation,
        capabilities: list[ExperimentCapability],
    ) -> ExperimentProposal:

        prompt = self._build_prompt(
            investigation,
            capabilities,
        )

        token_count = self.client.models.count_tokens(
            model=self.model,
            contents=prompt,
        )
        
        print(
            f"[Gemini planning input tokens] "
            f"{token_count.total_tokens}"
        )

        response = generate_with_retry(
            lambda: self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ExperimentProposal,
                ),
            )
        )

        usage = response.usage_metadata

        if usage is not None:
            self.usage_records.append(
                ModelUsage(
                    operation="planning",
                    input_tokens=usage.prompt_token_count or 0,
                    output_tokens=usage.candidates_token_count or 0,
                    thoughts_tokens=usage.thoughts_token_count or 0,
                    total_tokens=usage.total_token_count or 0,
                )
            )

        if response.usage_metadata:
            print(
                "[Gemini planning usage]",
                response.usage_metadata,
            )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response"
            )

        return ExperimentProposal.model_validate_json(
            response.text
        )

    @staticmethod
    def _build_prompt(
        investigation: Investigation,
        capabilities: list[ExperimentCapability],
    ) -> str:

        hypotheses = "\n".join(
            (
                f"- {hypothesis.hypothesis_id}: "
                f"{hypothesis.description} "
                f"(confidence="
                f"{hypothesis.confidence:.2f})"
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
                f"  Description: "
                f"{capability.description}\n"
                f"  Allowed tools: "
                f"{capability.allowed_tools}\n"
                f"  Risk: {capability.risk_level}\n"
                f"  Cost: "
                f"{capability.estimated_cost}\n"
            )
            for capability in capabilities
        )

        return f"""
You are the planning component of an autonomous
technical investigation system.

Given the current investigation state and available
capabilities, propose a small set of experiments that
reduce uncertainty.

Rules:
- Propose only registered capabilities.
- experiment_id must exactly match a capability ID.
- Use only tools allowed by that capability.
- Do not repeat completed experiments.
- Target existing hypotheses only.
- Prefer informative, cheap, and low-risk experiments.
- Do not execute experiments.
- Do not invent evidence or hypotheses.

INVESTIGATION

Problem:
{investigation.problem}

Current hypotheses:
{hypotheses or "None"}

Previous evidence:
{evidence or "None"}

Experiments already performed:
{completed_experiments or "None"}

AVAILABLE CAPABILITIES

{capability_text or "None"}
"""

    def analyze(
        self,
        investigation: Investigation,
        result: ExperimentResult,
    ) -> ResultAssessment:

        prompt = self._build_result_assessment_prompt(
            investigation,
            result,
        )

        token_count = self.client.models.count_tokens(
            model=self.model,
            contents=prompt,
        )
        
        print(
            f"[Gemini planning input tokens] "
            f"{token_count.total_tokens}"
        )

        response = generate_with_retry(
            lambda: self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ResultAssessment,
                ),
            )
        )

        usage = response.usage_metadata

        if usage is not None:
            self.usage_records.append(
                ModelUsage(
                    operation="analysis",
                    input_tokens=usage.prompt_token_count or 0,
                    output_tokens=usage.candidates_token_count or 0,
                    thoughts_tokens=usage.thoughts_token_count or 0,
                    total_tokens=usage.total_token_count or 0,
                )
            )

        if response.usage_metadata:
            print(
                "[Gemini planning usage]",
                response.usage_metadata,
            )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty result assessment"
            )

        return ResultAssessment.model_validate_json(
            response.text
        )

    @staticmethod
    def _build_result_assessment_prompt(
        investigation: Investigation,
        result: ExperimentResult,
    ) -> str:

        hypotheses = "\n".join(
            (
                f"- {hypothesis.hypothesis_id}: "
                f"{hypothesis.description} "
                f"(confidence="
                f"{hypothesis.confidence:.3f})"
            )
            for hypothesis in investigation.hypotheses
        )

        previous_evidence = "\n".join(
            (
                f"- {item.evidence_id}: "
                f"{item.observation}"
            )
            for item in investigation.evidence
            if item.experiment_id != result.experiment_id
        )

        observations = "\n".join(
            f"- {observation}"
            for observation in result.observations
        )

        return f"""
You are the result-analysis component of an
autonomous technical investigation system.

Analyze the latest experiment result using the
current investigation state.

Rules:
- Assess every known hypothesis.
- Use only supplied evidence.
- Do not invent evidence or hypotheses.
- Do not execute tools or modify anything.
- Assign each hypothesis a confidence from 0.0 to 1.0.
- Confidence values must form a normalized distribution.
- Decide whether the evidence is sufficient to verify
  the leading hypothesis.
- If verification is insufficient, identify the most
  useful next uncertainty.

INVESTIGATION PROBLEM:
{investigation.problem}

CURRENT HYPOTHESES:
{hypotheses}

PREVIOUS EVIDENCE:
{previous_evidence or "None"}

CURRENT EXPERIMENT RESULT:

Experiment ID:
{result.experiment_id}

Status:
{result.status.value}

Observations:
{observations or "None"}

Error:
{result.error or "None"}
"""