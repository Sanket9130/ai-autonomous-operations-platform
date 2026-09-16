from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.core.config import settings

# Configure engine based on SQLite vs PostgreSQL
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from backend.app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Automatic schema migration for existing SQLite / PostgreSQL databases
    with engine.connect() as conn:
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(engine)
            if "work_orders" in inspector.get_table_names():
                columns = [col["name"] for col in inspector.get_columns("work_orders")]
                if "priority" not in columns:
                    conn.execute(text("ALTER TABLE work_orders ADD COLUMN priority VARCHAR(32) DEFAULT 'MEDIUM'"))
                    conn.commit()
                if "notes" not in columns:
                    conn.execute(text("ALTER TABLE work_orders ADD COLUMN notes TEXT"))
                    conn.commit()
        except Exception:
            pass
