"""
Pet product catalog + care guide models — Petco.com mirror.
Domain: Pet supplies with health-aware recommendation context.
"""
import enum, uuid
from typing import Optional
from datetime import datetime
from sqlalchemy import Boolean, Enum, Float, Index, Integer, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PetType(str, enum.Enum):
    DOG = "dog"
    CAT = "cat"
    FISH = "fish"
    BIRD = "bird"
    REPTILE = "reptile"
    SMALL_ANIMAL = "small_animal"
    ALL = "all"


class ProductCategory(str, enum.Enum):
    FOOD_DRY = "food_dry"
    FOOD_WET = "food_wet"
    FOOD_RAW = "food_raw"
    TREATS = "treats"
    SUPPLEMENTS = "supplements"
    TOYS = "toys"
    BEDS = "beds"
    CARRIERS = "carriers"
    GROOMING = "grooming"
    HEALTH_WELLNESS = "health_wellness"
    TRAINING = "training"
    AQUATICS = "aquatics"
    OTHER = "other"


class LifeStage(str, enum.Enum):
    PUPPY_KITTEN = "puppy_kitten"
    ADULT = "adult"
    SENIOR = "senior"
    ALL_STAGES = "all_stages"


class PetProduct(Base):
    __tablename__ = "pet_products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    sku: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[ProductCategory] = mapped_column(Enum(ProductCategory), nullable=False, index=True)
    pet_type: Mapped[PetType] = mapped_column(Enum(PetType), nullable=False, index=True)
    life_stage: Mapped[LifeStage] = mapped_column(Enum(LifeStage), default=LifeStage.ALL_STAGES, index=True)

    # Descriptions for RAG
    description: Mapped[Optional[str]] = mapped_column(Text)
    ingredients: Mapped[Optional[str]] = mapped_column(Text)
    guaranteed_analysis: Mapped[Optional[str]] = mapped_column(Text)
    feeding_guidelines: Mapped[Optional[str]] = mapped_column(Text)
    health_benefits: Mapped[Optional[str]] = mapped_column(Text)

    # Health context — for health-aware recommendations
    suitable_for_conditions: Mapped[Optional[list]] = mapped_column(JSONB, default=list)  # ["joint_issues", "kidney_disease"]
    breed_specific: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    vet_recommended: Mapped[bool] = mapped_column(Boolean, default=False)
    prescription_required: Mapped[bool] = mapped_column(Boolean, default=False)

    # Nutrition (for food products)
    protein_pct: Mapped[Optional[float]] = mapped_column(Float)
    fat_pct: Mapped[Optional[float]] = mapped_column(Float)
    fiber_pct: Mapped[Optional[float]] = mapped_column(Float)
    calories_per_cup: Mapped[Optional[int]] = mapped_column(Integer)
    grain_free: Mapped[bool] = mapped_column(Boolean, default=False)
    primary_protein: Mapped[Optional[str]] = mapped_column(String(100))

    price_usd: Mapped[Optional[float]] = mapped_column(Float, index=True)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    is_indexed: Mapped[bool] = mapped_column(Boolean, default=False)
    qdrant_point_ids: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    rating: Mapped[Optional[float]] = mapped_column(Float)
    review_count: Mapped[Optional[int]] = mapped_column(Integer)

    __table_args__ = (
        Index("ix_pet_product_type_cat", "pet_type", "category"),
        Index("ix_pet_product_stage", "life_stage", "pet_type"),
    )


class PetCareGuide(Base):
    __tablename__ = "pet_care_guides"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    pet_type: Mapped[PetType] = mapped_column(Enum(PetType), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String(100), index=True)  # "nutrition", "health", "training"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    qdrant_point_ids: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    is_indexed: Mapped[bool] = mapped_column(Boolean, default=False)


class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    query: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[Optional[str]] = mapped_column(Text)
    recommended_skus: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer)
    pet_type_filter: Mapped[Optional[str]] = mapped_column(String(20))
    health_condition: Mapped[Optional[str]] = mapped_column(String(100))
