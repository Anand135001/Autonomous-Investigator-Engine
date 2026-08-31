from __future__ import annotations

import asyncio
from typing import Any

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from investigator.fleet.agents import root_agent


APP_NAME = "investigation_fleet"
USER_ID = "demo_user"
SESSION_ID = "demo_session"


def _extract_text(event: Any) -> str:
    content = getattr(event, "content", None)

    if content is None:
        return ""

    parts = getattr(content, "parts", None) or []

    texts: list[str] = []

    for part in parts:
        text = getattr(part, "text", None)

        if text:
            texts.append(text)

    return "\n".join(texts)


def _agent_name(event: Any) -> str:
    return getattr(event, "author", "unknown")


def _is_tool_call(event: Any) -> bool:
    content = getattr(event, "content", None)

    if content is None:
        return False

    parts = getattr(content, "parts", None) or []

    return any(
        getattr(part, "function_call", None) is not None
        for part in parts
    )


def _is_transfer(event: Any) -> bool:
    actions = getattr(event, "actions", None)

    if actions is None:
        return False

    return bool(getattr(actions, "transfer_to_agent", None))


def _tool_name(event: Any) -> str | None:
    content = getattr(event, "content", None)

    if content is None:
        return None

    parts = getattr(content, "parts", None) or []

    for part in parts:
        function_call = getattr(part, "function_call", None)

        if function_call is not None:
            return getattr(function_call, "name", None)

    return None


def _print_header() -> None:
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║        AUTONOMOUS INVESTIGATION FLEET                ║")
    print("║        Case: API Latency Regression                  ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()


async def run() -> None:
    session_service = InMemorySessionService()

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part(
                text="""
Investigate the checkout API latency regression.

Repository:
benchmark/fixtures/checkout-service

Incident:
p95 latency increased from 180ms to 1700ms
after the latest deployment.

Perform the investigation autonomously.
Use the specialist fleet and verify the root cause.
"""
            )
        ],
    )

    _print_header()

    last_agent = None

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=message,
    ):
        agent = _agent_name(event)

        if agent != last_agent:
            print()
            print(f"[AGENT] {agent.upper()}")
            print("-" * 58)
            last_agent = agent

        if _is_transfer(event):
            actions = event.actions
            target = actions.transfer_to_agent

            print(f"  → Delegating to {target}")

        tool = _tool_name(event)

        if tool:
            print(f"  ⚙ Executing: {tool}")

        text = _extract_text(event)

        if text:
            print()
            print(text)


if __name__ == "__main__":
    asyncio.run(run())