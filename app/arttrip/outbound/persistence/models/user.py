from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Enum,
    Identity,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import relationship

from arttrip.application.domain.user.onboarding_step import OnboardingStep
from arttrip.application.domain.user.role import UserRole
from arttrip.application.domain.user.user import User
from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.timestamps import (
    created_at_column,
    updated_at_column,
)
from arttrip.outbound.persistence.types import list_enum_values

users_table = Table(
    "users",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("email", String(255), nullable=True),
    Column("fcm_token", String(255), nullable=True),
    Column("nickname", String(255), nullable=False),
    Column(
        "onboarding_step",
        Enum(
            OnboardingStep,
            name="onboarding_step",
            native_enum=False,
            length=50,
            create_constraint=True,
            validate_strings=True,
            values_callable=list_enum_values,
        ),
        nullable=False,
    ),
    Column("profile_image_key", String(255), nullable=False),
    Column("push_enabled", Boolean, nullable=False),
    Column(
        "role",
        Enum(
            UserRole,
            name="role",
            native_enum=False,
            length=50,
            create_constraint=True,
            validate_strings=True,
            values_callable=list_enum_values,
        ),
        nullable=False,
    ),
    updated_at_column(nullable=False),
    created_at_column(nullable=False),
    CheckConstraint(
        "btrim(profile_image_key) <> ''", name="profile_image_key_not_blank"
    ),
)


def map_users_table() -> None:
    mapper_registry.map_imperatively(
        User,
        users_table,
        properties={
            "_id": users_table.c.id,
            "registered_at": users_table.c.created_at,
            "social_accounts": relationship("SocialAccount", back_populates="user"),
            "keywords": relationship(
                "UserKeyword",
                back_populates="user",
                cascade="all, delete-orphan",
            ),
        },
        exclude_properties=["fcm_token"],
    )
