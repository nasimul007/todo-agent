from datetime import datetime

from sqlalchemy import (
    insert,
    update,
    delete,
    select
)

from database import engine
from models import todos


class TodoService:

    @staticmethod
    def create_todo(title: str, description: str = "", priority: int = 3):
        now = datetime.now()

        stmt = (
            insert(todos)
            .values(
                title=title,
                description=description,
                status="pending",
                priority=priority,
                created_at=now,
                updated_at=now
            )
        )

        with engine.begin() as conn:
            result = conn.execute(stmt)

        return result.inserted_primary_key[0]

    @staticmethod
    def get_todo(todo_id: int):
        stmt = (
            select(todos)
            .where(todos.c.id == todo_id)
        )

        with engine.begin() as conn:
            row = conn.execute(stmt).mappings().first()

        return dict(row) if row else None

    @staticmethod
    def get_all_todos():
        stmt = (
            select(todos)
            .order_by(todos.c.created_at.desc())
        )

        with engine.begin() as conn:
            rows = conn.execute(stmt).mappings().all()

        return [dict(r) for r in rows]

    @staticmethod
    def update_todo(todo_id: int, **fields):
        fields["updated_at"] = datetime.now()

        stmt = (
            update(todos)
            .where(todos.c.id == todo_id)
            .values(**fields)
        )

        with engine.begin() as conn:
            result = conn.execute(stmt)

        return result.rowcount > 0

    @staticmethod
    def delete_todo(todo_id: int):
        stmt = (
            delete(todos)
            .where(todos.c.id == todo_id)
        )

        with engine.begin() as conn:
            result = conn.execute(stmt)

        return result.rowcount > 0