"""Seed test users and tasks into the SQLite test database.

Usage:
    python test/fixtures/seed_test_data.py [--clean]

Behavior:
- Reads TEST_DB_URL from environment.
- Optionally removes previously seeded rows with --clean.
- Inserts 3 users and 20 tasks per user (60 total).
"""

from __future__ import annotations

import argparse
import os
import random
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy import MetaData, create_engine, delete, insert, select, text
from sqlalchemy.engine import Engine


# Ensure imports work even when this script is run directly.
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from tests.fixtures.data_factory import TaskFactory, UserFactory


SEEDED_USER_LOCAL_PREFIX = "seed_user_"
SEEDED_DISPLAY_NAME_PREFIX = "Seed User"
SEEDED_TASK_TITLE_PREFIX = "[seed]"


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for seed behavior."""
    parser = argparse.ArgumentParser(description="Seed test users and tasks into TEST_DB_URL SQLite database.")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete previously seeded users/tasks before inserting new records.",
    )
    return parser.parse_args()


def get_engine() -> Engine:
    """Create a SQLAlchemy engine from TEST_DB_URL."""
    db_url = os.environ.get("TEST_DB_URL")
    if not db_url:
        raise ValueError("TEST_DB_URL is required, but it was not found in the environment.")
    return create_engine(db_url)


def reflect_tables(engine: Engine) -> tuple[Any, Any]:
    """Reflect users and tasks tables from the configured database."""
    metadata = MetaData()
    metadata.reflect(bind=engine)

    users_table = metadata.tables.get("users")
    tasks_table = metadata.tables.get("tasks")

    if users_table is None or tasks_table is None:
        raise RuntimeError("Expected tables 'users' and 'tasks' to exist in TEST_DB_URL database.")

    return users_table, tasks_table


def build_seed_users() -> list[dict[str, str]]:
    """Create 3 deterministic-tag users with hashed passwords."""
    users: list[dict[str, str]] = []
    for index in range(1, 4):
        user = UserFactory.valid_user()
        domain = random.choice(("example.com", "test.invalid"))
        user["email"] = f"{SEEDED_USER_LOCAL_PREFIX}{index}@{domain}"
        users.append(
            {
                "email": user["email"],
                "password_hash": user["password"],
                "display_name": f"{SEEDED_DISPLAY_NAME_PREFIX} {index}",
            }
        )
    return users


def build_user_tasks(user_id: int, count: int = 20) -> list[dict[str, Any]]:
    """Create task payloads for a specific user with varied statuses and priorities."""
    statuses = ["active", "completed", "overdue", "archived"]
    priorities = ["low", "medium", "high"]
    tasks: list[dict[str, Any]] = []

    for index in range(count):
        task = TaskFactory.valid_task()
        task_status = statuses[index % len(statuses)]
        task_priority = priorities[index % len(priorities)]

        task_due_date = date.today() + timedelta(days=(index % 14) + 1)
        if task_status == "overdue":
            task_due_date = date.today() - timedelta(days=(index % 10) + 1)

        task.update(
            {
                "title": f"{SEEDED_TASK_TITLE_PREFIX} User {user_id} Task {index + 1}",
                "status": task_status,
                "priority": task_priority,
                "due_date": task_due_date.isoformat(),
                "user_id": user_id,
            }
        )
        tasks.append(task)

    return tasks


def clean_seed_data(engine: Engine, users_table: Any, tasks_table: Any) -> dict[str, int]:
    """Delete previously seeded tasks/users and return deletion counts."""
    deleted_counts = {"tasks": 0, "users": 0}

    with engine.begin() as connection:
        connection.execute(text("PRAGMA foreign_keys = ON"))

        seeded_user_ids = [
            row[0]
            for row in connection.execute(
                select(users_table.c.id).where(users_table.c.email.like(f"{SEEDED_USER_LOCAL_PREFIX}%"))
            ).all()
        ]

        if seeded_user_ids:
            task_result = connection.execute(delete(tasks_table).where(tasks_table.c.user_id.in_(seeded_user_ids)))
            user_result = connection.execute(delete(users_table).where(users_table.c.id.in_(seeded_user_ids)))
            deleted_counts["tasks"] = int(task_result.rowcount or 0)
            deleted_counts["users"] = int(user_result.rowcount or 0)

    return deleted_counts


def seed_data(engine: Engine, users_table: Any, tasks_table: Any) -> dict[str, int]:
    """Insert users and related tasks. Returns insert counters."""
    inserted = {"users": 0, "tasks": 0}

    with engine.begin() as connection:
        connection.execute(text("PRAGMA foreign_keys = ON"))
        users = build_seed_users()

        for user in users:
            user_result = connection.execute(insert(users_table).values(**user))
            user_id = int(user_result.inserted_primary_key[0])
            inserted["users"] += 1

            tasks = build_user_tasks(user_id=user_id, count=20)
            if tasks:
                task_result = connection.execute(insert(tasks_table), tasks)
                inserted["tasks"] += int(task_result.rowcount or len(tasks))

    return inserted


def print_summary(cleaned: bool, deleted: dict[str, int], inserted: dict[str, int]) -> None:
    """Print concise summary of seeding actions."""
    print("Test data seed summary")
    print(f"- Clean requested: {cleaned}")
    print(f"- Deleted users: {deleted['users']}")
    print(f"- Deleted tasks: {deleted['tasks']}")
    print(f"- Inserted users: {inserted['users']}")
    print(f"- Inserted tasks: {inserted['tasks']}")


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    engine = get_engine()

    try:
        users_table, tasks_table = reflect_tables(engine)

        deleted = {"users": 0, "tasks": 0}
        if args.clean:
            deleted = clean_seed_data(engine, users_table, tasks_table)

        inserted = seed_data(engine, users_table, tasks_table)
        print_summary(cleaned=args.clean, deleted=deleted, inserted=inserted)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
