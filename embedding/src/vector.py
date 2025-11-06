from qdrant_client import QdrantClient
from qdrant_client.http import models
import logging
import os
from typing import Dict, Any, List


def store_vectors_qdrant(embedding_results: List[Dict[str, Any]], config: Dict[str, Any]):
    """
    Stores paper embeddings in a Qdrant collection.

    Args:
        embedding_results: List[Dict[str, Any]] with fields {"id": str, "embedding": List[float]}
        config: Dict[str, Any] from config.yaml or .env
    """
    collection_name = config.get("collection_name", "papers")
    vector_size = config.get("vector_size")  # must match embedding dimension
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")

    client = QdrantClient(url=url, api_key=api_key)

    # ensure collection exists
    try:
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
        )
        logging.info(f"Ensured collection '{collection_name}' exists with size {vector_size}")
    except Exception as e:
        logging.warning(f"Could not create collection '{collection_name}' (maybe exists): {e}")

    # prepare qdrant points
    points = []
    for item in embedding_results:
        pid = item["id"]
        embedding = item["embedding"]
        payload = {"id": pid}  # optional: add categories, title, etc. later
        points.append(models.PointStruct(id=pid, vector=embedding, payload=payload))

    # upsert into qdrant
    try:
        client.upsert(
            collection_name=collection_name,
            points=points,
        )
        logging.info(f"Successfully inserted {len(points)} vectors into '{collection_name}'")
    except Exception as e:
        logging.error(f"Failed to upsert vectors: {e}")
