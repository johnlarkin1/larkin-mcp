"""Semantic search utilities for the larkin-mcp server.

This module provides semantic (embedding-based) search functionality.
Requires the 'semantic' optional dependency: pip install larkin-mcp[semantic]
"""

import logging
from functools import lru_cache

from src.util.resources import list_resources, load_resource

logger = logging.getLogger(__name__)

# Check if sentence-transformers is available
try:
    from sentence_transformers import SentenceTransformer

    SEMANTIC_SEARCH_AVAILABLE = True
except ImportError:
    SEMANTIC_SEARCH_AVAILABLE = False
    logger.info("sentence-transformers not installed. Semantic search disabled.")


# Default model - small and fast
DEFAULT_MODEL = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model(model_name: str = DEFAULT_MODEL) -> "SentenceTransformer":
    """Load and cache the sentence transformer model.

    Args:
        model_name: Name of the sentence-transformers model to use.

    Returns:
        Loaded SentenceTransformer model.

    Raises:
        RuntimeError: If sentence-transformers is not installed.
    """
    if not SEMANTIC_SEARCH_AVAILABLE:
        raise RuntimeError(
            "Semantic search requires sentence-transformers. Install with: pip install larkin-mcp[semantic]"
        )

    logger.info(f"Loading sentence transformer model: {model_name}")
    return SentenceTransformer(model_name)


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks for embedding.

    Args:
        text: Text to split.
        chunk_size: Maximum characters per chunk.
        overlap: Number of overlapping characters between chunks.

    Returns:
        List of text chunks.
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = end - overlap

    return chunks


@lru_cache(maxsize=32)
def _get_resource_embeddings(resource_name: str, model_name: str = DEFAULT_MODEL) -> tuple:
    """Get embeddings for a resource's chunks.

    Args:
        resource_name: Name of the resource.
        model_name: Sentence transformer model name.

    Returns:
        Tuple of (chunks, embeddings).
    """
    model = _get_model(model_name)
    content = load_resource(resource_name, raise_on_error=True)
    chunks = _chunk_text(content)
    embeddings = model.encode(chunks)
    return chunks, embeddings


def semantic_search(
    query: str,
    top_k: int = 5,
    threshold: float = 0.3,
    model_name: str = DEFAULT_MODEL,
) -> list[dict]:
    """Search resources using semantic similarity.

    Args:
        query: Search query text.
        top_k: Maximum number of results to return.
        threshold: Minimum similarity score (0-1) to include in results.
        model_name: Sentence transformer model to use.

    Returns:
        List of dictionaries with 'resource', 'chunk', and 'score' keys,
        sorted by similarity score (highest first).

    Raises:
        RuntimeError: If sentence-transformers is not installed.
    """
    if not SEMANTIC_SEARCH_AVAILABLE:
        raise RuntimeError(
            "Semantic search requires sentence-transformers. Install with: pip install larkin-mcp[semantic]"
        )

    model = _get_model(model_name)
    query_embedding = model.encode([query])[0]

    results = []
    for resource_name in list_resources():
        try:
            chunks, embeddings = _get_resource_embeddings(resource_name, model_name)

            # Calculate cosine similarities
            from sentence_transformers import util

            similarities = util.cos_sim(query_embedding, embeddings)[0]

            for i, (chunk, score) in enumerate(zip(chunks, similarities, strict=False)):
                score_float = float(score)
                if score_float >= threshold:
                    results.append(
                        {
                            "resource": resource_name,
                            "chunk": chunk.strip(),
                            "score": score_float,
                            "chunk_index": i,
                        }
                    )
        except Exception as e:
            logger.warning(f"Error processing resource '{resource_name}': {e}")
            continue

    # Sort by score (highest first) and limit to top_k
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def is_semantic_search_available() -> bool:
    """Check if semantic search is available.

    Returns:
        True if sentence-transformers is installed, False otherwise.
    """
    return SEMANTIC_SEARCH_AVAILABLE
