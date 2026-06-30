"""
Qdrant vector store for Petco pet product + care guide collections.
Mirrors the healthcare-payer-rag Qdrant pattern with two collections.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from openai import AsyncOpenAI
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.config import get_settings

settings = get_settings()


@dataclass
class QdrantResult:
    point_id: str
    score: float
    payload: dict = field(default_factory=dict)
    text: str = ""


class PetcoQdrantStore:
    """
    Two Qdrant collections:
      - petco_products   : product catalog chunks
      - petco_care_guides: care guide paragraphs
    """

    def __init__(self) -> None:
        self._client = AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)
        self._openai = AsyncOpenAI(api_key=settings.openai_api_key)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def ensure_collections(self) -> None:
        existing = {c.name for c in (await self._client.get_collections()).collections}
        vec_params = VectorParams(size=settings.qdrant_vector_size, distance=Distance.COSINE)

        for col in (settings.qdrant_collection_products, settings.qdrant_collection_guides):
            if col not in existing:
                await self._client.create_collection(collection_name=col, vectors_config=vec_params)

    # ------------------------------------------------------------------
    # Embedding
    # ------------------------------------------------------------------

    async def _embed(self, texts: list[str]) -> list[list[float]]:
        response = await self._openai.embeddings.create(
            model=settings.openai_embedding_model,
            input=texts,
        )
        return [e.embedding for e in response.data]

    # ------------------------------------------------------------------
    # Upsert
    # ------------------------------------------------------------------

    async def upsert_product_chunks(self, chunks: list[dict[str, Any]]) -> list[str]:
        """
        chunks: [{"text": str, "payload": {...}}]
        Returns list of point_ids upserted.
        """
        texts = [c["text"] for c in chunks]
        embeddings = await self._embed(texts)

        points: list[PointStruct] = []
        point_ids: list[str] = []
        for chunk, vec in zip(chunks, embeddings):
            pid = str(uuid.uuid4())
            point_ids.append(pid)
            payload = chunk.get("payload", {})
            payload["text"] = chunk["text"]
            points.append(PointStruct(id=pid, vector=vec, payload=payload))

        await self._client.upsert(collection_name=settings.qdrant_collection_products, points=points)
        return point_ids

    async def upsert_guide_chunks(self, chunks: list[dict[str, Any]]) -> list[str]:
        texts = [c["text"] for c in chunks]
        embeddings = await self._embed(texts)

        points: list[PointStruct] = []
        point_ids: list[str] = []
        for chunk, vec in zip(chunks, embeddings):
            pid = str(uuid.uuid4())
            point_ids.append(pid)
            payload = chunk.get("payload", {})
            payload["text"] = chunk["text"]
            points.append(PointStruct(id=pid, vector=vec, payload=payload))

        await self._client.upsert(collection_name=settings.qdrant_collection_guides, points=points)
        return point_ids

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    async def search_products(
        self,
        query: str,
        top_k: int = 20,
        pet_type: str | None = None,
        category: str | None = None,
        life_stage: str | None = None,
    ) -> list[QdrantResult]:
        query_vec = (await self._embed([query]))[0]

        conditions: list[FieldCondition] = []
        if pet_type:
            conditions.append(FieldCondition(key="pet_type", match=MatchValue(value=pet_type)))
        if category:
            conditions.append(FieldCondition(key="category", match=MatchValue(value=category)))
        if life_stage:
            conditions.append(FieldCondition(key="life_stage", match=MatchValue(value=life_stage)))

        query_filter = Filter(must=conditions) if conditions else None

        hits = await self._client.search(
            collection_name=settings.qdrant_collection_products,
            query_vector=query_vec,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
        )

        return [
            QdrantResult(
                point_id=str(h.id),
                score=h.score,
                payload=h.payload or {},
                text=(h.payload or {}).get("text", ""),
            )
            for h in hits
        ]

    async def search_guides(self, query: str, top_k: int = 10, pet_type: str | None = None) -> list[QdrantResult]:
        query_vec = (await self._embed([query]))[0]
        conditions = [FieldCondition(key="pet_type", match=MatchValue(value=pet_type))] if pet_type else []
        query_filter = Filter(must=conditions) if conditions else None

        hits = await self._client.search(
            collection_name=settings.qdrant_collection_guides,
            query_vector=query_vec,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
        )
        return [
            QdrantResult(
                point_id=str(h.id),
                score=h.score,
                payload=h.payload or {},
                text=(h.payload or {}).get("text", ""),
            )
            for h in hits
        ]


_store: PetcoQdrantStore | None = None


def get_qdrant_store() -> PetcoQdrantStore:
    global _store
    if _store is None:
        _store = PetcoQdrantStore()
    return _store
