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

def check_qdrant_collection(config: Dict[str, Any]):
    collection_name = config.get("collection_name", "papers")
    vector_size = config.get("vector_size")
    sleep_time = config.get("initial_sleep", 10)

    try:
        # check if collection exists
        existing_collections = [c.name for c in client.get_collections().collections]
        if collection_name in existing_collections:
            logging.info(f"Collection '{collection_name}' already exists. Skipping recreation.")
            return
        else:
            # create collection if missing
            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
            )
            logging.info(f"Created new collection '{collection_name}' with vector size {vector_size}")
    except Exception as e:
        logging.error(f"Error ensuring collection '{collection_name}': {e}")
        return

    logging.info(f"Sleeping for {sleep_time} seconds to ensure Qdrant collection is ready...")
    time.sleep(sleep_time)


def store_vectors_qdrant(embedding_results: List[Dict[str, Any]], config: Dict[str, Any]):
    """
    Stores paper embeddings in a qdrant collection.

    Args:
        embedding_results: List[Dict[str, Any]] with fields {"id": str, "embedding": List[float]}
        config: Dict[str, Any] from config.yaml or .env
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

    try:
        client.upsert(
            collection_name=collection_name,
            points=points,
        )
        logging.info(f"Successfully inserted {len(points)} vectors into '{collection_name}'")
    except Exception as e:
        logging.error(f"Failed to upsert vectors.")

    

