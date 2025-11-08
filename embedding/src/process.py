import json
import time
import logging
from pathlib import Path
import yaml
from typing import List, Dict, Any
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .embedding import generate_embeddings_for_papers
from .db import store_metadata_supabase
from .vector import store_vectors_qdrant, check_qdrant_collection
from .checkpoint import load_checkpoint, save_checkpoint

# load config.yaml
CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

# global thread pool
EXECUTOR = ThreadPoolExecutor(max_workers=config["advanced"].get("max_workers", 4))

# initialise logger
log_file = config["logging"].get("log_file", "batch_embedding.log")
logging.basicConfig(
    filename=log_file,
    level=getattr(logging, config["logging"].get("level", "INFO")),
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# log in terminal too
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)

# helper funcs
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


def load_dataset(path: str):
    """Streams JSON dataset line by line."""
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    logging.warning(f"Skipping invalid JSON at line {line_num}: {e}")


def generate_batches(dataset_path, batch_size):
    batch = []
    for paper in load_dataset(dataset_path):
        if "cs.LG" not in paper["categories"].split():
            continue
        if not is_after_year(paper, config["dataset"]["from_year"]):
            continue

        batch.append(paper)
        if len(batch) >= batch_size:
            yield batch
            batch = []

    if batch:
        yield batch


async def process_batch(batch: List[Dict[str, Any]]):
    """Process a single batch asynchronously: embedding + DB + Qdrant."""
    loop = asyncio.get_running_loop()
    embedding_results = None

    try:
        embedding_results = await loop.run_in_executor(
            EXECUTOR,
            generate_embeddings_for_papers,
            batch,
            config["dataset"]["abstract_field"],
            config["dataset"]["id_field"],
            config["openai"]["model"],
            len(batch),
        )
        logging.info(f"Generated embeddings for batch of {len(batch)} papers")
    except Exception as e:
        logging.error(f"Failed embedding batch: {e}")
        return

    async def store_metadata():
        await loop.run_in_executor(EXECUTOR, store_metadata_supabase, batch, config["supabase"])

    async def store_vectors():
        await loop.run_in_executor(EXECUTOR, store_vectors_qdrant, embedding_results, config["qdrant"])

    await asyncio.gather(store_metadata(), store_vectors())


async def run_pipeline_async(dataset_path, batch_size, checkpoint_path, sleep_time, last_processed):
    total_processed = 0

    for batch in generate_batches(dataset_path, batch_size):
        if last_processed:
            # skip all papers up to (and including) last_processed
            if batch[-1]["id"] <= last_processed:
                continue
            else:
                last_processed = None  # start normal processing after skip

        total_processed += len(batch)
        logging.info(f"Processing batch ending at paper {total_processed}")

        await process_batch(batch)

        # save checkpoint (last paper in batch)
        last_id = batch[-1]["id"]
        save_checkpoint(checkpoint_path, last_id)

        await asyncio.sleep(sleep_time)  # async-friendly sleep

    logging.info(f"Data ingestion completed successfully. Total processed: {total_processed}")


def run_pipeline():
    dataset_path = config["dataset"]["path"]
    batch_size = config["openai"]["batch_size"]
    sleep_time = config["openai"].get("sleep_between_batches", 1)
    checkpoint_path = Path(config["dataset"].get("checkpoint_path", "checkpoint.txt"))

    check_qdrant_collection(config["qdrant"])  # ensure qdrant is ready

    if checkpoint_path.exists():
        last_processed = load_checkpoint(checkpoint_path)
        logging.info(f"Resuming from checkpoint: {last_processed}")
    else:
        checkpoint_path.touch()
        last_processed = None
        logging.info("No checkpoint found. Starting from scratch.")

    logging.info(f"Starting streaming ingestion with batch size {batch_size}")

    try:
        asyncio.run(run_pipeline_async(dataset_path, batch_size, checkpoint_path, sleep_time, last_processed))
    except KeyboardInterrupt:
        logging.warning("Pipeline interrupted by user.")
    finally:
        EXECUTOR.shutdown(wait=True)
        logging.info("Thread pool shut down.")
