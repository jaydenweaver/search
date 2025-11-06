import json
import time
import logging
from pathlib import Path
import yaml
from typing import List, Dict, Any
from datetime import datetime

from embedding import generate_embeddings_for_papers
#from db import store_metadata_supabase
#from vector import store_vectors_qdrant


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

def is_after_year(paper, year):
    try:
        update_str = paper.get("update_date")
        if not update_str:
            return False
        update_date = datetime.strptime(update_str, "%Y-%m-%d")
        return update_date.year >= year
    except Exception as e:
        logging.warning(f"Invalid date for paper {paper.get('id', 'unknown')}: {e}")
        return False

def load_dataset(path: str) -> List[Dict[str, Any]]:
    """ Streams JSON dataset from file. """
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1): # streams json lines to handle larger datasets
            if line.strip(): # skip blanks
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    logging.warning(f"Skipping invalid JSON at line {line_num}: {e}")

def generate_batches(dataset_path, batch_size):
    batch = []
    for paper in load_dataset(dataset_path):
        if "cs.LG" not in paper['categories'].split():
            continue

        if not is_after_year(paper, config['dataset']['from_year']):
            continue

        batch.append(paper)

        if len(batch) >= batch_size:
            yield batch
            batch = []

    if batch:
        yield batch

def process_batch(batch: List[Dict[str, Any]]):
    """ Process a single batch: embedding + DB + Qdrant. """
    abstracts = [p[config['dataset']['abstract_field']] for p in batch]

    # generate embeddings
    try:
        embedding_results = generate_embeddings_for_papers(
            papers=batch,
            text_field=config['dataset']['abstract_field'],
            id_field=config['dataset']['id_field'],
            model=config['openai']['model'],
            batch_size=len(batch)
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

    # store embeddings in qdrant
    try:
        store_vectors_qdrant(embedding_results, config['qdrant'], config['dataset'])
    except Exception as e:
        logging.error(f"Failed storing vectors in Qdrant: {e}")


def run_pipeline():
    dataset_path = config['dataset']['path']
    batch_size = config['openai']['batch_size']
    sleep_time = config['openai'].get('sleep_between_batches', 1)

    logging.info(f"Starting streaming ingestion with batch size {batch_size}")

    total_processed = 0

    for batch in generate_batches(dataset_path, batch_size):
        total_processed += len(batch)
        logging.info(f"Processing batch ending at paper {total_processed}")
        # process_batch(batch)  # uncomment to process

        time.sleep(sleep_time)  # rate limiting

    logging.info(f"Data ingestion completed successfully. Total processed: {total_processed}")

