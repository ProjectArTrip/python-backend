from sqlalchemy import (
    Column,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from arttrip.application.domain.user.user_keyword import UserKeyword
from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.timestamps import created_at_column

user_keyword_table = Table(
    "user_keyword",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("keyword_id", Integer, ForeignKey("keyword.id"), nullable=False),
    created_at_column(nullable=False),
    UniqueConstraint("user_id", "keyword_id"),
)

Index(None, user_keyword_table.c.keyword_id, user_keyword_table.c.user_id)


def map_user_keyword_table() -> None:
    mapper_registry.map_imperatively(
        UserKeyword,
        user_keyword_table,
        properties={
            "_id": user_keyword_table.c.id,
            "selected_at": user_keyword_table.c.created_at,
            "user": relationship("User", back_populates="keywords"),
        },
    )
