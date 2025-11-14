import os
import json
import yaml
import asyncio
import random
import time
import httpx
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from openai import AsyncOpenAI, APIError, RateLimitError

# load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
TABLE_NAME = config["supabase"]["papers_table"]

retry_exceptions = (
    TimeoutError,
    ConnectionError,
    httpx.ConnectError,
    httpx.ReadTimeout,
    APIError,
    RateLimitError,
    UnexpectedResponse,
)

class SearchResult(BaseModel):
    id: str
    title: str
    authors: str
    abstract: str
    score: float

# exceptions
class SearchError(Exception):
    status_code = 500
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class BadRequestError(SearchError):
    status_code = 400

class NotFoundError(SearchError):
    status_code = 404

class ExternalServiceError(SearchError):
    status_code = 502

class RateLimitExceeded(SearchError):
    status_code = 429

# fetch metadata from Supabase
async def fetch_metadata(paper_ids):
    ids_filter = ",".join(paper_ids)
    url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?id=in.({ids_filter})&select=id,title,authors,abstract"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, timeout=10.0)
        resp.raise_for_status()
        return resp.json()

# retry helper
async def retry_async(func, *args, **kwargs):
    max_retries = config.get("max_retries", 3)
    base_delay = config.get("base_delay", 0.5)
    for attempt in range(max_retries):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return await asyncio.to_thread(func, *args, **kwargs)
        except RateLimitError as e:
            raise RateLimitExceeded(f"Rate limit exceeded: {e}") from e
        except Exception as e:
            if attempt == max_retries - 1 or not isinstance(e, retry_exceptions):
                raise ExternalServiceError(f"{func.__name__} failed after {max_retries} retries: {e}") from e
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.1)
            print(f"[WARN] Attempt {attempt+1}/{max_retries} failed for {func.__name__}: {e}. Retrying in {delay:.2f}s...")
            await asyncio.sleep(delay)

# search
async def perform_search(query: str) -> list[SearchResult]:
    if not query or len(query) < 3:
        raise BadRequestError("Query must be at least 3 characters.")

    start_total = time.time()

    # embeddings
    start_openai = time.time()
    response = await retry_async(
        openai_client.embeddings.create,
        model=config["openai"]["model"],
        input=query
    )
    vector = response.data[0].embedding
    openai_time = time.time() - start_openai

    # qdrant search
    start_qdrant = time.time()
    results = await retry_async(
        qdrant.search,
        collection_name=config["qdrant"]["collection_name"],
        query_vector=vector,
        limit=10,
        with_payload=True
    )
    qdrant_time = time.time() - start_qdrant

    paper_ids = [res.payload.get("paper_id") for res in results if res.payload.get("paper_id")]

    if not paper_ids:
        total_time = time.time() - start_total
        print(f"[TIMING] OpenAI: {openai_time:.2f}s, Qdrant: {qdrant_time:.2f}s, Metadata: 0.00s, Total: {total_time:.2f}s")
        raise NotFoundError("No papers found for this query.")

    # fetch metadata
    start_supabase = time.time()
    metadata_list = await retry_async(fetch_metadata, paper_ids)
    supabase_time = time.time() - start_supabase

    metadata_map = {p["id"]: p for p in metadata_list}

    combined_results = []
    for res in results:
        pid = res.payload.get("paper_id")
        if not pid or pid not in metadata_map:
            continue
        meta = metadata_map[pid]
        combined_results.append(
            SearchResult(
                id=pid,
                title=meta.get("title", ""),
                authors=meta.get("authors", ""),
                abstract=meta.get("abstract", ""),
                score=res.score
            )
        )

    total_time = time.time() - start_total
    print(f"[TIMING] OpenAI: {openai_time:.2f}s, Qdrant: {qdrant_time:.2f}s, Metadata: {supabase_time:.2f}s, Total: {total_time:.2f}s")

    return combined_results

# lambda handler
def lambda_handler(event, context):
    try:
        query = event.get("queryStringParameters", {}).get("query")
        if not query:
            raise BadRequestError("Missing query parameter")

        results = asyncio.run(perform_search(query))
        results_json = [r.dict() for r in results]

        return {"statusCode": 200, "body": json.dumps(results_json)}

    except SearchError as e:
        print(f"[ERROR] {e.message}")
        return {"statusCode": e.status_code, "body": json.dumps({"error": e.message})}

    except Exception as e:
        print(f"[ERROR] {e}")
        return {"statusCode": 500, "body": json.dumps({"error": "Internal server error"})}
