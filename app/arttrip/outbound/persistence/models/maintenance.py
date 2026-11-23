from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Identity,
    Integer,
    String,
    Table,
)

from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.timestamps import (
    created_at_column,
    updated_at_column,
)
from arttrip.outbound.persistence.types import TIMESTAMPTZ

maintenance_table = Table(
    "maintenance",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("title", String(100), nullable=False),
    Column("message", String(1000), nullable=False),
    Column("button_text", String(50), nullable=False),
    Column("state", String(50), nullable=False),
    Column("force_exit", Boolean, nullable=False),
    Column("refresh_after_seconds", Integer, nullable=False),
    Column("version", Integer, nullable=False),
    Column("start_at", TIMESTAMPTZ, nullable=False),
    Column("end_at", TIMESTAMPTZ, nullable=False),
    created_at_column(nullable=False),
    updated_at_column(nullable=False),
    CheckConstraint("start_at < end_at", name="period"),
    CheckConstraint("refresh_after_seconds >= 0", name="refresh_after_seconds"),
    CheckConstraint("version >= 0", name="version"),
    CheckConstraint("created_at <= updated_at", name="audit_time"),
)
