from __future__ import annotations

import json
import uuid
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from investigator.fleet.agents import root_agent
from investigator.fleet.firestore_state import FleetStateStore
from scripts.setup_benchmark_fixtures import (
    main as setup_fixtures,
)

APP_NAME = "investigation_fleet"


class InvestigationRequest(BaseModel):
    case_id: str = "api_latency_regression"
    mode: str = "demo"


class InvestigationResponse(BaseModel):
    investigation_id: str
    case_id: str
    status: str


app = FastAPI(
    title="Investigation Fleet",
    version="1.0.0",
)


def _project_root() -> Path:
    return (
        Path(__file__).resolve().parents[2]
    )


def _load_demo_trace() -> dict:
    trace_path = (
        _project_root()
        / "benchmark"
        / "demo"
        / "api_latency_fleet_trace.json"
    )

    if not trace_path.exists():
        raise FileNotFoundError(
            f"Demo trace does not exist: {trace_path}"
        )

    return json.loads(
        trace_path.read_text(
            encoding="utf-8"
        )
    )


def _now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _event_to_record(event: Any) -> dict:
    record = {
        "timestamp": _now(),
        "agent": getattr(
            event,
            "author",
            "unknown",
        ),
    }

    actions = getattr(
        event,
        "actions",
        None,
    )

    if actions is not None:
        transfer = getattr(
            actions,
            "transfer_to_agent",
            None,
        )

        if transfer:
            record["type"] = "delegation"
            record["target_agent"] = transfer
            return record

    content = getattr(
        event,
        "content",
        None,
    )

    if content is not None:
        parts = getattr(
            content,
            "parts",
            None,
        ) or []

        for part in parts:
            function_call = getattr(
                part,
                "function_call",
                None,
            )

            if function_call is not None:
                record["type"] = "tool_call"
                record["tool"] = getattr(
                    function_call,
                    "name",
                    "unknown",
                )
                return record

    record["type"] = "event"

    texts: list[str] = []

    if content is not None:
        parts = getattr(
            content,
            "parts",
            None,
        ) or []

        for part in parts:
            text = getattr(
                part,
                "text",
                None,
            )

            if text:
                texts.append(text)

    if texts:
        record["text"] = "\n".join(texts)

    return record


async def _run_investigation(
    investigation_id: str,
    case_id: str,
) -> None:

    setup_fixtures()

    store = FleetStateStore()

    project_root = _project_root()

    case_path = (
        project_root
        / "benchmark"
        / "cases"
        / f"{case_id}.json"
    )

    if not case_path.exists():
        store.save(
            investigation_id,
            {
                "status": "failed",
                "error": f"Unknown case: {case_id}",
                "updated_at": _now(),
            },
        )
        return

    case_data = (
        __import__("json")
        .loads(
            case_path.read_text(
                encoding="utf-8"
            )
        )
    )

    repository_path = str(
        project_root
        / case_data[
            "repository_path"
        ]
    )

    session_service = (
        InMemorySessionService()
    )

    user_id = investigation_id
    session_id = str(
        uuid.uuid4()
    )

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
        state={
            "investigation_id": investigation_id,
            "case_id": case_id,
        },
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
                text=(
                    "Investigate this incident autonomously.\n\n"
                    f"Case: {case_id}\n"
                    f"Problem: {case_data['problem']}\n\n"
                    f"Repository: {repository_path}\n\n"
                    "Use the specialist fleet. "
                    "Collect source and runtime evidence, "
                    "then verify the root cause."
                )
            )
        ],
    )

    store.save(
        investigation_id,
        {
            "investigation_id": investigation_id,
            "case_id": case_id,
            "status": "running",
            "created_at": _now(),
            "updated_at": _now(),
            "events": [],
        },
    )

    events: list[dict] = []

    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        ):
            record = _event_to_record(event)
            events.append(record)

            store.save(
                investigation_id,
                {
                    "status": "running",
                    "updated_at": _now(),
                    "events": events,
                    "latest_event": record,
                },
            )

        final_text = ""

        for record in reversed(events):
            text = record.get("text")

            if text:
                final_text = text
                break

        verified = (
            "VERIFICATION: VERIFIED"
            in final_text
        )

        store.save(
            investigation_id,
            {
                "status": (
                    "resolved"
                    if verified
                    else "completed"
                ),
                "updated_at": _now(),
                "events": events,
                "final_output": final_text,
                "root_cause_verified": verified,
            },
        )

    except Exception as exc:

        store.save(
            investigation_id,
            {
                "status": "failed",
                "updated_at": _now(),
                "events": events,
                "error": str(exc),
            },
        )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/investigations",
    response_model=InvestigationResponse,
)
async def create_investigation(
    request: InvestigationRequest,
) -> InvestigationResponse:

    project_root = _project_root()

    case_path = (
        project_root
        / "benchmark"
        / "cases"
        / f"{request.case_id}.json"
    )

    if not case_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Unknown case: {request.case_id}",
        )

    investigation_id = (
        f"INV-{uuid.uuid4().hex[:10]}"
    )

    if request.mode == "demo":

        await _run_demo_investigation(
            investigation_id,
            request.case_id,
        )
    
    elif request.mode == "live":
    
        await _run_investigation(
            investigation_id,
            request.case_id,
        )
    
    else:
    
        raise HTTPException(
            status_code=400,
            detail=(
                "mode must be either "
                "'demo' or 'live'."
            ),
        )
    
    result = FleetStateStore().get(
        investigation_id
    )
    
    return InvestigationResponse(
        investigation_id=investigation_id,
        case_id=request.case_id,
        status=(
            result["status"]
            if result is not None
            else "failed"
        ),
    )


@app.get(
    "/investigations/{investigation_id}"
)
async def get_investigation(
    investigation_id: str,
) -> dict:

    store = FleetStateStore()

    result = store.get(
        investigation_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found.",
        )

    return result


async def _run_demo_investigation(
    investigation_id: str,
    case_id: str,
) -> None:

    store = FleetStateStore()

    trace = _load_demo_trace()

    if trace["case_id"] != case_id:
        raise ValueError(
            f"Demo trace is for {trace['case_id']}, "
            f"not {case_id}."
        )

    events = trace["events"]

    store.save(
        investigation_id,
        {
            "investigation_id": investigation_id,
            "case_id": case_id,
            "status": "running",
            "mode": "demo",
            "created_at": _now(),
            "updated_at": _now(),
            "events": [],
        },
    )

    replayed_events: list[dict] = []

    for event in events:

        replayed_events.append(event)

        store.save(
            investigation_id,
            {
                "status": "running",
                "mode": "demo",
                "updated_at": _now(),
                "events": replayed_events,
                "latest_event": event,
            },
        )

        await asyncio.sleep(1)

    store.save(
        investigation_id,
        {
            "status": "resolved",
            "mode": "demo",
            "updated_at": _now(),
            "events": replayed_events,
            "final_output": (
                "ROOT CAUSE VERIFIED: "
                f"{trace['root_cause']}"
            ),
            "root_cause_verified": True,
            "root_cause": trace["root_cause"],
            "confidence": trace["confidence"],
        },
    )