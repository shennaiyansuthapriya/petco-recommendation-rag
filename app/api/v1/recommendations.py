"""
Pet product recommendation endpoints — /api/v1/recommendations
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.recommendation_service import PetProductRecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class RecommendRequest(BaseModel):
    query: str = Field(..., min_length=5, max_length=500)
    pet_type: str | None = None
    category: str | None = None
    life_stage: str | None = None
    health_condition: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)


class RecommendResponse(BaseModel):
    query: str
    answer: str
    sources: list[dict[str, Any]]
    latency_ms: int
    top_k_retrieved: int


@router.post("/", response_model=RecommendResponse)
async def recommend(request: RecommendRequest, db: AsyncSession = Depends(get_db)) -> RecommendResponse:
    """
    Qdrant ANN + Cohere Rerank + GPT-4o pet product recommendation.
    Health-condition aware — e.g. 'high-protein food for senior dog with kidney disease'.
    """
    service = PetProductRecommendationService(db)
    result = await service.recommend(
        query=request.query,
        pet_type=request.pet_type,
        category=request.category,
        life_stage=request.life_stage,
        health_condition=request.health_condition,
        top_k=request.top_k,
    )
    return RecommendResponse(
        query=result.query,
        answer=result.answer,
        sources=result.sources,
        latency_ms=result.latency_ms,
        top_k_retrieved=result.top_k_retrieved,
    )


@router.post("/products/{product_id}/index")
async def index_product(product_id: UUID, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    service = PetProductRecommendationService(db)
    try:
        return await service.index_product_by_id(str(product_id))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/guides/{guide_id}/index")
async def index_guide(guide_id: UUID, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    service = PetProductRecommendationService(db)
    try:
        return await service.index_guide_by_id(str(guide_id))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/index/stats")
async def index_stats(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    service = PetProductRecommendationService(db)
    return await service.get_index_stats()
