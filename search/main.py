from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from openai import AsyncOpenAI, APIError, RateLimitError
from exception_handlers import register_exception_handlers
from exceptions import ExternalServiceError, RateLimitExceeded, NotFoundError
import os
import yaml
from dotenv import load_dotenv
import asyncio
import inspect
import random
import httpx
import time

load_dotenv()

# load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="Paperfind API")
register_exception_handlers(app)

# cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with frontend url later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# fetch metadata from supabase
async def fetch_metadata(paper_ids):
    ids_filter = ",".join(paper_ids)
    url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?id=in.({ids_filter})&select=id,title,authors,abstract"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        return data
    
async def retry_async(func, *args, **kwargs):
    max_retries = config.get("max_retries", 3)
    base_delay = config.get("base_delay", 0.5)

    for attempt in range(max_retries):
        try:
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                # run sync functions in a thread pool to avoid blocking
                return await asyncio.to_thread(func, *args, **kwargs)
            
        except RateLimitError as e:
            raise RateLimitExceeded(str(e)) from e
        
        except Exception as e:
            if attempt == max_retries - 1 or not isinstance(e, retry_exceptions) :
                raise ExternalServiceError(f"{func.__name__} failed after {max_retries} retries: {e}") from e

            # exponential backoff + jitter
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.1)
            print(f"[WARN] Attempt {attempt+1}/{max_retries} failed for {func.__name__}: {e}. Retrying in {delay:.2f}s...")
            await asyncio.sleep(delay)

@app.get("/search", response_model=list[SearchResult])
async def search_papers(query: str = Query(..., min_length=3, description="Search query")):
    start_total = time.time()

    # openai embedding
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

    # get paper ids
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

    # merge results
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