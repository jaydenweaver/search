import logging
import os
from supabase import create_client, Client
from typing import Dict, Any, List

def get_supabase_client(config: Dict[str, Any]) -> Client:
    """ Initializes and returns a Supabase client. """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    return create_client(url, key)

def store_metadata_supabase(batch: List[Dict[str, Any]], config: Dict[str, Any]):
    """
    Store metadata for a batch of papers in Supabase.
    Expected Supabase table schema:
        id (text, primary key)
        title (text)
        authors (text)
        categories (text)
        abstract (text)
        update_date (date)
        doi (text)
    Uses upsert to avoid duplicating papers.
    """
    supabase = get_supabase_client(config)

    try:
        # prepare batch data in the correct format
        data_batch = [
            {
                "id": paper.get("id"),
                "title": paper.get("title"),
                "authors": paper.get("authors"),
                "categories": paper.get("categories"),
                "abstract": paper.get("abstract"),
                "update_date": paper.get("update_date"),
                "doi": paper.get("doi"),
            }
            for paper in batch
        ]

        # upsert the entire batch at once
        response = supabase.table(config["papers_table"]).upsert(data_batch).execute()

        if hasattr(response, "error") and response.error:
            logging.error(f"Supabase batch insert error: {response.error}")
        else:
            logging.info(f"Stored metadata for batch of {len(batch)} papers")

    except Exception as e:
        logging.error(f"Failed to store metadata batch: {e}")
