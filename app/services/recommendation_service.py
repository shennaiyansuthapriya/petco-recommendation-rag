"""
Recommendation service — orchestrates indexing and RAG queries for Petco products.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.vectorstore import get_qdrant_store
from app.ingestion.product_loader import index_care_guide, index_product
from app.models.product import PetCareGuide, PetProduct, RecommendationLog
from app.rag.chain import PetcoRAGChain, RecommendationResult


class PetProductRecommendationService:

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._chain = PetcoRAGChain()

    async def recommend(
        self,
        query: str,
        pet_type: str | None = None,
        category: str | None = None,
        life_stage: str | None = None,
        health_condition: str | None = None,
        top_k: int = 5,
    ) -> RecommendationResult:
        result = await self._chain.recommend(
            query=query,
            top_k=top_k,
            pet_type=pet_type,
            category=category,
            life_stage=life_stage,
            health_condition=health_condition,
        )

        log = RecommendationLog(
            query=query,
            answer=result.answer,
            recommended_skus=[s.get("sku") for s in result.sources],
            latency_ms=result.latency_ms,
            pet_type_filter=pet_type,
            health_condition=health_condition,
        )
        self._db.add(log)
        await self._db.commit()

        return result

    async def index_product_by_id(self, product_id: str) -> dict[str, Any]:
        stmt = select(PetProduct).where(PetProduct.id == product_id)
        result = await self._db.execute(stmt)
        product = result.scalar_one_or_none()
        if not product:
            raise ValueError(f"Product {product_id} not found")

        product_dict = {
            "sku": product.sku,
            "name": product.name,
            "brand": product.brand,
            "pet_type": product.pet_type.value if product.pet_type else None,
            "category": product.category.value if product.category else None,
            "life_stage": product.life_stage.value if product.life_stage else None,
            "description": product.description,
            "ingredients": product.ingredients,
            "guaranteed_analysis": product.guaranteed_analysis,
            "feeding_guidelines": product.feeding_guidelines,
            "health_benefits": product.health_benefits,
            "suitable_for_conditions": product.suitable_for_conditions,
            "vet_recommended": product.vet_recommended,
            "grain_free": product.grain_free,
            "primary_protein": product.primary_protein,
            "protein_pct": product.protein_pct,
            "fat_pct": product.fat_pct,
            "fiber_pct": product.fiber_pct,
            "calories_per_cup": product.calories_per_cup,
            "price_usd": product.price_usd,
        }

        point_ids = await index_product(product_dict)

        await self._db.execute(
            update(PetProduct)
            .where(PetProduct.id == product_id)
            .values(is_indexed=True, qdrant_point_ids=point_ids)
        )
        await self._db.commit()

        return {"product_id": str(product_id), "qdrant_point_ids": point_ids, "indexed": True}

    async def index_guide_by_id(self, guide_id: str) -> dict[str, Any]:
        stmt = select(PetCareGuide).where(PetCareGuide.id == guide_id)
        result = await self._db.execute(stmt)
        guide = result.scalar_one_or_none()
        if not guide:
            raise ValueError(f"Guide {guide_id} not found")

        guide_dict = {
            "title": guide.title,
            "pet_type": guide.pet_type.value if guide.pet_type else None,
            "topic": guide.topic,
            "content": guide.content,
        }
        point_ids = await index_care_guide(guide_dict)

        await self._db.execute(
            update(PetCareGuide)
            .where(PetCareGuide.id == guide_id)
            .values(is_indexed=True, qdrant_point_ids=point_ids)
        )
        await self._db.commit()
        return {"guide_id": str(guide_id), "qdrant_point_ids": point_ids, "indexed": True}

    async def get_index_stats(self) -> dict[str, Any]:
        store = get_qdrant_store()
        from qdrant_client import AsyncQdrantClient
        from app.config import get_settings
        cfg = get_settings()
        client = AsyncQdrantClient(url=cfg.qdrant_url)
        prod_info = await client.get_collection(cfg.qdrant_collection_products)
        guide_info = await client.get_collection(cfg.qdrant_collection_guides)
        return {
            "products_vectors": prod_info.vectors_count,
            "guides_vectors": guide_info.vectors_count,
            "rerank_model": cfg.cohere_rerank_model,
            "embedding_model": cfg.openai_embedding_model,
        }
