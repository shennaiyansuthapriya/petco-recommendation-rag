"""
Pet product CRUD endpoints — /api/v1/products
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.product import LifeStage, PetProduct, PetType, ProductCategory

router = APIRouter(prefix="/products", tags=["products"])


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=500)
    brand: str
    category: ProductCategory
    pet_type: PetType
    life_stage: LifeStage = LifeStage.ALL_STAGES
    sku: str | None = None
    description: str | None = None
    ingredients: str | None = None
    health_benefits: str | None = None
    suitable_for_conditions: list[str] | None = None
    vet_recommended: bool = False
    grain_free: bool = False
    primary_protein: str | None = None
    protein_pct: float | None = None
    fat_pct: float | None = None
    fiber_pct: float | None = None
    calories_per_cup: int | None = None
    price_usd: float | None = None


class ProductResponse(BaseModel):
    id: UUID
    name: str
    brand: str
    pet_type: str
    category: str
    life_stage: str
    sku: str | None
    price_usd: float | None
    vet_recommended: bool
    is_indexed: bool

    class Config:
        from_attributes = True


@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(body: ProductCreate, db: AsyncSession = Depends(get_db)) -> ProductResponse:
    product = PetProduct(**body.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return ProductResponse(
        id=product.id,
        name=product.name,
        brand=product.brand,
        pet_type=product.pet_type.value,
        category=product.category.value,
        life_stage=product.life_stage.value,
        sku=product.sku,
        price_usd=product.price_usd,
        vet_recommended=product.vet_recommended,
        is_indexed=product.is_indexed,
    )


@router.get("/", response_model=list[ProductResponse])
async def list_products(
    pet_type: str | None = Query(None),
    category: str | None = Query(None),
    life_stage: str | None = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[ProductResponse]:
    stmt = select(PetProduct).limit(limit)
    if pet_type:
        stmt = stmt.where(PetProduct.pet_type == pet_type)
    if category:
        stmt = stmt.where(PetProduct.category == category)
    if life_stage:
        stmt = stmt.where(PetProduct.life_stage == life_stage)
    result = await db.execute(stmt)
    products = result.scalars().all()
    return [
        ProductResponse(
            id=p.id,
            name=p.name,
            brand=p.brand,
            pet_type=p.pet_type.value,
            category=p.category.value,
            life_stage=p.life_stage.value,
            sku=p.sku,
            price_usd=p.price_usd,
            vet_recommended=p.vet_recommended,
            is_indexed=p.is_indexed,
        )
        for p in products
    ]
