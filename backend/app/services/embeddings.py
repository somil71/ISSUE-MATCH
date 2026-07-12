from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache
def _model() -> SentenceTransformer:
    # Imported here, not at module load, so importing this module (and thus
    # the whole FastAPI app at startup) doesn't pull in torch/transformers --
    # that import alone can take longer than Vercel's fixed serverless
    # startup timeout, crashing the app before it ever binds its port.
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def embed_texts(texts: list[str]) -> np.ndarray:
    """L2-normalized embeddings, so cosine similarity is a plain dot product."""
    return _model().encode(texts, convert_to_numpy=True, normalize_embeddings=True)
