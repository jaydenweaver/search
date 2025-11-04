# src/process.py
import json
import time
import logging
from pathlib import Path
import yaml
from typing import List, Dict, Any

from .embedding import generate_embeddings
from .db import store_metadata_supabase
from .vector import store_vectors_qdrant


# load config.yaml
CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

# initialise logger
log_file = config['logging'].get('log_file', 'batch_embedding.log')
logging.basicConfig(
    filename=log_file,
    level=getattr(logging, config['logging'].get('level', 'INFO')),
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def load_dataset(path: str) -> List[Dict[str, Any]]:
    """ Load JSON dataset from file. """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    logging.info(f"Loaded {len(data)} papers from dataset")
    return data

def process_batch(batch: List[Dict[str, Any]]):
    """ Process a single batch: embedding + DB + Qdrant. """
    abstracts = [p[config['dataset']['abstract_field']] for p in batch]
    paper_ids = [p[config['dataset']['id_field']] for p in batch]

    # generate embeddings
    try:
        embeddings = generate_embeddings(
            texts=abstracts,
            model=config['openai']['model'],
            batch_size=len(batch)  # embed batch at once
        )
        logging.info(f"Generated embeddings for batch of {len(batch)} papers")
    except Exception as e:
        logging.error(f"Failed embedding batch: {e}")
        return

    # store metadata in supabase
    for p in batch:
        try:
            store_metadata_supabase(p, config['supabase'])
        except Exception as e:
            logging.error(f"Failed storing metadata for paper {p[config['dataset']['id_field']]}: {e}")

    # store embeddings
    try:
        store_vectors_qdrant(batch, embeddings, config['qdrant'], config['dataset'])
    except Exception as e:
        logging.error(f"Failed storing vectors in Qdrant: {e}")


def run_pipeline():
    dataset = load_dataset(config['dataset']['path'])
    batch_size = config['openai']['batch_size']
    sleep_time = config['openai'].get('sleep_between_batches', 1)

    total = len(dataset)
    logging.info(f"Starting pipeline for {total} papers with batch size {batch_size}")

    for i in range(0, total, batch_size):
        batch = dataset[i:i + batch_size]
        logging.info(f"Processing batch {i} to {i + len(batch)}")
        process_batch(batch)
        time.sleep(sleep_time)  # polite rate-limiting

    logging.info("Pipeline completed successfully!")

