from sqlalchemy import (
    Column,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import CHAR

from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.types import TIMESTAMPTZ

exhibit_sync_table = Table(
    "exhibit_sync",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("exhibit_id", Integer, ForeignKey("exhibit.id"), nullable=False),
    Column("source", String(50), nullable=False),
    Column("external_id", String(255), nullable=False),
    Column("content_hash", CHAR(64), nullable=False),
    Column("synced_at", TIMESTAMPTZ, nullable=False),
    UniqueConstraint("source", "external_id"),
    Index(None, "exhibit_id"),
)
