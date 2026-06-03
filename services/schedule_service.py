from datetime import datetime

from sqlalchemy import (
    insert,
    update,
    delete,
    select,
    and_
)

from database import engine
from models import schedule_events


class ScheduleConflictError(Exception):
    pass


class ScheduleService:

    @staticmethod
    def has_overlap(start_time, end_time, exclude_id=None):

        conditions = [
            schedule_events.c.start_time < end_time,
            schedule_events.c.end_time > start_time
        ]

        if exclude_id:
            conditions.append(
                schedule_events.c.id != exclude_id
            )

        stmt = (
            select(schedule_events.c.id)
            .where(and_(*conditions))
            .limit(1)
        )

        with engine.begin() as conn:
            row = conn.execute(stmt).first()

        return row is not None

    @staticmethod
    def create_schedule(todo_id, start_time, end_time):

        if start_time >= end_time:
            raise ValueError("end_time must be greater than start_time")

        if ScheduleService.has_overlap(start_time, end_time):
            raise ScheduleConflictError("Schedule overlaps existing booking")

        stmt = (
            insert(schedule_events)
            .values(
                todo_id=todo_id,
                start_time=start_time,
                end_time=end_time,
                created_at=datetime.now()
            )
        )

        with engine.begin() as conn:
            result = conn.execute(stmt)

        return result.inserted_primary_key[0]

    @staticmethod
    def get_schedule(schedule_id):

        stmt = (
            select(schedule_events)
            .where(schedule_events.c.id == schedule_id)
        )

        with engine.begin() as conn:
            row = conn.execute(stmt).mappings().first()

        return dict(row) if row else None

    @staticmethod
    def get_all_schedules():

        stmt = (
            select(schedule_events)
            .order_by(schedule_events.c.start_time)
        )

        with engine.begin() as conn:
            rows = conn.execute(stmt).mappings().all()

        return [dict(r) for r in rows]

    @staticmethod
    def update_schedule(schedule_id, start_time, end_time):
        if ScheduleService.has_overlap(start_time, end_time, exclude_id=schedule_id):
            raise ScheduleConflictError("Schedule overlaps existing booking")

        stmt = (
            update(schedule_events)
            .where(
                schedule_events.c.id == schedule_id
            )
            .values(
                start_time=start_time,
                end_time=end_time
            )
        )

        with engine.begin() as conn:
            result = conn.execute(stmt)

        return result.rowcount > 0

    @staticmethod
    def delete_schedule(schedule_id):

        stmt = (
            delete(schedule_events)
            .where(
                schedule_events.c.id == schedule_id
            )
        )

        with engine.begin() as conn:
            result = conn.execute(stmt)

        return result.rowcount > 0