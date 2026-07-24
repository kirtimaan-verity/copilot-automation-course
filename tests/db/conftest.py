"""Shared pytest fixtures for database tests."""

from __future__ import annotations

import os
from typing import Any, Dict, Iterator, Mapping

import pytest
from faker import Faker
from sqlalchemy import MetaData, create_engine, delete, event, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.sql.schema import Table


@pytest.fixture(scope="session")
def db_engine() -> Iterator[Engine]:
    """Create one SQLAlchemy engine for the whole test session."""
    db_url = os.environ.get("TEST_DB_URL", "sqlite:///./db/app.db")
    engine = create_engine(db_url)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def db_tables(db_engine: Engine) -> Mapping[str, Table]:
    """Reflect existing tables from the configured database."""
    metadata = MetaData()
    metadata.reflect(bind=db_engine)
    return metadata.tables


@pytest.fixture(scope="function")
def db_session(db_engine: Engine) -> Iterator[Session]:
    """Provide an isolated session using an outer transaction + nested savepoint."""
    connection = db_engine.connect()
    connection.execute(text("PRAGMA foreign_keys = ON"))
    if connection.in_transaction():
        connection.rollback()

    outer_transaction = connection.begin()
    session = Session(bind=connection)
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session_obj: Session, transaction: Any) -> None:
        parent = transaction.parent
        if transaction.nested and (parent is None or not parent.nested):
            session_obj.begin_nested()

    try:
        yield session
    finally:
        event.remove(session, "after_transaction_end", restart_savepoint)
        session.close()
        outer_transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def test_user(db_session: Session, db_tables: Mapping[str, Table]) -> Iterator[Dict[str, Any]]:
    """Insert a test user and remove it during teardown."""
    faker = Faker()
    users_table = db_tables["users"]
    password_hash = faker.sha256()

    insert_result = db_session.execute(
        users_table.insert().values(
            email=faker.unique.email(),
            password_hash=password_hash,
            display_name=faker.name(),
        )
    )
    user_id = insert_result.inserted_primary_key[0]

    user_row = db_session.execute(select(users_table).where(users_table.c.id == user_id)).mappings().one()
    user_data = dict(user_row)

    try:
        yield user_data
    finally:
        db_session.execute(delete(users_table).where(users_table.c.id == user_id))
        db_session.flush()
