from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from arttrip.application.domain.notification.push_delivery import PushDelivery
from arttrip.application.domain.notification.push_delivery_status import (
    PushDeliveryStatus,
)
from arttrip.application.domain.notification.push_dispatch import PushDispatch
from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.timestamps import (
    created_at_column,
    updated_at_column,
)
from arttrip.outbound.persistence.types import list_enum_values

push_dispatch_table = Table(
    "push_dispatch",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("title", String(255), nullable=False),
    Column("body", String(255), nullable=False),
    Column("data", JSONB, nullable=False),
    created_at_column(nullable=False),
)

push_delivery_table = Table(
    "push_delivery",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("dispatch_id", Integer, ForeignKey("push_dispatch.id"), nullable=False),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("token_hash", String(64), nullable=False),
    Column(
        "status",
        Enum(
            PushDeliveryStatus,
            name="push_delivery_status",
            native_enum=False,
            length=20,
            create_constraint=True,
            validate_strings=True,
            values_callable=list_enum_values,
        ),
        nullable=False,
    ),
    Column("message_id", String(255), nullable=True),
    Column("error_code", String(100), nullable=True),
    created_at_column(nullable=False),
    updated_at_column(nullable=True),
)

Index(None, push_delivery_table.c.dispatch_id)
Index(None, push_delivery_table.c.user_id)
Index(None, push_delivery_table.c.status)


def map_push_dispatch_table() -> None:
    mapper_registry.map_imperatively(
        PushDispatch,
        push_dispatch_table,
        properties={
            "_id": push_dispatch_table.c.id,
            "deliveries": relationship(
                "PushDelivery",
                cascade="all, delete-orphan",
                order_by=push_delivery_table.c.id,
            ),
        },
        exclude_properties=["created_at"],
    )


def map_push_delivery_table() -> None:
    mapper_registry.map_imperatively(
        PushDelivery,
        push_delivery_table,
        properties={"_id": push_delivery_table.c.id},
        exclude_properties=["created_at", "updated_at"],
    )
