import json

from services import embedding_service, llm_service, supabase_service

_TOP_CHUNKS = 8

_SYSTEM_PROMPT = (
    "You are PRAGYA AI's predictive maintenance analyst. Using the provided document "
    "chunks, identify maintenance findings for the mentioned equipment. Return ONLY "
    "valid JSON with keys: maintenance_findings (list of objects with keys "
    "equipment_tag, condition, urgency (float 0-1), recommended_action), confidence "
    "(float 0-1)."
)


def run(query: str, entities: list[str]) -> dict:
    """Retrieve equipment context and produce maintenance findings via Groq."""
    query_embedding = embedding_service.encode(query)
    chunks = supabase_service.similarity_search(query_embedding, _TOP_CHUNKS, {})

    user_prompt = json.dumps(
        {"query": query, "equipment": entities, "document_chunks": chunks},
        default=str,
    )
    result = llm_service.chat_json(_SYSTEM_PROMPT, user_prompt, temperature=0.0)
    result.setdefault("maintenance_findings", [])
    result.setdefault("confidence", 0.0)
    return result
