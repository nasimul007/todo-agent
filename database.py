from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///todo.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True
)