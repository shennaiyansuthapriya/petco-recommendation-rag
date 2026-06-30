from functools import lru_cache
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["development", "testing", "production"] = "development"
    app_name: str = "petco-recommendation-rag"
    app_version: str = "1.0.0"
    debug: bool = True

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = "gpt-4o-2024-08-06"
    openai_embedding_model: str = "text-embedding-3-large"
    openai_temperature: float = 0.0

    cohere_api_key: str = Field(default="", alias="COHERE_API_KEY")
    cohere_rerank_model: str = "rerank-english-v3.0"
    cohere_rerank_top_n: int = 5

    qdrant_url: str = "http://localhost:6335"
    qdrant_api_key: str = ""
    qdrant_collection_products: str = "petco_products"
    qdrant_collection_guides: str = "petco_care_guides"
    qdrant_vector_size: int = 3072

    database_url: str = "postgresql+asyncpg://petco_user:petco_pass@localhost:5438/petco_db"
    sync_database_url: str = "postgresql://petco_user:petco_pass@localhost:5438/petco_db"
    redis_url: str = "redis://localhost:6384/0"

    retrieval_top_k: int = 12
    rerank_top_n: int = 5
    chunk_size: int = 512
    chunk_overlap: int = 64

    allowed_origins: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
