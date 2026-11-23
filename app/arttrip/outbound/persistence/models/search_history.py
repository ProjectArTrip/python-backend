from sqlalchemy import (
    Column,
    ForeignKey,
    Identity,
    Integer,
    String,
    Table,
    UniqueConstraint,
)

from arttrip.application.domain.search_history.search_history import SearchHistory
from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.timestamps import created_at_column

search_history_table = Table(
    "search_history",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("content", String(255), nullable=False),
    created_at_column(nullable=False),
    UniqueConstraint("user_id", "content"),
)


def map_search_history_table() -> None:
    mapper_registry.map_imperatively(
        SearchHistory,
        search_history_table,
        properties={"_id": search_history_table.c.id},
    )
