from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
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

notice_table = Table(
    "notice",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("title", String(255), nullable=True),
    Column("content", String(255), nullable=True),
    Column("role", String(50), nullable=False),
    created_at_column(nullable=True),
    updated_at_column(nullable=True),
    CheckConstraint(
        "updated_at IS NULL OR created_at IS NULL OR created_at <= updated_at",
        name="audit_time",
    ),
)
