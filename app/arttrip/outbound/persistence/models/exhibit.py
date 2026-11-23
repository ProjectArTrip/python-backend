from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    Enum,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.orm import relationship

from arttrip.application.domain.exhibit.exhibit import Exhibit
from arttrip.application.domain.exhibit.exhibit_status import ExhibitStatus
from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.timestamps import (
    created_at_column,
    updated_at_column,
)
from arttrip.outbound.persistence.types import list_enum_values

exhibit_table = Table(
    "exhibit",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column(
        "exhibit_hall_id",
        Integer,
        ForeignKey("exhibit_hall.id"),
        nullable=False,
    ),
    Column("title", String(255), nullable=True),
    Column("description", Text, nullable=True),
    Column("poster_url", String(1024), nullable=True),
    Column("random_key", DOUBLE_PRECISION, nullable=False, default=func.random()),
    Column(
        "status",
        Enum(
            ExhibitStatus,
            name="status",
            native_enum=False,
            length=50,
            create_constraint=True,
            validate_strings=True,
            values_callable=list_enum_values,
        ),
        nullable=False,
    ),
    Column("ticket_url", String(1024), nullable=True),
    Column("start_date", Date, nullable=True),
    Column("end_date", Date, nullable=True),
    Column("view_count", Integer, nullable=False, server_default="0"),
    Column("owner_user_id", Integer, ForeignKey("users.id"), nullable=True),
    updated_at_column(nullable=True),
    created_at_column(nullable=True),
    CheckConstraint(
        "start_date IS NULL OR end_date IS NULL OR start_date <= end_date",
        name="date_range",
    ),
    Index(None, "exhibit_hall_id"),
    Index(None, "owner_user_id"),
    UniqueConstraint(
        "exhibit_hall_id", "title", "start_date", postgresql_nulls_not_distinct=True
    ),
)

exhibit_keyword_table = Table(
    "exhibit_keyword",
    mapper_registry.metadata,
    Column("exhibit_id", Integer, ForeignKey("exhibit.id"), primary_key=True),
    Column("keyword_id", Integer, ForeignKey("keyword.id"), primary_key=True),
    Index(None, "keyword_id", "exhibit_id"),
)


def map_exhibit_table() -> None:
    mapper_registry.map_imperatively(
        Exhibit,
        exhibit_table,
        properties={
            "_id": exhibit_table.c.id,
            "hall": relationship("ExhibitHall", lazy="joined"),
            "keywords": relationship("Keyword", secondary=exhibit_keyword_table),
            "owner_id": exhibit_table.c.owner_user_id,
        },
        exclude_properties=["random_key", "view_count", "created_at", "updated_at"],
    )
