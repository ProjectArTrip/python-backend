from sqlalchemy import (
    CheckConstraint,
    Column,
    Enum,
    Identity,
    Integer,
    String,
    Table,
    UniqueConstraint,
)

from arttrip.application.domain.keyword.keyword import Keyword
from arttrip.application.domain.keyword.keyword_type import KeywordType
from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.timestamps import (
    created_at_column,
    updated_at_column,
)
from arttrip.outbound.persistence.types import list_enum_values

keyword_table = Table(
    "keyword",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("name", String(255), nullable=False),
    Column(
        "type",
        Enum(
            KeywordType,
            name="type",
            native_enum=False,
            length=50,
            create_constraint=True,
            validate_strings=True,
            values_callable=list_enum_values,
        ),
        nullable=False,
    ),
    created_at_column(nullable=True),
    updated_at_column(nullable=True),
    UniqueConstraint("type", "name"),
    CheckConstraint(r"name !~ '\s'", name="name_no_whitespace"),
)


def map_keyword_table() -> None:
    mapper_registry.map_imperatively(
        Keyword,
        keyword_table,
        properties={
            "_id": keyword_table.c.id,
            "keyword_type": keyword_table.c.type,
        },
    )
