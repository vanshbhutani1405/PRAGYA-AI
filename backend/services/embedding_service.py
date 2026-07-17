from sentence_transformers import SentenceTransformer

from config import settings

_model = SentenceTransformer(settings.EMBEDDING_MODEL)


def encode(text: str) -> list[float]:
    """Encode text into an embedding vector."""
    vector = _model.encode(text, normalize_embeddings=True)
    return vector.tolist()
