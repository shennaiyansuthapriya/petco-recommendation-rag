"""
Two-stage retriever for Petco pet product recommendation.
Stage 1: Qdrant ANN search (top_k * 3 candidates)
Stage 2: Cohere Rerank v3 cross-encoder re-ranking

Mirrors the healthcare-payer-rag retriever pattern.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import cohere
from cohere import RerankResponse

from app.config import get_settings
from app.core.vectorstore import PetcoQdrantStore, QdrantResult, get_qdrant_store

settings = get_settings()


@dataclass
class RankedResult:
    point_id: str
    qdrant_score: float
    cohere_relevance_score: float
    metadata: dict = field(default_factory=dict)
    text: str = ""

    @property
    def final_score(self) -> float:
        return self.cohere_relevance_score


class PetcoRetriever:
    """
    Qdrant → Cohere Rerank v3 retrieval pipeline.
    Retrieves from both product and care-guide collections,
    then re-ranks the combined candidate set.
    """

    def __init__(self, store: PetcoQdrantStore | None = None) -> None:
        self._store = store or get_qdrant_store()
        self._cohere = cohere.AsyncClientV2(api_key=settings.cohere_api_key)

    async def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        pet_type: str | None = None,
        category: str | None = None,
        life_stage: str | None = None,
        include_guides: bool = True,
    ) -> list[RankedResult]:
        top_k = top_k or settings.retrieval_top_k
        candidate_k = top_k * 3

        # Stage 1 — ANN search
        product_hits = await self._store.search_products(
            query=query,
            top_k=candidate_k,
            pet_type=pet_type,
            category=category,
            life_stage=life_stage,
        )
        guide_hits: list[QdrantResult] = []
        if include_guides:
            guide_hits = await self._store.search_guides(query=query, top_k=10, pet_type=pet_type)

        all_hits: list[QdrantResult] = product_hits + guide_hits
        if not all_hits:
            return []

        # Stage 2 — Cohere Rerank v3
        rerank_docs = [h.text for h in all_hits]
        rerank_response: RerankResponse = await self._cohere.rerank(
            model=settings.cohere_rerank_model,
            query=query,
            documents=rerank_docs,
            top_n=min(settings.rerank_top_n, len(rerank_docs)),
        )

        ranked: list[RankedResult] = []
        for item in rerank_response.results:
            original = all_hits[item.index]
            ranked.append(
                RankedResult(
                    point_id=original.point_id,
                    qdrant_score=original.score,
                    cohere_relevance_score=item.relevance_score,
                    metadata=original.payload,
                    text=original.text,
                )
            )

        ranked.sort(key=lambda r: r.cohere_relevance_score, reverse=True)
        return ranked[:top_k]


_retriever: PetcoRetriever | None = None


def get_retriever() -> PetcoRetriever:
    global _retriever
    if _retriever is None:
        _retriever = PetcoRetriever()
    return _retriever
