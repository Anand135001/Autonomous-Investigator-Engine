import asyncio
import uuid

from google.adk.runners import Runner
from google.adk.sessions import (
    InMemorySessionService,
)
from google.genai import types

from investigator.fleet.agents import root_agent


APP_NAME = "investigation_fleet"


async def main() -> None:
    session_service = (
        InMemorySessionService()
    )

    user_id = "demo-user"
    session_id = str(
        uuid.uuid4()
    )

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )

    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part(
                text=(
                    "Investigate this incident:\n\n"
                    "The checkout API p95 latency increased "
                    "from 180ms to 1700ms after the latest "
                    "deployment.\n\n"
                    "You are operating as an investigation "
                    "fleet. Delegate to the appropriate "
                    "specialists. The incident repository is:\n"
                    "benchmark/fixtures/checkout-service"
                )
            )
        ],
    )

    print(
        "=== ADK FLEET INVESTIGATION ==="
    )

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        print(event)


if __name__ == "__main__":
    asyncio.run(main())