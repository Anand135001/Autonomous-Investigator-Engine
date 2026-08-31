import os

from google.adk.agents import Agent

from investigator.fleet.tools import (
    inspect_deployment_diff,
    reproduce_performance,
)


MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)




cache_agent = Agent(
    name="cache_investigator",
    model=MODEL,
    description=(
        "Investigates cache behavior and cache metrics."
    ),
    instruction="""
You are the Cache Investigator.

Your responsibility is ONLY cache-related evidence.

Analyze cache hit rates, misses, and related metrics.
Determine whether cache behavior changed in a way that
could explain the incident.

Do not invent metrics.
Do not declare the final root cause.
""",
)


verifier_agent = Agent(
    name="evidence_verifier",
    model=MODEL,
    description=(
        "Verifies the root cause from specialist findings."
    ),
    instruction="""
You are the Evidence Verifier.

You receive findings from specialist investigators.

Your responsibility is to determine whether the
root-cause hypothesis is sufficiently supported.

You must:
- use only supplied evidence
- distinguish source evidence from runtime evidence
- compare the competing hypotheses
- identify whether independent evidence supports
  the same causal mechanism
- state clearly whether verification is sufficient
- never invent evidence
- never execute tools

Your final response must contain:

VERIFICATION: VERIFIED or INSUFFICIENT

ROOT_CAUSE:
<best-supported hypothesis>

CONFIDENCE:
<number between 0 and 1>

REASON:
<concise explanation based only on evidence>
""",
)


runtime_agent = Agent(
    name="runtime_investigator",
    model=MODEL,
    description=(
        "Investigates runtime behavior through "
        "controlled performance reproduction."
    ),
    instruction="""
You are the Runtime Investigator.

You receive an investigation from the Code Investigator.

Your responsibility is ONLY runtime evidence.

Use reproduce_performance to measure the supplied
incident fixture.

You must:
1. Execute reproduce_performance.
2. Report baseline latency.
3. Report regressed latency.
4. Report baseline query count.
5. Report regressed query count.
6. Report the latency ratio.
7. State whether the regression is reproducible.
8. After completing your runtime investigation,
   transfer the investigation to the Evidence Verifier.

Do not invent measurements.
Do not modify source code.
Do not declare the final root cause yourself.
""",
    tools=[
        reproduce_performance,
    ],
    sub_agents=[
        verifier_agent
    ]
)


code_agent = Agent(
    name="code_investigator",
    model=MODEL,
    description=(
        "Investigates source and deployment changes "
        "for operational regressions."
    ),
    instruction="""
You are the Code Investigator.

Your responsibility is ONLY source-level investigation.

Use inspect_deployment_diff to inspect the incident
repository.

You must:
1. Inspect the latest deployment diff.
2. Identify changed files.
3. Identify suspicious performance-related changes.
4. Explain the mechanism that could explain the incident.
5. Report concrete evidence from the Git diff.

Do not invent runtime measurements.
Do not claim the root cause is verified.

After completing your source investigation,
transfer the investigation to the Runtime Investigator.
""",
    tools=[
        inspect_deployment_diff,
    ],
    sub_agents=[
        runtime_agent,
    ]
)


root_agent = Agent(
    name="fleet_commander",
    model=MODEL,
    description=(
        "Coordinates the investigation specialist fleet."
    ),
    instruction="""
You are the Fleet Commander.

You coordinate an autonomous investigation.

Your responsibility is orchestration.

For a performance incident:
1. Start with the Code Investigator.
2. Allow it to inspect source changes.
3. Allow the Runtime Investigator to reproduce the issue.
4. Allow the Evidence Verifier to evaluate the combined findings.
5. Do not invent findings yourself.
6. Do not declare a root cause without verifier evidence.
""",
    sub_agents=[
        code_agent,
    ],
)