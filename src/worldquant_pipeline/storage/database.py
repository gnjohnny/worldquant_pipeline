"""Database connection and session factory for PostgreSQL."""
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from worldquant_pipeline.config.settings import get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy declarative models."""


_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_engine(db_url: str | None = None) -> Engine:
    """Get or create the singleton SQLAlchemy engine."""
    global _engine, _session_factory
    if _engine is None or db_url is not None:
        url = db_url or get_settings().database_url
        _engine = create_engine(url, pool_pre_ping=True)
        _session_factory = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine


def get_session(db_url: str | None = None) -> Session:
    """Create a new database session."""
    get_engine(db_url)
    assert _session_factory is not None
    return _session_factory()


def init_db(engine: Engine | None = None) -> None:
    """Create all registered database tables."""
    eng = engine or get_engine()
    Base.metadata.create_all(bind=eng)
