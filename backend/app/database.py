from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings

engine = create_engine(f"sqlite:///{settings.db_path}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from . import models  # noqa: F401  注册所有模型
    Base.metadata.create_all(bind=engine)
    _ensure_schema()  # SQLite 补列(create_all 不会给已存在的表加列)


def _ensure_schema():
    """幂等迁移:给已存在的表补缺失列(create_all 从不 ALTER 旧表)。"""
    with engine.begin() as conn:
        cols = {row[1] for row in conn.execute(text("PRAGMA table_info(knowledge_points)"))}
        if "card" not in cols:
            conn.execute(text("ALTER TABLE knowledge_points ADD COLUMN card TEXT DEFAULT ''"))
