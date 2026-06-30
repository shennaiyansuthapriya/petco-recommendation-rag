"""initial schema

Revision ID: 0001
Revises:
Create Date: 2024-08-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pet_products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("sku", sa.String(50), nullable=True, unique=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("brand", sa.String(100), nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "food_dry", "food_wet", "food_raw", "treats", "supplements",
                "toys", "beds", "carriers", "grooming", "health_wellness",
                "training", "aquatics", "other",
                name="productcategory",
            ),
            nullable=False,
        ),
        sa.Column(
            "pet_type",
            sa.Enum("dog", "cat", "fish", "bird", "reptile", "small_animal", "all", name="pettype"),
            nullable=False,
        ),
        sa.Column(
            "life_stage",
            sa.Enum("puppy_kitten", "adult", "senior", "all_stages", name="lifestage"),
            nullable=False,
            server_default="all_stages",
        ),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("ingredients", sa.Text, nullable=True),
        sa.Column("guaranteed_analysis", sa.Text, nullable=True),
        sa.Column("feeding_guidelines", sa.Text, nullable=True),
        sa.Column("health_benefits", sa.Text, nullable=True),
        sa.Column("suitable_for_conditions", postgresql.JSONB, nullable=True),
        sa.Column("breed_specific", postgresql.JSONB, nullable=True),
        sa.Column("vet_recommended", sa.Boolean, default=False, nullable=False),
        sa.Column("prescription_required", sa.Boolean, default=False, nullable=False),
        sa.Column("protein_pct", sa.Float, nullable=True),
        sa.Column("fat_pct", sa.Float, nullable=True),
        sa.Column("fiber_pct", sa.Float, nullable=True),
        sa.Column("calories_per_cup", sa.Integer, nullable=True),
        sa.Column("grain_free", sa.Boolean, default=False, nullable=False),
        sa.Column("primary_protein", sa.String(100), nullable=True),
        sa.Column("price_usd", sa.Float, nullable=True),
        sa.Column("in_stock", sa.Boolean, default=True, nullable=False),
        sa.Column("is_indexed", sa.Boolean, default=False, nullable=False),
        sa.Column("qdrant_point_ids", postgresql.JSONB, nullable=True),
        sa.Column("rating", sa.Float, nullable=True),
        sa.Column("review_count", sa.Integer, nullable=True),
    )
    op.create_index("ix_pet_products_name", "pet_products", ["name"])
    op.create_index("ix_pet_products_brand", "pet_products", ["brand"])
    op.create_index("ix_pet_product_type_cat", "pet_products", ["pet_type", "category"])
    op.create_index("ix_pet_product_stage", "pet_products", ["life_stage", "pet_type"])

    op.create_table(
        "pet_care_guides",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("pet_type", sa.Enum("dog", "cat", "fish", "bird", "reptile", "small_animal", "all", name="pettype", create_type=False), nullable=False),
        sa.Column("topic", sa.String(100), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("qdrant_point_ids", postgresql.JSONB, nullable=True),
        sa.Column("is_indexed", sa.Boolean, default=False, nullable=False),
    )

    op.create_table(
        "recommendation_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("query", sa.Text, nullable=False),
        sa.Column("answer", sa.Text, nullable=True),
        sa.Column("recommended_skus", postgresql.JSONB, nullable=True),
        sa.Column("latency_ms", sa.Integer, nullable=True),
        sa.Column("pet_type_filter", sa.String(20), nullable=True),
        sa.Column("health_condition", sa.String(100), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("recommendation_logs")
    op.drop_table("pet_care_guides")
    op.drop_table("pet_products")
    op.execute("DROP TYPE IF EXISTS productcategory")
    op.execute("DROP TYPE IF EXISTS pettype")
    op.execute("DROP TYPE IF EXISTS lifestage")
