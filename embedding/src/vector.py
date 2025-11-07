from qdrant_client import QdrantClient
from qdrant_client.http import models
import logging
import os
import time
import uuid
from typing import Dict, Any, List

url = os.getenv("QDRANT_URL")
api_key = os.getenv("QDRANT_API_KEY")

client = QdrantClient(url=url, api_key=api_key)

def recreate_qdrant_collection(config: Dict[str, Any]):
    collection_name = config.get("collection_name", "papers")
    vector_size = config.get("vector_size")  # must match embedding dimension
    sleep_time = config.get("initial_sleep")

    try:
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
        )
        logging.info(f"Ensured collection '{collection_name}' exists with size {vector_size}")
    except Exception as e:
        logging.warning(f"Could not create collection '{collection_name}' (maybe exists): {e}")

    logging.info(f"Sleeping for {sleep_time} seconds to ensure qdrant collection is ready for upsert...")
    time.sleep(sleep_time)


def store_vectors_qdrant(embedding_results: List[Dict[str, Any]], config: Dict[str, Any]):
    """
    Stores paper embeddings in a qdrant collection with automatic retries.

    Args:
        embedding_results: List[Dict[str, Any]] with fields {"id": str, "embedding": List[float]}
        config: Dict[str, Any] from config.yaml or .env
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds for exponential backoff
    """
    collection_name = config.get("collection_name", "papers")
    
    points = []
    for item in embedding_results:
        pid = item["id"]
        # use consistent uuid integer id to satisfy qdrant
        points.append(models.PointStruct(
            id=uuid.uuid5(uuid.NAMESPACE_DNS, pid).int >> 64,
            vector=item["embedding"], 
            payload={"paper_id": pid}
        ))

    max_retries = config["max_retries"]
    base_delay = config["base_delay"]
    attempt = 0
    while attempt < max_retries:
        try:
            client.upsert(
                collection_name=collection_name,
                points=points,
            )
            logging.info(f"Successfully inserted {len(points)} vectors into '{collection_name}'")
            return  # success, exit the function
        except Exception as e:
            attempt += 1
            delay = base_delay * (2 ** (attempt - 1))  # exponential backoff
            logging.warning(f"Attempt {attempt}/{max_retries} failed to upsert vectors: {e}. Retrying in {delay:.1f}s...")
            time.sleep(delay)

    logging.error(f"Failed to upsert vectors after {max_retries} attempts.")

