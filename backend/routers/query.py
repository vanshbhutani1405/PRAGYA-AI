import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agents.graph import compiled_graph
from services import supabase_service

router = APIRouter(prefix="/api/v1", tags=["query"])


class QueryRequest(BaseModel):
    query: str
    session_id: str


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


_NODE_LABELS = {
    "event_router": "routing",
    "copilot_agent": "copilot",
    "maintenance_agent": "maintenance",
    "compliance_agent": "compliance",
    "synthesis_arbitration": "synthesis",
}


async def _run_stream(request: QueryRequest):
    history = supabase_service.get_chat_history(request.session_id, limit=12)
    initial_state = {
        "query": request.query,
        "chat_history": [
            {"role": m["role"], "content": m["content"]} for m in history
        ],
    }

    final_synthesis = {}
    async for event in compiled_graph.astream_events(initial_state, version="v2"):
        kind = event["event"]
        name = event.get("name")
        if kind == "on_chain_start" and name in _NODE_LABELS:
            yield _sse("node_start", {"agent": _NODE_LABELS[name]})
        elif kind == "on_chain_end" and name in _NODE_LABELS:
            output = event["data"].get("output", {})
            payload = output if isinstance(output, dict) else {}
            if name == "synthesis_arbitration":
                final_synthesis = payload.get("synthesis", {})
            yield _sse(
                "node_end",
                {"agent": _NODE_LABELS[name], "output": payload},
            )

    supabase_service.save_chat_message(
        {
            "session_id": request.session_id,
            "role": "user",
            "content": request.query,
        }
    )
    supabase_service.save_chat_message(
        {
            "session_id": request.session_id,
            "role": "assistant",
            "content": json.dumps(final_synthesis, default=str),
        }
    )
    yield _sse("synthesis", final_synthesis)
    yield _sse("done", {})


@router.post("/query")
async def query(request: QueryRequest):
    return StreamingResponse(_run_stream(request), media_type="text/event-stream")
