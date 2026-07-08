from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache
def _model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def embed_texts(texts: list[str]) -> np.ndarray:
    """L2-normalized embeddings, so cosine similarity is a plain dot product."""
    return _model().encode(texts, convert_to_numpy=True, normalize_embeddings=True)
