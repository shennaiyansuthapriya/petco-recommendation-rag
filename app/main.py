"""
Petco Pet Product Recommendation RAG — FastAPI application entry point.
Qdrant ANN + Cohere Rerank v3 retrieval with GPT-4o synthesis via LlamaIndex.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api.v1 import products as products_router
from app.api.v1 import recommendations as rec_router
from app.config import get_settings
from app.core.vectorstore import get_qdrant_store

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Ensure Qdrant collections exist at startup
    store = get_qdrant_store()
    await store.ensure_collections()
    yield


app = FastAPI(
    title="Petco Pet Product Recommendation RAG",
    description=(
        "Health-aware pet product recommendation powered by Qdrant vector search, "
        "Cohere Rerank v3 cross-encoder re-ranking, and GPT-4o synthesis."
    ),
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rec_router.router, prefix="/api/v1")
app.include_router(products_router.router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }
