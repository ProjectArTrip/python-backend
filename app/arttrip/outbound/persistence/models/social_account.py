from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    Identity,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from arttrip.application.domain.auth.social_provider import SocialProvider
from arttrip.application.domain.social_account.social_account import SocialAccount
from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.types import TIMESTAMPTZ, list_enum_values

social_accounts_table = Table(
    "social_accounts",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column(
        "provider",
        Enum(
            SocialProvider,
            name="provider",
            native_enum=False,
            length=50,
            create_constraint=True,
            validate_strings=True,
            values_callable=list_enum_values,
        ),
        nullable=False,
    ),
    Column("provider_user_id", String(255), nullable=False),
    Column("provider_refresh_token", Text, nullable=True),
    Column("linked_at", TIMESTAMPTZ, nullable=False),
    UniqueConstraint("provider", "provider_user_id"),
    UniqueConstraint("user_id", "provider"),
)


def map_social_accounts_table() -> None:
    mapper_registry.map_imperatively(
        SocialAccount,
        social_accounts_table,
        properties={
            "_id": social_accounts_table.c.id,
            "user": relationship("User", back_populates="social_accounts"),
        },
        exclude_properties=["provider_refresh_token"],
    )
