from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)

metadata = MetaData()

todos = Table(
    "todos",
    metadata,

    Column("id", Integer, primary_key=True),

    Column("title", String(255), nullable=False),

    Column("description", Text),

    Column("status", String(20), nullable=False, default="pending"),

    Column("priority", Integer, nullable=False, default=3),

    Column("created_at", DateTime, nullable=False),

    Column("updated_at", DateTime, nullable=False)
)

schedule_events = Table(
    "schedule_events",
    metadata,

    Column("id", Integer, primary_key=True),

    Column("todo_id", Integer, ForeignKey("todos.id"), nullable=False),

    Column("start_time", DateTime, nullable=False),

    Column("end_time", DateTime, nullable=False),

    Column("created_at", DateTime, nullable=False)
)

recurrence_rules = Table(
    "recurrence_rules",
    metadata,

    Column("id", Integer, primary_key=True),

    Column("todo_id", Integer, ForeignKey("todos.id"), nullable=False),

    Column("frequency", String(20), nullable=False),

    Column("interval_value", Integer, nullable=False, default=1),

    Column("by_weekday", String(50)),

    Column("until_date", DateTime)
)