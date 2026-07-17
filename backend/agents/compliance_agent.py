import json

from services import embedding_service, llm_service, supabase_service

_TOP_REGULATIONS = 8
_TOP_PROCEDURES = 8

_SYSTEM_PROMPT = (
    "You are PRAGYA AI's compliance auditor. Compare the procedure content against the "
    "regulation content and identify where procedures fail to satisfy regulations. "
    "Return ONLY valid JSON with key compliance_gaps: a list of objects with keys "
    "regulation_ref (string), gap_description (string), severity (float 0-1), "
    "recommended_corrective_action (string). Return an empty list when fully compliant."
)


def run(query: str) -> dict:
    """Compare regulation chunks against procedure chunks and surface compliance gaps."""
    query_embedding = embedding_service.encode(query)
    regulations = supabase_service.similarity_search(
        query_embedding, _TOP_REGULATIONS, {"document_type": "regulation"}
    )
    procedures = supabase_service.similarity_search(
        query_embedding, _TOP_PROCEDURES, {"document_type": "procedure"}
    )

    user_prompt = json.dumps(
        {"query": query, "regulations": regulations, "procedures": procedures},
        default=str,
    )
    result = llm_service.chat_json(_SYSTEM_PROMPT, user_prompt, temperature=0.0)
    result.setdefault("compliance_gaps", [])
    return result
