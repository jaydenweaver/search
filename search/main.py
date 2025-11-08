from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from qdrant_client import QdrantClient
import openai
import os
import yaml
from dotenv import load_dotenv
import asyncio

load_dotenv()

# load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="Paperfind API")

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

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

class SearchResult(BaseModel):
    id: str
    title: str
    authors: list
    abstract: str
    score: float

@app.get("/search", response_model=list[SearchResult])
async def search_papers(query: str = Query(..., min_length=3, description="Search query")):
    try:
        # generate embedding from query
        response = await openai.embeddings.create(
            model=config["openai"]["model"],
            input=query
        )
        vector = response.data[0].embedding

        # qdrant search
        results = qdrant.search(
            collection_name=config["qdrant"]["collection_name"],
            query_vector=vector,
            limit=10,
            with_payload=True
        )

        # get paper id's
        paper_ids = [res.payload.get("id") for res in results if res.payload.get("id")]

        if not paper_ids:
            return []

        # fetch metadata from supabase
        def fetch_metadata():
            response = (
                supabase.table(config["supabase"]["papers_table"])
                .select("id, title, authors, abstract")
                .in_("id", paper_ids)
                .execute()
            )
            return response.data or []

        metadata_list = await asyncio.to_thread(fetch_metadata)

        metadata_hash = {p["id"]: p for p in metadata_list}

        # merge results
        combined_results = []
        for res in results:
            pid = res.payload.get("id")
            if not pid or pid not in metadata_hash:
                continue
            meta = metadata_hash[pid]
            combined_results.append(
                SearchResult(
                    id=pid,
                    title=meta.get("title", ""),
                    authors=meta.get("authors", []),
                    abstract=meta.get("abstract", ""),
                    score=res.score
                )
            )

        return combined_results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
