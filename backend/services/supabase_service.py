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
