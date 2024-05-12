from sqlmodel import Session, SQLModel, create_engine
from app.config import settings

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

ASYNC_POSTGRES_URL: str = (
    "postgresql+asyncpg://"
    + f"{settings.postgres_user}:"
    + f"{settings.postgres_password}"
    + f"@{settings.postgres_host}:"
    + f"{settings.postgres_port}/"
    + f"{settings.postgres_db or ''}"
)

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
