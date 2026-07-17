import json

from services import embedding_service, llm_service, neo4j_service, supabase_service

_TOP_CHUNKS = 8

_SYSTEM_PROMPT = (
    "You are PRAGYA AI's operations copilot for industrial plant knowledge. "
    "Answer the operator's query using ONLY the provided document context and entity "
    "graph states. Resolve each mentioned entity to its state at the query timestamp. "
    "Return ONLY valid JSON with keys: answer (string), confidence (float 0-1), "
    "citations (list of strings), entity_states_used (list of objects with keys "
    "tag and state), confidence_decay_flag (boolean, true when relied-upon entity "
    "states are stale relative to the query timestamp)."
)


def _resolve_entity_states(entities: list[str]) -> list[dict]:
    resolved = []
    for tag in entities:
        graph = neo4j_service.get_entity_neighbours(tag)
        if graph:
            resolved.append(graph)
    return resolved


def run(query: str, chat_history: list[dict], entities: list[str], timestamp: str) -> dict:
    """GraphRAG dual retrieval: vector chunks + 1-hop graph expansion, then Groq reasoning."""
    query_embedding = embedding_service.encode(query)
    chunks = supabase_service.similarity_search(query_embedding, _TOP_CHUNKS, {})
    graph_context = _resolve_entity_states(entities)

    history = chat_history[-12:]
    user_prompt = json.dumps(
        {
            "query": query,
            "query_timestamp": timestamp,
            "chat_history": history,
            "document_chunks": chunks,
            "entity_graph": graph_context,
        },
        default=str,
    )
    result = llm_service.chat_json(_SYSTEM_PROMPT, user_prompt, temperature=0.0)
    result.setdefault("answer", "")
    result.setdefault("confidence", 0.0)
    result.setdefault("citations", [])
    result.setdefault("entity_states_used", [])
    result.setdefault("confidence_decay_flag", False)
    return result
