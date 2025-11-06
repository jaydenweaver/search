import logging
import time
from typing import List, Dict, Any
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

client = OpenAI()

@retry( # retry if api call fails
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=2, max=60),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
def _embed_batch(texts: List[str], model: str) -> List[List[float]]:
    """ Helper which calls the API once for a batch of texts. """
    response = client.embeddings.create(model=model, input=texts)
    return [d.embedding for d in response.data]


def generate_embeddings_for_papers(
    papers: List[Dict[str, Any]],
    text_field: str,
    id_field: str,
    model: str,
    batch_size: int = 100,
) -> List[Dict[str, Any]]:
    """
    Generate embeddings for a batch of paper dicts while preserving their IDs.
    
    Returns:
        List of dicts: [{"id": ..., "embedding": [...]}]
    """
    results = []
    total = len(papers)
    logging.info(f"Generating embeddings for {total} papers with model {model}")

    for i in range(0, total, batch_size):
        batch = papers[i : i + batch_size]
        batch_texts = [p[text_field] for p in batch]
        batch_ids = [p[id_field] for p in batch]

        try:
            embeddings = _embed_batch(batch_texts, model)
            batch_results = [
                {"id": pid, "embedding": emb}
                for pid, emb in zip(batch_ids, embeddings)
            ]
            results.extend(batch_results)
            logging.info(f"Embedded batch {i // batch_size + 1}: {len(batch)} papers")
            time.sleep(0.5)
        except Exception as e:
            logging.error(f"Embedding batch {i // batch_size + 1} failed: {e}")
            raise

    if len(results) != total:
        logging.warning(f"Expected {total} embeddings but got {len(results)}")

    return results
