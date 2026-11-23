from sqlalchemy import (
    Boolean,
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
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from arttrip.application.domain.curation.curation import Curation
from arttrip.application.domain.curation.curation_exhibit import CurationExhibit
from arttrip.application.domain.curation.refresh_cycle import RefreshCycle
from arttrip.application.domain.curation.sort_type import SortType
from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.timestamps import (
    created_at_column,
    updated_at_column,
)
from arttrip.outbound.persistence.types import list_enum_values

curation_table = Table(
    "curation",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("title", String(100), nullable=False),
    Column("active", Boolean, nullable=False),
    Column("display_count", Integer, nullable=True),
    Column(
        "refresh_cycle",
        Enum(
            RefreshCycle,
            name="refresh_cycle",
            native_enum=False,
            length=50,
            create_constraint=True,
            validate_strings=True,
            values_callable=list_enum_values,
        ),
        nullable=False,
    ),
    Column(
        "sort_type",
        Enum(
            SortType,
            name="sort_type",
            native_enum=False,
            length=50,
            create_constraint=True,
            validate_strings=True,
            values_callable=list_enum_values,
        ),
        nullable=True,
    ),
    Column("visible_from", Date, nullable=False),
    Column("visible_to", Date, nullable=False),
    created_at_column(nullable=False),
    updated_at_column(nullable=True),
    CheckConstraint("visible_from <= visible_to", name="visible_period"),
    CheckConstraint(
        "display_count IS NULL OR display_count >= 0", name="display_count"
    ),
    CheckConstraint(
        "updated_at IS NULL OR created_at <= updated_at", name="audit_time"
    ),
)

curation_exhibit_table: Table = Table(
    "curation_exhibit",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("curation_id", Integer, ForeignKey("curation.id"), nullable=False),
    Column("exhibit_id", Integer, ForeignKey("exhibit.id"), nullable=False),
    Column("display_order", Integer, nullable=False),
    UniqueConstraint(
        "curation_id", "exhibit_id", deferrable=True, initially="DEFERRED"
    ),
    UniqueConstraint(
        "curation_id", "display_order", deferrable=True, initially="DEFERRED"
    ),
    CheckConstraint("display_order >= 0", name="display_order"),
)

Index(None, curation_exhibit_table.c.exhibit_id)


def map_curation_table() -> None:
    mapper_registry.map_imperatively(
        Curation,
        curation_table,
        properties={
            "_id": curation_table.c.id,
            "exhibits": relationship(
                "CurationExhibit",
                back_populates="curation",
                cascade="all, delete-orphan",
                order_by=curation_exhibit_table.c.display_order,
            ),
        },
        exclude_properties=[
            "display_count",
            "created_at",
            "updated_at",
        ],
    )


def map_curation_exhibit_table() -> None:
    mapper_registry.map_imperatively(
        CurationExhibit,
        curation_exhibit_table,
        properties={
            "_id": curation_exhibit_table.c.id,
            "curation": relationship("Curation", back_populates="exhibits"),
        },
    )
