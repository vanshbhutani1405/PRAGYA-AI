import json

from services import llm_service

_SYSTEM_PROMPT = (
    "You are PRAGYA AI's synthesis and arbitration engine. You receive outputs from "
    "multiple specialist agents (copilot, maintenance, compliance). Detect cross-agent "
    "conflicts where recommendations contradict each other. Return ONLY valid JSON with "
    "keys: primary_recommendation (string), conflicts (list of objects with keys "
    "agents_involved, description, resolution), financial_exposure_inr (number), "
    "action_stubs (list of strings), severity (float 0-1), urgency (float 0-1), "
    "confidence (float 0-1). Base severity/urgency/confidence on the aggregated agent "
    "signals."
)

_SEVERITY_WEIGHT = 0.40
_URGENCY_WEIGHT = 0.35
_CONFIDENCE_WEIGHT = 0.25


def run(agent_outputs: dict) -> dict:
    """Detect conflicts across agent outputs and compute the composite priority score."""
    user_prompt = json.dumps({"agent_outputs": agent_outputs}, default=str)
    result = llm_service.chat_json(_SYSTEM_PROMPT, user_prompt, temperature=0.0)

    result.setdefault("primary_recommendation", "")
    result.setdefault("conflicts", [])
    result.setdefault("financial_exposure_inr", 0)
    result.setdefault("action_stubs", [])

    severity = float(result.get("severity", 0.0) or 0.0)
    urgency = float(result.get("urgency", 0.0) or 0.0)
    confidence = float(result.get("confidence", 0.0) or 0.0)
    result["composite_score"] = (
        _SEVERITY_WEIGHT * severity
        + _URGENCY_WEIGHT * urgency
        + _CONFIDENCE_WEIGHT * confidence
    )
    return result
