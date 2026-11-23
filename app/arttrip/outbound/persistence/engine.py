from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from arttrip.common.database import DatabaseSettings


def create_database_engine(db: DatabaseSettings) -> Engine:
    return create_engine(
        db.url,
        pool_pre_ping=True,
        pool_size=db.pool_size,
        max_overflow=db.pool_max_overflow,
        pool_timeout=db.pool_timeout_seconds,
        pool_recycle=db.pool_recycle_seconds,
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
