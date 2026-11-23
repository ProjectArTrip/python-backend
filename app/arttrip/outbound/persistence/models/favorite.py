from sqlalchemy import (
    Column,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Table,
    UniqueConstraint,
)

from arttrip.application.domain.favorite.favorite import Favorite
from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.timestamps import created_at_column

favorite_table = Table(
    "favorite",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("exhibit_id", Integer, ForeignKey("exhibit.id"), nullable=False),
    created_at_column(nullable=False),
    UniqueConstraint("user_id", "exhibit_id"),
)

Index(None, favorite_table.c.user_id, favorite_table.c.created_at.desc())
Index(None, favorite_table.c.exhibit_id)


def map_favorite_table() -> None:
    mapper_registry.map_imperatively(
        Favorite,
        favorite_table,
        properties={"_id": favorite_table.c.id},
    )
