from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Table,
    Text,
    text,
)

from arttrip.application.domain.artist_application.artist_application import (
    ArtistApplication,
)
from arttrip.application.domain.artist_application.artist_application_status import (
    ArtistApplicationStatus,
)
from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.timestamps import (
    created_at_column,
    updated_at_column,
)
from arttrip.outbound.persistence.types import TIMESTAMPTZ, list_enum_values

artist_application_table = Table(
    "artist_application",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("introduction", Text, nullable=False),
    Column("portfolio_url", String(1024), nullable=True),
    Column(
        "status",
        Enum(
            ArtistApplicationStatus,
            name="status",
            native_enum=False,
            length=50,
            create_constraint=True,
            validate_strings=True,
            values_callable=list_enum_values,
        ),
        nullable=False,
    ),
    Column("rejection_reason", String(500), nullable=True),
    Column("reviewed_by", Integer, ForeignKey("users.id"), nullable=True),
    Column("reviewed_at", TIMESTAMPTZ, nullable=True),
    created_at_column(nullable=False),
    updated_at_column(nullable=True),
)

Index(
    None,
    artist_application_table.c.user_id,
    unique=True,
    postgresql_where=text("status = 'PENDING'"),
)
Index(
    None,
    artist_application_table.c.status,
    artist_application_table.c.created_at.desc(),
)


def map_artist_application_table() -> None:
    mapper_registry.map_imperatively(
        ArtistApplication,
        artist_application_table,
        properties={
            "_id": artist_application_table.c.id,
            "submitted_at": artist_application_table.c.created_at,
        },
    )
