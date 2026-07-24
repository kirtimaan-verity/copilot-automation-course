"""Database schema and constraint tests for SQLite via SQLAlchemy."""

from __future__ import annotations

from typing import Any, Dict, Mapping

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql.schema import Table


@pytest.fixture(scope="function")
def valid_task_data(test_user: Dict[str, Any]) -> Dict[str, Any]:
    """Return a valid baseline task payload for inserts."""
    return {
        "title": "Valid task title",
        "description": "Valid task description",
        "due_date": "2030-01-01",
        "priority": "medium",
        "status": "active",
        "user_id": test_user["id"],
    }


def test_tasks_table_exists(db_tables: Mapping[str, Table]) -> None:
    """Validate that the tasks table is present in reflected metadata."""
    assert "tasks" in db_tables, "Expected 'tasks' table to exist in reflected database metadata."


def test_users_table_exists(db_tables: Mapping[str, Table]) -> None:
    """Validate that the users table is present in reflected metadata."""
    assert "users" in db_tables, "Expected 'users' table to exist in reflected database metadata."


def test_tasks_has_required_columns(db_tables: Mapping[str, Table]) -> None:
    """Validate required columns exist on the tasks table."""
    tasks_table = db_tables["tasks"]
    required_columns = {"id", "user_id", "title", "status", "created_at"}
    actual_columns = set(tasks_table.columns.keys())
    missing_columns = required_columns - actual_columns

    assert not missing_columns, f"Expected required task columns to exist, missing: {sorted(missing_columns)}"


def test_task_title_cannot_exceed_200_chars(
    db_session: Session, db_tables: Mapping[str, Table], valid_task_data: Dict[str, Any]
) -> None:
    """Validate title length CHECK constraint rejects values above 200 characters."""
    tasks_table = db_tables["tasks"]
    payload = dict(valid_task_data)
    payload["title"] = "x" * 201

    with pytest.raises(IntegrityError):
        db_session.execute(tasks_table.insert().values(**payload))
        db_session.flush()


def test_task_priority_must_be_valid_value(
    db_session: Session, db_tables: Mapping[str, Table], valid_task_data: Dict[str, Any]
) -> None:
    """Validate priority CHECK constraint rejects invalid values."""
    tasks_table = db_tables["tasks"]
    payload = dict(valid_task_data)
    payload["priority"] = "urgent"

    with pytest.raises(IntegrityError):
        db_session.execute(tasks_table.insert().values(**payload))
        db_session.flush()


def test_task_status_must_be_valid_value(
    db_session: Session, db_tables: Mapping[str, Table], valid_task_data: Dict[str, Any]
) -> None:
    """Validate status CHECK constraint rejects invalid values."""
    tasks_table = db_tables["tasks"]
    payload = dict(valid_task_data)
    payload["status"] = "in_progress"

    with pytest.raises(IntegrityError):
        db_session.execute(tasks_table.insert().values(**payload))
        db_session.flush()


def test_task_user_id_foreign_key_enforced(
    db_session: Session, db_tables: Mapping[str, Table], valid_task_data: Dict[str, Any]
) -> None:
    """Validate foreign key constraint rejects non-existent user references."""
    tasks_table = db_tables["tasks"]
    payload = dict(valid_task_data)
    payload["user_id"] = 9999999

    with pytest.raises(IntegrityError):
        db_session.execute(tasks_table.insert().values(**payload))
        db_session.flush()


def test_user_email_must_be_unique(
    db_session: Session, db_tables: Mapping[str, Table], test_user: Dict[str, Any]
) -> None:
    """Validate users.email uniqueness constraint blocks duplicate emails."""
    users_table = db_tables["users"]

    with pytest.raises(IntegrityError):
        db_session.execute(
            users_table.insert().values(
                email=test_user["email"],
                password_hash="duplicate_hash",
                display_name="Duplicate User",
            )
        )
        db_session.flush()


def test_task_deleted_when_user_deleted(
    db_session: Session, db_tables: Mapping[str, Table], valid_task_data: Dict[str, Any], test_user: Dict[str, Any]
) -> None:
    """Validate ON DELETE CASCADE removes tasks when parent user is deleted."""
    tasks_table = db_tables["tasks"]
    users_table = db_tables["users"]

    db_session.execute(tasks_table.insert().values(**valid_task_data))
    db_session.flush()

    db_session.execute(delete(users_table).where(users_table.c.id == test_user["id"]))
    db_session.flush()

    remaining_tasks = db_session.execute(
        select(func.count()).select_from(tasks_table).where(tasks_table.c.user_id == test_user["id"])
    ).scalar_one()

    assert remaining_tasks == 0, "Expected user deletion to cascade and remove all dependent tasks."


def test_task_created_at_auto_populated(
    db_session: Session, db_tables: Mapping[str, Table], valid_task_data: Dict[str, Any]
) -> None:
    """Validate created_at is automatically populated on task insert."""
    tasks_table = db_tables["tasks"]

    insert_result = db_session.execute(tasks_table.insert().values(**valid_task_data))
    task_id = insert_result.inserted_primary_key[0]
    row = db_session.execute(select(tasks_table).where(tasks_table.c.id == task_id)).mappings().one()

    assert row["created_at"] is not None, "Expected created_at to be auto-populated for inserted tasks."


def test_task_default_priority_is_medium(
    db_session: Session, db_tables: Mapping[str, Table], test_user: Dict[str, Any]
) -> None:
    """Validate default priority is set to medium when omitted."""
    tasks_table = db_tables["tasks"]
    insert_result = db_session.execute(
        tasks_table.insert().values(
            title="Default priority task",
            status="active",
            user_id=test_user["id"],
        )
    )
    task_id = insert_result.inserted_primary_key[0]
    row = db_session.execute(select(tasks_table).where(tasks_table.c.id == task_id)).mappings().one()

    assert row["priority"] == "medium", "Expected default task priority to be 'medium'."


def test_task_default_status_is_active(
    db_session: Session, db_tables: Mapping[str, Table], test_user: Dict[str, Any]
) -> None:
    """Validate default status is set to active when omitted."""
    tasks_table = db_tables["tasks"]
    insert_result = db_session.execute(
        tasks_table.insert().values(
            title="Default status task",
            priority="low",
            user_id=test_user["id"],
        )
    )
    task_id = insert_result.inserted_primary_key[0]
    row = db_session.execute(select(tasks_table).where(tasks_table.c.id == task_id)).mappings().one()

    assert row["status"] == "active", "Expected default task status to be 'active'."