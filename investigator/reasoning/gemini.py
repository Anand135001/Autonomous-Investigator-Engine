import os

from google import genai
from google.genai import types

from investigator.domain.models import Investigation
from investigator.reasoning.schemas import ExperimentProposal


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


    def propose_experiments(self, investigation: Investigation) -> ExperimentProposal:

        prompt = self._build_prompt(investigation)

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
    def _build_prompt(investigation: Investigation) -> str:

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
"""