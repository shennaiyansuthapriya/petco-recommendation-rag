"""
Unit tests for Petco Qdrant + Cohere Rerank retriever.
Tests use mocks to avoid requiring live API keys.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.retriever import PetcoRetriever, RankedResult
from app.core.vectorstore import QdrantResult


@pytest.fixture
def mock_qdrant_results() -> list[QdrantResult]:
    return [
        QdrantResult(
            point_id="p1",
            score=0.92,
            payload={"sku": "RC-ADU-LB-15", "name": "Royal Canin Large Breed", "pet_type": "dog", "category": "food_dry"},
            text="Royal Canin Large Breed Adult food for dogs over 55 lbs with joint support",
        ),
        QdrantResult(
            point_id="p2",
            score=0.85,
            payload={"sku": "HC-ADU-WGF-12", "name": "Hill's Perfect Weight", "pet_type": "dog", "category": "food_dry"},
            text="Hill's Science Diet weight management food clinically proven to help dogs lose weight",
        ),
        QdrantResult(
            point_id="p3",
            score=0.78,
            payload={"sku": "VET-DOG-JNT", "name": "Nutramax Cosequin", "pet_type": "dog", "category": "supplements"},
            text="Veterinarian recommended joint supplement with glucosamine chondroitin MSM",
        ),
    ]


@pytest.fixture
def mock_cohere_rerank_response():
    mock_result = MagicMock()
    mock_result.results = [
        MagicMock(index=2, relevance_score=0.98),
        MagicMock(index=0, relevance_score=0.87),
        MagicMock(index=1, relevance_score=0.72),
    ]
    return mock_result


@pytest.mark.asyncio
async def test_retriever_rerank_ordering(mock_qdrant_results, mock_cohere_rerank_response) -> None:
    """Cohere Rerank should reorder candidates by relevance score."""
    retriever = PetcoRetriever()

    with patch.object(retriever._store, "search_products", new_callable=AsyncMock) as mock_search:
        with patch.object(retriever._store, "search_guides", new_callable=AsyncMock) as mock_guides:
            with patch.object(retriever._cohere, "rerank", new_callable=AsyncMock) as mock_rerank:
                mock_search.return_value = mock_qdrant_results
                mock_guides.return_value = []
                mock_rerank.return_value = mock_cohere_rerank_response

                results = await retriever.retrieve(
                    query="joint support for large breed dog",
                    pet_type="dog",
                )

    assert len(results) == 3
    # First result should have highest cohere score (index 2 = Nutramax Cosequin)
    assert results[0].cohere_relevance_score == 0.98
    assert results[0].point_id == "p3"
    # Results should be sorted descending by cohere score
    scores = [r.cohere_relevance_score for r in results]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_retriever_pet_type_filter_passed(mock_qdrant_results, mock_cohere_rerank_response) -> None:
    """pet_type filter should be passed to Qdrant search."""
    retriever = PetcoRetriever()

    with patch.object(retriever._store, "search_products", new_callable=AsyncMock) as mock_search:
        with patch.object(retriever._store, "search_guides", new_callable=AsyncMock):
            with patch.object(retriever._cohere, "rerank", new_callable=AsyncMock) as mock_rerank:
                mock_search.return_value = mock_qdrant_results
                mock_rerank.return_value = mock_cohere_rerank_response

                await retriever.retrieve(query="food for my cat", pet_type="cat", include_guides=False)

                mock_search.assert_called_once()
                call_kwargs = mock_search.call_args[1]
                assert call_kwargs["pet_type"] == "cat"


def test_ranked_result_final_score() -> None:
    result = RankedResult(
        point_id="x",
        qdrant_score=0.5,
        cohere_relevance_score=0.95,
        metadata={},
        text="test",
    )
    assert result.final_score == 0.95
