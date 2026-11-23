from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from arttrip.application.domain.review.review import Review
from arttrip.outbound.persistence.models.review_image import review_image_table
from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.timestamps import (
    created_at_column,
    updated_at_column,
)
from arttrip.outbound.persistence.types import TIMESTAMPTZ

review_table = Table(
    "review",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("exhibit_id", Integer, ForeignKey("exhibit.id"), nullable=False),
    Column("content", String(500), nullable=False),
    Column("visit_date", Date, nullable=False),
    Column("status", String(50), nullable=False),
    Column("rejection_reason", String(200), nullable=True),
    Column("reviewed_by", Integer, ForeignKey("users.id"), nullable=True),
    Column("reviewed_at", TIMESTAMPTZ, nullable=True),
    created_at_column(nullable=False),
    updated_at_column(nullable=False),
    UniqueConstraint("user_id", "exhibit_id"),
)

Index(None, review_table.c.exhibit_id, review_table.c.status, review_table.c.id.desc())
Index(None, review_table.c.user_id, review_table.c.id.desc())


def map_review_table() -> None:
    mapper_registry.map_imperatively(
        Review,
        review_table,
        properties={
            "_id": review_table.c.id,
            "images": relationship(
                "ReviewImage",
                back_populates="review",
                cascade="all, delete-orphan",
                order_by=review_image_table.c.display_order,
                lazy="selectin",
            ),
        },
    )
