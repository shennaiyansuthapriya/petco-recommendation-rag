"""
Product catalog and care guide ingestion for Petco recommendation RAG.
Loads from JSON/CSV, embeds with OpenAI, upserts to Qdrant.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI

from app.config import get_settings
from app.core.vectorstore import get_qdrant_store

settings = get_settings()


def _build_product_chunk_text(product: dict[str, Any]) -> str:
    """Rich text for embedding — includes name, brand, nutritional info, health context."""
    parts: list[str] = []
    if product.get("name"):
        parts.append(f"Product: {product['name']}")
    if product.get("brand"):
        parts.append(f"Brand: {product['brand']}")
    if product.get("pet_type"):
        parts.append(f"For: {product['pet_type']}s")
    if product.get("life_stage"):
        parts.append(f"Life stage: {product['life_stage']}")
    if product.get("category"):
        parts.append(f"Category: {product['category']}")
    if product.get("description"):
        parts.append(product["description"])
    if product.get("health_benefits"):
        parts.append(f"Health benefits: {product['health_benefits']}")
    if product.get("ingredients"):
        parts.append(f"Ingredients: {product['ingredients'][:300]}")
    if product.get("guaranteed_analysis"):
        parts.append(f"Guaranteed analysis: {product['guaranteed_analysis']}")
    if product.get("feeding_guidelines"):
        parts.append(f"Feeding guidelines: {product['feeding_guidelines']}")
    # Nutritional specs
    specs = []
    if product.get("protein_pct"):
        specs.append(f"protein {product['protein_pct']}%")
    if product.get("fat_pct"):
        specs.append(f"fat {product['fat_pct']}%")
    if product.get("fiber_pct"):
        specs.append(f"fiber {product['fiber_pct']}%")
    if product.get("calories_per_cup"):
        specs.append(f"{product['calories_per_cup']} kcal/cup")
    if specs:
        parts.append("Nutrition: " + ", ".join(specs))
    if product.get("grain_free"):
        parts.append("Grain-free")
    if product.get("primary_protein"):
        parts.append(f"Primary protein: {product['primary_protein']}")
    if product.get("suitable_for_conditions"):
        conditions = product["suitable_for_conditions"]
        if conditions:
            parts.append(f"Suitable for: {', '.join(conditions)}")
    if product.get("vet_recommended"):
        parts.append("Vet recommended")
    return ". ".join(parts)


def _build_guide_chunk_text(guide: dict[str, Any]) -> str:
    return (
        f"Care Guide — {guide.get('pet_type', '')} — {guide.get('topic', '')}: "
        f"{guide.get('title', '')}\n{guide.get('content', '')}"
    )


async def index_product(product: dict[str, Any]) -> list[str]:
    """Embed and upsert a single product to Qdrant. Returns point_ids."""
    store = get_qdrant_store()
    text = _build_product_chunk_text(product)

    # Chunk large descriptions
    chunks = _split_chunks(text)
    chunk_dicts = [
        {
            "text": chunk,
            "payload": {
                "sku": product.get("sku"),
                "name": product.get("name"),
                "brand": product.get("brand"),
                "pet_type": product.get("pet_type"),
                "category": product.get("category"),
                "life_stage": product.get("life_stage"),
                "protein_pct": product.get("protein_pct"),
                "fat_pct": product.get("fat_pct"),
                "calories_per_cup": product.get("calories_per_cup"),
                "price_usd": product.get("price_usd"),
                "vet_recommended": product.get("vet_recommended", False),
                "grain_free": product.get("grain_free", False),
                "primary_protein": product.get("primary_protein"),
            },
        }
        for chunk in chunks
    ]

    return await store.upsert_product_chunks(chunk_dicts)


async def index_care_guide(guide: dict[str, Any]) -> list[str]:
    store = get_qdrant_store()
    text = _build_guide_chunk_text(guide)
    chunks = _split_chunks(text, max_chars=1800)
    chunk_dicts = [
        {
            "text": chunk,
            "payload": {
                "title": guide.get("title"),
                "pet_type": guide.get("pet_type"),
                "topic": guide.get("topic"),
                "source": "care_guide",
            },
        }
        for chunk in chunks
    ]
    return await store.upsert_guide_chunks(chunk_dicts)


def _split_chunks(text: str, max_chars: int = 2000, overlap_chars: int = 150) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap_chars
    return chunks


async def load_products_from_json(filepath: str) -> int:
    path = Path(filepath)
    with open(path) as f:
        products: list[dict] = json.load(f)
    store = get_qdrant_store()
    await store.ensure_collections()
    count = 0
    for product in products:
        await index_product(product)
        count += 1
    return count


async def load_guides_from_json(filepath: str) -> int:
    path = Path(filepath)
    with open(path) as f:
        guides: list[dict] = json.load(f)
    store = get_qdrant_store()
    await store.ensure_collections()
    count = 0
    for guide in guides:
        await index_care_guide(guide)
        count += 1
    return count
