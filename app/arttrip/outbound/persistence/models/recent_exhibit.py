from sqlalchemy import (
    Column,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Table,
    UniqueConstraint,
)

from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.types import TIMESTAMPTZ

recent_exhibit_table = Table(
    "recent_exhibit",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("exhibit_id", Integer, ForeignKey("exhibit.id"), nullable=False),
    Column("viewed_at", TIMESTAMPTZ, nullable=False),
    UniqueConstraint("user_id", "exhibit_id"),
)

Index(None, recent_exhibit_table.c.user_id, recent_exhibit_table.c.viewed_at.desc())
