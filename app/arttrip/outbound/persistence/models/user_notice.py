from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Table,
    text,
)

from arttrip.application.domain.notification.notification import Notification
from arttrip.application.domain.notification.notification_action import (
    NotificationAction,
)
from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.timestamps import (
    created_at_column,
    updated_at_column,
)
from arttrip.outbound.persistence.types import TIMESTAMPTZ, list_enum_values

user_notice_table = Table(
    "user_notice",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("title", String(255), nullable=True),
    Column(
        "action",
        Enum(
            NotificationAction,
            name="action",
            native_enum=False,
            length=50,
            create_constraint=True,
            validate_strings=True,
            values_callable=list_enum_values,
        ),
        nullable=False,
    ),
    Column("body", String(255), nullable=True),
    Column("is_read", Boolean, nullable=False, server_default=text("false")),
    Column("read_at", TIMESTAMPTZ, nullable=True),
    Column("reference_id", Integer, nullable=True),
    created_at_column(nullable=False),
    updated_at_column(nullable=True),
    CheckConstraint(
        "(is_read = false AND read_at IS NULL)"
        " OR (is_read = true AND read_at IS NOT NULL)",
        name="read_state",
    ),
)

Index(None, user_notice_table.c.user_id, user_notice_table.c.created_at.desc())
Index(
    None,
    user_notice_table.c.user_id,
    postgresql_where=text("is_read = false"),
)


def map_user_notice_table() -> None:
    mapper_registry.map_imperatively(
        Notification,
        user_notice_table,
        properties={"_id": user_notice_table.c.id},
    )
