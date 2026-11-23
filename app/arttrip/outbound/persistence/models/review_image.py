from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Identity,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from arttrip.application.domain.review.review_image import ReviewImage
from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.timestamps import (
    created_at_column,
    updated_at_column,
)

review_image_table = Table(
    "review_image",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("review_id", Integer, ForeignKey("review.id"), nullable=False),
    Column("display_order", Integer, nullable=False),
    Column("image_key", String(512), nullable=False),
    created_at_column(nullable=False),
    updated_at_column(nullable=True),
    UniqueConstraint(
        "review_id", "display_order", deferrable=True, initially="DEFERRED"
    ),
    CheckConstraint("display_order >= 1", name="display_order"),
)


def map_review_image_table() -> None:
    mapper_registry.map_imperatively(
        ReviewImage,
        review_image_table,
        properties={
            "_id": review_image_table.c.id,
            "review": relationship("Review", back_populates="images"),
        },
    )
