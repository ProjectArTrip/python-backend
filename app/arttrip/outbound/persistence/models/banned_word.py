from sqlalchemy import Boolean, Column, Identity, Integer, String, Table

from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.timestamps import (
    created_at_column,
    updated_at_column,
)

banned_word_table = Table(
    "banned_word",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("word", String(100), nullable=False, unique=True),
    Column("active", Boolean, nullable=False),
    created_at_column(nullable=True),
    updated_at_column(nullable=True),
)
