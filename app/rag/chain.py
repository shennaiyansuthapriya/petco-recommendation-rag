"""
Petco RAG chain — Qdrant ANN + Cohere Rerank v3 → GPT-4o synthesis.
Uses LlamaIndex OpenAI LLM wrapper consistent with the healthcare-payer-rag pattern.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from llama_index.llms.openai import OpenAI as LlamaOpenAI

from app.config import get_settings
from app.core.retriever import PetcoRetriever, RankedResult, get_retriever
from app.rag.prompts import (
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
    build_context,
    build_filter_context,
)

settings = get_settings()


@dataclass
class RecommendationResult:
    query: str
    answer: str
    sources: list[dict] = field(default_factory=list)
    latency_ms: int = 0
    top_k_retrieved: int = 0


class PetcoRAGChain:
    """
    Two-stage retrieval (Qdrant → Cohere Rerank) + GPT-4o synthesis.
    LlamaIndex OpenAI LLM used for synthesis consistent with the LlamaIndex stack.
    """

    def __init__(self, retriever: PetcoRetriever | None = None) -> None:
        self._retriever = retriever or get_retriever()
        self._llm = LlamaOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=settings.openai_temperature,
        )

    async def recommend(
        self,
        query: str,
        top_k: int | None = None,
        pet_type: str | None = None,
        category: str | None = None,
        life_stage: str | None = None,
        health_condition: str | None = None,
    ) -> RecommendationResult:
        t0 = time.monotonic()

        ranked: list[RankedResult] = await self._retriever.retrieve(
            query=query,
            top_k=top_k or settings.retrieval_top_k,
            pet_type=pet_type,
            category=category,
            life_stage=life_stage,
        )

        result_dicts = [
            {
                "text": r.text,
                "metadata": r.metadata,
                "cohere_relevance_score": r.cohere_relevance_score,
                "source": r.metadata.get("source", "product"),
            }
            for r in ranked
        ]
        context = build_context(result_dicts)
        filter_ctx = build_filter_context(pet_type, health_condition)

        full_prompt = (
            f"System: {SYSTEM_PROMPT}\n\n"
            + USER_PROMPT_TEMPLATE.format(context=context, query=query, filter_context=filter_ctx)
        )

        response = await self._llm.acomplete(full_prompt)
        answer = str(response)

        latency_ms = int((time.monotonic() - t0) * 1000)

        sources = [
            {
                "name": r.metadata.get("name"),
                "brand": r.metadata.get("brand"),
                "sku": r.metadata.get("sku"),
                "pet_type": r.metadata.get("pet_type"),
                "cohere_score": round(r.cohere_relevance_score, 4),
            }
            for r in ranked
        ]

        return RecommendationResult(
            query=query,
            answer=answer,
            sources=sources,
            latency_ms=latency_ms,
            top_k_retrieved=len(ranked),
        )
