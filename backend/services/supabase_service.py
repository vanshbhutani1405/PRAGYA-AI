from supabase import create_client, Client

from config import settings

_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def index_chunks(chunks: list[dict], metadata: dict) -> list[dict]:
    """Insert chunk rows (content, embedding, metadata) into the document_chunks table."""
    rows = []
    for chunk in chunks:
        rows.append(
            {
                "content": chunk["content"],
                "embedding": chunk["embedding"],
                "chunk_index": chunk["chunk_index"],
                "metadata": metadata,
            }
        )
    response = _client.table("document_chunks").insert(rows).execute()
    return response.data


def similarity_search(
    query_embedding: list[float], match_count: int, filter_dict: dict
) -> list[dict]:
    """Vector similarity search via the match_document_chunks RPC."""
    response = _client.rpc(
        "match_document_chunks",
        {
            "query_embedding": query_embedding,
            "match_count": match_count,
            "filter": filter_dict or {},
        },
    ).execute()
    return response.data


def insert_document(document: dict) -> dict:
    """Register a document row and return the created record."""
    response = _client.table("documents").insert(document).execute()
    return response.data[0] if response.data else {}


def list_documents() -> list[dict]:
    """List all registered documents."""
    response = (
        _client.table("documents").select("*").order("created_at", desc=True).execute()
    )
    return response.data


def save_chat_message(message: dict) -> dict:
    """Persist a chat message (session_id, role, content) to chat_messages."""
    response = _client.table("chat_messages").insert(message).execute()
    return response.data[0] if response.data else {}


def get_chat_history(session_id: str, limit: int = 12) -> list[dict]:
    """Return the most recent chat messages for a session in chronological order."""
    response = (
        _client.table("chat_messages")
        .select("*")
        .eq("session_id", session_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return list(reversed(response.data))


def get_conflicts(status: str | None = None) -> list[dict]:
    """Fetch conflicts, optionally filtered by status, ordered by severity then detected_at."""
    query = _client.table("conflicts").select("*")
    if status is not None:
        query = query.eq("status", status)
    response = (
        query.order("severity", desc=True).order("detected_at", desc=True).execute()
    )
    return response.data


def get_conflict_by_id(conflict_id: str) -> dict:
    """Fetch a single conflict row, or an empty dict if not found."""
    response = _client.table("conflicts").select("*").eq("id", conflict_id).execute()
    return response.data[0] if response.data else {}


def update_conflict(conflict_id: str, updates_dict: dict) -> dict:
    """Patch arbitrary fields on a conflict row and return the updated record."""
    response = (
        _client.table("conflicts")
        .update(updates_dict)
        .eq("id", conflict_id)
        .execute()
    )
    return response.data[0] if response.data else {}


def insert_conflict(conflict_dict: dict) -> dict:
    """Insert a new conflict record and return it."""
    response = _client.table("conflicts").insert(conflict_dict).execute()
    return response.data[0] if response.data else {}


def get_expert_contributions() -> list[dict]:
    """Fetch all expert contributions, newest first."""
    response = (
        _client.table("expert_contributions")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return response.data


def insert_expert_contribution(data_dict: dict) -> dict:
    """Insert a single expert contribution row and return it."""
    response = _client.table("expert_contributions").insert(data_dict).execute()
    return response.data[0] if response.data else {}


def get_benchmark_results() -> list[dict]:
    """Fetch all benchmark result rows."""
    response = _client.table("benchmark_results").select("*").execute()
    return response.data


def seed_benchmarks(questions_list: list[dict]) -> dict:
    """Upsert benchmark questions by query_id, skipping any that already exist."""
    existing = _client.table("benchmark_results").select("query_id").execute()
    existing_ids = {row["query_id"] for row in existing.data}
    new_rows = [q for q in questions_list if q.get("query_id") not in existing_ids]
    if not new_rows:
        return {"inserted": 0, "skipped": len(questions_list), "rows": []}
    response = _client.table("benchmark_results").insert(new_rows).execute()
    return {
        "inserted": len(response.data),
        "skipped": len(questions_list) - len(new_rows),
        "rows": response.data,
    }

