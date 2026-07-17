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

