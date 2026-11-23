from datetime import datetime

from sqlalchemy import Column, func

from arttrip.outbound.persistence.types import TIMESTAMPTZ


def created_at_column(*, nullable: bool) -> Column[datetime]:
    return Column("created_at", TIMESTAMPTZ, nullable=nullable, default=func.now())


def updated_at_column(*, nullable: bool) -> Column[datetime]:
    return Column(
        "updated_at",
        TIMESTAMPTZ,
        nullable=nullable,
        default=func.now(),
        onupdate=func.now(),
    )
