import logging
import os
from supabase import create_client, Client
from typing import Dict, Any

def get_supabase_client(config: Dict[str, Any]) -> Client:
    """ Initializes and returns a Supabase client. """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    return create_client(url, key)

def store_metadata_supabase(paper: Dict[str, Any], config: Dict[str, Any]):
    """
    Store metadata for a single paper in Supabase.
    Expected Supabase table schema:
        id (text, primary key)
        title (text)
        authors (text)
        categories (text)
        abstract (text)
        update_date (date)
        doi (text)
    """
    supabase = get_supabase_client(config)

    try:
        data = {
            "id": paper.get("id"),
            "title": paper.get("title"),
            "authors": paper.get("authors"),
            "categories": paper.get("categories"),
            "abstract": paper.get("abstract"),
            "update_date": paper.get("update_date"),
            "doi": paper.get("doi"),
        }

        # insert with upsert=True so we don't duplicate papers
        response = supabase.table(config["table"]).upsert(data).execute()

        if hasattr(response, "error") and response.error:
            logging.error(f"Supabase insert error for {paper.get('id')}: {response.error}")
        else:
            logging.info(f"Stored metadata for paper {paper.get('id')}")
    except Exception as e:
        logging.error(f"Failed to store metadata for {paper.get('id')}: {e}")
